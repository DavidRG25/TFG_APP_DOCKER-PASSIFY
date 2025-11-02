"""Utilidades centralizadas para obtener clientes Docker de forma segura."""
from __future__ import annotations

import docker
from docker.errors import DockerException


def get_docker_client() -> docker.DockerClient | None:
    """Devuelve un cliente Docker si el daemon está disponible.

    La función captura ``DockerException`` para evitar que la importación del
    módulo falle cuando el daemon no está accesible (entornos CI, desarrollo sin
    Docker, etc.). En caso de no poder establecer la conexión se devuelve
    ``None`` para que las capas superiores decidan cómo reaccionar.
    """
    try:
        client = docker.from_env()
        # ``ping`` valida la conexión sin ejecutar operaciones destructivas.
        client.ping()
        return client
    except DockerException:
        return None
