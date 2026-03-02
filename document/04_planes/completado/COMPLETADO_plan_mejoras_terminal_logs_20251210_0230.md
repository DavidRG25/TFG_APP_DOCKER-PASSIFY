# Plan de Mejoras - Terminal y Logs
**Fecha creación**: 2025-12-09  
**Prioridad**: ALTA  
**Estado**: PENDIENTE

---

## 🎯 OBJETIVO

Mejorar significativamente la experiencia de terminal web y visualización de logs, implementando PyXtermJS para terminal y mejoras visuales/funcionales para logs.

---

## 📋 FASE 1: Implementación de PyXtermJS Terminal

### **Objetivo:**
Sustituir el consumer de terminal actual por PyXtermJS con integración Docker.

### **Tareas:**

#### **1.1 Instalación y configuración**
- [ ] Instalar `pyxtermjs`
```bash
pip install pyxtermjs
```

- [ ] Añadir a `requirements.txt`
- [ ] Configurar en `settings.py`

**Archivo**: `settings.py`
```python
INSTALLED_APPS += [
    'pyxtermjs',
]
```

#### **1.2 Modificar routing ASGI**
- [ ] Reemplazar `TerminalConsumer` por `PyXtermApp`
- [ ] Configurar ruta `/xterm/`

**Archivo**: `routing.py`
```python
from pyxtermjs.app import PyXtermApp
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Crear app personalizada que use docker exec
class DockerPyXtermApp(PyXtermApp):
    def get_command(self, request):
        """Override para usar docker exec en lugar de shell local"""
        service_id = request.GET.get('service_id')
        if not service_id:
            raise ValueError("service_id requerido")
        
        # Obtener servicio y verificar permisos
        from containers.models import Service
        service = Service.objects.get(id=service_id, owner=request.user)
        
        if not service.container_id:
            raise ValueError("Contenedor no disponible")
        
        # Comando docker exec
        return [
            'docker', 'exec', '-it',
            service.container_id,
            '/bin/bash'
        ]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('xterm/', DockerPyXtermApp.as_asgi()),
        ])
    ),
})
```

#### **1.3 Crear vista de terminal**
- [ ] Vista Django para renderizar página de terminal
- [ ] Template con PyXtermJS

**Archivo**: `containers/views.py`
```python
@login_required
def terminal_pyxterm(request, pk):
    """Terminal web usando PyXtermJS"""
    service = get_object_or_404(Service, pk=pk, owner=request.user)
    
    # Verificar que el contenedor está running
    if service.status != "running" or not service.container_id:
        return HttpResponse("El servicio no está en ejecución.", status=400)
    
    # Verificar que el contenedor existe en Docker
    docker_client = get_docker_client()
    try:
        container = docker_client.containers.get(service.container_id)
        container.reload()
        if container.status.lower() != "running":
            return HttpResponse("El contenedor no está en ejecución.", status=400)
    except NotFound:
        return HttpResponse("El contenedor no existe.", status=404)
    
    return render(request, "containers/terminal_pyxterm.html", {
        "service": service,
    })
```

