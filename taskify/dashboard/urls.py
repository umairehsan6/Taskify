from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin_statistics/', views.admindashboard_stats, name='admin_statistics'),
    path('users/', views.dashboard, name='dashboard'),  
    # path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('', views.new_employee_dashboard, name='new_employee_dashboard'),
    path('employee_statistics/' , views.employee_statistics, name='employee_statistics'),
    #department management
    path('add-department/', views.AddDepartments, name='add_department'),
    path('delete-department/<int:department_id>/', views.DeleteDepartment, name='delete_department'),
    path('assign-department/<int:user_id>/<int:department_id>/', views.AssignDepartment, name='assign_department'),
    #Projects management
    path('add-projects/', views.AddProjects, name='add-projects'),
    path('update-project-status/<int:project_id>/<str:new_status>/', views.UpdateProjectStatus, name='update-project-status'),
    path('all-projects/', views.AllProjects, name='all-projects'),
    path('get-project-tasks/<int:project_id>/', views.get_project_tasks, name='get-project-tasks'),
    path('check-project-unread/<int:project_id>/', views.check_project_unread, name='check-project-unread'),
    path('test-project-notification/<int:project_id>/', views.test_project_notification, name='test-project-notification'),
    #Tasks
    path('create-task/', views.CreateTask, name='create_task'),
    path('update-task-status/<int:task_id>/', views.UpdateTaskStatus, name='update_task_status'),
    path('start-task/<int:task_id>/', views.start_task, name='start_task'),
    path('complete-task/<int:task_id>/', views.UpdateTaskStatus, name='complete_task'),
    path('start-working/<int:task_id>/', views.start_working, name='start_working'),
    path('stop-working/<int:task_id>/', views.stop_working, name='stop_working'),
    path('delete-task/<int:project_id>/', views.DeleteTask, name='delete_task'),
    path('get-tasks/', views.GetTasks, name='get-tasks'),
    path('assigned-tasks/', views.AssignedTasks, name='assigned_tasks'),
    # path('assigned-tasks-team/', views.AssignedTasksTeam, name='assigned_tasks_team'),
    path('upload_task_file/<int:task_id>/', views.upload_task_file, name='upload_task_file'),
    path('upload_task_report/<int:task_id>/', views.upload_task_report, name='upload_task_report'),
    path('download_task_file/<int:task_id>/', views.download_task_file, name='download_task_file'),
    path('approve-task/<int:task_id>/', views.approve_task, name='approve_task'),
    # Task Time Tracking
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/settings/add/', views.add_office_hours, name='add_office_hours'),
    path('dashboard/settings/edit/', views.edit_office_hours, name='edit_office_hours'),
    path('dashboard/settings/delete/', views.delete_office_hours, name='delete_office_hours'),
    path('dashboard/settings/start-tracking/', views.start_tracking, name='start_tracking'),
    path('about-company/', views.about_company, name='about_company'),
    path('employee/company-profile/', views.employee_company_profile, name='employee_company_profile'),
    path('employee_profile/', views.employee_profile, name='employee_profile'),
    # get task comments
    path('get-task-comments/<int:task_id>/', views.get_task_comments, name='get-task-comments'),
    # path('add-task-comment/', views.add_task_comment, name='add-task-comment'),
    # path('check-unread-messages/<int:task_id>/', views.check_unread_messages, name='check-unread-messages'),

    path('pending-tasks/' , views.pending_tasks_json , name ='pending-tasks'),
    path('pending-tasks-json/', views.pending_tasks_json, name='pending-tasks-json'),
    path('approval-pending-tasks-json/', views.approval_pending_tasks_json, name='approval-pending-tasks-json'),
    path('ongoing-tasks/', views.ongoing_tasks_json, name='ongoing_tasks_json'),
    path('ongoing-tasks-json/', views.ongoing_tasks_json, name='ongoing-tasks-json'),
    path('get-task-report/<int:task_id>/', views.get_task_report, name='get_task_report'),
    path('get-task-file/<int:task_id>/', views.get_task_file, name='get_task_file'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
