import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, tasks, projects
from .models import users
from django.utils import timezone
from django.contrib.sessions.models import Session
from .models import read_status
import asyncio

logger = logging.getLogger(__name__)

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.task_group_name = f'chat_{self.task_id}'
        self.user_id = None
        self.is_viewing = True  # Track if user is actively viewing

        user_id = await self.get_user_id_from_session(self.scope['session'].session_key)
        if user_id:
            self.user_id = user_id
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
        # Mark that user is no longer viewing
        self.is_viewing = False
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.task_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'modal_close':
            # Handle modal close event
            self.is_viewing = False
            logger.info(f"User {self.user_id} stopped viewing task {self.task_id}")
            return
        elif message_type == 'modal_open':
            # Handle modal open event
            self.is_viewing = True
            logger.info(f"User {self.user_id} started viewing task {self.task_id}")
            return
        
        # Handle regular message
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

        # Only mark as read if this user is actively viewing the conversation
        # and this is not their own message
        if not is_current_user and current_user_id and self.is_viewing:
            await self.mark_task_as_read(current_user_id, task_id)
            
            # Send notification to hide the indicator for this user
            await self.channel_layer.group_send(
                f'user_{current_user_id}',
                {
                    'type': 'unread_notification',
                    'task_id': task_id,
                    'has_unread': False
                }
            )
            
            # Also check if we should hide project indicator
            project_id = await self.get_project_id_from_task(task_id)
            if project_id:
                # Check if all tasks in this project are now read
                all_tasks_read = await self.check_all_project_tasks_read(current_user_id, project_id)
                if all_tasks_read:
                    logger.info(f"All tasks in project {project_id} are read for user {current_user_id}, hiding project indicator")
                    await self.channel_layer.group_send(
                        f'user_{current_user_id}',
                        {
                            'type': 'project_unread_notification',
                            'project_id': project_id,
                            'has_unread': False
                        }
                    )

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
        logger.info(f"Starting send_unread_notification for task {task_id}, sender {sender_user_id}")
        
        # Get all users who should receive the notification
        users_to_notify = await self.get_users_to_notify(task_id, sender_user_id)
        logger.info(f"Users to notify: {users_to_notify}")
        
        for user_id in users_to_notify:
            logger.info(f"Sending notifications to user {user_id}")
            
            # Send notification to each user's personal channel
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'unread_notification',
                    'task_id': task_id,
                    'has_unread': True
                }
            )
            logger.info(f"Sent task unread notification to user {user_id}")
            
            # Also send project-level notification
            project_id = await self.get_project_id_from_task(task_id)
            logger.info(f"Got project_id {project_id} for task {task_id}")
            
            if project_id:
                logger.info(f"Sending project unread notification for project {project_id} to user {user_id}")
                await self.channel_layer.group_send(
                    f'user_{user_id}',
                    {
                        'type': 'project_unread_notification',
                        'project_id': project_id,
                        'has_unread': True
                    }
                )
                logger.info(f"Sent project unread notification to user {user_id}")
            else:
                logger.warning(f"No project_id found for task {task_id}")

    @database_sync_to_async
    def get_users_to_notify(self, task_id, sender_user_id):
        """Get all users who should receive unread notifications for this task"""
        try:
            task = tasks.objects.get(id=task_id)
            users_to_notify = set()
            
            # Add the assigned user
            if task.assigned_to:
                users_to_notify.add(task.assigned_to.id)
            
            # Add the user who assigned the task
            if task.assigned_from:
                users_to_notify.add(task.assigned_from.id)
            
            # Remove the sender from the notification list
            users_to_notify.discard(sender_user_id)
            
            return list(users_to_notify)
        except tasks.DoesNotExist:
            return []

    @database_sync_to_async
    def get_existing_comments(self, task_id):
        try:
            task = tasks.objects.get(id=task_id)
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
        except tasks.DoesNotExist:
            return []

    @database_sync_to_async
    def save_message(self, user_id, task_id, message_content):
        try:
            task = tasks.objects.get(id=task_id)
            user = users.objects.get(id=user_id)
            chat_msg = ChatMessage.objects.create(
                task=task,
                user=user,
                message=message_content
            )
            return chat_msg
        except (tasks.DoesNotExist, users.DoesNotExist) as e:
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
    def get_project_id_from_task(self, task_id):
        """Get the project ID for a given task ID"""
        try:
            task = tasks.objects.get(id=task_id)
            return task.project.id
        except tasks.DoesNotExist:
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
            user = users.objects.get(id=user_id)
            task = tasks.objects.get(id=task_id)
            
            # Get the latest message timestamp using the correct related name
            latest_message = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
            if latest_message:
                logger.info(f"Marking task {task_id} as read for user {user_id} with latest message timestamp {latest_message.timestamp}")
                read_status.objects.update_or_create(
                    user=user,
                    task=task,
                    defaults={'last_read_at': latest_message.timestamp}
                )
                logger.info(f"Successfully marked task {task_id} as read for user {user_id}")
            else:
                logger.info(f"No messages found for task {task_id}, skipping read status update")
        except (users.DoesNotExist, tasks.DoesNotExist) as e:
            logger.error(f"Error marking task as read: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in mark_task_as_read: {e}")

    @database_sync_to_async
    def check_all_project_tasks_read(self, user_id, project_id):
        """Check if all tasks in a project are read for the given user"""
        try:
            user = users.objects.get(id=user_id)
            project = projects.objects.get(id=project_id)
            
            # Get all tasks in the project
            project_tasks = tasks.objects.filter(project=project)
            
            for task in project_tasks:
                # Check if this task has unread messages
                last_read_status = read_status.objects.filter(user=user, task=task).first()
                latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
                
                if latest_comment:
                    # If there's no read status or the latest comment is newer than last read
                    if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                       latest_comment.user != user:
                        # This task has unread messages, so project should still show indicator
                        return False
            
            # All tasks are read
            return True
            
        except (users.DoesNotExist, projects.DoesNotExist):
            return False
        except Exception as e:
            logger.error(f"Error checking project tasks read status: {e}")
            return False

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

    async def project_unread_notification(self, event):
        """Handle project unread notification for the current user"""
        logger.info(f"UserNotificationConsumer received project_unread_notification: {event}")
        await self.send(text_data=json.dumps({
            'type': 'project_unread_notification',
            'project_id': event['project_id'],
            'has_unread': event['has_unread']
        }))
        logger.info(f"Sent project notification to client: project_id={event['project_id']}, has_unread={event['has_unread']}")

    @database_sync_to_async
    def get_user_id_from_session(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            return session.get_decoded().get('user_id')
        except Session.DoesNotExist:
            return None 