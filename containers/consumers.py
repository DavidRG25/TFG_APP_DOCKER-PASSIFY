import logging
import threading
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer
from django.http import Http404
from django.shortcuts import get_object_or_404

from docker.errors import DockerException

from .docker_client import get_docker_client
from .models import Service, ServiceContainer

logger = logging.getLogger(__name__)


class TerminalConsumer(WebsocketConsumer):
    """
    Canal WebSocket que expone una shell simple dentro del contenedor.
    
    MODO SIMPLE: Usa service.container_id (comportamiento anterior)
    MODO COMPOSE: Si se pasa ?container=<id>, usa ese ServiceContainer
    """

    def connect(self):
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._reader_thread = None
        self.sock = None

        from .views import user_is_admin, user_is_teacher
        try:
            if user_is_admin(user) or user_is_teacher(user):
                service = get_object_or_404(Service, pk=service_id)
            else:
                service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            self.close(code=4403)
            return

        # Determinar qué contenedor usar
        container_id_to_use = None
        container_name = "servicio"
        
        # Parsear query string para obtener parámetro container
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        container_param = query_params.get("container", [None])[0]
        
        if container_param:
            # Modo compose: usar ServiceContainer específico
            try:
                container_record = ServiceContainer.objects.get(pk=container_param, service=service)
                container_id_to_use = container_record.container_id
                container_name = container_record.name
            except ServiceContainer.DoesNotExist:
                self.accept()
                self.send("\r\n[ERROR] Contenedor no encontrado.\r\n")
                self.close()
                return
        else:
            # Modo simple: usar service.container_id (comportamiento anterior)
            container_id_to_use = service.container_id
        
        if not container_id_to_use:
            self.accept()
            self.send("\r\n[ERROR] El servicio no esta en ejecucion.\r\n")
            self.close()
            return

        self.accept()

        docker_client = get_docker_client()
        if docker_client is None:
            self.send("\r\n[ERROR] Docker no esta disponible actualmente.\r\n")
            self.close()
            return

        try:
            api = docker_client.api
            exec_obj = api.exec_create(
                container=container_id_to_use,
                cmd="/bin/sh",
                tty=True,
                stdin=True,
            )
            self.exec_id = exec_obj.get("Id")

            self.sock = api.exec_start(
                self.exec_id,
                detach=False,
                tty=True,
                stream=False,
                socket=True,
            )

            self._reader_thread = threading.Thread(
                target=self._read_from_container,
                name=f"ws-docker-reader-{self.exec_id}",
                daemon=True,
            )
            self._reader_thread.start()

            self.send(f"Conexión establecida con {container_name}.\r\n")
        except (DockerException, Exception) as exc:  # pragma: no cover - dependencias externas
            self.send(f"\r\n[ERROR al iniciar shell]: {exc}\r\n")
            self.close()

    def _get_raw_socket(self):
        if not self.sock:
            return None
        return getattr(self.sock, "_sock", self.sock)

    def receive(self, text_data=None, bytes_data=None):
        """Datos que llegan desde el navegador hacia el contenedor."""
        try:
            sock = self._get_raw_socket()
            if not sock:
                return
            data = bytes_data if bytes_data is not None else (text_data or "")
            if isinstance(data, str):
                data = data.encode("utf-8", errors="ignore")
            send_fn = getattr(sock, "sendall", None) or getattr(sock, "send", None)
            if send_fn:
                send_fn(data)
        except Exception:
            # Evitamos propagar ruidos de red al cliente.
            pass

    def _read_from_container(self):
        """Transfiere la salida del contenedor hacia el navegador."""
        try:
            sock = self._get_raw_socket()
            if not sock:
                return
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    logger.info("Terminal WS: container socket closed.")
                    self.send("\r\n[CONEXION CERRADA] El contenedor finalizó la sesión.\r\n")
                    break
                logger.debug(f"Terminal WS: recv {chunk!r}")
                try:
                    decoded = chunk.decode("utf-8")
                    self.send(text_data=decoded)
                    logger.debug(f"Terminal WS: sent {decoded!r}")
                except UnicodeDecodeError:
                    self.send(bytes_data=chunk)
                    logger.debug(f"Terminal WS: sent raw bytes")
        except Exception as exc:
            logger.error(f"Terminal WS: error reading from container: {exc}")
            try:
                self.send(text_data=f"\r\n[ERROR OUTPUT]: {exc}\r\n")
            except Exception:
                pass
        finally:
            try:
                self.close()
            except Exception:
                pass

    def disconnect(self, close_code):
        """Limpieza de recursos al cerrar la sesion WebSocket."""
        try:
            sock = self._get_raw_socket()
            if sock is not None:
                try:
                    sock.shutdown(2)
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
        finally:
            self.sock = None
            if self._reader_thread and self._reader_thread.is_alive():
                self._reader_thread.join(timeout=1)
            self._reader_thread = None
