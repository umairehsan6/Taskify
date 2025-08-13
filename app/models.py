from hmac import new
from django.db import models
import random
from django.utils import timezone
from django.db.models import Sum
import logging
from datetime import datetime, timedelta
import os
from django.core.mail import send_mail
import pytz
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as DjangoUser 
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password 
from django.db.models import Q, F

# Create your models here.
class department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    @classmethod
    def add_departments(cls, name):
        if cls.objects.filter(name=name).exists():
            raise ValidationError(f"Department {name} already exists.")
        else:
            cls.objects.create(name=name)
    @classmethod
    def delete_department(cls, department_id):
        if not cls.objects.filter(id=department_id).exists():
            raise ValidationError(f"Department does not exist.")
        else:
            cls.objects.filter(id=department_id).delete()
    def __str__(self):
        return self.name


class users(models.Model):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('teamlead', 'Team Lead'),
        ('project_manager', 'Project Manager'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee')
    status = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    verification_created_at = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)

    @classmethod
    def register_by_admin(cls, fname, lname, username, email, password,confirm_password, department_id=None, selected_designations=None):
        if cls.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        if cls.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        if DjangoUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered as a superuser or staff user.")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        try:
            validate_password(password, user=None)
        except ValidationError as e:
            raise ValidationError(e.messages)
        hashed_password = make_password(password)
        
        with transaction.atomic(): # Ensure atomicity of all related creations
            user = cls.objects.create(
                first_name=fname,
                last_name=lname,
                username=username,
                email=email,
                password=hashed_password,
                role='employee',
                status=True,
                is_verified=False,
            )

            if department_id:
                try:
                    department_obj = department.objects.get(id=department_id)
                    employee_details.objects.create(user=user, department=department_obj)
                except department.DoesNotExist:
                    raise ValidationError("Selected department does not exist.")
            
            if selected_designations:
                for designation_value in selected_designations:
                    employee_designation.objects.create(
                        user=user,
                        designation=designation_value,
                        date_assigned=timezone.now()
                    )
        
        return user
    @classmethod
    def confirm_new_password(cls, user_id, password, confirm_password):
        try:
            user = cls.objects.get(id=user_id)
        except cls.DoesNotExist:
            raise ValidationError("Session error: User not found.")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        try:
            validate_password(password, user=user)
        except ValidationError as e:
            raise ValidationError(e.messages)

        user.password = make_password(password)
        user.save()
        return user
        
    @classmethod
    def login(cls, username, password):
        try:
            # Safely get the user. If the user doesn't exist, this raises a DoesNotExist error.
            user = cls.objects.get(username=username)
        except cls.DoesNotExist:
            # Catch the DoesNotExist error and raise a generic login error
            raise ValidationError("Invalid username or password.")

        if user.status is False:
            # Raise an error if the user account is inactive
            raise ValidationError("Your account is disabled by the admin.")

        if check_password(password, user.password):
            # Return the user object only on success
            return user
        else:
            # Raise an error for an incorrect password
            raise ValidationError("Invalid username or password.")
        
    @classmethod
    def password_reset(cls, email):
        try:
            # Look up the user by email. If not found, a DoesNotExist exception is raised.
            user = cls.objects.get(email=email)
        except cls.DoesNotExist:
            # Raise a generic ValidationError to prevent leaking user existence info.
            raise ValidationError("A user with this email does not exist.")

        # If the user is found, generate a new verification code.
        user.generate_verification_code()
        send_mail(
                    subject='Password Reset OTP',
                    message=f'Your OTP for password reset is {user.verification_code} if you did not request this, please ignore this email.',
                    from_email='arshadotpwala@gmail.com',
                    recipient_list=[email],
                )

        return user , "OTP sent successfully."

    def generate_verification_code(self):
        raw_otp = random.randint(100000, 999999)
        self.verification_code = str(raw_otp)
        self.verification_created_at = timezone.now()
        self.verification_attempts = 0
        self.save()
        return raw_otp

    def is_code_expired(self):
        if not self.verification_created_at:
            return True
        return self.verification_created_at + timezone.timedelta(minutes=2) < timezone.now()

    def is_code_valid(self, entered_code):
        if str(self.verification_code) == str(entered_code):
            self.verification_attempts = 0
            self.save()
            return True
        else:
            self.verification_attempts += 1
            self.save()
            return False

    def is_max_attempts_reached(self):
        return self.verification_attempts >= 3
    @classmethod 
    def disableuser(cls , user_id):
        try:
            user = cls.objects.get(id=user_id)
            current_role = user.role
            if current_role == 'admin':
                raise ValidationError("Cant DIsable a admin user.")
            elif user.status == False:
                user.status = True
                user.save()
                return user
            elif user.status == True:
                user.status = False
                user.save()
                return user
        except cls.DoesNotExist:
            raise ValidationError("User not found.")
    @classmethod
    def promote_user(cls, user_id, new_role):
        try:
            user = cls.objects.get(id=user_id)
        except cls.DoesNotExist:
            raise ValidationError("User not found.")

        if user.role == 'admin':
            raise ValidationError("Can't promote or demote an admin user.")

        if new_role not in dict(cls.ROLE_CHOICES):
            raise ValidationError("Invalid role.")

        user.role = new_role
        user.save()
        return user
    
        
        

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

    @property
    def department(self):
        """Get department from employee_details"""
        try:
            user_details = self.employee_details.first()
            return user_details.department if user_details else None
        except:
            return None

    #projects
