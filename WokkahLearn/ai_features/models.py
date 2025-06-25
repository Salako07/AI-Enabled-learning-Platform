from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class AITutorSession(models.Model):
    """AI Tutor interactions and sessions"""
    
    SESSION_TYPES = [
        ('coding_help', 'Coding Help'),
        ('concept_explanation', 'Concept Explanation'),
        ('debugging', 'Debugging Assistance'),
        ('code_review', 'Code Review'),
        ('interview_prep', 'Interview Preparation'),
        ('project_guidance', 'Project Guidance'),
        ('career_advice', 'Career Advice'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_tutor_sessions')
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Context
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    topic = models.CharField(max_length=200, blank=True)
    programming_language = models.CharField(max_length=50, blank=True)
    
    # AI Configuration
    ai_model = models.CharField(max_length=50, default='gpt-4')
    ai_temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=2000)
    
    # Session Data
    initial_prompt = models.TextField()
    conversation_history = models.JSONField(default=list)
    user_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 rating
    
    # Metadata
    total_messages = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_tutor_sessions'
        verbose_name = 'AI Tutor Session'
        verbose_name_plural = 'AI Tutor Sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_session_type_display()}"
    
    def add_message(self, role, content, metadata=None):
        """Add a message to the conversation"""
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': str(models.DateTimeField().value_from_object(self)),
            'metadata': metadata or {}
        }
        self.conversation_history.append(message)
        self.total_messages += 1
        self.save()


