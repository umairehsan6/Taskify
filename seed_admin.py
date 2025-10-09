from django.core.management.base import BaseCommand
from app.models import users
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seeds a default admin user (without department) if not present.'

    def handle(self, *args, **options):
        username = 'teamlead'
        email = 'admin12@example.com'
        password = '1111'  # Change this after first login!
        first_name = 'Teamlead'
        last_name = 'User'

        if users.objects.filter(username=username, role='teamlead').exists():
            self.stdout.write(
                self.style.WARNING(f"Teamlead user '{username}' already exists. No action taken.")
            )
            return

        admin_user = users.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            role='teamlead',
            status=True,
            is_verified=True
        )
        self.stdout.write(
            self.style.SUCCESS(f"Teamlead user '{username}' created with password '{password}'. Please change this password after first login!")
        ) 