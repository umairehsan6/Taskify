from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import redirect
from .models import Department, UserDepartment , Projects , Tasks , OfficeHours , employeeProfile
from users.models import SignupUser
from django.http import JsonResponse, Http404, FileResponse
import os
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Tasks, TaskActivityLog
from django.db.models import Sum, Q, F
from datetime import datetime, timedelta
import logging
from .tasks import check_office_hours
from .models import companyDetails
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatMessage, TaskReadStatus
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
logger = logging.getLogger(__name__)
# Create your views here.
def AddDepartments(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  
        user_role = request.session.get('user_role', 'employee')
        if request.method == 'POST':
            department_name = request.POST.get('department_name')
            if Department.objects.filter(name=department_name).exists():
                messages.error(request, "This department already exists.")
            else:
                Department.objects.create(name=department_name)
                messages.success(request, f"Department {department_name} has been added successfully.")

        
        departments = Department.objects.all()

        return render(request, 'admin-dashboard/dashboard-departments.html', {
            'departments': departments, 
            'user_role': user_role,
            'active_page': 'departments',
        })
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')


def DeleteDepartment(request, department_id):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  # Use 'user_role'
        try:
            department = Department.objects.get(id=department_id)
            department.delete()
            messages.success(request, f"Department {department.name} has been deleted successfully.")
        except Department.DoesNotExist:
            messages.error(request, "Department does not exist.")
    else:
        messages.error(request, "You do not have permission to perform this action.")
    return redirect('add_department')  # Redirect to the same page or any other page as needed

def AssignDepartment(request, user_id, department_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        try:
            user = SignupUser.objects.get(id=user_id)
            department = Department.objects.get(id=department_id)
            user_department, created = UserDepartment.objects.get_or_create(user=user)
            user_department.department = department
            user_department.save()
            if is_ajax:
                return JsonResponse({'success': True, 'new_department': department.name})
            if created:
                messages.success(request, f"{user.username} was newly linked to department {department.name}.")
            else:
                messages.success(request, f"{user.username}'s department was updated to {department.name}.")
        except SignupUser.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'User does not exist.'}, status=404)
            messages.error(request, "User does not exist.")
        except Department.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Department does not exist.'}, status=404)
            messages.error(request, "Department does not exist.")
        return redirect('dashboard')
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'You do not have permission to perform this action.'}, status=403)
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')
    

    #Projects
    #Projects
def AddProjects(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  # Use 'user_role'
        user_role = request.session.get('user_role', 'employee')
        if request.method == 'POST':
            project_name = request.POST.get('project_name')
            description = request.POST.get('description')
            department_id = request.POST.get('department')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = 'pending'

            if Projects.objects.filter(name=project_name).exists():
                messages.error(request, "This project already exists.")
            else:
                department = Department.objects.get(id=department_id)
                Projects.objects.create(
                    name=project_name,
                    description=description,
                    department=department,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                )
                messages.success(request, f"Project {project_name} has been assigned to {department.name} team successfully.")
            return redirect('add-projects')
        else:
            departments = Department.objects.all()
            return render(request, 'admin-dashboard/dashboard-addprojects.html', {
                'departments': departments,
                'user_role': user_role,
                'active_page': 'new_project'
            })
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')
    
def AllProjects(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager', 'project_manager']:
        projects = Projects.objects.select_related('department').all()
        task_priorities = Tasks.task_priorty
        all_employees = UserDepartment.objects.select_related('user', 'department').all()
        user_role = request.session.get('user_role', 'employee')

        selected_project = None
        filtered_employees = None
        assign_project_id = request.GET.get('assign')
        if assign_project_id:
            try:
                selected_project = Projects.objects.get(id=assign_project_id)
                filtered_employees = all_employees.filter(department=selected_project.department)
            except Projects.DoesNotExist:
                selected_project = None
                filtered_employees = None

        return render(request, 'admin-dashboard/dashboard-allprojects.html', {
            'projects': projects,
            'active_page': 'all_projects',
            'task_priorities': task_priorities,
            'all_employees': all_employees,
            'selected_project': selected_project,
            'filtered_employees': filtered_employees,
            'user_role': user_role,
        })
    else:
        return redirect('login')
    
def UpdateProjectStatus(request, project_id, new_status):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    try:
        project = Projects.objects.get(id=project_id)
        project.status = new_status
        project.save()
        msg = f"Project status updated to {project.get_status_display()}."
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg, 'new_status': project.get_status_display()})
        messages.success(request, msg)
    except Projects.DoesNotExist:
        error_msg = "Project does not exist."
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg}, status=404)
        messages.error(request, error_msg)

    user_role = request.session.get('user_role')
    if user_role == 'admin':
        return redirect('all-projects')  # admin dashboard
    elif user_role in ['employee', 'project_manager', 'teamlead']:
        return redirect('new_employee_dashboard')  # employee/pm/teamlead dashboard
    else:
        return redirect('login')
    
