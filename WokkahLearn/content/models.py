# content/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class InteractiveContent(models.Model):
    """Interactive content elements for lessons"""
    
    CONTENT_TYPES = [
        ('code_editor', 'Code Editor'),
        ('quiz', 'Quiz'),
        ('drag_drop', 'Drag & Drop'),
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching Exercise'),
        ('simulation', 'Simulation'),
        ('visualization', 'Data Visualization'),
        ('virtual_lab', 'Virtual Lab'),
        ('ar_experience', 'AR Experience'),
        ('vr_environment', 'VR Environment'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson_id = models.UUIDField()  # Reference to lesson
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    # Content Configuration
    content_data = models.JSONField(default=dict)  # Flexible content structure
    settings = models.JSONField(default=dict)  # Interactive settings
    
    # Learning Objectives
    learning_objectives = models.JSONField(default=list, blank=True)
    skills_practiced = models.JSONField(default=list, blank=True)
    difficulty_level = models.CharField(max_length=20, default='medium')
    
    # Timing and Attempts
    estimated_duration = models.DurationField(default='00:10:00')
    max_attempts = models.IntegerField(default=0)  # 0 = unlimited
    time_limit = models.DurationField(null=True, blank=True)
    
    # AI Features
    ai_generated = models.BooleanField(default=False)
    ai_hints_enabled = models.BooleanField(default=True)
    ai_feedback_enabled = models.BooleanField(default=True)
    
    # Analytics
    completion_rate = models.FloatField(default=0.0)
    average_score = models.FloatField(default=0.0)
    average_attempts = models.FloatField(default=0.0)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'interactive_content'
        verbose_name = 'Interactive Content'
        verbose_name_plural = 'Interactive Content'
        ordering = ['lesson_id', 'order']
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"


class UserContentInteraction(models.Model):
    """Track user interactions with interactive content"""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_interactions')
    content = models.ForeignKey(InteractiveContent, on_delete=models.CASCADE, related_name='user_interactions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    
    # Attempt Information
    attempt_number = models.IntegerField(default=1)
    score = models.FloatField(null=True, blank=True)
    max_possible_score = models.FloatField(default=100.0)
    
    # User Responses and Data
    user_responses = models.JSONField(default=dict)
    interaction_data = models.JSONField(default=dict)  # Detailed interaction tracking
    
    # Timing
    time_spent = models.DurationField(default='00:00:00')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI Assistance
    hints_used = models.IntegerField(default=0)
    ai_help_requests = models.IntegerField(default=0)
    ai_feedback_received = models.JSONField(default=list, blank=True)
    
    # Learning Data
    concepts_learned = models.JSONField(default=list, blank=True)
    mistakes_made = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_content_interactions'
        verbose_name = 'User Content Interaction'
        verbose_name_plural = 'User Content Interactions'
        unique_together = ['user', 'content', 'attempt_number']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.content.title} (Attempt {self.attempt_number})"


class CodeExecutionEnvironment(models.Model):
    """Sandboxed code execution environments"""
    
    ENVIRONMENT_TYPES = [
        ('docker', 'Docker Container'),
        ('vm', 'Virtual Machine'),
        ('cloud_function', 'Cloud Function'),
        ('browser_sandbox', 'Browser Sandbox'),
    ]
    
    STATUS_CHOICES = [
        ('creating', 'Creating'),
        ('ready', 'Ready'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
        ('destroyed', 'Destroyed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_environments')
    environment_type = models.CharField(max_length=20, choices=ENVIRONMENT_TYPES, default='docker')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='creating')
    
    # Configuration
    programming_language = models.CharField(max_length=50)
    runtime_version = models.CharField(max_length=20)
    base_image = models.CharField(max_length=200)
    
    # Resources
    cpu_limit = models.FloatField(default=1.0)  # CPU cores
    memory_limit = models.IntegerField(default=512)  # MB
    disk_limit = models.IntegerField(default=1024)  # MB
    execution_timeout = models.IntegerField(default=30)  # seconds
    
    # Environment Data
    container_id = models.CharField(max_length=200, blank=True)
    environment_url = models.URLField(blank=True)
    access_token = models.CharField(max_length=100, blank=True)
    
    # File System
    workspace_files = models.JSONField(default=dict)  # File structure
    installed_packages = models.JSONField(default=list)
    environment_variables = models.JSONField(default=dict)
    
    # Usage Tracking
    total_executions = models.IntegerField(default=0)
    total_runtime = models.DurationField(default='00:00:00')
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Cleanup
    auto_destroy_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_execution_environments'
        verbose_name = 'Code Execution Environment'
        verbose_name_plural = 'Code Execution Environments'
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.programming_language} Environment"


class CodeExecution(models.Model):
    """Individual code execution records"""
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    environment = models.ForeignKey(CodeExecutionEnvironment, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    # Code Information
    source_code = models.TextField()
    filename = models.CharField(max_length=200, default='main.py')
    input_data = models.TextField(blank=True)
    
    # Execution Results
    output = models.TextField(blank=True)
    error_output = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    
    # Performance Metrics
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    memory_used = models.IntegerField(null=True, blank=True)  # bytes
    cpu_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Test Results (if applicable)
    test_cases_passed = models.IntegerField(default=0)
    test_cases_total = models.IntegerField(default=0)
    test_results = models.JSONField(default=list, blank=True)
    
    # Context
    lesson_id = models.UUIDField(null=True, blank=True)
    exercise_id = models.UUIDField(null=True, blank=True)
    collaboration_session_id = models.UUIDField(null=True, blank=True)
    
    executed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'code_executions'
        verbose_name = 'Code Execution'
        verbose_name_plural = 'Code Executions'
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"Execution {self.id} - {self.status}"


class MediaContent(models.Model):
    """Media files associated with courses and lessons"""
    
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('presentation', 'Presentation'),
        ('interactive', 'Interactive Media'),
        ('simulation', 'Simulation'),
        ('ar_model', 'AR Model'),
        ('vr_scene', 'VR Scene'),
    ]
    
    PROCESSING_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='pending')
    
    # File Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    original_filename = models.CharField(max_length=200)
    file_url = models.URLField()
    file_size = models.BigIntegerField()  # bytes
    mime_type = models.CharField(max_length=100)
    
    # Media Specific Properties
    duration = models.DurationField(null=True, blank=True)  # for video/audio
    dimensions = models.JSONField(default=dict, blank=True)  # width/height for images/videos
    resolution = models.CharField(max_length=20, blank=True)  # e.g., "1920x1080"
    
    # Processing Results
    thumbnail_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)
    transcoded_urls = models.JSONField(default=dict, blank=True)  # Different quality versions
    
    # AI Analysis
    ai_generated_metadata = models.JSONField(default=dict, blank=True)
    ai_transcription = models.TextField(blank=True)  # for video/audio
    ai_tags = models.JSONField(default=list, blank=True)
    
    # Usage and Relations
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    content_id = models.UUIDField(null=True, blank=True)
    
    # Access Control
    is_public = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'media_content'
        verbose_name = 'Media Content'
        verbose_name_plural = 'Media Content'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"


