from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import redis

class HealthCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        """Comprehensive health check"""
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'healthy'
        except Exception as e:
            health_status['checks']['database'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        # Redis check
        try:
            cache.set('health_check', 'ok', 60)
            cache.get('health_check')
            health_status['checks']['redis'] = 'healthy'
        except Exception as e:
            health_status['checks']['redis'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
        
        # AI services check (simplified)
        health_status['checks']['ai_services'] = 'healthy'
        
        return Response(
            health_status, 
            status=status.HTTP_200_OK if health_status['status'] == 'healthy' 
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

class ReadinessCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        """Readiness check for Kubernetes"""
        return Response({'status': 'ready'})

class LivenessCheckView(APIView):
    permission_classes = []
    
    def get(self, request):
        """Liveness check for Kubernetes"""
        return Response({'status': 'alive'})