##Tasks
def CreateTask(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        assigned_to_id = request.POST.get('assigned_to')
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        due_date = request.POST.get('duedate')
        priority = request.POST.get('priority')
        user_role = request.session.get('user_role')
        
        # Get hours and minutes from form data instead of session
        hours = int(request.POST.get('expected_time_hours', 0))
        minutes = int(request.POST.get('expected_time_minutes', 0))
        
        #summing hours and minutes
        expected_time = timedelta(hours=hours, minutes=minutes)

        try:
            project = Projects.objects.get(id=project_id)
            
            # Handle user_department lookup based on role
            if user_role == 'employee':
                # For employees, use their own user_department
                user_department = UserDepartment.objects.get(user_id=request.session['user_id'])
            else:
                # For team leads/project managers, use the selected employee's user_department
                if not assigned_to_id:
                    messages.error(request, "Please select an employee to assign the task to.")
                    return redirect('new_employee_dashboard')
                user_department = UserDepartment.objects.get(id=assigned_to_id)
            
            assigned_from_user = SignupUser.objects.get(id=request.session['user_id'])
            
            # Set initial status based on user role
            status = 'not_assigned' if user_role == 'employee' else 'pending'
            
            # Create the task
            Tasks.objects.create(
                project=project,
                assigned_to=user_department,
                task_name=task_name,
                task_description=task_description,
                due_date=due_date,
                priority=priority,
                status=status,
                assigned_from=assigned_from_user,
                expected_time=expected_time
                
            )
            messages.success(request, "Task successfully created.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Task created successfully!'})
            else:
                return redirect('new_employee_dashboard')
        except Projects.DoesNotExist:
            messages.error(request, "Project does not exist.")
        except UserDepartment.DoesNotExist:
            messages.error(request, "The selected user does not belong to the project's department.")
        except Exception as e:
            messages.error(request, f"Error creating task: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

        # Redirect based on user role
        if user_role == 'admin':
            return redirect('all-projects')
        elif user_role in ['project_manager', 'teamlead']:
            return redirect('new_employee_dashboard')
        elif user_role == 'employee':
            return redirect('new_employee_dashboard')
        else:
            return redirect('login')
        
def AssignedTasks(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin']:
        projects = Projects.objects.filter(status='ongoing')
        user_role = request.session.get('user_role', 'employee')
        
        # Get all tasks for ongoing projects
        tasks = Tasks.objects.filter(project__in=projects).select_related(
            'project', 'assigned_to__user', 'assigned_from'
        )
        
        if request.session['user_role'] == 'admin':
            return render(request, 'admin-dashboard/dashboard-tasks.html', {
                'projects': projects,
                'tasks': tasks,  # Add tasks to context
                'user_role': user_role,
                'active_page': 'assigned_tasks'
            })
    else:
        return redirect('login')
    
# def AssignedTasksTeam(request):
#     if 'user_role' in request.session and request.session['user_role'] in ['project_manager', 'teamlead']:
#         user_id = request.session['user_id']
#         user_role = request.session.get('user_role', 'employee')
#         user_departments = UserDepartment.objects.filter(user_id=user_id)

#         # Extract actual Department objects (or their IDs)
#         departments = user_departments.values_list('department', flat=True)

#         # Now query Projects with those department IDs
#         projects = Projects.objects.filter(
#             department__in=departments,
#             status='ongoing'  # Only show ongoing projects
#         )
        
#         # Get all tasks for these projects
#         tasks = Tasks.objects.filter(
#             project__in=projects
#         ).select_related(
#             'project',
#             'assigned_to__user',
#             'assigned_from'
#         )

#         return render(request, 'employee-dashboard/dashboard-emptasks.html', {
#             'projects': projects,
#             'tasks': tasks,  # Add tasks to context
#             'user_role': user_role,
#             'active_page': 'assigned_tasks_team'
#         })
#     else:
#         messages.error(request, "You do not have permission to access this page.")
#         return redirect('login')

    
def UpdateTaskStatus(request, task_id):
    if request.method == 'POST':
        try:
            task = Tasks.objects.get(id=task_id)
            new_status = request.POST.get('status') or 'completed'
            task.status = new_status
            if new_status == 'completed':
                task.submitted_on = timezone.now()
            task.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, f"Task status updated to {task.get_status_display()}.")
        except Tasks.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Task does not exist.'}, status=404)
            messages.error(request, "Task does not exist.")
    return redirect('new_employee_dashboard')

def hold_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Tasks.objects.get(id=task_id)
            user_department = UserDepartment.objects.get(user_id=request.session['user_id'])

            if task.status == 'pending':
                task.status = 'on_hold'
                task.save()
                messages.success(request, "Task has been put on hold.")
            elif task.status == 'in_progress': # Keep the existing logic for stopping work
                 task.status = 'on_hold'
                 task.save()
                 messages.success(request, "Task has been put on hold (stopped working).")
            else:
                messages.error(request, f"Task cannot be put on hold from status: {task.get_status_display()}.")


        except Tasks.DoesNotExist:
            messages.error(request, "Task does not exist.")
        except UserDepartment.DoesNotExist:
            messages.error(request, "User department not found.")
    return redirect('new_employee_dashboard')

def start_working(request, task_id):
    if request.method == 'POST':
        try:
            task = Tasks.objects.get(id=task_id)
            user_department = UserDepartment.objects.get(user_id=request.session['user_id'])

            if task.status == 'on_hold':
                # Put any other active tasks for this user on hold
                active_tasks = Tasks.objects.filter(
                    assigned_to=user_department,
                    status='in_progress'
                ).exclude(id=task_id)

                for active_task in active_tasks:
                    active_task.status = 'on_hold'
                    active_task.save()
                    # End any ongoing time tracking for other tasks and calculate duration
                    ongoing_sessions = TaskActivityLog.objects.filter(
                        task=active_task,
                        end_time__isnull=True
                    )
                    for session in ongoing_sessions:
                        session.end_time = timezone.now()
                        session.duration = session.end_time - session.start_time
                        session.save()

                # Set the current task to in_progress
                task.status = 'in_progress'
                task.save()
                # Start new time tracking session using the start_work method
                session = TaskActivityLog.start_work(task)
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                if session:
                    messages.success(request, f"Task status updated to {task.get_status_display()} (started working).")
                else:
                    messages.warning(request, f"Task marked as in progress, but time tracking will start when office hours begin.")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': f'Task cannot be started from status: {task.get_status_display()}.'}, status=400)
                messages.error(request, f"Task cannot be started from status: {task.get_status_display()}.")
        except Tasks.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Task does not exist.'}, status=404)
            messages.error(request, "Task does not exist.")
        except UserDepartment.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'User department not found.'}, status=404)
            messages.error(request, "User department not found.")
    return redirect('new_employee_dashboard')

def stop_working(request, task_id):
    if request.method == 'POST':
        try:
            task = Tasks.objects.get(id=task_id)
            user_department = UserDepartment.objects.get(user_id=request.session['user_id'])

            if task.status == 'in_progress':
                task.status = 'on_hold'
                task.save()
                # End time tracking session
                current_session = TaskActivityLog.objects.filter(
                    task=task,
                    end_time__isnull=True
                ).first()
                if current_session:
                    current_session.end_time = timezone.now()
                    current_session.duration = current_session.end_time - current_session.start_time
                    current_session.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, f"Task status updated to {task.get_status_display()} (stopped working). Time spent: {current_session.duration if current_session else ''}")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': f'Task cannot be stopped from status: {task.get_status_display()}.'}, status=400)
                messages.error(request, f"Task cannot be stopped from status: {task.get_status_display()}.")
        except Tasks.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Task does not exist.'}, status=404)
            messages.error(request, "Task does not exist.")
        except UserDepartment.DoesNotExist:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'User department not found.'}, status=404)
            messages.error(request, "User department not found.")
    return redirect('new_employee_dashboard')

def DeleteTask(request, project_id):
    task_id = request.GET.get('task_id') or request.POST.get('task_id')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if task_id:
        try:
            task = Tasks.objects.get(id=task_id)
            task.delete()
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Task deleted successfully.'})
            messages.success(request, "Task deleted successfully.")
        except Tasks.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Task does not exist.'}, status=404)
            messages.error(request, "Task does not exist.")
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'No task ID provided.'}, status=400)
        messages.error(request, "No task ID provided.")

    # Redirect based on user role
    if request.session['user_role'] == 'admin':
        return redirect('assigned_tasks')
    elif request.session['user_role'] in ['project_manager', 'teamlead']:
        return redirect('new_employee_dashboard')  # Redirect back to the team tasks page
    else:
        return redirect('new_employee_dashboard')

