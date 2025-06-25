from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'skills', views.UserSkillViewSet, basename='userskill')
router.register(r'learning-paths', views.UserLearningPathViewSet, basename='userlearningpath')
router.register(r'preferences', views.UserPreferencesViewSet, basename='userpreferences')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('auth/password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/avatar/', views.AvatarUploadView.as_view(), name='avatar_upload'),
    
    # Account management
    path('account/deactivate/', views.DeactivateAccountView.as_view(), name='deactivate_account'),
    path('account/delete/', views.DeleteAccountView.as_view(), name='delete_account'),
    
    # Social authentication (allauth)
    path('auth/social/', include('allauth.urls')),
    
    # ViewSet routes (includes /users/, /skills/, /learning-paths/, /preferences/)
    path('', include(router.urls)),
]

# Additional URL patterns that will be available:
# GET/POST /accounts/users/ - List/create users
# GET/PUT/PATCH/DELETE /accounts/users/{id}/ - User detail operations
# GET/PATCH /accounts/users/me/ - Current user profile
# POST /accounts/users/{id}/follow/ - Follow user
# GET /accounts/users/dashboard/ - User dashboard

# GET/POST /accounts/skills/ - List/create user skills
# GET/PUT/PATCH/DELETE /accounts/skills/{id}/ - Skill detail operations
# POST /accounts/skills/{id}/assess/ - Trigger skill assessment

# GET/POST /accounts/learning-paths/ - List/create learning paths
# GET/PUT/PATCH/DELETE /accounts/learning-paths/{id}/ - Learning path operations
# POST /accounts/learning-paths/{id}/start/ - Start learning path
# POST /accounts/learning-paths/{id}/complete/ - Complete learning path
# POST /accounts/learning-paths/generate_ai_path/ - Generate AI learning path

# GET/PUT/PATCH /accounts/preferences/ - User preferences (single object)