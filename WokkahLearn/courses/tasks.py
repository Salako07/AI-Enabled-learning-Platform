from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from datetime import timedelta, datetime
import logging
import random

from .models import (
    Course, CourseEnrollment, LessonProgress, CourseReview,
    LearningPath, LearningPathCourse, Category
)
from accounts.models import User, UserActivity

logger = logging.getLogger(__name__)


@shared_task
def send_enrollment_confirmation(user_id, course_id):
    """Send enrollment confirmation email"""
    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        
        subject = f'Welcome to {course.title}!'
        message = f"""
        Hi {user.first_name},
        
        Congratulations! You have successfully enrolled in "{course.title}".
        
        Course Details:
        - Instructor: {course.instructor.get_full_name()}
        - Difficulty: {course.get_difficulty_display()}
        - Estimated Duration: {course.estimated_duration}
        - Total Lessons: {course.total_lessons}
        
        Ready to start learning? Access your course dashboard to begin your first lesson.
        
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
        
        # Log enrollment activity
        UserActivity.objects.create(
            user=user,
            activity_type='course_start',
            course_id=course.id,
            metadata={'course_title': course.title}
        )
        
        logger.info(f"Enrollment confirmation sent to {user.email} for course {course.title}")
        return f"Confirmation email sent to {user.email}"
        
    except (User.DoesNotExist, Course.DoesNotExist) as e:
        logger.error(f"User or course not found: {str(e)}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Failed to send enrollment confirmation: {str(e)}")
        return f"Failed to send email: {str(e)}"


@shared_task
def send_course_completion_notification(user_id, course_id):
    """Send course completion notification"""
    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        enrollment = CourseEnrollment.objects.get(user=user, course=course)
        
        subject = f'Congratulations! You completed {course.title}'
        message = f"""
        Amazing work, {user.first_name}!
        
        You have successfully completed "{course.title}"!
        
        Your Achievement:
        - Course: {course.title}
        - Completion Date: {enrollment.completed_at.strftime('%B %d, %Y')}
        - Time Spent: {enrollment.total_time_spent}
        - Progress: 100%
        
        Your completion certificate will be generated and available in your dashboard shortly.
        
        What's next?
        - Explore related courses
        - Share your achievement on social media
        - Leave a review to help other learners
        
        Keep up the excellent work!
        
        The Wokkah Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        # Log completion activity
        UserActivity.objects.create(
            user=user,
            activity_type='course_complete',
            course_id=course.id,
            metadata={
                'course_title': course.title,
                'completion_time': str(enrollment.total_time_spent),
                'completion_date': enrollment.completed_at.isoformat()
            }
        )
        
        logger.info(f"Course completion notification sent to {user.email}")
        return f"Completion notification sent to {user.email}"
        
    except Exception as e:
        logger.error(f"Failed to send completion notification: {str(e)}")
        return f"Failed to send notification: {str(e)}"


