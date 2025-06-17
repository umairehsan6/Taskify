from django.db import models
import random
from django.utils import timezone
# Create your models here.
class SignupUser(models.Model):
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

    def __str__(self):
        return self.username
class UserVerification(models.Model):
    user = models.OneToOneField(SignupUser, on_delete=models.CASCADE, related_name='verification')
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def generate_verification_code(self):
        raw_otp = random.randint(100000, 999999)
        self.verification_code = str(raw_otp)  # Convert to string for consistency
        self.created_at = timezone.now()
        self.attempts = 0
        self.save()
        return raw_otp
    
    def is_code_expired(self):
        return self.created_at + timezone.timedelta(minutes=2) < timezone.now()
    
    def is_code_valid(self, entered_code):
        if str(self.verification_code) == str(entered_code):
            self.attempts = 0
            self.save()
            return True
        else:
            self.attempts += 1
            self.save()
            return False
    
    def is_max_attempts_reached(self):
        return self.attempts >= 3
    
    
    
        
