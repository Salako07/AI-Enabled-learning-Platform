from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import NotificationQueue, Notification, NotificationTemplate
from .services import EmailService, PushNotificationService, SMSService
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_notification_queue():
    """Process queued notifications"""
    try:
        # Get pending notifications ready to be sent
        pending_notifications = NotificationQueue.objects.filter(
            status='queued',
            scheduled_for__lte=timezone.now()
        ).order_by('priority', 'scheduled_for')[:50]  # Process 50 at a time
        
        processed_count = 0
        
        for queue_item in pending_notifications:
            try:
                queue_item.status = 'processing'
                queue_item.started_at = timezone.now()
                queue_item.save()
                
                notification = queue_item.notification
                success = send_notification_by_channel(notification)
                
                if success:
                    queue_item.status = 'completed'
                    queue_item.completed_at = timezone.now()
                    notification.status = 'sent'
                    notification.sent_at = timezone.now()
                else:
                    queue_item.status = 'failed'
                    queue_item.attempts += 1
                    
                    # Schedule retry if under max attempts
                    if queue_item.attempts < queue_item.max_attempts:
                        queue_item.status = 'retrying'
                        queue_item.next_retry_at = timezone.now() + timedelta(
                            minutes=2 ** queue_item.attempts  # Exponential backoff
                        )
                
                queue_item.save()
                notification.save()
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing notification queue item {queue_item.id}: {str(e)}")
                queue_item.status = 'failed'
                queue_item.last_error = str(e)
                queue_item.save()
                continue
        
        logger.info(f"Processed {processed_count} notifications")
        return f"Processed {processed_count} notifications"
        
    except Exception as e:
        logger.error(f"Error in process_notification_queue: {str(e)}")
        raise

def send_notification_by_channel(notification):
    """Send notification via appropriate channel"""
    try:
        if notification.channel == 'email':
            email_service = EmailService()
            return email_service.send_email(
                to_email=notification.user.email,
                subject=notification.title,
                html_content=notification.html_content or notification.message,
                text_content=notification.message
            )
        
        elif notification.channel == 'push':
            push_service = PushNotificationService()
            return push_service.send_push_notification(
                user=notification.user,
                title=notification.title,
                message=notification.message,
                data=notification.metadata
            )
        
        elif notification.channel == 'sms':
            sms_service = SMSService()
            return sms_service.send_sms(
                phone_number=notification.user.phone_number,
                message=notification.message
            )
        
        elif notification.channel == 'in_app':
            # In-app notifications are handled via WebSocket
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_notifications_{notification.user.id}',
                {
                    'type': 'notification',
                    'notification': {
                        'id': str(notification.id),
                        'title': notification.title,
                        'message': notification.message,
                        'action_url': notification.action_url,
                        'created_at': notification.created_at.isoformat(),
                    }
                }
            )
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error sending notification {notification.id}: {str(e)}")
        return False

@shared_task
def send_notification(user_id, template_type, context=None, channel=None, scheduled_for=None):
    """Create and queue a notification"""
    try:
        from accounts.models import User
        
        user = User.objects.get(id=user_id)
        template = NotificationTemplate.objects.get(notification_type=template_type)
        
        if not template.is_active:
            logger.warning(f"Template {template_type} is not active")
            return
        
        # Check user preferences
        if not should_send_notification(user, template_type, channel):
            logger.info(f"Notification blocked by user preferences: {template_type}")
            return
        
        context = context or {}
        
        # Render template
        title = template.title_template.format(**context)
        message = template.message_template.format(**context)
        html_content = template.html_template.format(**context) if template.html_template else ""
        
        # Determine channel
        if not channel:
            channel = template.default_channel
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            template=template,
            title=title,
            message=message,
            html_content=html_content,
            channel=channel,
            context_data=context,
            scheduled_for=scheduled_for or timezone.now(),
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Queue notification
        NotificationQueue.objects.create(
            notification=notification,
            priority=template.priority,
            scheduled_for=scheduled_for or timezone.now()
        )
        
        logger.info(f"Queued notification {notification.id} for user {user.email}")
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise

def should_send_notification(user, template_type, channel):
    """Check if notification should be sent based on user preferences"""
    try:
        prefs = user.notification_preferences
        
        if not prefs.notifications_enabled:
            return False
        
        # Check channel preferences
        if channel == 'email' and not prefs.email_notifications:
            return False
        elif channel == 'push' and not prefs.push_notifications:
            return False
        elif channel == 'sms' and not prefs.sms_notifications:
            return False
        
        # Check type-specific preferences
        type_mapping = {
            'course_enrollment': prefs.course_notifications,
            'assessment_result': prefs.assessment_notifications,
            'collaboration_invite': prefs.collaboration_notifications,
            'ai_recommendation': prefs.ai_notifications,
            'payment_success': prefs.payment_notifications,
            'payment_failed': prefs.payment_notifications,
        }
        
        if template_type in type_mapping and not type_mapping[template_type]:
            return False
        
        # Check quiet hours
        if prefs.quiet_hours_enabled and channel in ['push', 'sms']:
            now = timezone.now().time()
            if prefs.quiet_hours_start <= now <= prefs.quiet_hours_end:
                return False
        
        return True
        
    except Exception:
        # If preferences not found, allow notification
        return True