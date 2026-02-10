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


# ============================================================================
# DEPRECATED: TerminalConsumer antiguo - Usar DockerTerminalConsumer
# Se mantiene temporalmente para compatibilidad, pero se eliminará en v6.2.0
# ============================================================================

class TerminalConsumer(WebsocketConsumer):
    """
    Canal WebSocket que expone una shell simple dentro del contenedor.
    
    DEPRECATED: Usar DockerTerminalConsumer en su lugar.
    
    MODO SIMPLE: Usa service.container_id (comportamiento anterior)
    MODO COMPOSE: Si se pasa ?container=<id>, usa ese ServiceContainer
    """

    def connect(self):
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._reader_thread = None
        self.sock = None
        self.command_buffer = ""  # Buffer para acumular comandos

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
                # Si llega un Enter, analizamos lo acumulado ANTES de enviarlo
                if '\r' in data or '\n' in data:
                    import re
                    # Limpiamos caracteres de control comunes en terminales para el regex
                    clean_command = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', self.command_buffer)
                    command_lower = clean_command.lower().strip()
                    
                    DANGEROUS_PATTERNS = [
                        (r'rm\s+-rf\s+/', 'rm -rf / (borrado raíz)'),
                        (r'rm\s+-rf\s+/\*', 'rm -rf /* (borrado contenido)'),
                        (r'rm\s+-rf\s+~', 'rm -rf ~ (borrado home)'),
                        (r'rm\s+-r?f?\s+/', 'rm -rf / (variante)'),
                        (r'dd\s+if=/dev/(zero|random)', 'dd destructivo'),
                        (r'mkfs\.' , 'formateo de disco'),
                        (r'fork\(\)', 'fork bomb'),
                        (r':\(\)\{.*:\|:.*\}', 'fork bomb bash'),
                        (r'wget\s+https?://', 'descarga externa (wget)'),
                        (r'curl\s+https?://', 'descarga externa (curl)'),
                        (r'nc\s+-l', 'netcat listener'),
                        (r'ncat\s+-l', 'ncat listener'),
                        (r'/dev/tcp/', 'conexión TCP directa'),
                        (r'>\s*/dev/sd[a-z]', 'escritura directa a disco'),
                        (r'chmod\s+777\s+/', 'permisos peligrosos en raíz'),
                    ]
                    
                    for pattern, description in DANGEROUS_PATTERNS:
                        if re.search(pattern, command_lower):
                            # 1. Avisar al usuario en rojo
                            self.send(text_data=f"\r\n\033[1;31m[BLOQUEADO] Comando peligroso detectado: {description}\033[0m\r\n")
                            # 2. Loggear en el servidor
                            logger.warning(f"SEGURIDAD: Bloqueado '{description}' de Usuario: {self.scope.get('user')}")
                            # 3. CANCELAR el comando en el contenedor enviando CTRL+C (\x03)
                            # Esto limpia la línea del shell del contenedor sin ejecutar el Enter que está llegando
                            send_fn = getattr(sock, "sendall", None) or getattr(sock, "send", None)
                            if send_fn:
                                send_fn(b"\x03")
                            # 4. Limpiar buffer y SALIR sin enviar el Enter (\r)
                            self.command_buffer = ""
                            return

                    # Si es seguro, limpiamos buffer para el siguiente
                    self.command_buffer = ""
                
                # Manejo de Backspace para el buffer local
                elif data == '\x7f' or data == '\x08':
                    self.command_buffer = self.command_buffer[:-1]
                else:
                    self.command_buffer += data

                data = data.encode("utf-8", errors="ignore")
            
            # Enviar datos al contenedor (incluye el Enter si pasó el filtro anterior)
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


# ============================================================================
# NUEVO: DockerTerminalConsumer con PyXtermJS
# ============================================================================

