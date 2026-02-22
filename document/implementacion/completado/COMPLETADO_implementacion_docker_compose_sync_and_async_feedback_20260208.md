# Implementación: Sincronización Docker Compose y Operaciones Asíncronas

**Fecha:** 08/02/2026
**Autor:** David RG
**Estado:** ✅ Completado

## 1. Contexto

La gestión de servicios Docker Compose en la plataforma presentaba dos problemas principales de usabilidad y consistencia:

1.  **Desincronización de Estado:** Los servicios a menudo quedaban "atascados" visualmente en estado `starting` a pesar de estar funcionando correctamente en el backend.
2.  **Falta de Feedback Visual:** Las operaciones destructivas (`stop`, `remove`) eran síncronas y tan rápidas que la UI no ofrecía ningún feedback visual de que la acción se estaba procesando, causando confusión.

Esta implementación aborda ambos problemas mediante la introducción de mecanismos de sincronización automática y la conversión de operaciones clave a un modelo asíncrono con feedback visual explícito.

## 2. Cambios Arquitectónicos

### 2.1. Gestión Asíncrona de Estados Transitorios

Se ha modificado el flujo de las operaciones `stop` y `remove` para que no bloqueen el hilo de petición HTTP principal.

- **Antes:** El usuario pulsaba "Detener" -> El servidor ejecutaba `docker stop` (síncrono) -> La UI se actualizaba directamente a `stopped`.
- **Ahora:** El usuario pulsa "Detener" -> El servidor marca el estado como `stopping` en DB y lanza un hilo de fondo (worker) -> La petición HTTP retorna inmediatamente -> La UI muestra "Deteniendo..." -> El worker ejecuta `docker stop` -> El estado final cambia a `stopped`.

### 2.2. Estabilización de Docker Compose

Se ha introducido un periodo de estabilización post-despliegue para evitar condiciones de carrera donde la aplicación consultaba el estado de los contenedores antes de que Docker terminará de registrarlos completamente.

## 3. Detalles de Implementación

### 3.1. Backend (`containers/services.py`)

- **Nuevas Funciones Asíncronas:**
  - `stop_container_async(service)`: Establece estado `stopping` y delega a `_stop_container_worker`.
  - `remove_container_async(service)`: Establece estado `deleting` y delega a `_remove_container_worker`.
- **Workers:**
  - `_stop_container_worker`: Ejecuta la lógica de parada real.
  - `_remove_container_worker`: Ejecuta la eliminación de recursos.
- **Delays de UX:**
  - Se añadió `time.sleep(3)` tras `docker compose up` para estabilización.
  - Se añadió `time.sleep(1.5)` al inicio de las operaciones de parada/eliminación para garantizar que el usuario perciba el cambio de estado en la UI (feedback visual).
- **Sincronización:**
  - Mejora en `sync_service_status` para detectar correctamente contenedores Compose y transicionar de `starting` a `running`.

### 3.2. Vistas (`containers/views.py`)

- Los endpoints `stop` y `remove` del `ServiceViewSet` han sido actualizados para invocar las nuevas funciones `*_async`.
- Se mantiene la compatibilidad con respuestas HTMX y JSON estándar.

### 3.3. Frontend y Plantillas

- **Auto-refresco:** `templates/containers/student_panel.html` ahora incluye `hx-trigger="load, every 3s"` en la tabla de servicios para mantener el estado actualizado sin intervención del usuario.
- **Triggers Inmediatos:** Los botones de acción en `_simple.html` y `_compose.html` ahora disparan un evento `service:table-refresh` mediante `hx-on::after-request` para actualización instantánea tras el clic.
- **Badges de Estado:** `_status.html` actualizado para incluir estilos visuales para los estados `stopping` (amarillo) y `deleting` (rojo) con iconos animados (`fa-spin`).

## 4. Pruebas y Validación

- **Creación de Servicio Compose:** Validado que el servicio transiciona de `starting` a `running` automáticamente tras el periodo de estabilización.
- **Detención de Servicio:** Validado que al pulsar "Stop", el badge cambia inmediatamente a "Deteniendo..." (amarillo) y posteriormente a "Stopped" (gris).
- **Eliminación de Servicio:** Validado que al pulsar "Remove", el badge cambia inmediatamente a "Eliminando..." (rojo) y luego el servicio desaparece de la lista.
- **Persistencia:** Confirmado que los estados intermedios se reflejan en base de datos.

## 5. Archivos Afectados

1.  `containers/services.py`
2.  `containers/views.py`
3.  `templates/containers/student_panel.html`
4.  `templates/containers/_partials/services/_status.html`
5.  `templates/containers/_partials/services/_simple.html`
6.  `templates/containers/_partials/services/_compose.html`
