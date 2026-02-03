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
    max_workers=int(os.environ.get("SERVICE_WORKERS", "2"))
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
    from django.conf import settings
    from django.db import models

    sid = str(service.id)
    try:
        media_path = Path(settings.MEDIA_ROOT)
        
        # 1. Barredora de directorios de carga (dockerfiles, compose_files, user_code)
        for subdir in ["dockerfiles", "compose_files", "user_code"]:
            base_dir = media_path / subdir
            if not base_dir.exists(): continue
            
            # A. Borrar carpeta services/<id> si existe
            path_id = base_dir / "services" / sid
            if path_id.exists():
                for attempt in range(3):
                    try:
                        if os.name == 'nt':
                            for root, dirs, files in os.walk(path_id):
                                for d in dirs:
                                    try: os.chmod(os.path.join(root, d), stat.S_IRWXU)
                                    except: pass
                                for f in files:
                                    try: os.chmod(os.path.join(root, f), stat.S_IRWXU)
                                    except: pass
                        shutil.rmtree(path_id)
                        break
                    except:
                        time.sleep(1)

            # B. Limpiar archivos huérfanos (los que Django renombra con sufijos aleatorios)
            for item in base_dir.iterdir():
                if item.is_file():
                    iname = item.name.lower()
                    is_huerfano = False
                    
                    # Pattern matching: si lleva el ID o es un nombre genérico
                    if f"_{sid}" in iname:
                        is_huerfano = True
                    elif any(iname.startswith(p) for p in ["docker-compose", "dockerfile", "source"]):
                        # Verificación de match EXACTO en base de datos
                        django_rel_path = f"{subdir}/{item.name}"
                        from containers.models import Service as SModel
                        if not SModel.objects.filter(
                            models.Q(compose=django_rel_path) | 
                            models.Q(code=django_rel_path) | 
                            models.Q(dockerfile=django_rel_path)
                        ).exclude(id=service.id).exists():
                            is_huerfano = True
                    
                    if is_huerfano:
                        try: item.unlink()
                        except: pass
    except Exception:
        pass

    # 2. Limpiar el workspace principal (media/services/<id>)
    workspace = SERVICE_WORKSPACES_ROOT / sid
    if workspace.exists():
        for attempt in range(3):
            try:
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
            except:
                if attempt < 2: time.sleep(1)
                else: shutil.rmtree(workspace, ignore_errors=True)


def prepare_service_workspace(service: Service, *, unpack_code: bool = True) -> Path:
    """
    Prepara el workspace del servicio asegurando que:
    1. Todos los archivos (Dockerfile, docker-compose.yml) estén en services/<id>/
    2. El código fuente esté descomprimido según el modo:
       - Dockerfile: descomprime en services/<id>/ (mismo nivel que Dockerfile)
       - Compose: descomprime en services/<id>/src/
    
    Retorna el Path del workspace.
    """
    workspace = ensure_service_workspace(service)
    
    # Mapeo de campos FileField a nombres de archivo esperados
    mapping = {
        "dockerfile": "Dockerfile",
        "compose": "docker-compose.yml",
    }
    updated_fields = []
    
    for field, filename in mapping.items():
        ff = getattr(service, field, None)
        if not ff:
            continue
        
        # Ruta esperada en el workspace
        desired_rel = f"services/{service.pk}/{filename}"
        
        # Si el FileField no apunta a la ruta correcta, moverlo
        if ff.name != desired_rel:
            with ff.open("rb") as fh:
                getattr(service, field).save(desired_rel, fh, save=False)
            updated_fields.append(field)
        
        # Asegurar que existe una copia física en el workspace
        dest = workspace / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        with ff.open("rb") as source, open(dest, "wb") as target:
            shutil.copyfileobj(source, target)
    
    if updated_fields:
        service.save(update_fields=updated_fields)
    
    # Descomprimir código si existe
    if unpack_code and service.code:
        code_ext = os.path.splitext(service.code.name or "")[1] or ".zip"
        code_rel = f"services/{service.pk}/source{code_ext}"
        if service.code.name != code_rel:
            with service.code.open("rb") as fh:
                service.code.save(code_rel, fh, save=False)
            service.save(update_fields=["code"])
        
        # SIEMPRE descomprimir en la raíz del workspace
        # Esto funciona para:
        # - Dockerfile: COPY requirements.txt funciona
        # - Compose: build context "." encuentra Dockerfile y archivos
        code_target = workspace
        
        # Limpiar archivos de código previos pero mantener Dockerfile/compose
        for item in workspace.iterdir():
            if item.name not in ["Dockerfile", "docker-compose.yml", "source.zip", "source.rar"]:
                if item.is_file():
                    item.unlink()
                elif item.is_dir() and item.name not in [".vs"]:
                    shutil.rmtree(item)
        
        _unpack_code_archive_to(str(code_target), service.code)
    
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