def GetTasks(request):
    project_id = request.GET.get('project_id')
    if project_id:
        try:
            project = Projects.objects.get(id=project_id)
            tasks = Tasks.objects.filter(project=project).select_related(
                'project',
                'assigned_to__user',
                'assigned_from'
            )
            tasks_data = [
                {
                    'id': task.id,
                    'task_name': task.task_name,
                    'project': {
                        'id': task.project.id,
                        'name': task.project.name
                    },
                    'assigned_to': f"{task.assigned_to.user.first_name} {task.assigned_to.user.last_name}" if task.assigned_to.user.first_name else task.assigned_to.user.username,
                    'assigned_from': f"{task.assigned_from.first_name} {task.assigned_from.last_name}" if task.assigned_from and task.assigned_from.first_name else (task.assigned_from.username if task.assigned_from else 'N/A'),
                    'priority': task.get_priority_display(),
                    'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                    'status': task.status,
                    'status_display': task.get_status_display(),
                    'time_spent': task.get_total_time_spent(),
                    'file_url': f"/dashboard/download_task_file/{task.id}/" if task.task_file else None,
                    'file_name': task.task_file.name.split('/')[-1] if task.task_file else '',
                    'report': task.report or ''
                }
                for task in tasks
            ]
            return JsonResponse({'tasks': tasks_data})
        except Projects.DoesNotExist:
            return JsonResponse({'tasks': []})
    return JsonResponse({'tasks': []})

def upload_task_file(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Tasks, id=task_id)
            uploaded_file = request.FILES.get('myfile')
            if uploaded_file:
                task.task_file = uploaded_file
                task.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'file_url': task.task_file.url,
                        'file_name': task.task_file.name.split('/')[-1]
                    })
                messages.success(request, "File uploaded successfully.")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'No file selected.'}, status=400)
                messages.error(request, "No file selected.")
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=500)
            messages.error(request, f"Error uploading file: {str(e)}")
    return redirect('new_employee_dashboard')

def upload_task_report(request, task_id):
    if request.method == 'POST':
        try:
            task = get_object_or_404(Tasks, id=task_id)
            report_text = request.POST.get('report')
            if report_text:
                task.report = report_text
                task.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Report submitted successfully.'
                    })
                messages.success(request, "Report submitted successfully.")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Report text is required.'
                    }, status=400)
                messages.error(request, "Report text is required.")
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
            messages.error(request, f"Error submitting report: {str(e)}")
    return redirect('new_employee_dashboard')

def download_task_file(request, task_id):
    try:
        task = get_object_or_404(Tasks, id=task_id)
        if task.task_file:
            file_path = task.task_file.path
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        raise Http404("File not found")
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('new_employee_dashboard')

def approve_task(request, task_id):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            task = Tasks.objects.get(id=task_id)
            if task.status == 'not_assigned':
                task.status = 'pending'
                task.save()
                if is_ajax:
                    return JsonResponse({'success': True})
                messages.success(request, "Task has been approved and is now pending.")
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'This task cannot be approved.'}, status=400)
                messages.error(request, "This task cannot be approved.")
        except Tasks.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Task does not exist.'}, status=404)
            messages.error(request, "Task does not exist.")
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Unknown error.'}, status=500)
    if request.session['user_role'] == 'admin':
        return redirect('assigned_tasks')
    elif request.session['user_role'] in ['project_manager', 'teamlead']:
        return redirect('new_employee_dashboard')
    else:
        return redirect('login')
    
