from this import d
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password 
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import department as Department, projects , tasks , settings , employee_details, task_activity_log, users, companyDetails,ChatMessage, read_status , employee_designation, Notification ,department
from django.http import JsonResponse, Http404, FileResponse
from django.http import HttpResponse
from django.db import transaction
import os
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import tasks, task_activity_log
from django.db.models import Sum, Q, F, Max
from datetime import datetime, timedelta
from .models import Notification
from .tasks import check_office_hours
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse  
from django.core.exceptions import ValidationError
from .models import TaskStatsService
logger = logging.getLogger(__name__)

# Create your views here.
def Register(request):
    message = None
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                message = "This email is already registered as a superuser or staff user."
            elif users.objects.filter(email=email).exists():
                message = "This email is already registered."
            elif users.objects.filter(username=username).exists():
                message = "This username is already taken."
            else:
                hashed_password = make_password(password)
                signup_user = users.objects.create(
                    first_name=fname,
                    last_name=lname,
                    username=username,
                    email=email,
                    password=hashed_password,
                    role='employee',
                )
                signup_user.is_verified = False
                signup_user.save()
                raw_otp = signup_user.generate_verification_code()
                send_mail(
                    subject='OTP Verification',
                    message=f'Your verification code is {raw_otp}',
                    from_email='arshadotpwala@gmail.com',
                    recipient_list=[signup_user.email],
                )
                request.session['user_id'] = signup_user.id
                return redirect('verify_otp')

                # messages.success(request, "Account successfully created.")
                # return redirect('login')
        else:
            message = "Passwords do not match."
    return render(request, 'user/register/index.html', {'message': message})

def VerifyOTP(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')
    user = users.objects.get(id=user_id)
    if user.is_verified:
        if user.is_code_expired():
            user.verification_code = None
            user.verification_created_at = None
            user.verification_attempts = 0
            user.save()
            messages.error(request, "OTP is expired")
            return redirect('forgot-password')
        if request.method == 'POST':
            entered_otp = request.POST.get('otp')
            if user.is_max_attempts_reached():
                user.verification_code = None
                user.verification_created_at = None
                user.verification_attempts = 0
                user.save()
                messages.error(request, 'You have exceeded the number of attempts. Please Try Again Later')
                return redirect('register')
            if user.is_code_valid(entered_otp):
                user.verification_code = None
                user.verification_created_at = None
                user.verification_attempts = 0
                user.save()
                messages.success(request, "PLease Enter Your New Password")
                return redirect('confirm_newpass')
            else:
                user.save()
                messages.error(request, 'Invalid OTP')
    elif not user.is_verified:
        if request.method == 'POST':
            entered_otp = request.POST.get('otp')
            if user.is_max_attempts_reached():
                user.delete()
                messages.error(request, 'You have exceeded the number of attempts. Please register again')
                return redirect('register')
            if user.is_code_valid(entered_otp):
                user.is_active = True
                user.is_verified = True
                user.verification_code = None
                user.verification_created_at = None
                user.verification_attempts = 0
                user.save()
                messages.success(request, "Account successfully created.")
                return redirect('login')
            else:
                user.save()
                messages.error(request, 'Invalid OTP')
    return render(request, 'user/otp/index.html')

    


def Register_UserbyAdmin(request):
    if request.session['user_role'] in ['admin', 'manager']:
        departments = Department.objects.all()
        designations = employee_designation.designation_choices
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            role = 'employee'
            department_id = request.POST.get('department')  # This can be empty
            selected_designations = request.POST.getlist('designation')
            
            try:
                # Call the class method with all necessary data
                new_user = users.register_by_admin(
                    fname=fname,
                    lname=lname,
                    username=username,
                    email=email,
                    password=password,
                    confirm_password=confirm_password, # Pass confirm_password to the model method
                    department_id=department_id,
                    selected_designations=selected_designations
                )
                messages.success(request, f"User '{new_user.username}' successfully created.")
                return redirect('dashboard')
            except ValidationError as e: # Catch validation errors from the model method
                # Django's ValidationError can have a list of messages
                for msg in e.messages:
                    messages.error(request, msg)
            except Exception as e: # Catch any other unexpected errors
                messages.error(request, f"An unexpected error occurred: {e}")

            return render(request, 'user/adduser/index.html' ,{
                'departments': departments,
                'roles': users.ROLE_CHOICES,
                'designations': designations,
            })
        return render(request, 'user/adduser/index.html', {
            'departments': departments,
            'message': None,
            'roles': users.ROLE_CHOICES,
            'designations': designations,
        })
    else:
        return redirect('login')
    
def Login(request):
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')
        signup_user = users.objects.filter(username=username).first()
        if signup_user:
            try:
                user = users.login(username, password)
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['user_role'] = user.role 
                if user.role == 'admin' or user.role == 'manager':
                    return redirect('admin_statistics')
                else:
                    return redirect('new_employee_dashboard')  
            except ValidationError as e:
                message = e.message
        else:
            message = "Invalid username or password."
    return render(request, 'user/login/index.html', {'message': message})

def ForgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
           user, message = users.password_reset(email)
           if message == "OTP sent successfully.":
                request.session['user_id'] = user.id
                messages.success(request, message)
                return redirect('verify_otp')
        except users.DoesNotExist:
            messages.error(request, "User does not exist.")
    return render(request, 'user/forget/index.html')

def ConfirmNewPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.session.get('user_id')
        
        try:
            users.confirm_new_password(user_id, password, confirm_password)
            messages.success(request, "Password updated successfully.")
            return redirect('login')
        except ValidationError as e:
            messages.error(request, str(e))
    return render(request, 'user/newpass/index.html')

def Logout(request):
    request.session.flush()
    return redirect('login')

def ToggleUserStatus(request, user_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        try:
            user = users.disableuser(user_id)
            
            msg = f"{user.username}'s status has been updated to {'Active' if user.status else 'Disabled'}."
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'is_active': user.status,
                    'new_status_display': 'Active' if user.status else 'Disabled'
                })
            else:
                messages.success(request, msg)

        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            else:
                messages.error(request, str(e))
    else:
        msg = "You do not have permission to perform this action."
        if is_ajax:
            return JsonResponse({'success': False, 'error': msg}, status=403)
        else:
            messages.error(request, msg)
            
