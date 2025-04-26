import json
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.mail import EmailMultiAlternatives
# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField

from core.models import EntityModel
from core.fns import get_object_view_link, flatten_dict
from core.serializers import UserInfoSerializer

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

def send_mail_template(name, recipients, replacements={}, reply_to=None, attach_files=[]):
    if not settings.EMAIL_SEND_EMAILS:
        return True
    try:
        template = EmailTemplate.objects.get(name=name)
    except EmailTemplate.DoesNotExist:
        return False
    from_email = settings.EMAIL_HOST_USER
    subject = template.subject
    msg_text = template.msg_text
    msg_html = template.msg_html
    tmp = [subject := subject.replace('{' + key + '}', replacements[key]) for key in replacements.keys() if
           isinstance(replacements[key], str) and '{' + key + '}' in subject]
    tmp = [msg_text := msg_text.replace('{' + key + '}', replacements[key]) for key in replacements.keys() if
           isinstance(replacements[key], str) and '{' + key + '}' in msg_text]
    tmp = [msg_html := msg_html.replace('{' + key + '}', replacements[key]) for key in replacements.keys() if
           isinstance(replacements[key], str) and '{' + key + '}' in msg_html]
    del tmp

    msg = EmailMultiAlternatives(subject, msg_text, from_email, recipients)
    msg.attach_alternative(msg_html, "text/html")
    if reply_to:
        msg.reply_to = reply_to
    for file in attach_files:
        msg.attach_file(file)
    sent = msg.send(fail_silently=True)
    return sent


class Notification(EntityModel):
    DEFAULT_EMAIL_TEMPLATE = 'user_notification'

    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sent_notifications', null=True,
                                  blank=True)

    type = models.CharField(max_length=50)
    action = models.CharField(max_length=50, null=True, blank=True)
    object = models.CharField(max_length=50, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)

    link = models.CharField(max_length=2048, null=True, blank=True)
    link_text = models.CharField(max_length=50, null=True, blank=True)

    message = models.TextField(null=True, blank=True)
    long_message = models.TextField(null=True, blank=True)
    data = models.JSONField(blank=True, null=True)

    seen = models.BooleanField('Seen', default=False)

    def __str__(self):
        return self.message

    @staticmethod
    def notify_user(
            user: User,
            message,
            notification_type='message',
            data=None,
            action='display',
            target_object=None,
            target_object_id=None,
            from_user=None,
            send_mail=True,
            email_template=None,
            replacements=None,
            link_text='Go to Dashboard',
            action_link=None,
            send_browser_notification=False,
            long_message=None
    ):
        """
        Sends a notification to a user with support for email, in-app, and browser push.

        Parameters:
            user (User): The user who should receive the notification.
            message (str | None): The main message or a template name (prefix with ':'). If None and email_template is provided, the template's notification_msg is used.
            notification_type (str): Type of notification (e.g., 'message', 'alert', etc.).
            data (dict): Additional data to attach to the notification.
            action (str): Defines the client-side action ('display', 'link', etc.).
            target_object (Model): Optional related object for generating links.
            target_object_id (int): ID of the target object.
            from_user (User): Optional sender user.
            send_mail (bool): Whether to send the notification via email.
            email_template (str): Name of the email template to use (from EmailTemplate).
            replacements (dict): Replacement values for message/email templates.
            link_text (str): Display text for the action link.
            action_link (str): Direct override for the action URL.
            send_browser_notification (bool): Whether to trigger a browser push.
            long_message (str): Optional longer version of the message (can also be a template name).

        Returns:
            Notification: The created Notification object.

        Notes:
            - If `message` starts with ':', it will be treated as a MessageTemplate name.
            - If `email_template` is provided without `message`, the template's `notification_msg` is used.
            - Will only send emails if the user allows email notifications via `user.profile.email_notifications`.
            - Replacements can contain dynamic values such as user info, object info, or custom strings.
        """

        if data is None:
            data = {}
        if not user:
            return

        if (action == 'link' or link_text) and target_object:
            if not action_link:
                action_link = get_object_view_link(target_object, target_object_id,
                                                   data.get('base_id', None))

        n_replacements = replacements or {}
        n_replacements['user'] = UserInfoSerializer(user).data
        n_replacements['notification_data'] = data
        if action == 'link' and target_object and target_object_id:
            n_replacements['action_link'] = action_link
            n_replacements['action_link_text'] = link_text
        if from_user:
            n_replacements['from_user'] = UserInfoSerializer(from_user).data

        n_replacements = flatten_dict(n_replacements)

        if email_template and not message:
            notification_msg = str(EmailTemplate.objects.get(name=email_template).notification_msg or '')
            if n_replacements:
                __ = [notification_msg := notification_msg.replace('{' + key + '}', n_replacements[key]) for key in n_replacements.keys() if
                       isinstance(n_replacements[key], str) and '{' + key + '}' in notification_msg]
        else:
            notification_msg = str(message or '')
            if notification_msg and notification_msg.startswith(':'):
                template_name = notification_msg[1:]
                notification_msg = MessageTemplate.objects.get(name=template_name).process_replacements(replacements)

        if long_message and long_message.startswith(':'):
            template_name = long_message[1:]
            long_notification_msg = MessageTemplate.objects.get(name=template_name).process_replacements(replacements)
        else:
            long_notification_msg = long_message

        n_replacements['message'] = notification_msg
        n_replacements['long_message'] = long_notification_msg
        notification = Notification.objects.create(
            user=user,
            from_user=from_user,
            type=notification_type,
            action=action,
            object_id=target_object_id,
            object=target_object,
            message=notification_msg,
            long_message=long_notification_msg,
            link=action_link,
            link_text=link_text,
            data=data
        )

        # Send notification
        # from .serializers import NotificationSerializer

        # replace with websocket if possible
        # devices = FCMDevice.objects.filter(user=user, active=True)
        # fcm_data = {
        #     'artiq_event': 'notification',
        # }
        # notification_data = NotificationSerializer(notification).data
        # fcm_data['data'] = json.dumps(notification_data)
        # devices.send_message(FCMMessage(
        #     data=fcm_data,
        #     notification=FCMNotification(
        #         title="Artiq Swan Notification",
        #         body=notification_msg,
        #         image=urljoin(settings.FRONTEND_APP_DIR, '/assets/favicon.ico')
        #     ) if send_browser_notification else None
        # ))

        # Send email
        if send_mail and getattr(user, 'profile', None) and user.profile.email_notifications:
            if not email_template:
                email_template = Notification.DEFAULT_EMAIL_TEMPLATE
                if action == 'link' and target_object and target_object_id:
                    email_template = email_template + '_link'
            send_mail_template(email_template, [user.email], n_replacements)
        return notification

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["user", "seen"]),
        ]

