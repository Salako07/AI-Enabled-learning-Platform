from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.CollaborationRoomViewSet)
router.register(r'study-groups', views.StudyGroupViewSet)
router.register(r'peer-sessions', views.PeerProgrammingSessionViewSet)
router.register(r'mentorships', views.MentorshipRelationshipViewSet)
router.register(r'invitations', views.CollaborationInvitationViewSet)

urlpatterns = [
    # Room Management
    path('rooms/create/', views.CreateRoomView.as_view(), name='create_room'),
    path('rooms/<uuid:room_id>/join/', views.JoinRoomView.as_view(), name='join_room'),
    path('rooms/<uuid:room_id>/leave/', views.LeaveRoomView.as_view(), name='leave_room'),
    path('rooms/<uuid:room_id>/invite/', views.InviteToRoomView.as_view(), name='invite_to_room'),
    
    # Study Groups
    path('study-groups/discover/', views.DiscoverStudyGroupsView.as_view(), name='discover_study_groups'),
    path('study-groups/<uuid:group_id>/join/', views.JoinStudyGroupView.as_view(), name='join_study_group'),
    path('study-groups/<uuid:group_id>/leave/', views.LeaveStudyGroupView.as_view(), name='leave_study_group'),
    
    # Peer Programming
    path('peer-programming/find-partner/', views.FindProgrammingPartnerView.as_view(), name='find_programming_partner'),
    path('peer-programming/schedule/', views.SchedulePeerSessionView.as_view(), name='schedule_peer_session'),
    
    # Mentorship
    path('mentorship/find-mentor/', views.FindMentorView.as_view(), name='find_mentor'),
    path('mentorship/become-mentor/', views.BecomeMentorView.as_view(), name='become_mentor'),
    path('mentorship/request/', views.RequestMentorshipView.as_view(), name='request_mentorship'),
    
    # Real-time Features
    path('rooms/<uuid:room_id>/webrtc-config/', views.WebRTCConfigView.as_view(), name='webrtc_config'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]