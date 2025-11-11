# Implementación — Plan de Testing Posterior al Refactor (2025-11-06 00:38)

## 1. Objetivo
Resolver incidencias detectadas durante el testing funcional (refresco HTMX, error en terminal, duplicidad `user_code`) y dejar trazabilidad para los próximos commits.

## 2. Incidencia A — Refresco dinámico tras gestionar servicios
1. **Áreas a revisar**
   - `containers/views.py` (`ServiceViewSet.create/start/stop/remove`, helper `_htmx_response`).
   - `templates/containers/_service_rows.html` y `student_panel.html` (targets HTMX).
2. **Dependencias**
   - HTMX (`HX-Request`, `HX-Trigger`, `HX-Target`).
   - DRF Responses y serializadores.
3. **Acciones**
   - Asegurar que cada acción devuelve fragmento HTML listo para insertar.
   - Emitir triggers globales para refrescar `#service-table` o la fila concreta.
   - Ajustar `hx-target` en botones para evitar vacíos temporales.
4. **Testing**
   - Crear/Iniciar/Detener/Eliminar desde “Mis servicios” y desde “Asignatura”.
   - Revisar consola HTMX (sin 500/403). Añadir caso de prueba en `containers/tests.py` si procede.

## 3. Incidencia B — Error 500 en terminal
1. **Áreas a revisar**
   - `containers/views.py::terminal_view`.
   - `templates/terminal.html`.
   - `containers/urls.py` y `paasify/urls.py` (namespaces).
2. **Dependencias**
   - Django `reverse/redirect`.
   - Channels / TerminalConsumer (para validar end-to-end).
3. **Acciones**
   - Localizar `reverse('student_panel')` y actualizar a `reverse('containers:student_panel')` (o ruta correcta).
   - Verificar enlaces “Volver” en las plantillas.
4. **Testing**
   - Abrir terminal desde un servicio `running`.
   - Ejecutar `pytest containers/tests.py -k terminal_websocket` en entorno con Docker.

## 4. Incidencia C — Duplicidad directorio `user_code`
1. **Áreas a revisar**
   - `app_passify/settings.py` (MEDIA_ROOT, rutas de subida).
   - `containers/services.py` (`_save_filefield_to`, `_unpack_code_zip_to`, rutas temporales).
   - `.gitignore` y cualquier script que cree `user_code/`.
2. **Dependencias**
   - Django FileField y almacenamiento local.
   - Python `tempfile`, rutas absolutas vs relativas.
3. **Acciones**
   - Definir ruta única (`MEDIA_ROOT/user_code`).
   - Eliminar referencias al directorio raíz `/user_code`.
   - Limpiar carpeta antigua y asegurarse de que los ZIP se guardan en `media/user_code`.
4. **Testing**
   - Subir ZIP/Dockerfile y comprobar ubicaciones.
   - Revisar que `Service.code.path` apunta a `media/user_code/...`.

## 5. Roadmap de ejecución
1. **Fase A:** correcciones HTMX + pruebas manuales → commit `fix(htmx): refresco inmediato`.
2. **Fase B:** corrección terminal → prueba manual + `pytest` → commit `fix(terminal): ruta student_panel`.
3. **Fase C:** unificación `user_code` → creación servicio con ZIP → commit `refactor(storage): user_code en MEDIA`.
4. **Documentación:** actualizar `document/testing_servicios_ssh_volumenes_*` con nuevos pasos y registrar fase en `document/implementacion_servicios_ssh_fase5_*.md`.
