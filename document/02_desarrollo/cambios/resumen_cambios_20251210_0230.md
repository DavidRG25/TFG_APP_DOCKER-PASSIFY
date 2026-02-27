# Resumen de Cambios y Correcciones - 10/12/2025

Este documento resume las modificaciones, correcciones de errores y nuevas funcionalidades implementadas en la sesión del 10 de diciembre de 2025.

## 1. Integración de Proyectos y Servicios

Se ha completado la integración funcional y visual entre Servicios y Proyectos de Usuario (`UserProject`).

### Backend (Django)

- **Modelo `Service`**: Añadido campo `project` (`ForeignKey` a `UserProject`) y hecho el campo `image` opcional (`blank=True`) para soportar servicios personalizados sin imagen base explícita.
- **Vistas (`views.py`)**:
  - Actualizadas las vistas `student_panel` y `student_services_in_subject` para pasar el contexto de proyectos del usuario y estadísticas de proyectos.
  - Implementado filtrado de servicios por asignatura en la vista `service_table`.
- **Corrección de Migración**: Solucionado un error bloqueante en la migración `0005` que referenciaba un modelo inexistente (`paasify.sport`), corrigiéndolo a `paasify.Subject`.

### Frontend (Templates)

- **Modal Nuevo Servicio**: Añadido selector de proyectos obligatorio. Elimina la opción vacía y avisa si el usuario no tiene proyectos.
- **Tabla de Servicios**: Añadida columna "Proyecto" que muestra el nombre del proyecto (`place`).
- **Panel de Estadísticas**: Añadida nueva tarjeta "Proyectos" a la izquierda de totales. Se muestra solo en el Dashboard general y se oculta dentro de una asignatura específica.
- **Auto-refresco (Bug Fix)**: Corregido el bug donde el refresco automático de la tabla mostraba servicios de otros proyectos al estar dentro de una asignatura. Se añadió el parámetro `?subject=ID` dinámicamente al `hx-get` de la tabla.

## 2. Mejoras en Panel de Administración (Django Admin)

Se han mejorado las interfaces de administración para facilitar la gestión por parte del administrador/profesor.

- **Lista de Servicios**:
  - Nueva columna "Proyecto" en la tabla de listado.
  - Filtro de búsqueda por nombre de proyecto.
- **Edición de Servicio**:
  - Añadido campo editable "Proyecto".
  - El selector de proyectos filtra automáticamente para mostrar SOLO los proyectos asignados al propietario del servicio (`owner`), evitando asignaciones erróneas.
  - Campo "Imagen" ahora permite estar vacío (necesario para servicios Compose/Dockerfile puros).

## 3. Lista de Archivos Modificados Clave

- `containers/models.py`
- `containers/views.py`
- `containers/admin.py`
- `containers/migrations/0005_...py` (Fix)
- `containers/migrations/0015_...py` (Nuevo campo project)
- `containers/migrations/0016_...py` (Image blank=True)
- `templates/containers/student_panel.html`
- `templates/containers/_partials/panels/_modals.html`
- `templates/containers/_partials/panels/_stats.html`
- `templates/containers/_service_rows.html`

---
