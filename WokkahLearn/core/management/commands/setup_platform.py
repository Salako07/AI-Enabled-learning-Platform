# core/management/commands/setup_platform.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import UserPreferences
from courses.models import Category
from payments.models import SubscriptionPlan
from notifications.models import NotificationTemplate
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up the learning platform with initial data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create a superuser admin account',
        )
        parser.add_argument(
            '--load-sample-data',
            action='store_true',
            help='Load sample data for development',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up CodeMaster Learning Platform...'))
        
        # Create categories
        self.create_categories()
        
        # Create subscription plans
        self.create_subscription_plans()
        
        # Create notification templates
        self.create_notification_templates()
        
        # Create admin user if requested
        if options['create_admin']:
            self.create_admin_user()
        
        # Load sample data if requested
        if options['load_sample_data']:
            self.load_sample_data()
        
        self.stdout.write(self.style.SUCCESS('Platform setup completed successfully!'))
    
    def create_categories(self):
        """Create course categories"""
        categories = [
            {
                'name': 'Programming Fundamentals',
                'slug': 'programming-fundamentals',
                'description': 'Core programming concepts and languages',
                'icon': 'code',
                'color': '#007bff',
                'display_order': 1,
                'is_featured': True,
            },
            {
                'name': 'Web Development',
                'slug': 'web-development',
                'description': 'Frontend and backend web development',
                'icon': 'globe',
                'color': '#28a745',
                'display_order': 2,
                'is_featured': True,
            },
            {
                'name': 'Data Science',
                'slug': 'data-science',
                'description': 'Data analysis, machine learning, and AI',
                'icon': 'chart-bar',
                'color': '#17a2b8',
                'display_order': 3,
                'is_featured': True,
            },
            {
                'name': 'Mobile Development',
                'slug': 'mobile-development',
                'description': 'iOS and Android app development',
                'icon': 'mobile',
                'color': '#ffc107',
                'display_order': 4,
            },
            {
                'name': 'DevOps & Cloud',
                'slug': 'devops-cloud',
                'description': 'DevOps practices and cloud platforms',
                'icon': 'cloud',
                'color': '#6c757d',
                'display_order': 5,
            },
            {
                'name': 'Cybersecurity',
                'slug': 'cybersecurity',
                'description': 'Information security and ethical hacking',
                'icon': 'shield',
                'color': '#dc3545',
                'display_order': 6,
            },
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
    
    def create_subscription_plans(self):
        """Create subscription plans"""
        plans = [
            {
                'name': 'Free',
                'plan_type': 'free',
                'price': 0.00,
                'billing_interval': 'monthly',
                'trial_period_days': 0,
                'description': 'Get started with basic courses and limited AI features',
                'features': {
                    'courses_access': 'limited',
                    'ai_interactions': 10,
                    'collaboration': False,
                    'certificates': False,
                    'priority_support': False,
                },
                'course_access_limit': 3,
                'ai_interactions_limit': 10,
                'ai_tutor_access': False,
                'ai_mock_interviews': False,
                'collaboration_rooms': False,
                'display_order': 1,
                'is_featured': False,
            },
            {
                'name': 'Starter',
                'plan_type': 'starter',
                'price': 19.99,
                'billing_interval': 'monthly',
                'trial_period_days': 7,
                'description': 'Perfect for individual learners starting their coding journey',
                'features': {
                    'courses_access': 'unlimited',
                    'ai_interactions': 100,
                    'collaboration': True,
                    'certificates': True,
                    'priority_support': False,
                },
                'ai_interactions_limit': 100,
                'ai_tutor_access': True,
                'ai_mock_interviews': False,
                'collaboration_rooms': True,
                'display_order': 2,
                'is_featured': False,
            },
            {
                'name': 'Premium',
                'plan_type': 'premium',
                'price': 39.99,
                'billing_interval': 'monthly',
                'trial_period_days': 14,
                'description': 'Advanced features for serious developers and career changers',
                'features': {
                    'courses_access': 'unlimited',
                    'ai_interactions': 500,
                    'collaboration': True,
                    'certificates': True,
                    'priority_support': True,
                    'mock_interviews': True,
                    'vr_ar_access': False,
                },
                'ai_interactions_limit': 500,
                'ai_tutor_access': True,
                'ai_mock_interviews': True,
                'ai_code_review': True,
                'collaboration_rooms': True,
                'peer_programming': True,
                'mentorship_access': True,
                'display_order': 3,
                'is_featured': True,
                'is_popular': True,
            },
            {
                'name': 'Pro',
                'plan_type': 'pro',
                'price': 79.99,
                'billing_interval': 'monthly',
                'trial_period_days': 14,
                'description': 'Everything you need to master programming and advance your career',
                'features': {
                    'courses_access': 'unlimited',
                    'ai_interactions': 'unlimited',
                    'collaboration': True,
                    'certificates': True,
                    'priority_support': True,
                    'mock_interviews': True,
                    'vr_ar_access': True,
                    'white_label': False,
                },
                'ai_tutor_access': True,
                'ai_mock_interviews': True,
                'ai_code_review': True,
                'ai_personalization': True,
                'collaboration_rooms': True,
                'peer_programming': True,
                'mentorship_access': True,
                'vr_ar_access': True,
                'priority_support': True,
                'certification_access': True,
                'display_order': 4,
                'is_featured': True,
            },
        ]
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'Created subscription plan: {plan.name}')
    
    def create_notification_templates(self):
        """Create notification templates"""
        templates = [
            {
                'name': 'Welcome Email',
                'notification_type': 'welcome_email',
                'title_template': 'Welcome to {platform_name}, {user_name}!',
                'message_template': 'Welcome to {platform_name}! We\'re excited to help you on your coding journey.',
                'channels': ['email', 'in_app'],
                'default_channel': 'email',
                'priority': 'medium',
                'is_active': True,
            },
            {
                'name': 'Course Enrollment',
                'notification_type': 'course_enrollment',
                'title_template': 'Successfully enrolled in {course_title}',
                'message_template': 'You\'ve been enrolled in {course_title}. Start learning now!',
                'channels': ['in_app', 'email'],
                'default_channel': 'in_app',
                'priority': 'medium',
                'is_active': True,
            },
            {
                'name': 'Lesson Completion',
                'notification_type': 'lesson_completion',
                'title_template': 'Lesson completed! 🎉',
                'message_template': 'Great job completing {lesson_title}! Keep up the momentum.',
                'channels': ['in_app'],
                'default_channel': 'in_app',
                'priority': 'low',
                'is_active': True,
            },
            {
                'name': 'Assessment Result',
                'notification_type': 'assessment_result',
                'title_template': 'Assessment results ready',
                'message_template': 'Your assessment results for {assessment_title} are ready. Score: {score}%',
                'channels': ['in_app', 'email'],
                'default_channel': 'in_app',
                'priority': 'high',
                'is_active': True,
            },
            {
                'name': 'AI Recommendation',
                'notification_type': 'ai_recommendation',
                'title_template': 'New learning recommendation',
                'message_template': 'Based on your progress, we recommend: {recommendation_title}',
                'channels': ['in_app'],
                'default_channel': 'in_app',
                'priority': 'medium',
                'is_active': True,
            },
            {
                'name': 'Payment Success',
                'notification_type': 'payment_success',
                'title_template': 'Payment successful',
                'message_template': 'Your payment of ${amount} has been processed successfully.',
                'channels': ['email', 'in_app'],
                'default_channel': 'email',
                'priority': 'high',
                'is_active': True,
            },
            {
                'name': 'Payment Failed',
                'notification_type': 'payment_failed',
                'title_template': 'Payment failed',
                'message_template': 'We couldn\'t process your payment for {plan_name}. Please update your payment method.',
                'channels': ['email', 'in_app'],
                'default_channel': 'email',
                'priority': 'urgent',
                'is_active': True,
            },
            {
                'name': 'Collaboration Invite',
                'notification_type': 'collaboration_invite',
                'title_template': 'Collaboration invitation',
                'message_template': '{sender_name} invited you to collaborate on {room_name}',
                'channels': ['in_app', 'email'],
                'default_channel': 'in_app',
                'priority': 'high',
                'is_active': True,
            },
        ]
        
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created notification template: {template.name}')
    
    def create_admin_user(self):
        """Create admin user"""
        email = input('Enter admin email: ')
        password = input('Enter admin password: ')
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists'))
            return
        
        admin_user = User.objects.create_superuser(
            email=email,
            username=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        
        # Create preferences for admin user
        UserPreferences.objects.create(user=admin_user)
        
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {email}'))
    
    def load_sample_data(self):
        """Load sample data for development"""
        # This would create sample courses, users, etc.
        self.stdout.write(self.style.SUCCESS('Sample data loading would go here'))
