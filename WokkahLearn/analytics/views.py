from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import LearningAnalytics, UserBehaviorTracking

class PersonalAnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get personal learning analytics dashboard"""
        user = request.user
        
        # Time period
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Learning metrics
        enrollments = user.enrollments.filter(enrolled_at__gte=start_date)
        completed_courses = enrollments.filter(status='completed')
        
        # Skill development
        skills_gained = user.skills.filter(created_at__gte=start_date).count()
        
        # Time tracking
        behavior_data = UserBehaviorTracking.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        total_learning_time = behavior_data.aggregate(
            total=Sum('time_on_page')
        )['total'] or 0
        
        # AI interaction stats
        ai_sessions = user.ai_tutor_sessions.filter(
            started_at__gte=start_date
        ).count()
        
        mock_interviews = user.mock_interviews.filter(
            scheduled_at__gte=start_date
        ).count()
        
        # Progress metrics
        dashboard_data = {
            'period_days': days,
            'courses_enrolled': enrollments.count(),
            'courses_completed': completed_courses.count(),
            'completion_rate': (
                completed_courses.count() / enrollments.count() * 100
                if enrollments.count() > 0 else 0
            ),
            'skills_gained': skills_gained,
            'total_learning_time': total_learning_time,
            'ai_sessions': ai_sessions,
            'mock_interviews': mock_interviews,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'certificates_earned': completed_courses.filter(
                completion_certificate_issued=True
            ).count(),
        }
        
        return Response(dashboard_data)

class TrackEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Track user behavior event"""
        event_type = request.data.get('event_type')
        event_data = request.data.get('event_data', {})
        page_url = request.data.get('page_url', '')
        
        if not event_type:
            return Response({
                'error': 'Event type is required'
            }, status=400)
        
        # Create behavior tracking record
        UserBehaviorTracking.objects.create(
            user=request.user,
            event_type=event_type,
            event_data=event_data,
            page_url=page_url,
            session_id=request.session.session_key or '',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        return Response({'status': 'tracked'})