#Time Tracking
def dashboard_settings(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        office_hours = OfficeHours.objects.all().order_by('day')
        days_of_week = OfficeHours.DAYS_OF_WEEK
        user_role = request.session.get('user_role')
        
        context = {
            'office_hours': office_hours,
            'days_of_week': days_of_week,
            'active_page': 'settings',
            'user_role': user_role,
        }
        return render(request, 'admin-dashboard/dashboard-settings.html', context)
    else:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('login')


def add_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            break_start_time = request.POST.get('break_start_time')
            break_end_time = request.POST.get('break_end_time')
            is_working_day = request.POST.get('is_working_day') == 'on'
            
            try:
                OfficeHours.objects.create(
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                    break_start_time=break_start_time if break_start_time else None,
                    break_end_time=break_end_time if break_end_time else None,
                    is_working_day=is_working_day
                )
                messages.success(request, f"Office hours for {day} have been added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding office hours: {str(e)}")
        
        return redirect('dashboard_settings')
    else:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('login')


def edit_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            day = request.POST.get('day')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            break_start_time = request.POST.get('break_start_time')
            break_end_time = request.POST.get('break_end_time')
            is_working_day = request.POST.get('is_working_day') == 'on'
            
            try:
                office_hours = OfficeHours.objects.get(day=day)
                office_hours.start_time = start_time
                office_hours.end_time = end_time
                office_hours.break_start_time = break_start_time if break_start_time else None
                office_hours.break_end_time = break_end_time if break_end_time else None
                office_hours.is_working_day = is_working_day
                office_hours.save()
                messages.success(request, f"Office hours for {day} have been updated successfully.")
            except OfficeHours.DoesNotExist:
                messages.error(request, f"Office hours for {day} not found.")
            except Exception as e:
                messages.error(request, f"Error updating office hours: {str(e)}")
        
        return redirect('dashboard_settings')
    else:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('login')

def delete_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            day = request.POST.get('day')
            try:
                office_hours = OfficeHours.objects.get(day=day)
                office_hours.delete()
                messages.success(request, f"Office hours for {day} have been deleted successfully.")
            except OfficeHours.DoesNotExist:
                messages.error(request, f"Office hours for {day} not found.")
            except Exception as e:
                messages.error(request, f"Error deleting office hours: {str(e)}")
        
        return redirect('dashboard_settings')
    else:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('login')

def start_tracking(request):
    """
    View to start the office hours tracking system
    Only accessible by admin users
    """
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        # Run the check immediately
        check_office_hours()
        
        messages.success(request, "Office hours tracking system started successfully.")
        return redirect('dashboard_settings')
    else:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('login')

def get_user_total_time_today(user_department):
    now = timezone.localtime(timezone.now())
    today = now.date()
    start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    
    utc_start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    utc_end_of_today = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    completed_logs_ending_today = TaskActivityLog.objects.filter(
        task__assigned_to=user_department,
        end_time__gte=utc_start_of_today,
        end_time__lte=utc_end_of_today,
        end_time__isnull=False
    )
        
    completed_duration_sum = completed_logs_ending_today.aggregate(
        total=Sum('duration')
    )['total'] or timedelta(0)
    
    total_duration_today = completed_duration_sum

    ongoing_tasks = TaskActivityLog.objects.filter(
        task__assigned_to=user_department,
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


#Dasboard home pages
# Create your views here.
def dashboard(request):
        users = SignupUser.objects.all()
        departments = Department.objects.all()
        user_role = request.session.get('user_role', 'employee')
        roles_with_access = ['admin', 'manager']
        if 'user_role' in request.session and request.session['user_role'] in roles_with_access:
            return render(request, 'admin-dashboard/dashboard.html', 
                          {
                            'users': users,
                            'departments': departments,
                            'user_role': user_role,
                            'roles_with_access': roles_with_access,
                            'active_page': 'dashboard',
                            'roles': SignupUser.ROLE_CHOICES,
                                         })
        else:
            return redirect('login')
        
def new_employee_dashboard(request):
    
    if 'user_id' not in request.session:
        return redirect('login')
    
    signup_user = SignupUser.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')
    username = signup_user.first_name or signup_user.username
    roles_with_access = ['project_manager', 'teamlead']
    statuses_to_show = ['pending', 'on_hold', 'ongoing']
    user_departments = Department.objects.filter(userdepartment__user=signup_user)
    projects = Projects.objects.filter(department__in=user_departments)
    task_priorities = Tasks.task_priorty
    
    # Get user's department for time tracking
    user_department = UserDepartment.objects.filter(user=signup_user).first()
    total_time_today = get_user_total_time_today(user_department)

    # Get employee's assigned tasks
    tasks = Tasks.objects.filter(assigned_to__user=signup_user)
    #Filtered Employees
    filtered_employees = None
    if user_role in ['project_manager', 'teamlead']:
        # For team leads and project managers, get all employees in their departments
        filtered_employees = UserDepartment.objects.filter(
            department__in=user_departments
        ).select_related('user', 'department')
    else:
        # For regular employees, just include themselves
        filtered_employees = UserDepartment.objects.filter(
            user=signup_user
        ).select_related('user', 'department')
    
    # For team leads and project managers, get additional department tasks
    department_tasks = None
    if user_role in ['teamlead', 'project_manager']:
        department_tasks = Tasks.objects.filter(
            project__department__in=user_departments
        ).select_related('project', 'assigned_to__user')
    
    for task in tasks:
        if task.task_file:
            task.file_url = task.task_file.url
            task.file_name = task.task_file.name.split('/')[-1]
        
        # Check for unread messages
        task.has_unread_messages = False
        last_read_status = TaskReadStatus.objects.filter(user=signup_user, task=task).first()
        latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()

        if latest_comment:
            # A message is unread if: 
            # 1. There is no last_read_status for this user/task, OR
            # 2. The latest comment is newer than the last_read_at timestamp, AND
            # 3. The latest comment was NOT sent by the current user.
            if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
               latest_comment.user != signup_user:
                task.has_unread_messages = True
                logger.info(f"Task {task.id} ({task.task_name}) has unread messages for user {signup_user.id}")
            else:
                logger.debug(f"Task {task.id} ({task.task_name}) has no unread messages for user {signup_user.id}")
        else:
            logger.debug(f"Task {task.id} ({task.task_name}) has no messages")
    
    if department_tasks:
        for task in department_tasks:
            if task.task_file:
                task.file_url = task.task_file.url
                task.file_name = task.task_file.name.split('/')[-1]
            
            # Check for unread messages for department tasks as well
            task.has_unread_messages = False
            last_read_status = TaskReadStatus.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()

            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    task.has_unread_messages = True
                    logger.info(f"Task {task.id} ({task.task_name}) has unread messages for user {signup_user.id}")
                else:
                    logger.debug(f"Task {task.id} ({task.task_name}) has no unread messages for user {signup_user.id}")
            else:
                logger.debug(f"Task {task.id} ({task.task_name}) has no messages")
    
    for project in projects:
        project.has_tasks_assigned = Tasks.objects.filter(project=project, assigned_to__user=signup_user).exists()
        
        # Check if any tasks in this project have unread messages
        project.has_unread_messages = False
        project_tasks = Tasks.objects.filter(project=project)
        for task in project_tasks:
            last_read_status = TaskReadStatus.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
            
            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    project.has_unread_messages = True
                    logger.info(f"Project {project.id} ({project.name}) has unread messages for user {signup_user.id}")
                    break  # No need to check other tasks if we found unread messages
    
    #tasks expiring today 
    today = timezone.now().date()
    tasks_expiring_today = Tasks.objects.filter(
        due_date=today,
        assigned_to__user=signup_user
    ).exclude(status='completed').count()

    #Expired tasks
    expired_tasks = Tasks.objects.filter(
        due_date__lt=today,
        assigned_to__user=signup_user
    ).exclude(status='completed').count()
    
    #Tasks done today - using timezone-aware comparison
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    
    tasks_done_today = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_day,
        submitted_on__lte=end_of_day
    ).count()
    
    # Get or create employee profile
    profile, created = employeeProfile.objects.get_or_create(user=signup_user)
    
    has_permission = user_role in roles_with_access
    user_type = 'signup_user'

    # Fetch chat messages for the selected task
    task_id = request.GET.get('task_id')
    chat_messages = []
    if task_id:
        chat_messages = ChatMessage.objects.filter(task_id=task_id).order_by('-timestamp')

    context = {
        'user_type': user_type,
        'username': username,
        'user_role': user_role,
        'roles_with_access': roles_with_access,
        'statuses_to_show': statuses_to_show,
        'projects': projects,
        'tasks': tasks,
        'department_tasks': department_tasks,
        'has_permission': has_permission,
        'active_page': 'new_employee_dashboard',
        'task_priorities': task_priorities,
        'total_time_today': total_time_today,
        'user_department': user_department,
        'filtered_employees': filtered_employees,
        'tasks_expiring_today': tasks_expiring_today,
        'expired_tasks': expired_tasks,
        'tasks_done_today': tasks_done_today,
        'profile': profile,  # Add profile to context
        'chat_messages': chat_messages,  # Add chat messages to context
    }
    
    return render(request, 'employee-dashboard/emp-dash1.html', context)

def employee_statistics(request):
    if 'user_id' not in request.session:
        return redirect('login')

    signup_user = SignupUser.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')
    username = signup_user.first_name or signup_user.username

    # Get user's department
    user_department = UserDepartment.objects.filter(user=signup_user).first()

    # Tasks Done This Week
    now = timezone.now()
    start_of_week = now - timezone.timedelta(days=now.weekday())
    start_of_week = timezone.make_aware(datetime.combine(start_of_week.date(), datetime.min.time()))
    end_of_week = start_of_week + timezone.timedelta(days=6)
    
    tasks_done_this_week = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_week,
        submitted_on__lte=end_of_week
    ).count()

    # Total Time Spent This Week
    total_time_this_week = TaskActivityLog.objects.filter(
        task__assigned_to=user_department,
        end_time__gte=start_of_week,
        end_time__lte=end_of_week,
        end_time__isnull=False
    ).aggregate(total_time=Sum('duration'))['total_time'] or timedelta(0)

    # Format the total time
    total_seconds = total_time_this_week.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    formatted_time = f"{hours}h {minutes}m {int(total_seconds % 60)}s"

    # Late this week Submissions
    late_submissions = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_week,
        submitted_on__lte=end_of_week
    ).filter(
        due_date__lt=now
    ).count()

    # tasks on time this week
    tasks_on_time_this_week = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_week,
        submitted_on__lte=end_of_week
    ).filter(
        due_date__gte=now
    ).count()

    # Total Working Hours This Week assigned by office
    total_working_hours_this_week = timedelta()
    current_date_calculation = start_of_week.date()

    #Total assigned tasks this week
    total_tasks_this_week = Tasks.objects.filter(
        assigned_to__user=signup_user
    ).filter(
        # Include tasks due this week
        Q(due_date__gte=start_of_week, due_date__lte=end_of_week) |
        # OR include incomplete tasks from previous weeks
        Q(due_date__lt=start_of_week, status__in=['pending', 'in_progress', 'on_hold']) |
        # OR include tasks completed this week but were late
        Q(status='completed', 
          submitted_on__gte=start_of_week, 
          submitted_on__lte=end_of_week,
          due_date__lt=F('submitted_on'))
    ).count()

    for i in range(7):  # Loop through the week
        day_name = current_date_calculation.strftime('%A').lower()
        try:
            office_hours = OfficeHours.objects.get(day=day_name, is_working_day=True)
            
            # Calculate total hours for the day
            start_datetime = timezone.make_aware(datetime.combine(current_date_calculation, office_hours.start_time))
            end_datetime = timezone.make_aware(datetime.combine(current_date_calculation, office_hours.end_time))
            
            # If this is today, only count hours up to current time
            if current_date_calculation == now.date():
                current_time = now.time()
                if current_time < office_hours.start_time:
                    break
                elif current_time > office_hours.end_time:
                    # If current time is after office hours end, count full day
                    end_datetime = timezone.make_aware(datetime.combine(current_date_calculation, office_hours.end_time))
                else:
                    # If current time is during office hours, count up to current time
                    end_datetime = now
            
            day_duration = end_datetime - start_datetime
            
            # Subtract break time if exists
            if office_hours.break_start_time and office_hours.break_end_time:
                break_start = timezone.make_aware(datetime.combine(current_date_calculation, office_hours.break_start_time))
                break_end = timezone.make_aware(datetime.combine(current_date_calculation, office_hours.break_end_time))
                
                # If today, adjust break time calculation
                if current_date_calculation == now.date():
                    current_time = now.time()
                    if current_time < office_hours.break_start_time:
                        # If current time is before break, don't subtract break
                        break_duration = timedelta(0)
                    elif current_time > office_hours.break_end_time:
                        # If current time is after break, subtract full break
                        break_duration = break_end - break_start
                    else:
                        # If current time is during break, subtract partial break
                        break_duration = now - break_start
                else:
                    break_duration = break_end - break_start
                
                day_duration -= break_duration
            
            total_working_hours_this_week += day_duration
            
        except OfficeHours.DoesNotExist:
            pass  # Skip if no office hours defined for this day
        
        # If we've reached today, stop counting future days
        if current_date_calculation >= now.date():
            break
            
        current_date_calculation += timedelta(days=1)
    
    # Format total working hours
    total_working_seconds = total_working_hours_this_week.total_seconds()
    working_hours = int(total_working_seconds // 3600)
    working_minutes = int((total_working_seconds % 3600) // 60)
    formatted_working_hours = f"{working_hours}h {working_minutes}m"
    
    # performance statistics context
    on_time_ratio = tasks_on_time_this_week / tasks_done_this_week if tasks_done_this_week > 0 else 0
    late_penalty = late_submissions / tasks_done_this_week if tasks_done_this_week > 0 else 0
    
    # Convert both times to hours for better percentage calculation
    total_time_hours = total_time_this_week.total_seconds() / 3600  # Convert seconds to hours
    total_working_hours = total_working_hours_this_week.total_seconds() / 3600  # Convert seconds to hours
    time_efficiency = total_time_hours / total_working_hours if total_working_hours > 0 else 0
    total_task_score = (on_time_ratio * 1.0 + late_penalty * 0.50) / tasks_done_this_week if tasks_done_this_week > 0 else 0
    performance_statistics = round((total_task_score * 0.5 + time_efficiency * 0.5) * 100, 2)

    # Get tasks completed this week
    now = timezone.now()
    start_of_week = now - timezone.timedelta(days=now.weekday())
    start_of_week = timezone.make_aware(datetime.combine(start_of_week.date(), datetime.min.time()))
    end_of_week = start_of_week + timezone.timedelta(days=6)
    
    # Get tasks completed this week with related data
    completed_tasks = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_week,
        submitted_on__lte=end_of_week
    ).select_related('project').order_by('submitted_on')

    # Calculate task-wise totals and prepare detailed data
    task_actual_hours = []
    task_expected_hours = []
    task_labels = []
    task_details = []

    # Process each task
    for task in completed_tasks:
        # Calculate actual time spent
        actual_time = TaskActivityLog.objects.filter(task=task).aggregate(
            total=Sum('duration')
        )['total'] or timedelta()
        actual_hours = actual_time.total_seconds() / 3600
        
        # Calculate expected time
        expected_hours = 0
        if task.expected_time:
            expected_hours = task.expected_time.total_seconds() / 3600

        # Add to chart data
        task_labels.append(f"{task.task_name[:20]}...")  # Truncate long names
        task_actual_hours.append(round(actual_hours, 1))
        task_expected_hours.append(round(expected_hours, 1))

        # Prepare detailed task information
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

    context = {
        'active_page': 'employee_statistics',
        'tasks_done_this_week': tasks_done_this_week,
        'total_time_this_week': formatted_time,
        'username': username,
        'user_role': user_role,
        'late_submissions': late_submissions,
        'performance_statistics': performance_statistics,
        'tasks_on_time_this_week': tasks_on_time_this_week,
        'total_tasks_this_week': total_tasks_this_week,
        'chart_data': chart_data,
        'task_details': task_details  # Add detailed task information to context
    }

    return render(request, 'employee-dashboard/emp-stats.html', context)

def admindashboard_stats(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session['user_role'] not in ['admin', 'manager']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('login')
    
    # Get current month and year if not specified
    current_month = request.POST.get('month', datetime.now().strftime('%Y-%m'))
    
    # Parse the month string to get year and month
    selected_date = datetime.strptime(current_month, '%Y-%m')
    year = selected_date.year
    month = selected_date.month
    
    # Create start and end of month for filtering
    start_of_month = timezone.make_aware(datetime(year, month, 1))
    if month == 12:
        end_of_month = timezone.make_aware(datetime(year + 1, 1, 1)) - timedelta(days=1)
    else:
        end_of_month = timezone.make_aware(datetime(year, month + 1, 1)) - timedelta(days=1)
    
    # Calculate total working hours for the month
    total_working_hours_month = timedelta()
    current_date = start_of_month.date()
    while current_date <= end_of_month.date():
        day_name = current_date.strftime('%A').lower()
        try:
            office_hours = OfficeHours.objects.get(day=day_name, is_working_day=True)
            
            # Calculate total hours for the day
            start_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.start_time))
            end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
            
            # If this is today, only count hours up to current time
            if current_date == timezone.now().date():
                current_time = timezone.now().time()
                if current_time < office_hours.start_time:
                    break
                elif current_time > office_hours.end_time:
                    end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                else:
                    end_datetime = timezone.now()
            
            day_duration = end_datetime - start_datetime
            
            # Subtract break time if exists
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
            
        except OfficeHours.DoesNotExist:
            pass
        
        current_date += timedelta(days=1)
    
    # Convert total working hours to float
    total_working_hours_float = total_working_hours_month.total_seconds() / 3600
    
    # First get tasks completed in the selected month
    completed_tasks = Tasks.objects.filter(
        status='completed',
        submitted_on__gte=start_of_month,
        submitted_on__lte=end_of_month
    )
    
    # Calculate total hours worked for the month from activity logs of completed tasks
    total_duration = timedelta()
    for task in completed_tasks:
        # Get all activity logs for this task
        task_logs = TaskActivityLog.objects.filter(task=task)
        for log in task_logs:
            if log.duration:  # Only add if duration exists
                total_duration += log.duration
    
    # Convert total duration to hours
    total_hours = total_duration.total_seconds() / 3600
    
    # Count tasks completed in the selected month
    tasks_done = completed_tasks.count()

    # Get all employees (excluding admin users)
    employees = UserDepartment.objects.exclude(
        user__role='admin'
    ).select_related('user')

    # Calculate efficiency for each employee
    employee_stats = []
    for employee in employees:
        # Get all tasks assigned to this employee in the current month
        assigned_tasks = Tasks.objects.filter(
            assigned_to=employee,
            due_date__year=year,
            due_date__month=month
        )
        total_assigned_tasks = assigned_tasks.count()
        
        # Get employee's completed tasks for the month
        employee_tasks = completed_tasks.filter(assigned_to=employee)
        tasks_done_this_month = employee_tasks.count()
        
        # Calculate total time spent on completed tasks
        employee_duration = timedelta()
        for task in employee_tasks:
            task_logs = TaskActivityLog.objects.filter(task=task)
            for log in task_logs:
                if log.duration:
                    employee_duration += log.duration
        
        # Calculate total working hours for the month
        total_working_hours = timedelta()
        current_date = start_of_month.date()
        while current_date <= end_of_month.date():
            day_name = current_date.strftime('%A').lower()
            try:
                office_hours = OfficeHours.objects.get(day=day_name, is_working_day=True)
                
                # Calculate total hours for the day
                start_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.start_time))
                end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                
                # If this is today, only count hours up to current time
                if current_date == timezone.now().date():
                    current_time = timezone.now().time()
                    if current_time < office_hours.start_time:
                        break
                    elif current_time > office_hours.end_time:
                        end_datetime = timezone.make_aware(datetime.combine(current_date, office_hours.end_time))
                    else:
                        end_datetime = timezone.now()
                
                day_duration = end_datetime - start_datetime
                
                # Subtract break time if exists
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
                
                total_working_hours += day_duration
                
            except OfficeHours.DoesNotExist:
                pass
            
            current_date += timedelta(days=1)
        
        # Calculate efficiency metrics
        total_working_hours_float = total_working_hours.total_seconds() / 3600
        total_time_spent_float = employee_duration.total_seconds() / 3600
        
        # Calculate on-time ratio
        on_time_tasks = employee_tasks.filter(due_date__gte=F('submitted_on')).count()
        on_time_ratio = on_time_tasks / tasks_done_this_month if tasks_done_this_month > 0 else 0
        
        # Calculate late penalty
        late_tasks = employee_tasks.filter(due_date__lt=F('submitted_on')).count()
        late_penalty = late_tasks / tasks_done_this_month if tasks_done_this_month > 0 else 0
        
        # Calculate time efficiency
        time_efficiency = total_time_spent_float / total_working_hours_float if total_working_hours_float > 0 else 0
        
        # Calculate task completion score based on assigned tasks
        task_completion_score = (tasks_done_this_month / total_assigned_tasks * 100) if total_assigned_tasks > 0 else 0
        
        # Calculate final efficiency percentage with new weights
        # 40% for task completion (completed vs assigned tasks)
        # 30% for time efficiency (hours worked vs available)
        # 30% for task quality (on-time vs late)
        efficiency = round(
            (task_completion_score * 0.4) +  # Weight for task completion ratio
            (time_efficiency * 100 * 0.3) +  # Weight for time efficiency
            ((on_time_ratio * 100) * 0.3),   # Weight for on-time completion
            2
        )
        
        # Cap efficiency at 100%
        efficiency = min(efficiency, 100)
        
        # Get employee name safely
        if employee.user and employee.user.first_name:
            employee_name = f"{employee.user.first_name} {employee.user.last_name if employee.user.last_name else ''}"
        else:
            employee_name = employee.user.username if employee.user else "Unknown User"
        
        employee_stats.append({
            'name': employee_name,
            'efficiency': efficiency,
            'hours_worked': round(total_time_spent_float, 1),
            'total_working_hours': round(total_working_hours_float, 1),
            'tasks_completed': tasks_done_this_month,
            'total_assigned_tasks': total_assigned_tasks,
            'on_time_tasks': on_time_tasks,
            'late_tasks': late_tasks
        })
    
    context = {
        'active_page': 'admin_statistics',
        'user_role': request.session.get('user_role', 'employee'),
        'current_month': current_month,
        'hours_worked': round(total_hours, 1),
        'total_working_hours': round(total_working_hours_float, 1),
        'tasks_done': tasks_done,
        'employee_stats': employee_stats
    }
    return render(request, 'admin-dashboard/admindashboard-stats.html', context)

