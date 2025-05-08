import os
from uuid import uuid4

from PIL import Image, ExifTags
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.encoding import force_str
from django_currentuser.middleware import get_current_user
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
import json

from django.db import models

from core.fns import get_object_view_link

Image.MAX_IMAGE_PIXELS = None  # Set to None to disable the limit


def entity_files_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join(settings.ENTITY_FILES_BASE, instance._meta.model_name, '{0}.{1}'.format(uuid4().hex, ext))


def get_thumbnail_path(original_path):
    # Split the original path into directory and filename
    directory, filename = os.path.split(original_path)
    thumbnails_dir = os.path.join(directory, 'thumbnails')
    # Append '_thumb' to the filename before the extension
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_thumb{ext}"

    # Generate the new thumbnail path
    thumbnail_path = os.path.join(thumbnails_dir, new_filename)
    return thumbnail_path


class MetaFieldMixin(models.Model):
    meta = models.JSONField(default=dict)

    class Meta:
        abstract = True  # Ensures this mixin is abstract and won't create a database table

    def get_meta(self, key, default=None):
        """
        Retrieve a value from the meta field by key.
        Returns the default value if the key does not exist.
        """
        return self.meta.get(key, default)

    def set_meta(self, key, value):
        """
        Set a key-value pair in the meta field and save the model.
        """
        self.meta[key] = value
        self.save(update_fields=['meta'])

    def delete_meta(self, key):
        """
        Remove a key from the meta field and save the model.
        """
        if key in self.meta:
            del self.meta[key]
            self.save(update_fields=['meta'])

    def has_meta(self, key):
        """
        Check if a key exists in the meta field.
        """
        return key in self.meta


class EntityLinkMixin:
    @property
    def entity_model(self):
        if not (hasattr(self, 'entity') and hasattr(self, 'content_type') and hasattr(self, 'object_id')):
            return ''
        return self.content_type.model

    @property
    def entity_type_name(self):
        target_object = self.entity_model
        multi_word_objects = {
            'purchaseorder': 'Purchase Order',
            'jobhub': 'Job Hub',
            'jobitem': 'Job Item',
        }
        return multi_word_objects[
            target_object] if target_object in multi_word_objects.keys() else target_object.capitalize()

    @property
    def entity_link(self):
        target_object = self.entity_model
        if not target_object:
            return ''
        base_id = None
        if target_object in ['quotation', 'purchaseorder'] and self.entity.job_hub:
            base_id = self.entity.job_hub.id
        if target_object == 'jobitem':
            base_id = self.entity.job.job_hub.id
        return get_object_view_link(target_object, self.object_id, base_id)


class User(AbstractUser):
    # Add custom fields here
    last_seen = models.DateTimeField(null=True, blank=True)
    need_reset_password = models.BooleanField(default=False)

    @property
    def full_name(self):
        return ' '.join([i for i in [self.first_name, self.last_name] if i])

    @property
    def display_name(self):
        return self.full_name or self.username

    class Meta:
        db_table = 'auth_user'


