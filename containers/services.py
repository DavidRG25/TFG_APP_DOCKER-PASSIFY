# containers/services.py
import os
import random
import re
import shutil
import subprocess
import tempfile
import yaml

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.conf import settings
from django.db import IntegrityError, transaction

from docker import DockerClient
from docker.errors import APIError, DockerException, NotFound

from .docker_client import get_docker_client
from .models import PORT_RANGE_END, PORT_RANGE_START, PortReservation, Service, ServiceContainer

UNRAR_TOOL = os.environ.get("UNRAR_TOOL_PATH")
if not UNRAR_TOOL:
    print("[warning] UNRAR_TOOL_PATH is not set; RAR extraction may fail.")
elif not os.path.exists(UNRAR_TOOL):
    print("[warning] UNRAR_TOOL_PATH points to a missing path; RAR extraction may fail.")

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MiB
COMPOSE_EXTENSIONS = {".yml", ".yaml"}
CODE_EXTENSIONS = {".zip", ".rar"}

EXECUTOR = ThreadPoolExecutor(
    max_workers=int(os.environ.get("SERVICE_WORKERS", "10"))
)

SERVICE_WORKSPACES_ROOT = Path(getattr(settings, "SERVICE_WORKSPACES_ROOT", Path(settings.MEDIA_ROOT) / "services"))


# ==================== WORKSPACE MANAGEMENT ====================

def ensure_service_workspace(service: Service) -> Path:
    """
    Crea y retorna la carpeta workspace del servicio: media/services/<id>/
    Esta es la carpeta donde se almacenan todos los archivos del servicio.
    """
    workspace = SERVICE_WORKSPACES_ROOT / str(service.pk)
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def cleanup_service_workspace(service: Service) -> None:
    """Elimina completamente el workspace y cualquier rastro del servicio en media/"""
    import time
    import stat
    import os
    import shutil
    from pathlib import Path

    sid = str(service.id)
    workspace = SERVICE_WORKSPACES_ROOT / sid
    
    if workspace.exists():
        for attempt in range(3):
            try:
                # En Windows a veces hay problemas de permisos con archivos de solo lectura dentro de .git o similares
                if os.name == 'nt':
                    for root, dirs, files in os.walk(workspace):
                        for d in dirs:
                            try: os.chmod(os.path.join(root, d), stat.S_IRWXU)
                            except: pass
                        for f in files:
                            try: os.chmod(os.path.join(root, f), stat.S_IRWXU)
                            except: pass
                
                shutil.rmtree(workspace)
                break
            except Exception:
                if attempt < 2: 
                    time.sleep(1)
                else: 
                    # Último intento: forzar borrado ignorando errores
                    shutil.rmtree(workspace, ignore_errors=True)


def prepare_service_workspace(service: Service, *, unpack_code: bool = True) -> Path:
    """
    Prepara el workspace del servicio asegurando que:
    1. Todos los archivos (Dockerfile, docker-compose.yml) estén en services/<id>/
    2. El código fuente esté descomprimido en services/<id>/
    
    Retorna el Path del workspace.
    """
    workspace = ensure_service_workspace(service)
    
    # Mapeo de campos FileField a nombres de archivo esperados
    mapping = {
        "dockerfile": "Dockerfile",
        "compose": "docker-compose.yml",
    }
    updated_fields = []
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    for field, filename in mapping.items():
        ff = getattr(service, field, None)
        if not ff:
            continue
        
        # Ruta física deseada
        dest = workspace / filename
        desired_rel = f"services/{service.id}/{filename}"
        
        # Caso A: El archivo ya está en el sitio correcto y existe físicamente
        if ff.name == desired_rel and dest.exists():
            continue
            
        # Caso B: El archivo necesita ser movido o copiado
        try:
            # Si el archivo está en 'tmp/', lo leemos y movemos
            content = ff.read()
            
            # 1. Si el nombre en DB está mal (ej. apunta a 'tmp/'), actualizarlo
            if ff.name != desired_rel:
                old_path = ff.name
                ff.save(desired_rel, ContentFile(content), save=False)
                updated_fields.append(field)
                
                # Intentar borrar el rastro viejo (especialmente útil para limpiar services/tmp/)
                if old_path and old_path != desired_rel:
                    try: 
                        if default_storage.exists(old_path):
                            default_storage.delete(old_path)
                    except: pass
            
            # 2. Asegurar que el archivo existe físicamente en el workspace
            if not dest.exists():
                with open(dest, "wb") as f_out:
                    f_out.write(content)
                    
        except Exception as e:
            print(f"[warning] Error preparando {field}: {e}")
            continue

    if updated_fields:
        service.save(update_fields=updated_fields)
    
    # Descomprimir código si existe
    if unpack_code and service.code:
        code_ext = os.path.splitext(service.code.name or "")[1] or ".zip"
        code_rel = f"services/{service.id}/source{code_ext}"
        code_dest_phys = workspace / f"source{code_ext}"
        
        # Si el código no está en su sitio o es un temporal, moverlo
        if service.code.name != code_rel or not code_dest_phys.exists():
            old_code_path = service.code.name
            with service.code.open("rb") as f_in:
                content = f_in.read()
                service.code.save(code_rel, ContentFile(content), save=False)
            service.save(update_fields=["code"])
            
            if old_code_path and old_code_path != code_rel:
                try: 
                    if default_storage.exists(old_code_path):
                        default_storage.delete(old_code_path)
                except: pass
            
            # Asegurar copia física para descompresión
            with open(code_dest_phys, "wb") as f_out:
                f_out.write(content)
        
        # Limpiar archivos previos pero mantener los estructurales
        for item in workspace.iterdir():
            if item.name not in ["Dockerfile", "docker-compose.yml", "source.zip", "source.rar"]:
                if item.is_file():
                    item.unlink()
                elif item.is_dir() and item.name not in [".vs"]:
                    shutil.rmtree(item)
        
        # Descomprimir usando la ruta física para evitar errores de reapertura
        _unpack_code_archive_to(str(workspace), archive_path=str(code_dest_phys))
    
    return workspace


# ==================== DOCKER COMPOSE UTILITIES ====================

