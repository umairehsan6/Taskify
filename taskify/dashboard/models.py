from django.db import models
from django.db.models import Sum
from django.utils import timezone
import logging

# Create your models here.
from users.models import SignupUser

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserDepartment(models.Model):
    user = models.ForeignKey(SignupUser, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.user is None:
            return f"No User - {self.department.name if self.department else 'No Department'}"
        return f"{self.user.username} - {self.department.name if self.department else 'No Department'}"
    
    #Projects
class Projects(models.Model):
    Status_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, choices=Status_CHOICES, default='pending')


    def __str__(self):
        return self.name
    
#Tasks  
class Tasks(models.Model):
    taks_status = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
        ('not_assigned', 'Not Assigned'),
    ]
    task_priorty = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    project = models.ForeignKey(Projects, on_delete=models.SET_NULL, null=True, blank=True , related_name='tasks')
    assigned_to = models.ForeignKey(UserDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_from = models.ForeignKey(SignupUser, on_delete=models.SET_NULL, null=True, blank=True)
    task_name = models.CharField(max_length=50)
    task_description = models.TextField()  # Field name is `task_description`
    due_date = models.DateField(default=None, blank=True, null=True)
    # expected time to complete the task
    expected_time = models.DurationField(null=True, blank=True)  # Duration field for expected time
    priority = models.CharField(max_length=10, choices=task_priorty, default='medium')
    status = models.CharField(max_length=50, choices=taks_status, default='pending')
    task_file = models.FileField(upload_to='task_files/', null=True, blank=True)
    report = models.CharField(max_length=1000, null=True, blank=True)
    submitted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task_name} - {self.project.name} - {self.assigned_to.user.username}"

    def get_total_time_spent(self):
        total_duration = TaskActivityLog.objects.filter(task=self).aggregate(
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

class TaskActivityLog(models.Model):
    task = models.ForeignKey('dashboard.Tasks', on_delete=models.CASCADE, related_name='activity_logs')
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
        
        try:
            logger.info(f"Attempting to stop work for task: {task.task_name}")
            current_session = cls.objects.get(task=task, end_time__isnull=True)
            current_time = timezone.now()
            logger.info(f"Found active session. Current time: {current_time}")
            
            # If stopping outside office hours, set end time to last office hour
            if not OfficeHours.is_within_office_hours(current_time):
                day_name = current_time.strftime('%A').lower()
                try:
                    office_hours = OfficeHours.objects.get(day=day_name, is_working_day=True)
                    current_time = timezone.make_aware(
                        timezone.datetime.combine(current_time.date(), office_hours.end_time)
                    )
                    logger.info(f"Adjusted end time to office hours end: {current_time}")
                except OfficeHours.DoesNotExist:
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

class OfficeHours(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)
    is_working_day = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day']

    def __str__(self):
        return f"{self.get_day_display()} ({self.start_time} - {self.end_time})"
    
    @classmethod
    def is_within_office_hours(cls, datetime_obj):
        #Check if a given datetime is within office hours
        day_name = datetime_obj.strftime('%A').lower()
        try:
            office_hours = cls.objects.get(day=day_name, is_working_day=True)
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

    def __str__(self):
        return self.company_name if self.company_name else "Company Details"
    

class employeeProfile(models.Model):
    user = models.ForeignKey(SignupUser, on_delete=models.CASCADE, related_name='employee_details')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile" if self.user else "No User Profile"

class ChatMessage(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(SignupUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.task_name} - {self.user.username} - {self.message[:20]}..."

class TaskReadStatus(models.Model):
    user = models.ForeignKey(SignupUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'task') # Ensures one entry per user per task
        verbose_name_plural = "Task Read Statuses"

    def __str__(self):
        return f"{self.user.username} last read {self.task.task_name} at {self.last_read_at.strftime('%Y-%m-%d %H:%M')}"

class Notification(models.Model):
    user = models.ForeignKey(SignupUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}... ({'Read' if self.is_read else 'Unread'})"
