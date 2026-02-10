"""
Utilidades para manejo de logs de contenedores Docker.

Incluye funciones para:
- Obtener logs de contenedores
- Colorización avanzada con Rich
- Filtrado por nivel y texto
- Caché de logs
"""

import logging
from typing import List, Tuple
from django.core.cache import cache
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from io import StringIO

from .docker_client import get_docker_client
from .models import Service, ServiceContainer

logger = logging.getLogger(__name__)


def fetch_container_logs(service: Service, tail: int = 1000, since: str = None) -> Tuple[List[str], bool]:
    """
    Obtener logs del contenedor.
    
    Args:
        service: Servicio del cual obtener logs
        tail: Número de líneas a obtener (default: 1000)
        since: Timestamp desde cuando obtener logs (opcional)
    
    Returns:
        Tuple[List[str], bool]: (lista de líneas de log, es_desde_cache)
    """
    # Intentar obtener de caché
    cache_key = f"logs_{service.id}_{tail}_{since or 'all'}"
    cached_logs = cache.get(cache_key)
    
    if cached_logs:
        logger.debug(f"Logs obtenidos de caché para servicio {service.id}")
        return cached_logs, True
    
    docker_client = get_docker_client()
    if not docker_client:
        return [" ERROR: Docker no está disponible"], False
    
    logs_lines = []
    
    try:
        if service.has_compose:
            # Servicio Compose: obtener logs de todos los contenedores
            containers = ServiceContainer.objects.filter(service=service).order_by('name')
            
            for container_record in containers:
                if not container_record.container_id:
                    continue
                
                try:
                    container = docker_client.containers.get(container_record.container_id)
                    
                    # Obtener logs
                    logs_kwargs = {
                        'tail': tail,
                        'timestamps': True,
                    }
                    if since:
                        logs_kwargs['since'] = since
                    
                    container_logs = container.logs(**logs_kwargs).decode('utf-8', errors='replace')
                    
                    # Añadir header para identificar el contenedor
                    logs_lines.append(f"{'='*80}")
                    logs_lines.append(f"CONTENEDOR: {container_record.name}")
                    logs_lines.append(f"ID: {container_record.container_id[:12]}")
                    logs_lines.append(f"{'='*80}")
                    logs_lines.extend(container_logs.split('\n'))
                    logs_lines.append("")  # Línea en blanco entre contenedores
                    
                except Exception as e:
                    logger.error(f"Error obteniendo logs de contenedor {container_record.name}: {e}")
                    logs_lines.append(f"[ERROR] No se pudieron obtener logs de {container_record.name}: {e}")
        
        else:
            # Servicio simple: un solo contenedor
            if not service.container_id:
                return ["[INFO] El servicio no tiene contenedor asignado"], False
            
            try:
                container = docker_client.containers.get(service.container_id)
                
                logs_kwargs = {
                    'tail': tail,
                    'timestamps': True,
                }
                if since:
                    logs_kwargs['since'] = since
                
                container_logs = container.logs(**logs_kwargs).decode('utf-8', errors='replace')
                logs_lines = container_logs.split('\n')
                
            except Exception as e:
                logger.error(f"Error obteniendo logs de servicio {service.id}: {e}")
                return [f"[ERROR] No se pudieron obtener los logs: {e}"], False
    
    except Exception as e:
        logger.error(f"Error general obteniendo logs: {e}")
        return [f"[ERROR] Error inesperado: {e}"], False
    
    # Guardar en caché (5 minutos)
    cache.set(cache_key, logs_lines, 300)
    logger.debug(f"Logs guardados en caché para servicio {service.id}")
    
    return logs_lines, False


