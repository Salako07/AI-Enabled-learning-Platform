from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'interactive', views.InteractiveContentViewSet)
router.register(r'templates', views.ContentTemplateViewSet)
router.register(r'user-generated', views.UserGeneratedContentViewSet)
router.register(r'media', views.MediaContentViewSet)

urlpatterns = [
    # Interactive Content
    path('interactive/<uuid:content_id>/interact/', views.InteractContentView.as_view(), name='interact_content'),
    path('interactive/<uuid:content_id>/submit/', views.SubmitContentResponseView.as_view(), name='submit_content_response'),
    
    # Code Execution
    path('code/execute/', views.ExecuteCodeView.as_view(), name='execute_code'),
    path('code/environments/', views.CodeEnvironmentView.as_view(), name='code_environments'),
    path('code/environments/<uuid:env_id>/destroy/', views.DestroyEnvironmentView.as_view(), name='destroy_environment'),
    
    # Media Processing
    path('media/upload/', views.MediaUploadView.as_view(), name='media_upload'),
    path('media/<uuid:media_id>/process/', views.ProcessMediaView.as_view(), name='process_media'),
    
    # Templates
    path('templates/generate/', views.GenerateFromTemplateView.as_view(), name='generate_from_template'),
    
    # User Generated Content
    path('user-content/submit/', views.SubmitUserContentView.as_view(), name='submit_user_content'),
    path('user-content/<uuid:content_id>/moderate/', views.ModerateUserContentView.as_view(), name='moderate_user_content'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]
