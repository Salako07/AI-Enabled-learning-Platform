import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'process-notifications': {
        'task': 'notifications.tasks.process_notification_queue',
        'schedule': 30.0,  # every 30 seconds
    },
    'update-analytics': {
        'task': 'analytics.tasks.update_daily_analytics',
        'schedule': 3600.0,  # every hour
    },
    'cleanup-expired-sessions': {
        'task': 'accounts.tasks.cleanup_expired_sessions',
        'schedule': 86400.0,  # daily
    },
    'generate-ai-recommendations': {
        'task': 'ai_features.tasks.generate_user_recommendations',
        'schedule': 43200.0,  # every 12 hours
    },
    'process-subscription-renewals': {
        'task': 'payments.tasks.process_subscription_renewals',
        'schedule': 3600.0,  # hourly
    },
    'cleanup-code-environments': {
        'task': 'content.tasks.cleanup_idle_environments',
        'schedule': 1800.0,  # every 30 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')