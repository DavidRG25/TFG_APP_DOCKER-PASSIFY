# Bug: Terminal WebSocket 404
**Fecha**: 2025-12-07 22:43  
**Prioridad**: MEDIA  
**Estado**: ⏳ PENDIENTE

---

## 🐛 DESCRIPCIÓN DEL BUG

**Problema**: Al intentar acceder a la terminal web, se produce un error 404 en la ruta WebSocket

**Logs**:
```
Not Found: /ws/terminal/94/
[07/Dec/2025 22:26:14] "GET /ws/terminal/94/ HTTP/1.1" 404 5547
Not Found: /ws/terminal/94/
[07/Dec/2025 22:26:17] "GET /ws/terminal/94/ HTTP/1.1" 404 5547
```

**Comportamiento observado**:
- El botón "Terminal" es clickeable cuando el contenedor está running
- Se abre la página de terminal (`/paasify/containers/terminal/94/`)
- La página muestra "Reconectando..." o error de conexión WebSocket
- La consola del navegador muestra error 404 en `/ws/terminal/94/`

---

## 🔍 ANÁLISIS

### **Causa probable**:
1. Ruta WebSocket no configurada en `routing.py` o `urls.py`
2. Consumer de WebSocket no registrado
3. ASGI no configurado correctamente para WebSockets

### **Archivos relevantes**:
- `routing.py` - Configuración de rutas WebSocket
- `containers/consumers.py` - Consumer de terminal (si existe)
- `asgi.py` - Configuración ASGI
- `templates/containers/terminal.html` - Template de terminal

---

## 🔧 INVESTIGACIÓN REQUERIDA

### **Paso 1: Verificar routing.py**
Buscar si existe configuración de WebSocket:
```python
# routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from containers.consumers import TerminalConsumer

websocket_urlpatterns = [
    path('ws/terminal/<int:service_id>/', TerminalConsumer.as_asgi()),
]
```

### **Paso 2: Verificar consumer**
Verificar si existe `containers/consumers.py` con `TerminalConsumer`

### **Paso 3: Verificar ASGI**
Verificar que `asgi.py` esté configurado para WebSockets:
```python
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

### **Paso 4: Verificar dependencias**
Verificar que `channels` esté instalado:
```
pip list | grep channels
```

---

## 💡 SOLUCIÓN PROPUESTA

### **Opción 1: Implementar WebSocket con Channels**
1. Instalar `channels` y `channels-redis`
2. Crear `containers/consumers.py` con `TerminalConsumer`
3. Configurar `routing.py` con rutas WebSocket
4. Actualizar `asgi.py` para soportar WebSockets
5. Configurar Redis como backend (opcional)

### **Opción 2: Alternativa sin WebSocket**
1. Usar polling con HTMX cada X segundos
2. Endpoint REST que devuelva logs del contenedor
3. Menos eficiente pero más simple

---

## 📋 TAREAS PENDIENTES

- [ ] Verificar si `channels` está instalado
- [ ] Revisar `routing.py` y `asgi.py`
- [ ] Verificar si existe `containers/consumers.py`
- [ ] Decidir entre Opción 1 (WebSocket) u Opción 2 (Polling)
- [ ] Implementar solución elegida
- [ ] Testing de terminal web

---

## 🎯 IMPACTO

**Severidad**: MEDIA  
**Funcionalidad afectada**: Terminal web interactiva  
**Workaround**: Usar Docker Desktop o terminal externa para acceder al contenedor

**Nota**: Esta funcionalidad no es crítica para el funcionamiento básico de la aplicación. Los usuarios pueden gestionar contenedores sin necesidad de terminal web.

---

**Última actualización**: 2025-12-07 22:43  
**Estado**: Documentado, pendiente de implementación
