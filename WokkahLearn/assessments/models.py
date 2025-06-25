# assessments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Assessment(models.Model):
    """Assessments for evaluating student knowledge and skills"""
    
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('coding_challenge', 'Coding Challenge'),
        ('project', 'Project Assessment'),
        ('peer_review', 'Peer Review'),
        ('skill_test', 'Skill Test'),
        ('certification', 'Certification Exam'),
        ('placement_test', 'Placement Test'),
        ('mock_interview', 'Mock Interview'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Course and Content Relations
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    module_id = models.UUIDField(null=True, blank=True)
    
    # Assessment Configuration
    time_limit = models.DurationField(null=True, blank=True)  # null = no time limit
    max_attempts = models.IntegerField(default=1)  # 0 = unlimited
    passing_score = models.FloatField(default=70.0)  # percentage
    total_points = models.FloatField(default=100.0)
    
    # Settings
    randomize_questions = models.BooleanField(default=True)
    show_correct_answers = models.BooleanField(default=True)
    allow_review = models.BooleanField(default=True)
    immediate_feedback = models.BooleanField(default=False)
    
    # AI Features
    ai_generated = models.BooleanField(default=False)
    ai_proctoring_enabled = models.BooleanField(default=False)
    ai_grading_enabled = models.BooleanField(default=True)
    adaptive_difficulty = models.BooleanField(default=False)
    
    # Prerequisites and Requirements
    prerequisites = models.JSONField(default=list, blank=True)
    required_tools = models.JSONField(default=list, blank=True)  # e.g., specific IDEs, browsers
    
    # Analytics
    total_attempts = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    pass_rate = models.FloatField(default=0.0)
    average_completion_time = models.DurationField(null=True, blank=True)
    
    # Authoring
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_assessments'
    )
    
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    version = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessments'
        verbose_name = 'Assessment'
        verbose_name_plural = 'Assessments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"


class Question(models.Model):
    """Individual questions within assessments"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('single_choice', 'Single Choice'),
        ('true_false', 'True/False'),
        ('fill_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('coding', 'Coding Problem'),
        ('drag_drop', 'Drag and Drop'),
        ('matching', 'Matching'),
        ('ordering', 'Ordering'),
        ('file_upload', 'File Upload'),
        ('oral_response', 'Oral Response'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    
    # Question Content
    question_text = models.TextField()
    explanation = models.TextField(blank=True)
    hint = models.TextField(blank=True)
    
    # Media Attachments
    image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    audio_url = models.URLField(blank=True)
    code_snippet = models.TextField(blank=True)
    
    # Scoring
    points = models.FloatField(default=1.0)
    negative_marking = models.FloatField(default=0.0)  # Points deducted for wrong answers
    
    # Configuration
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)
    
    # AI Features
    ai_generated = models.BooleanField(default=False)
    ai_difficulty_score = models.FloatField(null=True, blank=True)
    ai_concepts = models.JSONField(default=list, blank=True)
    ai_grading_criteria = models.JSONField(default=dict, blank=True)
    
    # Analytics
    times_answered = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    average_time_spent = models.DurationField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['assessment', 'order']
        unique_together = ['assessment', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."
    
    @property
    def accuracy_rate(self):
        if self.times_answered == 0:
            return 0.0
        return (self.times_correct / self.times_answered) * 100


class QuestionOption(models.Model):
    """Answer options for multiple choice and similar questions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    
    # Option Content
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation = models.TextField(blank=True)
    
    # Media
    image_url = models.URLField(blank=True)
    
    # Configuration
    order = models.IntegerField(default=0)
    
    # Analytics
    times_selected = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'question_options'
        verbose_name = 'Question Option'
        verbose_name_plural = 'Question Options'
        ordering = ['question', 'order']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:30]}... - Option {self.order}"


