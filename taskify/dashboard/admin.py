from django.contrib import admin
from .models import Department, UserDepartment , Projects , Tasks , TaskActivityLog, OfficeHours , companyDetails, employeeProfile , ChatMessage, TaskReadStatus
from .models import Notification


# Register your models here.

@admin.register(UserDepartment)
class UserDepartment(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user_username', 'department_name')
    list_filter = ('department',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

#Projects
@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'start_date', 'end_date', 'status')
    search_fields = ('name', 'department__name')
    list_filter = ('status', 'department')

#Tasks
@admin.register(Tasks)
class Tasks(admin.ModelAdmin):
    list_display = ('task_name', 'project', 'assigned_to', 'status')
    search_fields = ('task_name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'task_name', 'assigned_to')

#time Tracking
@admin.register(TaskActivityLog)
class TaskActivityLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'start_time', 'end_time', 'duration')
    list_filter = ('task', 'start_time', 'end_time')
    

    def __str__(self):
        return f"{self.task} - {self.start_time} to {self.end_time}"
    


@admin.register(OfficeHours)
class OfficeHoursAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'is_working_day')
    list_editable = ('start_time', 'end_time', 'is_working_day')
    ordering = ['day']

@admin.register(companyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_phone', 'company_address')
    search_fields = ('company_name', 'company_email')
    list_filter = ('company_name',)
    
    def __str__(self):
        return self.company_name
    
@admin.register(employeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture', 'bio', 'address', 'date_of_birth')
    search_fields = ('user__username', 'bio', 'address')
    list_filter = ('user',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'message', 'timestamp')
    search_fields = ('task__task_name', 'user__username', 'message')
    list_filter = ('task', 'user', 'timestamp')

@admin.register(TaskReadStatus)
class TaskReadStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'last_read_at')
    list_filter = ('user', 'task')
    search_fields = ('user__username', 'task__task_name')
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'timestamp')