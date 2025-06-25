
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# API v1 patterns
api_v1_patterns = [
    path('auth/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('content/', include('content.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('ai/', include('ai_features.urls')),
    path('analytics/', include('analytics.urls')),
    path('payments/', include('payments.urls')),
    path('assessments/', include('assessments.urls')),
    path('notifications/', include('notifications.urls')),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Routes
    path('api/v1/', include(api_v1_patterns)),
    
    # Health Check
    path('health/', include('health.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns