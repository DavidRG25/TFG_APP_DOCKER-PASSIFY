import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import containers.routing  # ← asegúrate de que containers tenga un routing.py

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paasify.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            containers.routing.websocket_urlpatterns
        )
    ),
})