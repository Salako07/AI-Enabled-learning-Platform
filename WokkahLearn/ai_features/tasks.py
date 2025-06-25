from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AILearningRecommendation, AISkillAssessment
from .services import OpenAIService, RecommendationEngine
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_user_recommendations():
    """Generate AI-powered learning recommendations for active users"""
    try:
        from accounts.models import User
        
        # Get active users who haven't received recommendations recently
        cutoff_date = timezone.now() - timedelta(hours=24)
        users = User.objects.filter(
            is_active=True,
            subscription_active=True,
            last_active__gte=timezone.now() - timedelta(days=7)
        ).exclude(
            ai_recommendations__created_at__gte=cutoff_date
        )[:100]  # Process 100 users at a time
        
        recommendation_engine = RecommendationEngine()
        generated_count = 0
        
        for user in users:
            try:
                recommendations = recommendation_engine.generate_recommendations(user)
                
                for rec_data in recommendations:
                    AILearningRecommendation.objects.create(
                        user=user,
                        recommendation_type=rec_data['type'],
                        priority=rec_data['priority'],
                        title=rec_data['title'],
                        description=rec_data['description'],
                        reasoning=rec_data['reasoning'],
                        target_skill=rec_data.get('target_skill', ''),
                        ai_confidence_score=rec_data['confidence'],
                        course_id=rec_data.get('course_id'),
                        expires_at=timezone.now() + timedelta(days=7)
                    )
                
                generated_count += len(recommendations)
                logger.info(f"Generated {len(recommendations)} recommendations for user {user.email}")
                
            except Exception as e:
                logger.error(f"Error generating recommendations for user {user.id}: {str(e)}")
                continue
        
        logger.info(f"Generated {generated_count} total recommendations for {len(users)} users")
        return f"Generated {generated_count} recommendations"
        
    except Exception as e:
        logger.error(f"Error in generate_user_recommendations: {str(e)}")
        raise

@shared_task
def process_ai_code_review(review_id):
    """Process AI code review asynchronously"""
    try:
        from .models import AICodeReview
        
        review = AICodeReview.objects.get(id=review_id)
        review.status = 'in_progress'
        review.save()
        
        ai_service = OpenAIService()
        
        # Analyze code
        analysis_result = ai_service.analyze_code(
            code=review.code_content,
            language=review.programming_language,
            analysis_type=review.review_type
        )
        
        # Update review with results
        review.overall_score = analysis_result['overall_score']
        review.readability_score = analysis_result['readability_score']
        review.efficiency_score = analysis_result['efficiency_score']
        review.maintainability_score = analysis_result['maintainability_score']
        review.suggestions = analysis_result['suggestions']
        review.best_practices = analysis_result['best_practices']
        review.potential_bugs = analysis_result['potential_bugs']
        review.performance_issues = analysis_result['performance_issues']
        review.security_concerns = analysis_result['security_concerns']
        review.refactored_code = analysis_result.get('refactored_code', '')
        review.status = 'completed'
        review.completed_at = timezone.now()
        review.save()
        
        logger.info(f"Completed AI code review {review_id}")
        
        # Send notification to user
        from notifications.tasks import send_notification
        send_notification.delay(
            user_id=str(review.user.id),
            template_type='code_review_completed',
            context={
                'review_id': str(review.id),
                'score': review.overall_score,
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing AI code review {review_id}: {str(e)}")
        # Update review status to failed
        try:
            review = AICodeReview.objects.get(id=review_id)
            review.status = 'failed'
            review.save()
        except:
            pass
        raise

@shared_task
def process_skill_assessment(assessment_id):
    """Process AI skill assessment"""
    try:
        assessment = AISkillAssessment.objects.get(id=assessment_id)
        assessment.status = 'in_progress'
        assessment.save()
        
        ai_service = OpenAIService()
        
        # Process assessment responses
        assessment_result = ai_service.evaluate_skill_assessment(
            questions=assessment.questions,
            answers=assessment.user_answers,
            skill_areas=assessment.skill_areas
        )
        
        # Update assessment with results
        assessment.overall_score = assessment_result['overall_score']
        assessment.skill_scores = assessment_result['skill_scores']
        assessment.competency_level = assessment_result['competency_level']
        assessment.strengths = assessment_result['strengths']
        assessment.weaknesses = assessment_result['weaknesses']
        assessment.learning_recommendations = assessment_result['recommendations']
        assessment.ai_confidence_in_assessment = assessment_result['confidence']
        assessment.status = 'completed'
        assessment.completed_at = timezone.now()
        assessment.save()
        
        logger.info(f"Completed AI skill assessment {assessment_id}")
        
    except Exception as e:
        logger.error(f"Error processing skill assessment {assessment_id}: {str(e)}")
        try:
            assessment = AISkillAssessment.objects.get(id=assessment_id)
            assessment.status = 'failed'
            assessment.save()
        except:
            pass
        raise
