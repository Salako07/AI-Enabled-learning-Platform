from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'modules', views.CourseModuleViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'enrollments', views.CourseEnrollmentViewSet)
router.register(r'reviews', views.CourseReviewViewSet)
router.register(r'wishlist', views.CourseWishlistViewSet)
router.register(r'learning-paths', views.LearningPathViewSet)

urlpatterns = [
    # Course Discovery
    path('search/', views.CourseSearchView.as_view(), name='course_search'),
    path('featured/', views.FeaturedCoursesView.as_view(), name='featured_courses'),
    path('trending/', views.TrendingCoursesView.as_view(), name='trending_courses'),
    path('recommendations/', views.CourseRecommendationsView.as_view(), name='course_recommendations'),
    
    # Course Interaction
    path('<uuid:course_id>/enroll/', views.EnrollCourseView.as_view(), name='enroll_course'),
    path('<uuid:course_id>/progress/', views.CourseProgressView.as_view(), name='course_progress'),
    path('<uuid:course_id>/certificate/', views.CourseCertificateView.as_view(), name='course_certificate'),
    
    # Lesson Interaction
    path('lessons/<uuid:lesson_id>/start/', views.StartLessonView.as_view(), name='start_lesson'),
    path('lessons/<uuid:lesson_id>/complete/', views.CompleteLessonView.as_view(), name='complete_lesson'),
    path('lessons/<uuid:lesson_id>/bookmark/', views.BookmarkLessonView.as_view(), name='bookmark_lesson'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]