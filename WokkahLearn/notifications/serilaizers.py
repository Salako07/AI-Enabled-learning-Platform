from rest_framework import serializers
from .models import (
    Notification, NotificationPreference, NotificationTemplate,
    AnnouncementBanner
)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'channel', 'status', 'action_url',
            'actions_config', 'opened_at', 'clicked_at', 'sent_at',
            'expires_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'opened_at', 'clicked_at', 'sent_at', 'created_at'
        ]

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'notifications_enabled', 'email_notifications', 'push_notifications',
            'sms_notifications', 'digest_frequency', 'course_notifications',
            'assessment_notifications', 'collaboration_notifications',
            'ai_notifications', 'payment_notifications', 'marketing_notifications',
            'system_notifications', 'social_notifications', 'quiet_hours_enabled',
            'quiet_hours_start', 'quiet_hours_end', 'timezone'
        ]

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'title_template',
            'message_template', 'channels', 'priority', 'is_actionable',
            'is_active'
        ]

class AnnouncementBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementBanner
        fields = [
            'id', 'title', 'message', 'banner_type', 'target_audience',
            'is_dismissible', 'priority', 'background_color', 'text_color',
            'icon', 'action_text', 'action_url', 'start_date', 'end_date',
            'is_active'
        ]