class UserAssessmentAttempt(models.Model):
    """User attempts at assessments"""
    
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='attempts')
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Scoring
    total_score = models.FloatField(default=0.0)
    percentage_score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    time_remaining = models.DurationField(null=True, blank=True)
    
    # AI Proctoring Data
    proctoring_data = models.JSONField(default=dict, blank=True)
    proctoring_violations = models.JSONField(default=list, blank=True)
    proctoring_score = models.FloatField(null=True, blank=True)  # Integrity score
    
    # Grading
    auto_graded_score = models.FloatField(null=True, blank=True)
    manual_graded_score = models.FloatField(null=True, blank=True)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='graded_assessments'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    # Feedback
    instructor_feedback = models.TextField(blank=True)
    ai_feedback = models.JSONField(default=dict, blank=True)
    
    # Browser and Environment Data
    browser_info = models.JSONField(default=dict, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_assessment_attempts'
        verbose_name = 'User Assessment Attempt'
        verbose_name_plural = 'User Assessment Attempts'
        unique_together = ['user', 'assessment', 'attempt_number']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.assessment.title} (Attempt {self.attempt_number})"


class UserQuestionResponse(models.Model):
    """Individual question responses within assessment attempts"""
    
    RESPONSE_TYPES = [
        ('selected_option', 'Selected Option'),
        ('text_answer', 'Text Answer'),
        ('file_upload', 'File Upload'),
        ('code_submission', 'Code Submission'),
        ('audio_recording', 'Audio Recording'),
        ('video_recording', 'Video Recording'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(UserAssessmentAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES)
    
    # Response Data
    selected_options = models.ManyToManyField(QuestionOption, blank=True)
    text_response = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    code_submission = models.TextField(blank=True)
    audio_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    
    # Additional Response Data
    response_metadata = models.JSONField(default=dict, blank=True)
    
    # Scoring
    points_earned = models.FloatField(default=0.0)
    is_correct = models.BooleanField(null=True, blank=True)  # null for subjective questions
    
    # AI Grading
    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    
    # Manual Grading
    manual_score = models.FloatField(null=True, blank=True)
    manual_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='graded_responses'
    )
    
    # Timing and Behavior
    time_spent = models.DurationField(null=True, blank=True)
    response_changes = models.IntegerField(default=0)  # How many times answer was changed
    first_response_time = models.DurationField(null=True, blank=True)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_question_responses'
        verbose_name = 'User Question Response'
        verbose_name_plural = 'User Question Responses'
        unique_together = ['attempt', 'question']
        ordering = ['attempt', 'question__order']
    
    def __str__(self):
        return f"{self.attempt.user.full_name} - Q{self.question.order}"


class CodingAssessment(models.Model):
    """Specialized model for coding assessments"""
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('expert', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='coding_assessment')
    
    # Problem Definition
    problem_statement = models.TextField()
    input_description = models.TextField()
    output_description = models.TextField()
    constraints = models.TextField(blank=True)
    
    # Programming Configuration
    allowed_languages = models.JSONField(default=list)  # ['python', 'java', 'javascript']
    default_language = models.CharField(max_length=50, default='python')
    
    # Code Templates
    starter_code = models.JSONField(default=dict, blank=True)  # Language-specific starter code
    solution_code = models.JSONField(default=dict, blank=True)  # Reference solutions
    
    # Test Cases
    public_test_cases = models.JSONField(default=list)  # Visible to students
    private_test_cases = models.JSONField(default=list)  # Hidden test cases
    
    # Execution Limits
    time_limit_seconds = models.IntegerField(default=30)
    memory_limit_mb = models.IntegerField(default=128)
    
    # Scoring Configuration
    test_case_weights = models.JSONField(default=dict, blank=True)
    partial_credit_enabled = models.BooleanField(default=True)
    
    # AI Features
    ai_code_analysis = models.BooleanField(default=True)
    ai_similarity_check = models.BooleanField(default=True)  # Plagiarism detection
    ai_complexity_analysis = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'coding_assessments'
        verbose_name = 'Coding Assessment'
        verbose_name_plural = 'Coding Assessments'
    
    def __str__(self):
        return f"Coding Assessment: {self.assessment.title}"


class CodingSubmission(models.Model):
    """Code submissions for coding assessments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
        ('memory_exceeded', 'Memory Exceeded'),
    ]
    
    VERDICT_CHOICES = [
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('time_limit_exceeded', 'Time Limit Exceeded'),
        ('runtime_error', 'Runtime Error'),
        ('compile_error', 'Compile Error'),
        ('presentation_error', 'Presentation Error'),
        ('partial', 'Partial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(UserQuestionResponse, on_delete=models.CASCADE, related_name='code_submissions')
    coding_assessment = models.ForeignKey(CodingAssessment, on_delete=models.CASCADE, related_name='submissions')
    
    # Submission Details
    language = models.CharField(max_length=50)
    source_code = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, blank=True)
    
    # Execution Results
    test_results = models.JSONField(default=list, blank=True)
    passed_test_cases = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    memory_used = models.IntegerField(null=True, blank=True)  # bytes
    
    # Compilation and Runtime
    compile_output = models.TextField(blank=True)
    runtime_output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Scoring
    score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=100.0)
    
    # AI Analysis
    ai_complexity_analysis = models.JSONField(default=dict, blank=True)
    ai_code_quality_score = models.FloatField(null=True, blank=True)
    ai_similarity_score = models.FloatField(null=True, blank=True)  # For plagiarism detection
    ai_feedback = models.TextField(blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'coding_submissions'
        verbose_name = 'Coding Submission'
        verbose_name_plural = 'Coding Submissions'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Code Submission - {self.language} ({self.verdict})"


class PeerReview(models.Model):
    """Peer review assignments and submissions"""
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('declined', 'Declined'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='peer_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_reviews_assigned')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='peer_reviews_received')
    submission = models.ForeignKey(UserAssessmentAttempt, on_delete=models.CASCADE, related_name='peer_reviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Review Configuration
    review_criteria = models.JSONField(default=list)
    anonymous = models.BooleanField(default=True)
    
    # Review Content
    overall_score = models.FloatField(null=True, blank=True)
    criteria_scores = models.JSONField(default=dict, blank=True)
    written_feedback = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    
    # AI Assistance
    ai_generated_prompts = models.JSONField(default=list, blank=True)
    ai_feedback_quality_score = models.FloatField(null=True, blank=True)
    
    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Quality Control
    helpful_votes = models.IntegerField(default=0)
    reported = models.BooleanField(default=False)
    moderated = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'peer_reviews'
        verbose_name = 'Peer Review'
        verbose_name_plural = 'Peer Reviews'
        unique_together = ['reviewer', 'submission']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"Peer Review: {self.reviewer.full_name} reviewing {self.reviewee.full_name}"


class AssessmentAnalytics(models.Model):
    """Analytics data for assessments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE, related_name='analytics')
    
    # Participation Metrics
    total_attempts = models.IntegerField(default=0)
    unique_participants = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    # Performance Metrics
    average_score = models.FloatField(default=0.0)
    median_score = models.FloatField(default=0.0)
    highest_score = models.FloatField(default=0.0)
    lowest_score = models.FloatField(default=0.0)
    score_distribution = models.JSONField(default=dict, blank=True)
    
    # Time Metrics
    average_completion_time = models.DurationField(null=True, blank=True)
    median_completion_time = models.DurationField(null=True, blank=True)
    
    # Question Analysis
    question_difficulty_analysis = models.JSONField(default=dict, blank=True)
    most_missed_questions = models.JSONField(default=list, blank=True)
    question_discrimination_index = models.JSONField(default=dict, blank=True)
    
    # AI Insights
    ai_difficulty_prediction_accuracy = models.FloatField(null=True, blank=True)
    ai_generated_insights = models.JSONField(default=list, blank=True)
    recommended_improvements = models.JSONField(default=list, blank=True)
    
    # Quality Metrics
    reliability_coefficient = models.FloatField(null=True, blank=True)  # Cronbach's alpha
    validity_indicators = models.JSONField(default=dict, blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessment_analytics'
        verbose_name = 'Assessment Analytics'
        verbose_name_plural = 'Assessment Analytics'
    
    def __str__(self):
        return f"Analytics for {self.assessment.title}"