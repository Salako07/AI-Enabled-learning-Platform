from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from datetime import timedelta, datetime
import logging
from .models import User, UserActivity, UserLearningPath, UserSkill

logger = logging.getLogger(__name__)


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new users"""
    try:
        user = User.objects.get(id=user_id)
        subject = 'Welcome to Wokkah Learning Platform!'
        message = f"""
        Hi {user.first_name},
        
        Welcome to Wokkah Learning Platform! We're excited to have you join our community of learners.
        
        Here are some next steps to get you started:
        1. Complete your profile setup
        2. Take our skill assessment
        3. Browse our course catalog
        4. Set your learning goals
        
        Happy learning!
        
        The Wokkah Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to user {user.email}")
        return f"Welcome email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to send welcome email to user {user_id}: {str(e)}")
        return f"Failed to send email: {str(e)}"


@shared_task
def send_learning_reminder_email(user_id):
    """Send learning reminder to inactive users"""
    try:
        user = User.objects.get(id=user_id)
        
        # Check if user has been inactive for more than 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        if user.last_active > three_days_ago:
            return f"User {user.email} is still active, no reminder needed"
        
        subject = 'We miss you at Wokkah!'
        message = f"""
        Hi {user.first_name},
        
        We noticed you haven't been active on Wokkah Learning Platform recently. 
        Don't let your learning momentum slip away!
        
        Your current progress:
        - Courses completed: {user.courses_completed}
        - Current streak: {user.current_streak} days
        - Longest streak: {user.longest_streak} days
        
        Continue your learning journey today!
        
        Best regards,
        The Wokkah Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Learning reminder sent to user {user.email}")
        return f"Reminder email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to send reminder email to user {user_id}: {str(e)}")
        return f"Failed to send email: {str(e)}"


@shared_task
def update_user_learning_statistics():
    """Update learning statistics for all users"""
    try:
        updated_count = 0
        
        for user in User.objects.filter(is_active=True):
            # Calculate total learning time from activities
            learning_activities = UserActivity.objects.filter(
                user=user,
                activity_type__in=['lesson_complete', 'exercise_complete'],
                duration__isnull=False
            )
            
            total_time = sum([activity.duration for activity in learning_activities], timedelta())
            
            # Update completed courses count
            completed_courses = UserLearningPath.objects.filter(
                user=user,
                status='completed'
            ).count()
            
            # Calculate current streak
            current_streak = calculate_current_streak(user)
            
            # Update user statistics
            user.total_learning_time = total_time
            user.courses_completed = completed_courses
            user.current_streak = current_streak
            
            if current_streak > user.longest_streak:
                user.longest_streak = current_streak
            
            user.save()
            updated_count += 1
        
        logger.info(f"Updated learning statistics for {updated_count} users")
        return f"Updated statistics for {updated_count} users"
        
    except Exception as e:
        logger.error(f"Failed to update learning statistics: {str(e)}")
        return f"Failed to update statistics: {str(e)}"


def calculate_current_streak(user):
    """Calculate current learning streak for a user"""
    today = timezone.now().date()
    current_streak = 0
    
    for i in range(365):  # Check up to 365 days back
        check_date = today - timedelta(days=i)
        
        # Check if user had learning activity on this date
        had_activity = UserActivity.objects.filter(
            user=user,
            timestamp__date=check_date,
            activity_type__in=['lesson_complete', 'exercise_complete']
        ).exists()
        
        if had_activity:
            current_streak += 1
        else:
            break
    
    return current_streak


@shared_task
def generate_ai_learning_path(user_id, prompt, target_skills, difficulty_level):
    """Generate AI-powered learning path (mock implementation)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Mock AI generation - in real implementation, this would call AI service
        # This is a simplified version for demonstration
        learning_modules = []
        
        if 'python' in prompt.lower():
            learning_modules = [
                'Python Basics',
                'Data Structures',
                'Object-Oriented Programming',
                'Web Development with Django',
                'API Development'
            ]
        elif 'javascript' in prompt.lower():
            learning_modules = [
                'JavaScript Fundamentals',
                'DOM Manipulation',
                'Async Programming',
                'React Framework',
                'Node.js Backend'
            ]
        else:
            learning_modules = [
                'Programming Fundamentals',
                'Problem Solving',
                'Data Structures',
                'Algorithms',
                'Project Development'
            ]
        
        # Create learning path
        learning_path = UserLearningPath.objects.create(
            user=user,
            name=f"AI Generated: {prompt[:50]}",
            description=f"Customized learning path based on your goals: {prompt}",
            is_ai_generated=True,
            ai_generation_prompt=prompt,
            difficulty_level=difficulty_level,
            target_skills=target_skills,
            estimated_duration=timedelta(hours=len(learning_modules) * 8)  # 8 hours per module
        )
        
        logger.info(f"AI learning path generated for user {user.email}")
        return f"Learning path '{learning_path.name}' created for user {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to generate AI learning path for user {user_id}: {str(e)}")
        return f"Failed to generate learning path: {str(e)}"