def _compose_cmd() -> list[str]:
    """
    Devuelve el comando disponible para docker compose:
    - ['docker', 'compose'] si existe v2
    - ['docker-compose'] si existe v1
    """
    for cmd in (["docker", "compose"], ["docker-compose"]):
        try:
            subprocess.run(cmd + ["version"], check=True, capture_output=True)
            return cmd
        except Exception:
            continue
    raise RuntimeError("No se encontró 'docker compose' (v2) ni 'docker-compose' (v1).")


def _get_compose_project_name(service) -> str:
    """
    Genera un nombre de proyecto descriptivo para Docker Compose.
    Formato: usuario_proyecto_servicio (o svc{id} como fallback)
    
    Reglas de Docker:
    - Solo letras minúsculas, números, guiones y guiones bajos
    - No puede empezar con guión
    - No puede tener guiones consecutivos o al final
    """
    try:
        # Intentar construir nombre descriptivo
        username = service.owner.username if service.owner else "user"
        project_name = service.project.place if service.project else "project"
        service_name = service.name or f"svc{service.id}"
        
        # Sanitizar cada parte
        def sanitize(text):
            # Convertir a minúsculas
            text = text.lower()
            # Reemplazar espacios y caracteres especiales por guión bajo
            text = re.sub(r'[^a-z0-9_-]', '_', text)
            # Eliminar guiones/guiones bajos al inicio y final
            text = text.strip('_-')
            # Reemplazar múltiples guiones/guiones bajos consecutivos por uno solo
            text = re.sub(r'[-_]+', '_', text)
            return text or "unnamed"
        
        username = sanitize(username)
        project_name = sanitize(project_name)
        service_name = sanitize(service_name)
        
        # Formato: usuario_proyecto_servicio
        return f"{username}_{project_name}_{service_name}"
    except Exception:
        # Fallback al formato antiguo si algo falla
        return f"svc{service.id}"


def _extract_container_port_info(container):
    """
    Extrae información de puertos de un contenedor Docker.
    Retorna (internal_ports, assigned_ports)
    """
    internal_ports = []
    assigned_ports = []
    ports_settings = container.attrs.get("NetworkSettings", {}).get("Ports") or {}
    
    for binding_key, bindings in ports_settings.items():
        try:
            container_port, protocol = binding_key.split("/")
        except ValueError:
            continue
        try:
            container_port_int = int(container_port)
        except ValueError:
            continue
        
        internal_ports.append({"internal": container_port_int, "protocol": protocol})
        
        if bindings:
            for bind in bindings:
                host_port = bind.get("HostPort")
                if not host_port:
                    continue
                try:
                    host_port_int = int(host_port)
                except ValueError:
                    continue
                assigned_ports.append({
                    "internal": container_port_int,
                    "external": host_port_int,
                    "protocol": protocol
                })
    
    return internal_ports, assigned_ports


def _previous_port_assignments(service: Service) -> dict:
    """
    Crea un mapa {container_name: {(internal_port, protocol): host_port}} del estado previo.
    Usado para reutilizar puertos en compose.
    """
    mapping: dict[str, dict[tuple[int, str], int]] = {}
    for sc in service.containers.all():
        entries: dict[tuple[int, str], int] = {}
        for info in sc.assigned_ports or []:
            internal = info.get("internal")
            protocol = (info.get("protocol") or "tcp").lower()
            external = info.get("external")
            if internal is None or external is None:
                continue
            try:
                entries[(int(internal), protocol)] = int(external)
            except (TypeError, ValueError):
                continue
        mapping[sc.name] = entries
    return mapping


def _load_compose_data(compose_path: Path) -> dict:
    """Carga y valida el archivo docker-compose.yml"""
    if not compose_path.exists():
        raise RuntimeError("No se encontró docker-compose.yml en la carpeta del servicio.")
    
    with compose_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    
    if not isinstance(data, dict):
        raise RuntimeError("El archivo docker-compose.yml tiene un formato inválido.")
    
    services_data = data.get("services")
    if not services_data:
        raise RuntimeError("docker-compose.yml no define la clave 'services'.")
    
    if not isinstance(services_data, dict):
        raise RuntimeError("La sección 'services' debe ser un objeto.")
    
    return data


def _ensure_compose_ports(data: dict, previous_map: dict[str, dict[tuple[int, str], int]]) -> list[int]:
    """
    Normaliza las entradas de puertos en docker-compose y asigna host ports cuando no se especifican.
    Soporta notaciones: "8080:80", "80", etc.
    Retorna la lista de puertos reservados en esta ejecución.
    """
    reserved_now: list[int] = []
    services_data = data.get("services") or {}
    
    for svc_name, config in services_data.items():
        ports = config.get("ports")
        if not ports or not isinstance(ports, list):
            continue
        
        new_ports = []
        for entry in ports:
            host_port = None
            container_port = None
            protocol = "tcp"
            host_ip = None
            
            if isinstance(entry, int):
                container_port = entry
            elif isinstance(entry, str):
                base = entry
                if "/" in base:
                    base, protocol = base.split("/", 1)
                parts = base.split(":")
                if len(parts) == 3:  # host ip + host port + container
                    host_ip, host_port, container_port = parts
                elif len(parts) == 2:
                    host_port, container_port = parts
                elif len(parts) == 1:
                    container_port = parts[0]
                else:
                    container_port = parts[-1]
                    host_port = parts[-2]
            else:
                new_ports.append(entry)
                continue
            
            try:
                container_port = int(str(container_port).strip())
            except (TypeError, ValueError):
                new_ports.append(entry)
                continue
            
            prev_map = previous_map.get(svc_name, {})
            prev_host = prev_map.get((container_port, protocol.lower()))
            
            # IMPORTANTE: Siempre usar puertos del rango 40000-50000 para compose
            # Ignorar puertos especificados fuera del rango
            if host_port is not None and host_port != "":
                try:
                    host_port_int = int(str(host_port).strip())
                except (TypeError, ValueError):
                    raise RuntimeError(
                        f"El puerto declarado '{host_port}' en el servicio '{svc_name}' no es válido."
                    )
                # Verificar si está en el rango permitido
                if PORT_RANGE_START <= host_port_int <= PORT_RANGE_END:
                    # Puerto válido, usarlo
                    if prev_host != host_port_int:
                        _reserve_specific_port(host_port_int)
                        reserved_now.append(host_port_int)
                    final_host = host_port_int
                else:
                    # Puerto fuera del rango, asignar uno aleatorio
                    if prev_host and PORT_RANGE_START <= prev_host <= PORT_RANGE_END:
                        final_host = prev_host
                    else:
                        final_host = _reserve_random_port()
                        reserved_now.append(final_host)
            else:
                if prev_host and PortReservation.objects.filter(port=prev_host).exists():
                    final_host = prev_host
                elif prev_host:
                    _reserve_specific_port(prev_host)
                    reserved_now.append(prev_host)
                    final_host = prev_host
                else:
                    final_host = _reserve_random_port()
                    reserved_now.append(final_host)
            
            entry_value = f"{final_host}:{container_port}"
            if protocol and protocol.lower() != "tcp":
                entry_value = f"{entry_value}/{protocol}"
            if host_ip:
                entry_value = f"{host_ip}:{entry_value}"
            new_ports.append(entry_value)
        
        config["ports"] = new_ports
    
    return reserved_now


