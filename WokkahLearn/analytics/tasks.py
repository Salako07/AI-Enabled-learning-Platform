from celery import shared_task
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Count, Avg, Sum
from .models import LearningAnalytics, PlatformAnalytics, UserBehaviorTracking
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_daily_analytics():
    """Update daily analytics for all users and platform"""
    try:
        yesterday = date.today() - timedelta(days=1)
        
        # Update user learning analytics
        update_user_learning_analytics.delay(yesterday)
        
        # Update platform analytics
        update_platform_analytics.delay(yesterday)
        
        logger.info(f"Scheduled analytics updates for {yesterday}")
        
    except Exception as e:
        logger.error(f"Error in update_daily_analytics: {str(e)}")
        raise

@shared_task
def update_user_learning_analytics(date_str):
    """Update learning analytics for active users"""
    try:
        from accounts.models import User
        from courses.models import CourseEnrollment, LessonProgress
        
        target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        start_datetime = timezone.datetime.combine(target_date, timezone.datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        
        # Get users who were active on target date
        active_users = User.objects.filter(
            activities__timestamp__gte=start_datetime,
            activities__timestamp__lt=end_datetime
        ).distinct()
        
        for user in active_users:
            # Calculate engagement metrics
            user_activities = UserBehaviorTracking.objects.filter(
                user=user,
                timestamp__gte=start_datetime,
                timestamp__lt=end_datetime
            )
            
            engagement_metrics = {
                'total_sessions': user_activities.values('session_id').distinct().count(),
                'total_time_spent': user_activities.aggregate(
                    total=Sum('time_on_page')
                )['total'] or 0,
                'page_views': user_activities.filter(event_type='page_view').count(),
                'interactions': user_activities.exclude(event_type='page_view').count(),
            }
            
            # Calculate progress metrics
            lessons_completed = LessonProgress.objects.filter(
                enrollment__user=user,
                completed=True,
                completed_at__gte=start_datetime,
                completed_at__lt=end_datetime
            ).count()
            
            progress_metrics = {
                'lessons_completed': lessons_completed,
                'exercises_completed': user_activities.filter(
                    event_type='exercise_complete'
                ).count(),
                'assessments_taken': user_activities.filter(
                    event_type='assessment_complete'
                ).count(),
            }
            
            # Create or update analytics record
            analytics, created = LearningAnalytics.objects.get_or_create(
                user=user,
                metric_type='engagement',
                aggregation_period='daily',
                period_start=start_datetime,
                defaults={
                    'period_end': end_datetime,
                    'metrics': {**engagement_metrics, **progress_metrics}
                }
            )
            
            if not created:
                analytics.metrics.update({**engagement_metrics, **progress_metrics})
                analytics.save()
        
        logger.info(f"Updated learning analytics for {len(active_users)} users on {target_date}")
        
    except Exception as e:
        logger.error(f"Error updating user learning analytics: {str(e)}")
        raise

@shared_task
def update_platform_analytics(date_str):
    """Update platform-wide analytics"""
    try:
        from accounts.models import User
        from courses.models import Course, CourseEnrollment
        from payments.models import PaymentTransaction
        
        target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        start_datetime = timezone.datetime.combine(target_date, timezone.datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        
        # User metrics
        new_users = User.objects.filter(
            date_joined__gte=start_datetime,
            date_joined__lt=end_datetime
        ).count()
        
        active_users = User.objects.filter(
            activities__timestamp__gte=start_datetime,
            activities__timestamp__lt=end_datetime
        ).distinct().count()
        
        # Course metrics
        new_enrollments = CourseEnrollment.objects.filter(
            enrolled_at__gte=start_datetime,
            enrolled_at__lt=end_datetime
        ).count()
        
        completed_courses = CourseEnrollment.objects.filter(
            completed_at__gte=start_datetime,
            completed_at__lt=end_datetime
        ).count()
        
        # Revenue metrics
        successful_transactions = PaymentTransaction.objects.filter(
            processed_at__gte=start_datetime,
            processed_at__lt=end_datetime,
            status='succeeded'
        )
        
        daily_revenue = successful_transactions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Create analytics records
        analytics_data = [
            ('user_engagement', 'new_users', new_users),
            ('user_engagement', 'active_users', active_users),
            ('course_performance', 'new_enrollments', new_enrollments),
            ('course_performance', 'completed_courses', completed_courses),
            ('revenue_metrics', 'daily_revenue', float(daily_revenue)),
        ]
        
        for category, metric_name, value in analytics_data:
            PlatformAnalytics.objects.update_or_create(
                metric_category=category,
                metric_name=metric_name,
                date=target_date,
                defaults={'value': value}
            )
        
        logger.info(f"Updated platform analytics for {target_date}")
        
    except Exception as e:
        logger.error(f"Error updating platform analytics: {str(e)}")
        raise