@shared_task
def generate_certificate(user_id, course_id):
    """Generate course completion certificate"""
    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        enrollment = CourseEnrollment.objects.get(user=user, course=course)
        
        # In a real implementation, this would generate a PDF certificate
        # For now, we'll just mark it as issued and send an email
        
        certificate_data = {
            'course_title': course.title,
            'user_name': user.get_full_name(),
            'completion_date': enrollment.completed_at,
            'certificate_id': f"WOKKAH-{enrollment.id}",
            'instructor_name': course.instructor.get_full_name(),
            'course_duration': str(course.estimated_duration),
        }
        
        # Mark certificate as issued
        enrollment.completion_certificate_issued = True
        enrollment.save()
        
        # Send certificate email
        subject = f'Your Certificate for {course.title}'
        message = f"""
        Congratulations {user.first_name}!
        
        Your certificate of completion for "{course.title}" is ready!
        
        Certificate Details:
        - Certificate ID: {certificate_data['certificate_id']}
        - Course: {course.title}
        - Instructor: {certificate_data['instructor_name']}
        - Completion Date: {enrollment.completed_at.strftime('%B %d, %Y')}
        
        You can download your certificate from your dashboard.
        
        Share your achievement with the world!
        
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
        
        logger.info(f"Certificate generated for {user.email} - Course: {course.title}")
        return f"Certificate generated for {user.email}"
        
    except Exception as e:
        logger.error(f"Failed to generate certificate: {str(e)}")
        return f"Failed to generate certificate: {str(e)}"


@shared_task
def update_course_analytics(course_id):
    """Update course analytics and ratings"""
    try:
        course = Course.objects.get(id=course_id)
        
        # Update average rating
        reviews = CourseReview.objects.filter(course=course)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            course.average_rating = round(avg_rating, 2)
            course.rating_count = reviews.count()
        
        # Update completion rate
        enrollments = CourseEnrollment.objects.filter(course=course)
        if enrollments.exists():
            completed = enrollments.filter(status='completed').count()
            total = enrollments.count()
            course.completion_rate = round((completed / total) * 100, 2)
        
        course.save()
        
        logger.info(f"Analytics updated for course: {course.title}")
        return f"Analytics updated for {course.title}"
        
    except Course.DoesNotExist:
        logger.error(f"Course with id {course_id} not found")
        return f"Course not found"
    except Exception as e:
        logger.error(f"Failed to update course analytics: {str(e)}")
        return f"Failed to update analytics: {str(e)}"


@shared_task
def generate_ai_learning_path(user_id, prompt, target_skills, difficulty_level):
    """Generate AI-powered learning path for courses"""
    try:
        user = User.objects.get(id=user_id)
        
        # Mock AI learning path generation
        # In real implementation, this would call an AI service
        
        # Determine relevant courses based on prompt and skills
        relevant_courses = []
        
        # Simple keyword matching for demonstration
        keywords_to_courses = {
            'python': ['python', 'django', 'flask', 'data science'],
            'javascript': ['javascript', 'react', 'node', 'vue'],
            'web development': ['html', 'css', 'javascript', 'react'],
            'data science': ['python', 'pandas', 'machine learning', 'statistics'],
            'machine learning': ['python', 'tensorflow', 'scikit-learn', 'deep learning'],
            'mobile': ['react native', 'flutter', 'swift', 'kotlin'],
            'devops': ['docker', 'kubernetes', 'aws', 'ci/cd'],
        }
        
        # Find courses based on prompt keywords
        matching_keywords = []
        prompt_lower = prompt.lower()
        
        for keyword, related_skills in keywords_to_courses.items():
            if keyword in prompt_lower:
                matching_keywords.extend(related_skills)
        
        # Add target skills to matching keywords
        matching_keywords.extend([skill.lower() for skill in target_skills])
        
        # Find courses that match the keywords
        if matching_keywords:
            courses = Course.objects.filter(
                status='published',
                difficulty=difficulty_level
            ).filter(
                Q(title__icontains=matching_keywords[0]) |
                Q(description__icontains=matching_keywords[0]) |
                Q(ai_skill_tags__overlap=matching_keywords)
            )[:5]  # Limit to 5 courses
        else:
            # Fallback: popular courses in the difficulty level
            courses = Course.objects.filter(
                status='published',
                difficulty=difficulty_level
            ).order_by('-enrollment_count', '-average_rating')[:5]
        
        # Create learning path
        learning_path = LearningPath.objects.create(
            title=f"AI Generated: {prompt[:50]}",
            slug=f"ai-path-{user.id}-{timezone.now().timestamp()}",
            description=f"Customized learning path based on: {prompt}",
            difficulty=difficulty_level,
            ai_generated=True,
            ai_generation_prompt=prompt,
            target_skills=target_skills,
            created_by=user,
            estimated_duration=timedelta(hours=sum([course.estimated_effort_hours for course in courses])),
            is_public=False  # Private by default
        )
        
        # Add courses to learning path
        for order, course in enumerate(courses):
            LearningPathCourse.objects.create(
                learning_path=learning_path,
                course=course,
                order=order + 1,
                is_required=True
            )
        
        # Send notification email
        subject = 'Your AI Learning Path is Ready!'
        message = f"""
        Hi {user.first_name},
        
        Your personalized AI learning path "{learning_path.title}" has been generated and is ready for you!
        
        Path Details:
        - {len(courses)} courses selected
        - Estimated duration: {learning_path.estimated_duration}
        - Difficulty level: {difficulty_level.title()}
        - Target skills: {', '.join(target_skills)}
        
        Courses in your path:
        {chr(10).join([f"• {course.title}" for course in courses])}
        
        Start your learning journey today!
        
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
        
        logger.info(f"AI learning path generated: {learning_path.title} for user {user.email}")
        return f"Learning path '{learning_path.title}' created for {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User not found"
    except Exception as e:
        logger.error(f"Failed to generate AI learning path: {str(e)}")
        return f"Failed to generate learning path: {str(e)}"