def get_project_tasks(request, project_id):
    print(f"DEBUG: get_project_tasks view reached for project_id: {project_id}")
    if 'user_id' not in request.session:
        logging.warning("Unauthorized access to get_project_tasks: User not in session.")
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        logging.info(f"Attempting to fetch project with ID: {project_id}")
        project = Projects.objects.get(id=project_id)
        logging.info(f"Successfully fetched project: {project.name} (ID: {project.id})")
        
        # Get the current user
        signup_user = SignupUser.objects.get(id=request.session['user_id'])
        
        tasks = Tasks.objects.filter(project=project).select_related('assigned_to__user')
        logging.info(f"Found {tasks.count()} tasks for project {project.name}.")
        
        tasks_data = []
        for task in tasks:
            assigned_name = 'Unassigned'  # Default value
            if task.assigned_to and task.assigned_to.user:  # Check both assigned_to and user exist
                assigned_user = task.assigned_to.user
                assigned_name = f"{assigned_user.first_name} {assigned_user.last_name}" if assigned_user.first_name else assigned_user.username
            
            # Check for unread messages
            has_unread_messages = False
            last_read_status = TaskReadStatus.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()

            if latest_comment:
                # A message is unread if: 
                # 1. There is no last_read_status for this user/task, OR
                # 2. The latest comment is newer than the last_read_at timestamp, AND
                # 3. The latest comment was NOT sent by the current user.
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    has_unread_messages = True
                    logger.info(f"Task {task.id} ({task.task_name}) has unread messages for user {signup_user.id}")
                else:
                    logger.debug(f"Task {task.id} ({task.task_name}) has no unread messages for user {signup_user.id}")
            else:
                logger.debug(f"Task {task.id} ({task.task_name}) has no messages")
            
            task_data = {
                'id': task.id,
                'task_name': task.task_name,
                'task_description': task.task_description[:100] + '...' if len(task.task_description) > 100 else task.task_description,
                'status': task.status,
                'status_display': task.get_status_display(),
                'priority': task.priority,
                'report': task.report,
                'file_name': task.task_file.name.split('/')[-1] if task.task_file else None,
                'file_url': f"/dashboard/download_task_file/{task.id}/" if task.task_file else None,  # <-- ADD THIS LINE
                'assigned_to': assigned_name,
                'time_spent': task.get_total_time_spent(),
                'has_unread_messages': has_unread_messages  # Add unread message status
            }
            tasks_data.append(task_data)
        
        logging.info("Successfully prepared tasks data for JSON response.")
        return JsonResponse({'tasks': tasks_data})
    except Projects.DoesNotExist:
        logging.warning(f"Project with ID {project_id} not found.")
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_project_tasks for project ID {project_id}: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

