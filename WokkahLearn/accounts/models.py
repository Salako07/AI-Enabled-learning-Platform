from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.core.validators import RegexValidator
import uuid

class User(AbstractUser):
    """Extended user model with additional fields for the learning platform"""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
        ('enterprise', 'Enterprise User'),
    ]
    
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
        ('reading', 'Reading/Writing'),
    ]
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Profile Information
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Learning Preferences
    learning_style = models.CharField(
        max_length=20, 
        choices=LEARNING_STYLE_CHOICES, 
        blank=True
    )
    current_skill_level = models.CharField(
        max_length=20, 
        choices=SKILL_LEVEL_CHOICES, 
        default='beginner'
    )
    learning_goals = models.TextField(blank=True)
    preferred_languages = models.JSONField(default=list, blank=True)
    
    # Subscription and Payment
    subscription_tier = models.CharField(max_length=20, default='free')
    subscription_active = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Activity Tracking
    last_active = models.DateTimeField(auto_now=True)
    total_learning_time = models.DurationField(default=timedelta)
    courses_completed = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    
    # AI Personalization
    ai_learning_preferences = models.JSONField(default=dict, blank=True)
    ai_skill_assessment = models.JSONField(default=dict, blank=True)
    
    # Notifications and Privacy
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_progress_data(self):
        """Return user's learning progress data"""
        return {
            'courses_completed': self.courses_completed,
            'total_learning_time': self.total_learning_time,
            'current_streak': self.current_streak,
            'skill_level': self.current_skill_level,
        }


class UserSkill(models.Model):
    """Track user skills and proficiency levels"""
    
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Basic'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.IntegerField(choices=PROFICIENCY_CHOICES, default=1)
    verified = models.BooleanField(default=False)
    last_assessed = models.DateTimeField(auto_now=True)
    
    # AI Assessment Data
    ai_confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    assessment_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skills'
        unique_together = ['user', 'skill_name']
        verbose_name = 'User Skill'
        verbose_name_plural = 'User Skills'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.skill_name} ({self.get_proficiency_level_display()})"


class UserLearningPath(models.Model):
    """Personalized learning paths for users"""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # AI Generated Path
    is_ai_generated = models.BooleanField(default=False)
    ai_generation_prompt = models.TextField(blank=True)
    
    # Progress Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.FloatField(default=0.0)
    estimated_duration = models.DurationField()
    actual_duration = models.DurationField(null=True, blank=True)
    
    # Metadata
    difficulty_level = models.CharField(max_length=20, choices=User.SKILL_LEVEL_CHOICES)
    target_skills = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_learning_paths'
        verbose_name = 'User Learning Path'
        verbose_name_plural = 'User Learning Paths'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.name}"


class UserPreferences(models.Model):
    """Detailed user preferences for personalization"""
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    DIFFICULTY_PREFERENCE_CHOICES = [
        ('easy', 'Prefer Easier Content'),
        ('balanced', 'Balanced Difficulty'),
        ('challenging', 'Prefer Challenging Content'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # UI Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='auto')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Learning Preferences
    difficulty_preference = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_PREFERENCE_CHOICES, 
        default='balanced'
    )
    preferred_session_length = models.DurationField(default='01:00:00')  # 1 hour default
    break_reminders = models.BooleanField(default=True)
    
    # AI Preferences
    ai_assistance_level = models.CharField(
        max_length=20,
        choices=[
            ('minimal', 'Minimal Assistance'),
            ('balanced', 'Balanced Assistance'),
            ('high', 'High Assistance'),
        ],
        default='balanced'
    )
    ai_feedback_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('after_exercise', 'After Each Exercise'),
            ('after_lesson', 'After Each Lesson'),
        ],
        default='after_exercise'
    )
    
    # Collaboration Preferences
    allow_peer_collaboration = models.BooleanField(default=True)
    allow_mentorship = models.BooleanField(default=True)
    public_progress = models.BooleanField(default=True)
    
    # Notification Preferences
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Never'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.full_name} Preferences"


class UserActivity(models.Model):
    """Track user activities for analytics and AI personalization"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('course_start', 'Course Started'),
        ('course_complete', 'Course Completed'),
        ('lesson_start', 'Lesson Started'),
        ('lesson_complete', 'Lesson Completed'),
        ('exercise_start', 'Exercise Started'),
        ('exercise_complete', 'Exercise Completed'),
        ('ai_interaction', 'AI Interaction'),
        ('collaboration_start', 'Collaboration Started'),
        ('collaboration_end', 'Collaboration Ended'),
        ('assessment_start', 'Assessment Started'),
        ('assessment_complete', 'Assessment Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Related Objects
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    exercise_id = models.UUIDField(null=True, blank=True)
    
    # Activity Data
    duration = models.DurationField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_activity_type_display()} at {self.timestamp}"