def PromoteUser(request, user_id, new_role):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def respond(success, msg, status=200, extra=None):
        if is_ajax:
            data = {
                'success': success,
            }
            if success:
                data['message'] = msg
                if extra:
                    data.update(extra)
            else:
                data['error'] = msg  # 👈 restore this line
            return JsonResponse(data, status=status)
        else:
            (messages.success if success else messages.error)(request, msg)
            return redirect('dashboard')

    # Permission check
    if request.session.get('user_role') not in ['admin', 'manager']:
        return respond(False, "You do not have permission to perform this action.", status=403)

    # Promotion logic
    try:
        user = users.promote_user(user_id, new_role)
        msg = f"{user.username} has been promoted to {user.get_role_display()}."
        return respond(True, msg, extra={'new_role': user.get_role_display()})
    except ValidationError as e:
        return respond(False, str(e), status=400)


#dashboard  
def Adddepartments(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  
        user_role = request.session.get('user_role', 'employee')
        if request.method == 'POST':
            department_name = request.POST.get('department_name')
            try:
                Department.add_departments(department_name)
                messages.success(request, f"department {department_name} has been added successfully.")
            except ValidationError as e:
                messages.error(request, str(e))

        
        departments = Department.objects.all()  

        return render(request, 'admin/departments/index.html', {
            'departments': departments, 
            'user_role': user_role,
            'active_page': 'departments',
        })
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')


def Deletedepartment(request, department_id):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  # Use 'user_role'
        try:
            Department.delete_department(department_id)
            messages.success(request, f"Department has been deleted successfully.")
        except ValidationError as e:
                messages.error(request, str(e))
    else:
        messages.error(request, "You do not have permission to perform this action.")
    return redirect('add_department')  # Redirect to the same page or any other page as needed

def Assigndepartment(request, user_id, department_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        try:
            employee_details_obj=employee_details.assign_department(department_id, user_id)
            if is_ajax:
                return JsonResponse({'success': True, 'new_department': employee_details_obj.department.name ,})
            messages.success(request, f"{employee_details_obj.user.username}'s department was updated to {employee_details_obj.department.name}.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
            messages.error(request, str(e))
        return redirect('dashboard')
    else:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'You do not have permission to perform this action.'}, status=403)
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')
    

    #Projects
    #Projects
def Addprojects(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        user_role = request.session.get('user_role', 'employee')
        if request.method == 'POST':
            project_name = request.POST.get('project_name')
            description = request.POST.get('description')
            department_id = request.POST.get('department')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            status = 0  # Pending

            try:
                projects.add_projects(project_name, description, department_id, start_date, end_date, status)
                messages.success(request, f"Project {project_name} has been added successfully.")
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect('add-projects')
        else:
            departments = Department.objects.all()
            return render(request, 'admin/newproject/index.html', {
                'departments': departments,
                'user_role': user_role,
                'active_page': 'new_project'
            })
    else:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('login')
    
def Allprojects(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager', 'project_manager']:
        all_projects = projects.objects.select_related('department').all()
        task_priorities = tasks.task_priorty
        all_employees = users.objects.select_related('user').all()
        user_role = request.session.get('user_role', 'employee')

        selected_project = None
        filtered_employees = None
        assign_project_id = request.GET.get('assign')
        if assign_project_id:
            try:
                selected_project = projects.objects.get(id=assign_project_id)
                # Filter employees by department using employee_details
                filtered_employees = all_employees.filter(employee_details__department=selected_project.department)
            except projects.DoesNotExist:
                selected_project = None
                filtered_employees = None

        return render(request, 'admin/allprojects/index.html', {
            'projects': all_projects,
            'active_page': 'all_projects',
            'task_priorities': task_priorities,
            'all_employees': all_employees,
            'selected_project': selected_project,
            'filtered_employees': filtered_employees,
            'user_role': user_role,
        })
    else:
        return redirect('login')
    
def Updateprojectstatus(request, project_id, new_status):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    try:
        # Use the model method to update project status
        project = projects.update_project_status(project_id, new_status)
        
        # Success message
        msg = f"Project status updated to {project.get_status_display()}."
        if is_ajax:
            return JsonResponse({'success': True, 'message': msg, 'new_status': project.get_status_display()})
        messages.success(request, msg)
    except ValidationError as e:
        # Handle validation errors from the model method
        error_msg = str(e)
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        messages.error(request, error_msg)
    except projects.DoesNotExist:
        # This should be handled by the model method, but keeping as a fallback
        error_msg = "Project does not exist."
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg}, status=404)
        messages.error(request, error_msg)

    # Redirect based on user role
    user_role = request.session.get('user_role')
    if user_role == 'admin':
        return redirect('all-projects')
    elif user_role in ['employee', 'project_manager', 'teamlead']:
        return redirect('new_employee_dashboard')
    else:
        return redirect('login')
    
##tasks
def CreateTask(request):
    if request.method == 'POST':
        try:
            user_role = request.session.get('user_role')
            current_user = users.objects.get(id=request.session['user_id'])

            project_id = request.POST.get('project_id')
            assigned_to_id = request.POST.get('assigned_to')
            task_name = request.POST.get('task_name')
            task_description = request.POST.get('task_description')
            due_date = request.POST.get('duedate')
            priority = request.POST.get('priority')

            # Parse time
            hours = int(request.POST.get('expected_time_hours', 0))
            minutes = int(request.POST.get('expected_time_minutes', 0))
            expected_time = timedelta(hours=hours, minutes=minutes)

            # Due date
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            # Get assigned_to user
            assigned_to = current_user if user_role == 'employee' else users.objects.get(id=assigned_to_id)

            # Determine status
            status = 5 if user_role == 'employee' else 0

            # Call model method
            task = tasks.createtask(
                project_id=project_id,
                task_name=task_name,
                task_description=task_description,
                assigned_to=assigned_to,
                assigned_from=current_user,
                priority=priority,
                expected_time=expected_time,
                status=status,
                due_date=due_date
            )

            # Notifications
            if user_role in ['teamlead', 'project_manager', 'admin'] and current_user != assigned_to:
                Notification.objects.get_or_create(
                    user=assigned_to,
                    message=f"You have been assigned a new task: {task_name} by {current_user.username}",
                    defaults={'is_read': False}
                )
            elif user_role == 'employee' and current_user == assigned_to:
                notif_msg = f"{current_user.username} requested approval for a new task: {task_name}."
                teamleads = users.objects.filter(role='teamlead', employee_details__department=assigned_to.department)
                admins = users.objects.filter(role='admin')
                for user in set(list(teamleads) + list(admins)):
                    if user != current_user:
                        Notification.objects.get_or_create(
                            user=user,
                            message=notif_msg,
                            defaults={'is_read': False}
                        )

            messages.success(request, "Task successfully created.")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Task created successfully!'})
            else:
                return redirect('new_employee_dashboard')

        except ValidationError as e:
            messages.error(request, str(e))
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            messages.error(request, f"Error creating task: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    # Redirect fallback
    role_redirects = {
        'admin': 'all-projects',
        'project_manager': 'new_employee_dashboard',
        'teamlead': 'new_employee_dashboard',
        'employee': 'new_employee_dashboard',
    }
    return redirect(role_redirects.get(request.session.get('user_role'), 'login'))
        
def Assignedtasks(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin']:
        user_projects = projects.objects.filter(status=1)  # Ongoing
        user_role = request.session.get('user_role', 'employee')
        user_tasks = tasks.objects.filter(project__in=user_projects).select_related(
            'project', 'assigned_to', 'assigned_from'
        )
        for project in user_projects:
            print(project.status)
        if request.session['user_role'] == 'admin':
            return render(request, 'admin/assignedtasks/index.html', {
                'projects': user_projects,
                'tasks': user_tasks,
                'user_role': user_role,
                'active_page': ''
            })
    else:
        return redirect('login')

#update task statuses
def Updatetaskstatus(request, task_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == 'POST':
        try:
            # Use the model method to update task status
            new_status = request.POST.get('status')
            task = tasks.update_task_status(task_id, new_status)
            
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, f"Task status updated to {task.get_status_display()}.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error: {str(e)}")
    if is_ajax:
        # If AJAX and we reach here, something went wrong
        return JsonResponse({'success': False, 'error': 'Could not complete task.'}, status=400)
    return redirect('new_employee_dashboard')

def start_working(request, task_id):
    from django.utils import timezone
    from .models import settings
    import pytz

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == 'POST':
        try:
            # Get current time in Asia/Karachi timezone (use provided local time for accuracy)
            import datetime
            karachi_tz = pytz.timezone('Asia/Karachi')
            now = datetime.datetime(2025, 8, 14, 1, 32, 31, tzinfo=karachi_tz)
            # Enforce office hours check
            if not settings.is_within_office_hours(now):
                msg = "Cannot start task: not within office hours or no office hours set for today."
                if is_ajax:
                    return JsonResponse({'success': False, 'error': msg}, status=400)
                messages.error(request, msg)
                return redirect('new_employee_dashboard')
            # Use the model method to update task status to "In Progress" (1)
            task = tasks.update_task_status(task_id, 1)
            # Check if time tracking session was created
            session_exists = task_activity_log.objects.filter(
                task=task,
                end_time__isnull=True
            ).exists()
            if is_ajax:
                return JsonResponse({'success': True})
            if session_exists:
                messages.success(request, f"Task status updated to {task.get_status_display()} (started working).")
            else:
                messages.warning(request, f"Task marked as in progress, but time tracking will start when office hours begin.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error: {str(e)}")
    return redirect('new_employee_dashboard')

def stop_working(request, task_id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == 'POST':
        try:
            # Use the model method to update task status to "On Hold" (3)
            task = tasks.update_task_status(task_id, 3)
            
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, f"Task status updated to {task.get_status_display()} (stopped working).")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error: {str(e)}")
    return redirect('new_employee_dashboard')

def DeleteTask(request, project_id):
    task_id = request.GET.get('task_id') or request.POST.get('task_id')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    user_id = request.session['user_id']
    username = request.session.get('username')
    
    if task_id:
        try:
            # Use the model method to delete the task
            tasks.delete_task(task_id, username)
            
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'Task deleted successfully.'})
            messages.success(request, "Task deleted successfully.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error: {str(e)}")
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

def Gettasks(request):
    project_id = request.GET.get('project_id')
    if project_id:
        try:
            project = projects.objects.get(id=project_id)
            project_tasks = tasks.objects.filter(project=project).select_related(
                'project',
                'assigned_to',
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
                    'assigned_to': f"{task.assigned_to.first_name} {task.assigned_to.last_name}" if task.assigned_to and task.assigned_to.first_name else (task.assigned_to.username if task.assigned_to else 'Unassigned'),
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
                for task in project_tasks
            ]
            return JsonResponse({'tasks': tasks_data})
        except projects.DoesNotExist:
            return JsonResponse({'tasks': []})
    return JsonResponse({'tasks': []})

def upload_task_file(request, task_id):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            uploaded_file = request.FILES.get('myfile')
            result = tasks.upload_task_file(task_id, uploaded_file)
            
            if is_ajax:
                return JsonResponse(result)
            messages.success(request, "File uploaded successfully.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error uploading file: {str(e)}")
    return redirect('new_employee_dashboard')

def upload_task_report(request, task_id):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            report_text = request.POST.get('report')
            result = tasks.upload_task_report(task_id, report_text)
            
            if is_ajax:
                return JsonResponse(result)
            messages.success(request, "Report submitted successfully.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f"Error submitting report: {str(e)}")
    return redirect('new_employee_dashboard')

def download_task_file(request, task_id):
    try:
        result = tasks.get_task_file(task_id)
        file_path = result['file_path']
        file_name = result['file_name']
        
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        # Use quotes and encoding for the filename to handle special characters
        response['Content-Disposition'] = f'attachment; filename="{file_name}"; filename*=UTF-8\'\'{file_name}'
        return response
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('new_employee_dashboard')
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('new_employee_dashboard')

def approve_task(request, task_id):
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            task = tasks.update_task_status(task_id, 3)
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, "Task has been approved and is now pending.")
        except ValidationError as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, str(e))
        except Exception as e:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Unknown error.'}, status=500)
            messages.error(request, f"Error approving task: {str(e)}")
            
    if request.session['user_role'] == 'admin':
        return redirect('assigned_tasks')
    elif request.session['user_role'] in ['project_manager', 'teamlead']:
        return redirect('new_employee_dashboard')
    return redirect('login')
    