def about_company(request):
    user_role = request.session.get('user_role', 'employee')
    company = companyDetails.get_instance()
    
    if request.method == 'POST' and request.user.is_staff:
        company.company_name = request.POST.get('company_name')
        company.company_description = request.POST.get('company_description')
        company.company_email = request.POST.get('company_email')
        company.company_phone = request.POST.get('company_phone')
        company.company_website = request.POST.get('company_website')
        company.company_address = request.POST.get('company_address')
        
        founded_date_str = request.POST.get('company_founded_date')
        if founded_date_str:
            company.company_founded_date = datetime.strptime(founded_date_str, '%Y-%m-%d').date()
        else:
            company.company_founded_date = None

        # Handle logo upload
        if 'company_logo' in request.FILES and request.FILES['company_logo']:
            # Delete old logo if it exists
            if company.company_logo:
                try:
                    os.remove(company.company_logo.path)
                except:
                    pass
            company.company_logo = request.FILES['company_logo']
        
        # Handle social media links (JSON field)
        social_media_links_json = request.POST.get('company_social_media_links')
        if social_media_links_json:
            company.company_social_media_links = json.loads(social_media_links_json)
        else:
            company.company_social_media_links = {}

        company.save()
        messages.success(request, 'Company details updated successfully!')
        return redirect('about_company')
    
    context = {
        'company': company,
        'user_role': user_role,
        'active_page': 'about_company',
    }
    return render(request, 'admin-dashboard/about-company.html', context)

