# containers/services.py
import os
import shutil
import tempfile
import subprocess
import random
import re
import yaml

import docker
from docker.errors import NotFound, APIError

from .models import Service, PortReservation

client = docker.from_env()

PORT_RANGE_START = 40000
PORT_RANGE_END = 50000

# Carpeta persistente para código descomprimido en modo "imagen por defecto"
USER_CODE_ROOT = os.path.join(os.getcwd(), "user_code")
os.makedirs(USER_CODE_ROOT, exist_ok=True)


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


# ---------- Utilidades varias ----------

_slug_rx = re.compile(r"[^a-z0-9_.-]+")


def _slug(s: str) -> str:
    """Slug muy permisivo (lower, reemplaza espacios/caracteres raros por '-')."""
    return _slug_rx.sub("-", (s or "").strip().lower()).strip("-") or "svc"


def _infer_internal_port(image_ref: str | None, fallback: int = 80) -> int:
    """
    Dado un nombre de imagen (p.ej. 'mysql:8'), infiere el puerto interno más común.
    Si no se reconoce, devuelve 'fallback'.
    """
    ref = (image_ref or "").lower()
    if "mysql" in ref:
        return 3306
    if "postgres" in ref or "postgis" in ref:
        return 5432
    if "redis" in ref:
        return 6379
    if "mongo" in ref:
        return 27017
    if "mariadb" in ref:
        return 3306
    if "rabbitmq" in ref:
        return 5672
    if "elasticsearch" in ref:
        return 9200
    if "kibana" in ref:
        return 5601
    if "nginx" in ref or "httpd" in ref or "apache" in ref or "caddy" in ref:
        return 80
    if "node" in ref or "express" in ref:
        return 3000
    if "phpmyadmin" in ref:
        return 80
    return fallback


# ---------- Utilidades de puertos ----------

def _reserve_free_port() -> int:
    """Reserva un puerto libre dentro del rango configurado."""
    for _ in range(2000):
        port = random.randint(PORT_RANGE_START, PORT_RANGE_END)
        if not PortReservation.objects.filter(port=port).exists():
            PortReservation.objects.create(port=port)
            return port
    raise RuntimeError("No free ports available in defined range")


def _release_port(port: int | None):
    if port:
        PortReservation.objects.filter(port=port).delete()


# ---------- Utilidades de ficheros ----------

def _save_filefield_to(tmp_path: str, ff) -> str:
    """Guarda el contenido de un FileField en 'tmp_path' y devuelve esa ruta."""
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    with ff.open("rb"):
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(ff, out)
    return tmp_path


def _unpack_zip_to_dir(target_dir: str, ff) -> str:
    """
    Descomprime un ZIP en 'target_dir' (limpiándolo antes). Devuelve la ruta del dir.
    """
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, exist_ok=True)
    zpath = os.path.join(target_dir, "_code.zip")
    _save_filefield_to(zpath, ff)
    shutil.unpack_archive(zpath, target_dir)
    os.remove(zpath)
    return target_dir


# ---------- Compose helpers ----------

