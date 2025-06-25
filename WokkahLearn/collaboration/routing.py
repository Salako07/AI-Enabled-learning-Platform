from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/collaboration/room/<uuid:room_id>/', consumers.CollaborationRoomConsumer.as_asgi()),
    path('ws/collaboration/code/<uuid:room_id>/', consumers.CodeCollaboration.as_asgi()),
    path('ws/ai/tutor/<uuid:session_id>/', consumers.AITutorConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/learning-progress/', consumers.LearningProgress.as_asgi()),
]
