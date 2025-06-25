from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserSkill, UserLearningPath, UserPreferences

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 
            'password', 'password_confirm', 'learning_style', 
            'current_skill_level', 'learning_goals'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    progress_data = serializers.ReadOnlyField(source='get_progress_data')
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'bio', 'avatar', 'github_username', 'linkedin_url', 'website_url',
            'learning_style', 'current_skill_level', 'learning_goals',
            'subscription_tier', 'subscription_active', 'current_streak',
            'longest_streak', 'courses_completed', 'total_learning_time',
            'public_profile', 'progress_data', 'created_at'
        ]
        read_only_fields = [
            'id', 'subscription_tier', 'subscription_active', 'current_streak',
            'longest_streak', 'courses_completed', 'total_learning_time', 'created_at'
        ]

class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill_name', 'proficiency_level', 'verified',
            'ai_confidence_score', 'last_assessed', 'created_at'
        ]
        read_only_fields = ['id', 'verified', 'ai_confidence_score', 'last_assessed', 'created_at']

class UserLearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLearningPath
        fields = [
            'id', 'name', 'description', 'status', 'progress_percentage',
            'estimated_duration', 'difficulty_level', 'target_skills',
            'is_ai_generated', 'created_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'is_ai_generated', 'created_at']

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = [
            'theme', 'language', 'timezone', 'difficulty_preference',
            'preferred_session_length', 'break_reminders', 'ai_assistance_level',
            'ai_feedback_frequency', 'allow_peer_collaboration', 'allow_mentorship',
            'public_progress', 'email_frequency'
        ]