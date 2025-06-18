import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chat.routing

# Ensures settings are properly loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles traditional HTTP
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.chat_urlpatterns  # Your websocket routes
        )
    ),
})
