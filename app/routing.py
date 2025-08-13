from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/comments/(?P<task_id>\d+)/$", consumers.CommentConsumer.as_asgi()),
    re_path(r"ws/notifications/$", consumers.UserNotificationConsumer.as_asgi()),
]
