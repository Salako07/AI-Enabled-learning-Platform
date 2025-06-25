from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)
router.register(r'preferences', views.NotificationPreferenceViewSet)
router.register(r'templates', views.NotificationTemplateViewSet)

urlpatterns = [
    # Notification Management
    path('mark-read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    path('mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    path('unread-count/', views.UnreadNotificationCountView.as_view(), name='unread_notification_count'),
    
    # Preferences
    path('preferences/update/', views.UpdateNotificationPreferencesView.as_view(), name='update_notification_preferences'),
    path('unsubscribe/<uuid:token>/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    
    # Push Notifications
    path('push/register/', views.RegisterPushDeviceView.as_view(), name='register_push_device'),
    path('push/unregister/', views.UnregisterPushDeviceView.as_view(), name='unregister_push_device'),
    
    # Announcements
    path('announcements/', views.AnnouncementBannerView.as_view(), name='announcements'),
    path('announcements/<uuid:banner_id>/interact/', views.BannerInteractionView.as_view(), name='banner_interaction'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)
router.register(r'preferences', views.NotificationPreferenceViewSet)
router.register(r'templates', views.NotificationTemplateViewSet)

urlpatterns = [
    # Notification Management
    path('mark-read/', views.MarkNotificationsReadView.as_view(), name='mark_notifications_read'),
    path('mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),
    path('unread-count/', views.UnreadNotificationCountView.as_view(), name='unread_notification_count'),
    
    # Preferences
    path('preferences/update/', views.UpdateNotificationPreferencesView.as_view(), name='update_notification_preferences'),
    path('unsubscribe/<uuid:token>/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    
    # Push Notifications
    path('push/register/', views.RegisterPushDeviceView.as_view(), name='register_push_device'),
    path('push/unregister/', views.UnregisterPushDeviceView.as_view(), name='unregister_push_device'),
    
    # Announcements
    path('announcements/', views.AnnouncementBannerView.as_view(), name='announcements'),
    path('announcements/<uuid:banner_id>/interact/', views.BannerInteractionView.as_view(), name='banner_interaction'),
    
    # ViewSet URLs
    path('', include(router.urls)),
]

