# containers/services.py
import os
import random
import re
import shutil
import subprocess

import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.conf import settings
from django.db import IntegrityError, transaction

from docker import DockerClient
from docker.errors import APIError, DockerException, NotFound

from .docker_client import get_docker_client
from .models import PORT_RANGE_END, PORT_RANGE_START, PortReservation, Service

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
    raise RuntimeError("No se encontrÃ³ 'docker compose' (v2) ni 'docker-compose' (v1).")


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

    Si el contenedor termina inmediatamente (estado exited/dead) registramos los logs,
    liberamos el puerto reservado y lanzamos una excepción para notificar al usuario.
    """
    try:
        container.reload()
        status = (container.status or "").lower()
    except DockerException:
        return

    if status not in {"running"}:
        try:
            log_tail = container.logs(tail=200).decode(errors="replace")
        except Exception:
            log_tail = "(logs no disponibles)"
        service.status = "error"
        _append_log(service, f"[Docker] {log_tail}".strip())
        service.save(update_fields=["status", "logs"])
        try:
            container.remove(force=True)
        except DockerException:
            pass
        _release_port(reserved_port)
        raise RuntimeError("El contenedor finalizó inmediatamente. Revisa los logs para más detalles.")


# ---------- Utilidades de ficheros ----------

def _validate_upload(ff, *, allowed_extensions=None, max_size=MAX_UPLOAD_SIZE):
    """Valida tamaÃ±o y extensiÃ³n permitida para un ``FieldFile``."""
    if ff is None:
        return

    if max_size and getattr(ff, "size", None) and ff.size > max_size:
        raise ValueError(
            f"El archivo '{getattr(ff, 'name', 'desconocido')}' supera el tamaÃ±o mÃ¡ximo permitido ({max_size // (1024 * 1024)} MiB)."
        )

    if allowed_extensions is not None:
        name = getattr(ff, "name", "") or ""
        extension = os.path.splitext(name)[1].lower()
        if extension not in allowed_extensions:
            allowed = ", ".join(sorted(ext or 'sin extensiÃ³n' for ext in allowed_extensions))
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
        proc_test = subprocess.run(test_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("El archivo RAR esta incompleto o dañado. Intentalo de nuevo.") from exc
    if proc_test.stdout:
        _ = proc_test.stdout  # silencio lint

    try:
        subprocess.run(extract_cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("El archivo RAR esta incompleto o dañado. Intentalo de nuevo.") from exc


# ---------- FunciÃ³n principal ----------

def _run_container_internal(
    service: Service,
    *,
    force_restart: bool = False,
    custom_port: int | None = None,
    command: list[str] | None = None,
):
    """
    Arranca (o rearma) el contenedor asociado a un Service.
    Prioridad:
      1) docker-compose (si se subiÃ³)
      2) Dockerfile       (si se subiÃ³)
      3) Imagen permitida (catÃ¡logo)
    """
    docker_client = get_docker_client()
    if docker_client is None:
        service.status = "error"
        service.logs = "Docker no estÃ¡ disponible. Inicia el daemon y vuelve a intentarlo."
        service.save()
        raise RuntimeError("Docker no estÃ¡ disponible en el entorno de ejecuciÃ³n.")

    try:
        if service.compose:
            _validate_upload(service.compose, allowed_extensions=COMPOSE_EXTENSIONS)
        if service.code:
            _validate_upload(service.code, allowed_extensions=CODE_EXTENSIONS)
        if service.dockerfile:
            # Dockerfile admite nombres sin extensiÃ³n, por lo que solo se valida tamaÃ±o.
            _validate_upload(service.dockerfile, allowed_extensions=None)
    except ValueError as exc:
        service.status = "error"
        service.logs = str(exc)
        service.save()
        raise

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

        # Si ya existe y no es reinicio, asegurar que estÃ© en marcha y salir
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

        # --------- Reserva de puerto (solo para caso NO compose) ---------
        # custom_port es proporcionado por la vista al encolar la tarea.
        if service.compose:
            # docker-compose maneja puertos por su YAML; no reservamos aqui
            pass
        else:
            if custom_port:
                _reserve_specific_port(custom_port)
                port = custom_port
            else:
                port = _reserve_random_port()
            service.assigned_port = port
            service.save(update_fields=["assigned_port"])

        # --------- Caso docker-compose ---------
        if service.compose:
            with tempfile.TemporaryDirectory() as tmpdir:
                compose_path = os.path.join(tmpdir, "docker-compose.yml")
                _save_filefield_to(compose_path, service.compose)

                # Si hay cÃ³digo, lo descomprimimos como contexto de trabajo (p.ej. ./app)
                if service.code:
                    _unpack_code_archive_to(os.path.join(tmpdir, "app"), service.code)

                # Nombre de proyecto Ãºnico para poder localizar el contenedor
                project = f"svc{service.id}"

                try:
                    cmd = _compose_cmd() + ["-p", project, "-f", compose_path, "up", "--build", "-d"]
                    proc = subprocess.run(
                        cmd, check=True, cwd=tmpdir, capture_output=True, text=True
                    )
                    stdout = proc.stdout or ""
                    stderr = proc.stderr or ""
                except subprocess.CalledProcessError as e:
                    service.status = "error"
                    service.logs = (e.stderr or e.stdout or str(e)).strip()
                    service.save()
                    raise RuntimeError(f"Error al ejecutar docker compose:\n{service.logs}")

                # Buscar contenedor por labels del proyecto compose
                # Tomamos el primero (suponemos un Ãºnico servicio en el YAML para este MVP)
                containers = docker_client.containers.list(
                    all=True, filters={"label": f"com.docker.compose.project={project}"}
                )
                if not containers:
                    service.status = "error"
                    service.logs = "docker-compose: no se detectÃ³ ningÃºn contenedor con el proyecto especificado."
                    service.save()
                    raise RuntimeError(service.logs)

                container = containers[0]
                service.container_id = container.id
                service.status = "running"
                service.assigned_port = None  # Puertos quedan definidos en el YAML
                # Guardar algo de log informativo
                service.logs = ("docker-compose up -d completado.\n" + stdout + "\n" + stderr).strip()
                service.save()
                return

        # --------- Caso Dockerfile ---------
        slug = _service_slug(service)

        image_cmd = None

        if service.dockerfile:
            with tempfile.TemporaryDirectory() as builddir:
                dockerfile_path = os.path.join(builddir, "Dockerfile")
                _save_filefield_to(dockerfile_path, service.dockerfile)

                if service.code:
                    _unpack_code_archive_to(builddir, service.code)

                image_tag = f"svc_{service.id}_{slug}_image"
                try:
                    proc = subprocess.run(
                        ["docker", "build", "-t", image_tag, builddir],
                        check=True,
                        capture_output=True,
                        text=True,
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
            # --------- Caso imagen directa del catÃ¡logo ---------
            image_to_run = service.image

        try:
            image_attrs = docker_client.images.get(image_to_run).attrs
            image_cmd = image_attrs.get("Config", {}).get("Cmd") or None
        except DockerException:
            image_cmd = None

        # --------- Variables y volÃºmenes (para no-compose) ---------
        volume_name = service.volume_name or f"svc_{service.id}_{slug}_data"
        try:
            docker_client.volumes.create(name=volume_name)
        except APIError as e:
            if e.response.status_code != 409:  # 409 es 'conflicto', el volumen ya existe (OK)
                raise RuntimeError(f"No se pudo crear el volumen '{volume_name}': {e}")
        service.volume_name = volume_name
        volumes = {volume_name: {"bind": "/data", "mode": "rw"}}

        user_vols = service.volumes or {}
        if isinstance(user_vols, dict):
            volumes.update(user_vols)

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
        container_name = f"svc_{service.id}_{slug}_ctr"

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


# ---------- Stop / Remove ----------

def stop_container(service: Service):
    if not service.container_id:
        return
    try:
        docker_client = get_docker_client()
        if docker_client is None:
            raise RuntimeError("Docker no estÃ¡ disponible para detener el servicio.")
        docker_client.containers.get(service.container_id).stop()
        service.status = "stopped"
        service.save()
    except NotFound:
        service.status = "removed"
        service.save()
    except (DockerException, RuntimeError) as exc:
        service.logs = str(exc)
        service.save()
        raise


def remove_container(service: Service):
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no está disponible para eliminar el servicio.")

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

    # Liberar puertos
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

    service.container_id = None
    service.assigned_port = None
    service.volume_name = None
    service.status = "removed"
    service.save()
