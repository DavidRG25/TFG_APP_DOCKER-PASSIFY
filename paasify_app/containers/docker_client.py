"""Utilidades centralizadas para obtener clientes Docker de forma segura."""
from __future__ import annotations

import os
import docker
from docker.errors import DockerException
import logging

logger = logging.getLogger(__name__)

# Cache global para el cliente Docker autenticado
_docker_client_cache: docker.DockerClient | None = None
_docker_auth_attempted: bool = False


def get_docker_client() -> docker.DockerClient | None:
    """Devuelve un cliente Docker si el daemon está disponible.
    
    Si las variables DOCKER_HUB_USERNAME y DOCKER_HUB_PASSWORD están configuradas
    en el entorno, se intentará autenticar con Docker Hub para aumentar el límite
    de pulls de 100 a 200 por cada 6 horas.
    
    El cliente se cachea para evitar múltiples autenticaciones innecesarias.

    La función captura ``DockerException`` para evitar que la importación del
    módulo falle cuando el daemon no está accesible (entornos CI, desarrollo sin
    Docker, etc.). En caso de no poder establecer la conexión se devuelve
    ``None`` para que las capas superiores decidan cómo reaccionar.
    """
    global _docker_client_cache, _docker_auth_attempted
    
    # Si ya tenemos un cliente cacheado, devolverlo
    if _docker_client_cache is not None:
        return _docker_client_cache
    
    try:
        client = docker.from_env()
        
        # Intentar autenticación con Docker Hub si hay credenciales (solo una vez)
        if not _docker_auth_attempted:
            _docker_auth_attempted = True
            
            docker_username = os.environ.get("DOCKER_HUB_USERNAME", "").strip()
            docker_password = os.environ.get("DOCKER_HUB_PASSWORD", "").strip()
            
            if docker_username and docker_password:
                try:
                    client.login(
                        username=docker_username,
                        password=docker_password,
                        registry="https://index.docker.io/v1/"
                    )
                    logger.info(f"✓ Autenticado en Docker Hub como '{docker_username}'")
                except Exception as e:
                    # Si falla el login, continuamos sin autenticación
                    logger.warning(f"No se pudo autenticar en Docker Hub: {e}")
        
        # Cachear el cliente para futuras llamadas
        _docker_client_cache = client
        return client
    except (DockerException, OSError):
        return None

