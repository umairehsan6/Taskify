from django.core.management.base import BaseCommand
from app.models import users
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seeds a default admin user (without department) if not present.'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = '1111'  # Change this after first login!
        first_name = 'Admin'
        last_name = 'User'

        if users.objects.filter(username=username, role='admin').exists():
            self.stdout.write(
                self.style.WARNING(f"Admin user '{username}' already exists. No action taken.")
            )
            return

        admin_user = users.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            role='admin',
            status=True,
            is_verified=True
        )
        self.stdout.write(
            self.style.SUCCESS(f"Admin user '{username}' created with password '{password}'. Please change this password after first login!")
        ) 