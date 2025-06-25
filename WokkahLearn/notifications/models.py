# notifications/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    
    NOTIFICATION_TYPES = [
        ('course_enrollment', 'Course Enrollment'),
        ('lesson_completion', 'Lesson Completion'),
        ('assessment_result', 'Assessment Result'),
        ('collaboration_invite', 'Collaboration Invite'),
        ('ai_recommendation', 'AI Recommendation'),
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('subscription_expiry', 'Subscription Expiry'),
        ('achievement_earned', 'Achievement Earned'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('system_announcement', 'System Announcement'),
        ('security_alert', 'Security Alert'),
        ('feature_update', 'Feature Update'),
        ('maintenance_notice', 'Maintenance Notice'),
        ('social_activity', 'Social Activity'),
        ('mentor_message', 'Mentor Message'),
        ('peer_review_assigned', 'Peer Review Assigned'),
        ('certificate_ready', 'Certificate Ready'),
        ('skill_milestone', 'Skill Milestone'),
        ('learning_streak', 'Learning Streak'),
    ]
    
    CHANNELS = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('sms', 'SMS'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, unique=True)
    
    # Template Content
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    html_template = models.TextField(blank=True)  # For rich notifications
    
    # Channel Configuration
    channels = models.JSONField(default=list)  # Which channels to use
    default_channel = models.CharField(max_length=20, choices=CHANNELS, default='in_app')
    
    # Behavior
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_actionable = models.BooleanField(default=False)  # Has buttons/actions
    action_config = models.JSONField(default=dict, blank=True)  # Button configs
    
    # Personalization
    personalization_enabled = models.BooleanField(default=True)
    ai_personalization = models.BooleanField(default=False)
    
    # Frequency Control
    max_frequency = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='instant'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class Notification(models.Model):
    """Individual notifications sent to users"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CHANNELS = [
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('sms', 'SMS'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(
        NotificationTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications'
    )
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Delivery
    channel = models.CharField(max_length=20, choices=CHANNELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Context and Data
    context_data = models.JSONField(default=dict, blank=True)  # Template variables
    metadata = models.JSONField(default=dict, blank=True)  # Additional data
    
    # Related Objects
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    assessment_id = models.UUIDField(null=True, blank=True)
    collaboration_room_id = models.UUIDField(null=True, blank=True)
    
    # Actions
    action_url = models.URLField(blank=True)
    action_data = models.JSONField(default=dict, blank=True)
    actions_config = models.JSONField(default=list, blank=True)  # Multiple actions
    
    # Interaction Tracking
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    action_taken_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery Details
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True)
    
    # External Service Data
    external_id = models.CharField(max_length=100, blank=True)  # Email service ID, etc.
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['channel', 'status']),
            models.Index(fields=['scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.title} to {self.user.full_name} ({self.channel})"


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Global Settings
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Frequency Preferences
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Never'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    # Type-specific Preferences
    course_notifications = models.BooleanField(default=True)
    assessment_notifications = models.BooleanField(default=True)
    collaboration_notifications = models.BooleanField(default=True)
    ai_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    marketing_notifications = models.BooleanField(default=False)
    system_notifications = models.BooleanField(default=True)
    social_notifications = models.BooleanField(default=True)
    
    # Advanced Settings
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # AI Personalization
    ai_personalized_timing = models.BooleanField(default=True)
    ai_content_optimization = models.BooleanField(default=True)
    
    # Detailed Type Preferences
    type_preferences = models.JSONField(default=dict, blank=True)  # Per notification type settings
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preferences'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification Preferences for {self.user.full_name}"


class NotificationDigest(models.Model):
    """Notification digests for batched delivery"""
    
    DIGEST_TYPES = [
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
        ('monthly', 'Monthly Digest'),
        ('custom', 'Custom Digest'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_digests')
    digest_type = models.CharField(max_length=20, choices=DIGEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Content
    title = models.CharField(max_length=200)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Included Notifications
    notifications = models.ManyToManyField(Notification, related_name='digests')
    notification_count = models.IntegerField(default=0)
    
    # AI Personalization
    ai_generated_summary = models.TextField(blank=True)
    ai_priority_insights = models.JSONField(default=list, blank=True)
    ai_recommended_actions = models.JSONField(default=list, blank=True)
    
    # Delivery
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_digests'
        verbose_name = 'Notification Digest'
        verbose_name_plural = 'Notification Digests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_digest_type_display()} for {self.user.full_name}"


class PushDevice(models.Model):
    """Push notification device tokens"""
    
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web Browser'),
        ('desktop', 'Desktop App'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_devices')
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    
    # Device Information
    device_token = models.TextField()  # FCM/APNS token
    device_id = models.CharField(max_length=200, blank=True)
    device_name = models.CharField(max_length=100, blank=True)
    
    # Platform Details
    platform_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    
    # Delivery Statistics
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'push_devices'
        verbose_name = 'Push Device'
        verbose_name_plural = 'Push Devices'
        unique_together = ['user', 'device_token']
        ordering = ['-last_used']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_device_type_display()}"


class NotificationQueue(models.Model):
    """Queue for processing notifications"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='queue_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Processing Details
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    # Scheduling
    scheduled_for = models.DateTimeField()
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Processing Results
    last_error = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Timestamps
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notification_queue'
        verbose_name = 'Notification Queue Item'
        verbose_name_plural = 'Notification Queue Items'
        ordering = ['priority', 'scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['priority', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"Queue Item {self.id} - {self.notification.title}"


class NotificationAnalytics(models.Model):
    """Analytics for notification performance"""
    
    METRIC_TYPES = [
        ('delivery_rate', 'Delivery Rate'),
        ('open_rate', 'Open Rate'),
        ('click_rate', 'Click Rate'),
        ('conversion_rate', 'Conversion Rate'),
        ('unsubscribe_rate', 'Unsubscribe Rate'),
        ('engagement_score', 'Engagement Score'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        NotificationTemplate, 
        on_delete=models.CASCADE, 
        related_name='analytics',
        null=True,
        blank=True
    )
    channel = models.CharField(max_length=20)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    
    # Time Period
    date = models.DateField()
    hour = models.IntegerField(null=True, blank=True)  # For hourly metrics
    
    # Metrics
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_opened = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    total_converted = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    total_unsubscribed = models.IntegerField(default=0)
    
    # Calculated Rates
    delivery_rate = models.FloatField(default=0.0)
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    
    # Segmentation
    user_segment = models.CharField(max_length=50, blank=True)  # e.g., new_users, premium_users
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_analytics'
        verbose_name = 'Notification Analytics'
        verbose_name_plural = 'Notification Analytics'
        unique_together = ['template', 'channel', 'metric_type', 'date', 'hour', 'user_segment']
        ordering = ['-date', '-hour']
    
    def __str__(self):
        template_name = self.template.name if self.template else 'All Templates'
        return f"{template_name} - {self.channel} - {self.date}"


class AnnouncementBanner(models.Model):
    """Site-wide announcement banners"""
    
    BANNER_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance'),
        ('feature', 'New Feature'),
        ('promotion', 'Promotion'),
    ]
    
    TARGET_AUDIENCES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('instructors', 'Instructors Only'),
        ('premium', 'Premium Users'),
        ('free', 'Free Users'),
        ('new_users', 'New Users'),
        ('enterprise', 'Enterprise Users'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='info')
    
    # Targeting
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCES, default='all')
    user_filters = models.JSONField(default=dict, blank=True)  # Advanced filtering
    
    # Display Configuration
    is_dismissible = models.BooleanField(default=True)
    show_on_pages = models.JSONField(default=list, blank=True)  # Specific pages
    priority = models.IntegerField(default=0)  # Higher = more important
    
    # Styling
    background_color = models.CharField(max_length=7, blank=True)  # Hex color
    text_color = models.CharField(max_length=7, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    # Actions
    action_text = models.CharField(max_length=100, blank=True)
    action_url = models.URLField(blank=True)
    
    # Scheduling
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    dismiss_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcement_banners'
        verbose_name = 'Announcement Banner'
        verbose_name_plural = 'Announcement Banners'
        ordering = ['-priority', '-start_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"


class UserBannerInteraction(models.Model):
    """Track user interactions with announcement banners"""
    
    INTERACTION_TYPES = [
        ('viewed', 'Viewed'),
        ('clicked', 'Clicked'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banner_interactions')
    banner = models.ForeignKey(AnnouncementBanner, on_delete=models.CASCADE, related_name='user_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Context
    page_url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_banner_interactions'
        verbose_name = 'User Banner Interaction'
        verbose_name_plural = 'User Banner Interactions'
        unique_together = ['user', 'banner', 'interaction_type']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.full_name} {self.interaction_type} {self.banner.title}"