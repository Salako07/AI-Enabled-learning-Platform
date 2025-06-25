from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Course, CourseModule, Lesson, CourseEnrollment,
    LessonProgress, CourseReview, CourseWishlist, LearningPath,
    LearningPathCourse
)

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'is_featured', 'display_order', 'children', 'course_count'
        ]
        read_only_fields = ['id', 'children', 'course_count']
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.all(), many=True).data
        return []
    
    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class InstructorSerializer(serializers.ModelSerializer):
    """Simplified instructor serializer for course details"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'avatar', 'bio']
        read_only_fields = ['id', 'first_name', 'last_name', 'email', 'avatar', 'bio']


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'lesson_type', 'content', 'order',
            'video_url', 'video_duration', 'slides_url', 'resources',
            'has_coding_environment', 'coding_language', 'starter_code',
            'estimated_duration', 'is_preview', 'ai_generated',
            'ai_difficulty_score', 'ai_concepts', 'view_count',
            'is_completed', 'is_bookmarked', 'user_progress'
        ]
        read_only_fields = [
            'id', 'view_count', 'is_completed', 'is_bookmarked', 'user_progress'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = CourseEnrollment.objects.get(
                    user=request.user,
                    course=obj.module.course
                )
                lesson_progress = LessonProgress.objects.get(
                    enrollment=enrollment,
                    lesson=obj
                )
                return lesson_progress.completed
            except (CourseEnrollment.DoesNotExist, LessonProgress.DoesNotExist):
                return False
        return False
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = CourseEnrollment.objects.get(
                    user=request.user,
                    course=obj.module.course
                )
                lesson_progress = LessonProgress.objects.get(
                    enrollment=enrollment,
                    lesson=obj
                )
                return lesson_progress.bookmarked
            except (CourseEnrollment.DoesNotExist, LessonProgress.DoesNotExist):
                return False
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = CourseEnrollment.objects.get(
                    user=request.user,
                    course=obj.module.course
                )
                lesson_progress = LessonProgress.objects.get(
                    enrollment=enrollment,
                    lesson=obj
                )
                return LessonProgressSerializer(lesson_progress).data
            except (CourseEnrollment.DoesNotExist, LessonProgress.DoesNotExist):
                return None
        return None


class CourseModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.ReadOnlyField(source='lessons.count')
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseModule
        fields = [
            'id', 'title', 'description', 'order', 'estimated_duration',
            'is_preview', 'unlock_condition', 'lessons', 'lesson_count',
            'is_unlocked'
        ]
        read_only_fields = ['id', 'lessons', 'lesson_count', 'is_unlocked']
    
    def get_is_unlocked(self, obj):
        # Simple implementation - in real app, this would check unlock conditions
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if user is enrolled
            try:
                CourseEnrollment.objects.get(
                    user=request.user,
                    course=obj.course
                )
                return True  # Simplified - all modules unlocked for enrolled users
            except CourseEnrollment.DoesNotExist:
                return obj.is_preview
        return obj.is_preview


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for course lists"""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'course_type',
            'difficulty', 'instructor_name', 'category_name', 'thumbnail',
            'is_free', 'price', 'estimated_duration', 'estimated_effort_hours',
            'enrollment_count', 'average_rating', 'rating_count',
            'is_featured', 'is_trending', 'is_enrolled', 'is_wishlisted',
            'published_at'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseEnrollment.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
    
    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseWishlist.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(read_only=True)
    co_instructors = InstructorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    modules = CourseModuleSerializer(many=True, read_only=True)
    total_lessons = serializers.ReadOnlyField()
    user_enrollment = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'course_type', 'difficulty', 'instructor', 'co_instructors',
            'category', 'thumbnail', 'preview_video', 'is_free', 'price',
            'subscription_tiers', 'learning_objectives', 'prerequisites',
            'target_audience', 'estimated_duration', 'estimated_effort_hours',
            'ai_generated_content', 'ai_difficulty_tags', 'ai_skill_tags',
            'status', 'view_count', 'enrollment_count', 'completion_rate',
            'average_rating', 'rating_count', 'is_featured', 'is_trending',
            'modules', 'total_lessons', 'user_enrollment', 'is_enrolled',
            'is_wishlisted', 'recent_reviews', 'published_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'slug', 'view_count', 'enrollment_count', 'completion_rate',
            'average_rating', 'rating_count', 'total_lessons', 'user_enrollment',
            'is_enrolled', 'is_wishlisted', 'recent_reviews', 'published_at',
            'created_at'
        ]
    
    def get_user_enrollment(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = CourseEnrollment.objects.get(user=request.user, course=obj)
                return CourseEnrollmentSerializer(enrollment).data
            except CourseEnrollment.DoesNotExist:
                return None
        return None
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseEnrollment.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
    
    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseWishlist.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
    
    def get_recent_reviews(self, obj):
        reviews = obj.reviews.order_by('-created_at')[:3]
        return CourseReviewSerializer(reviews, many=True).data


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'course', 'course_id', 'status', 'progress_percentage',
            'current_lesson', 'total_time_spent', 'last_accessed',
            'completed_at', 'completion_certificate_issued',
            'access_expires_at', 'enrolled_at'
        ]
        read_only_fields = [
            'id', 'progress_percentage', 'total_time_spent', 'last_accessed',
            'completed_at', 'completion_certificate_issued', 'enrolled_at'
        ]


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'started', 'completed',
            'time_spent', 'video_watch_percentage', 'notes', 'bookmarked',
            'ai_help_requests', 'ai_hints_used', 'started_at',
            'completed_at', 'last_accessed'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'last_accessed'
        ]


class CourseReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar.url', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseReview
        fields = [
            'id', 'course', 'course_title', 'user_name', 'user_avatar',
            'rating', 'title', 'review_text', 'content_quality',
            'instructor_quality', 'difficulty_rating', 'verified_completion',
            'helpful_votes', 'reported', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_name', 'user_avatar', 'course_title',
            'verified_completion', 'helpful_votes', 'reported',
            'created_at', 'updated_at'
        ]


class CourseWishlistSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = CourseWishlist
        fields = [
            'id', 'course', 'notify_on_discount', 'notify_on_update',
            'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class LearningPathCourseSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = LearningPathCourse
        fields = [
            'id', 'course', 'order', 'is_required', 'unlock_condition'
        ]


class LearningPathSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    courses = LearningPathCourseSerializer(source='learningpathcourse_set', many=True, read_only=True)
    course_count = serializers.SerializerMethodField()
    total_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty',
            'creator_name', 'estimated_duration', 'target_skills',
            'career_outcomes', 'ai_generated', 'ai_generation_prompt',
            'is_public', 'courses', 'course_count', 'total_duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'creator_name', 'courses', 'course_count',
            'total_duration', 'created_at', 'updated_at'
        ]
    
    def get_course_count(self, obj):
        return obj.courses.count()
    
    def get_total_duration(self, obj):
        # Calculate total duration from all courses in the path
        total_hours = sum([
            course.estimated_effort_hours 
            for course in obj.courses.all()
        ])
        return f"{total_hours} hours"


class LearningPathCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating learning paths with course selection"""
    course_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = LearningPath
        fields = [
            'title', 'description', 'difficulty', 'target_skills',
            'career_outcomes', 'is_public', 'course_ids'
        ]
    
    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        validated_data['created_by'] = self.context['request'].user
        
        learning_path = LearningPath.objects.create(**validated_data)
        
        # Add courses to learning path
        for order, course_id in enumerate(course_ids):
            try:
                course = Course.objects.get(id=course_id, status='published')
                LearningPathCourse.objects.create(
                    learning_path=learning_path,
                    course=course,
                    order=order + 1
                )
            except Course.DoesNotExist:
                continue
        
        # Calculate estimated duration
        total_duration = sum([
            course.estimated_duration.total_seconds() / 3600
            for course in learning_path.courses.all()
        ])
        learning_path.estimated_duration = f"{total_duration:.1f} hours"
        learning_path.save()
        
        return learning_path


# Utility serializers

class CourseStatsSerializer(serializers.Serializer):
    """Serializer for course statistics"""
    total_enrollments = serializers.IntegerField()
    active_enrollments = serializers.IntegerField()
    completed_enrollments = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_enrollments = serializers.IntegerField()


class CourseSearchResultSerializer(serializers.Serializer):
    """Serializer for search results with metadata"""
    courses = CourseListSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    filters_applied = serializers.DictField()