def colorize_logs_rich(logs: List[str]) -> str:
    """
    Colorizar logs usando la librería Rich.
    
    Detecta:
    - Niveles de log (ERROR, WARN, INFO, DEBUG)
    - JSON
    - URLs
    - IPs
    - Paths de archivos
    
    Args:
        logs: Lista de líneas de log
    
    Returns:
        str: HTML con logs colorizados
    """
    console = Console(record=True, width=120, force_terminal=True, legacy_windows=False)
    
    for line in logs:
        if not line.strip():
            console.print()
            continue
        
        line_lower = line.lower()
        
        # Detectar JSON
        if line.strip().startswith('{') or line.strip().startswith('['):
            try:
                syntax = Syntax(line, "json", theme="monokai", line_numbers=False, word_wrap=True)
                console.print(syntax)
                continue
            except:
                pass
        
        # Detectar niveles de log
        if 'error' in line_lower or 'fatal' in line_lower or 'critical' in line_lower:
            console.print(f"[bold red]🔴 {line}[/bold red]")
        elif 'warn' in line_lower or 'warning' in line_lower:
            console.print(f"[bold yellow]🟡 {line}[/bold yellow]")
        elif 'info' in line_lower:
            console.print(f"[green]🟢 {line}[/green]")
        elif 'debug' in line_lower:
            console.print(f"[blue]🔵 {line}[/blue]")
        elif line.startswith('==='):
            # Headers de contenedores
            console.print(f"[bold cyan]{line}[/bold cyan]")
        elif line.startswith('CONTENEDOR:') or line.startswith('ID:'):
            console.print(f"[bold magenta]{line}[/bold magenta]")
        else:
            console.print(line)
    
    # Exportar como HTML
    html_output = console.export_html(inline_styles=True, code_format="<pre>{code}</pre>")
    
    return html_output


def colorize_logs_simple(logs: List[str]) -> str:
    """
    Colorización simple con CSS (fallback si Rich falla).
    
    Args:
        logs: Lista de líneas de log
    
    Returns:
        str: HTML con logs colorizados
    """
    from django.utils.html import escape
    
    html_lines = []
    
    for line in logs:
        if not line.strip():
            html_lines.append('<div class="log-line"></div>')
            continue
        
        line_escaped = escape(line)
        line_lower = line.lower()
        
        # Detectar nivel
        if 'error' in line_lower or 'fatal' in line_lower:
            css_class = 'log-error'
            icon = '🔴'
        elif 'warn' in line_lower:
            css_class = 'log-warn'
            icon = '🟡'
        elif 'info' in line_lower:
            css_class = 'log-info'
            icon = '🟢'
        elif 'debug' in line_lower:
            css_class = 'log-debug'
            icon = '🔵'
        elif line.startswith('==='):
            css_class = 'log-header'
            icon = ''
        else:
            css_class = 'log-default'
            icon = ''
        
        html_lines.append(f'<div class="log-line {css_class}">{icon} {line_escaped}</div>')
    
    return '\n'.join(html_lines)


def filter_logs(logs: List[str], search_text: str) -> List[str]:
    """
    Filtrar logs por texto de búsqueda.
    
    Args:
        logs: Lista de líneas de log
        search_text: Texto a buscar (case-insensitive)
    
    Returns:
        List[str]: Logs filtrados
    """
    if not search_text:
        return logs
    
    search_lower = search_text.lower()
    return [line for line in logs if search_lower in line.lower()]


def filter_by_level(logs: List[str], level: str) -> List[str]:
    """
    Filtrar logs por nivel.
    
    Args:
        logs: Lista de líneas de log
        level: Nivel a filtrar (ERROR, WARN, INFO, DEBUG)
    
    Returns:
        List[str]: Logs filtrados
    """
    if not level or level == 'ALL':
        return logs
    
    level_lower = level.lower()
    return [line for line in logs if level_lower in line.lower()]


def invalidate_logs_cache(service: Service):
    """
    Invalidar caché de logs para un servicio.
    
    Args:
        service: Servicio cuyo caché invalidar
    """
    # Invalidar todas las variantes de caché para este servicio
    for tail in [100, 500, 1000, 'all']:
        for since in [None, 'all']:
            cache_key = f"logs_{service.id}_{tail}_{since or 'all'}"
            cache.delete(cache_key)
    
    logger.info(f"Caché de logs invalidado para servicio {service.id}")