def employee_company_profile(request):
    company = companyDetails.get_instance()
    user_role = request.session.get('user_role', 'employee')
    return render(request, 'employee-dashboard/company-profile.html', {
        'company': company,
        'user_role': user_role,
        'active_page': 'employee_company_profile'
    })

def employee_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    signup_user = SignupUser.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')
    
    # Get or create employee profile
    profile, created = employeeProfile.objects.get_or_create(user=signup_user)
    
    if request.method == 'POST':
        # Update profile fields
        profile.contact_number = request.POST.get('contact_number')
        profile.address = request.POST.get('address')
        profile.bio = request.POST.get('bio')
        
        # Handle date of birth
        dob = request.POST.get('date_of_birth')
        if dob:
            profile.date_of_birth = dob
            
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('employee_profile')
    
    context = {
        'user': signup_user,
        'profile': profile,
        'user_role': user_role,
        'active_page': 'employee_profile'
    }
    return render(request, 'employee-dashboard/employee-profile.html', context)

def get_task_comments(request, task_id):
    if 'user_id' not in request.session:
        print("Error: User not authenticated")
        return JsonResponse({'error': 'Not authenticated'}, status=401)
        
    try:
        print(f"Fetching comments for task {task_id}")
        
        # First verify the task exists
        try:
            task = Tasks.objects.get(id=task_id)
        except Tasks.DoesNotExist:
            print(f"Error: Task {task_id} not found")
            return JsonResponse({'error': 'Task not found'}, status=404)
            
        # Get messages with related user data
        messages = ChatMessage.objects.filter(task_id=task_id).select_related('user').order_by('timestamp')
        print(f"Found {messages.count()} messages")
        
        response_data = {
            'messages': []
        }
        
        for msg in messages:
            try:
                message_data = {
                    'username': msg.user.username if msg.user else 'Unknown User',
                    'message': msg.message,
                    'timestamp': msg.timestamp.strftime('%B %d, %Y %H:%M') if msg.timestamp else '',
                    'is_current_user': msg.user.id == request.session['user_id'] if msg.user else False
                }
                response_data['messages'].append(message_data)
            except Exception as e:
                print(f"Error processing message {msg.id}: {str(e)}")
                continue
        
        print("Response data:", response_data)
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        print(f"Error in get_task_comments: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return JsonResponse({
            'error': 'Internal server error',
            'details': str(e)
        }, status=500)

