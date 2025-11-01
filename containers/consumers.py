import threading
import docker
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import Service

# Cliente de alto nivel y API de bajo nivel
_docker = docker.from_env()
_api = _docker.api


class TerminalConsumer(WebsocketConsumer):
    """
    WebSocket <-> /bin/sh dentro del contenedor Docker del servicio.
    Requiere que el usuario autenticado sea el owner del Service.
    """

    def connect(self):
        # /ws/terminal/<service_id>/
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")

        # Seguridad: solo el propietario puede abrir su terminal
        try:
            service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            self.close(code=4403)  # policy violation
            return

        if not service.container_id:
            # No hay contenedor corriendo
            self.accept()
            self.send("\r\n[ERROR] El servicio no está en ejecución.\r\n")
            self.close()
            return

        self.accept()

        try:
            # Creamos exec interactivo con TTY y STDIN
            exec_obj = _api.exec_create(
                container=service.container_id,
                cmd="/bin/sh",
                tty=True,
                stdin=True,
            )
            self.exec_id = exec_obj.get("Id")

            # Abrimos un socket bidireccional (TTY=True => no multiplexado)
            self.sock = _api.exec_start(
                self.exec_id,
                detach=False,
                tty=True,
                stream=False,
                socket=True,   # ← clave: nos devuelve un socket
            )

            # Lector asíncrono desde Docker → WebSocket
            self._reader_thread = threading.Thread(
                target=self._read_from_container,
                name=f"ws-docker-reader-{self.exec_id}",
                daemon=True,
            )
            self._reader_thread.start()

            # Mensaje de bienvenida
            self.send("Conexión establecida. Escribe comandos.\r\n")

        except Exception as e:
            self.send(f"\r\n[ERROR al iniciar shell]: {e}\r\n")
            self.close()

    def receive(self, text_data=None, bytes_data=None):
        """Datos del navegador → contenedor."""
        try:
            if getattr(self, "sock", None) is None:
                return
            data = bytes_data if bytes_data is not None else (text_data or "")
            if isinstance(data, str):
                data = data.encode("utf-8", errors="ignore")
            # Enviar tal cual (TTY=True no va multiplexado)
            self.sock.send(data)
        except Exception:
            # Evitar romper la conexión por excepciones menores de envío
            pass

    def _read_from_container(self):
        """Lee del socket Docker y manda al WebSocket."""
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                try:
                    self.send(chunk.decode("utf-8", errors="ignore"))
                except Exception:
                    # Si no puede decodificar, manda binario como texto seguro
                    self.send(str(chunk))
        except Exception as e:
            try:
                self.send(f"\r\n[ERROR OUTPUT]: {e}\r\n")
            except Exception:
                pass
        finally:
            # Cerrar desde lado servidor si termina el exec
            try:
                self.close()
            except Exception:
                pass

    def disconnect(self, close_code):
        """Limpieza de recursos."""
        try:
            if getattr(self, "sock", None) is not None:
                try:
                    self.sock.shutdown(2)  # SHUT_RDWR
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
        finally:
            self.sock = None