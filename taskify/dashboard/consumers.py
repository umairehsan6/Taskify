import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, Tasks
from users.models import SignupUser
from django.utils import timezone
from django.contrib.sessions.models import Session
from dashboard.models import TaskReadStatus

logger = logging.getLogger(__name__)

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.task_group_name = f'chat_{self.task_id}'

        user_id = await self.get_user_id_from_session(self.scope['session'].session_key)
        if user_id:
            # Mark messages as read for this user and task
            await self.mark_task_as_read(user_id, self.task_id)
        
        # Join room group
        await self.channel_layer.group_add(
            self.task_group_name,
            self.channel_name
        )
        await self.accept()

        # Send existing comments
        existing_comments = await self.get_existing_comments(self.task_id)
        for comment in existing_comments:
            await self.send(text_data=json.dumps(comment))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.task_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        task_id = text_data_json['task_id']
        
        # Get user from session
        session_key = self.scope['session'].session_key
        if not session_key:
            await self.send(text_data=json.dumps({'error': 'Session not found.'}))
            return

        user_id = await self.get_user_id_from_session(session_key)
        if not user_id:
            await self.send(text_data=json.dumps({'error': 'User not authenticated.'}))
            return

        # Save the message to the database
        chat_message = await self.save_message(user_id, task_id, message_content)
        
        if chat_message:
            # Send message to room group
            await self.channel_layer.group_send(
                self.task_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'username': chat_message.user.username,
                    'timestamp': chat_message.timestamp.strftime('%B %d, %Y %H:%M'),
                    'sender_user_id': user_id,
                    'task_id': task_id  # Add task_id for notifications
                }
            )
            
            # Send unread notification to all users except the sender
            await self.send_unread_notification(task_id, user_id)
        else:
            await self.send(text_data=json.dumps({'error': 'Failed to save message.'}))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']
        task_id = event.get('task_id')
        # For other clients, check if the sender is the current user based on their session
        current_user_id = await self.get_user_id_from_session(self.scope['session'].session_key)
        is_current_user = (current_user_id == event.get('sender_user_id')) 

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
            'is_current_user': is_current_user,
            'task_id': task_id
        }))

    async def send_unread_notification(self, task_id, sender_user_id):
        """Send unread notification to all users except the sender"""
        # Get all users who should receive the notification
        users_to_notify = await self.get_users_to_notify(task_id, sender_user_id)
        
        for user_id in users_to_notify:
            # Send notification to each user's personal channel
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'unread_notification',
                    'task_id': task_id,
                    'has_unread': True
                }
            )

    @database_sync_to_async
    def get_users_to_notify(self, task_id, sender_user_id):
        """Get all users who should receive unread notifications for this task"""
        try:
            task = Tasks.objects.get(id=task_id)
            users_to_notify = set()
            
            # Add the assigned user
            if task.assigned_to and task.assigned_to.user:
                users_to_notify.add(task.assigned_to.user.id)
            
            # Add the user who assigned the task
            if task.assigned_from:
                users_to_notify.add(task.assigned_from.id)
            
            # Remove the sender from the notification list
            users_to_notify.discard(sender_user_id)
            
            return list(users_to_notify)
        except Tasks.DoesNotExist:
            return []

    @database_sync_to_async
    def get_existing_comments(self, task_id):
        try:
            task = Tasks.objects.get(id=task_id)
            messages = ChatMessage.objects.filter(task=task).select_related('user').order_by('timestamp')
            comments_data = []
            for msg in messages:
                comments_data.append({
                    'username': msg.user.username if msg.user else 'Unknown User',
                    'message': msg.message,
                    'timestamp': msg.timestamp.strftime('%B %d, %Y %H:%M') if msg.timestamp else '',
                    'is_current_user': msg.user.id == self.scope['session'].get('user_id') if msg.user else False
                })
            return comments_data
        except Tasks.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(self, user_id, task_id, message_content):
        try:
            task = Tasks.objects.get(id=task_id)
            user = SignupUser.objects.get(id=user_id)
            chat_msg = ChatMessage.objects.create(
                task=task,
                user=user,
                message=message_content
            )
            return chat_msg
        except (Tasks.DoesNotExist, SignupUser.DoesNotExist) as e:
            print(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def get_user_id_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            return session.get_decoded().get('user_id')
        except Session.DoesNotExist:
            return None

    @database_sync_to_async
    def get_historical_messages(self):
        # Fetch historical messages for the specific task
        messages = ChatMessage.objects.filter(task__id=self.task_id).order_by('timestamp').select_related('user')
        return [{
            'message': msg.message,
            'username': msg.user.username,
            'timestamp': msg.timestamp.strftime('%B %d, %Y %H:%M'),
            'sender_id': str(msg.user.id) # Include sender_id for correct client-side rendering
        } for msg in messages]

    async def send_historical_messages(self):
        messages = await self.get_historical_messages()
        for message_data in messages:
            # For historical messages, determine is_current_user for each message individually
            is_current_user = str(message_data['sender_id']) == str(self.scope['session'].get('user_id'))
            await self.send(text_data=json.dumps({
                'message': message_data['message'],
                'username': message_data['username'],
                'timestamp': message_data['timestamp'],
                'is_current_user': is_current_user
            }))

    @database_sync_to_async
    def mark_task_as_read(self, user_id, task_id):
        try:
            user = SignupUser.objects.get(id=user_id)
            task = Tasks.objects.get(id=task_id)
            TaskReadStatus.objects.update_or_create(
                user=user,
                task=task,
                defaults={'last_read_at': timezone.now()}
            )
            print(f"User {user_id} marked task {task_id} as read.")
        except (SignupUser.DoesNotExist, Tasks.DoesNotExist) as e:
            print(f"Error marking task as read: {e}")

# Add new consumer for user notifications
class UserNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_group_name = None  # Initialize to None
        user_id = await self.get_user_id_from_session(self.scope['session'].session_key)
        if not user_id:
            await self.close()
            return
        
        self.user_group_name = f'user_{user_id}'
        
        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Only try to leave the group if we successfully joined it
        if self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def unread_notification(self, event):
        """Handle unread notification for the current user"""
        await self.send(text_data=json.dumps({
            'type': 'unread_notification',
            'task_id': event['task_id'],
            'has_unread': event['has_unread']
        }))

    @database_sync_to_async
    def get_user_id_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            return session.get_decoded().get('user_id')
        except Session.DoesNotExist:
            return None 