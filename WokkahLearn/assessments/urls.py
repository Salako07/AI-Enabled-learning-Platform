from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'attempts', views.UserAssessmentAttemptViewSet)
router.register(r'coding-assessments', views.CodingAssessmentViewSet)
router.register(r'peer-reviews', views.PeerReviewViewSet)

urlpatterns = [
    # Assessment Taking
    path('<uuid:assessment_id>/start/', views.StartAssessmentView.as_view(), name='start_assessment'),
    path('<uuid:assessment_id>/submit/', views.SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('attempts/<uuid:attempt_id>/answer/', views.AnswerQuestionView.as_view(), name='answer_question'),
    
    # Coding Assessments
    path('coding/<uuid:assessment_id>/execute/', views.ExecuteCodeView.as_view(), name='execute_code'),
    path('coding/<uuid:assessment_id>/submit/', views.SubmitCodeView.as_view(), name='submit_code'),
    path('coding/test-cases/<uuid:assessment_id>/', views.GetTestCasesView.as_view(), name='get_test_cases'),
    
    # Results and Analytics
    path('attempts/<uuid:attempt_id>/results/', views.AssessmentResultsView.as_view(), name='assessment_results'),
    path('<uuid:assessment_id>/analytics/', views.AssessmentAnalyticsView.as_view(), name='assessment_analytics'),
    
    # Peer Review
    path('peer-review/<uuid:review_id>/submit/', views.SubmitPeerReviewView.as_view(), name='submit_peer_review'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