def sync_service_status(service: Service):
    """
    Sincroniza el estado del servicio con Docker de forma proactiva.
    
    Rescata servicios estancados en estados transitorios (pending, starting, etc.)
    si Docker ya informa de un estado estable.
    """
    # Ignorar servicios eliminados - no deben ser "resucitados"
    if service.status == "removed":
        return
        
    docker_client = get_docker_client()
    if docker_client is None:
        return

    if service.has_compose:
        # ===== SINCRONIZACIÓN COMPOSE =====
        project = _get_compose_project_name(service)
        
        try:
            containers = docker_client.containers.list(
                all=True, 
                filters={"label": f"com.docker.compose.project={project}"}
            )
            

            
            if not containers:

                return

            all_running = True
            any_running = False
            for ctr in containers:
                ctr.reload()
                status = (ctr.status or "").lower()
                
                # Un contenedor está "listo" si está corriendo O si ha terminado con éxito (exit code 0)
                exit_code = ctr.attrs.get('State', {}).get('ExitCode', 0)
                is_ready = (status == "running") or (status == "exited" and exit_code == 0)
                

                
                if status == "running":
                    any_running = True
                
                if not is_ready:
                    all_running = False
                
                svc_name = ctr.labels.get("com.docker.compose.service") or ctr.name
                if svc_name == "principal": continue
                
                internal_ports, assigned_ports = _extract_container_port_info(ctr)
                
                # Sincronizar ServiceContainer records
                ServiceContainer.objects.update_or_create(
                    service=service,
                    name=svc_name,
                    defaults={
                        "container_id": ctr.id,
                        "status": status,
                        "internal_ports": internal_ports,
                        "assigned_ports": assigned_ports,
                    }
                )



            # Si PaaSify cree que no corre pero Docker dice que TODO corre, rescatarlo.
            # Solo pasamos a 'running' si ABSOLUTAMENTE TODOS los contenedores están listos.
            if any_running and all_running and service.status != "running":

                service.status = "running"
                if not service.container_id:
                    service.container_id = containers[0].id
                service.save(update_fields=["status", "container_id"])
            elif not any_running and service.status == "running":
                # Si PaaSify cree que corre pero Docker dice que no hay ninguno

                service.status = "stopped"
                service.save(update_fields=["status"])
            else:
                pass
                
        except Exception as e:
            print(f"[sync_service_status] Error sincronizando servicio Compose {service.id}: {e}")
            import traceback
            traceback.print_exc()
    else:
        # ===== SINCRONIZACIÓN SIMPLE =====
        if not service.container_id:
            return

        try:
            container = docker_client.containers.get(service.container_id)
            container.reload()
            docker_status = (container.status or "").lower()
            
            # RESCATE: Si está running, forzar estado running
            if docker_status == "running" and service.status != "running":
                service.status = "running"
                # Intentar recuperar puerto si se perdió
                if not service.assigned_port:
                    _, assigned = _extract_container_port_info(container)
                    if assigned:
                        service.assigned_port = assigned[0].get("external")
                service.save()
                return

            # CIERRE: Si está muerto, forzar estado stopped/error
            if docker_status in {"exited", "dead", "stopped"}:
                if service.status not in {"stopped", "error", "removed", "deleting"}:
                    service.status = "stopped"
                    service.save(update_fields=["status"])
                return

            # Respetar estados transitorios de PaaSify si Docker no dice lo contrario
            if service.status in {"building", "pulling", "deleting", "creating"}:
                return
                
        except NotFound:
            if service.status != "deleting":
                service.status = "removed"
                service.save()
        except DockerException:
            pass


# ==================== PORT MANAGEMENT ====================

def _release_port(port: int | None):
    if port:
        PortReservation.objects.filter(port=port).delete()


def _reserve_specific_port(port: int) -> None:
    try:
        with transaction.atomic():
            PortReservation.objects.create(port=port)
    except IntegrityError as exc:
        raise RuntimeError(f"El puerto {port} ya esta en uso.") from exc


def generate_random_port() -> int:
    return random.randint(PORT_RANGE_START, PORT_RANGE_END)


def _reserve_random_port() -> int:
    """Reserva un puerto aleatorio dentro del rango definido."""
    for _ in range(50):
        candidate = generate_random_port()
        try:
            with transaction.atomic():
                PortReservation.objects.create(port=candidate)
            return candidate
        except IntegrityError:
            continue
    return PortReservation.reserve_free_port()


# ==================== LOGGING & UTILITIES ====================

def _append_log(service: Service, message: str) -> None:
    """Añade una línea al histórico de logs del servicio."""
    current = service.logs or ""
    if current:
        service.logs = f"{current.rstrip()}\n{message}"
    else:
        service.logs = message


