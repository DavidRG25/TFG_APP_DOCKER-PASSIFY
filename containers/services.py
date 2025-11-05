# containers/services.py
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

from django.db import IntegrityError, transaction

from docker.errors import APIError, DockerException, NotFound

from .docker_client import get_docker_client
from .models import PortReservation, Service

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MiB
COMPOSE_EXTENSIONS = {".yml", ".yaml"}
CODE_EXTENSIONS = {".zip"}

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


def _unpack_code_zip_to(target_dir: str, ff) -> None:
    """
    Descomprime un ZIP de cÃ³digo a 'target_dir'.
    """
    os.makedirs(target_dir, exist_ok=True)
    # Guardar ZIP a temp antes de descomprimir
    zpath = os.path.join(target_dir, "_code.zip")
    _save_filefield_to(zpath, ff)
    shutil.unpack_archive(zpath, target_dir)
    os.remove(zpath)


# ---------- FunciÃ³n principal ----------

def _run_container_internal(
    service: Service,
    *,
    force_restart: bool = False,
    custom_port: int | None = None,
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
                port = PortReservation.reserve_free_port()

        # --------- Caso docker-compose ---------
        if service.compose:
            with tempfile.TemporaryDirectory() as tmpdir:
                compose_path = os.path.join(tmpdir, "docker-compose.yml")
                _save_filefield_to(compose_path, service.compose)

                # Si hay cÃ³digo, lo descomprimimos como contexto de trabajo (p.ej. ./app)
                if service.code:
                    _unpack_code_zip_to(os.path.join(tmpdir, "app"), service.code)

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
        if service.dockerfile:
            with tempfile.TemporaryDirectory() as builddir:
                dockerfile_path = os.path.join(builddir, "Dockerfile")
                _save_filefield_to(dockerfile_path, service.dockerfile)

                if service.code:
                    _unpack_code_zip_to(builddir, service.code)

                image_tag = f"{service.owner.username}/{service.name}:{port or 'latest'}"
                try:
                    proc = subprocess.run(
                        ["docker", "build", "-t", image_tag, builddir],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    build_out = (proc.stdout or "") + "\n" + (proc.stderr or "")
                except subprocess.CalledProcessError as e:
                    service.status = "error"
                    service.logs = (e.stderr or e.stdout or str(e)).strip()
                    service.save()
                    raise RuntimeError(f"Error al construir la imagen:\n{service.logs}")

                image_to_run = image_tag
        else:
            # --------- Caso imagen directa del catÃ¡logo ---------
            image_to_run = service.image

        # --------- Variables y volÃºmenes (para no-compose) ---------
        volumes = {}
        # Montaje de /app si se subiÃ³ un ZIP (nota: en runtime un ZIP no sirve; aquÃ­ solo se expone el archivo)
        # Para casos reales, se recomienda usar Dockerfile o compose con COPY en build.
        if service.code and hasattr(service.code, "path"):
            volumes[service.code.path] = {"bind": "/app", "mode": "rw"}

        user_vols = service.volumes or {}
        if isinstance(user_vols, dict):
            volumes.update(user_vols)

        env_vars = service.env_vars or {}
        if not isinstance(env_vars, dict):
            env_vars = {}

        # Puerto interno configurable (si aÃ±adÃ­s el campo al modelo); por defecto 80
        internal_port = getattr(service, "internal_port", 80)

        container = docker_client.containers.run(
            image=image_to_run,
            detach=True,
            tty=True,
            stdin_open=True,                 # importante para la terminal
            name=f"{service.owner.username}_{service.name}_{port or 'auto'}",
            ports={f"{internal_port}/tcp": port} if port else None,
            volumes=volumes or None,
            environment=env_vars or None,
            working_dir="/app" if volumes else None,
        )

        service.container_id = container.id
        service.assigned_port = port
        service.status = "running"
        # Guardar build logs si venÃ­a de Dockerfile
        if service.dockerfile:
            service.logs = (service.logs or "") + "\nImagen construida y contenedor arrancado."
        service.save()

    except (APIError, DockerException, RuntimeError, ValueError) as exc:
        _release_port(port)
        service.status = "error"
        service.logs = str(exc)
        service.save()
        raise


def _run_container_worker(service_id: int, force_restart: bool, custom_port: int | None) -> None:
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return
    _run_container_internal(service, force_restart=force_restart, custom_port=custom_port)


def run_container(
    service: Service,
    force_restart: bool = False,
    custom_port: int | None = None,
    enqueue: bool = True,
) -> None:
    """
    Encola la ejecucion del contenedor para no bloquear el hilo que atiende la peticion.
    """
    if not enqueue:
        _run_container_internal(service, force_restart=force_restart, custom_port=custom_port)
        return

    service.status = "pending"
    service.logs = (service.logs or "") + "\nEjecucion encolada."
    service.save(update_fields=["status", "logs", "updated_at"])
    EXECUTOR.submit(_run_container_worker, service.pk, force_restart, custom_port)


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
    if service.container_id:
        try:
            docker_client = get_docker_client()
            if docker_client is None:
                raise RuntimeError("Docker no estÃ¡ disponible para eliminar el servicio.")
            docker_client.containers.get(service.container_id).remove(force=True)
        except NotFound:
            pass
        except (DockerException, RuntimeError) as exc:
            service.logs = str(exc)
            service.save()
            raise

    _release_port(service.assigned_port)

    service.container_id = None
    service.assigned_port = None
    service.status = "removed"
    service.save()
