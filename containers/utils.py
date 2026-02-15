"""
Utilidades para manejo de logs de contenedores Docker.

Incluye funciones para:
- Obtener logs de contenedores
- Colorización avanzada con Rich
- Filtrado por nivel y texto
- Caché de logs
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from django.core.cache import cache
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from io import StringIO
import dateutil.parser

from .docker_client import get_docker_client
from .models import Service, ServiceContainer

logger = logging.getLogger(__name__)


def fetch_container_logs(service: Service, tail: int = 1000, since: str = None, container_name: str = None, force_refresh: bool = False) -> Tuple[List[str], bool]:
    cache_key = f"logs_{service.id}_{tail}_{since or 'all'}_{container_name or 'all'}"
    if not force_refresh:
        cached_logs = cache.get(cache_key)
        if cached_logs: return cached_logs, True

    docker_client = get_docker_client()
    if not docker_client: return [" ERROR: Docker no disponible"], False
    
    # Calcular 'since' exacto si es relativo
    since_seconds = None
    if since:
        match = re.match(r'(\d+)([mhd])', since)
        if match:
            val, unit = int(match.group(1)), match.group(2)
            mult = {'m': 60, 'h': 3600, 'd': 86400}
            since_seconds = int(datetime.now(timezone.utc).timestamp()) - (val * mult[unit])

    temp_logs = []
    try:
        logs_kwargs = {'tail': tail, 'timestamps': True, 'stream': False}
        if since_seconds:
            logs_kwargs['since'] = since_seconds
        elif since:
            logs_kwargs['since'] = since

        containers = []
        if service.has_compose:
            c_query = ServiceContainer.objects.filter(service=service)
            if container_name and container_name != 'all':
                c_query = c_query.filter(name=container_name)
            containers = list(c_query.filter(container_id__isnull=False))
        elif service.container_id:
            containers = [service] 

        # Timezone de España (CET=UTC+1 en invierno)
        # Para ser precisos sin pytz, usamos un offset fijo
        spain_tz = timezone(timedelta(hours=1))

        for c_rec in containers:
            c_id = getattr(c_rec, 'container_id', None) or getattr(c_rec, 'container_id', None)
            if not c_id and not service.has_compose: c_id = service.container_id
            if not c_id: continue
            
            try:
                c = docker_client.containers.get(c_id)
                data = c.logs(**logs_kwargs).decode('utf-8', errors='replace')
                prefix = f"[{getattr(c_rec, 'name', 'serv')}] " if service.has_compose else ""
                
                for line in data.splitlines():
                    if not line.strip(): continue
                    
                    # El formato de Docker con timestamps=True es: "2026-02-15T12:11:00.246570572Z contenido..."
                    parts = line.split(' ', 1)
                    raw_ts = parts[0]
                    content = parts[1] if len(parts) > 1 else ""
                    
                    try:
                        # Parsing preciso con dateutil
                        dt_utc = dateutil.parser.parse(raw_ts)
                        
                        # Filtro manual de seguridad (por si Docker falla o el reloj deriva)
                        if since_seconds and dt_utc.timestamp() < since_seconds:
                            continue
                            
                        # Convertir a hora de España
                        dt_spain = dt_utc.astimezone(spain_tz)
                        # Formato completo sugerido: 15/02/2026 13:30:00
                        human_ts = dt_spain.strftime("%d/%m/%Y %H:%M:%S")
                        
                        # Formatear línea final: [DD/MM/YYYY HH:MM:SS] contenido
                        formatted_line = f"[{human_ts}] {prefix}{content}"
                        temp_logs.append((dt_utc.timestamp(), formatted_line))
                    except:
                        # Si falla el parseo, dejamos el log original
                        temp_logs.append((0, f"{prefix}{line}"))
            except Exception as e: 
                logger.error(f"Error recuperando logs de {c_id}: {e}")
                continue

        temp_logs.sort(key=lambda x: x[0])
        lines = [l[1] for l in temp_logs]
        
        # SI NO HAY LOGS DE CONTENEDOR Y EL SERVICIO TIENE ERROR, MOSTRAR LOGS DEL SISTEMA (EJ. FALLO BUILD/RAR)
        if not lines and service.status == 'error' and service.logs:
            lines = [f"[SISTEMA] {line}" for line in service.logs.splitlines()]
            return lines, False

        if tail != 'all':
            try: 
                t_count = int(tail)
                if len(lines) > t_count:
                    lines = lines[-t_count:]
            except: pass
            
        cache.set(cache_key, lines, 30 if not force_refresh else 5)
        return lines, False
    except Exception as e:
        logger.error(f"Error general en fetch_container_logs: {e}")
        return [f"[ERROR] {e}"], False


def group_logs_by_container(logs: List[str]) -> List[str]:
    """
    Agrupa logs que tienen el prefijo [nombre] por contenedor y añade cabeceras.
    """
    import re
    p_regex = re.compile(r'^\[([^\]]+)\]')
    
    grouped = {} # name -> list of lines
    order = []
    
    for line in logs:
        match = p_regex.match(line)
        if match:
            name = match.group(1)
            # Quitar el prefijo para la visualización final si se agrupa
            content = line[len(match.group(0))+1:]
        else:
            name = "default"
            content = line
            
        if name not in grouped:
            grouped[name] = []
            order.append(name)
        grouped[name].append(content)
    
    final = []
    for name in order:
        if name != "default":
            final.append(f"{'='*80}")
            final.append(f"CONTENEDOR: {name}")
            final.append(f"{'='*80}")
        
        final.extend(grouped[name])
        final.append("") # Espacio entre contenedores
        
    return final


def colorize_logs_rich(logs: List[str]) -> str:
    from rich.console import Console
    from rich.text import Text
    import io
    string_io = io.StringIO()
    # Forzamos fondo negro y letras blancas puro
    console = Console(width=2000, record=True, force_terminal=False, file=string_io)
    
    for line in logs:
        if not line or not line.strip():
            console.print("")
            continue
        
        line_lower = line.lower()
        # TEXTO BLANCO PURO Y NEGRITA (MÁXIMO CONTRASTE)
        text = Text(line, style="bold #ffffff")
        
        if any(lvl in line_lower for lvl in ['error', 'fatal', 'critical', '[err]']):
            text.stylize("bold red")
            console.print(Text("🔴 ") + text)
        elif any(lvl in line_lower for lvl in ['warn', 'warning', '[wrn]']):
            text.stylize("bold yellow")
            console.print(Text("🟡 ") + text)
        elif 'info' in line_lower:
            text.stylize("bold green")
            console.print(Text("🟢 ") + text)
        elif 'debug' in line_lower:
            text.stylize("bold blue")
            console.print(Text("🔵 ") + text)
        elif line.startswith('==='):
            text.stylize("bold cyan")
            console.print(text)
        elif line.startswith('CONTENEDOR:'):
            text.stylize("bold magenta")
            console.print(text)
        else:
            console.print(text)
    
    return console.export_html(
        inline_styles=True, 
        code_format="<pre style='white-space: pre !important; font-family: inherit; margin: 0; color: #ffffff;'>{code}</pre>"
    )


def colorize_logs_simple(logs: List[str]) -> str:
    """Fallback simple de colorización."""
    from django.utils.html import escape
    html_lines = []
    for line in logs:
        if not line:
            html_lines.append('<div style="height: 1em;"></div>')
            continue
        line_escaped = escape(line)
        line_lower = line_escaped.lower()
        
        cls, icon = "log-default", ""
        if any(lvl in line_lower for lvl in ['error', 'fatal', 'critical']):
            cls, icon = "log-error", "🔴"
        elif any(lvl in line_lower for lvl in ['warn', 'warning']):
            cls, icon = "log-warn", "🟡"
        elif 'info' in line_lower:
            cls, icon = "log-info", "🟢"
        elif 'debug' in line_lower:
            cls, icon = "log-debug", "🔵"
            
        html_lines.append(f'<div class="log-line {cls}">{icon} {line_escaped}</div>')
    return "\n".join(html_lines)


def filter_logs(logs: List[str], search_text: str) -> List[str]:
    if not search_text: return logs
    text = search_text.lower()
    return [l for l in logs if text in l.lower()]


def filter_by_level(logs: List[str], level: str) -> List[str]:
    if not level or level == 'ALL': return logs
    lvl = level.upper()
    
    patterns = {
        'ERROR': ['error', 'fatal', 'critical', 'fail', '[err]', '(err)'],
        'WARN': ['warn', 'warning', '[wrn]', '(wrn)'],
        'INFO': ['info'],
        'DEBUG': ['debug']
    }
    keywords = patterns.get(lvl, [lvl.lower()])
    return [l for l in logs if any(k in l.lower() for k in keywords)]


def invalidate_logs_cache(service: Service):
    """
    Invalidar todas las variantes de caché de logs para un servicio.
    """
    # Intentamos borrar el patrón general
    # Como no podemos hacer cache.delete_pattern fácilmente en todos los backends,
    # borramos las combinaciones más comunes
    tails = [100, 500, 1000, 10000, 'all']
    sinces = [None, 'all', '5m', '15m', '1h', '4h', '24h', '7d']
    
    # Obtener nombres de contenedores si los hay
    container_names = ['all']
    if service.has_compose:
        container_names.extend([c.name for c in service.containers.all()])

    count = 0
    for tail in tails:
        for since in sinces:
            for c_name in container_names:
                cache_key = f"logs_{service.id}_{tail}_{since or 'all'}_{c_name}"
                if cache.delete(cache_key):
                    count += 1
    
    logger.info(f"Caché de logs invalidado para servicio {service.id} ({count} llaves eliminadas)")
