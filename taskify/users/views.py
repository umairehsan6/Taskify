from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from .models import SignupUser, UserVerification
from dashboard.models import Department, UserDepartment
from django.core.mail import send_mail

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
            elif SignupUser.objects.filter(email=email).exists():
                message = "This email is already registered."
            elif SignupUser.objects.filter(username=username).exists():
                message = "This username is already taken."
            else:
                hashed_password = make_password(password)
                signup_user = SignupUser.objects.create(
                    first_name=fname,
                    last_name=lname,
                    username=username,
                    email=email,
                    password=hashed_password,
                    role='employee',
                )
                signup_user.is_verified = False
                signup_user.save()
                otp_obj , created = UserVerification.objects.get_or_create(user=signup_user)
                raw_otp = otp_obj.generate_verification_code()
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
    return render(request, 'users/register.html', {'message': message})

def VerifyOTP(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')
    user = SignupUser.objects.get(id=user_id)
    otp_obj = UserVerification.objects.get(user=user)
    if user.is_verified:
        if otp_obj.is_code_expired():
            otp_obj.delete()
            messages.error(request, "OTP is expired")
            return redirect('forgot-password')
        
        if request.method == 'POST':
            entered_otp = request.POST.get('otp')
            if otp_obj.is_max_attempts_reached():
                otp_obj.delete()
                messages.error(request, 'You have exceeded the number of attempts. Please Try Again Later')
                return redirect('register')
                
            if otp_obj.is_code_valid(entered_otp):
                otp_obj.delete()
                messages.success(request, "PLease Enter Your New Password")
                return redirect('confirm_newpass')
            else:
                otp_obj.save()
                messages.error(request, 'Invalid OTP')
    
    elif not user.is_verified:
        if request.method == 'POST':
            entered_otp = request.POST.get('otp')
            if otp_obj.is_max_attempts_reached():
                otp_obj.delete()
                user.delete()
                messages.error(request, 'You have exceeded the number of attempts. Please register again')
                return redirect('register')
                
            if otp_obj.is_code_valid(entered_otp):
                user.is_active = True
                user.is_verified = True
                user.save()
                otp_obj.delete()
                messages.success(request, "Account successfully created.")
                return redirect('login')
            else:
                otp_obj.save()
                messages.error(request, 'Invalid OTP')
    return render(request, 'users/otp.html' ,)

    


def Register_UserbyAdmin(request):
    if request.session['user_role'] in ['admin', 'manager']:
        departments = Department.objects.all()
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            role = request.POST.get('role')
            department_id = request.POST.get('department')  # This can be empty
            
            if password == confirm_password:
                if User.objects.filter(email=email).exists():
                    message = "This email is already registered as a superuser or staff user."
                elif SignupUser.objects.filter(email=email).exists():
                    message = "This email is already registered."
                elif SignupUser.objects.filter(username=username).exists():
                    message = "This username is already taken."
                else:
                    hashed_password = make_password(password)
                    signup_user = SignupUser.objects.create(
                        first_name=fname,
                        last_name=lname,
                        username=username,
                        email=email,
                        password=hashed_password,
                        role=role,
                    )
                    signup_user.save()
                    
                    # Create the user-department relationship only if a department was selected
                    if department_id:
                        try:
                            department_obj = Department.objects.get(id=department_id)
                            UserDepartment.objects.create(
                                user=signup_user,
                                department=department_obj
                            )
                        except Department.DoesNotExist:
                            messages.warning(request, "Selected department does not exist. User created without department assignment.")
                    
                    messages.success(request, "User successfully created.")
                    # Maintain the current user's role in session
                    request.session['user_role'] = request.session['user_role']
                    return redirect('dashboard')
            else:
                message = "Passwords do not match."
            return render(request, 'users/add-user.html' ,{
                'departments': departments,
                'message': message,
                'roles': SignupUser.ROLE_CHOICES,
            })
        return render(request, 'users/add-user.html', {
            'departments': departments,
            'message': None,
            'roles': SignupUser.ROLE_CHOICES,
        })
    else:
        return redirect('login')
    
def Login(request):
    message = None
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password')
        signup_user = SignupUser.objects.filter(username=username).first()
        if signup_user:
            if not signup_user.status:  
                message = "Your account is disabled by the admin."
            elif check_password(password, signup_user.password):  
                request.session['user_id'] = signup_user.id
                request.session['username'] = signup_user.username
                request.session['user_role'] = signup_user.role 
                if signup_user.role == 'admin' or signup_user.role == 'manager':
                    return redirect('admin_statistics')
                else:
                    return redirect('new_employee_dashboard')  
            else:
                message = "Invalid username or password."
        else:
            message = "Invalid username or password."
    return render(request, 'users/login.html', {'message': message})

def ForgetPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = SignupUser.objects.get(email=email)
            if user:
                otp_obj, created = UserVerification.objects.get_or_create(user=user)
                raw_otp = otp_obj.generate_verification_code()
                send_mail(
                    subject='Password Reset OTP',
                    message=f'Your OTP for password reset is {raw_otp} if you did not request this, please ignore this email.',
                    from_email='arshadotpwala@gmail.com',
                    recipient_list=[email],
                )
                request.session['user_id'] = user.id
                messages.success(request, "OTP has been sent to your email.")
                return redirect('verify_otp')
        except SignupUser.DoesNotExist:
            messages.error(request, "User does not exist.")
    return render(request, 'users/forget-password.html')

def ConfirmNewPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.session.get('user_id')
        if password == confirm_password:
            user = SignupUser.objects.get(id=user_id)
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password updated successfully.")
            return redirect('login')
    return render(request, 'users/confirm-newpass.html')

def Logout(request):
    request.session.flush()
    return redirect('login')

def ToggleUserStatus(request, user_id):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  # Use 'user_role'
        try:
            user = SignupUser.objects.get(id=user_id)
            if user.role == 'admin':  # Prevent disabling admins
                messages.error(request, "You cannot disable an admin.")
            else:
                user.status = not user.status  # Toggle the status
                user.save()
                messages.success(request, f"{user.username}'s status has been updated.")
        except SignupUser.DoesNotExist:
            messages.error(request, "User does not exist.")
    else:
        messages.error(request, "You do not have permission to perform this action.")
    return redirect('dashboard')

def PromoteUser(request, user_id, new_role):
    if 'user_role' in request.session and request.session['user_role'] in ['admin', 'manager']:  # Use 'user_role'
        try:
            user = SignupUser.objects.get(id=user_id)
            if user.role == 'admin':  # Prevent demoting an admin
                messages.error(request, "You cannot demote an admin.")
            elif new_role in dict(SignupUser.ROLE_CHOICES):  # Validate the role
                user.role = new_role  # Update the user's role
                user.save()
                messages.success(request, f"{user.username} has been promoted to {new_role.replace('_', ' ').capitalize()}.")
            else:
                messages.error(request, "Invalid role.")
        except SignupUser.DoesNotExist:
            messages.error(request, "User does not exist.")
    else:
        messages.error(request, "You do not have permission to perform this action.")
    return redirect('dashboard')