def _run_command_stream_logs(service: Service, cmd: list[str], cwd: str = None):
    """
    Ejecuta un comando y va guardando la salida en los logs del servicio en tiempo real.
    """
    import subprocess
    import sys
    import os
    import time
    
    _append_log(service, f"> {' '.join(cmd)}")
    service.save(update_fields=["logs"])
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        last_save = time.time()
        line_count = 0
        
        # Leer línea a línea
        for line in process.stdout:
            if line:
                _append_log(service, line.strip())
                line_count += 1
                
                # Guardar cada segundo o cada 15 líneas para no saturar DB
                now = time.time()
                if now - last_save > 1.0 or line_count >= 15:
                    service.save(update_fields=["logs"])
                    last_save = now
                    line_count = 0
                
        process.wait()
        service.save(update_fields=["logs"]) # Asegurar guardado final
        
        if process.returncode != 0:
            raise RuntimeError(f"El comando falló con código {process.returncode}")
            
    except Exception as e:
        _append_log(service, f"ERROR al ejecutar comando: {str(e)}")
        service.save(update_fields=["logs"])
        raise


def _service_slug(service: Service) -> str:
    base = (service.name or "").lower()
    base = re.sub(r"[^a-z0-9-_]+", "-", base)
    base = re.sub(r"-{2,}", "-", base).strip("-")
    if not base:
        base = f"svc{service.id}"
    return base


def _ensure_container_running(service: Service, container, reserved_port: int | None):
    """Verifica que Docker haya iniciado el contenedor.

    Espera hasta 15 segundos para que el contenedor arranque.
    Si el contenedor termina inmediatamente (estado exited/dead) registramos los logs,
    liberamos el puerto reservado y lanzamos una excepción para notificar al usuario.
    """
    import time
    
    # Esperar hasta 15 segundos para que el contenedor arranque
    # Algunos contenedores (Flask, Django) tardan en inicializar
    max_attempts = 30  # 30 intentos x 0.5s = 15 segundos
    
    for attempt in range(max_attempts):
        try:
            container.reload()
            status = (container.status or "").lower()
        except DockerException:
            # Si no podemos recargar, asumimos que está arrancando
            time.sleep(0.5)
            continue
        
        # ✅ Contenedor arrancado correctamente
        if status == "running":
            return
        
        # Estados temporales: esperar un poco más
        if status in {"created", "restarting"}:
            time.sleep(0.5)
            continue
        
        # Estados de error definitivos: salir inmediatamente
        if status in {"exited", "dead", "removing"}:
            break
        
        # Estado "paused" o desconocido: dar más oportunidades
        time.sleep(0.5)
    
    # Verificación final: dar una última oportunidad
    time.sleep(1)  # Espera extra de 1 segundo
    try:
        container.reload()
        status = (container.status or "").lower()
    except DockerException:
        status = "unknown"
    
    # Si finalmente está running, todo bien
    if status == "running":
        return
    
    # Si llegamos aquí y NO está en un estado de error definitivo, asumir que está OK
    # Esto evita falsos positivos con contenedores que tardan en arrancar
    if status not in {"exited", "dead", "removing"}:
        _append_log(service, f"[Advertencia] Contenedor en estado '{status}', pero se asume correcto.")
        service.save(update_fields=["logs"])
        return
    
    # Solo marcar como error si está definitivamente muerto
    try:
        log_tail = container.logs(tail=200).decode(errors="replace")
    except Exception:
        log_tail = "(logs no disponibles)"
    service.status = "error"
    _append_log(service, f"[Docker] Contenedor en estado '{status}'. Logs:")
    _append_log(service, log_tail.strip())
    service.save(update_fields=["status", "logs"])
    try:
        container.remove(force=True)
    except DockerException:
        pass
    _release_port(reserved_port)
    raise RuntimeError(f"El contenedor no arrancó correctamente (estado: {status}). Revisa los logs para más detalles.")


# ==================== FILE UTILITIES ====================

def _validate_upload(ff, *, allowed_extensions=None, max_size=MAX_UPLOAD_SIZE):
    """Valida tamaño y extensión permitida para un ``FieldFile``."""
    if ff is None:
        return

    if max_size and getattr(ff, "size", None) and ff.size > max_size:
        raise ValueError(
            f"El archivo '{getattr(ff, 'name', 'desconocido')}' supera el tamaño máximo permitido ({max_size // (1024 * 1024)} MiB)."
        )

    if allowed_extensions is not None:
        name = getattr(ff, "name", "") or ""
        extension = os.path.splitext(name)[1].lower()
        if extension not in allowed_extensions:
            allowed = ", ".join(sorted(ext or 'sin extensión' for ext in allowed_extensions))
            raise ValueError(
                f"El archivo '{name}' debe tener una de las extensiones permitidas: {allowed}."
            )


def _save_filefield_to(tmp_path: str, ff) -> str:
    """
    Guarda el contenido de un FileField en 'tmp_path' y devuelve esa ruta.
    """
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    with ff.open("rb") as in_fh:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(in_fh, out)
    return tmp_path


def _unpack_code_archive_to(target_dir: str, ff=None, archive_path=None) -> None:
    """
    Descomprime un archivo de código (zip o rar) a 'target_dir'.
    Puede recibir un FileField (ff) o una ruta física (archive_path).
    """
    os.makedirs(target_dir, exist_ok=True)
    
    if archive_path and os.path.exists(archive_path):
        tmp_path = archive_path
        # No borraremos el archivo original si nos dan archive_path
        should_delete_tmp = False
        extension = os.path.splitext(archive_path)[1].lower()
    elif ff:
        name = getattr(ff, "name", "") or ""
        extension = os.path.splitext(name)[1].lower()
        tmp_path = os.path.join(target_dir, f"_code_tmp{extension or '.tmp'}")
        _save_filefield_to(tmp_path, ff)
        should_delete_tmp = True
    else:
        raise ValueError("Se debe proporcionar al menos 'ff' o 'archive_path'")

    try:
        if extension == ".rar":
            _extract_rar_with_tool(tmp_path, target_dir)
        else:
            try:
                shutil.unpack_archive(tmp_path, target_dir)
            except Exception as exc:
                raise RuntimeError(f"No se pudo descomprimir el archivo: {exc}") from exc
    finally:
        if should_delete_tmp and os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass


