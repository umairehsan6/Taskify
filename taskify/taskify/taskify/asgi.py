import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskify.settings')

application = get_asgi_application()
# The above code sets up the ASGI application for the Django project, allowing it to handle both HTTP and WebSocket protocols. 