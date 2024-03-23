from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from .models import Note
from utils.fns import json_loads
from rest_framework import serializers

User = get_user_model()


class LogEntrySerializer(serializers.ModelSerializer):
    change_message = serializers.JSONField()
    username = serializers.StringRelatedField(source='user.username', read_only=True)
    user_email = serializers.StringRelatedField(source='user.email')
    user_first_name = serializers.StringRelatedField(source='user.first_name', read_only=True)
    user_last_name = serializers.StringRelatedField(source='user.last_name', read_only=True)

    def to_representation(self, instance):
        ret = super(LogEntrySerializer, self).to_representation(instance)
        ret['change_message'] = json_loads(ret['change_message'])
        return ret

    class Meta:
        model = LogEntry
        fields = '__all__'


class SerializerUserDefaults:
    extra_kwargs = {
        'created_by': {
            'read_only': True,
            'default': serializers.CurrentUserDefault(),
        },
        'updated_by': {
            'default': serializers.CurrentUserDefault()
        }
    }


class EntitySerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField(read_only=True)

    def get_history(self, instance):
        return LogEntrySerializer(instance.history(), many=True).data


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']


class UserAccountSerializer(serializers.ModelSerializer):
    staff_roles = serializers.SerializerMethodField()
    log_entries = serializers.SerializerMethodField()

    def get_staff_roles(self, instance):
        return instance.groups.values_list('name', flat=True)

    def get_log_entries(self, instance):
        return LogEntrySerializer(LogEntry.objects.filter(user=instance)[:100], many=True).data

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'staff_roles', 'log_entries']
        read_only_field = []


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['user'] = UserInfoSerializer(self.user).data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['roles'] = list(self.user.get_all_permissions())

        if self.user.is_superuser or self.user.is_staff:
            data['roles'].append('browse_admin')

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class NoteSerializer(serializers.ModelSerializer):
    created_by = UserInfoSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'created_by', 'note', 'created_at', ]
