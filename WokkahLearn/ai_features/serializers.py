from rest_framework import serializers
from .models import (
    AITutorSession, AIMockInterview, AICodeReview,
    AILearningRecommendation, AISkillAssessment
)

class AITutorSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITutorSession
        fields = [
            'id', 'session_type', 'status', 'topic', 'programming_language',
            'total_messages', 'user_satisfaction', 'started_at', 'ended_at'
        ]
        read_only_fields = ['id', 'total_messages', 'started_at', 'ended_at']

class AIMockInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMockInterview
        fields = [
            'id', 'interview_type', 'difficulty_level', 'status', 'target_company',
            'target_role', 'duration_minutes', 'overall_score', 'technical_score',
            'communication_score', 'strengths', 'weaknesses', 'recommendations',
            'scheduled_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'overall_score', 'technical_score', 'communication_score',
            'strengths', 'weaknesses', 'recommendations', 'completed_at'
        ]

class AICodeReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AICodeReview
        fields = [
            'id', 'review_type', 'programming_language', 'file_name',
            'overall_score', 'readability_score', 'efficiency_score',
            'suggestions', 'best_practices', 'potential_bugs',
            'refactored_code', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'overall_score', 'readability_score', 'efficiency_score',
            'suggestions', 'best_practices', 'potential_bugs', 'refactored_code',
            'created_at', 'completed_at'
        ]

class AILearningRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AILearningRecommendation
        fields = [
            'id', 'recommendation_type', 'priority', 'title', 'description',
            'reasoning', 'target_skill', 'ai_confidence_score', 'course_id',
            'lesson_id', 'external_url', 'viewed', 'clicked', 'dismissed',
            'expires_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'ai_confidence_score', 'viewed', 'clicked', 'dismissed', 'created_at'
        ]

class AISkillAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISkillAssessment
        fields = [
            'id', 'assessment_type', 'status', 'skill_areas', 'difficulty_level',
            'duration_minutes', 'overall_score', 'skill_scores', 'competency_level',
            'strengths', 'weaknesses', 'learning_recommendations',
            'started_at', 'completed_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'overall_score', 'skill_scores', 'competency_level',
            'strengths', 'weaknesses', 'learning_recommendations', 'started_at', 'completed_at'
        ]