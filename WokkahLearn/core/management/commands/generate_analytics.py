from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from analytics.tasks import update_user_learning_analytics, update_platform_analytics

class Command(BaseCommand):
    help = 'Generate analytics data for specified date range'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to generate analytics for (default: 7)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of existing analytics',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        force = options['force']
        
        self.stdout.write(f'Generating analytics for the last {days} days...')
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Update user analytics
            update_user_learning_analytics.delay(date_str)
            
            # Update platform analytics
            update_platform_analytics.delay(date_str)
            
            self.stdout.write(f'Queued analytics generation for {date_str}')
            
            current_date += timedelta(days=1)
        
        self.stdout.write(self.style.SUCCESS('Analytics generation queued successfully!'))