class DockerTerminalConsumer(WebsocketConsumer):
    """
    Consumer WebSocket mejorado para terminal interactiva con PyXtermJS.
    
    Características:
    - Soporte para múltiples shells (/bin/bash, /bin/sh, /bin/ash)
    - Reconexión automática
    - Mejor manejo de errores
    - Timeout configurable
    - Logs detallados
    """
    
    SHELL_PRIORITY = ['/bin/bash', '/bin/sh', '/bin/ash', '/bin/zsh']
    TIMEOUT_SECONDS = 300  # 5 minutos sin actividad
    
    def connect(self):
        """Inicializar conexión WebSocket y ejecutar shell en contenedor"""
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._reader_thread = None
        self.sock = None
        self.last_activity = None
        
        # Verificar autenticación
        if not user or not user.is_authenticated:
            self.close(code=4401)
            return
        
        # Obtener servicio y verificar permisos
        from .views import user_is_admin, user_is_teacher
        try:
            if user_is_admin(user) or user_is_teacher(user):
                service = get_object_or_404(Service, pk=service_id)
            else:
                service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            logger.warning(f"Terminal: Usuario {user} intentó acceder a servicio {service_id} sin permisos")
            self.close(code=4403)
            return
        
        # Determinar contenedor a usar (simple o compose)
        container_id_to_use, container_name = self._get_container_info(service)
        
        if not container_id_to_use:
            self.accept()
            self.send(text_data="\r\n\033[1;31m[ERROR]\033[0m El servicio no está en ejecución.\r\n")
            self.close()
            return
        
        self.accept()
        
        # Verificar Docker disponible
        docker_client = get_docker_client()
        if docker_client is None:
            self.send(text_data="\r\n\033[1;31m[ERROR]\033[0m Docker no está disponible.\r\n")
            self.close()
            return
        
        # Detectar shell disponible y crear exec
        shell = self._detect_available_shell(docker_client, container_id_to_use)
        if not shell:
            self.send(text_data="\r\n\033[1;31m[ERROR]\033[0m No se encontró ningún shell disponible en el contenedor.\r\n")
            self.close()
            return
        
        try:
            api = docker_client.api
            exec_obj = api.exec_create(
                container=container_id_to_use,
                cmd=shell,
                tty=True,
                stdin=True,
                environment={"TERM": "xterm-256color"},
            )
            self.exec_id = exec_obj.get("Id")
            
            self.sock = api.exec_start(
                self.exec_id,
                detach=False,
                tty=True,
                stream=False,
                socket=True,
            )
            
            # Iniciar hilo de lectura
            self._reader_thread = threading.Thread(
                target=self._read_from_container,
                name=f"pyxterm-reader-{self.exec_id[:12]}",
                daemon=True,
            )
            self._reader_thread.start()
            
            # Mensaje de bienvenida
            welcome_msg = f"\033[1;32m✓ Conectado a {container_name}\033[0m\r\n"
            welcome_msg += f"\033[0;36mShell: {shell}\033[0m\r\n\r\n"
            self.send(text_data=welcome_msg)
            
            logger.info(f"Terminal: Usuario {user} conectado a {container_name} ({shell})")
            
        except (DockerException, Exception) as exc:
            logger.error(f"Terminal: Error al iniciar shell: {exc}")
            self.send(text_data=f"\r\n\033[1;31m[ERROR]\033[0m {exc}\r\n")
            self.close()
    
    def _get_container_info(self, service):
        """Obtener ID y nombre del contenedor (simple o compose)"""
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        container_param = query_params.get("container", [None])[0]
        
        if container_param:
            # Modo compose
            try:
                container_record = ServiceContainer.objects.get(pk=container_param, service=service)
                return container_record.container_id, container_record.name
            except ServiceContainer.DoesNotExist:
                return None, None
        else:
            # Modo simple
            return service.container_id, service.name
    
    def _detect_available_shell(self, docker_client, container_id):
        """Detectar qué shell está disponible en el contenedor"""
        for shell in self.SHELL_PRIORITY:
            try:
                # Probar si el shell existe
                exec_test = docker_client.api.exec_create(
                    container=container_id,
                    cmd=f"test -x {shell}",
                    tty=False,
                )
                result = docker_client.api.exec_start(exec_test['Id'], detach=False)
                inspect = docker_client.api.exec_inspect(exec_test['Id'])
                
                if inspect['ExitCode'] == 0:
                    logger.info(f"Terminal: Shell detectado: {shell}")
                    return shell
            except Exception:
                continue
        
        logger.warning(f"Terminal: No se encontró ningún shell en {self.SHELL_PRIORITY}")
        return None
    
    def _get_raw_socket(self):
        """Obtener socket raw"""
        if not self.sock:
            return None
        return getattr(self.sock, "_sock", self.sock)
    
    def receive(self, text_data=None, bytes_data=None):
        """Recibir datos del navegador y enviarlos al contenedor"""
        import time
        self.last_activity = time.time()
        
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
        except Exception as exc:
            logger.error(f"Terminal: Error enviando datos: {exc}")
    
    def _read_from_container(self):
        """Leer salida del contenedor y enviarla al navegador"""
        import time
        self.last_activity = time.time()
        
        try:
            sock = self._get_raw_socket()
            if not sock:
                return
            
            while True:
                # Verificar timeout
                if self.last_activity and (time.time() - self.last_activity) > self.TIMEOUT_SECONDS:
                    logger.info("Terminal: Timeout por inactividad")
                    self.send(text_data="\r\n\033[1;33m[TIMEOUT]\033[0m Sesión cerrada por inactividad.\r\n")
                    break
                
                chunk = sock.recv(4096)
                if not chunk:
                    logger.info("Terminal: Socket cerrado por el contenedor")
                    self.send(text_data="\r\n\033[1;33m[DESCONECTADO]\033[0m El contenedor cerró la conexión.\r\n")
                    break
                
                try:
                    decoded = chunk.decode("utf-8")
                    self.send(text_data=decoded)
                except UnicodeDecodeError:
                    self.send(bytes_data=chunk)
                    
        except Exception as exc:
            logger.error(f"Terminal: Error leyendo del contenedor: {exc}")
            try:
                self.send(text_data=f"\r\n\033[1;31m[ERROR]\033[0m {exc}\r\n")
            except Exception:
                pass
        finally:
            try:
                self.close()
            except Exception:
                pass
    
    def disconnect(self, close_code):
        """Limpiar recursos al desconectar"""
        logger.info(f"Terminal: Desconexión (code={close_code})")
        
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