**Archivo**: `templates/containers/terminal_pyxterm.html`
```html
{% extends "base.html" %}
{% load static %}

{% block extrahead %}
<link rel="stylesheet" href="{% static 'pyxtermjs/xterm.css' %}">
<style>
    .terminal-container {
        height: calc(100vh - 200px);
        background-color: #000;
        padding: 20px;
    }
    #terminal {
        height: 100%;
    }
</style>
{% endblock %}

{% block body %}
<div class="container-fluid">
    <div class="row mb-3">
        <div class="col">
            <h3>Terminal - {{ service.name }}</h3>
            <p class="text-muted">Contenedor: {{ service.container_id|slice:":12" }}</p>
        </div>
        <div class="col-auto">
            <a href="{% url 'containers:student_panel' %}" class="btn btn-secondary">
                Volver
            </a>
        </div>
    </div>
    
    <div class="terminal-container">
        <div id="terminal"></div>
    </div>
</div>
{% endblock %}

{% block extrascripts %}
<script src="{% static 'pyxtermjs/xterm.js' %}"></script>
<script src="{% static 'pyxtermjs/xterm-addon-fit.js' %}"></script>
<script>
    const term = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        theme: {
            background: '#000000',
            foreground: '#ffffff'
        }
    });
    
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();
    
    // Conectar a WebSocket
    const ws = new WebSocket(
        `ws://${window.location.host}/xterm/?service_id={{ service.id }}`
    );
    
    ws.onopen = () => {
        term.write('Conectado al contenedor...\r\n');
    };
    
    ws.onmessage = (event) => {
        term.write(event.data);
    };
    
    term.onData((data) => {
        ws.send(data);
    });
    
    ws.onerror = (error) => {
        term.write('\r\n\x1b[31mError de conexión\x1b[0m\r\n');
    };
    
    ws.onclose = () => {
        term.write('\r\n\x1b[33mConexión cerrada\x1b[0m\r\n');
    };
    
    // Ajustar tamaño al redimensionar ventana
    window.addEventListener('resize', () => {
        fitAddon.fit();
    });
</script>
{% endblock %}
```

#### **1.4 Seguridad y autenticación**
- [ ] Middleware de autenticación para WebSocket
- [ ] Verificar permisos (solo propietario del servicio)
- [ ] Timeout de sesión

**Archivo**: `containers/middleware.py`
```python
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Obtener usuario de la sesión
        scope['user'] = await self.get_user(scope)
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, scope):
        from django.contrib.auth import get_user
        # Lógica de autenticación
        return get_user(scope.get('session', {}))
```

#### **1.5 Actualizar botón Terminal en UI**
- [ ] Cambiar URL del botón Terminal
- [ ] Actualizar tooltip

**Archivo**: `templates/containers/_service_rows.html`
```html
<a href="{% url 'containers:terminal_pyxterm' service.id %}"
   class="btn btn-sm btn-secondary"
   {% if service.status != 'running' %}disabled{% endif %}>
   <i class="fas fa-terminal"></i> Terminal
</a>
```

**Estimación**: 8-10 horas

---

## 📋 FASE 2: Página Dedicada para Logs

### **Objetivo:**
Crear una página dedicada con visualización mejorada de logs, filtros y funcionalidades avanzadas.

### **Tareas:**

#### **2.1 Crear página dedicada de logs**
- [ ] Vista `logs_page`
- [ ] Template `containers/logs_page.html`
- [ ] Ruta en `urls.py`

**Estructura propuesta**:
```
┌─────────────────────────────────────────────────┐
│ 📋 Logs - mi-servicio                           │
│ Contenedor: abc123def456                        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 🔍 [Buscar texto...]  [ERROR▼] [INFO▼] [WARN▼] │
│ [📋 Copiar] [💾 Descargar] [🔄 Seguir] [🗑️ Limpiar]│
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ [2025-12-09 22:00:01] INFO  Starting server...  │
│ [2025-12-09 22:00:02] INFO  Listening on :5000  │
│ [2025-12-09 22:00:05] WARN  Deprecated API used │
│ [2025-12-09 22:00:10] ERROR Connection failed   │
│ [2025-12-09 22:00:11] INFO  Retrying...         │
│                                                 │
│ ▼ Mostrando 1000 líneas (últimas 24h)          │
└─────────────────────────────────────────────────┘
```

**Archivo**: `containers/views.py`
```python
@login_required
def logs_page(request, pk):
    """Página dedicada para visualizar logs"""
    service = get_object_or_404(Service, pk=pk, owner=request.user)
    
    # Obtener parámetros de filtro
    search_text = request.GET.get('search', '')
    log_level = request.GET.get('level', 'ALL')
    tail = request.GET.get('tail', '1000')
    
    # Obtener logs del contenedor
    logs = fetch_container_logs(service, tail=int(tail))
    
    # Aplicar filtros
    if search_text:
        logs = [line for line in logs if search_text in line]
    
    if log_level != 'ALL':
        logs = [line for line in logs if log_level in line]
    
    # Colorear logs
    from .utils import colorize_logs
    logs_html = colorize_logs(logs)
    
    return render(request, "containers/logs_page.html", {
        "service": service,
        "logs_html": logs_html,
        "search_text": search_text,
        "log_level": log_level,
        "total_lines": len(logs),
    })
