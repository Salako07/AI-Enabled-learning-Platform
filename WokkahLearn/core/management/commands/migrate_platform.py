from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all migrations and setup for the platform'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Running platform migrations...'))
        
        # Run migrations
        call_command('migrate', verbosity=1)
        
        # Create cache table
        try:
            call_command('createcachetable')
        except:
            pass  # Table might already exist
        
        # Collect static files
        call_command('collectstatic', '--noinput', verbosity=1)
        
        self.stdout.write(self.style.SUCCESS('Platform migrations completed!'))