class ContentTemplate(models.Model):
    """Reusable content templates for quick course creation"""
    
    TEMPLATE_TYPES = [
        ('lesson', 'Lesson Template'),
        ('quiz', 'Quiz Template'),
        ('exercise', 'Exercise Template'),
        ('project', 'Project Template'),
        ('assessment', 'Assessment Template'),
        ('module', 'Module Template'),
    ]
    
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('data_science', 'Data Science'),
        ('web_development', 'Web Development'),
        ('mobile_development', 'Mobile Development'),
        ('devops', 'DevOps'),
        ('machine_learning', 'Machine Learning'),
        ('system_design', 'System Design'),
        ('algorithms', 'Algorithms'),
        ('databases', 'Databases'),
        ('security', 'Security'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    
    # Template Information
    name = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    
    # Template Structure
    template_data = models.JSONField(default=dict)  # The actual template structure
    default_settings = models.JSONField(default=dict)
    required_fields = models.JSONField(default=list)
    
    # Customization Options
    customizable_fields = models.JSONField(default=list)
    ai_customization_enabled = models.BooleanField(default=True)
    
    # Usage and Quality
    usage_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # AI Generation
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_templates'
        verbose_name = 'Content Template'
        verbose_name_plural = 'Content Templates'
        ordering = ['-usage_count', '-rating']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class UserGeneratedContent(models.Model):
    """Content created by users (community contributions)"""
    
    CONTENT_TYPES = [
        ('tutorial', 'Tutorial'),
        ('solution', 'Solution'),
        ('explanation', 'Explanation'),
        ('tip', 'Tip/Trick'),
        ('resource', 'Resource'),
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('review', 'Review'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('featured', 'Featured'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Content Information
    title = models.CharField(max_length=200)
    content = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    
    # Relations
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    parent_content_id = models.UUIDField(null=True, blank=True)  # For replies/responses
    
    # Engagement
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    
    # Moderation
    reported_count = models.IntegerField(default=0)
    moderation_notes = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='moderated_content'
    )
    
    # AI Analysis
    ai_quality_score = models.FloatField(default=0.0)
    ai_content_tags = models.JSONField(default=list, blank=True)
    ai_moderation_flags = models.JSONField(default=list, blank=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_content')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_generated_content'
        verbose_name = 'User Generated Content'
        verbose_name_plural = 'User Generated Content'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.full_name}"


class ContentVersioning(models.Model):
    """Version control for content changes"""
    
    CONTENT_MODEL_CHOICES = [
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('interactive_content', 'Interactive Content'),
        ('media_content', 'Media Content'),
        ('template', 'Template'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_model = models.CharField(max_length=30, choices=CONTENT_MODEL_CHOICES)
    content_id = models.UUIDField()
    version_number = models.IntegerField()
    
    # Version Data
    content_snapshot = models.JSONField()  # Full content at this version
    changes_summary = models.TextField(blank=True)
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('create', 'Created'),
            ('update', 'Updated'),
            ('delete', 'Deleted'),
            ('restore', 'Restored'),
        ]
    )
    
    # Change Details
    fields_changed = models.JSONField(default=list)
    diff_data = models.JSONField(default=dict)  # Detailed changes
    
    # Author and Approval
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_versions')
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_versions'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # AI Assistance
    ai_assisted = models.BooleanField(default=False)
    ai_suggestions_used = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_versioning'
        verbose_name = 'Content Version'
        verbose_name_plural = 'Content Versions'
        unique_together = ['content_model', 'content_id', 'version_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.content_model} {self.content_id} v{self.version_number}"