from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tutor-sessions', views.AITutorSessionViewSet)
router.register(r'mock-interviews', views.AIMockInterviewViewSet)
router.register(r'code-reviews', views.AICodeReviewViewSet)
router.register(r'recommendations', views.AILearningRecommendationViewSet)
router.register(r'assessments', views.AISkillAssessmentViewSet)
router.register(r'learning-paths', views.AILearningPathViewSet)

urlpatterns = [
    # AI Tutor
    path('tutor/chat/', views.AITutorChatView.as_view(), name='ai_tutor_chat'),
    path('tutor/explain/', views.AIExplainView.as_view(), name='ai_explain'),
    
    # Code Analysis
    path('code/analyze/', views.CodeAnalysisView.as_view(), name='code_analysis'),
    path('code/debug/', views.CodeDebuggingView.as_view(), name='code_debugging'),
    path('code/optimize/', views.CodeOptimizationView.as_view(), name='code_optimization'),
    
    # Mock Interviews
    path('interview/schedule/', views.ScheduleMockInterviewView.as_view(), name='schedule_mock_interview'),
    path('interview/<uuid:interview_id>/start/', views.StartMockInterviewView.as_view(), name='start_mock_interview'),
    path('interview/<uuid:interview_id>/submit/', views.SubmitMockInterviewView.as_view(), name='submit_mock_interview'),
    
    # Personalization
    path('personalize/content/', views.PersonalizeContentView.as_view(), name='personalize_content'),
    path('skill-gap-analysis/', views.SkillGapAnalysisView.as_view(), name='skill_gap_analysis'),
    path('learning-path/generate/', views.GenerateLearningPathView.as_view(), name='generate_learning_path'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