class projects(models.Model):
    Status_CHOICES = [
        (0, 'Pending'),
        (1, 'Ongoing'),
        (2, 'Completed'),
        (3, 'On Hold'),
        (4, 'Cancelled'),
    ]
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    department = models.ForeignKey(department, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.IntegerField(choices=Status_CHOICES, default=0)

    #add projects
    @classmethod 
    def add_projects(cls , name , description , department_id , start_date , end_date , status):
        department_obj = department.objects.get(id=department_id)
        if cls.objects.filter(name=name).exists():
            raise ValidationError("Project name already exists.")
        elif department_obj is None:
            raise ValidationError("Department not found.")
        elif start_date > end_date:
            raise ValidationError("Start date must be before end date.")
        else:
            project = cls.objects.create(
                name = name,
                description = description,
                department = department_obj,
                start_date = start_date,
                end_date = end_date,
                status = status
            )
            return project
    @classmethod
    def update_project_status(cls , project_id , new_status ):
        try:
            project = cls.objects.get(id=project_id)
            project.status = int(new_status)
            if new_status not in dict(cls.Status_CHOICES):
                raise ValidationError("Invalid status.")
            elif new_status == 2:
                project.end_date = timezone.now().date()
                incomplete_tasks = project.tasks.exclude(status=2)
                if incomplete_tasks.exists():
                    raise ValidationError("Cannot complete project with incomplete tasks.")
            elif new_status == 0:
                project.end_date = None
                
            project.save()
            return project
        except cls.DoesNotExist:
            raise ValidationError("Project not found.")

    def __str__(self):
        return self.name
    
    @classmethod
    def get_project_tasks_data(cls, project_id, current_user):
        """Get all tasks for a project with complete data including unread message status"""
        from django.db.models import Max
        from .models import ChatMessage, read_status, tasks
        import logging
        logger = logging.getLogger(__name__)
        try:
            project = cls.objects.get(id=project_id)
            tasks_qs = tasks.objects.filter(project=project).select_related('assigned_to')
            tasks_qs = tasks_qs.annotate(latest_message=Max('messages__timestamp')).order_by('-latest_message', '-id')
            tasks_data = []
            for task in tasks_qs:
                assigned_name = 'Unassigned'
                if task.assigned_to:
                    assigned_name = f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to.first_name else task.assigned_to.username
                has_unread_messages = cls._check_task_unread_messages(task, current_user, logger)
                task_data = {
                    'id': task.id,
                    'task_name': task.task_name,
                    'task_description': task.task_description[:100] + '...' if len(task.task_description) > 100 else task.task_description,
                    'status': task.status,
                    'status_display': task.get_status_display(),
                    'priority': task.priority,
                    'report': task.report,
                    'file_name': task.task_file.name.split('/')[-1] if task.task_file else None,
                    'file_url': f"/dashboard/download_task_file/{task.id}/" if task.task_file else None,
                    'assigned_to': assigned_name,
                    'time_spent': task.get_total_time_spent(),
                    'has_unread_messages': has_unread_messages
                }
                tasks_data.append(task_data)
            logging.info("Successfully prepared tasks data for JSON response.")
            return {'success': True, 'tasks': tasks_data}
        except cls.DoesNotExist:
            logging.warning(f"Project with ID {project_id} not found.")
            return {'success': False, 'error': 'Project not found', 'status': 404}
        except Exception as e:
            logging.error(f"An unexpected error occurred in get_project_tasks_data for project ID {project_id}: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'status': 500}

    @staticmethod
    def _check_task_unread_messages(task, current_user, logger):
        from .models import ChatMessage, read_status
        has_unread_messages = False
        last_read_status = read_status.objects.filter(user=current_user, task=task).first()
        latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
        if latest_comment:
            if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
               latest_comment.user != current_user:
                has_unread_messages = True
                logger.info(f"Task {task.id} ({task.task_name}) has unread messages for user {current_user.id}")
            else:
                logger.debug(f"Task {task.id} ({task.task_name}) has no unread messages for user {current_user.id}")
        else:
            logger.debug(f"Task {task.id} ({task.task_name}) has no messages")
        return has_unread_messages

#tasks  
class tasks(models.Model):
    taks_status = [
        (0, 'Pending'),
        (1, 'In Progress'),
        (2, 'Completed'),
        (3, 'On Hold'),
        (4, 'Cancelled'),
        (5, 'Not Assigned'),
    ]
    task_priorty = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    project = models.ForeignKey(projects, on_delete=models.SET_NULL, null=True, blank=True , related_name='tasks')
    task_name = models.CharField(max_length=50)
    task_description = models.TextField()  # Field name is `task_description`
    assigned_to = models.ForeignKey(users, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned_to')
    assigned_from = models.ForeignKey(users, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned_from')
    priority = models.CharField(max_length=10, choices=task_priorty, default='medium')
    expected_time = models.DurationField(null=True, blank=True)  # Duration field for expected time
    task_file = models.FileField(upload_to='task_files/', null=True, blank=True)
    report = models.CharField(max_length=1000, null=True, blank=True)
    status = models.IntegerField(choices=taks_status, default=0)
    due_date = models.DateField(default=None, blank=True, null=True)
    submitted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_name} - {self.project.name} - {self.assigned_to.username if self.assigned_to else 'Unassigned'}"
    @classmethod
    def get_task_counts(cls, user, date=None):
            """Get various task counts for a user on a specific date (defaults to today)."""
            if date is None:
                date = timezone.now().date()

            # Create timezone-aware datetime objects for the day's boundaries
            start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end_of_day = timezone.make_aware(datetime.combine(date, datetime.max.time()))

            # Base queryset for user's tasks
            user_tasks = cls.objects.filter(assigned_to=user)

            return {
                'tasks_expiring_today': user_tasks.filter(
                    due_date=date
                ).exclude(status=2).count(),

                'expired_tasks': user_tasks.filter(
                    due_date__lt=date
                ).exclude(status=2).count(),

                'tasks_done_today': user_tasks.filter(
                    status=2,
                    submitted_on__gte=start_of_day,
                    submitted_on__lte=end_of_day
                ).count()
            }

    @classmethod
    def createtask(cls, project_id, task_name, task_description, assigned_to, assigned_from, priority, expected_time, status, due_date):
        if not all([project_id, task_name, assigned_to, assigned_from, due_date]):
            raise ValidationError("Missing required task fields.")

        try:
            project_obj = projects.objects.get(id=project_id)
        except projects.DoesNotExist:
            raise ValidationError("Project not found.")

        if assigned_to is None or assigned_from is None:
            raise ValidationError("Assigned user(s) not found.")

        if priority not in dict(cls.task_priorty):
            raise ValidationError("Invalid priority.")

        if status not in dict(cls.taks_status):
            raise ValidationError("Invalid status.")

        if due_date < timezone.now().date():
            raise ValidationError("Due date must be in the future.")

        task = cls.objects.create(
            project=project_obj,
            assigned_to=assigned_to,
            task_name=task_name,
            task_description=task_description,
            due_date=due_date,
            priority=priority,
            status=status,
            assigned_from=assigned_from,
            expected_time=expected_time
        )
        return task

    @classmethod
    def update_task_status(cls, task_id, new_status):
        try:
            task = cls.objects.get(id=task_id)
            
            # Validate the new status
            if str(new_status) == '' or new_status is None or new_status == 'completed':
                new_status = 2  # Completed
            
            new_status = int(new_status)
            if new_status not in dict(cls.taks_status):
                raise ValidationError("Invalid status.")
            
            # Handle approval transition (from status 5 to 3)
            if new_status == 3 and task.status == 5:
                task.status = new_status
                task.save()
                
                # Notify the assigned employee
                if task.assigned_to:
                    Notification.objects.create(
                        user=task.assigned_to,
                        message=f"Your task '{task.task_name}' has been approved and is now pending.",
                        is_read=False
                    )
                # Notify the creator if different
                if task.assigned_from and task.assigned_from != task.assigned_to:
                    Notification.objects.create(
                        user=task.assigned_from,
                        message=f"The task '{task.task_name}' you requested has been approved.",
                        is_read=False
                    )
                return task
            
            # Handle specific status transitions
            if new_status == 3:  # On Hold
                # If task is in progress, stop timer first
                if task.status == 1:
                    task_activity_log.stop_work(task)
                    task.status = 3
                    task.save()
                    return task
                elif task.status == 3:  # Already on hold
                    return task
                else:
                    raise ValidationError(f"Task cannot be put on hold from status: {task.get_status_display()}")
            
            # Handle starting work (status 1 - In Progress)
            elif new_status == 1:  # In Progress
                if task.status == 3:  # Only allow starting from On Hold status
                    # Get the user from the task's assigned_to field
                    user = task.assigned_to
                    if not user:
                        raise ValidationError("Task is not assigned to any user.")
                    
                    # Put any other active tasks for this user on hold
                    active_tasks = cls.objects.filter(
                        assigned_to=user,
                        status=1
                    ).exclude(id=task_id)
                    
                    for active_task in active_tasks:
                        active_task.status = 3
                        active_task.save()
                        # End any ongoing time tracking for other tasks
                        ongoing_sessions = task_activity_log.objects.filter(
                            task=active_task,
                            end_time__isnull=True
                        )
                        for session in ongoing_sessions:    
                            session.end_time = timezone.now()
                            session.duration = session.end_time - session.start_time
                            session.save()
                    
                    # Set the current task to in_progress
                    task.status = 1
                    task.save()
                    
                    # Start new time tracking session
                    session = task_activity_log.start_work(task)
                    return task
                else:
                    raise ValidationError(f"Task cannot be started from status: {task.get_status_display()}")
            
            # If completing and task is in progress, stop timer first
            if new_status == 2 and task.status == 1:
                task_activity_log.stop_work(task)
            
            # Update task status
            task.status = new_status
            if new_status == 2:  # Completed
                task.submitted_on = timezone.now()
            
            task.save()
            
            # Handle notifications
            department = None
            if task.assigned_to and hasattr(task.assigned_to, 'employee_details'):
                department = task.assigned_to.employee_details.first().department if task.assigned_to.employee_details.exists() else None
            
            if department:
                teamleads = users.objects.filter(employee_details__department=department, role='teamlead')
                admins = users.objects.filter(role='admin')
                users_to_notify = list(teamleads) + list(admins)
                
                # Remove duplicates by user id
                unique_users = {user.id: user for user in users_to_notify}.values()
                
                for user in unique_users:
                    Notification.objects.create(
                        user=user,
                        message=f"Task '{task.task_name}' from {task.project.name} by {task.assigned_to.first_name if task.assigned_to else 'Unknown'} has been updated to {task.get_status_display()} now you can view reports and files",
                        is_read=False
                    )
            
            return task
            
        except cls.DoesNotExist:
            raise ValidationError("Task does not exist.")

    #departments all tasks
    @classmethod
    def get_department_tasks(cls, department_obj):
        if department_obj:
            return cls.objects.filter(project__department=department_obj).select_related('project', 'assigned_to')
        return cls.objects.none()
    
    @classmethod
    def delete_task(cls, task_id, username=None):
        try:
            task = cls.objects.get(id=task_id)
            
            # Handle notification for rejected tasks (status 5)
            if task.status == 5 and username and task.assigned_to:
                from .models import Notification
                Notification.objects.create(
                    user=task.assigned_to,
                    message=f"Your task '{task.task_name}' has been rejected and deleted by {username}",
                    is_read=False
                )
            
            # Delete the task
            task.delete()
            return True
            
        except cls.DoesNotExist:
            raise ValidationError("Task does not exist.")
        except Exception as e:
            raise ValidationError(f"Error deleting task: {str(e)}")

    @classmethod
    def upload_task_file(cls, task_id, file):
        """Upload a file for a task"""
        try:
            task = cls.objects.get(id=task_id)
            if not file:
                raise ValidationError("No file provided.")
                
            # Save the file to the task
            task.task_file = file
            task.save()
            
            return {
                'success': True,
                'file_url': task.task_file.url,
                'file_name': task.task_file.name.split('/')[-1]
            }
            
        except cls.DoesNotExist:
            raise ValidationError("Task does not exist.")
        except Exception as e:
            raise ValidationError(f"Error uploading file: {str(e)}")
    
    @classmethod
    def upload_task_report(cls, task_id, report_text):
        """Upload a report for a task"""
        try:
            task = cls.objects.get(id=task_id)
            if not report_text:
                raise ValidationError("Report text is required.")
                
            # Save the report to the task
            task.report = report_text
            task.save()
            
            return {
                'success': True,
                'message': 'Report submitted successfully.'
            }
            
        except cls.DoesNotExist:
            raise ValidationError("Task does not exist.")
        except Exception as e:
            raise ValidationError(f"Error submitting report: {str(e)}")
    
    @classmethod
    def get_task_file(cls, task_id):
        """Get the file for a task"""
        try:
            task = cls.objects.get(id=task_id)
            if not task.task_file:
                raise ValidationError("Task has no file attached.")
                
            file_path = task.task_file.path
            if not os.path.exists(file_path):
                raise ValidationError("File not found on server.")
                
            return {
                'success': True,
                'file_path': file_path,
                'file_name': os.path.basename(file_path)
            }
            
        except cls.DoesNotExist:
            raise ValidationError("Task does not exist.")
        except Exception as e:
            raise ValidationError(f"Error retrieving file: {str(e)}")     
    
    def get_total_time_spent(self):
        total_duration = task_activity_log.objects.filter(task=self).aggregate(
            total=Sum('duration')
        )['total']
        if total_duration:
            # Convert to hours and minutes
            total_seconds = total_duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            result = f"{hours}h {minutes}m"
            return result
        return "0h 0m"
    
    def get_expected_time_display(self):
        if self.expected_time:
            total_seconds = self.expected_time.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"

class task_activity_log(models.Model):
    task = models.ForeignKey('tasks', on_delete=models.CASCADE, related_name='activity_logs')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Activity log for {self.task.task_name}"

    def calculate_duration(self):
        if self.end_time:
            self.duration = self.end_time - self.start_time
            self.save()
        return self.duration
    @classmethod
    def get_user_total_time_today(cls, user):
        """Calculate total time spent by user today"""
        now = timezone.localtime(timezone.now())
        today = now.date()
        start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        
        utc_start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        utc_end_of_today = timezone.make_aware(datetime.combine(today, datetime.max.time()))

        # Get completed logs for today
        completed_logs_ending_today = cls.objects.filter(
            task__assigned_to=user,
            end_time__gte=utc_start_of_today,
            end_time__lte=utc_end_of_today,
            end_time__isnull=False
        )
            
        completed_duration_sum = completed_logs_ending_today.aggregate(
            total=Sum('duration')
        )['total'] or timedelta(0)
        
        total_duration_today = completed_duration_sum

        # Get ongoing tasks
        ongoing_tasks = cls.objects.filter(
            task__assigned_to=user,
            end_time__isnull=True
        )
        
        for log in ongoing_tasks:
            local_start = timezone.localtime(log.start_time)
            
            if local_start.date() == today:
                current_duration = now - local_start
                total_duration_today += current_duration
                
            elif local_start.date() < today:
                current_duration_today = now - start_of_today
                total_duration_today += current_duration_today

        total_seconds = total_duration_today.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return f"{hours}h {minutes}m {seconds}s"
    



    @classmethod
    def start_work(cls, task):
        # End any ongoing sessions for this task
        ongoing_sessions = cls.objects.filter(
            task=task,
            end_time__isnull=True
        )
        for session in ongoing_sessions:
            session.end_time = timezone.now()
            session.calculate_duration()
            session.save()

        # Create new session
        return cls.objects.create(task=task)
    


    @classmethod
    def stop_work(cls, task):
        logger = logging.getLogger(__name__)
        karachi_tz = pytz.timezone('Asia/Karachi')
        try:
            logger.info(f"Attempting to stop work for task: {task.task_name}")
            current_session = cls.objects.get(task=task, end_time__isnull=True)
            current_time = timezone.now().astimezone(karachi_tz)
            logger.info(f"Found active session. Current time: {current_time}")
            # If stopping outside office hours, set end time to last office hour
            if not settings.is_within_office_hours(current_time):
                day_name = current_time.strftime('%A').lower()
                try:
                    office_hours = settings.objects.get(day=day_name)
                    current_time = karachi_tz.localize(
                        timezone.datetime.combine(current_time.date(), office_hours.end_time)
                    )
                    logger.info(f"Adjusted end time to office hours end: {current_time}")
                except settings.DoesNotExist:
                    logger.warning(f"No office hours found for {day_name}")
            current_session.end_time = current_time
            logger.info(f"Set end_time to: {current_time}")
            # Calculate duration
            duration = current_session.calculate_duration()
            logger.info(f"Calculated duration: {duration}")
            # Force save to ensure duration is stored
            current_session.save(force_update=True)
            logger.info("Saved session with duration")
            return current_session
        except cls.DoesNotExist:
            logger.warning(f"No active session found for task: {task.task_name}")
            return None
        except Exception as e:
            logger.error(f"Error stopping work: {str(e)}")
            return None

class settings(models.Model):
    day = models.CharField(max_length=10, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'app_settings'
        ordering = ['day']
        constraints = [
            models.UniqueConstraint(fields=['day'], name='unique_day_entry')
        ]

    @classmethod
    def get_office_hours(cls):
        """Get all office hours ordered by day"""
        return cls.objects.all().order_by('day')

    @classmethod
    def add_office_hours(cls, day, start_time, end_time, break_start_time=None, break_end_time=None):
        """Add new office hours for a day"""
        try:
            cls.objects.create(
                day=day,
                start_time=start_time,
                end_time=end_time,
                break_start_time=break_start_time,
                break_end_time=break_end_time
            )
        except Exception as e:
            raise ValidationError(f"Error adding office hours: {str(e)}")

    @classmethod
    def update_office_hours(cls, day, start_time, end_time, break_start_time=None, break_end_time=None):
        """Update office hours for a specific day"""
        try:
            office_hours = cls.objects.get(day=day)
            office_hours.start_time = start_time
            office_hours.end_time = end_time
            office_hours.break_start_time = break_start_time
            office_hours.break_end_time = break_end_time
            office_hours.save()
        except cls.DoesNotExist:
            raise ValidationError(f"Office hours for {day} not found.")
        except Exception as e:
            raise ValidationError(f"Error updating office hours: {str(e)}")

    @classmethod
    def delete_office_hours(cls, day):
        """Delete office hours for a specific day"""
        try:
            office_hours = cls.objects.get(day=day)
            office_hours.delete()
        except cls.DoesNotExist:
            raise ValidationError(f"Office hours for {day} not found.")
        except Exception as e:
            raise ValidationError(f"Error deleting office hours: {str(e)}")

    def __str__(self):
        return f"{self.day.capitalize()} ({self.start_time} - {self.end_time})"
    
    @classmethod
    def is_within_office_hours(cls, datetime_obj):
        #Check if a given datetime is within office hours
        day_name = datetime_obj.strftime('%A').lower()
        try:
            office_hours = cls.objects.get(day=day_name)
            current_time = datetime_obj.time()
            
            # Debug logging
            print(f"Checking office hours for {day_name}:")
            print(f"Current time: {current_time}")
            print(f"Office hours: {office_hours.start_time} - {office_hours.end_time}")
            print(f"Break time: {office_hours.break_start_time} - {office_hours.break_end_time}")
            
            # Check if we're in break time
            if (office_hours.break_start_time and office_hours.break_end_time and 
                office_hours.break_start_time <= current_time <= office_hours.break_end_time):
                print("Currently in break time")
                return False
                
            # Check if we're within office hours
            is_within = office_hours.start_time <= current_time <= office_hours.end_time
            print(f"Within office hours: {is_within}")
            return is_within
            
        except cls.DoesNotExist:
            print(f"No office hours defined for {day_name}")
            return False

class companyDetails(models.Model):
    company_logo = models.ImageField(upload_to='company_logo/', null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    company_phone = models.CharField(max_length=15, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    company_website = models.URLField(null=True, blank=True)
    company_address = models.TextField(null=True, blank=True)
    company_founded_date = models.DateField(null=True, blank=True)
    company_social_media_links = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Company Details'
        verbose_name_plural = 'Company Details'

    def save(self, *args, **kwargs):
        # Delete all other instances except this one
        companyDetails.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        # Get or create the single instance
        instance, created = cls.objects.get_or_create(pk=1)
        return instance

    def update_details(self, *, company_name=None, company_description=None, company_email=None, company_phone=None, company_website=None, company_address=None, company_founded_date=None, company_logo_file=None, social_media_links_json=None, social_platforms=None, social_urls=None):
        """
        Updates the company details instance from provided parameters (no request object).
        Handles business logic, including validation, parsing, and file management.
        """
        import os, json
        from datetime import datetime
        self.company_name = company_name
        self.company_description = company_description
        self.company_email = company_email
        self.company_phone = company_phone
        self.company_website = company_website
        self.company_address = company_address
        # Parse date
        if company_founded_date:
            try:
                if isinstance(company_founded_date, str):
                    self.company_founded_date = datetime.strptime(company_founded_date, '%Y-%m-%d').date()
                else:
                    self.company_founded_date = company_founded_date
            except Exception:
                self.company_founded_date = None
        else:
            self.company_founded_date = None
        # Handle logo upload
        if company_logo_file:
            if self.company_logo:
                try:
                    os.remove(self.company_logo.path)
                except Exception:
                    pass
            self.company_logo = company_logo_file
        # Handle social media links
        if social_media_links_json:
            try:
                self.company_social_media_links = json.loads(social_media_links_json)
            except json.JSONDecodeError:
                links = {}
                if social_platforms and social_urls:
                    for i, platform in enumerate(social_platforms):
                        if i < len(social_urls) and social_urls[i]:
                            links[platform] = social_urls[i]
                self.company_social_media_links = links
        elif social_platforms and social_urls:
            links = {}
            for i, platform in enumerate(social_platforms):
                if i < len(social_urls) and social_urls[i]:
                    links[platform] = social_urls[i]
            self.company_social_media_links = links
        return self

    def __str__(self):
        return self.company_name if self.company_name else "Company Details"
    

class employee_details(models.Model):
    GENDER_CHOICES = [
        (0, 'Male'),
        (1, 'Female'),
        (2, 'Other'),
    ]
    user = models.ForeignKey(users, on_delete=models.CASCADE, related_name='employee_details')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    # designation = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_details')

    class Meta:
        db_table = 'app_employee_details'
    
    @classmethod
    def assign_department(cls , department_id , user_id):
        user = users.objects.get(id=user_id)
        department_obj = department.objects.get(id=department_id)
        if not department_obj:
            raise ValidationError(f"Department does not exist.")
        elif not user:
            raise ValidationError(f"User does not exist.")    
        else:
            #replace old department
            employee_detail_obj = employee_details.objects.get(user=user)
            employee_detail_obj.department = department_obj
            employee_detail_obj.save()
        return employee_detail_obj

    @classmethod
    def get_admin_profile_context(cls, user_id):
        from .models import users, employee_designation, department
        context = {}
        user = users.objects.get(id=user_id)
        user_role = getattr(user, 'role', 'emp')
        user_details = cls.objects.filter(user=user).first()
        user_designation = employee_designation.objects.filter(user=user)
        designation_choice = employee_designation.designation_choices
        current_designations = user_designation.values_list('designation', flat=True)
        designation_list = []
        for item in current_designations:
            designation_list.extend([d.strip() for d in str(item).split(',')])
        current_designations = designation_list
        departments_obj = department.objects.all()
        context = {
            'user': user,
            'user_role': user_role,
            'user_details': user_details,
            'user_designation': user_designation,
            'departments': departments_obj,
            'designation_choices': designation_choice,
            'current_designations': designation_list,
        }
        return context

    @classmethod
    def update_admin_profile(cls, user_id, department_id, designation_codes):
        from .models import users, department, employee_designation
        from django.db import transaction
        user_obj = users.objects.get(id=user_id)
        department_obj = department.objects.get(id=department_id)
        employee_instance, created = cls.objects.update_or_create(user=user_obj, defaults={'department': department_obj})
        with transaction.atomic():
            current_db_designation_objects = employee_designation.objects.filter(user=user_obj)
            current_db_codes = set(current_db_designation_objects.values_list('designation', flat=True))
            new_desired_codes = set(designation_codes)
            codes_to_add = new_desired_codes - current_db_codes
            codes_to_remove = current_db_codes - new_desired_codes
            added_count = 0
            if codes_to_add:
                for code in codes_to_add:
                    employee_designation.objects.create(user=user_obj, designation=code)
                    added_count += 1
            removed_count = 0
            if codes_to_remove:
                employee_designation.objects.filter(user=user_obj, designation__in=list(codes_to_remove)).delete()
                removed_count += 1  # This counts the delete operation, not individual items
        return added_count, removed_count

        

    def __str__(self):
        return f"{self.user.username}'s Profile" if self.user else "No User Profile"

    #filter Employees based on department
    @classmethod
    def filter_employees_by_department(cls, department_obj):
        if department_obj:
            return cls.objects.filter(department=department_obj)
        return cls.objects.none()

     

    
class employee_designation(models.Model):
    designation_choices = [
        ('intern', 'Intern'),
        ('trainee', 'Trainee'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('teamlead', 'TeamLead'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('projectmanager', 'Project Manager'),
        ('qa', 'Quality Assurance'),
        ('hr', 'Human Resources'),
        ('admin', 'Admin'),
        ('ceo', 'CEO')
    ]
    user = models.ForeignKey(users, on_delete=models.CASCADE, related_name='designations')
    designation = models.CharField(max_length=50, choices=designation_choices)
    date_assigned = models.DateField(auto_now_add=True)
    # multiple designations can be added for a user



    def __str__(self):
        return f"{self.user.username} - {self.designation}"

class ChatMessage(models.Model):
    task = models.ForeignKey(tasks, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.task_name} - {self.user.username} - {self.message[:20]}..."

class read_status(models.Model):
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    task = models.ForeignKey(tasks, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'task') # Ensures one entry per user per task
        verbose_name_plural = "Task Read Statuses"
    

    @classmethod
    def check_unread_messages(cls, user):
        # This method needs to be restructured to work as a class method
        # It should iterate over tasks to check for unread messages for the given user.
        unread_tasks = []
        for task in tasks.objects.all():  # Or a filtered list of tasks relevant to the user
            last_read_status = cls.objects.filter(user=user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()

            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and latest_comment.user != user:
                    unread_tasks.append(task)
        
        return unread_tasks


    def __str__(self):
        return f"{self.user.username} last read {self.task.task_name} at {self.last_read_at.strftime('%Y-%m-%d %H:%M')}"

class Notification(models.Model):
    user = models.ForeignKey(users, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}... ({'Read' if self.is_read else 'Unread'})"

class TaskStatsService:
    @staticmethod
    def get_employee_monthly_stats(user, year, month):
        from .models import tasks, task_activity_log, settings
        from datetime import datetime, timedelta
        from django.utils import timezone
        # Calculate month boundaries
        start_of_month = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(days=1)
        else:
            end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(days=1)
        today = timezone.now().date()
        # Total working hours this month
        total_working_hours_this_month = timedelta()
        current_date = start_of_month.date()
        while current_date <= end_of_month.date():
            day_name = current_date.strftime('%A').lower()
            try:
                office_hours = settings.objects.get(day=day_name)
                start_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.start_time))
                end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                # Only count up to today for current month, but full month for previous months
                if (year == today.year and month == today.month and current_date == today):
                    current_time = timezone.now().time()
                    if current_time < office_hours.start_time:
                        break
                    elif current_time > office_hours.end_time:
                        end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                    else:
                        end_datetime = timezone.now()
                day_duration = end_datetime - start_datetime
                if office_hours.break_start_time and office_hours.break_end_time:
                    break_start = timezone.make_aware(datetime.combine(current_date, office_hours.break_start_time))
                    break_end = timezone.make_aware(datetime.combine(current_date, office_hours.break_end_time))
                    if (year == today.year and month == today.month and current_date == today):
                        current_time = timezone.now().time()
                        if current_time < office_hours.break_start_time:
                            break_duration = timedelta(0)
                        elif current_time > office_hours.break_end_time:
                            break_duration = break_end - break_start
                        else:
                            break_duration = timezone.now() - break_start
                    else:
                        break_duration = break_end - break_start
                    day_duration -= break_duration
                total_working_hours_this_month += day_duration
            except settings.DoesNotExist:
                pass
            # For current month, stop at today
            if (year == today.year and month == today.month and current_date == today):
                break
            current_date += timedelta(days=1)
        total_working_seconds = total_working_hours_this_month.total_seconds()
        working_hours = int(total_working_seconds // 3600)
        working_minutes = int((total_working_seconds % 3600) // 60)
        formatted_working_hours = f"{working_hours}h {working_minutes}m"
        total_working_hours_float = total_working_hours_this_month.total_seconds() / 3600
        # Tasks done this month
        tasks_done_this_month = tasks.objects.filter(
            assigned_to=user,
            status=2,
            submitted_on__gte=start_of_month,
            submitted_on__lte=end_of_month
        )
        tasks_done_this_month_count = tasks_done_this_month.count()
        # Total time spent this month
        total_time_this_month = task_activity_log.objects.filter(
            task__assigned_to=user,
            end_time__gte=start_of_month,
            end_time__lte=end_of_month,
            end_time__isnull=False
        ).aggregate(total_time=Sum('duration'))['total_time'] or timedelta(0)
        total_seconds = total_time_this_month.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        formatted_time = f"{hours}h {minutes}m {int(total_seconds % 60)}s"
        # Late submissions this month
        late_submissions_this_month = tasks_done_this_month.filter(due_date__lt=F('submitted_on')).count()
        # Tasks on time this month
        tasks_on_time_this_month = tasks_done_this_month.filter(due_date__gte=F('submitted_on')).count()
        # Total assigned tasks this month
        total_tasks_this_month = tasks.objects.filter(
            assigned_to=user,
            due_date__year=year,
            due_date__month=month
        ).count()
        # Efficiency calculation (same as admin)
        total_time_spent_float = total_time_this_month.total_seconds() / 3600
        on_time_ratio = tasks_on_time_this_month / tasks_done_this_month_count if tasks_done_this_month_count > 0 else 0
        late_penalty = late_submissions_this_month / tasks_done_this_month_count if tasks_done_this_month_count > 0 else 0
        time_efficiency = total_time_spent_float / total_working_hours_float if total_working_hours_float > 0 else 0
        task_completion_score = (tasks_done_this_month_count / total_tasks_this_month * 100) if total_tasks_this_month > 0 else 0
        efficiency = round(
            (task_completion_score * 0.4) +
            (time_efficiency * 100 * 0.3) +
            ((on_time_ratio * 100) * 0.3),
            2
        )
        efficiency = min(efficiency, 100)
        # Get tasks completed this month with related data
        completed_tasks = tasks_done_this_month.select_related('project').order_by('submitted_on')
        task_actual_hours = []
        task_expected_hours = []
        task_labels = []
        task_details = []
        for task in completed_tasks:
            actual_time = task_activity_log.objects.filter(task=task).aggregate(
                total=Sum('duration')
            )['total'] or timedelta()
            actual_hours = actual_time.total_seconds() / 3600
            expected_hours = 0
            if task.expected_time:
                expected_hours = task.expected_time.total_seconds() / 3600
            task_labels.append(f"{task.task_name[:20]}...")
            task_actual_hours.append(round(actual_hours, 1))
            task_expected_hours.append(round(expected_hours, 1))
            task_detail = {
                'name': task.task_name,
                'project': task.project.name if task.project else 'N/A',
                'actual_hours': round(actual_hours, 1),
                'expected_hours': round(expected_hours, 1),
                'completion_date': task.submitted_on.strftime('%Y-%m-%d %H:%M'),
                'time_difference': round(actual_hours - expected_hours, 1),
                'status': 'Over Time' if actual_hours > expected_hours else 'Under Time' if actual_hours < expected_hours else 'On Time'
            }
            task_details.append(task_detail)
        chart_data = {
            'labels': task_labels,
            'datasets': [
                {
                    'label': 'Actual Hours',
                    'data': task_actual_hours,
                    'borderColor': 'rgb(199, 135, 8)',
                    'tension': 0.1,
                    'fill': False,
                    'type': 'line'
                },
                {
                    'label': 'Expected Hours',
                    'data': task_expected_hours,
                    'borderColor': 'rgb(36, 135, 32)',
                    'tension': 0.1,
                    'fill': False,
                    'type': 'line'
                }
            ]
        }
        return {
            'tasks_done_this_month': tasks_done_this_month_count,
            'total_time_this_month': formatted_time,
            'late_submissions_this_month': late_submissions_this_month,
            'performance_statistics': efficiency,
            'tasks_on_time_this_month': tasks_on_time_this_month,
            'total_tasks_this_month': total_tasks_this_month,
            'chart_data': chart_data,
            'task_details': task_details,
            'current_month': f"{year:04d}-{month:02d}",
            'total_working_hours_this_month': total_working_hours_float,
        }

    @staticmethod
    def get_all_employees_monthly_stats(year, month):
        from datetime import datetime, timedelta
        from django.utils import timezone
        start_of_month = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(days=1)
        else:
            end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(days=1)
        employees = users.objects.filter(role__in=['employee', 'teamlead', 'project_manager', 'manager'], status=True)
        employee_stats = []
        for emp in employees:
            stats = TaskStatsService.get_employee_monthly_stats(emp, year, month)
            # Calculate total working hours in hours (float, rounded to 1 decimal)
            total_working_hours_this_month = round(stats.get('total_working_hours_this_month', 0.0), 1)
            # Calculate hours worked in hours (float, rounded to 1 decimal)
            total_time_this_month = stats.get('total_time_this_month', '0h 0m 0s')
            # Parse hours worked as float
            hours_worked_points = 0.0
            try:
                h, rest = total_time_this_month.split('h')
                h = float(h.strip())
                m, s = rest.split('m')
                m = float(m.strip())
                hours_worked_points = round(h + m/60, 1)
            except Exception:
                hours_worked_points = 0.0
            employee_stats.append({
                'name': f"{emp.first_name} {emp.last_name}" if emp.first_name else emp.username,
                'efficiency': stats['performance_statistics'],
                'hours_worked': stats['total_time_this_month'].split('h')[0],
                'hours_worked_points': hours_worked_points,
                'total_working_hours': total_working_hours_this_month,
                'tasks_completed': stats['tasks_done_this_month'],
                'total_assigned_tasks': stats['total_tasks_this_month'],
                'on_time_tasks': stats['tasks_on_time_this_month'],
                'late_tasks': stats['late_submissions_this_month']
            })
        return employee_stats 
    



    @classmethod
    def start_work(cls, task):
        # End any ongoing sessions for this task
        ongoing_sessions = cls.objects.filter(
            task=task,
            end_time__isnull=True
        )
        for session in ongoing_sessions:
            session.end_time = timezone.now()
            session.calculate_duration()
            session.save()

        # Create new session
        return cls.objects.create(task=task)
    


    @classmethod
    def stop_work(cls, task):
        logger = logging.getLogger(__name__)
        karachi_tz = pytz.timezone('Asia/Karachi')
        try:
            logger.info(f"Attempting to stop work for task: {task.task_name}")
            current_session = cls.objects.get(task=task, end_time__isnull=True)
            current_time = timezone.now().astimezone(karachi_tz)
            
            logger.info(f"Found active session. Current time: {current_time}")
            # If stopping outside office hours, set end time to last office hour
            if not settings.is_within_office_hours(current_time):
                day_name = current_time.strftime('%A').lower()
                try:
                    office_hours = settings.objects.get(day=day_name)
                    current_time = karachi_tz.localize(
                        timezone.datetime.combine(current_time.date(), office_hours.end_time)
                    )
                    logger.info(f"Adjusted end time to office hours end: {current_time}")
                except settings.DoesNotExist:
                    logger.warning(f"No office hours found for {day_name}")
            current_session.end_time = current_time
            logger.info(f"Set end_time to: {current_time}")
            # Calculate duration
            duration = current_session.calculate_duration()
            logger.info(f"Calculated duration: {duration}")
            # Force save to ensure duration is stored
            current_session.save(force_update=True)
            logger.info("Saved session with duration")
            return current_session
        except cls.DoesNotExist:
            logger.warning(f"No active session found for task: {task.task_name}")
            return None
        except Exception as e:
            logger.error(f"Error stopping work: {str(e)}")
            return None

    @staticmethod
    def get_agency_monthly_stats(year, month):
        from .models import users, tasks, task_activity_log, settings, projects
        from datetime import datetime, timedelta
        from django.utils import timezone
        start_of_month = timezone.make_aware(datetime(year, month, 1))
        if month == 12:
            end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(days=1)
        else:
            end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(days=1)
        employees = users.objects.filter(role__in=['employee', 'teamlead', 'project_manager', 'manager'], status=True)
        num_employees = employees.count()
        # Total working hours for the month (per employee)
        total_working_hours_month = timedelta()
        current_date = start_of_month.date()
        while current_date <= end_of_month.date():
            day_name = current_date.strftime('%A').lower()
            try:
                office_hours = settings.objects.get(day=day_name)
                start_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.start_time))
                end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                if current_date == timezone.now().date():
                    current_time = timezone.now().time()
                    if current_time < office_hours.start_time:
                        break
                    elif current_time > office_hours.end_time:
                        end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                    else:
                        end_datetime = timezone.now()
                day_duration = end_datetime - start_datetime
                if office_hours.break_start_time and office_hours.break_end_time:
                    break_start = timezone.make_aware(datetime.combine(current_date, office_hours.break_start_time))
                    break_end = timezone.make_aware(datetime.combine(current_date, office_hours.break_end_time))
                    if current_date == timezone.now().date():
                        current_time = timezone.now().time()
                        if current_time < office_hours.break_start_time:
                            break_duration = timedelta(0)
                        elif current_time > office_hours.break_end_time:
                            break_duration = break_end - break_start
                        else:
                            break_duration = timezone.now() - break_start
                    else:
                        break_duration = break_end - break_start
                    day_duration -= break_duration
                total_working_hours_month += day_duration
            except settings.DoesNotExist:
                pass
            current_date += timedelta(days=1)
        # Agency total working hours (all employees)
        per_employee_hours = total_working_hours_month.total_seconds() / 3600
        total_working_hours_agency = per_employee_hours * num_employees
        # Total hours worked (sum of all activity logs for completed tasks in month)
        completed_tasks = tasks.objects.filter(
            status=2,
            submitted_on__gte=start_of_month,
            submitted_on__lte=end_of_month
        )
        total_duration = timedelta()
        for task in completed_tasks:
            task_logs = task_activity_log.objects.filter(task=task)
            for log in task_logs:
                if log.duration:
                    total_duration += log.duration
        total_hours = total_duration.total_seconds() / 3600
        # Total tasks done
        tasks_done = completed_tasks.count()
        # Projects done (completed in this month)
        projects_done = projects.objects.filter(
            status=2,
            end_date__gte=start_of_month,
            end_date__lte=end_of_month
        ).count()
        return {
            'hours_worked': round(total_hours, 1),
            'total_working_hours': round(total_working_hours_agency, 1),
            'tasks_done': tasks_done,
            'projects_done': projects_done
        } 
    


