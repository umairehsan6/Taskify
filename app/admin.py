from django.contrib import admin

# Register your models here.
from .models import users , department , employee_designation, projects , tasks , task_activity_log , settings , companyDetails , employee_details , ChatMessage , read_status , Notification

class usersAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'email', 'role', 'get_department')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    
    def get_department(self, obj):
        try:
            return obj.employee_details.department.name if obj.employee_details.department else 'No Department'
        except:
            return 'No Department'
    get_department.short_description = 'Department'
admin.site.register(users, usersAdmin)


@admin.register(department)
class departmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

#projects
@admin.register(projects)
class projectsAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'start_date', 'end_date', 'status')
    search_fields = ('name', 'department__name')
    list_filter = ('status', 'department')

#Tasks
@admin.register(tasks)
class tasksAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'project', 'assigned_to', 'status')
    search_fields = ('task_name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'task_name', 'assigned_to')

#time Tracking
@admin.register(task_activity_log)
class task_activity_logAdmin(admin.ModelAdmin):
    list_display = ('task', 'start_time', 'end_time', 'duration')
    list_filter = ('task', 'start_time', 'end_time')
    

    def __str__(self):
        return f"{self.task} - {self.start_time} to {self.end_time}"
    


@admin.register(settings)
class settingsAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time')
    list_editable = ('start_time', 'end_time')
    ordering = ['day']

@admin.register(companyDetails)
class CompanyDetailsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_email', 'company_phone', 'company_address')
    search_fields = ('company_name', 'company_email')
    list_filter = ('company_name',)
    
    def __str__(self):
        return self.company_name
    
@admin.register(employee_details)
class employee_detailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'profile_picture', 'bio', 'address', 'date_of_birth')
    search_fields = ('user__username', 'bio', 'address', 'department__name')
    list_filter = ('user', 'department')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'message', 'timestamp')
    search_fields = ('task__task_name', 'user__username', 'message')
    list_filter = ('task', 'user', 'timestamp')

@admin.register(read_status)
class read_statusAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'last_read_at')
    list_filter = ('user', 'task')
    search_fields = ('user__username', 'task__task_name')
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'timestamp')

@admin.register(employee_designation)
class employee_designationAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'date_assigned')
    search_fields = ('user__username', 'designation')
    list_filter = ('designation', 'date_assigned')

    def __str__(self):
        return f"{self.user.username} - {self.designation}"