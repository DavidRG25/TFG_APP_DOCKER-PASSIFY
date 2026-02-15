import logging
import threading
import time
import socket
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer
from django.http import Http404
from django.shortcuts import get_object_or_404

from docker.errors import DockerException

from .docker_client import get_docker_client
from .models import Service, ServiceContainer

logger = logging.getLogger(__name__)



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
    TIMEOUT_SECONDS = 300  # 5 minutos de inactividad (Producción)
    
    def connect(self):
        """Inicializar conexión WebSocket y ejecutar shell en contenedor"""
        service_id = self.scope["url_route"]["kwargs"].get("service_id")
        user = self.scope.get("user")
        self._reader_thread = None
        self.sock = None
        self.last_activity = time.time()
        self._stopped = False
        
        # Verificar autenticación
        if not user or not user.is_authenticated:
            self.close(code=4401)
            return
        
        # Obtener servicio y verificar permisos
        from .views import user_is_admin, user_is_teacher
        try:
            if user_is_admin(user):
                # Admins tienen acceso total
                service = get_object_or_404(Service, pk=service_id)
            elif user_is_teacher(user):
                # Profesores solo acceden si el servicio es de su asignatura
                service = get_object_or_404(Service, pk=service_id)
                if service.subject and service.subject.teacher_user != user:
                    logger.warning(f"Terminal: Teacher {user} intentó acceder a servicio {service_id} de otra asignatura")
                    self.accept()
                    self.send(text_data="\r\n\033[1;31m[ERROR]\033[0m No tienes permisos para acceder a la terminal de este alumno.\r\n")
                    self.close(code=4403)
                    return
            else:
                # Alumnos solo sus propios servicios
                service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            logger.warning(f"Terminal: Usuario {user} intentó acceder a servicio {service_id} sin permisos")
            self.accept()
            self.send(text_data="\r\n\033[1;31m[ERROR]\033[0m No tienes permisos para acceder a esta terminal.\r\n")
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
            
            # Iniciar hilos de trabajo
            self._reader_thread = threading.Thread(
                target=self._read_from_container,
                name=f"terminal-reader-{service_id}",
                daemon=True,
            )
            self._reader_thread.start()
            
            self._timeout_thread = threading.Thread(
                target=self._timeout_monitor,
                name=f"terminal-timeout-{service_id}",
                daemon=True,
            )
            self._timeout_thread.start()
            
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
    
    def _timeout_monitor(self):
        """Hilo dedicado a vigilar la inactividad"""
        while not self._stopped:
            time.sleep(2)
            current_time = time.time()
            if self.last_activity and (current_time - self.last_activity) > self.TIMEOUT_SECONDS:
                logger.info(f"Terminal: Timeout alcanzado ({self.TIMEOUT_SECONDS}s)")
                try:
                    self.send(text_data="\r\n\033[1;33m[TIMEOUT]\033[0m Sesión cerrada por inactividad.\r\n")
                    self.close()
                except Exception:
                    pass
                break

    def _read_from_container(self):
        """Leer salida del contenedor y enviarla al navegador"""
        try:
            sock = self._get_raw_socket()
            if not sock:
                return
            
            # Lectura bloqueante estándar (más compatible con Windows Docker Pipes)
            while not self._stopped:
                chunk = sock.recv(4096)
                
                if not chunk:
                    if not self._stopped:
                        logger.info("Terminal: Connection closed by container")
                        self.send(text_data="\r\n\033[1;33m[DESCONECTADO]\033[0m El contenedor cerró la conexión.\r\n")
                    break
                
                # Actualizar actividad al recibir datos del contenedor
                self.last_activity = time.time()
                
                try:
                    decoded = chunk.decode("utf-8")
                    self.send(text_data=decoded)
                except UnicodeDecodeError:
                    self.send(bytes_data=chunk)
                    
        except Exception as exc:
            if not self._stopped:
                logger.error(f"Terminal: Error leyendo del contenedor: {exc}")
                try:
                    self.send(text_data=f"\r\n\033[1;31m[ERROR]\033[0m {exc}\r\n")
                except Exception:
                    pass
        finally:
            self.close()
    
    def disconnect(self, close_code):
        """Limpiar recursos al desconectar"""
        logger.info(f"Terminal: Desconexión (code={close_code})")
        self._stopped = True
        
        try:
            sock = self._get_raw_socket()
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
        finally:
            self.sock = None


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
        self._threads = []
        self._send_lock = threading.Lock() # Lock para evitar colisiones entre hilos
        self._stop_streaming = False
        
        # Verificar autenticación
        if not user or not user.is_authenticated:
            self.close(code=4401)
            return
        
        # Obtener servicio
        from .views import user_is_admin, user_is_teacher
        try:
            if user_is_admin(user) or user_is_teacher(user):
                service = get_object_or_404(Service, pk=service_id)
            else:
                service = get_object_or_404(Service, pk=service_id, owner=user)
        except Http404:
            self.close(code=4403)
            return
        
        self.service = service
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        self.selected_container_id = query_params.get("container", [None])[0]
        self.tail = query_params.get("tail", ["10"])[0]
        self.since = query_params.get("since", [None])[0]
        
        self.accept()
        
        docker_client = get_docker_client()
        if not docker_client:
            self.send_json({"log": "🔴 [ERROR] Docker no disponible"})
            self.close()
            return
        
        self.docker_client = docker_client
        self._start_streaming()
        
        logger.info(f"Logs Stream: Abierto para servicio {service_id}")

    def send_json(self, data):
        import json
        with self._send_lock: # Asegurar exclusión mutua
            try:
                self.send(text_data=json.dumps(data))
            except: pass

    def _start_streaming(self):
        """Inicia hilos de streaming para los contenedores seleccionados"""
        self._threads_map = {} # Mapa de nombre -> hilo para control individual
        
        if self.service.has_compose:
            containers_query = ServiceContainer.objects.filter(service=self.service)
            if self.selected_container_id and self.selected_container_id != 'all':
                try:
                    containers_query = containers_query.filter(id=int(self.selected_container_id))
                except: pass
            
            containers = list(containers_query.filter(container_id__isnull=False))
            for c_rec in containers:
                self._launch_thread(c_rec.container_id, c_rec.name)
        else:
            if self.service.container_id:
                self._launch_thread(self.service.container_id, self.service.name)

    def _launch_thread(self, container_id, name):
        """Lanza un hilo de seguimiento para un contenedor"""
        if name in self._threads_map and self._threads_map[name].is_alive():
            return # Ya hay uno funcionando
            
        t = threading.Thread(
            target=self._follow_container_logs,
            args=(container_id, name),
            daemon=True
        )
        t.start()
        self._threads_map[name] = t
        self._threads.append(t)

    def _follow_container_logs(self, container_id, name):
        """Sigue los logs de un contenedor con buffering y auto-reconexión limitada"""
        import struct
        import time
        import dateutil.parser
        from datetime import timedelta, timezone
        from .utils import colorize_logs_rich
        
        prefix = f"[{name}] " if self.service.has_compose else ""
        retry_count = 0
        max_retries = 5
        
        while not self._stop_streaming:
            try:
                # Intentar obtener el contenedor
                id_to_fetch = container_id
                
                # Intentar refrescar ID solo si no lo tenemos o si hemos fallado antes
                if retry_count > 0:
                    try:
                        if not self.service.has_compose:
                            self.service.refresh_from_db()
                            id_to_fetch = self.service.container_id
                        else:
                            c_rec = ServiceContainer.objects.get(service=self.service, name=name)
                            id_to_fetch = c_rec.container_id
                    except: pass

                if not id_to_fetch:
                    raise Exception("ID no disponible")

                container = self.docker_client.containers.get(id_to_fetch)
                
                # Si el contenedor no está corriendo, lo tratamos como un intento de espera
                if container.status != "running":
                    raise Exception(f"Estado: {container.status}")

                self.send_json({"log": f"<div style='color: #4ade80; border-top: 1px solid #333; padding-top: 5px;'>🔌 Conectando a stream: {name}...</div>"})
                
                # Buffer para acumular fragmentos
                line_buffer = b""
                
                # Iniciamos stream
                # Iniciamos stream
                logs_kwargs = {'stream': True, 'follow': True, 'timestamps': True} # Añadir timestamps
                
                # Configurar tail
                try:
                    if self.tail == 'all': logs_kwargs['tail'] = 'all'
                    else: logs_kwargs['tail'] = int(self.tail)
                except:
                    logs_kwargs['tail'] = 10
                
                # Configurar since
                if self.since:
                    logs_kwargs['since'] = self.since

                log_stream = container.logs(**logs_kwargs)
                
                # Si llegamos aquí, hemos conectado
                retry_count = 0 
                
                for chunk in log_stream:
                    if self._stop_streaming: break
                    
                    data = chunk
                    if len(data) >= 8 and data[1:4] == b'\x00\x00\x00' and data[0] in [1, 2]:
                        try:
                            while len(data) >= 8:
                                header = data[:8]
                                size = struct.unpack('>I', header[4:8])[0]
                                payload = data[8:8+size]
                                line_buffer += payload
                                data = data[8+size:]
                        except:
                            line_buffer += data
                    else:
                        line_buffer += data

                    if b'\n' in line_buffer:
                        parts = line_buffer.split(b'\n')
                        line_buffer = parts.pop()
                        for l in parts:
                            txt = l.decode('utf-8', errors='replace').strip()
                            if txt:
                                # Formatear con hora local (España)
                                parts = txt.split(' ', 1)
                                if 'T' in parts[0]:
                                    try:
                                        raw_ts = parts[0]
                                        content = parts[1] if len(parts) > 1 else ""
                                        dt_utc = dateutil.parser.parse(raw_ts)
                                        dt_spain = dt_utc.astimezone(timezone(timedelta(hours=1)))
                                        human_ts = dt_spain.strftime("%d/%m/%Y %H:%M:%S")
                                        txt = f"[{human_ts}] {content}"
                                    except: pass
                                
                                self.send_json({"log": colorize_logs_rich([f"{prefix}{txt}"])})
                
                # Si el stream termina solo y no hemos parado nosotros
                if not self._stop_streaming:
                    self.send_json({"log": f"<div style='color: #f87171;'>🛰️ {name} ha finalizado el stream (contenedor parado).</div>"})
                    retry_count += 1
                    
            except Exception as e:
                if self._stop_streaming: break
                retry_count += 1
                
                if retry_count >= max_retries:
                    self.send_json({"log": f"""
                        <div style='color: #ef4444; padding: 10px; border: 1px dashed #ef4444; border-radius: 8px; margin: 10px 0; background: rgba(239, 68, 68, 0.1);'>
                            ⚠️ <strong>{name}</strong> no responde (Intento {retry_count}/{max_retries}).<br>
                            <small style='color: #fca5a5;'>Motivo: {str(e)}</small><br>
                            <button onclick='reconnect_container("{name}")' 
                                    style='background: #3b82f6; color: white; border: none; padding: 6px 15px; border-radius: 6px; margin-top: 10px; cursor: pointer; font-weight: bold;'>
                                <i class="fas fa-sync"></i> Reintentar ahora
                            </button>
                        </div>
                    """})
                    break 
                
                self.send_json({"log": f"<div style='color: #fbbf24; font-size: 0.9em; margin: 4px 0;'>⏳ Esperando a {name} ({retry_count}/{max_retries})... <small>[{str(e)}]</small></div>"})
                time.sleep(4)
        
        if self._stop_streaming:
            self.send_json({"log": f"<div style='color: #6b7280; font-style: italic; border-top: 1px solid #333;'>🚫 Seguimiento detenido para: {name}</div>"})

    def receive(self, text_data=None, bytes_data=None):
        import json
        try:
            data = json.loads(text_data)
            command = data.get("command")
            
            if command == "stop":
                self._stop_streaming = True
                self.close()
            elif command == "reconnect":
                container_name = data.get("container")
                if container_name:
                    # Para servicios simples, el container_id está en service.container_id
                    # Para compose, en ServiceContainer
                    cid = self.service.container_id
                    if self.service.has_compose:
                        try:
                            cid = ServiceContainer.objects.get(service=self.service, name=container_name).container_id
                        except: cid = None
                    
                    if cid:
                        self._launch_thread(cid, container_name)
        except:
            if text_data == "stop":
                self._stop_streaming = True
                self.close()

    def disconnect(self, close_code):
        self._stop_streaming = True
        logger.info(f"Logs Stream: Finalizado para servicio {self.service.id}")