def check_project_unread(request, project_id):
    """Check if a project has any unread messages for the current user"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        signup_user = SignupUser.objects.get(id=request.session['user_id'])
        project = Projects.objects.get(id=project_id)
        
        # Check if any tasks in this project have unread messages
        has_unread = False
        project_tasks = Tasks.objects.filter(project=project)
        
        for task in project_tasks:
            last_read_status = TaskReadStatus.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
            
            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    has_unread = True
                    break
        
        return JsonResponse({'has_unread': has_unread})
        
    except (Projects.DoesNotExist, SignupUser.DoesNotExist):
        return JsonResponse({'error': 'Project or user not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def test_project_notification(request, project_id):
    """Test endpoint to manually trigger project notifications"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        import json
        
        channel_layer = get_channel_layer()
        user_id = request.session['user_id']
        
        # Send test project notification
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'project_unread_notification',
                'project_id': project_id,
                'has_unread': True
            }
        )
        
        return JsonResponse({'success': True, 'message': f'Test notification sent for project {project_id}'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def pending_tasks_json(request):
    # Get the logged-in user's UserDepartment
    from .models import UserDepartment
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    try:
        user_department = UserDepartment.objects.get(user_id=request.session['user_id'])
    except UserDepartment.DoesNotExist:
        return JsonResponse({'tasks': []})

    pending_tasks = Tasks.objects.filter(status='pending', assigned_to=user_department).order_by('-id')
    tasks_data = []
    for task in pending_tasks:
        tasks_data.append({
            'id': task.id,
            'task_name': task.task_name,
            'project': task.project.name if task.project else '',
            'priority': task.get_priority_display(),
            'status': task.get_status_display(),
            'due_date': task.due_date.strftime('%B %d, %Y') if task.due_date else '',
            'time_spent': task.get_total_time_spent() if hasattr(task, 'get_total_time_spent') else '0h 0m',
            'description': task.task_description or '',
        })
    return JsonResponse({'tasks': tasks_data})

def start_task(request, task_id):
    if request.method == 'POST':
        try:
            task = Tasks.objects.get(id=task_id)
            if task.status == 'pending':
                task.status = 'on_hold'
                task.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Task cannot be started from current status.'}, status=400)
        except Tasks.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def ongoing_tasks_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    try:
        user_department = UserDepartment.objects.get(user_id=request.session['user_id'])
    except UserDepartment.DoesNotExist:
        return JsonResponse({'tasks': []})

    ongoing_tasks = Tasks.objects.filter(
        assigned_to=user_department,
        status__in=['in_progress', 'on_hold']
    ).order_by('-id')
    tasks_data = []
    for task in ongoing_tasks:
        tasks_data.append({
            'id': task.id,
            'task_name': task.task_name,
            'project': task.project.name if task.project else '',
            'priority': task.get_priority_display(),
            'status': task.get_status_display(),
            'due_date': task.due_date.strftime('%B %d, %Y') if task.due_date else '',
            'time_spent': task.get_total_time_spent() if hasattr(task, 'get_total_time_spent') else '0h 0m',
            'description': task.task_description or '',
        })
    return JsonResponse({'tasks': tasks_data})
def get_task_report(request, task_id):
    try:
        task = Tasks.objects.get(id=task_id)
        return JsonResponse({'success': True, 'report': task.report or ''})
    except Tasks.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
def get_task_file(request, task_id):
    try:
        task = Tasks.objects.get(id=task_id)
        file_url = task.task_file.url if task.task_file else ''
        file_name = task.task_file.name.split('/')[-1] if task.task_file else ''
        return JsonResponse({'success': True, 'file_url': file_url, 'file_name': file_name})
    except Tasks.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

def approval_pending_tasks_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    
    user_role = request.session.get('user_role', 'employee')
    signup_user = SignupUser.objects.get(id=request.session['user_id'])
    
    try:
        if user_role in ['teamlead', 'project_manager']:
            # For team leads/project managers, get their departments
            user_departments = Department.objects.filter(userdepartment__user=signup_user)
            tasks = Tasks.objects.filter(
                project__department__in=user_departments,
                status='not_assigned'
            ).select_related('project', 'assigned_to__user')
        else:
            # For regular employees, get only their tasks
            tasks = Tasks.objects.filter(
                assigned_to__user=signup_user,
                status='not_assigned'
            ).select_related('project')

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': task.id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'project_name': task.project.name if task.project else '',
                'project_department': task.project.department.name if task.project and task.project.department else '',
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
                'status': task.status,
                'status_display': task.get_status_display(),
                'priority': task.get_priority_display(),
                'time_spent': task.get_total_time_spent()
            })
        
        return JsonResponse({'tasks': tasks_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_project_employees(request, project_id):
    try:
        project = Projects.objects.get(id=project_id)
        employees = UserDepartment.objects.filter(department=project.department)
        employee_list = [
            {
                'id': emp.user.id,
                'name': f"{emp.user.first_name} {emp.user.last_name}".strip() or emp.user.username
            }
            for emp in employees if emp.user is not None  # Only include if user exists
        ]
        return JsonResponse({'employees': employee_list})
    except Projects.DoesNotExist:
        return JsonResponse({'employees': []})

@require_GET
@csrf_exempt
def employee_today_stats_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    signup_user = SignupUser.objects.get(id=request.session['user_id'])
    user_department = UserDepartment.objects.filter(user=signup_user).first()
    today = timezone.now().date()
    total_time_today = get_user_total_time_today(user_department)
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    tasks_done_today = Tasks.objects.filter(
        assigned_to__user=signup_user,
        status='completed',
        submitted_on__gte=start_of_day,
        submitted_on__lte=end_of_day
    ).count()
    tasks_expiring_today = Tasks.objects.filter(
        due_date=today,
        assigned_to__user=signup_user
    ).exclude(status='completed').count()
    expired_tasks = Tasks.objects.filter(
        due_date__lt=today,
        assigned_to__user=signup_user
    ).exclude(status='completed').count()
    return JsonResponse({
        'total_time_today': total_time_today,
        'tasks_done_today': tasks_done_today,
        'tasks_expiring_today': tasks_expiring_today,
        'expired_tasks': expired_tasks
    })