@shared_task
def send_course_reminder_notifications():
    """Send reminders to users who haven't accessed their courses recently"""
    try:
        # Find active enrollments with no recent activity
        cutoff_date = timezone.now() - timedelta(days=7)
        
        inactive_enrollments = CourseEnrollment.objects.filter(
            status='active',
            last_accessed__lt=cutoff_date,
            user__email_notifications=True
        ).select_related('user', 'course')
        
        sent_count = 0
        
        for enrollment in inactive_enrollments:
            user = enrollment.user
            course = enrollment.course
            
            subject = f"Continue your learning in {course.title}"
            message = f"""
            Hi {user.first_name},
            
            We noticed you haven't accessed "{course.title}" in a while. 
            Don't let your learning momentum slip away!
            
            Your Progress:
            - Current progress: {enrollment.progress_percentage}%
            - Time spent: {enrollment.total_time_spent}
            - Last lesson: {enrollment.current_lesson.title if enrollment.current_lesson else 'Not started'}
            
            Continue where you left off and keep building your skills!
            
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
        
        logger.info(f"Course reminders sent to {sent_count} users")
        return f"Reminders sent to {sent_count} users"
        
    except Exception as e:
        logger.error(f"Failed to send course reminders: {str(e)}")
        return f"Failed to send reminders: {str(e)}"


@shared_task
def update_trending_courses():
    """Update trending courses based on recent activity"""
    try:
        # Calculate trending based on recent enrollments, views, and completions
        one_week_ago = timezone.now() - timedelta(days=7)
        
        courses = Course.objects.filter(status='published').annotate(
            recent_enrollments=Count(
                'enrollments',
                filter=Q(enrollments__enrolled_at__gte=one_week_ago)
            ),
            recent_completions=Count(
                'enrollments',
                filter=Q(
                    enrollments__completed_at__gte=one_week_ago,
                    enrollments__status='completed'
                )
            )
        )
        
        # Reset trending status
        Course.objects.update(is_trending=False)
        
        # Mark top courses as trending
        trending_courses = courses.order_by(
            '-recent_enrollments', 
            '-recent_completions', 
            '-view_count'
        )[:20]
        
        trending_ids = [course.id for course in trending_courses]
        Course.objects.filter(id__in=trending_ids).update(is_trending=True)
        
        logger.info(f"Updated {len(trending_ids)} trending courses")
        return f"Updated {len(trending_ids)} trending courses"
        
    except Exception as e:
        logger.error(f"Failed to update trending courses: {str(e)}")
        return f"Failed to update trending courses: {str(e)}"


@shared_task
def generate_course_recommendations(user_id):
    """Generate personalized course recommendations for a user"""
    try:
        user = User.objects.get(id=user_id)
        
        # Get user's learning history
        completed_courses = CourseEnrollment.objects.filter(
            user=user,
            status='completed'
        ).values_list('course', flat=True)
        
        enrolled_courses = CourseEnrollment.objects.filter(
            user=user
        ).values_list('course', flat=True)
        
        user_skills = list(user.skills.values_list('skill_name', flat=True))
        
        # Find similar courses based on various factors
        recommendations = []
        
        # 1. Courses in same categories as completed courses
        if completed_courses:
            completed_course_categories = Course.objects.filter(
                id__in=completed_courses
            ).values_list('category', flat=True)
            
            category_recommendations = Course.objects.filter(
                category__in=completed_course_categories,
                status='published'
            ).exclude(
                id__in=enrolled_courses
            ).order_by('-average_rating')[:10]
            
            recommendations.extend(category_recommendations)
        
        # 2. Courses matching user's skills
        if user_skills:
            skill_recommendations = Course.objects.filter(
                ai_skill_tags__overlap=user_skills,
                status='published'
            ).exclude(
                id__in=enrolled_courses
            ).order_by('-average_rating')[:10]
            
            recommendations.extend(skill_recommendations)
        
        # 3. Popular courses at user's skill level
        level_recommendations = Course.objects.filter(
            difficulty=user.current_skill_level,
            status='published'
        ).exclude(
            id__in=enrolled_courses
        ).order_by('-enrollment_count')[:10]
        
        recommendations.extend(level_recommendations)
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))[:15]
        
        # Cache recommendations
        from django.core.cache import cache
        cache.set(f'recommendations_{user_id}', unique_recommendations, 3600)  # 1 hour
        
        logger.info(f"Generated {len(unique_recommendations)} recommendations for user {user.email}")
        return f"Generated {len(unique_recommendations)} recommendations for {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User not found"
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {str(e)}")
        return f"Failed to generate recommendations: {str(e)}"


@shared_task
def cleanup_incomplete_enrollments():
    """Clean up old incomplete enrollments"""
    try:
        # Find enrollments that are active but haven't been accessed in 6 months
        cutoff_date = timezone.now() - timedelta(days=180)
        
        old_enrollments = CourseEnrollment.objects.filter(
            status='active',
            progress_percentage__lt=10,  # Less than 10% progress
            last_accessed__lt=cutoff_date
        )
        
        # Mark as dropped instead of deleting
        updated_count = old_enrollments.update(status='dropped')
        
        logger.info(f"Marked {updated_count} old enrollments as dropped")
        return f"Cleaned up {updated_count} old enrollments"
        
    except Exception as e:
        logger.error(f"Failed to cleanup enrollments: {str(e)}")
        return f"Failed to cleanup: {str(e)}"


@shared_task
def send_course_launch_notifications(course_id):
    """Send notifications when a new course is launched"""
    try:
        course = Course.objects.get(id=course_id)
        
        # Find users who might be interested based on their skills and wishlist
        interested_users = []
        
        # Users with relevant skills
        if course.ai_skill_tags:
            skill_users = User.objects.filter(
                skills__skill_name__in=course.ai_skill_tags,
                email_notifications=True
            ).distinct()
            interested_users.extend(skill_users)
        
        # Users in the same category preferences
        category_users = User.objects.filter(
            enrollments__course__category=course.category,
            email_notifications=True
        ).distinct()
        interested_users.extend(category_users)
        
        # Remove duplicates
        unique_users = list(set(interested_users))[:100]  # Limit to 100 users
        
        sent_count = 0
        for user in unique_users:
            subject = f'New Course Alert: {course.title}'
            message = f"""
            Hi {user.first_name},
            
            Exciting news! A new course that matches your interests has just been launched.
            
            "{course.title}"
            
            Course Details:
            - Instructor: {course.instructor.get_full_name()}
            - Difficulty: {course.get_difficulty_display()}
            - Duration: {course.estimated_duration}
            - Category: {course.category.name if course.category else 'General'}
            
            {course.short_description}
            
            Enroll now to start your learning journey!
            
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
        
        logger.info(f"Course launch notifications sent to {sent_count} users for {course.title}")
        return f"Launch notifications sent to {sent_count} users"
        
    except Course.DoesNotExist:
        logger.error(f"Course with id {course_id} not found")
        return f"Course not found"
    except Exception as e:
        logger.error(f"Failed to send launch notifications: {str(e)}")
        return f"Failed to send notifications: {str(e)}"