def _unpack_code_archive_to(target_dir: str, ff) -> None:
    """
    Descomprime un archivo de codigo (zip o rar) a 'target_dir'.
    """
    os.makedirs(target_dir, exist_ok=True)
    name = getattr(ff, "name", "") or ""
    extension = os.path.splitext(name)[1].lower()
    tmp_path = os.path.join(target_dir, f"_code{extension or '.tmp'}")
    _save_filefield_to(tmp_path, ff)

    if extension == ".rar":
        try:
            _extract_rar_with_tool(tmp_path, target_dir)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return

    try:
        shutil.unpack_archive(tmp_path, target_dir)
    except Exception as exc:
        raise RuntimeError(f"No se pudo descomprimir el archivo: {exc}") from exc
    finally:
        os.remove(tmp_path)


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
    try:
        workspace = prepare_service_workspace(service)
        compose_path = workspace / "docker-compose.yml"
        
        if not compose_path.exists():
            raise RuntimeError("No se encontró docker-compose.yml en el workspace del servicio.")
        
        # Cargar y procesar puertos
        data = _load_compose_data(compose_path)
        previous_ports = _previous_port_assignments(service)
        reserved_ports = _ensure_compose_ports(data, previous_ports)
        
        # Guardar el YAML modificado con puertos asignados
        with compose_path.open("w", encoding="utf-8") as fh:
            yaml.dump(data, fh)
        
        # Ejecutar docker compose desde workspace
        project = _get_compose_project_name(service)
        cmd = _compose_cmd() + ["-p", project, "-f", str(compose_path), "up", "--build", "-d"]
        
        _append_log(service, f"Ejecutando: {' '.join(cmd)}")
        _append_log(service, f"Workspace: {workspace}")
        service.save(update_fields=["logs"])
        
        proc = subprocess.run(
            cmd, 
            cwd=str(workspace),  # ← IMPORTANTE: ejecutar desde workspace
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',  # ← FIX: Evitar UnicodeDecodeError en Windows
            errors='replace'    # ← FIX: Reemplazar caracteres inválidos
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        
        _append_log(service, f"STDOUT: {stdout}")
        _append_log(service, f"STDERR: {stderr}")
        service.save(update_fields=["logs"])
        
    except subprocess.CalledProcessError as e:
        # Liberar puertos reservados si falla
        for port in reserved_ports:
            _release_port(port)
        service.status = "error"
        error_msg = (e.stderr or e.stdout or str(e)).strip()
        _append_log(service, f"ERROR subprocess: {error_msg}")
        service.save()
        raise RuntimeError(f"Error al ejecutar docker compose:\n{error_msg}")
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
    service.status = "running"
    _append_log(service, "docker-compose up -d completado.")
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
                container = docker_client.containers.get(service.container_id)
                if container.status != "running":
                    container.start()
                    service.status = "running"
                    service.save()
                return
            except NotFound:
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
            try:
                proc = subprocess.run(
                    ["docker", "build", "-t", image_tag, str(workspace)],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                build_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
            except subprocess.CalledProcessError as e:
                build_out = (e.stdout or "") + "\n" + (e.stderr or "")
                service.status = "error"
                service.logs = build_out.strip() or str(e)
                service.save(update_fields=["status", "logs"])
                raise RuntimeError(f"Error al construir la imagen:\n{service.logs}")

            image_to_run = image_tag
            service.logs = ("docker build completado.\n" + build_out).strip()
            service.save(update_fields=["logs"])
        else:
            # --------- Caso imagen directa del catálogo ---------
            image_to_run = service.image

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
        container_name = f"{safe_name}_ctr"

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
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return
    _run_container_internal(
        service, force_restart=force_restart, custom_port=custom_port, command=command
    )


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


def remove_container(service: Service):
    """
    Elimina el servicio completamente.
    
    MODO SIMPLE: Elimina contenedor, volumen, imagen (si fue construida) y libera puerto
    MODO COMPOSE: Usa docker compose down --rmi local --volumes para limpieza completa
    """
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no está disponible para eliminar el servicio.")

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
