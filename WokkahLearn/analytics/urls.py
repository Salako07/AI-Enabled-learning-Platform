from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'learning-analytics', views.LearningAnalyticsViewSet)
router.register(r'platform-analytics', views.PlatformAnalyticsViewSet)
router.register(r'user-behavior', views.UserBehaviorTrackingViewSet)

urlpatterns = [
    # Personal Analytics
    path('dashboard/', views.PersonalAnalyticsDashboardView.as_view(), name='personal_analytics'),
    path('progress/', views.LearningProgressView.as_view(), name='learning_progress'),
    path('time-tracking/', views.TimeTrackingView.as_view(), name='time_tracking'),
    path('skill-development/', views.SkillDevelopmentView.as_view(), name='skill_development'),
    
    # Course Analytics
    path('courses/<uuid:course_id>/analytics/', views.CourseAnalyticsView.as_view(), name='course_analytics'),
    path('content/<uuid:content_id>/analytics/', views.ContentAnalyticsView.as_view(), name='content_analytics'),
    
    # Instructor Analytics
    path('instructor/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor/courses/', views.InstructorCourseAnalyticsView.as_view(), name='instructor_course_analytics'),
    
    # Platform Analytics (Admin)
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    path('admin/revenue/', views.RevenueAnalyticsView.as_view(), name='revenue_analytics'),
    
    # Behavior Tracking
    path('track-event/', views.TrackEventView.as_view(), name='track_event'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'learning-analytics', views.LearningAnalyticsViewSet)
router.register(r'platform-analytics', views.PlatformAnalyticsViewSet)
router.register(r'user-behavior', views.UserBehaviorTrackingViewSet)

urlpatterns = [
    # Personal Analytics
    path('dashboard/', views.PersonalAnalyticsDashboardView.as_view(), name='personal_analytics'),
    path('progress/', views.LearningProgressView.as_view(), name='learning_progress'),
    path('time-tracking/', views.TimeTrackingView.as_view(), name='time_tracking'),
    path('skill-development/', views.SkillDevelopmentView.as_view(), name='skill_development'),
    
    # Course Analytics
    path('courses/<uuid:course_id>/analytics/', views.CourseAnalyticsView.as_view(), name='course_analytics'),
    path('content/<uuid:content_id>/analytics/', views.ContentAnalyticsView.as_view(), name='content_analytics'),
    
    # Instructor Analytics
    path('instructor/dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('instructor/courses/', views.InstructorCourseAnalyticsView.as_view(), name='instructor_course_analytics'),
    
    # Platform Analytics (Admin)
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    path('admin/revenue/', views.RevenueAnalyticsView.as_view(), name='revenue_analytics'),
    
    # Behavior Tracking
    path('track-event/', views.TrackEventView.as_view(), name='track_event'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]