#Time Tracking
def dashboard_settings(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        office_hours = settings.get_office_hours()
        days_of_week = [['monday', 'Monday'], ['tuesday', 'Tuesday'], ['wednesday', 'Wednesday'],
                       ['thursday', 'Thursday'], ['friday', 'Friday'], ['saturday', 'Saturday'],
                       ['sunday', 'Sunday']]
        context = {
            'office_hours': office_hours,
            'days_of_week': days_of_week,
            'active_page': 'settings',
            'user_role': request.session.get('user_role')
        }
        return render(request, 'admin/timesettings/index.html', context)
    messages.error(request, "You don't have permission to perform this action.")
    return redirect('login')


def add_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            try:
                settings.add_office_hours(
                    day=request.POST.get('day'),
                    start_time=request.POST.get('start_time'),
                    end_time=request.POST.get('end_time'),
                    break_start_time=request.POST.get('break_start_time'),
                    break_end_time=request.POST.get('break_end_time')
                )
                messages.success(request, f"Office hours have been added successfully.")
            except ValidationError as e:
                messages.error(request, str(e))
        return redirect('dashboard_settings')
    messages.error(request, "You don't have permission to perform this action.")
    return redirect('login')


def edit_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            try:
                settings.update_office_hours(
                    day=request.POST.get('day'),
                    start_time=request.POST.get('start_time'),
                    end_time=request.POST.get('end_time'),
                    break_start_time=request.POST.get('break_start_time'),
                    break_end_time=request.POST.get('break_end_time')
                )
                messages.success(request, f"Office hours have been updated successfully.")
            except ValidationError as e:
                messages.error(request, str(e))
        return redirect('dashboard_settings')
    messages.error(request, "You don't have permission to perform this action.")
    return redirect('login')

def delete_office_hours(request):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:
        if request.method == 'POST':
            try:
                settings.delete_office_hours(day=request.POST.get('day'))
                messages.success(request, f"Office hours have been deleted successfully.")
            except ValidationError as e:
                messages.error(request, str(e))
        return redirect('dashboard_settings')
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




#Dasboard home pages
# Create your views here.
def dashboard(request):
        user = users.objects.all()
        departments = Department.objects.all()
        user_role = request.session.get('user_role', 'employee')
        roles_with_access = ['admin', 'manager']
        if 'user_role' in request.session and request.session['user_role'] in roles_with_access:
            return render(request, 'admin/users/index.html', 
                          {
                            'users': user,
                            'departments': departments,
                            'user_role': user_role,
                            'roles_with_access': roles_with_access,
                            'active_page': 'dashboard',
                            'roles': users.ROLE_CHOICES,
                                         })
        else:
            return redirect('login')
        
def new_employee_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    elif request.session.get('user_role') == 'admin':
        return redirect('admin_statistics')
    signup_user = users.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')
    username = signup_user.first_name or signup_user.username
    roles_with_access = ['project_manager', 'teamlead']
    statuses_to_show = [0, 1, 3]
    user_department_obj = signup_user.department
    user_departments = [user_department_obj] if user_department_obj else []
    task_priorities = tasks.task_priorty
    user_department = user_department_obj
    user_projects = projects.objects.filter(department__in=user_departments)

    # Get user's department for time tracking
    total_time_today = task_activity_log.get_user_total_time_today(signup_user)

    #Filtered Employees
    filtered_employees = employee_details.filter_employees_by_department(user_department_obj)
    print(f"Filtered Employees: {filtered_employees.count()}")

    # For team leads and project managers, get additional department tasks
    department_tasks = None
    if user_role in ['teamlead', 'project_manager']:
        department_tasks = tasks.get_department_tasks(user_department_obj)
    
    # Get employee's assigned tasks
    user_tasks = tasks.objects.filter(assigned_to=signup_user)
    for task in user_tasks:
        if task.task_file:
            task.file_url = task.task_file.url
            task.file_name = task.task_file.name.split('/')[-1]
        
        # Check for unread messages
        read_status.check_unread_messages(signup_user)
    
    if department_tasks:
        for task in department_tasks:
            if task.task_file:
                task.file_url = task.task_file.url
                task.file_name = task.task_file.name.split('/')[-1]
    
    for project in user_projects:
        project.has_tasks_assigned = tasks.objects.filter(project=project, assigned_to=signup_user).exists()
        
        # Check if any tasks in this project have unread messages
        project.has_unread_messages = False
        project_tasks = tasks.objects.filter(project=project)
        for task in project_tasks:
            last_read_status = read_status.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
            
            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    project.has_unread_messages = True
                    logger.info(f"Project {project.id} ({project.name}) has unread messages for user {signup_user.id}")
                    break  # No need to check other tasks if we found unread messages
    
    #tasks STats for today context updated in the contect
    task_counts = tasks.get_task_counts(signup_user)
    # Get or create employee profile
    profile, created = employee_details.objects.get_or_create(user=signup_user)
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
        'projects': user_projects,
        'tasks': user_tasks,
        'department_tasks': department_tasks,
        'has_permission': has_permission,
        'active_page': 'new_employee_dashboard',
        'task_priorities': task_priorities,
        'total_time_today': total_time_today,
        'user_department': user_department,
        'filtered_employees': filtered_employees,
        'profile': profile,  # Add profile to context
        'chat_messages': chat_messages,  # Add chat messages to context
        'tasks_expiring_today': task_counts['tasks_expiring_today'],
        'expired_tasks': task_counts['expired_tasks'],
        'tasks_done_today': task_counts['tasks_done_today'],
    }
    return render(request, 'employee/dashboard/index.html', context)

