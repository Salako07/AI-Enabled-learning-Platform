# analytics/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class LearningAnalytics(models.Model):
    """Comprehensive learning analytics for users"""
    
    METRIC_TYPES = [
        ('engagement', 'Engagement'),
        ('progress', 'Progress'),
        ('performance', 'Performance'),
        ('retention', 'Retention'),
        ('skill_development', 'Skill Development'),
        ('collaboration', 'Collaboration'),
        ('ai_interaction', 'AI Interaction'),
    ]
    
    AGGREGATION_PERIODS = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_analytics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    aggregation_period = models.CharField(max_length=20, choices=AGGREGATION_PERIODS)
    
    # Time Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metrics Data
    metrics = models.JSONField(default=dict)
    
    # Context
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    skill_area = models.CharField(max_length=100, blank=True)
    
    # AI Insights
    ai_insights = models.JSONField(default=dict, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_analytics'
        verbose_name = 'Learning Analytics'
        verbose_name_plural = 'Learning Analytics'
        unique_together = ['user', 'metric_type', 'aggregation_period', 'period_start']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_metric_type_display()} ({self.aggregation_period})"


class PlatformAnalytics(models.Model):
    """Platform-wide analytics and metrics"""
    
    METRIC_CATEGORIES = [
        ('user_engagement', 'User Engagement'),
        ('course_performance', 'Course Performance'),
        ('content_effectiveness', 'Content Effectiveness'),
        ('ai_performance', 'AI Performance'),
        ('collaboration_metrics', 'Collaboration Metrics'),
        ('revenue_metrics', 'Revenue Metrics'),
        ('system_performance', 'System Performance'),
        ('feature_usage', 'Feature Usage'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_category = models.CharField(max_length=30, choices=METRIC_CATEGORIES)
    metric_name = models.CharField(max_length=100)
    
    # Time Period
    date = models.DateField()
    hour = models.IntegerField(null=True, blank=True)  # For hourly metrics
    
    # Metric Values
    value = models.FloatField()
    additional_data = models.JSONField(default=dict, blank=True)
    
    # Segmentation
    segment = models.CharField(max_length=100, blank=True)  # e.g., user_type, course_category
    cohort = models.CharField(max_length=100, blank=True)  # e.g., signup_month
    
    # Comparison Data
    previous_period_value = models.FloatField(null=True, blank=True)
    change_percentage = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'platform_analytics'
        verbose_name = 'Platform Analytics'
        verbose_name_plural = 'Platform Analytics'
        unique_together = ['metric_category', 'metric_name', 'date', 'hour', 'segment']
        ordering = ['-date', '-hour']
    
    def __str__(self):
        return f"{self.metric_name} - {self.date}"


class UserBehaviorTracking(models.Model):
    """Detailed user behavior tracking for analytics"""
    
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('click', 'Click'),
        ('scroll', 'Scroll'),
        ('video_play', 'Video Play'),
        ('video_pause', 'Video Pause'),
        ('code_execution', 'Code Execution'),
        ('search', 'Search'),
        ('download', 'Download'),
        ('bookmark', 'Bookmark'),
        ('share', 'Share'),
        ('rating', 'Rating'),
        ('feedback', 'Feedback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behavior_tracking')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Event Details
    event_data = models.JSONField(default=dict)
    page_url = models.URLField()
    referrer_url = models.URLField(blank=True)
    
    # Context
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    content_id = models.UUIDField(null=True, blank=True)
    
    # Session Information
    session_id = models.CharField(max_length=100)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Device and Browser
    device_type = models.CharField(max_length=20, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=50, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    time_on_page = models.FloatField(null=True, blank=True)  # seconds
    
    class Meta:
        db_table = 'user_behavior_tracking'
        verbose_name = 'User Behavior Tracking'
        verbose_name_plural = 'User Behavior Tracking'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_event_type_display()}"


class LearningPathAnalytics(models.Model):
    """Analytics for learning path effectiveness"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learning_path_id = models.UUIDField()
    
    # Completion Metrics
    total_enrollments = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Time Metrics
    average_completion_time = models.DurationField(null=True, blank=True)
    median_completion_time = models.DurationField(null=True, blank=True)
    fastest_completion_time = models.DurationField(null=True, blank=True)
    
    # Engagement Metrics
    average_session_duration = models.DurationField(null=True, blank=True)
    total_time_spent = models.DurationField(default='00:00:00')
    dropout_points = models.JSONField(default=list, blank=True)  # Where users typically drop off
    
    # Satisfaction Metrics
    average_rating = models.FloatField(default=0.0)
    nps_score = models.FloatField(null=True, blank=True)  # Net Promoter Score
    satisfaction_distribution = models.JSONField(default=dict, blank=True)
    
    # AI Effectiveness
    ai_recommendation_accuracy = models.FloatField(default=0.0)
    ai_personalization_score = models.FloatField(default=0.0)
    
    # Date Range
    analysis_period_start = models.DateTimeField()
    analysis_period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_path_analytics'
        verbose_name = 'Learning Path Analytics'
        verbose_name_plural = 'Learning Path Analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Learning Path Analytics {self.learning_path_id}"


class ContentAnalytics(models.Model):
    """Analytics for individual content pieces"""
    
    CONTENT_TYPES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('interactive_content', 'Interactive Content'),
        ('video', 'Video'),
        ('quiz', 'Quiz'),
        ('exercise', 'Exercise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.UUIDField()
    
    # Engagement Metrics
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    total_time_spent = models.DurationField(default='00:00:00')
    average_session_duration = models.DurationField(null=True, blank=True)
    
    # Completion Metrics
    total_starts = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    average_completion_time = models.DurationField(null=True, blank=True)
    
    # Interaction Metrics
    total_interactions = models.IntegerField(default=0)
    average_interactions_per_user = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(default=0.0)
    
    # Quality Metrics
    average_rating = models.FloatField(default=0.0)
    total_ratings = models.IntegerField(default=0)
    difficulty_feedback = models.JSONField(default=dict, blank=True)
    
    # Performance Issues
    error_rate = models.FloatField(default=0.0)
    loading_time_issues = models.IntegerField(default=0)
    user_reported_issues = models.IntegerField(default=0)
    
    # AI Analytics
    ai_difficulty_prediction = models.FloatField(null=True, blank=True)
    ai_engagement_prediction = models.FloatField(null=True, blank=True)
    ai_improvement_suggestions = models.JSONField(default=list, blank=True)
    
    # Date Range
    analysis_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_analytics'
        verbose_name = 'Content Analytics'
        verbose_name_plural = 'Content Analytics'
        unique_together = ['content_type', 'content_id', 'analysis_date']
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"{self.get_content_type_display()} {self.content_id} - {self.analysis_date}"


class A_BTestResult(models.Model):
    """A/B testing results for platform optimization"""
    
    TEST_TYPES = [
        ('ui_change', 'UI Change'),
        ('content_variation', 'Content Variation'),
        ('feature_toggle', 'Feature Toggle'),
        ('pricing_test', 'Pricing Test'),
        ('recommendation_algorithm', 'Recommendation Algorithm'),
        ('ai_prompt', 'AI Prompt'),
        ('notification_timing', 'Notification Timing'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test_name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=30, choices=TEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Test Configuration
    description = models.TextField()
    hypothesis = models.TextField()
    success_metrics = models.JSONField(default=list)
    
    # Variants
    control_variant = models.JSONField(default=dict)
    test_variants = models.JSONField(default=list)
    traffic_allocation = models.JSONField(default=dict)  # Percentage allocation per variant
    
    # Targeting
    target_audience = models.JSONField(default=dict, blank=True)
    exclusion_criteria = models.JSONField(default=dict, blank=True)
    
    # Results
    participants_count = models.IntegerField(default=0)
    results_data = models.JSONField(default=dict, blank=True)
    statistical_significance = models.FloatField(null=True, blank=True)
    confidence_level = models.FloatField(default=95.0)
    
    # Analysis
    winner_variant = models.CharField(max_length=100, blank=True)
    improvement_percentage = models.FloatField(null=True, blank=True)
    conclusions = models.TextField(blank=True)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ab_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ab_test_results'
        verbose_name = 'A/B Test Result'
        verbose_name_plural = 'A/B Test Results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.test_name} ({self.status})"


class UserCohortAnalysis(models.Model):
    """Cohort analysis for user retention and behavior"""
    
    COHORT_TYPES = [
        ('signup_month', 'Signup Month'),
        ('first_purchase', 'First Purchase'),
        ('course_completion', 'Course Completion'),
        ('subscription_tier', 'Subscription Tier'),
        ('user_role', 'User Role'),
        ('acquisition_channel', 'Acquisition Channel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cohort_type = models.CharField(max_length=30, choices=COHORT_TYPES)
    cohort_identifier = models.CharField(max_length=100)  # e.g., "2024-01", "premium", etc.
    
    # Cohort Metrics
    total_users = models.IntegerField(default=0)
    period_number = models.IntegerField()  # 0=first period, 1=second period, etc.
    
    # Retention Metrics
    active_users = models.IntegerField(default=0)
    retention_rate = models.FloatField(default=0.0)
    
    # Engagement Metrics
    average_sessions = models.FloatField(default=0.0)
    average_session_duration = models.DurationField(null=True, blank=True)
    total_learning_time = models.DurationField(default='00:00:00')
    
    # Revenue Metrics (if applicable)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_revenue_per_user = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Learning Metrics
    courses_completed = models.IntegerField(default=0)
    skills_gained = models.IntegerField(default=0)
    certificates_earned = models.IntegerField(default=0)
    
    # Date
    analysis_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_cohort_analysis'
        verbose_name = 'User Cohort Analysis'
        verbose_name_plural = 'User Cohort Analysis'
        unique_together = ['cohort_type', 'cohort_identifier', 'period_number', 'analysis_date']
        ordering = ['cohort_type', 'cohort_identifier', 'period_number']
    
    def __str__(self):
        return f"{self.cohort_type} {self.cohort_identifier} - Period {self.period_number}"


class PredictiveAnalytics(models.Model):
    """AI-powered predictive analytics"""
    
    PREDICTION_TYPES = [
        ('churn_risk', 'Churn Risk'),
        ('course_completion', 'Course Completion Probability'),
        ('skill_mastery', 'Skill Mastery Timeline'),
        ('engagement_drop', 'Engagement Drop Risk'),
        ('upsell_opportunity', 'Upsell Opportunity'),
        ('content_performance', 'Content Performance'),
        ('learning_path_success', 'Learning Path Success'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low (< 70%)'),
        ('medium', 'Medium (70-85%)'),
        ('high', 'High (> 85%)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions', null=True, blank=True)
    prediction_type = models.CharField(max_length=30, choices=PREDICTION_TYPES)
    
    # Prediction Details
    predicted_value = models.FloatField()
    confidence_score = models.FloatField()  # 0.0 to 1.0
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)
    
    # Model Information
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=20)
    features_used = models.JSONField(default=list)
    
    # Context
    target_entity_type = models.CharField(max_length=50, blank=True)  # course, lesson, etc.
    target_entity_id = models.UUIDField(null=True, blank=True)
    
    # Prediction Timeline
    prediction_horizon = models.DurationField()  # How far into the future
    prediction_date = models.DateTimeField()  # When this prediction is for
    
    # Outcome Tracking
    actual_outcome = models.FloatField(null=True, blank=True)
    outcome_recorded_at = models.DateTimeField(null=True, blank=True)
    prediction_accuracy = models.FloatField(null=True, blank=True)
    
    # Actionable Insights
    recommended_actions = models.JSONField(default=list, blank=True)
    intervention_suggestions = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'predictive_analytics'
        verbose_name = 'Predictive Analytics'
        verbose_name_plural = 'Predictive Analytics'
        ordering = ['-created_at']
    
    def __str__(self):
        user_name = self.user.full_name if self.user else "Platform"
        return f"{self.get_prediction_type_display()} for {user_name}"