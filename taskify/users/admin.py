from django.contrib import admin

# Register your models here.
from .models import SignupUser , UserVerification

class SignupUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'username', 'email', 'role')
    search_fields = ('first_name', 'last_name', 'username', 'email')
admin.site.register(SignupUser, SignupUserAdmin)

class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_code', 'created_at', 'attempts')
admin.site.register(UserVerification, UserVerificationAdmin)
