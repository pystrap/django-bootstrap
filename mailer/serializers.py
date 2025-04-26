from rest_framework import serializers

from .models import MessageTemplate, Notification


class MessageTemplateModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = ['id', 'msg', 'tags']


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    from_user = serializers.StringRelatedField()
    date = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Notification
        fields = ['id', 'object_id', 'object', 'type', 'user', 'from_user', 'action', 'long_message',
                  'message', 'data', 'seen', 'created_at', 'date', 'link', 'link_text']