```

#### **2.2 Implementar filtros dinámicos con HTMX**
- [ ] Campo de búsqueda con actualización en tiempo real
- [ ] Filtros por nivel de log (ERROR, WARN, INFO)
- [ ] Selector de cantidad de líneas (100, 500, 1000, ALL)

**Archivo**: `templates/containers/logs_page.html`
```html
<div class="filters-toolbar">
    <input type="text" 
           name="search" 
           placeholder="🔍 Buscar en logs..."
           hx-get="{% url 'containers:logs_page' service.id %}"
           hx-trigger="keyup changed delay:500ms"
           hx-target="#logs-content"
           hx-include="[name='level'], [name='tail']"
           value="{{ search_text }}">
    
    <select name="level"
            hx-get="{% url 'containers:logs_page' service.id %}"
            hx-trigger="change"
            hx-target="#logs-content"
            hx-include="[name='search'], [name='tail']">
        <option value="ALL">Todos</option>
        <option value="ERROR" {% if log_level == 'ERROR' %}selected{% endif %}>ERROR</option>
        <option value="WARN" {% if log_level == 'WARN' %}selected{% endif %}>WARN</option>
        <option value="INFO" {% if log_level == 'INFO' %}selected{% endif %}>INFO</option>
    </select>
    
    <select name="tail"
            hx-get="{% url 'containers:logs_page' service.id %}"
            hx-trigger="change"
            hx-target="#logs-content"
            hx-include="[name='search'], [name='level']">
        <option value="100">100 líneas</option>
        <option value="500">500 líneas</option>
        <option value="1000" selected>1000 líneas</option>
        <option value="all">Todas</option>
    </select>
</div>
```

#### **2.3 Resaltado de color con Rich**
- [ ] Instalar librería `rich`
- [ ] Crear función `colorize_logs`
- [ ] Aplicar colores según severidad

**Archivo**: `containers/utils.py`
```python
from rich.console import Console
from rich.syntax import Syntax
from io import StringIO

def colorize_logs(logs):
    """Colorea logs según nivel de severidad"""
    html_lines = []
    
    for line in logs:
        # Detectar nivel de log
        if 'ERROR' in line or 'FATAL' in line:
            color = 'red'
            icon = '🔴'
        elif 'WARN' in line or 'WARNING' in line:
            color = 'yellow'
            icon = '🟡'
        elif 'INFO' in line:
            color = 'green'
            icon = '🟢'
        elif 'DEBUG' in line:
            color = 'blue'
            icon = '🔵'
        else:
            color = 'white'
            icon = '⚪'
        
        # Escapar HTML
        from django.utils.html import escape
        line_escaped = escape(line)
        
        # Añadir color
        html_line = f'<span class="log-{color}">{icon} {line_escaped}</span>'
        html_lines.append(html_line)
    
    return '\n'.join(html_lines)
```

**Archivo**: `static/css/logs.css`
```css
.logs-container {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    padding: 20px;
    border-radius: 8px;
    max-height: 70vh;
    overflow-y: auto;
}

.log-red {
    color: #f44336;
}

.log-yellow {
    color: #ffc107;
}

.log-green {
    color: #4caf50;
}

.log-blue {
    color: #2196f3;
}

.log-white {
    color: #d4d4d4;
}

.logs-container pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}
```

#### **2.4 Funciones utilitarias**
- [ ] Botón "Copiar todo"
- [ ] Botón "Descargar .log"
- [ ] Toggle "Seguir en Vivo" (auto-refresh)
- [ ] Botón "Limpiar pantalla"

**JavaScript para funcionalidades**:
```javascript
// Copiar logs
function copyLogs() {
    const logsText = document.getElementById('logs-content').innerText;
    navigator.clipboard.writeText(logsText);
    showToast('Logs copiados al portapapeles');
}

