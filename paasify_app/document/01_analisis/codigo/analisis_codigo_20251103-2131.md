---
# Análisis de Código — Rama: feature/analisis-codigo
> Resumen: Diagnóstico integral tras los tres checks funcionales reportados y la ejecución ASGI con Daphne.

## 🧩 Objetivo
Revisar la rama `feature/analisis-codigo` para contrastar los fallos documentados en los tres checks funcionales y en la ejecución con Daphne, validando plantillas, vistas, permisos y el flujo de creación de contenedores.

## 📂 Archivos revisados
- `templates/base.html`
- `templates/registration/login.html`
- `containers/views.py`
- `containers/services.py`
- `templates/containers/student_panel.html`
- `paasify/admin.py`
- `security/views/SecurityViews.py`
- `tests/test_containers.py`

## ⚠️ Problemas detectados
1. **Fallo crítico en login bajo ASGI**: `templates/base.html` evalúa directamente `user.groups.filter(name__iexact='student').exists` (y equivalentes para `teacher`), lo que provoca `TemplateSyntaxError` porque el motor no admite llamadas a métodos con parámetros dentro de `{% if %}`. La vista `security/views/SecurityViews.login` no aporta banderas de rol en el contexto, de modo que el error se manifiesta cada vez que se renderiza el template base en Daphne.【F:templates/base.html†L37-L56】【F:security/views/SecurityViews.py†L10-L44】
2. **Duplicidad de navegación por roles y redirecciones incorrectas**: El menú principal en `templates/base.html` sigue generando enlaces de alumnos y profesores simultáneamente cuando un usuario pertenece a más de un grupo. Además, la comprobación directa de grupos desde plantilla impide personalizar flujos (p.ej. profesores redirigidos al admin).【F:templates/base.html†L37-L68】
3. **Modal “Nuevo servicio” inestable**: Aunque existe un manejador `htmx:afterRequest` en `templates/containers/student_panel.html`, los errores del backend (p. ej. fallos en `run_container`) devuelven 500 y evitan que se cierre el modal o se limpien campos, dejando al usuario sin feedback claro. Tampoco se valida el nombre del servicio en mayúsculas ni se muestran mensajes específicos del backend al usuario.【F:templates/containers/student_panel.html†L168-L212】【F:containers/services.py†L70-L144】
4. **Persistencia de contenedores “running” pese a errores**: `_sync_service` en `containers/views.py` solo marca el servicio como `removed` si la consulta a Docker falla; no sincroniza estados intermedios (pausado, reiniciando), de modo que un contenedor caído puede permanecer en la tabla como activo. A su vez, `run_container` no actualiza `status` cuando un compose falla antes de lanzar contenedores, lo que alimenta la inconsistencia observada en los checks.【F:containers/views.py†L23-L84】【F:containers/services.py†L122-L209】
5. **Gestión admin de alumnos con validaciones frágiles**: `PlayerAdminForm.clean` obliga a seleccionar usuario o crear uno nuevo, incluso cuando se rellenan todos los campos, y marca errores genéricos. Esto coincide con la incidencia reportada en la creación de alumnos desde el admin (campos obligatorios fallan).【F:paasify/admin.py†L85-L148】
6. **Flujo de profesor hacia vistas de alumno**: `post_login` en `containers/views.py` sólo diferencia superusuario y profesor, pero la navegación en `templates/base.html` permite que un profesor llegue a URLs de alumno (`containers:student_panel`), reproduciendo la redirección al admin y la petición de credenciales descritas en los checks.【F:containers/views.py†L318-L362】【F:templates/base.html†L37-L68】
7. **Carga de archivos Docker**: `run_container` guarda Dockerfile/compose en temporales pero no limpia correctamente los recursos ni registra los comandos ejecutados; cuando `docker compose` falla, solo se devuelve el stderr plano y no se adjunta a la respuesta HTMX, generando la percepción de “sin logs”.【F:containers/services.py†L153-L216】
8. **Terminal WebSocket inestable**: `containers/consumers.py` crea un `exec_start` directo y mantiene un socket sin reconexión ni heartbeats. Ante un corte, se cierra la conexión y se intenta reabrir sin revalidar contenedor, justificando las desconexiones constantes observadas.【F:containers/consumers.py†L37-L104】
9. **Sincronización tras logout/login**: `ServiceViewSet.get_queryset` ejecuta `_sync_service` pero no refresca `status` cuando Docker no responde; el resultado queda cacheado hasta la recarga de la tabla por HTMX, por lo que tras reingresar la lista puede aparecer vacía hasta que se triggeréa otra actualización.【F:containers/views.py†L57-L84】

**Ejecución de validaciones:**
- `python -m compileall app_passify containers paasify security templates tests` → compilación correcta.
- `pytest` → 1 prueba pasada, 1 omitida por falta de daemon Docker.

## 💡 Propuestas de solución
- Calcular `is_student`, `is_teacher` y `is_admin` en un context processor o en cada vista y utilizar flags booleanas en las plantillas, eliminando las llamadas directas a `user.groups.filter(...)`.
- Simplificar el menú en `base.html` para que cada rol muestre solo sus enlaces y evitar rutas cruzadas.
- Propagar los mensajes de error de `run_container` a la interfaz HTMX, cerrar el modal incluso ante fallos y normalizar el nombre del servicio a minúsculas (o validar antes de enviar).
- Extender `_sync_service` para actualizar estados (`paused`, `error`) y limpiar `assigned_port` cuando el contenedor ya no existe; registrar en la base cualquier excepción de compose/Dockerfile.
- Revisar `PlayerAdminForm` para que los campos marcados como completados no sean invalidados por validaciones genéricas, permitiendo crear alumnos sin crear usuario nuevo si se proporciona uno existente.
- Ajustar el control de acceso en vistas y plantillas para que los profesores no puedan crear contenedores ni acceder a paneles de alumno, y mostrar vistas específicas de profesor.
- Añadir registros detallados y limpieza de temporales en `run_container`, garantizando que los logs se persistan en `service.logs` y se presenten al usuario.
- Introducir un bucle asíncrono en el consumer WebSocket con heartbeats o reconexiones controladas, y manejo explícito del cierre del exec.

## 🧠 Impacto estimado
Aplicar estas medidas estabilizará el login bajo Daphne, evitará duplicidad de navegación y garantizará que cada rol acceda únicamente a sus funcionalidades. Los alumnos recibirán feedback consistente en la creación de contenedores, los profesores mantendrán un flujo claro hacia sus asignaturas y el panel admin podrá crear alumnos sin fricciones. Además, mejorar la sincronización con Docker reducirá la discrepancia entre el estado real y la interfaz, mientras que la terminal WebSocket será más fiable.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.
---
