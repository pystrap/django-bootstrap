from rest_framework import serializers

from .models import MessageTemplate


class MessageTemplateModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = ['id', 'msg', 'tags']
