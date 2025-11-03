# containers/routing.py
from django.urls import path
from .consumers import TerminalConsumer

# Rutas WebSocket de la app "containers"
# Deben ser incluidas en app_passify/asgi.py dentro de URLRouter(...)
websocket_urlpatterns = [
    path("ws/terminal/<int:service_id>/", TerminalConsumer.as_asgi()),
]