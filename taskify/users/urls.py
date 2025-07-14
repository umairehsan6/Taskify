from django.urls import path
from . import views

urlpatterns = [
    # path('register/', views.Register, name='register'),  
    path('', views.Login, name='login'),   
    path('logout/', views.Logout, name='logout'),
    path('toggle-status/<int:user_id>/', views.ToggleUserStatus, name='toggle_status'), 
    path('promote-user/<int:user_id>/<str:new_role>/', views.PromoteUser, name='promote_user'), 
    path('register-user-by-admin/', views.Register_UserbyAdmin, name='register_user_by_admin'),
    path('verify-otp/', views.VerifyOTP, name='verify_otp'),
    path('forgot-password/', views.ForgetPassword, name='forgot_password'),
    path('confirm-newpass/', views.ConfirmNewPassword, name='confirm_newpass'),
]