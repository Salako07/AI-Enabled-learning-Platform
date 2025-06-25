import json
import uuid
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import CollaborationRoom, RoomParticipant, CodeCollaboration

class CollaborationRoomConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time collaboration rooms"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'collaboration_room_{self.room_id}'
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check if user has permission to join the room
        has_permission = await self.check_room_permission()
        if not has_permission:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to room participants
        await self.add_participant()
        
        # Notify others about user joining
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'username': self.user.username,
                'full_name': self.user.get_full_name(),
            }
        )
    
    async def disconnect(self, close_code):
        # Remove user from room participants
        await self.remove_participant()
        
        # Notify others about user leaving
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'screen_share':
                await self.handle_screen_share(data)
            elif message_type == 'webrtc_signal':
                await self.handle_webrtc_signal(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'whiteboard_update':
                await self.handle_whiteboard_update(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def handle_chat_message(self, data):
        message = data.get('message', '')
        if message.strip():
            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'full_name': self.user.get_full_name(),
                    'timestamp': str(timezone.now()),
                }
            )
    
    async def handle_webrtc_signal(self, data):
        target_user = data.get('target_user')
        signal_data = data.get('signal_data')
        
        # Send WebRTC signal to specific user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_signal',
                'signal_data': signal_data,
                'from_user': str(self.user.id),
                'target_user': target_user,
            }
        )
    
    async def handle_cursor_position(self, data):
        # Broadcast cursor position to other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_position',
                'user_id': str(self.user.id),
                'position': data.get('position'),
            }
        )
    
    async def handle_whiteboard_update(self, data):
        # Update whiteboard and broadcast to others
        await self.update_whiteboard_data(data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'whiteboard_update',
                'user_id': str(self.user.id),
                'update_data': data.get('update_data'),
            }
        )
    
    # Group message handlers
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event['full_name'],
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'full_name': event['full_name'],
            'timestamp': event['timestamp'],
        }))
    
    async def webrtc_signal(self, event):
        # Only send to target user
        if event.get('target_user') == str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'webrtc_signal',
                'signal_data': event['signal_data'],
                'from_user': event['from_user'],
            }))
    
    async def cursor_position(self, event):
        # Don't send cursor position back to sender
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'user_id': event['user_id'],
                'position': event['position'],
            }))
    
    async def whiteboard_update(self, event):
        # Don't send update back to sender
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'whiteboard_update',
                'user_id': event['user_id'],
                'update_data': event['update_data'],
            }))
    
    @database_sync_to_async
    def check_room_permission(self):
        """Check if user has permission to join the room"""
        try:
            room = CollaborationRoom.objects.get(id=self.room_id)
            if room.privacy == 'public':
                return True
            elif room.privacy == 'private':
                return room.participants.filter(id=self.user.id).exists()
            elif room.privacy == 'invite_only':
                return RoomParticipant.objects.filter(
                    room=room, 
                    user=self.user, 
                    status='invited'
                ).exists()
            return False
        except CollaborationRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def add_participant(self):
        """Add user as participant to the room"""
        try:
            room = CollaborationRoom.objects.get(id=self.room_id)
            participant, created = RoomParticipant.objects.get_or_create(
                room=room,
                user=self.user,
                defaults={
                    'status': 'joined',
                    'joined_at': timezone.now()
                }
            )
            if not created:
                participant.status = 'joined'
                participant.joined_at = timezone.now()
                participant.save()
        except CollaborationRoom.DoesNotExist:
            pass
    
    @database_sync_to_async
    def remove_participant(self):
        """Update participant status when leaving"""
        try:
            participant = RoomParticipant.objects.get(
                room_id=self.room_id,
                user=self.user
            )
            participant.status = 'left'
            participant.left_at = timezone.now()
            participant.save()
        except RoomParticipant.DoesNotExist:
            pass
    
    @database_sync_to_async
    def update_whiteboard_data(self, data):
        """Update whiteboard data in database"""
        try:
            room = CollaborationRoom.objects.get(id=self.room_id)
            if not room.whiteboard_data:
                room.whiteboard_data = {}
            
            # Merge whiteboard updates
            room.whiteboard_data.update(data.get('update_data', {}))
            room.save()
        except CollaborationRoom.DoesNotExist:
            pass


class CodeCollaborationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time code collaboration"""
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'code_collaboration_{self.room_id}'
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Check permissions
        has_permission = await self.check_code_permission()
        if not has_permission:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current code state
        current_code = await self.get_current_code()
        await self.send(text_data=json.dumps({
            'type': 'code_state',
            'code': current_code,
        }))
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'code_change':
                await self.handle_code_change(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'selection_change':
                await self.handle_selection_change(data)
            elif message_type == 'code_execution':
                await self.handle_code_execution(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def handle_code_change(self, data):
        """Handle operational transform for code changes"""
        operation = data.get('operation')
        version = data.get('version')
        
        # Apply operational transform
        await self.apply_operation(operation, version)
        
        # Broadcast to other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'code_change',
                'operation': operation,
                'version': version,
                'user_id': str(self.user.id),
            }
        )
    
    async def handle_cursor_position(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_position',
                'user_id': str(self.user.id),
                'position': data.get('position'),
                'line': data.get('line'),
                'column': data.get('column'),
            }
        )
    
    async def handle_selection_change(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_change',
                'user_id': str(self.user.id),
                'selection': data.get('selection'),
            }
        )
    
    async def handle_code_execution(self, data):
        """Handle code execution requests"""
        # Execute code asynchronously
        execution_result = await self.execute_code(data.get('code'))
        
        # Broadcast execution result
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'execution_result',
                'result': execution_result,
                'user_id': str(self.user.id),
            }
        )
    
    # Group message handlers
    async def code_change(self, event):
        # Don't send change back to sender
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'code_change',
                'operation': event['operation'],
                'version': event['version'],
                'user_id': event['user_id'],
            }))
    
    async def cursor_position(self, event):
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'user_id': event['user_id'],
                'position': event['position'],
                'line': event['line'],
                'column': event['column'],
            }))
    
    async def selection_change(self, event):
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'selection_change',
                'user_id': event['user_id'],
                'selection': event['selection'],
            }))
    
    async def execution_result(self, event):
        await self.send(text_data=json.dumps({
            'type': 'execution_result',
            'result': event['result'],
            'user_id': event['user_id'],
        }))
    
    @database_sync_to_async
    def check_code_permission(self):
        """Check if user can collaborate on code in this room"""
        try:
            participant = RoomParticipant.objects.get(
                room_id=self.room_id,
                user=self.user
            )
            return participant.can_edit_code
        except RoomParticipant.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_current_code(self):
        """Get current code state"""
        try:
            code_session = CodeCollaboration.objects.get(room_id=self.room_id)
            return code_session.current_code
        except CodeCollaboration.DoesNotExist:
            return ""
    
    @database_sync_to_async
    def apply_operation(self, operation, version):
        """Apply operational transform to code"""
        try:
            code_session = CodeCollaboration.objects.get(room_id=self.room_id)
            
            # Add operation to edit history
            if not code_session.edit_history:
                code_session.edit_history = []
            
            code_session.edit_history.append({
                'operation': operation,
                'version': version,
                'user_id': str(self.user.id),
                'timestamp': str(timezone.now()),
            })
            
            # Apply operation to current code (simplified)
            if operation['type'] == 'insert':
                pos = operation['position']
                text = operation['text']
                current = code_session.current_code
                code_session.current_code = current[:pos] + text + current[pos:]
            elif operation['type'] == 'delete':
                start = operation['start']
                end = operation['end']
                current = code_session.current_code
                code_session.current_code = current[:start] + current[end:]
            
            code_session.version += 1
            code_session.save()
            
        except CodeCollaboration.DoesNotExist:
            # Create new code session
            CodeCollaboration.objects.create(
                room_id=self.room_id,
                current_code="",
                version=1,
                edit_history=[{
                    'operation': operation,
                    'version': version,
                    'user_id': str(self.user.id),
                    'timestamp': str(timezone.now()),
                }]
            )
    
    async def execute_code(self, code):
        """Execute code in sandbox environment"""
        # This would integrate with the code execution service
        # For now, return a mock result
        return {
            'success': True,
            'output': 'Code executed successfully',
            'execution_time': 0.5,
            'memory_used': 1024,
        }


class AITutorConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for AI tutor sessions"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Verify session belongs to user
        session_valid = await self.verify_session()
        if not session_valid:
            await self.close()
            return
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Update session status
        await self.end_session()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'code_help':
                await self.handle_code_help(data)
            elif message_type == 'explain_concept':
                await self.handle_explain_concept(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def handle_chat_message(self, data):
        """Handle chat message with AI tutor"""
        message = data.get('message')
        
        # Process message with AI
        ai_response = await self.get_ai_response(message)
        
        # Save conversation
        await self.save_conversation(message, ai_response)
        
        # Send AI response
        await self.send(text_data=json.dumps({
            'type': 'ai_response',
            'message': ai_response,
            'timestamp': str(timezone.now()),
        }))
    
    async def handle_code_help(self, data):
        """Handle code help request"""
        code = data.get('code')
        language = data.get('language')
        issue = data.get('issue')
        
        # Get AI code help
        ai_help = await self.get_ai_code_help(code, language, issue)
        
        await self.send(text_data=json.dumps({
            'type': 'code_help_response',
            'help': ai_help,
            'timestamp': str(timezone.now()),
        }))
    
    @database_sync_to_async
    def verify_session(self):
        """Verify AI tutor session belongs to user"""
        try:
            from ai_features.models import AITutorSession
            session = AITutorSession.objects.get(
                id=self.session_id,
                user=self.user
            )
            return session.status == 'active'
        except AITutorSession.DoesNotExist:
            return False
    
    async def get_ai_response(self, message):
        """Get response from AI service"""
        # This would integrate with OpenAI/Anthropic APIs
        # For now, return a mock response
        return f"AI response to: {message}"
    
    async def get_ai_code_help(self, code, language, issue):
        """Get AI help for code"""
        return {
            'suggestions': ['Check your syntax', 'Consider edge cases'],
            'explanation': 'Here\'s what might be wrong...',
            'improved_code': code,
        }
    
    @database_sync_to_async
    def save_conversation(self, user_message, ai_response):
        """Save conversation to database"""
        try:
            from ai_features.models import AITutorSession
            session = AITutorSession.objects.get(id=self.session_id)
            session.add_message('user', user_message)
            session.add_message('assistant', ai_response)
        except AITutorSession.DoesNotExist:
            pass
    
    @database_sync_to_async
    def end_session(self):
        """Mark session as ended"""
        try:
            from ai_features.models import AITutorSession
            session = AITutorSession.objects.get(id=self.session_id)
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
        except AITutorSession.DoesNotExist:
            pass


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        self.user_group_name = f'user_notifications_{self.user.id}'
        
        # Join user notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                await self.mark_notification_read(data.get('notification_id'))
                
        except json.JSONDecodeError:
            pass
    
    async def notification(self, event):
        """Send notification to user"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification'],
        }))
    
    async def unread_count_update(self, event):
        """Send updated unread count"""
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'count': event['count'],
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            from notifications.models import Notification
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.status = 'read'
            notification.opened_at = timezone.now()
            notification.save()
        except Notification.DoesNotExist:
            pass