def _extract_rar_with_tool(tmp_path: str, target_dir: str) -> None:
    """
    Usa la herramienta externa definida en UNRAR_TOOL_PATH para probar y extraer el RAR.
    """
    if not UNRAR_TOOL:
        raise RuntimeError("UNRAR_TOOL_PATH no esta definido; instala 7z/unrar y configura la variable de entorno.")
    if not os.path.exists(UNRAR_TOOL):
        raise RuntimeError(f"UNRAR_TOOL_PATH apunta a una ruta inexistente: {UNRAR_TOOL}")

    os.makedirs(target_dir, exist_ok=True)

    test_cmd = [UNRAR_TOOL, "t", tmp_path]
    extract_cmd = [UNRAR_TOOL, "x", tmp_path, f"-o{target_dir}", "-y"]

    try:
        proc_test = subprocess.run(test_cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("El archivo RAR esta incompleto o dañado. Intentalo de nuevo.") from exc
    if proc_test.stdout:
        _ = proc_test.stdout  # silencio lint

    try:
        subprocess.run(extract_cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("El archivo RAR esta incompleto o dañado. Intentalo de nuevo.") from exc


# ==================== MAIN CONTAINER EXECUTION ====================

def _run_container_internal(
    service: Service,
    *,
    force_restart: bool = False,
    custom_port: int | None = None,
    command: list[str] | None = None,
):
    """
    Arranca (o rearma) el contenedor asociado a un Service.
    
    MODO SIMPLE (Dockerfile o catálogo):
      - Crea UN SOLO contenedor
      - NO crea ServiceContainer records
      - Mantiene compatibilidad total con funcionalidad anterior
    
    MODO COMPOSE (docker-compose.yml):
      - Ejecuta docker compose desde workspace
      - Crea ServiceContainer por cada servicio del YAML
      - Maneja puertos automáticamente
    """
    docker_client = get_docker_client()
    if docker_client is None:
        service.status = "error"
        service.logs = "Docker no está disponible. Inicia el daemon y vuelve a intentarlo."
        service.save()
        raise RuntimeError("Docker no está disponible en el entorno de ejecución.")

    # Validar archivos subidos
    try:
        if service.compose:
            _validate_upload(service.compose, allowed_extensions=COMPOSE_EXTENSIONS)
        if service.code:
            _validate_upload(service.code, allowed_extensions=CODE_EXTENSIONS)
        if service.dockerfile:
            _validate_upload(service.dockerfile, allowed_extensions=None)
    except ValueError as exc:
        service.status = "error"
        service.logs = str(exc)
        service.save()
        raise

    # ========== DECISIÓN: ¿Es compose o simple? ==========
    if service.has_compose:
        # ===== MODO COMPOSE =====
        _run_compose_service(service, docker_client, force_restart)
    else:
        # ===== MODO SIMPLE (mantiene funcionalidad anterior 100%) =====
        _run_simple_service(service, docker_client, force_restart, custom_port, command)


def _run_compose_service(service: Service, docker_client, force_restart: bool):
    """
    Ejecuta un servicio docker-compose.
    Crea ServiceContainer records para cada contenedor.
    """
    service.status = "starting"
    _append_log(service, "--- Iniciando proceso de despliegue Compose ---")
    service.save(update_fields=["status", "logs"])

    try:
        # 1. Preparar workspace
        _append_log(service, "[1/3] Preparando archivos y workspace...")
        workspace = prepare_service_workspace(service)
        compose_path = workspace / "docker-compose.yml"
        
        if not compose_path.exists():
            raise RuntimeError("No se encontró docker-compose.yml en el workspace del servicio.")
        
        # 2. Cargar y procesar puertos
        _append_log(service, "[2/3] Validando configuración y reservando puertos...")
        data = _load_compose_data(compose_path)
        previous_ports = _previous_port_assignments(service)
        reserved_ports = _ensure_compose_ports(data, previous_ports)
        
        # Guardar el YAML modificado con puertos asignados
        with compose_path.open("w", encoding="utf-8") as fh:
            yaml.dump(data, fh)
        
        # 3. Ejecutar docker compose
        project = _get_compose_project_name(service)
        cmd = _compose_cmd() + ["-p", project, "-f", str(compose_path), "up", "--build", "-d"]
        
        _append_log(service, f"[3/3] Ejecutando orquestación (Proyecto: {project})...")
        service.save(update_fields=["logs"])
        
        # Limpiar registros previos de ServiceContainer para evitar duplicados/basura
        service.containers.all().delete()
        
        _run_command_stream_logs(service, cmd, cwd=str(workspace))
        
    except (subprocess.CalledProcessError, RuntimeError) as e:
        # Liberar puertos reservados si falla
        for port in reserved_ports:
            _release_port(port)
        service.status = "error"
        _append_log(service, f"ERROR: {str(e)}")
        service.save()
        raise
    except Exception as e:
        service.status = "error"
        _append_log(service, f"ERROR general: {str(e)}")
        service.save()
        raise
    
    # Detectar contenedores creados
    containers = docker_client.containers.list(
        all=True, 
        filters={"label": f"com.docker.compose.project={project}"}
    )
    
    if not containers:
        service.status = "error"
        _append_log(service, "docker-compose: no se detectó ningún contenedor con el proyecto especificado.")
        service.save()
        raise RuntimeError("No se detectaron contenedores")
    
    _append_log(service, f"Contenedores detectados: {len(containers)}")
    service.save(update_fields=["logs"])
    
    # Crear/actualizar ServiceContainer por cada uno
    for ctr in containers:
        svc_name = ctr.labels.get("com.docker.compose.service") or ctr.name
        
        # IMPORTANTE: NO crear si name == "principal"
        if svc_name == "principal":
            continue
        
        internal_ports, assigned_ports = _extract_container_port_info(ctr)
        
        ServiceContainer.objects.update_or_create(
            service=service,
            name=svc_name,
            defaults={
                "container_id": ctr.id,
                "status": ctr.status,
                "internal_ports": internal_ports,
                "assigned_ports": assigned_ports,
            }
        )
        _append_log(service, f"ServiceContainer creado: {svc_name} ({ctr.status})")
    
    # Actualizar Service
    service.container_id = containers[0].id  # Contenedor principal para compatibilidad
    
    # Esperar 3 segundos para dar tiempo a que los contenedores se estabilicen
    # antes de que sync_service_status los verifique
    import time
    _append_log(service, "Esperando 3 segundos para estabilización de contenedores...")
    time.sleep(3)
    
    # Dejar en 'starting' para que sync_service_status haga la transición a 'running'
    # cuando verifique que todos los contenedores están realmente listos.
    # Esto evita condiciones de carrera donde marcamos como running antes de tiempo.
    _append_log(service, "docker-compose up ejecutado. Verificando estado de contenedores...")
    service.save()



def _run_simple_service(service: Service, docker_client, force_restart: bool, custom_port: int | None, command: list[str] | None):
    """
    Ejecuta un servicio simple (Dockerfile o catálogo).
    MANTIENE 100% compatibilidad con funcionalidad anterior.
    NO crea ServiceContainer records.
    """
    port = None
    try:
        # Si hay que reiniciar, eliminar contenedor previo y liberar puerto
        if force_restart and service.container_id:
            try:
                docker_client.containers.get(service.container_id).remove(force=True)
            except NotFound:
                pass
            except DockerException as exc:
                service.logs = f"No se pudo eliminar el contenedor previo: {exc}"
                service.save()
                raise RuntimeError(service.logs)
            service.container_id = None
            _release_port(service.assigned_port)
            service.assigned_port = None

        # Si ya existe y no es reinicio, asegurar que esté en marcha y salir
        if service.container_id and not force_restart:
            try:
                _append_log(service, f"Intentando arrancar contenedor existente: {service.container_id}")
                container = docker_client.containers.get(service.container_id)
                if container.status != "running":
                    container.start()
                    service.status = "running"
                    _append_log(service, "Contenedor arrancado (reutilizado).")
                    service.save(update_fields=["status", "logs", "updated_at"])
                else:
                    service.status = "running"
                    service.save(update_fields=["status", "updated_at"])
                return
            except NotFound:
                _append_log(service, "Contenedor previo no encontrado en Docker, se creará uno nuevo.")
                service.container_id = None
            except DockerException as exc:
                service.logs = f"Error al consultar el contenedor existente: {exc}"
                service.status = "error"
                service.save()
                raise RuntimeError(service.logs)

        # Reserva de puerto
        if custom_port:
            _reserve_specific_port(custom_port)
            port = custom_port
        else:
            port = _reserve_random_port()
        service.assigned_port = port
        service.save(update_fields=["assigned_port"])

        # --------- Caso Dockerfile ---------
        slug = _service_slug(service)
        image_cmd = None

        if service.dockerfile:
            workspace = prepare_service_workspace(service)
            dockerfile_path = workspace / "Dockerfile"
            
            if not dockerfile_path.exists():
                raise RuntimeError("No se encontró Dockerfile en el workspace del servicio.")
            
            image_tag = f"svc_{service.id}_{slug}_image"
            service.status = "building"
            _append_log(service, "Construyendo imagen personalizada...")
            service.save(update_fields=["status", "logs"])
            
            _run_command_stream_logs(service, ["docker", "build", "-t", image_tag, str(workspace)])

            image_to_run = image_tag
            _append_log(service, "Imagen construida correctamente.")
            service.save(update_fields=["logs"])
        else:
            # --------- Caso imagen directa del catálogo ---------
            image_to_run = service.image
            service.status = "pulling"
            _append_log(service, f"Descargando imagen: {image_to_run}...")
            service.save(update_fields=["status", "logs"])
            
            # Usamos comandos docker directamente para tener streaming de logs
            _run_command_stream_logs(service, ["docker", "pull", image_to_run])
            _append_log(service, "Imagen descargada.")
            service.save(update_fields=["logs"])

        try:
            image_attrs = docker_client.images.get(image_to_run).attrs
            image_cmd = image_attrs.get("Config", {}).get("Cmd") or None
        except DockerException:
            image_cmd = None

        # --------- Variables (volúmenes DESHABILITADOS por seguridad) ---------
        # SEGURIDAD CRÍTICA: Los volúmenes están completamente deshabilitados en contenedores simples
        # para prevenir escalada de privilegios mediante bind mounts.
        # Solo se permiten volúmenes nombrados en Docker Compose con validación estricta.
        volumes = None  # NO crear volúmenes automáticamente

        env_vars_raw = service.env_vars or {}
        if not isinstance(env_vars_raw, dict):
            env_vars_raw = {}
        env_vars = dict(env_vars_raw)

        # Puerto interno configurable; por defecto 80
        internal_port = getattr(service, "internal_port", 80) or 80
        if service.internal_port is None:
            service.internal_port = internal_port
            service.save(update_fields=["internal_port"])

        ports = {}
        if port:
            ports[f"{internal_port}/tcp"] = port
        
        # Nombre descriptivo: usar nombre del servicio o slug como fallback
        safe_name = re.sub(r'[^a-z0-9_-]', '_', (service.name or slug).lower())
        container_name = f"{safe_name}_{service.id}_ctr"

        _append_log(service, f"Arrancando nuevo contenedor: {container_name}")

        normalized_command = command
        if isinstance(normalized_command, (list, tuple)):
            if not any((str(part).strip() if isinstance(part, str) else part) for part in normalized_command):
                normalized_command = None
        elif isinstance(normalized_command, str) and not normalized_command.strip():
            normalized_command = None

        normalized_image_cmd = image_cmd
        if isinstance(normalized_image_cmd, (list, tuple)):
            if not any((str(part).strip() if isinstance(part, str) else part) for part in normalized_image_cmd):
                normalized_image_cmd = None
        elif isinstance(normalized_image_cmd, str) and not normalized_image_cmd.strip():
            normalized_image_cmd = None

        run_command = normalized_command if normalized_command is not None else normalized_image_cmd

        container = docker_client.containers.run(
            image=image_to_run,
            command=run_command,
            detach=True,
            tty=True,                 # importante para la terminal
            stdin_open=True,
            name=container_name,
            ports=ports,
            volumes=volumes or None,
            environment=env_vars or None,
        )
        _append_log(service, "Contenedor creado, esperando verificación...")
        _ensure_container_running(service, container, port)

        service.container_id = container.id
        service.assigned_port = port
        service.status = "running"
        # Guardar el tag de la imagen (importante para servicios con Dockerfile)
        service.image = image_to_run
        # Guardar build logs si venía de Dockerfile
        if service.dockerfile:
            _append_log(service, "Imagen construida y contenedor arrancado.")
        service.save()

    except (APIError, DockerException, RuntimeError, ValueError) as exc:
        _release_port(port)
        service.status = "error"
        service.logs = str(exc)
        service.save()
        raise


def _run_container_worker(
    service_id: int, force_restart: bool, custom_port: int | None, command: list[str] | None
) -> None:
    service = None
    try:
        service = Service.objects.get(pk=service_id)
        _run_container_internal(
            service, force_restart=force_restart, custom_port=custom_port, command=command
        )
    except Service.DoesNotExist:
        return
    except Exception as exc:
        if service:
            try:
                service.status = "error"
                _append_log(service, f"Error crítico en el worker: {str(exc)}")
                service.save(update_fields=["status", "logs", "updated_at"])
            except:
                pass
        print(f"[error] Excepción no controlada en _run_container_worker: {exc}")
        import traceback
        traceback.print_exc()


def run_container(
    service: Service,
    force_restart: bool = False,
    custom_port: int | None = None,
    command: list[str] | None = None,
    enqueue: bool = True,
) -> None:
    """
    Encola la ejecucion del contenedor para no bloquear el hilo que atiende la peticion.
    """
    # Guardar contra ejecuciones duplicadas si ya está en cola o iniciándose
    if service.status in ["pending", "starting"] and not force_restart:
        return

    if not enqueue:
        _run_container_internal(
            service,
            force_restart=force_restart,
            custom_port=custom_port,
            command=command,
        )
        return

    service.status = "pending"
    _append_log(service, "Ejecucion encolada.")
    service.save(update_fields=["status", "logs", "updated_at"])
    EXECUTOR.submit(_run_container_worker, service.pk, force_restart, custom_port, command)


# ==================== STOP / REMOVE ====================

def stop_container(service: Service):
    """
    Detiene el servicio.
    
    MODO SIMPLE: Detiene el contenedor único
    MODO COMPOSE: Usa docker compose stop para detener todos simultáneamente
    """
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no está disponible para detener el servicio.")
    
    # Establecer estado "stopping" antes de comenzar
    service.status = "stopping"
    _append_log(service, "Deteniendo servicio...")
    service.save(update_fields=["status", "logs", "updated_at"])
    
    # Pequeño delay para que el auto-refresh capture el estado 'stopping'
    import time
    time.sleep(1.5)
    
    if service.has_compose:
        # ===== MODO COMPOSE: Usar docker compose stop =====
        try:
            workspace = ensure_service_workspace(service)
            compose_path = workspace / "docker-compose.yml"
            
            if not compose_path.exists():
                service.status = "error"
                service.save(update_fields=["status"])
                raise RuntimeError("No se encontró docker-compose.yml")
            
            project = _get_compose_project_name(service)
            cmd = _compose_cmd() + ["-p", project, "-f", str(compose_path), "stop"]
            
            subprocess.run(
                cmd,
                cwd=str(workspace),
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Actualizar estado de todos los ServiceContainer
            service.containers.all().update(status="stopped")
            
            service.status = "stopped"
            _append_log(service, "docker-compose stop completado.")
            service.save()
            
        except subprocess.CalledProcessError as e:
            error_msg = (e.stderr or e.stdout or str(e)).strip()
            service.status = "error"
            _append_log(service, f"Error al detener compose: {error_msg}")
            service.save()
            raise RuntimeError(f"Error al detener docker-compose: {error_msg}")
        except Exception as e:
            service.status = "error"
            _append_log(service, f"Error al detener: {str(e)}")
            service.save()
            raise
    else:
        # ===== MODO SIMPLE: Detener contenedor único =====
        if service.container_id:
            try:
                container = docker_client.containers.get(service.container_id)
                container.stop(timeout=10)  # Timeout de 10 segundos
                
                # Verificar que realmente se detuvo
                container.reload()
                docker_status = (container.status or "").lower()
                
                if docker_status in {"exited", "stopped"}:
                    service.status = "stopped"
                    _append_log(service, "Contenedor detenido correctamente.")
                else:
                    service.status = "stopped"  # Asumir detenido aunque el estado sea otro
                    _append_log(service, f"Contenedor en estado '{docker_status}', marcado como detenido.")
                
                service.save()
                
            except NotFound:
                service.status = "removed"
                _append_log(service, "Contenedor no encontrado, marcado como eliminado.")
                service.save()
            except DockerException as exc:
                service.status = "error"
                _append_log(service, f"Error al detener: {str(exc)}")
                service.save()
                raise
        else:
            # No hay container_id, marcar como stopped
            service.status = "stopped"
            service.save()


def _stop_container_worker(service_id: int) -> None:
    """Worker que ejecuta stop_container en background."""
    service = None
    try:
        service = Service.objects.get(pk=service_id)
        stop_container(service)
    except Service.DoesNotExist:
        return
    except Exception as exc:
        if service:
            try:
                service.status = "error"
                _append_log(service, f"Error al detener: {str(exc)}")
                service.save(update_fields=["status", "logs", "updated_at"])
            except:
                pass
        print(f"[error] Excepción en _stop_container_worker: {exc}")
        import traceback
        traceback.print_exc()


def stop_container_async(service: Service) -> None:
    """
    Encola la detención del servicio para no bloquear el hilo HTTP.
    """
    # Cambiar estado a 'stopping' inmediatamente
    service.status = "stopping"
    _append_log(service, "Deteniendo servicio...")
    service.save(update_fields=["status", "logs", "updated_at"])
    
    # Ejecutar en background
    EXECUTOR.submit(_stop_container_worker, service.pk)


def remove_container(service: Service):
    """
    Elimina el servicio completamente.
    
    MODO SIMPLE: Elimina contenedor, volumen, imagen (si fue construida) y libera puerto
    MODO COMPOSE: Usa docker compose down --rmi local --volumes para limpieza completa
    """
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no está disponible para eliminar el servicio.")

    # Pequeño delay para que el auto-refresh capture el estado 'deleting'
    import time
    time.sleep(1.5)

    if service.has_compose:
        # ===== MODO COMPOSE: Usar docker compose down =====
        try:
            workspace = ensure_service_workspace(service)
            compose_path = workspace / "docker-compose.yml"
            
            if compose_path.exists():
                project = _get_compose_project_name(service)
                cmd = _compose_cmd() + [
                    "-p", project,
                    "-f", str(compose_path),
                    "down",
                    "--rmi", "local",  # Solo eliminar imágenes construidas localmente
                    "--volumes"         # Eliminar volúmenes
                ]
                
                subprocess.run(
                    cmd,
                    cwd=str(workspace),
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            
            # Liberar puertos de todos los contenedores
            for sc in service.containers.all():
                for port_info in sc.assigned_ports or []:
                    external = port_info.get("external")
                    if external:
                        _release_port(external)
            
            # Eliminar registros de ServiceContainer
            service.containers.all().delete()
            
            # Limpiar volúmenes huérfanos (anónimos no eliminados por --volumes)
            try:
                prune_cmd = ["docker", "volume", "prune", "-f"]
                subprocess.run(
                    prune_cmd,
                    check=False,  # No fallar si no hay volúmenes que limpiar
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                _append_log(service, "Volúmenes huérfanos limpiados")
            except Exception as e:
                # No es crítico si falla
                _append_log(service, f"Advertencia al limpiar volúmenes: {str(e)}")
            
        except subprocess.CalledProcessError as e:
            error_msg = (e.stderr or e.stdout or str(e)).strip()
            _append_log(service, f"Error al eliminar compose: {error_msg}")
            service.save(update_fields=["logs"])
            # Continuar con limpieza aunque falle
        except Exception as e:
            _append_log(service, f"Error al eliminar: {str(e)}")
            service.save(update_fields=["logs"])
        
        # Limpiar workspace
        cleanup_service_workspace(service)
        
    else:
        # ===== MODO SIMPLE: Limpieza manual =====
        # Eliminar contenedor principal
        if service.container_id:
            try:
                container = docker_client.containers.get(service.container_id)
                container.remove(force=True)
            except NotFound:
                pass
            except DockerException as exc:
                _append_log(service, f"Error al eliminar el contenedor: {exc}")
                service.save(update_fields=["logs"])

        # Liberar puerto
        _release_port(service.assigned_port)

        # Eliminar volumen
        if service.volume_name:
            try:
                volume = docker_client.volumes.get(service.volume_name)
                volume.remove(force=True)
            except NotFound:
                pass
            except DockerException as exc:
                _append_log(service, f"Error al eliminar el volumen: {exc}")
                service.save(update_fields=["logs"])
        
        # Eliminar imagen si fue construida con Dockerfile
        if service.dockerfile:
            slug = _service_slug(service)
            image_tag = f"svc_{service.id}_{slug}_image"
            try:
                docker_client.images.remove(image_tag, force=True)
            except NotFound:
                pass
            except DockerException as exc:
                _append_log(service, f"Error al eliminar imagen: {exc}")
                service.save(update_fields=["logs"])
        
        # Limpiar workspace
        cleanup_service_workspace(service)

    service.container_id = None
    service.assigned_port = None
    service.volume_name = None
    service.status = "removed"
    service.save()


def _remove_container_worker(service_id: int) -> None:
    """Worker que ejecuta remove_container en background."""
    service = None
    try:
        service = Service.objects.get(pk=service_id)
        remove_container(service)
    except Service.DoesNotExist:
        return
    except Exception as exc:
        if service:
            try:
                service.status = "error"
                _append_log(service, f"Error al eliminar: {str(exc)}")
                service.save(update_fields=["status", "logs", "updated_at"])
            except:
                pass
        print(f"[error] Excepción en _remove_container_worker: {exc}")
        import traceback
        traceback.print_exc()


def remove_container_async(service: Service) -> None:
    """
    Encola la eliminación del servicio para no bloquear el hilo HTTP.
    """
    # Cambiar estado a 'deleting' inmediatamente
    service.status = "deleting"
    _append_log(service, "Eliminando servicio...")
    service.save(update_fields=["status", "logs", "updated_at"])
    
    # Ejecutar en background
    EXECUTOR.submit(_remove_container_worker, service.pk)


# ==================== SERVICE CONTAINER OPERATIONS ====================

def start_service_container_record(container_record: ServiceContainer):
    """Inicia un contenedor específico de compose"""
    docker_client = get_docker_client()
    if not docker_client or not container_record.container_id:
        raise RuntimeError("No se puede iniciar el contenedor.")
    
    try:
        docker_client.containers.get(container_record.container_id).start()
        container_record.status = "running"
        container_record.save()
    except NotFound:
        container_record.status = "removed"
        container_record.save()
        raise RuntimeError("El contenedor no existe.")
    except DockerException as exc:
        raise RuntimeError(f"Error al iniciar el contenedor: {exc}")


def stop_service_container_record(container_record: ServiceContainer):
    """Detiene un contenedor específico de compose"""
    docker_client = get_docker_client()
    if not docker_client or not container_record.container_id:
        raise RuntimeError("No se puede detener el contenedor.")
    
    try:
        docker_client.containers.get(container_record.container_id).stop()
        container_record.status = "stopped"
        container_record.save()
    except NotFound:
        container_record.status = "removed"
        container_record.save()
        raise RuntimeError("El contenedor no existe.")
    except DockerException as exc:
        raise RuntimeError(f"Error al detener el contenedor: {exc}")


def fetch_container_logs(container_record: ServiceContainer, tail: int = 200) -> str:
    """Obtiene logs de un contenedor específico"""
    docker_client = get_docker_client()
    if not docker_client or not container_record.container_id:
        return "(contenedor no disponible)"
    
    try:
        container = docker_client.containers.get(container_record.container_id)
        return container.logs(tail=tail).decode(errors="replace")
    except NotFound:
        return "(contenedor no encontrado)"
    except DockerException as exc:
        return f"(error obteniendo logs: {exc})"
