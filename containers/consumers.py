import threading

from channels.generic.websocket import WebsocketConsumer
from django.http import Http404
from django.shortcuts import get_object_or_404

from docker.errors import DockerException

from .docker_client import get_docker_client
from .models import Service


class TerminalConsumer(WebsocketConsumer):
    """Canal WebSocket que expone una shell simple dentro del contenedor."""

    def connect(self):
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._reader_thread = None
        self.sock = None

        try:
            service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            self.close(code=4403)
            return

        if not service.container_id:
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
                container=service.container_id,
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

            self.send("Conexion establecida. Escribe comandos.\r\n")
        except (DockerException, Exception) as exc:  # pragma: no cover - dependencias externas
            self.send(f"\r\n[ERROR al iniciar shell]: {exc}\r\n")
            self.close()

    def receive(self, text_data=None, bytes_data=None):
        """Datos que llegan desde el navegador hacia el contenedor."""
        try:
            if not self.sock:
                return
            data = bytes_data if bytes_data is not None else (text_data or "")
            if isinstance(data, str):
                data = data.encode("utf-8", errors="ignore")
            self.sock.send(data)
        except Exception:
            # Evitamos propagar ruidos de red al cliente.
            pass

    def _read_from_container(self):
        """Transfiere la salida del contenedor hacia el navegador."""
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                try:
                    self.send(chunk.decode("utf-8", errors="ignore"))
                except Exception:
                    self.send(str(chunk))
        except Exception as exc:
            try:
                self.send(f"\r\n[ERROR OUTPUT]: {exc}\r\n")
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
            if self.sock is not None:
                try:
                    self.sock.shutdown(2)
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
        finally:
            self.sock = None
            if self._reader_thread and self._reader_thread.is_alive():
                self._reader_thread.join(timeout=1)
            self._reader_thread = None