@shared_task
def send_weekly_progress_report():
    """Send weekly progress reports to users"""
    try:
        one_week_ago = timezone.now() - timedelta(days=7)
        sent_count = 0
        
        for user in User.objects.filter(
            is_active=True,
            email_notifications=True,
            preferences__email_frequency='weekly'
        ):
            # Get week's activities
            week_activities = UserActivity.objects.filter(
                user=user,
                timestamp__gte=one_week_ago
            )
            
            if not week_activities.exists():
                continue
            
            # Calculate weekly stats
            lessons_completed = week_activities.filter(
                activity_type='lesson_complete'
            ).count()
            
            exercises_completed = week_activities.filter(
                activity_type='exercise_complete'
            ).count()
            
            total_time = sum([
                activity.duration for activity in week_activities 
                if activity.duration
            ], timedelta())
            
            subject = 'Your Weekly Learning Progress'
            message = f"""
            Hi {user.first_name},
            
            Here's your learning progress for this week:
            
            📚 Lessons completed: {lessons_completed}
            ✍️ Exercises completed: {exercises_completed}
            ⏰ Total learning time: {total_time}
            🔥 Current streak: {user.current_streak} days
            
            Keep up the great work!
            
            Best regards,
            The Wokkah Team
            """
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            sent_count += 1
        
        logger.info(f"Weekly progress reports sent to {sent_count} users")
        return f"Progress reports sent to {sent_count} users"
        
    except Exception as e:
        logger.error(f"Failed to send weekly progress reports: {str(e)}")
        return f"Failed to send reports: {str(e)}"


@shared_task
def cleanup_old_user_activities():
    """Clean up user activities older than 6 months"""
    try:
        six_months_ago = timezone.now() - timedelta(days=180)
        
        old_activities = UserActivity.objects.filter(
            timestamp__lt=six_months_ago
        )
        
        deleted_count = old_activities.count()
        old_activities.delete()
        
        logger.info(f"Cleaned up {deleted_count} old user activities")
        return f"Cleaned up {deleted_count} old activities"
        
    except Exception as e:
        logger.error(f"Failed to cleanup old activities: {str(e)}")
        return f"Failed to cleanup: {str(e)}"


@shared_task
def assess_user_skills_with_ai(user_id, skill_names):
    """Assess user skills using AI (mock implementation)"""
    try:
        user = User.objects.get(id=user_id)
        
        for skill_name in skill_names:
            skill, created = UserSkill.objects.get_or_create(
                user=user,
                skill_name=skill_name
            )
            
            # Mock AI assessment - in real implementation, this would analyze user's code/activities
            # Generate random but realistic assessment
            import random
            
            # Base assessment on user's overall skill level
            base_level = {
                'beginner': 1,
                'intermediate': 3,
                'advanced': 4,
                'expert': 5
            }.get(user.current_skill_level, 2)
            
            # Add some variance
            assessed_level = max(1, min(5, base_level + random.randint(-1, 1)))
            confidence = random.uniform(0.7, 0.95)
            
            skill.proficiency_level = assessed_level
            skill.ai_confidence_score = confidence
            skill.assessment_data = {
                'assessment_method': 'ai_analysis',
                'factors_analyzed': ['code_quality', 'problem_solving', 'best_practices'],
                'assessment_date': timezone.now().isoformat()
            }
            skill.save()
        
        logger.info(f"AI skill assessment completed for user {user.email}")
        return f"Skills assessed for user {user.email}: {', '.join(skill_names)}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to assess skills for user {user_id}: {str(e)}")
        return f"Failed to assess skills: {str(e)}"


@shared_task
def send_course_completion_certificate(user_id, course_id):
    """Send course completion certificate via email"""
    try:
        user = User.objects.get(id=user_id)
        learning_path = UserLearningPath.objects.get(id=course_id, user=user)
        
        subject = f'Certificate of Completion - {learning_path.name}'
        message = f"""
        Congratulations {user.first_name}!
        
        You have successfully completed the course: {learning_path.name}
        
        Course Details:
        - Duration: {learning_path.actual_duration or learning_path.estimated_duration}
        - Difficulty Level: {learning_path.get_difficulty_level_display()}
        - Completion Date: {timezone.now().strftime('%B %d, %Y')}
        
        Your certificate is attached to this email.
        
        Keep up the excellent work!
        
        Best regards,
        The Wokkah Team
        """
        
        # In a real implementation, you would generate and attach a PDF certificate
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        logger.info(f"Certificate sent to user {user.email} for course {learning_path.name}")
        return f"Certificate sent to {user.email}"
        
    except (User.DoesNotExist, UserLearningPath.DoesNotExist):
        logger.error(f"User or course not found: user_id={user_id}, course_id={course_id}")
        return "User or course not found"
    except Exception as e:
        logger.error(f"Failed to send certificate: {str(e)}")
        return f"Failed to send certificate: {str(e)}"


# Periodic tasks (these would be configured in Django settings or Celery beat schedule)
@shared_task
def daily_learning_reminders():
    """Send daily learning reminders to inactive users"""
    three_days_ago = timezone.now() - timedelta(days=3)
    inactive_users = User.objects.filter(
        is_active=True,
        last_active__lt=three_days_ago,
        email_notifications=True
    )
    
    for user in inactive_users:
        send_learning_reminder_email.delay(user.id)
    
    return f"Scheduled reminders for {inactive_users.count()} inactive users"


@shared_task
def weekly_statistics_update():
    """Weekly task to update all user statistics"""
    update_user_learning_statistics.delay()
    send_weekly_progress_report.delay()
    return "Weekly statistics update initiated"


@shared_task
def monthly_cleanup():
    """Monthly cleanup tasks"""
    cleanup_old_user_activities.delay()
    return "Monthly cleanup initiated"