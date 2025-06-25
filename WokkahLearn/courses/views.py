from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg, Count, Sum, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from datetime import timedelta, datetime
import logging

from .models import (
    Category, Course, CourseModule, Lesson, CourseEnrollment,
    LessonProgress, CourseReview, CourseWishlist, LearningPath,
    LearningPathCourse
)
from .serializers import (
    CategorySerializer, CourseSerializer, CourseModuleSerializer,
    LessonSerializer, CourseEnrollmentSerializer, LessonProgressSerializer,
    CourseReviewSerializer, LearningPathSerializer
)
from .tasks import (
    send_enrollment_confirmation, update_course_analytics,
    generate_certificate, send_course_completion_notification
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Don't paginate categories
    
    def get_queryset(self):
        # Only show parent categories by default
        if self.action == 'list':
            return Category.objects.filter(parent=None).order_by('display_order', 'name')
        return super().get_queryset()
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """Get courses in this category"""
        category = self.get_object()
        courses = Course.objects.filter(
            category=category,
            status='published'
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(courses, request)
        
        serializer = CourseSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured categories"""
        categories = Category.objects.filter(is_featured=True).order_by('display_order')
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['created_at', 'title', 'price', 'average_rating', 'enrollment_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related(
            'instructor', 'category'
        ).prefetch_related('modules__lessons')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by price
        is_free = self.request.query_params.get('is_free')
        if is_free == 'true':
            queryset = queryset.filter(is_free=True)
        elif is_free == 'false':
            queryset = queryset.filter(is_free=False)
        
        # Price range filters
        price_min = self.request.query_params.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        
        price_max = self.request.query_params.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Filter by instructor
        instructor = self.request.query_params.get('instructor')
        if instructor:
            queryset = queryset.filter(instructor__id=instructor)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """Get course details and increment view count"""
        course = self.get_object()
        
        # Increment view count
        Course.objects.filter(pk=course.pk).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll user in course"""
        course = self.get_object()
        
        # Check if already enrolled
        enrollment, created = CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'active'}
        )
        
        if not created:
            return Response({
                'message': 'Already enrolled in this course',
                'enrollment': CourseEnrollmentSerializer(enrollment).data
            })
        
        # Check subscription access for paid courses
        if not course.is_free and not request.user.subscription_active:
            enrollment.delete()  # Remove the enrollment we just created
            return Response({
                'error': 'Premium subscription required for this course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Update course enrollment count
        Course.objects.filter(pk=course.pk).update(enrollment_count=F('enrollment_count') + 1)
        
        # Send enrollment confirmation email
        send_enrollment_confirmation.delay(request.user.id, course.id)
        
        return Response({
            'message': 'Successfully enrolled in course',
            'enrollment': CourseEnrollmentSerializer(enrollment).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def progress(self, request, pk=None):
        """Get user's progress in course"""
        course = self.get_object()
        
        try:
            enrollment = CourseEnrollment.objects.get(user=request.user, course=course)
            lesson_progress = LessonProgress.objects.filter(enrollment=enrollment)
            
            return Response({
                'enrollment': CourseEnrollmentSerializer(enrollment).data,
                'lesson_progress': LessonProgressSerializer(lesson_progress, many=True).data,
                'total_lessons': course.total_lessons,
                'completed_lessons': lesson_progress.filter(completed=True).count()
            })
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Not enrolled in this course'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_to_wishlist(self, request, pk=None):
        """Add course to user's wishlist"""
        course = self.get_object()
        
        wishlist_item, created = CourseWishlist.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if created:
            return Response({'message': 'Added to wishlist'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already in wishlist'})
    
    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def remove_from_wishlist(self, request, pk=None):
        """Remove course from user's wishlist"""
        course = self.get_object()
        
        try:
            wishlist_item = CourseWishlist.objects.get(user=request.user, course=course)
            wishlist_item.delete()
            return Response({'message': 'Removed from wishlist'})
        except CourseWishlist.DoesNotExist:
            return Response({'error': 'Not in wishlist'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get course reviews with pagination"""
        course = self.get_object()
        reviews = CourseReview.objects.filter(course=course).order_by('-created_at')
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(reviews, request)
        
        serializer = CourseReviewSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request, pk=None):
        """Get course analytics (instructor only)"""
        course = self.get_object()
        
        if course.instructor != request.user and request.user not in course.co_instructors.all():
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate analytics
        enrollments = CourseEnrollment.objects.filter(course=course)
        completed_enrollments = enrollments.filter(status='completed')
        
        analytics = {
            'total_enrollments': enrollments.count(),
            'active_enrollments': enrollments.filter(status='active').count(),
            'completed_enrollments': completed_enrollments.count(),
            'completion_rate': (completed_enrollments.count() / enrollments.count() * 100) if enrollments.count() > 0 else 0,
            'average_rating': course.average_rating,
            'total_reviews': course.rating_count,
            'total_revenue': enrollments.count() * course.price if not course.is_free else 0,
            'average_time_to_complete': completed_enrollments.aggregate(
                avg_time=Avg('total_time_spent')
            )['avg_time'],
            'monthly_enrollments': enrollments.filter(
                enrolled_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        return Response(analytics)


class CourseModuleViewSet(viewsets.ModelViewSet):
    serializer_class = CourseModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if course_id:
            return CourseModule.objects.filter(course__id=course_id).order_by('order')
        return CourseModule.objects.all()


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        module_id = self.request.query_params.get('module')
        if module_id:
            return Lesson.objects.filter(module__id=module_id).order_by('order')
        return Lesson.objects.all()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        """Start a lesson"""
        lesson = self.get_object()
        
        # Check if user is enrolled in the course
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course to start lesson'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create or update lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={
                'started': True,
                'started_at': timezone.now()
            }
        )
        
        if not lesson_progress.started:
            lesson_progress.started = True
            lesson_progress.started_at = timezone.now()
            lesson_progress.save()
        
        # Update current lesson in enrollment
        enrollment.current_lesson = lesson
        enrollment.save()
        
        return Response({
            'message': 'Lesson started',
            'progress': LessonProgressSerializer(lesson_progress).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        """Complete a lesson"""
        lesson = self.get_object()
        
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course to complete lesson'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        # Mark as completed
        lesson_progress.completed = True
        lesson_progress.completed_at = timezone.now()
        if not lesson_progress.started:
            lesson_progress.started = True
            lesson_progress.started_at = timezone.now()
        
        lesson_progress.save()
        
        # Update enrollment progress
        enrollment.update_progress()
        
        # Check if course is completed
        if enrollment.progress_percentage >= 100:
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            enrollment.save()
            
            # Update user stats
            enrollment.user.courses_completed = F('courses_completed') + 1
            enrollment.user.save()
            
            # Send completion notification
            send_course_completion_notification.delay(enrollment.user.id, enrollment.course.id)
            
            # Generate certificate
            generate_certificate.delay(enrollment.user.id, enrollment.course.id)
        
        return Response({
            'message': 'Lesson completed',
            'progress': LessonProgressSerializer(lesson_progress).data,
            'course_progress': enrollment.progress_percentage
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        """Bookmark/unbookmark a lesson"""
        lesson = self.get_object()
        
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course to bookmark lesson'
            }, status=status.HTTP_403_FORBIDDEN)
        
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        lesson_progress.bookmarked = not lesson_progress.bookmarked
        lesson_progress.save()
        
        return Response({
            'message': f"Lesson {'bookmarked' if lesson_progress.bookmarked else 'unbookmarked'}",
            'bookmarked': lesson_progress.bookmarked
        })


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CourseEnrollment.objects.filter(user=self.request.user).order_by('-enrolled_at')
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause course enrollment"""
        enrollment = self.get_object()
        enrollment.status = 'paused'
        enrollment.save()
        
        return Response({'message': 'Course paused'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume course enrollment"""
        enrollment = self.get_object()
        if enrollment.status == 'paused':
            enrollment.status = 'active'
            enrollment.save()
            return Response({'message': 'Course resumed'})
        
        return Response({'error': 'Course is not paused'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def drop(self, request, pk=None):
        """Drop from course"""
        enrollment = self.get_object()
        enrollment.status = 'dropped'
        enrollment.save()
        
        # Update course enrollment count
        Course.objects.filter(pk=enrollment.course.pk).update(
            enrollment_count=F('enrollment_count') - 1
        )
        
        return Response({'message': 'Dropped from course'})


class CourseReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CourseReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CourseReview.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Check if user completed the course
        course = serializer.validated_data['course']
        try:
            enrollment = CourseEnrollment.objects.get(
                user=self.request.user,
                course=course,
                status='completed'
            )
            verified_completion = True
        except CourseEnrollment.DoesNotExist:
            verified_completion = False
        
        review = serializer.save(
            user=self.request.user,
            verified_completion=verified_completion
        )
        
        # Update course average rating
        update_course_analytics.delay(course.id)
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        review.helpful_votes = F('helpful_votes') + 1
        review.save()
        
        return Response({'message': 'Review marked as helpful'})


class CourseWishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CourseWishlist.objects.filter(user=self.request.user).order_by('-added_at')
    
    def get_serializer_class(self):
        # Return a simple serializer for wishlist items
        return CourseSerializer  # We'll serialize the course, not the wishlist item
    
    def list(self, request):
        """List user's wishlist courses"""
        wishlist_items = self.get_queryset()
        courses = [item.course for item in wishlist_items]
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(courses, request)
        
        serializer = CourseSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class LearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        if self.action == 'list':
            return LearningPath.objects.filter(is_public=True).order_by('-created_at')
        return LearningPath.objects.all()
    
    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """Get courses in learning path"""
        learning_path = self.get_object()
        path_courses = LearningPathCourse.objects.filter(
            learning_path=learning_path
        ).order_by('order').select_related('course')
        
        courses_data = []
        for path_course in path_courses:
            course_data = CourseSerializer(path_course.course, context={'request': request}).data
            course_data['path_order'] = path_course.order
            course_data['is_required'] = path_course.is_required
            courses_data.append(course_data)
        
        return Response(courses_data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generate_ai_path(self, request):
        """Generate AI-powered learning path"""
        from .tasks import generate_ai_learning_path
        
        prompt = request.data.get('prompt', '')
        target_skills = request.data.get('target_skills', [])
        difficulty = request.data.get('difficulty', 'intermediate')
        
        if not prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trigger AI generation task
        task = generate_ai_learning_path.delay(
            request.user.id, prompt, target_skills, difficulty
        )
        
        return Response({
            'message': 'AI learning path generation started',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


# Standalone API Views

class CourseSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Advanced course search with AI recommendations"""
        query = request.query_params.get('q', '')
        
        # Build base queryset
        queryset = Course.objects.filter(status='published')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(ai_skill_tags__contains=[query])
            )
        
        # Apply filters
        filters = {
            'category__slug': request.query_params.get('category'),
            'difficulty': request.query_params.get('difficulty'),
            'instructor__id': request.query_params.get('instructor'),
        }
        
        for key, value in filters.items():
            if value:
                queryset = queryset.filter(**{key: value})
        
        # Price filters
        is_free = request.query_params.get('is_free')
        if is_free == 'true':
            queryset = queryset.filter(is_free=True)
        elif is_free == 'false':
            queryset = queryset.filter(is_free=False)
        
        price_min = request.query_params.get('price_min')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        
        price_max = request.query_params.get('price_max')
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Sorting
        sort_by = request.query_params.get('sort', 'relevance')
        if sort_by == 'popularity':
            queryset = queryset.order_by('-enrollment_count')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # relevance
            queryset = queryset.order_by('-average_rating', '-enrollment_count')
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        serializer = CourseSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class FeaturedCoursesView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get featured courses"""
        courses = Course.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-created_at')[:12]
        
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class TrendingCoursesView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get trending courses based on recent enrollment activity"""
        # Cache trending courses for 1 hour
        cache_key = 'trending_courses'
        trending_courses = cache.get(cache_key)
        
        if not trending_courses:
            # Calculate trending based on recent enrollments and views
            one_week_ago = timezone.now() - timedelta(days=7)
            
            trending_courses = Course.objects.filter(
                status='published'
            ).annotate(
                recent_enrollments=Count(
                    'enrollments',
                    filter=Q(enrollments__enrolled_at__gte=one_week_ago)
                )
            ).order_by('-recent_enrollments', '-view_count')[:12]
            
            cache.set(cache_key, trending_courses, 3600)  # Cache for 1 hour
        
        serializer = CourseSerializer(trending_courses, many=True, context={'request': request})
        return Response(serializer.data)


class CourseRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get personalized course recommendations"""
        user = request.user
        
        # Get user's completed courses and skills
        completed_courses = CourseEnrollment.objects.filter(
            user=user,
            status='completed'
        ).values_list('course__id', flat=True)
        
        user_skills = user.skills.values_list('skill_name', flat=True)
        
        # Find courses with similar skills/tags
        recommended_courses = Course.objects.filter(
            status='published'
        ).exclude(
            id__in=completed_courses
        ).exclude(
            enrollments__user=user  # Exclude already enrolled courses
        )
        
        # Filter by user's skill level and interests
        if user_skills:
            recommended_courses = recommended_courses.filter(
                Q(ai_skill_tags__overlap=list(user_skills)) |
                Q(difficulty=user.current_skill_level)
            )
        
        # Order by rating and popularity
        recommended_courses = recommended_courses.order_by(
            '-average_rating', '-enrollment_count'
        )[:12]
        
        serializer = CourseSerializer(
            recommended_courses, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class EnrollCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_id):
        """Enroll in a specific course"""
        try:
            course = Course.objects.get(id=course_id, status='published')
        except Course.DoesNotExist:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already enrolled
        if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
            return Response({
                'error': 'Already enrolled in this course'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check subscription access
        if not course.is_free and not request.user.subscription_active:
            return Response({
                'error': 'Premium subscription required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create enrollment
        enrollment = CourseEnrollment.objects.create(
            user=request.user,
            course=course
        )
        
        # Update course stats
        Course.objects.filter(pk=course.pk).update(
            enrollment_count=F('enrollment_count') + 1
        )
        
        # Send confirmation email
        send_enrollment_confirmation.delay(request.user.id, course.id)
        
        return Response({
            'message': 'Successfully enrolled',
            'enrollment': CourseEnrollmentSerializer(enrollment).data
        }, status=status.HTTP_201_CREATED)


class CourseProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        """Get detailed course progress"""
        try:
            course = Course.objects.get(id=course_id)
            enrollment = CourseEnrollment.objects.get(user=request.user, course=course)
        except (Course.DoesNotExist, CourseEnrollment.DoesNotExist):
            return Response({
                'error': 'Course or enrollment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get lesson progress
        lesson_progress = LessonProgress.objects.filter(enrollment=enrollment)
        
        # Calculate detailed progress
        total_lessons = course.total_lessons
        completed_lessons = lesson_progress.filter(completed=True).count()
        started_lessons = lesson_progress.filter(started=True).count()
        
        progress_data = {
            'enrollment': CourseEnrollmentSerializer(enrollment).data,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'started_lessons': started_lessons,
            'progress_percentage': enrollment.progress_percentage,
            'time_spent': enrollment.total_time_spent,
            'last_accessed': enrollment.last_accessed,
            'current_lesson': enrollment.current_lesson_id,
            'lesson_progress': LessonProgressSerializer(lesson_progress, many=True).data
        }
        
        return Response(progress_data)


class CourseCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        """Get course completion certificate"""
        try:
            course = Course.objects.get(id=course_id)
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=course,
                status='completed'
            )
        except (Course.DoesNotExist, CourseEnrollment.DoesNotExist):
            return Response({
                'error': 'Course not completed or enrollment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not enrollment.completion_certificate_issued:
            # Generate certificate
            generate_certificate.delay(request.user.id, course.id)
            enrollment.completion_certificate_issued = True
            enrollment.save()
        
        # Return certificate data (in real implementation, this would be a PDF URL)
        certificate_data = {
            'course_title': course.title,
            'user_name': request.user.get_full_name(),
            'completion_date': enrollment.completed_at,
            'certificate_id': f"CERT-{enrollment.id}",
            'instructor_name': course.instructor.get_full_name(),
            # 'certificate_url': 'https://certificates.example.com/...'
        }
        
        return Response(certificate_data)


# Additional utility views

class StartLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, lesson_id):
        """Start a specific lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({
                'error': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check enrollment
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create/update lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={
                'started': True,
                'started_at': timezone.now()
            }
        )
        
        if not lesson_progress.started:
            lesson_progress.started = True
            lesson_progress.started_at = timezone.now()
            lesson_progress.save()
        
        return Response({
            'message': 'Lesson started',
            'progress': LessonProgressSerializer(lesson_progress).data
        })


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, lesson_id):
        """Complete a specific lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({
                'error': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check enrollment
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course,
                status='active'
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Mark lesson as completed
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        lesson_progress.completed = True
        lesson_progress.completed_at = timezone.now()
        if not lesson_progress.started:
            lesson_progress.started = True
            lesson_progress.started_at = timezone.now()
        
        lesson_progress.save()
        
        # Update enrollment progress
        enrollment.update_progress()
        
        return Response({
            'message': 'Lesson completed',
            'progress': LessonProgressSerializer(lesson_progress).data,
            'course_progress': enrollment.progress_percentage
        })


class BookmarkLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, lesson_id):
        """Bookmark/unbookmark a lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            return Response({
                'error': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check enrollment
        try:
            enrollment = CourseEnrollment.objects.get(
                user=request.user,
                course=lesson.module.course
            )
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Must be enrolled in course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        lesson_progress.bookmarked = not lesson_progress.bookmarked
        lesson_progress.save()
        
        return Response({
            'message': f"Lesson {'bookmarked' if lesson_progress.bookmarked else 'unbookmarked'}",
            'bookmarked': lesson_progress.bookmarked
        })