class AIMockInterview(models.Model):
    """AI-powered mock interviews"""
    
    INTERVIEW_TYPES = [
        ('coding', 'Coding Interview'),
        ('system_design', 'System Design'),
        ('behavioral', 'Behavioral Interview'),
        ('api_design', 'API Design'),
        ('ood', 'Object-Oriented Design'),
        ('database_design', 'Database Design'),
        ('algorithms', 'Algorithms & Data Structures'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('staff', 'Staff Level'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mock_interviews')
    interview_type = models.CharField(max_length=30, choices=INTERVIEW_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Interview Configuration
    target_company = models.CharField(max_length=100, blank=True)
    target_role = models.CharField(max_length=100, blank=True)
    duration_minutes = models.IntegerField(default=60)
    
    # Questions and Responses
    questions = models.JSONField(default=list)
    user_responses = models.JSONField(default=list)
    interviewer_feedback = models.JSONField(default=list)
    
    # Scoring and Evaluation
    overall_score = models.FloatField(null=True, blank=True)  # 0-100
    technical_score = models.FloatField(null=True, blank=True)
    communication_score = models.FloatField(null=True, blank=True)
    problem_solving_score = models.FloatField(null=True, blank=True)
    
    # AI Analysis
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    improvement_areas = models.JSONField(default=list)
    
    # Recording and Playback
    session_recording_url = models.URLField(blank=True)
    code_submission_url = models.URLField(blank=True)
    
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_mock_interviews'
        verbose_name = 'AI Mock Interview'
        verbose_name_plural = 'AI Mock Interviews'
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.get_interview_type_display()} ({self.scheduled_at})"


class AICodeReview(models.Model):
    """AI-powered code reviews"""
    
    REVIEW_TYPES = [
        ('exercise', 'Exercise Solution'),
        ('project', 'Project Code'),
        ('general', 'General Code Review'),
        ('debugging', 'Debugging Help'),
        ('optimization', 'Code Optimization'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_code_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Code Information
    code_content = models.TextField()
    programming_language = models.CharField(max_length=50)
    file_name = models.CharField(max_length=200, blank=True)
    
    # Context
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    problem_description = models.TextField(blank=True)
    
    # AI Analysis Results
    overall_score = models.FloatField(null=True, blank=True)  # 0-100
    readability_score = models.FloatField(null=True, blank=True)
    efficiency_score = models.FloatField(null=True, blank=True)
    maintainability_score = models.FloatField(null=True, blank=True)
    
    # Detailed Feedback
    suggestions = models.JSONField(default=list)
    best_practices = models.JSONField(default=list)
    potential_bugs = models.JSONField(default=list)
    performance_issues = models.JSONField(default=list)
    security_concerns = models.JSONField(default=list)
    
    # Improved Code
    suggested_improvements = models.TextField(blank=True)
    refactored_code = models.TextField(blank=True)
    
    # AI Model Info
    ai_model_used = models.CharField(max_length=50, default='gpt-4')
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_code_reviews'
        verbose_name = 'AI Code Review'
        verbose_name_plural = 'AI Code Reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Code Review for {self.user.full_name} - {self.file_name}"


class AILearningRecommendation(models.Model):
    """AI-generated learning recommendations"""
    
    RECOMMENDATION_TYPES = [
        ('course', 'Course Recommendation'),
        ('lesson', 'Lesson Recommendation'),
        ('practice', 'Practice Recommendation'),
        ('review', 'Review Recommendation'),
        ('skill_gap', 'Skill Gap Recommendation'),
        ('career_path', 'Career Path Recommendation'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Recommendation Content
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField()  # Why this is recommended
    
    # Targeting
    target_skill = models.CharField(max_length=100, blank=True)
    current_skill_level = models.CharField(max_length=20, blank=True)
    target_skill_level = models.CharField(max_length=20, blank=True)
    
    # Links and Resources
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    external_url = models.URLField(blank=True)
    
    # AI Generation Data
    ai_confidence_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    generation_context = models.JSONField(default=dict)
    
    # User Interaction
    viewed = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    user_feedback = models.CharField(
        max_length=20,
        choices=[
            ('helpful', 'Helpful'),
            ('not_helpful', 'Not Helpful'),
            ('irrelevant', 'Irrelevant'),
        ],
        blank=True
    )
    
    # Scheduling
    expires_at = models.DateTimeField(null=True, blank=True)
    shown_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_learning_recommendations'
        verbose_name = 'AI Learning Recommendation'
        verbose_name_plural = 'AI Learning Recommendations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recommendation for {self.user.full_name}: {self.title}"


class AISkillAssessment(models.Model):
    """AI-powered skill assessments"""
    
    ASSESSMENT_TYPES = [
        ('initial', 'Initial Assessment'),
        ('periodic', 'Periodic Assessment'),
        ('skill_check', 'Skill Check'),
        ('course_completion', 'Course Completion Assessment'),
        ('certification', 'Certification Assessment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Assessment Configuration
    skill_areas = models.JSONField(default=list)  # Skills being assessed
    difficulty_level = models.CharField(max_length=20, default='adaptive')
    duration_minutes = models.IntegerField(default=30)
    
    # Questions and Responses
    questions = models.JSONField(default=list)
    user_answers = models.JSONField(default=list)
    ai_evaluation = models.JSONField(default=dict)
    
    # Results
    overall_score = models.FloatField(null=True, blank=True)  # 0-100
    skill_scores = models.JSONField(default=dict)  # Individual skill scores
    competency_level = models.CharField(max_length=20, blank=True)
    
    # AI Analysis
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    learning_recommendations = models.JSONField(default=list)
    next_steps = models.JSONField(default=list)
    
    # Adaptive Learning Data
    question_difficulty_progression = models.JSONField(default=list)
    ai_confidence_in_assessment = models.FloatField(default=0.0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_skill_assessments'
        verbose_name = 'AI Skill Assessment'
        verbose_name_plural = 'AI Skill Assessments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assessment for {self.user.full_name} - {self.get_assessment_type_display()}"


class AILearningPath(models.Model):
    """AI-generated personalized learning paths"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_learning_paths')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Path Definition
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_skills = models.JSONField(default=list)
    target_role = models.CharField(max_length=100, blank=True)
    
    # AI Generation Context
    generation_prompt = models.TextField()
    user_context = models.JSONField(default=dict)  # User's current skills, preferences, etc.
    ai_reasoning = models.TextField()
    
    # Path Structure
    learning_steps = models.JSONField(default=list)
    estimated_duration = models.DurationField()
    difficulty_progression = models.JSONField(default=list)
    
    # Progress Tracking
    current_step = models.IntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    completed_steps = models.JSONField(default=list)
    
    # Adaptive Elements
    adaptation_history = models.JSONField(default=list)  # How the path has been modified
    last_adapted = models.DateTimeField(null=True, blank=True)
    
    # Success Metrics
    engagement_score = models.FloatField(default=0.0)
    effectiveness_score = models.FloatField(default=0.0)
    user_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 rating
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_learning_paths'
        verbose_name = 'AI Learning Path'
        verbose_name_plural = 'AI Learning Paths'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Learning Path for {self.user.full_name}: {self.title}"


class AIContentGeneration(models.Model):
    """Track AI-generated content for courses and lessons"""
    
    CONTENT_TYPES = [
        ('lesson', 'Lesson Content'),
        ('quiz', 'Quiz Questions'),
        ('exercise', 'Coding Exercise'),
        ('project', 'Project Description'),
        ('explanation', 'Concept Explanation'),
        ('example', 'Code Example'),
        ('assessment', 'Assessment Questions'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('generated', 'Generated'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request Information
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_content_requests')
    generation_prompt = models.TextField()
    context_data = models.JSONField(default=dict)
    
    # Target Information
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    target_skill_level = models.CharField(max_length=20, blank=True)
    programming_language = models.CharField(max_length=50, blank=True)
    
    # Generated Content
    generated_content = models.TextField(blank=True)
    content_metadata = models.JSONField(default=dict)
    quality_score = models.FloatField(null=True, blank=True)  # 0-100
    
    # AI Model Information
    ai_model_used = models.CharField(max_length=50)
    generation_tokens = models.IntegerField(default=0)
    generation_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    generation_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Review and Approval
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_ai_content'
    )
    review_notes = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_content_generation'
        verbose_name = 'AI Content Generation'
        verbose_name_plural = 'AI Content Generation'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI {self.get_content_type_display()} for {self.requested_by.full_name}"