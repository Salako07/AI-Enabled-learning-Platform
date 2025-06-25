# collaboration/models.py

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class CollaborationRoom(models.Model):
    """Real-time collaboration rooms for coding and learning"""
    
    ROOM_TYPES = [
        ('pair_programming', 'Pair Programming'),
        ('study_group', 'Study Group'),
        ('live_session', 'Live Session'),
        ('office_hours', 'Office Hours'),
        ('project_collaboration', 'Project Collaboration'),
        ('code_review', 'Code Review Session'),
        ('whiteboard', 'Whiteboard Session'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('invite_only', 'Invite Only'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_type = models.CharField(max_length=30, choices=ROOM_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    
    # Ownership and Moderation
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    moderators = models.ManyToManyField(User, blank=True, related_name='moderated_rooms')
    
    # Participants
    participants = models.ManyToManyField(User, through='RoomParticipant', related_name='collaboration_rooms')
    max_participants = models.IntegerField(default=10)
    
    # Session Information
    course_id = models.UUIDField(null=True, blank=True)
    lesson_id = models.UUIDField(null=True, blank=True)
    programming_language = models.CharField(max_length=50, blank=True)
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Features and Settings
    enable_video = models.BooleanField(default=True)
    enable_audio = models.BooleanField(default=True)
    enable_screen_share = models.BooleanField(default=True)
    enable_code_editor = models.BooleanField(default=True)
    enable_whiteboard = models.BooleanField(default=False)
    enable_file_sharing = models.BooleanField(default=True)
    enable_recording = models.BooleanField(default=False)
    
    # Session Data
    session_recording_url = models.URLField(blank=True)
    shared_code = models.TextField(blank=True)
    whiteboard_data = models.JSONField(default=dict, blank=True)
    chat_history = models.JSONField(default=list, blank=True)
    
    # Analytics
    total_participants = models.IntegerField(default=0)
    average_session_rating = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collaboration_rooms'
        verbose_name = 'Collaboration Room'
        verbose_name_plural = 'Collaboration Rooms'
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def add_participant(self, user, role='participant'):
        """Add a participant to the room"""
        participant, created = RoomParticipant.objects.get_or_create(
            room=self,
            user=user,
            defaults={'role': role}
        )
        return participant


class RoomParticipant(models.Model):
    """Participants in collaboration rooms"""
    
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('moderator', 'Moderator'),
        ('participant', 'Participant'),
        ('observer', 'Observer'),
    ]
    
    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('joined', 'Joined'),
        ('left', 'Left'),
        ('removed', 'Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='room_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='invited')
    
    # Permissions
    can_edit_code = models.BooleanField(default=True)
    can_share_screen = models.BooleanField(default=True)
    can_use_microphone = models.BooleanField(default=True)
    can_use_camera = models.BooleanField(default=True)
    
    # Activity Tracking
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    total_time_spent = models.DurationField(default='00:00:00')
    
    # Feedback
    session_rating = models.IntegerField(null=True, blank=True)  # 1-5
    feedback = models.TextField(blank=True)
    
    invited_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'room_participants'
        verbose_name = 'Room Participant'
        verbose_name_plural = 'Room Participants'
        unique_together = ['room', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} in {self.room.name} ({self.role})"


class StudyGroup(models.Model):
    """Persistent study groups for ongoing collaboration"""
    
    GROUP_TYPES = [
        ('course_based', 'Course-Based'),
        ('skill_based', 'Skill-Based'),
        ('project_based', 'Project-Based'),
        ('interview_prep', 'Interview Preparation'),
        ('general', 'General Learning'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Organization
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_study_groups')
    members = models.ManyToManyField(User, through='StudyGroupMember', related_name='study_groups')
    max_members = models.IntegerField(default=20)
    
    # Focus Areas
    course_id = models.UUIDField(null=True, blank=True)
    target_skills = models.JSONField(default=list, blank=True)
    programming_languages = models.JSONField(default=list, blank=True)
    
    # Settings
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Schedule
    meeting_schedule = models.JSONField(default=dict, blank=True)  # Recurring meeting schedule
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Activity
    last_activity = models.DateTimeField(auto_now=True)
    total_sessions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_groups'
        verbose_name = 'Study Group'
        verbose_name_plural = 'Study Groups'
        ordering = ['-last_activity']
    
    def __str__(self):
        return self.name


class StudyGroupMember(models.Model):
    """Members of study groups"""
    
    ROLE_CHOICES = [
        ('creator', 'Creator'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('removed', 'Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='group_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Activity
    sessions_attended = models.IntegerField(default=0)
    contribution_score = models.FloatField(default=0.0)
    last_active = models.DateTimeField(auto_now=True)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'study_group_members'
        verbose_name = 'Study Group Member'
        verbose_name_plural = 'Study Group Members'
        unique_together = ['study_group', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} in {self.study_group.name}"


class PeerProgrammingSession(models.Model):
    """Dedicated peer programming sessions"""
    
    SESSION_TYPES = [
        ('practice', 'Practice Session'),
        ('interview_prep', 'Interview Preparation'),
        ('project_work', 'Project Work'),
        ('debugging', 'Debugging Session'),
        ('learning', 'Learning Session'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Participants
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='driver_sessions')
    navigator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='navigator_sessions')
    
    # Session Configuration
    programming_language = models.CharField(max_length=50)
    problem_description = models.TextField()
    difficulty_level = models.CharField(max_length=20, default='medium')
    
    # Code and Progress
    initial_code = models.TextField(blank=True)
    final_code = models.TextField(blank=True)
    code_history = models.JSONField(default=list, blank=True)  # Save code snapshots
    
    # Scheduling
    scheduled_start = models.DateTimeField()
    scheduled_duration = models.DurationField(default='01:00:00')
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Feedback and Evaluation
    driver_feedback = models.TextField(blank=True)
    navigator_feedback = models.TextField(blank=True)
    mutual_rating = models.IntegerField(null=True, blank=True)  # 1-5
    
    # Learning Outcomes
    concepts_learned = models.JSONField(default=list, blank=True)
    challenges_faced = models.JSONField(default=list, blank=True)
    solutions_found = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'peer_programming_sessions'
        verbose_name = 'Peer Programming Session'
        verbose_name_plural = 'Peer Programming Sessions'
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"Peer Programming: {self.driver.full_name} & {self.navigator.full_name}"


class MentorshipRelationship(models.Model):
    """Mentorship connections between users"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    RELATIONSHIP_TYPES = [
        ('career', 'Career Mentorship'),
        ('technical', 'Technical Mentorship'),
        ('interview_prep', 'Interview Preparation'),
        ('project_guidance', 'Project Guidance'),
        ('general', 'General Mentorship'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentoring_relationships')
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_relationships')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    
    # Goals and Expectations
    goals = models.TextField()
    expected_duration = models.DurationField(default='90 days')  # 3 months default
    meeting_frequency = models.CharField(max_length=50, default='weekly')
    
    # Progress Tracking
    total_sessions = models.IntegerField(default=0)
    next_session_date = models.DateTimeField(null=True, blank=True)
    progress_notes = models.TextField(blank=True)
    
    # Evaluation
    mentor_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5
    mentee_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5
    goals_achieved = models.JSONField(default=list, blank=True)
    
    # Matching Information
    matched_by_ai = models.BooleanField(default=False)
    matching_score = models.FloatField(null=True, blank=True)  # AI matching confidence
    
    established_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentorship_relationships'
        verbose_name = 'Mentorship Relationship'
        verbose_name_plural = 'Mentorship Relationships'
        unique_together = ['mentor', 'mentee']
    
    def __str__(self):
        return f"{self.mentor.full_name} mentoring {self.mentee.full_name}"


class CollaborationInvitation(models.Model):
    """Invitations to collaboration sessions"""
    
    INVITATION_TYPES = [
        ('room', 'Room Invitation'),
        ('study_group', 'Study Group Invitation'),
        ('peer_programming', 'Peer Programming Invitation'),
        ('mentorship', 'Mentorship Invitation'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invitation_type = models.CharField(max_length=20, choices=INVITATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Participants
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    
    # Invitation Details
    subject = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    
    # Related Objects
    room_id = models.UUIDField(null=True, blank=True)
    study_group_id = models.UUIDField(null=True, blank=True)
    peer_session_id = models.UUIDField(null=True, blank=True)
    
    # Response
    response_message = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'collaboration_invitations'
        verbose_name = 'Collaboration Invitation'
        verbose_name_plural = 'Collaboration Invitations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation from {self.sender.full_name} to {self.recipient.full_name}"


class CodeCollaboration(models.Model):
    """Real-time code collaboration sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(CollaborationRoom, on_delete=models.CASCADE, related_name='code_sessions')
    
    # Code Information
    filename = models.CharField(max_length=200, default='main.py')
    programming_language = models.CharField(max_length=50)
    initial_code = models.TextField(blank=True)
    current_code = models.TextField(blank=True)
    
    # Collaboration Data
    edit_history = models.JSONField(default=list, blank=True)  # Operational transforms
    cursor_positions = models.JSONField(default=dict, blank=True)  # User cursor positions
    selections = models.JSONField(default=dict, blank=True)  # User text selections
    
    # Execution and Testing
    last_execution_output = models.TextField(blank=True)
    last_execution_error = models.TextField(blank=True)
    test_results = models.JSONField(default=dict, blank=True)
    
    # Version Control
    version = models.IntegerField(default=1)
    saved_versions = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_collaborations'
        verbose_name = 'Code Collaboration'
        verbose_name_plural = 'Code Collaborations'
    
    def __str__(self):
        return f"Code Session in {self.room.name} - {self.filename}"