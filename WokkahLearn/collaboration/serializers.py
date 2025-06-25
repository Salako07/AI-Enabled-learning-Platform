from rest_framework import serializers
from .models import (
    CollaborationRoom, RoomParticipant, StudyGroup,
    PeerProgrammingSession, MentorshipRelationship
)

class RoomParticipantSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar.url', read_only=True)
    
    class Meta:
        model = RoomParticipant
        fields = [
            'id', 'user', 'user_name', 'user_avatar', 'role', 'status',
            'can_edit_code', 'can_share_screen', 'joined_at', 'total_time_spent'
        ]

class CollaborationRoomSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)
    participants = RoomParticipantSerializer(source='room_participants', many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborationRoom
        fields = [
            'id', 'name', 'description', 'room_type', 'status', 'privacy',
            'host', 'host_name', 'max_participants', 'participant_count',
            'programming_language', 'scheduled_start', 'scheduled_end',
            'enable_video', 'enable_audio', 'enable_screen_share',
            'enable_code_editor', 'enable_whiteboard', 'participants'
        ]
    
    def get_participant_count(self, obj):
        return obj.participants.count()

class StudyGroupSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'description', 'group_type', 'status', 'creator_name',
            'max_members', 'member_count', 'target_skills', 'programming_languages',
            'is_public', 'requires_approval', 'meeting_schedule', 'created_at'
        ]
    
    def get_member_count(self, obj):
        return obj.members.count()

class PeerProgrammingSessionSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    navigator_name = serializers.CharField(source='navigator.get_full_name', read_only=True)
    
    class Meta:
        model = PeerProgrammingSession
        fields = [
            'id', 'session_type', 'status', 'driver', 'driver_name',
            'navigator', 'navigator_name', 'programming_language',
            'problem_description', 'difficulty_level', 'scheduled_start',
            'scheduled_duration', 'mutual_rating', 'concepts_learned'
        ]

class MentorshipRelationshipSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.get_full_name', read_only=True)
    mentee_name = serializers.CharField(source='mentee.get_full_name', read_only=True)
    
    class Meta:
        model = MentorshipRelationship
        fields = [
            'id', 'mentor', 'mentor_name', 'mentee', 'mentee_name',
            'status', 'relationship_type', 'goals', 'expected_duration',
            'meeting_frequency', 'total_sessions', 'next_session_date',
            'mentor_satisfaction', 'mentee_satisfaction', 'established_at'
        ]