def _compose_detect_context(compose_yaml_path: str) -> str | None:
    """
    Lee docker-compose.yml y devuelve un 'build.context' si lo hay.
    - Si 'build: .' o 'build: {context: "."}', devuelve "."
    - Si no hay build, devuelve None
    """
    try:
        with open(compose_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return None

    services = data.get("services") or {}
    for _svc_name, svc in services.items():
        if isinstance(svc, dict) and "build" in svc:
            build = svc["build"]
            if isinstance(build, str):
                # build: "."
                return build.strip() or "."
            if isinstance(build, dict):
                ctx = build.get("context")
                if isinstance(ctx, str) and ctx.strip():
                    return ctx.strip()
                # build sin context => se asume "."
                return "."
    return None


# ---------- Función principal ----------

def run_container(service: Service, force_restart: bool = False):
    """
    Arranca (o rearma) el contenedor asociado a un Service.
    Prioridad:
      1) docker-compose (si se subió)
      2) Dockerfile       (si se subió)
      3) Imagen permitida (catálogo)
    """
    port = None
    try:
        # Reinicio forzado: eliminar contenedor y liberar puerto
        if force_restart and service.container_id:
            try:
                client.containers.get(service.container_id).remove(force=True)
            except NotFound:
                pass
            service.container_id = None
            _release_port(service.assigned_port)
            service.assigned_port = None

        # Si ya existe (y no es reinicio), intentar arrancarlo y salir
        if service.container_id and not force_restart:
            container = client.containers.get(service.container_id)
            if container.status != "running":
                container.start()
                service.status = "running"
                service.save()
            return

        # --------- Reserva de puerto (solo para caso NO compose) ---------
        custom_port = getattr(service, "_custom_port", None)
        if service.compose:
            # docker-compose maneja puertos por su YAML
            pass
        else:
            if custom_port:
                cport = int(custom_port)
                if not (PORT_RANGE_START <= cport <= PORT_RANGE_END):
                    raise RuntimeError(f"Puerto fuera de rango ({PORT_RANGE_START}-{PORT_RANGE_END}).")
                if PortReservation.objects.filter(port=cport).exists():
                    raise RuntimeError(f"El puerto {cport} ya está en uso.")
                port = cport
                PortReservation.objects.create(port=port)
            else:
                port = _reserve_free_port()

        # --------- Caso docker-compose ---------
        if service.compose:
            with tempfile.TemporaryDirectory() as tmpdir:
                compose_path = os.path.join(tmpdir, "docker-compose.yml")
                _save_filefield_to(compose_path, service.compose)

                # Si hay código, intentar colocarlo según build.context
                if service.code:
                    context = _compose_detect_context(compose_path)
                    if context is None:
                        # No hay build, el YAML no va a usar el ZIP salvo que el propio YAML monte volúmenes.
                        # No hacemos nada especial aquí.
                        pass
                    else:
                        # Normalizamos ruta de contexto
                        ctx_path = os.path.normpath(os.path.join(tmpdir, context))
                        _unpack_zip_to_dir(ctx_path, service.code)

                project = f"svc{service.id}"

                try:
                    cmd = _compose_cmd() + ["-p", project, "-f", compose_path, "up", "--build", "-d"]
                    proc = subprocess.run(
                        cmd, cwd=tmpdir, check=True, capture_output=True, text=True
                    )
                    stdout = proc.stdout or ""
                    stderr = proc.stderr or ""
                except subprocess.CalledProcessError as e:
                    service.status = "error"
                    service.logs = (e.stderr or e.stdout or str(e)).strip()
                    service.save()
                    raise RuntimeError(f"Error al ejecutar docker compose:\n{service.logs}")

                # Tomamos el primer contenedor del proyecto
                containers = client.containers.list(
                    all=True,
                    filters={"label": f"com.docker.compose.project={project}"}
                )
                if not containers:
                    service.status = "error"
                    service.logs = "docker-compose: no se detectó ningún contenedor del proyecto."
                    service.save()
                    raise RuntimeError(service.logs)

                container = containers[0]
                service.container_id = container.id
                service.status = "running"
                service.assigned_port = None  # los puertos los define el YAML
                service.logs = ("docker-compose up -d completado.\n" + stdout + "\n" + stderr).strip()
                service.save()
                return

        # --------- Caso Dockerfile ---------
        if service.dockerfile:
            with tempfile.TemporaryDirectory() as builddir:
                dockerfile_path = os.path.join(builddir, "Dockerfile")
                _save_filefield_to(dockerfile_path, service.dockerfile)

                # El ZIP (si existe) va al build context
                if service.code:
                    _unpack_zip_to_dir(builddir, service.code)

                repo = f"{_slug(service.owner.username)}/{_slug(service.name)}"
                tag = str(port or "latest")
                image_tag = f"{repo}:{tag}"

                try:
                    proc = subprocess.run(
                        ["docker", "build", "-t", image_tag, builddir],
                        check=True, capture_output=True, text=True,
                    )
                    build_out = (proc.stdout or "") + ("\n" + (proc.stderr or "") if proc.stderr else "")
                except subprocess.CalledProcessError as e:
                    service.status = "error"
                    service.logs = (e.stderr or e.stdout or str(e)).strip()
                    service.save()
                    raise RuntimeError(f"Error al construir la imagen:\n{service.logs}")

                image_to_run = image_tag
                # Guardamos algo de log de build
                service.logs = (service.logs or "") + ("\n" + build_out if build_out else "")
        else:
            # --------- Caso imagen directa del catálogo ---------
            image_to_run = service.image

        # --------- Variables/volúmenes (NO compose) ---------
        volumes = {}

        # Si hay ZIP de código en modo "imagen por defecto", lo descomprimimos a una carpeta persistente y la montamos
        code_mount_dir = None
        if (not service.dockerfile) and (not service.compose) and service.code:
            code_mount_dir = os.path.join(USER_CODE_ROOT, f"svc{service.id}_code")
            _unpack_zip_to_dir(code_mount_dir, service.code)
            volumes[code_mount_dir] = {"bind": "/app", "mode": "rw"}

        user_vols = service.volumes or {}
        if isinstance(user_vols, dict):
            volumes.update(user_vols)

        env_vars = service.env_vars or {}
        if not isinstance(env_vars, dict):
            env_vars = {}

        # Puerto interno: usar el del modelo si existe; si no, inferir por imagen
        internal_port = getattr(service, "internal_port", None)
        if not internal_port:
            internal_port = _infer_internal_port(image_to_run, fallback=80)

        # Intentar pull para imágenes del catálogo si no existen
        try:
            client.images.pull(image_to_run)
        except Exception:
            # Si ya existe localmente, pull fallará con 404 o similar; continuamos
            pass

        # Nombre único y válido
        safe_name = f"{_slug(service.owner.username)}_{_slug(service.name)}_{_slug(str(port or 'auto'))}"

        container = client.containers.run(
            image=image_to_run,
            detach=True,
            tty=True,
            stdin_open=True,  # necesario para la terminal
            name=safe_name,
            ports={f"{internal_port}/tcp": port} if port else None,
            volumes=volumes or None,
            environment=env_vars or None,
            working_dir="/app" if code_mount_dir else None,
        )

        service.container_id = container.id
        service.assigned_port = port
        service.status = "running"
        if service.dockerfile:
            service.logs = (service.logs or "") + "\nImagen construida y contenedor arrancado."
        service.save()

    except (APIError, RuntimeError) as exc:
        _release_port(port)
        service.status = "error"
        service.logs = str(exc)
        service.save()
        raise


# ---------- Stop / Remove ----------

def stop_container(service: Service):
    if not service.container_id:
        return
    try:
        client.containers.get(service.container_id).stop()
        service.status = "stopped"
        service.save()
    except NotFound:
        service.status = "removed"
        service.save()


def remove_container(service: Service):
    if service.container_id:
        try:
            client.containers.get(service.container_id).remove(force=True)
        except NotFound:
            pass

    _release_port(service.assigned_port)

    service.container_id = None
    service.assigned_port = None
    service.status = "removed"