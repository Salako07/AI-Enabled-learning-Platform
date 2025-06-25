from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import UserSubscription, PaymentAttempt
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_subscription_renewals():
    """Process subscription renewals and failed payments"""
    try:
        # Find subscriptions that need renewal
        today = timezone.now().date()
        expiring_subscriptions = UserSubscription.objects.filter(
            end_date__lte=today,
            status='active'
        )
        
        for subscription in expiring_subscriptions:
            try:
                # Attempt to renew subscription
                renewal_success = attempt_subscription_renewal(subscription)
                
                if renewal_success:
                    logger.info(f"Successfully renewed subscription {subscription.id}")
                else:
                    # Mark as past due and schedule retry
                    subscription.status = 'past_due'
                    subscription.save()
                    
                    # Schedule retry in 3 days
                    retry_date = timezone.now() + timedelta(days=3)
                    PaymentAttempt.objects.create(
                        subscription=subscription,
                        attempt_type='automatic',
                        amount=subscription.plan.price,
                        retry_number=1,
                        next_retry_date=retry_date
                    )
                    
            except Exception as e:
                logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
                continue
        
        logger.info(f"Processed {len(expiring_subscriptions)} subscription renewals")
        
    except Exception as e:
        logger.error(f"Error in process_subscription_renewals: {str(e)}")
        raise

def attempt_subscription_renewal(subscription):
    """Attempt to renew a subscription"""
    try:
        # This would integrate with Stripe or other payment processor
        # For now, return success for demo
        
        # Extend subscription period
        if subscription.plan.billing_interval == 'monthly':
            subscription.end_date = subscription.end_date + timedelta(days=30)
        elif subscription.plan.billing_interval == 'yearly':
            subscription.end_date = subscription.end_date + timedelta(days=365)
        
        subscription.current_period_start = timezone.now()
        subscription.current_period_end = subscription.end_date
        subscription.save()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to renew subscription {subscription.id}: {str(e)}")
        return False

@shared_task
def send_payment_reminder(subscription_id):
    """Send payment reminder for failed payment"""
    try:
        subscription = UserSubscription.objects.get(id=subscription_id)
        
        from notifications.tasks import send_notification
        send_notification.delay(
            user_id=str(subscription.user.id),
            template_type='payment_failed',
            context={
                'user_name': subscription.user.get_full_name(),
                'plan_name': subscription.plan.name,
                'amount': str(subscription.plan.price),
            }
        )
        
        logger.info(f"Sent payment reminder for subscription {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error sending payment reminder: {str(e)}")
        raise