from rest_framework import serializers
from .models import (
    Assessment, Question, QuestionOption, UserAssessmentAttempt,
    UserQuestionResponse, CodingAssessment, CodingSubmission
)

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'option_text', 'explanation', 'image_url', 'order']
        # Don't expose is_correct to prevent cheating

class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)
    accuracy_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'explanation', 'hint',
            'image_url', 'video_url', 'code_snippet', 'points', 'order',
            'options', 'accuracy_rate'
        ]

class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'description', 'assessment_type', 'difficulty_level',
            'time_limit', 'max_attempts', 'passing_score', 'total_points',
            'randomize_questions', 'show_correct_answers', 'allow_review',
            'immediate_feedback', 'ai_proctoring_enabled', 'questions',
            'question_count', 'total_attempts', 'average_score', 'pass_rate'
        ]
    
    def get_question_count(self, obj):
        return obj.questions.count()

class UserAssessmentAttemptSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserAssessmentAttempt
        fields = [
            'id', 'assessment', 'assessment_title', 'user_name', 'attempt_number',
            'status', 'total_score', 'percentage_score', 'passed',
            'started_at', 'submitted_at', 'time_spent', 'instructor_feedback'
        ]
        read_only_fields = [
            'id', 'total_score', 'percentage_score', 'passed',
            'started_at', 'submitted_at', 'time_spent'
        ]

class UserQuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuestionResponse
        fields = [
            'id', 'question', 'response_type', 'selected_options',
            'text_response', 'code_submission', 'points_earned',
            'is_correct', 'ai_feedback', 'manual_feedback', 'time_spent'
        ]

class CodingAssessmentSerializer(serializers.ModelSerializer):
    assessment = AssessmentSerializer(read_only=True)
    
    class Meta:
        model = CodingAssessment
        fields = [
            'id', 'assessment', 'problem_statement', 'input_description',
            'output_description', 'constraints', 'allowed_languages',
            'default_language', 'starter_code', 'public_test_cases',
            'time_limit_seconds', 'memory_limit_mb', 'partial_credit_enabled'
        ]

class CodingSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingSubmission
        fields = [
            'id', 'language', 'status', 'verdict', 'passed_test_cases',
            'total_test_cases', 'execution_time', 'memory_used',
            'score', 'max_score', 'ai_code_quality_score', 'ai_feedback',
            'submitted_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'verdict', 'passed_test_cases', 'total_test_cases',
            'execution_time', 'memory_used', 'score', 'ai_code_quality_score',
            'ai_feedback', 'submitted_at', 'completed_at'
        ]