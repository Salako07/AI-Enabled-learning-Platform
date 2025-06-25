from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from .models import User, UserSkill, UserLearningPath, UserPreferences, UserActivity
from .serializers import (
    UserSerializer, UserSkillSerializer, UserLearningPathSerializer,
    UserPreferencesSerializer, RegisterSerializer, LoginSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            # Create default preferences
            UserPreferences.objects.create(user=user)
            
            # Log registration activity
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'registration': True}
            )
            
            return Response({
                'user': UserSerializer(user).data,
                'access': str(access),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(email=email, password=password)
            if user and user.is_active:
                update_last_login(None, user)
                
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                
                # Log login activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return Response({
                    'user': UserSerializer(user).data,
                    'access': str(access),
                    'refresh': str(refresh),
                })
            
            return Response({
                'error': 'Invalid credentials or account is inactive'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log logout activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{frontend_url}/password-reset-confirm/{uid}/{token}/"
            
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Don't reveal whether user exists
            return Response({'message': 'If an account with that email exists, a password reset email has been sent.'}, 
                          status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uid, token, new_password]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not all([old_password, new_password]):
            return Response({'error': 'Both old and new passwords are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'avatar' not in request.data:
            return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.avatar = request.data['avatar']
        request.user.save()
        
        return Response({
            'message': 'Avatar uploaded successfully',
            'avatar_url': request.user.avatar.url if request.user.avatar else None
        })


class DeactivateAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        password = request.data.get('password')
        if not password or not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.is_active = False
        request.user.save()
        
        return Response({'message': 'Account deactivated successfully'}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        password = request.data.get('password')
        if not password or not request.user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            # Only show public profiles
            return User.objects.filter(public_profile=True, is_active=True)
        return super().get_queryset()
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow another user"""
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response({
                'error': 'Cannot follow yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # This would need a Follow model to implement properly
        # For now, just return success
        return Response({'status': 'followed'})
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get user dashboard data"""
        user = request.user
        recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:10]
        
        dashboard_data = {
            'user': UserSerializer(user).data,
            'recent_activities': [
                {
                    'type': activity.activity_type,
                    'timestamp': activity.timestamp,
                    'metadata': activity.metadata
                } for activity in recent_activities
            ]
        }
        
        return Response(dashboard_data)


class UserSkillViewSet(viewsets.ModelViewSet):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assess(self, request, pk=None):
        """Trigger AI assessment for a skill"""
        skill = self.get_object()
        # This would integrate with AI assessment service
        # For now, just update the assessment timestamp
        skill.save()  # This will update last_assessed due to auto_now=True
        
        return Response({'message': 'Assessment initiated'})


class UserLearningPathViewSet(viewsets.ModelViewSet):
    serializer_class = UserLearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserLearningPath.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a learning path"""
        learning_path = self.get_object()
        learning_path.status = 'in_progress'
        learning_path.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='course_start',
            metadata={'learning_path_id': str(learning_path.id)}
        )
        
        return Response({'message': 'Learning path started'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a learning path"""
        learning_path = self.get_object()
        learning_path.status = 'completed'
        learning_path.progress_percentage = 100.0
        learning_path.save()
        
        # Update user statistics
        request.user.courses_completed += 1
        request.user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='course_complete',
            metadata={'learning_path_id': str(learning_path.id)}
        )
        
        return Response({'message': 'Learning path completed'})
    
    @action(detail=False, methods=['post'])
    def generate_ai_path(self, request):
        """Generate AI-powered learning path"""
        prompt = request.data.get('prompt', '')
        target_skills = request.data.get('target_skills', [])
        difficulty = request.data.get('difficulty', 'intermediate')
        
        # This would integrate with AI service to generate personalized path
        # For now, create a basic path
        learning_path = UserLearningPath.objects.create(
            user=request.user,
            name=f"AI Generated Path",
            description=f"Generated based on: {prompt}",
            is_ai_generated=True,
            ai_generation_prompt=prompt,
            difficulty_level=difficulty,
            target_skills=target_skills,
            estimated_duration='40:00:00'  # 40 hours default
        )
        
        return Response(UserLearningPathSerializer(learning_path).data)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create user preferences"""
        preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return preferences
    
    def list(self, request):
        """Return single preferences object instead of list"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
    
    def create(self, request):
        """Update existing preferences instead of creating new"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """Update user preferences"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)