from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthCheckView.as_view(), name='health_check'),
    path('ready/', views.ReadinessCheckView.as_view(), name='readiness_check'),
    path('live/', views.LivenessCheckView.as_view(), name='liveness_check'),
]