# ============================================================================
# NUEVO: LogsStreamConsumer para logs en vivo
# ============================================================================

class LogsStreamConsumer(WebsocketConsumer):
    """
    Consumer WebSocket para streaming de logs en tiempo real.
    
    Características:
    - Seguimiento en vivo con `docker logs --follow`
    - Soporte para servicios Compose (múltiples contenedores)
    - Auto-reconexión
    - Control de pausa/reanudación
    """
    
    def connect(self):
        """Inicializar conexión y comenzar streaming"""
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._stream_thread = None
        self._stop_streaming = False
        
        # Verificar autenticación
        if not user or not user.is_authenticated:
            self.close(code=4401)
            return
        
        # Obtener servicio y verificar permisos
        from .views import user_is_admin, user_is_teacher
        try:
            if user_is_admin(user) or user_is_teacher(user):
                service = get_object_or_404(Service, pk=service_id)
            else:
                service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            logger.warning(f"Logs Stream: Usuario {user} sin permisos para servicio {service_id}")
            self.close(code=4403)
            return
        
        self.service = service
        self.accept()
        
        # Verificar Docker disponible
        docker_client = get_docker_client()
        if not docker_client:
            self.send(text_data="[ERROR] Docker no está disponible\n")
            self.close()
            return
        
        self.docker_client = docker_client
        
        # Iniciar streaming
        self._stream_thread = threading.Thread(
            target=self._stream_logs,
            name=f"logs-stream-{service_id}",
            daemon=True,
        )
        self._stream_thread.start()
        
        logger.info(f"Logs Stream: Iniciado para servicio {service_id} por usuario {user}")
    
    def _stream_logs(self):
        """Stream logs en tiempo real"""
        import time
        
        try:
            if self.service.has_compose:
                # Servicio Compose: stream de todos los contenedores
                containers = ServiceContainer.objects.filter(service=self.service).order_by('name')
                
                for container_record in containers:
                    if self._stop_streaming:
                        break
                    
                    if not container_record.container_id:
                        continue
                    
                    try:
                        container = self.docker_client.containers.get(container_record.container_id)
                        
                        # Enviar header
                        self.send(text_data=f"\n{'='*80}\n")
                        self.send(text_data=f"📦 CONTENEDOR: {container_record.name}\n")
                        self.send(text_data=f"{'='*80}\n\n")
                        
                        # Stream logs
                        for line in container.logs(stream=True, follow=True, tail=100):
                            if self._stop_streaming:
                                break
                            
                            try:
                                decoded = line.decode('utf-8')
                                self.send(text_data=decoded)
                            except UnicodeDecodeError:
                                self.send(text_data=line.decode('utf-8', errors='replace'))
                            
                            time.sleep(0.01)  # Evitar saturar
                    
                    except Exception as e:
                        logger.error(f"Logs Stream: Error en contenedor {container_record.name}: {e}")
                        self.send(text_data=f"[ERROR] {container_record.name}: {e}\n")
            
            else:
                # Servicio simple: un solo contenedor
                if not self.service.container_id:
                    self.send(text_data="[INFO] El servicio no tiene contenedor asignado\n")
                    return
                
                try:
                    container = self.docker_client.containers.get(self.service.container_id)
                    
                    # Stream logs
                    for line in container.logs(stream=True, follow=True, tail=100):
                        if self._stop_streaming:
                            break
                        
                        try:
                            decoded = line.decode('utf-8')
                            self.send(text_data=decoded)
                        except UnicodeDecodeError:
                            self.send(text_data=line.decode('utf-8', errors='replace'))
                        
                        time.sleep(0.01)
                
                except Exception as e:
                    logger.error(f"Logs Stream: Error en servicio {self.service.id}: {e}")
                    self.send(text_data=f"[ERROR] {e}\n")
        
        except Exception as e:
            logger.error(f"Logs Stream: Error general: {e}")
            self.send(text_data=f"[ERROR] Error inesperado: {e}\n")
        
        finally:
            logger.info(f"Logs Stream: Finalizado para servicio {self.service.id}")
    
    def receive(self, text_data=None, bytes_data=None):
        """
        Recibir comandos de control.
        
        Comandos:
        - "pause": Pausar streaming
        - "resume": Reanudar streaming
        - "stop": Detener completamente
        """
        if text_data:
            command = text_data.strip().lower()
            
            if command == "pause":
                self._stop_streaming = True
                self.send(text_data="[PAUSADO] Streaming pausado\n")
            
            elif command == "resume":
                self._stop_streaming = False
                self.send(text_data="[REANUDADO] Streaming reanudado\n")
                # Reiniciar thread
                if not self._stream_thread or not self._stream_thread.is_alive():
                    self._stream_thread = threading.Thread(
                        target=self._stream_logs,
                        daemon=True,
                    )
                    self._stream_thread.start()
            
            elif command == "stop":
                self._stop_streaming = True
                self.close()
    
    def disconnect(self, close_code):
        """Limpiar recursos al desconectar"""
        logger.info(f"Logs Stream: Desconexión (code={close_code})")
        
        self._stop_streaming = True
        
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=2)
        
        self._stream_thread = None
