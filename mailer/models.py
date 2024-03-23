from django.contrib.postgres.fields import ArrayField
# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField

from core.models import EntityModel

User = get_user_model()


class EmailTemplate(models.Model):
    name = models.CharField('Template Name', max_length=50, unique=True)
    subject = models.CharField('Email subject', max_length=200, blank=True)
    msg_text = models.TextField('Message (Plain text)', null=True, blank=True)
    msg_html = HTMLField('Message HTML', null=True, blank=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class MessageTemplate(EntityModel):
    msg = models.TextField('Message', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=20), default=list, size=10)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.msg