@shared_task
def generate_instructor_analytics_report(instructor_id):
    """Generate analytics report for instructor"""
    try:
        instructor = User.objects.get(id=instructor_id, role='instructor')
        
        # Get instructor's courses
        courses = Course.objects.filter(instructor=instructor)
        
        # Calculate analytics
        total_enrollments = CourseEnrollment.objects.filter(course__in=courses).count()
        total_completions = CourseEnrollment.objects.filter(
            course__in=courses,
            status='completed'
        ).count()
        
        total_revenue = CourseEnrollment.objects.filter(
            course__in=courses
        ).aggregate(
            revenue=Sum('course__price')
        )['revenue'] or 0
        
        avg_rating = CourseReview.objects.filter(
            course__in=courses
        ).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
        
        # Generate report
        report_data = {
            'instructor_name': instructor.get_full_name(),
            'total_courses': courses.count(),
            'total_enrollments': total_enrollments,
            'total_completions': total_completions,
            'completion_rate': (total_completions / total_enrollments * 100) if total_enrollments > 0 else 0,
            'total_revenue': total_revenue,
            'average_rating': round(avg_rating, 2),
            'generated_at': timezone.now()
        }
        
        # Send report email
        subject = 'Your Monthly Teaching Analytics Report'
        message = f"""
        Hi {instructor.first_name},
        
        Here's your monthly teaching analytics report:
        
        📊 Course Performance:
        - Total courses: {report_data['total_courses']}
        - Total enrollments: {report_data['total_enrollments']}
        - Total completions: {report_data['total_completions']}
        - Completion rate: {report_data['completion_rate']:.1f}%
        
        ⭐ Quality Metrics:
        - Average rating: {report_data['average_rating']}/5.0
        
        💰 Revenue:
        - Total revenue: ${report_data['total_revenue']}
        
        Keep up the excellent work in educating and inspiring learners!
        
        Best regards,
        The Wokkah Team
        """
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instructor.email],
            fail_silently=False,
        )
        
        logger.info(f"Analytics report generated for instructor {instructor.email}")
        return f"Report generated for {instructor.email}"
        
    except User.DoesNotExist:
        logger.error(f"Instructor with id {instructor_id} not found")
        return f"Instructor not found"
    except Exception as e:
        logger.error(f"Failed to generate instructor report: {str(e)}")
        return f"Failed to generate report: {str(e)}"


# Periodic tasks configuration
@shared_task
def daily_course_tasks():
    """Daily tasks for course management"""
    send_course_reminder_notifications.delay()
    update_trending_courses.delay()
    return "Daily course tasks initiated"


@shared_task
def weekly_course_tasks():
    """Weekly tasks for course management"""
    cleanup_incomplete_enrollments.delay()
    return "Weekly course tasks initiated"


@shared_task
def monthly_instructor_reports():
    """Generate monthly reports for all instructors"""
    instructors = User.objects.filter(role='instructor', is_active=True)
    
    for instructor in instructors:
        generate_instructor_analytics_report.delay(instructor.id)
    
    return f"Monthly reports scheduled for {instructors.count()} instructors"