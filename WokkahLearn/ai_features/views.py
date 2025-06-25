from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AITutorSession, AIMockInterview, AICodeReview
from .serializers import (
    AITutorSessionSerializer, AIMockInterviewSerializer, 
    AICodeReviewSerializer
)
from .services import OpenAIService, AnthropicService

class AITutorChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Chat with AI tutor"""
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        context = request.data.get('context', {})
        
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create AI tutor session
        if session_id:
            try:
                session = AITutorSession.objects.get(
                    id=session_id, 
                    user=request.user
                )
            except AITutorSession.DoesNotExist:
                return Response({
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            session = AITutorSession.objects.create(
                user=request.user,
                session_type='coding_help',
                initial_prompt=message,
                course_id=context.get('course_id'),
                lesson_id=context.get('lesson_id'),
                programming_language=context.get('language', 'python')
            )
        
        # Get AI response
        ai_service = OpenAIService()
        try:
            response = ai_service.get_tutor_response(
                message=message,
                session_history=session.conversation_history,
                context=context
            )
            
            # Save conversation
            session.add_message('user', message)
            session.add_message('assistant', response['message'])
            
            return Response({
                'session_id': str(session.id),
                'response': response['message'],
                'suggestions': response.get('suggestions', []),
                'code_examples': response.get('code_examples', []),
            })
            
        except Exception as e:
            return Response({
                'error': 'AI service unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class CodeAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Analyze code with AI"""
        code = request.data.get('code')
        language = request.data.get('language', 'python')
        analysis_type = request.data.get('type', 'general')
        
        if not code:
            return Response({
                'error': 'Code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check subscription limits
        if not self.check_ai_usage_limit(request.user):
            return Response({
                'error': 'AI usage limit exceeded'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Create code review record
        code_review = AICodeReview.objects.create(
            user=request.user,
            review_type=analysis_type,
            code_content=code,
            programming_language=language
        )
        
        try:
            # Get AI analysis
            ai_service = OpenAIService()
            analysis = ai_service.analyze_code(
                code=code,
                language=language,
                analysis_type=analysis_type
            )
            
            # Update code review with results
            code_review.status = 'completed'
            code_review.overall_score = analysis['overall_score']
            code_review.suggestions = analysis['suggestions']
            code_review.best_practices = analysis['best_practices']
            code_review.potential_bugs = analysis['potential_bugs']
            code_review.performance_issues = analysis['performance_issues']
            code_review.refactored_code = analysis.get('refactored_code', '')
            code_review.save()
            
            return Response({
                'review_id': str(code_review.id),
                'analysis': analysis,
            })
            
        except Exception as e:
            code_review.status = 'failed'
            code_review.save()
            return Response({
                'error': 'Analysis failed'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    def check_ai_usage_limit(self, user):
        """Check if user has exceeded AI usage limits"""
        # Implementation depends on subscription plan
        return True  # Simplified

class ScheduleMockInterviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Schedule an AI mock interview"""
        interview_type = request.data.get('type', 'coding')
        difficulty = request.data.get('difficulty', 'mid')
        scheduled_time = request.data.get('scheduled_time')
        target_company = request.data.get('company', '')
        target_role = request.data.get('role', '')
        
        # Check subscription access
        if not request.user.subscription_tier in ['premium', 'pro', 'enterprise']:
            return Response({
                'error': 'Premium subscription required for mock interviews'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create mock interview
        interview = AIMockInterview.objects.create(
            user=request.user,
            interview_type=interview_type,
            difficulty_level=difficulty,
            scheduled_at=scheduled_time,
            target_company=target_company,
            target_role=target_role
        )
        
        # Generate interview questions
        ai_service = OpenAIService()
        try:
            questions = ai_service.generate_interview_questions(
                interview_type=interview_type,
                difficulty=difficulty,
                company=target_company,
                role=target_role
            )
            
            interview.questions = questions
            interview.save()
            
            return Response({
                'interview': AIMockInterviewSerializer(interview).data,
                'message': 'Mock interview scheduled successfully'
            })
            
        except Exception as e:
            interview.delete()
            return Response({
                'error': 'Failed to generate interview questions'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
