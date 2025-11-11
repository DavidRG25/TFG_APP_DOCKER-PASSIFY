# Implementación — Testing Post Refactor (Fase 5, 2025-11-06 01:15)

## 1. Alcance
1. Refrescar automáticamente la tabla de servicios tras acciones HTMX (crear, iniciar, detener, eliminar) sin recargar la página.
2. Corregir el error 500 al abrir la terminal (referencia incorrecta al panel de servicios).
3. Unificar el almacenamiento de archivos `user_code` bajo `MEDIA_ROOT` para evitar directorios duplicados.

## 2. Cambios clave
1. **HTMX / UI**
   - `containers/views.py`: `_htmx_response` ahora emite `service:table-refresh` y delega el render al `tbody`.
   - `templates/containers/student_panel.html`: el `<tbody>` escucha `load`, `service:table-refresh` y `every 5s`, y el formulario usa `hx-swap="none"`.
   - `templates/containers/_service_rows.html`: los botones principales usan `hx-swap="none"` y el texto de confirmación se normalizó.
2. **Terminal**
   - Actualizados los enlaces en `templates/base.html`, `templates/containers/terminal.html` y `containers/edit_service.html` para usar `containers:student_panel`, evitando el `NoReverseMatch`.
3. **Media / user_code**
   - `app_passify/settings.py`: añadidos `MEDIA_URL`, `MEDIA_ROOT` y creación automática de `MEDIA_ROOT/user_code`.
   - `.gitignore` ya contemplaba `media/`, se mantiene sin cambios.

## 3. Verificación
1. HTMX: Crear/iniciar/detener/eliminar servicios desde “Mis servicios” y “Asignatura 1”; observar que la tabla cambia de `PENDING` a `RUNNING/STOPPED` sin recargar.
2. Terminal: Abrir `/paasify/containers/terminal/<id>/` para un servicio `running`; el enlace “Volver” funciona.
3. Al subir ZIP/Dockerfile, los archivos aparecen únicamente en `media/user_code/…` y no se recrea un directorio `user_code` en la raíz del repo.

## 4. Pendientes / notas
1. Documentar en el checklist de despliegue que `media/` debe persistirse (volumen) para conservar los ZIP.
2. Considerar limpieza automática de archivos antiguos en `media/user_code` como tarea futura.
