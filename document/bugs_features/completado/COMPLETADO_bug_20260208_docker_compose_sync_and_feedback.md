# Bug Fix & Feature: Docker Compose Sync & Transient States Feedback

## 1. Descripción del Problema

Se identificaron varios problemas relacionados con el ciclo de vida y la usabilidad de los servicios Docker (especialmente Docker Compose) en la plataforma:

1.  **Sincronización de Estado Deficiente (Docker Compose):**
    - Los servicios creados con `docker-compose.yml` (e.g., `build: .` o imágenes directas) a menudo se quedaban indefinidamente en estado `starting` en la UI, aunque los contenedores ya estuvieran `running` en Docker.
    - El usuario tenía que refrescar manualmente la página (F5) para ver el estado real `running`.
    - La función `sync_service_status` no se invocaba de manera proactiva tras el despliegue.

2.  **Falta de Feedback Visual en Operaciones Destructivas (Stop/Remove):**
    - Al detener (`stop`) o eliminar (`remove`) un servicio, la operación se realizaba de forma síncrona y muy rápida.
    - La UI no mostraba ningún estado intermedio (`stopping`, `deleting`), pasando directamente de `running` a `stopped` o desapareciendo.
    - Esto generaba confusión en el usuario sobre si la acción se estaba ejecutando.

3.  **Falso Positivo de "Running" Prematuro:**
    - En algunos casos, `docker compose up` retornaba éxito antes de que los contenedores estuvieran realmente listos/estables, provocando verificaciones de estado fallidas inmediatamente después.

## 2. Solución Implementada

Se realizó una refactorización completa del manejo de estados y operaciones de contenedores para garantizar la consistencia y mejorar la UX.

### 2.1. Sincronización Automática y Estabilización

- **Delay de Estabilización:** Se añadió una espera explícita de **3 segundos** después de ejecutar `docker compose up` y antes de guardar el estado inicial. Esto permite que el motor de Docker estabilice los contenedores antes de cualquier verificación.
  - _Archivo:_ `containers/services.py`
- **Auto-Sync en Vista:** Se aseguró que la vista `student_services_in_subject` llame a `sync_service_status` para cada servicio al cargar, garantizando que el estado mostrado sea el real de Docker.
- **Auto-Refresh en UI:** Se implementó un `hx-trigger="load, every 3s"` en la tabla de servicios del panel de estudiante para que la UI se actualice automáticamente sin intervención del usuario.

### 2.2. Operaciones Asíncronas y Estados Transitorios

Para resolver la falta de feedback visual, se convirtieron las operaciones síncronas en asíncronas (background tasks):

- **Async Stop & Remove:**
  - Se crearon las funciones `stop_container_async` y `remove_container_async` en `containers/services.py`.
  - Estas funciones establecen inmediatamente el estado del servicio a `stopping` o `deleting` en la base de datos y luego lanzan la operación real en un hilo de fondo (usando `EXECUTOR.submit`).
- **Feedback Visual Inmediato:**
  - Se actualizaron los controladores en `views.py` para usar las versiones asíncronas.
  - Se modificaron los templates de botones (`_simple.html`, `_compose.html`) para disparar un evento `service:table-refresh` inmediatamente después del click.
  - Se actualizó el badge de estado (`_status.html`) para incluir estilos visuales y animados (iconos `fa-spin`) para los estados `stopping` (amarillo) y `deleting` (rojo).

## 3. Archivos Modificados

- `containers/services.py`: Lógica principal de delays, workers asíncronos y sincronización.
- `containers/views.py`: Adaptación de endpoints `stop` y `remove` para usar lógica asíncrona.
- `templates/containers/student_panel.html`: Configuración de auto-refresh HTMX.
- `templates/containers/_partials/services/_status.html`: Nuevos estilos para estados `stopping` y `deleting`.
- `templates/containers/_partials/services/_simple.html` y `_compose.html`: Triggers HTMX para refresco inmediato.

## 4. Resultado Final

- **Ciclo de vida fluido:** `pending` -> `starting` (con delay de estabilización) -> `running` (automático).
- **Feedback claro:**
  - Botón "Stop" -> Estado cambia a `stopping` (amarillo, animado) -> `stopped` (gris).
  - Botón "Remove" -> Estado cambia a `deleting` (rojo, animado) -> Desaparece.
- **UX Mejorada:** El usuario siempre sabe qué está pasando con sus servicios sin necesidad de recargar la página manualmente.

## 5. Estado

**ESTADO:** ✅ COMPLETADO
**FECHA:** 08/02/2026
