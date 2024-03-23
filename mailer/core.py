from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .models import EmailTemplate


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
