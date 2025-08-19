from django.urls import re_path
from . import consumers

chat_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>[0-9a-fA-F-]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/video/room/(?P<room_id>[0-9a-fA-F-]+)/$', consumers.VideoConsumer.as_asgi()),
]