# containers/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/terminal/<int:service_id>/", consumers.TerminalConsumer.as_asgi()),
    path("ws/terminal-v2/<int:service_id>/", consumers.DockerTerminalConsumer.as_asgi()),  # Nueva terminal mejorada
    path("ws/logs-stream/<int:service_id>/", consumers.LogsStreamConsumer.as_asgi()),  # Logs en vivo
]
