from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'image_url', 'timestamp', 'is_read', 'content_type', 'object_id']
        read_only_fields = ['id', 'user', 'message', 'image_url', 'timestamp', 'content_type', 'object_id']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['in_app_notifications', 'email_notifications', 'push_notifications', 'sms_notifications']