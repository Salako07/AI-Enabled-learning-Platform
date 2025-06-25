from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, CourseModule, Lesson
from datetime import timedelta
from django.utils import timezone
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample courses and content for development'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample content...'))
        
        # Get or create an instructor
        instructor, created = User.objects.get_or_create(
            email='instructor@codemaster.com',
            defaults={
                'username': 'instructor',
                'first_name': 'John',
                'last_name': 'Instructor',
                'role': 'instructor',
                'is_staff': True,
            }
        )
        
        if created:
            instructor.set_password('instructor123')
            instructor.save()
        
        # Get programming fundamentals category
        category = Category.objects.get(slug='programming-fundamentals')
        
        # Create sample courses
        courses_data = [
            {
                'title': 'Python Programming Fundamentals',
                'slug': 'python-programming-fundamentals',
                'description': 'Learn Python programming from scratch with hands-on exercises and projects.',
                'short_description': 'Master Python basics with practical examples and exercises.',
                'difficulty': 'beginner',
                'is_free': True,
                'price': 0.00,
                'estimated_duration': timedelta(hours=20),
                'estimated_effort_hours': 20.0,
                'learning_objectives': [
                    'Understand Python syntax and basic concepts',
                    'Write and debug Python programs',
                    'Work with data structures and functions',
                    'Build simple applications'
                ],
                'prerequisites': [],
                'target_audience': 'Beginners with no programming experience',
            },
            {
                'title': 'JavaScript for Web Development',
                'slug': 'javascript-web-development',
                'description': 'Learn modern JavaScript and build interactive web applications.',
                'short_description': 'Master JavaScript for frontend and backend development.',
                'difficulty': 'intermediate',
                'is_free': False,
                'price': 49.99,
                'estimated_duration': timedelta(hours=30),
                'estimated_effort_hours': 30.0,
                'learning_objectives': [
                    'Master JavaScript ES6+ features',
                    'Build interactive web interfaces',
                    'Understand asynchronous programming',
                    'Work with APIs and databases'
                ],
                'prerequisites': ['Basic HTML and CSS knowledge'],
                'target_audience': 'Developers with basic web development knowledge',
            },
        ]
        
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults={
                    **course_data,
                    'instructor': instructor,
                    'category': category,
                    'status': 'published',
                    'published_at': timezone.now(),
                }
            )
            
            if created:
                self.stdout.write(f'Created course: {course.title}')
                
                # Create modules and lessons for the course
                self.create_course_content(course)
    
    def create_course_content(self, course):
        """Create modules and lessons for a course"""
        if 'Python' in course.title:
            self.create_python_course_content(course)
        elif 'JavaScript' in course.title:
            self.create_javascript_course_content(course)
    
    def create_python_course_content(self, course):
        """Create content for Python course"""
        modules_data = [
            {
                'title': 'Getting Started with Python',
                'description': 'Introduction to Python programming language',
                'order': 1,
                'estimated_duration': timedelta(hours=5),
                'lessons': [
                    {
                        'title': 'What is Python?',
                        'lesson_type': 'text',
                        'content': 'Python is a high-level programming language...',
                        'estimated_duration': timedelta(minutes=30),
                    },
                    {
                        'title': 'Installing Python',
                        'lesson_type': 'video',
                        'content': 'Learn how to install Python on your system...',
                        'estimated_duration': timedelta(minutes=45),
                    },
                    {
                        'title': 'Your First Python Program',
                        'lesson_type': 'coding_exercise',
                        'content': 'Write your first Python program...',
                        'has_coding_environment': True,
                        'coding_language': 'python',
                        'starter_code': 'print("Hello, World!")',
                        'estimated_duration': timedelta(minutes=60),
                    },
                ]
            },
            {
                'title': 'Python Basics',
                'description': 'Learn Python syntax and basic concepts',
                'order': 2,
                'estimated_duration': timedelta(hours=8),
                'lessons': [
                    {
                        'title': 'Variables and Data Types',
                        'lesson_type': 'interactive',
                        'content': 'Understanding Python variables and data types...',
                        'estimated_duration': timedelta(hours=1),
                    },
                    {
                        'title': 'Control Structures',
                        'lesson_type': 'coding_exercise',
                        'content': 'Learn about if statements, loops, and more...',
                        'has_coding_environment': True,
                        'coding_language': 'python',
                        'estimated_duration': timedelta(hours=2),
                    },
                ]
            },
        ]
        
        for module_data in modules_data:
            lessons_data = module_data.pop('lessons')
            module = CourseModule.objects.create(
                course=course,
                **module_data
            )
            
            for lesson_data in lessons_data:
                lesson_data['order'] = len(module.lessons.all()) + 1
                Lesson.objects.create(
                    module=module,
                    **lesson_data
                )
        
        self.stdout.write(f'Created content for course: {course.title}')
    
    def create_javascript_course_content(self, course):
        """Create content for JavaScript course"""
        # Similar structure as Python course
        pass
