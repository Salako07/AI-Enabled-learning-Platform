# courses/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class Category(models.Model):
    """Course categories for organization"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class or name
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # SEO and Display
    meta_description = models.CharField(max_length=160, blank=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Main course model"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    TYPE_CHOICES = [
        ('course', 'Course'),
        ('learning_path', 'Learning Path'),
        ('bootcamp', 'Bootcamp'),
        ('workshop', 'Workshop'),
        ('certification', 'Certification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Content and Structure
    course_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='course')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # Instructors and Authors
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses')
    co_instructors = models.ManyToManyField(User, blank=True, related_name='co_taught_courses')
    
    # Media and Assets
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    preview_video = models.URLField(blank=True)
    
    # Pricing and Access
    is_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subscription_tiers = models.JSONField(default=list, blank=True)  # ['free', 'premium', 'pro']
    
    # Learning Outcomes and Requirements
    learning_objectives = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    target_audience = models.TextField(blank=True)
    
    # Time and Completion
    estimated_duration = models.DurationField()
    estimated_effort_hours = models.FloatField(default=0.0)
    
    # AI and Personalization
    ai_generated_content = models.BooleanField(default=False)
    ai_difficulty_tags = models.JSONField(default=list, blank=True)
    ai_skill_tags = models.JSONField(default=list, blank=True)
    
    # Status and Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics and Engagement
    view_count = models.IntegerField(default=0)
    enrollment_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    
    # SEO and Marketing
    meta_description = models.CharField(max_length=160, blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_lessons(self):
        return self.modules.aggregate(
            total=models.Sum('lessons__count')
        )['total'] or 0
    
    def get_enrollment_for_user(self, user):
        """Get enrollment for a specific user"""
        try:
            return self.enrollments.get(user=user)
        except CourseEnrollment.DoesNotExist:
            return None


class CourseModule(models.Model):
    """Course modules/chapters"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    # Access Control
    is_preview = models.BooleanField(default=False)
    unlock_condition = models.JSONField(default=dict, blank=True)  # Conditions to unlock this module
    
    # Estimated time
    estimated_duration = models.DurationField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_modules'
        verbose_name = 'Course Module'
        verbose_name_plural = 'Course Modules'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lessons within modules"""
    
    LESSON_TYPES = [
        ('text', 'Text Lesson'),
        ('video', 'Video Lesson'),
        ('interactive', 'Interactive Lesson'),
        ('quiz', 'Quiz'),
        ('coding_exercise', 'Coding Exercise'),
        ('project', 'Project'),
        ('live_session', 'Live Session'),
        ('ai_tutor', 'AI Tutor Session'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    content = models.TextField(blank=True)  # Main lesson content
    order = models.IntegerField(default=0)
    
    # Media and Resources
    video_url = models.URLField(blank=True)
    video_duration = models.DurationField(null=True, blank=True)
    slides_url = models.URLField(blank=True)
    resources = models.JSONField(default=list, blank=True)  # Additional resources/links
    
    # Interactive Elements
    has_coding_environment = models.BooleanField(default=False)
    coding_language = models.CharField(max_length=50, blank=True)
    starter_code = models.TextField(blank=True)
    solution_code = models.TextField(blank=True)
    
    # AI Features
    ai_generated = models.BooleanField(default=False)
    ai_difficulty_score = models.FloatField(default=0.0)
    ai_concepts = models.JSONField(default=list, blank=True)
    
    # Access and Prerequisites
    is_preview = models.BooleanField(default=False)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Time Estimation
    estimated_duration = models.DurationField()
    
    # Analytics
    view_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"


class CourseEnrollment(models.Model):
    """Track course enrollments and progress"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('dropped', 'Dropped'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # Progress Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.FloatField(default=0.0)
    current_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Time Tracking
    total_time_spent = models.DurationField(default='00:00:00')
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Completion Data
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_certificate_issued = models.BooleanField(default=False)
    
    # Payment and Access
    access_expires_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # AI Personalization
    ai_learning_path = models.JSONField(default=dict, blank=True)
    ai_recommendations = models.JSONField(default=list, blank=True)
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_enrollments'
        verbose_name = 'Course Enrollment'
        verbose_name_plural = 'Course Enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.course.title}"
    
    def update_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            self.progress_percentage = 0.0
        else:
            completed_lessons = self.lesson_progress.filter(completed=True).count()
            self.progress_percentage = (completed_lessons / total_lessons) * 100
        self.save()


class LessonProgress(models.Model):
    """Track individual lesson progress for each enrollment"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    
    # Progress Data
    started = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    time_spent = models.DurationField(default='00:00:00')
    
    # Interaction Data
    video_watch_percentage = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)
    bookmarked = models.BooleanField(default=False)
    
    # AI Assistance
    ai_help_requests = models.IntegerField(default=0)
    ai_hints_used = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lesson_progress'
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        return f"{self.enrollment.user.full_name} - {self.lesson.title}"


class CourseReview(models.Model):
    """Course reviews and ratings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    
    # Rating and Review
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField()
    
    # Detailed Ratings
    content_quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    instructor_quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    difficulty_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Verification
    verified_completion = models.BooleanField(default=False)
    
    # Engagement
    helpful_votes = models.IntegerField(default=0)
    reported = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_reviews'
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
        unique_together = ['course', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.user.full_name} ({self.rating}/5)"


class CourseWishlist(models.Model):
    """User course wishlist"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')
    
    # Notification preferences
    notify_on_discount = models.BooleanField(default=True)
    notify_on_update = models.BooleanField(default=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_wishlist'
        verbose_name = 'Course Wishlist'
        verbose_name_plural = 'Course Wishlist'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.course.title}"


class LearningPath(models.Model):
    """Structured learning paths with multiple courses"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('mixed', 'Mixed Level'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    
    # Structure
    courses = models.ManyToManyField(Course, through='LearningPathCourse')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    # AI Generation
    ai_generated = models.BooleanField(default=False)
    ai_generation_prompt = models.TextField(blank=True)
    
    # Metadata
    estimated_duration = models.DurationField()
    target_skills = models.JSONField(default=list, blank=True)
    career_outcomes = models.JSONField(default=list, blank=True)
    
    # Visibility and Access
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_learning_paths')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        verbose_name = 'Learning Path'
        verbose_name_plural = 'Learning Paths'
    
    def __str__(self):
        return self.title


class LearningPathCourse(models.Model):
    """Courses within learning paths with order and prerequisites"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    
    # Requirements
    is_required = models.BooleanField(default=True)
    unlock_condition = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_path_courses'
        verbose_name = 'Learning Path Course'
        verbose_name_plural = 'Learning Path Courses'
        unique_together = ['learning_path', 'course']
        ordering = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.title} - {self.course.title}"