def employee_statistics(request):
    if 'user_id' not in request.session:
        return redirect('login')
    elif request.session.get('user_role') == 'admin':
        return redirect('admin_statistics')
    signup_user = users.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')
    username = signup_user.first_name or signup_user.username
    # Month selection logic (default to current month)
    if request.method == 'POST' and 'month' in request.POST:
        current_month = request.POST['month']
    else:
        current_month = timezone.now().strftime('%Y-%m')
    year, month = map(int, current_month.split('-'))
    stats = TaskStatsService.get_employee_monthly_stats(signup_user, year, month)
    context = {
        'active_page': 'employee_statistics',
        'current_month': stats['current_month'],
        'tasks_done_this_month': stats['tasks_done_this_month'],
        'total_time_this_month': stats['total_time_this_month'],
        'username': username,
        'user_role': user_role,
        'late_submissions_this_month': stats['late_submissions_this_month'],
        'performance_statistics': stats['performance_statistics'],
        'tasks_on_time_this_month': stats['tasks_on_time_this_month'],
        'total_tasks_this_month': stats['total_tasks_this_month'],
        'chart_data': stats['chart_data'],
        'task_details': stats['task_details']
    }
    return render(request, 'employee/stats/index.html', context)

def admindashboard_stats(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session['user_role'] not in ['admin', 'manager']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('login')
    if request.method == 'POST' and 'month' in request.POST:
        current_month = request.POST['month']
    else:
        current_month = timezone.now().strftime('%Y-%m')
    year, month = map(int, current_month.split('-'))
    employee_stats = TaskStatsService.get_all_employees_monthly_stats(year, month)
    agency_stats = TaskStatsService.get_agency_monthly_stats(year, month)
    context = {
        'active_page': 'admin_statistics',
        'user_role': request.session.get('user_role', 'employee'),
        'current_month': current_month,
        'employee_stats': employee_stats,
        'hours_worked': agency_stats['hours_worked'],
        'total_working_hours': agency_stats['total_working_hours'],
        'tasks_done': agency_stats['tasks_done'],
        'projects_done': agency_stats['projects_done'],
    }
    return render(request, 'admin/dashboard/index.html', context)

def get_project_tasks(request, project_id):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    try:
        signup_user = users.objects.get(id=request.session['user_id'])
        result = projects.get_project_tasks_data(project_id, signup_user)
        if result.get('success'):
            return JsonResponse({'tasks': result['tasks']})
        else:
            return JsonResponse({'error': result.get('error', 'Unknown error')}, status=result.get('status', 500))
    except users.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def about_company(request):
    user_role = request.session.get('user_role', 'employee')
    company = companyDetails.get_instance()
    
    if request.method == 'POST' and user_role in ['admin', 'manager']:
        print(f"Processing company update for user role: {user_role}")
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        # Extract all parameters from request
        company_name = request.POST.get('company_name')
        company_description = request.POST.get('company_description')
        company_email = request.POST.get('company_email')
        company_phone = request.POST.get('company_phone')
        company_website = request.POST.get('company_website')
        company_address = request.POST.get('company_address')
        company_founded_date = request.POST.get('company_founded_date')
        company_logo_file = request.FILES.get('company_logo') if 'company_logo' in request.FILES else None
        social_media_links_json = request.POST.get('company_social_media_links')
        social_platforms = request.POST.getlist('social_platform[]')
        social_urls = request.POST.getlist('social_url[]')
        company.update_details(
            company_name=company_name,
            company_description=company_description,
            company_email=company_email,
            company_phone=company_phone,
            company_website=company_website,
            company_address=company_address,
            company_founded_date=company_founded_date,
            company_logo_file=company_logo_file,
            social_media_links_json=social_media_links_json,
            social_platforms=social_platforms,
            social_urls=social_urls,
        )
        company.save()
        messages.success(request, 'Company details updated successfully!')
        return redirect('about_company')
    elif request.method == 'POST':
        print(f"POST request received but user role '{user_role}' not authorized")
        messages.error(request, 'You do not have permission to update company details.')
        return redirect('about_company')
    
    context = {
        'company': company,
        'user_role': user_role,
        'active_page': 'about_company',
    }
    return render(request, 'admin/about/index.html', context)

def employee_company_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session.get('user_role') == 'admin':
        return redirect('admin_statistics')
    company = companyDetails.get_instance()
    user_role = request.session.get('user_role', 'employee')
    return render(request, 'employee/aboutcompany/index.html', {
        'company': company,
        'user_role': user_role,
        'active_page': 'employee_company_profile'
    })

def employee_profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    if request.session.get('user_role') == 'admin':
        return redirect('admin_statistics')
    signup_user = users.objects.get(id=request.session['user_id'])
    user_role = request.session.get('user_role', 'employee')

    
    # Get or create employee profile
    profile, created = employee_details.objects.get_or_create(user=signup_user)
    designations = employee_designation.objects.filter(user=signup_user)
    if request.method == 'POST':
        # Update profile fields
        profile.contact_number = request.POST.get('contact_number')
        profile.address = request.POST.get('address')
        profile.bio = request.POST.get('bio')
        profile.gender = request.POST.get('gender')
        profile.emergency_contact_number = request.POST.get('emergency_contact_number')
        profile.city = request.POST.get('city')
        
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
        'active_page': 'employee_profile',
        'designations': designations,
    }
    return render(request, 'employee/profile/index.html', context)