class EntityModel(models.Model):
    """
    Used in all the entity models as base
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL, related_name='created_%(class)s', null=True,
                                   blank=True, editable=False)

    # updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
    #                                related_name='%(class)s_updated_by',
    #                                on_delete=models.SET_NULL,
    #                                null=True, blank=True, )

    def history(self):
        return LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(self).pk,
                                       object_id=self.pk, action_time__gte=self.created_at).order_by('-action_time')

    def log_action(self, user, action, msg, **kwargs):
        change_fields = kwargs.get('changed_fields', [])
        if 'changed_fields' in kwargs:
            del kwargs['changed_fields']
        message = {
            'msg': msg,
            **kwargs
        }
        if action == ADDITION:
            message['added'] = {}
        if action == CHANGE:
            message['changed'] = {'fields': change_fields}
        if action == DELETION:
            message['deleted'] = {}
        return LogEntry.objects.log_action(
            user_id=user,
            content_type_id=ContentType.objects.get_for_model(self).pk,
            object_id=self.pk,
            object_repr=force_str(self),
            change_message=json.dumps(message),
            action_flag=action
        )

    def save(self, *args, **kwargs):
        if not self.created_by:
            user = get_current_user()
            if user and user.is_authenticated:
                self.created_by = user
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Note(EntityModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.note

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class GlobalPermissions(models.Model):
    class Meta:
        managed = False  # No database table creation or deletion  \
        # operations will be performed for this model.

        default_permissions = ()  # disable "add", "change", "delete"
        # and "view" default permissions

        permissions = (
            ('browse_admin', 'Access the admin interface'),
        )


class AppSettings(models.Model):
    name = models.CharField('Key', max_length=32, unique=True)
    data = models.JSONField(blank=True, null=True)

    @property
    def value(self):
        return self.data

    @staticmethod
    def get_setting(name):
        row, created = AppSettings.objects.get_or_create(name=name)
        return row.data

    class Meta:
        ordering = ['name']


class BaseFile(EntityModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    entity = GenericForeignKey('content_type', 'object_id')
    file = models.FileField('File', upload_to=entity_files_path, null=True, blank=True, max_length=255)
    file_name = models.CharField('File Name', max_length=255, blank=True, null=True)

    @property
    def name(self):
        return self.file_name if self.file_name else os.path.basename(self.file.name)

    def __str__(self):
        return self.name

    def has_file(self):
        return bool(self.file)

    has_file.boolean = True
    has_file.short_description = 'Has File'

    class Meta:
        abstract = True
        ordering = ['created_at']
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]


class File(BaseFile):
    pass


class ImageFile(BaseFile):
    img_height = models.PositiveIntegerField(editable=False, null=True, blank=True)
    img_width = models.PositiveIntegerField(editable=False, null=True, blank=True)
    file = models.ImageField('Image', upload_to=entity_files_path, height_field='img_height', width_field='img_width',
                             null=True, blank=True, max_length=255)
    thumbnail = models.CharField(max_length=255, null=True, blank=True)

    def get_thumbnail_path(self):
        return get_thumbnail_path(self.file.name)

    def img_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail
        if not self.file or not os.path.exists(os.path.join(settings.MEDIA_ROOT, self.file.name)):
            return 'https://dummyimage.com/150/bbbbbb/eeeeee&text=No+Image'

        thumbnail_path = self.get_thumbnail_path()
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, thumbnail_path)):
            thumbnail = os.path.join(settings.MEDIA_URL, thumbnail_path)
            self.thumbnail = thumbnail
            self.save(update_fields=['thumbnail'])
            return thumbnail

        thumbnail_size = (200, 200)

        try:
            image_path = os.path.join(settings.MEDIA_ROOT, self.file.name)

            # Open the image and preserve the original EXIF metadata
            with Image.open(image_path) as image:
                if hasattr(image, '_getexif'):  # Check if the image has EXIF data
                    exif = image._getexif()
                    if exif is not None:
                        for key, value in exif.items():
                            tag = ExifTags.TAGS.get(key)
                            if tag == 'Orientation':
                                if value == 3:
                                    image = image.rotate(180, expand=True)
                                elif value == 6:
                                    image = image.rotate(270, expand=True)
                                elif value == 8:
                                    image = image.rotate(90, expand=True)

                image.thumbnail(thumbnail_size, Image.BICUBIC)

                # Save the thumbnail
                os.makedirs(os.path.join(settings.MEDIA_ROOT, os.path.dirname(thumbnail_path)), exist_ok=True)
                image.save(os.path.join(settings.MEDIA_ROOT, thumbnail_path), quality=100)

                thumbnail = os.path.join(settings.MEDIA_URL, thumbnail_path)
                self.thumbnail = thumbnail
                self.save(update_fields=['thumbnail'])
                return thumbnail
        except Exception as e:
            print(e)
            return 'https://dummyimage.com/150/bbbbbb/eeeeee&text=Image+Error'

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