// Descargar logs
function downloadLogs() {
    const logsText = document.getElementById('logs-content').innerText;
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs-{{ service.name }}-${new Date().toISOString()}.log`;
    a.click();
}

// Seguir en vivo
let followInterval = null;
function toggleFollow() {
    const btn = document.getElementById('follow-btn');
    if (followInterval) {
        clearInterval(followInterval);
        followInterval = null;
        btn.textContent = '▶️ Seguir';
        btn.classList.remove('active');
    } else {
        followInterval = setInterval(() => {
            htmx.trigger('#logs-content', 'refresh');
        }, 2000);
        btn.textContent = '⏸️ Pausar';
        btn.classList.add('active');
    }
}

// Auto-scroll al final
function scrollToBottom() {
    const container = document.querySelector('.logs-container');
    container.scrollTop = container.scrollHeight;
}
```

**Estimación**: 6-8 horas

---

## 📋 FASE 3: Mejoras UX y Diseño

### **Tareas:**

#### **3.1 Diseño oscuro para logs**
- [ ] Fondo oscuro (#1e1e1e)
- [ ] Fuente monoespaciada
- [ ] Scroll suave
- [ ] Números de línea (opcional)

#### **3.2 Toolbar de acciones**
- [ ] Iconos claros para cada acción
- [ ] Tooltips explicativos
- [ ] Feedback visual al copiar/descargar

#### **3.3 Responsive design**
- [ ] Adaptar a móvil
- [ ] Toolbar colapsable en pantallas pequeñas

#### **3.4 Indicadores de estado**
- [ ] Mostrar cantidad de líneas filtradas
- [ ] Indicador de "Siguiendo en vivo"
- [ ] Timestamp de última actualización

**Estimación**: 3-4 horas

---

## 📋 FASE 4: Testing y Optimización

### **Tareas:**

#### **4.1 Testing de Terminal**
- [ ] Probar conexión WebSocket
- [ ] Probar docker exec
- [ ] Probar con diferentes shells (/bin/bash, /bin/sh)
- [ ] Probar timeout y reconexión

#### **4.2 Testing de Logs**
- [ ] Probar filtros
- [ ] Probar con logs grandes (>10000 líneas)
- [ ] Probar descarga
- [ ] Probar seguimiento en vivo

#### **4.3 Optimización**
- [ ] Paginación de logs si son muy grandes
- [ ] Lazy loading
- [ ] Caché de logs recientes

#### **4.4 Documentación**
- [ ] Documentar uso de terminal
- [ ] Documentar filtros de logs
- [ ] Guía de troubleshooting

**Estimación**: 4-5 horas

---

## 📊 RESUMEN

### **Tiempo total estimado**: 21-27 horas

### **Fases**:
1. ✅ PyXtermJS Terminal (8-10h)
2. ✅ Página dedicada Logs (6-8h)
3. ✅ Mejoras UX y Diseño (3-4h)
4. ✅ Testing y Optimización (4-5h)

### **Beneficios**:
- ✅ Terminal web nativa y funcional
- ✅ Mejor visualización de logs
- ✅ Filtros y búsqueda avanzada
- ✅ Descarga y copia de logs
- ✅ Seguimiento en tiempo real
- ✅ UX profesional

### **Dependencias**:
- pyxtermjs
- rich (para colorear logs)
- channels (ya instalado)
- daphne (ya instalado)

---

## 🔄 PRÓXIMOS PASOS

1. Revisar y aprobar plan
2. Implementar Fase 1 (PyXtermJS)
3. Implementar Fase 2 (Logs mejorados)
4. Implementar Fase 3 (UX)
5. Testing completo
6. Documentación

---

**Estado**: PENDIENTE DE APROBACIÓN  
**Prioridad**: ALTA (funcionalidad core)
