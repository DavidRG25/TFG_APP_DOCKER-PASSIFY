import threading
import socket
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
    WebSocket <-> shell interactivo dentro del contenedor Docker del servicio.
    Requiere que el usuario autenticado sea el owner del Service.
    """

    def _pick_shell(self, container_id: str) -> str:
        """
        Intenta encontrar un shell utilizable dentro del contenedor.
        Orden de prueba: /bin/sh, /bin/bash, powershell, cmd.exe
        Devuelve el comando como string.
        """
        candidates = ["/bin/sh", "/bin/bash", "powershell", "cmd.exe"]
        for cmd in candidates:
            try:
                # Probar a crear un exec "echo ok" con cmd; si falla, probamos el siguiente
                probe = _api.exec_create(container=container_id, cmd=[cmd, "-c", "echo ok"] if "sh" in cmd or "bash" in cmd else cmd)
                _api.exec_start(probe, tty=True, stream=False)
                return cmd
            except Exception:
                continue
        # Último recurso: /bin/sh (muchas imágenes mínimas lo tienen)
        return "/bin/sh"

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

        # Verificar que el contenedor existe y está running
        if not service.container_id:
            self.accept()
            self.send(text_data="\r\n[ERROR] El servicio no está en ejecución (sin container_id).\r\n")
            self.close()
            return

        try:
            container = _docker.containers.get(service.container_id)
            container.reload()
            if container.status != "running":
                self.accept()
                self.send(text_data=f"\r\n[ERROR] El contenedor existe pero no está en ejecución (estado: {container.status}).\r\n")
                self.close()
                return
        except Exception as e:
            self.accept()
            self.send(text_data=f"\r\n[ERROR] No se pudo acceder al contenedor: {e}\r\n")
            self.close()
            return

        # Ya podemos aceptar la conexión WS
        self.accept()

        try:
            shell_cmd = self._pick_shell(service.container_id)

            # Crear exec interactivo con TTY y STDIN
            # Nota: cuando tty=True, el stream no va multiplexado (no hay cabeceras de multiplexado).
            if shell_cmd in ("powershell", "cmd.exe"):
                exec_obj = _api.exec_create(
                    container=service.container_id,
                    cmd=shell_cmd,
                    tty=True,
                    stdin=True,
                )
            else:
                exec_obj = _api.exec_create(
                    container=service.container_id,
                    cmd=shell_cmd,
                    tty=True,
                    stdin=True,
                    env={"TERM": "xterm"},
                )

            self.exec_id = exec_obj.get("Id")

            # Abrimos un socket bidireccional
            self.sock = _api.exec_start(
                self.exec_id,
                detach=False,
                tty=True,
                stream=False,
                socket=True,  # devuelve un socket tipo docker-tcp
            )

            # Poner timeout para permitir cierre limpio
            if isinstance(self.sock, socket.socket):
                try:
                    self.sock.settimeout(1.0)
                except Exception:
                    pass

            # Estado de control
            self._alive = True

            # Lector asíncrono desde Docker → WebSocket
            self._reader_thread = threading.Thread(
                target=self._read_from_container,
                name=f"ws-docker-reader-{self.exec_id}",
                daemon=True,
            )
            self._reader_thread.start()

            # Mensaje de bienvenida
            self.send(text_data=f"Conexión establecida. Shell: {shell_cmd}\r\n")

        except Exception as e:
            self.send(text_data=f"\r\n[ERROR al iniciar shell]: {e}\r\n")
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
            while self._alive and getattr(self, "sock", None) is not None:
                try:
                    chunk = self.sock.recv(4096)
                except socket.timeout:
                    continue
                except Exception as e:
                    # Errores de lectura: salir del bucle
                    try:
                        self.send(text_data=f"\r\n[ERROR OUTPUT]: {e}\r\n")
                    except Exception:
                        pass
                    break

                if not chunk:
                    break

                try:
                    self.send(text_data=chunk.decode("utf-8", errors="ignore"))
                except Exception:
                    # Si no puede decodificar, manda representación segura
                    self.send(text_data=str(chunk))
        finally:
            # Cerrar desde lado servidor si termina el exec
            try:
                self.close()
            except Exception:
                pass

    def disconnect(self, close_code):
        """Limpieza de recursos."""
        self._alive = False
        try:
            if getattr(self, "sock", None) is not None:
                try:
                    # SHUT_RDWR = 2, puede lanzar si no es socket real
                    if isinstance(self.sock, socket.socket):
                        self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
        finally:
            self.sock = None