def get_task_comments(request, task_id):
    if 'user_id' not in request.session:
        print("Error: User not authenticated")
        return JsonResponse({'error': 'Not authenticated'}, status=401)
        
    try:
        print(f"Fetching comments for task {task_id}")
        
        # First verify the task exists
        try:
            task = tasks.objects.get(id=task_id)
        except tasks.DoesNotExist:
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
        signup_user = users.objects.get(id=request.session['user_id'])
        project = projects.objects.get(id=project_id)
        
        # Check if any tasks in this project have unread messages
        has_unread = False
        project_tasks = tasks.objects.filter(project=project)
        
        for task in project_tasks:
            last_read_status = read_status.objects.filter(user=signup_user, task=task).first()
            latest_comment = ChatMessage.objects.filter(task=task).order_by('-timestamp').first()
            
            if latest_comment:
                if (not last_read_status or latest_comment.timestamp > last_read_status.last_read_at) and \
                   latest_comment.user != signup_user:
                    has_unread = True
                    break
        
                return JsonResponse({'has_unread': has_unread})
        
    except (projects.DoesNotExist, users.DoesNotExist):
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
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    try:
        signup_user = users.objects.get(id=request.session['user_id'])
    except users.DoesNotExist:
        return JsonResponse({'tasks': []})

    pending_tasks = tasks.objects.filter(status=0, assigned_to=signup_user).order_by('-id')
    tasks_data = []
    for task in pending_tasks:
        tasks_data.append({
            'id': task.id,
            'task_name': task.task_name,
            'project': task.project.name if task.project else '',
            'project_id': task.project.id if task.project else '',
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
            task = tasks.objects.get(id=task_id)
            if task.status == 0:
                task.status = 3
                task.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Task cannot be started from current status.'}, status=400)
        except tasks.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)
    return JsonResponse({'error': 'Invalid request.'}, status=400)

def ongoing_tasks_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    try:
        signup_user = users.objects.get(id=request.session['user_id'])
    except users.DoesNotExist:
        return JsonResponse({'tasks': []})

    # Always show only the user's own ongoing tasks, regardless of role
    ongoing_tasks = tasks.objects.filter(
        assigned_to=signup_user,
        status__in=[1, 3]
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
        task = tasks.objects.get(id=task_id)
        return JsonResponse({'success': True, 'report': task.report or ''})
    except tasks.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)
def get_task_file(request, task_id):
    try:
        task = tasks.objects.get(id=task_id)
        file_url = task.task_file.url if task.task_file else ''
        file_name = task.task_file.name.split('/')[-1] if task.task_file else ''
        return JsonResponse({'success': True, 'file_url': file_url, 'file_name': file_name})
    except tasks.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

def approval_pending_tasks_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'tasks': []})
    user_role = request.session.get('user_role', 'employee')
    try:
        signup_user = users.objects.get(id=request.session['user_id'])
    except users.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    try:
        if user_role in ['teamlead', 'project_manager']:
            user_department_obj = signup_user.department
            if user_department_obj:
                tasks_qs = tasks.objects.filter(
                    project__department=user_department_obj,
                    status=5
                ).select_related('project', 'assigned_to')
            else:
                tasks_qs = tasks.objects.none()
        else:
            tasks_qs = tasks.objects.filter(
                assigned_to=signup_user,
                status=5
            ).select_related('project')

        tasks_data = []
        for task in tasks_qs:
            tasks_data.append({
                'id': task.id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'project_name': task.project.name if task.project else '',
                'project_id': task.project.id if task.project else '',
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
        project = projects.objects.get(id=project_id)
        # Filter employees by department using employee_details
        employees = users.objects.filter(employee_details__department=project.department)
        employee_list = [
            {
                'id': emp.id,
                'name': f"{emp.first_name} {emp.last_name}".strip() or emp.username
            }
            for emp in employees
        ]
        return JsonResponse({'employees': employee_list})
    except projects.DoesNotExist:
        return JsonResponse({'employees': []})

@require_GET
@csrf_exempt
def employee_today_stats_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    signup_user = users.objects.get(id=request.session['user_id'])
    user_department = signup_user
    today = timezone.now().date()
    total_time_today = task_activity_log.get_user_total_time_today(user_department)
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    tasks_done_today = tasks.objects.filter(
        assigned_to=signup_user,
        status=2,
        submitted_on__gte=start_of_day,
        submitted_on__lte=end_of_day
    ).count()
    tasks_expiring_today = tasks.objects.filter(
        due_date=today,
        assigned_to=signup_user
    ).exclude(status=2).count()
    expired_tasks = tasks.objects.filter(
        due_date__lt=today,
        assigned_to=signup_user
    ).exclude(status=2).count()
    return JsonResponse({
        'total_time_today': total_time_today,
        'tasks_done_today': tasks_done_today,
        'tasks_expiring_today': tasks_expiring_today,
        'expired_tasks': expired_tasks
    })

@require_GET
def employee_notifications_json(request):
    if 'user_id' not in request.session:
        return JsonResponse({'notifications': []}, status=401)
    try:
        user = users.objects.get(id=request.session['user_id'])
        notifications = Notification.objects.filter(user=user).order_by('-timestamp')
        notifications_data = [
            {
                'id': n.id,
                'message': n.message,
                'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M'),
                'is_read': n.is_read
            }
            for n in notifications
        ]
        return JsonResponse({'notifications': notifications_data})
    except Exception as e:
        return JsonResponse({'notifications': [], 'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def mark_notifications_read(request):
    if 'user_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    try:
        user = users.objects.get(id=request.session['user_id'])
        try:
            data = json.loads(request.body.decode('utf-8'))
            notification_ids = data.get('notification_ids', None)
        except Exception:
            notification_ids = None
        if notification_ids:
            Notification.objects.filter(user=user, id__in=notification_ids, is_read=False).update(is_read=True)
        else:
            Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def allNotificaations(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = users.objects.get(id=request.session['user_id'])
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')
    
    context = {
        'notifications': notifications,
        'user_role': request.session.get('user_role', 'employee'),
        # 'active_page': 'all_notifications'
    }
    return render(request, 'employee/notifications/index.html', context)

#read all notifications
@require_POST
def readAllNotifications(request):
    print("=== readAllNotifications view called ===")
    print(f"Request method: {request.method}")
    print(f"Session user_id: {request.session.get('user_id', 'NOT FOUND')}")
    
    # Use session-based user lookup for consistency
    if 'user_id' not in request.session:
        print("ERROR: No user_id in session")
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    try:
        user = users.objects.get(id=request.session['user_id'])
        print(f"Found user: {user.username} (ID: {user.id})")
        
        # Count unread notifications before update
        unread_count_before = Notification.objects.filter(user=user, is_read=False).count()
        print(f"Unread notifications before update: {unread_count_before}")
        
        # Update notifications
        updated_count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        print(f"Marked {updated_count} notifications as read")
        
        # Count unread notifications after update
        unread_count_after = Notification.objects.filter(user=user, is_read=False).count()
        print(f"Unread notifications after update: {unread_count_after}")
        
        print("=== readAllNotifications view completed successfully ===")
        return JsonResponse({'success': True, 'updated_count': updated_count})
        
    except users.DoesNotExist:
        print(f"ERROR: User with ID {request.session['user_id']} does not exist")
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        print(f"ERROR in readAllNotifications: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


#delete task by teamlead or project manager

def admin_notifications_json(request):
    if 'user_id' not in request.session or request.session.get('user_role') != 'admin':
        return JsonResponse({'notifications': []}, status=401)
    try:
        user = users.objects.get(id=request.session['user_id'])
        notifications = Notification.objects.filter(user=user).order_by('-timestamp')
        notifications_data = [
            {
                'id': n.id,
                'message': n.message,
                'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M'),
                'is_read': n.is_read
            }
            for n in notifications
        ]
        return JsonResponse({'notifications': notifications_data})
    except Exception as e:
        return JsonResponse({'notifications': [], 'error': str(e)}, status=500)

def adminAllNotifications(request):
    if 'user_id' not in request.session or request.session.get('user_role') != 'admin':
        return redirect('login')
    user = users.objects.get(id=request.session['user_id'])
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')
    # Do NOT mark as read here; this will be handled by JS after page load
    context = {
        'notifications': notifications,
        'user_role': 'admin',
    }
    return render(request, 'admin/notifications/index.html', context)



# employee profile on admin side 
def employee_profile_admin(request, user_id):
    if request.session['user_role'] in ['admin', 'manager']:
        try:
            context = employee_details.get_admin_profile_context(user_id)
        except users.DoesNotExist:
            messages.error(request, 'Employee not found.')
            return redirect('admin_statistics')
        return render(request, 'admin/employeeprofile/index.html', context)
    return redirect('login')

def admin_editing_emp_profile(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        department_id = request.POST.get('department')
        designation_codes = request.POST.getlist('designations')

        added_count, removed_count = employee_details.update_admin_profile(user_id, department_id, designation_codes)

        if added_count > 0 or removed_count > 0:
            print(f"Employee designations updated (Added: {added_count}, Removed: {removed_count}).")
        else:
            print("No changes to designations.")
        messages.success(request, "Employee profile updated successfully!")
        return redirect(reverse('employee-profile-admin', kwargs={'user_id': user_id}))

 