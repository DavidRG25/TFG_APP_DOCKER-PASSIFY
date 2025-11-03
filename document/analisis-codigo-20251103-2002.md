# Análisis de Código — Rama: feature/analisis-codigo
_Resumen: Revisión completa tras los últimos tests funcionales y ejecución ASGI con Daphne, identificando los regresos pendientes en permisos, plantillas y orquestación de contenedores._

## 🧩 Objetivo
Reevaluar la rama `feature/analisis-codigo` después de las mejoras aplicadas por el usuario, contrastándola con los hallazgos de los tres checks funcionales y la prueba final con Daphne.

## 📂 Archivos revisados
- `templates/base.html`
- `templates/registration/login.html`
- `templates/containers/student_panel.html`
- `templates/containers/_service_rows.html`
- `templates/containers/subjects.html`
- `templates/professor/dashboard.html`
- `containers/views.py`
- `containers/services.py`
- `containers/serializers.py`
- `containers/consumers.py`
- `containers/admin.py`
- `containers/urls.py`
- `app_passify/urls.py`
- `paasify/admin.py`
- `paasify/models/SportModel.py`
- `paasify/models/ProjectModel.py`
- `tests/test_containers.py`

## ⚠️ Problemas detectados
1. **Fallo crítico en el login bajo Daphne.** `templates/base.html` evalúa expresiones como `user.groups.filter(name__iexact='student')` dentro de `{% if %}`, lo que Django prohíbe y provoca el `TemplateSyntaxError` reproducido en la ejecución ASGI. Además, `security/views/SecurityViews.login` no añade banderas de rol al contexto, obligando a la plantilla a invocar consultas directas.
2. **Matriz de navegación dependiente de lógica de plantilla.** Las secciones "Proyectos" y "Mis asignaturas" se pintan únicamente con condicionales en `base.html`; los profesores acaban en redirecciones cíclicas (panel alumno → dashboard profesor) y los alumnos ven ambos enlaces apuntar a vistas HTMX que comparten plantilla (`student_panel.html`) generando confusión.
3. **Gestión de alumnos en admin inestable.** `paasify/admin.py` mantiene campos extra (`players`) y obliga a escoger usuario existente o crear uno nuevo. Cuando no se marca la casilla "Crear usuario nuevo" la validación lanza un `ValidationError` genérico que el admin reporta como "Este campo es obligatorio" aunque todos los campos estén rellenados, reproduciendo el bug descrito en el CHECK 3.
4. **Borrado de asignaturas rompe integridad referencial.** `Game` (paasify/models/ProjectModel.py) usa `on_delete=models.DO_NOTHING`, por lo que al eliminar un `Sport` se dispara `IntegrityError` y deja registros huérfanos.
5. **Alta de servicios sin normalizar nombres.** En `containers/services.py` y `ServiceSerializer` no se valida que `service.name` sea slug/`lowercase`; Docker rechaza repositorios con mayúsculas (`repository name must be lowercase`).
6. **Modal HTMX sin limpiar tras errores.** El flujo de creación (`student_panel.html`) solo oculta y resetea el modal cuando la respuesta es 2xx. Ante respuestas 4xx/5xx (Dockerfile ausente, compose fallido, nombre inválido) el formulario queda abierto sin feedback visible y mantiene archivos seleccionados.
7. **Carga de ZIP en modo catálogo.** Para imágenes del catálogo se monta el ZIP original como volumen (`service.code.path` → `/app`). Docker espera un directorio y responde "not a directory", reproduciendo el fallo de CHECK 2.
8. **docker-compose sin soporte de Dockerfile de contexto.** El validador obliga a subir *solo* Dockerfile o *solo* docker-compose. Muchos `docker-compose.yml` referencian un Dockerfile (`build: .`), por lo que la acción actual lanza `open Dockerfile: no such file or directory`.
9. **Sincronización de estado limitada.** `_sync_service` únicamente marca `removed` cuando el contenedor no existe. Contenedores pausados/fallidos siguen figurando como `running`, coincidiendo con los síntomas del CHECK 3 y con la desaparición temporal de servicios tras re-login.
10. **WebSocket inestable.** `TerminalConsumer` crea un `threading.Thread` que cierra el socket al primer `recv()` vacío sin reenlazar; no hay keep-alive ni reintentos. Esto explica las desconexiones constantes registradas en CHECK 3.
11. **Carga de estáticos en bucle.** El `tbody` de `student_panel.html` refresca cada 5 s con HTMX, pero también reinserta los scripts de Bootstrap/HTMX provocando flashes y recarga de recursos en navegación prolongada.
12. **Documentación desactualizada.** `README.md` no describe el arranque con Daphne (`python -m daphne ...`), paso imprescindible para reproducir el error crítico reportado.

## 💡 Propuestas de solución
1. Exponer flags de rol (`is_student`, `is_teacher`, `is_admin`) desde `SecurityViews.login` y sustituir las llamadas a QuerySet por dichas banderas o por filtros precalculados en un `context_processor`/etiqueta personalizada.
2. Separar menús por rol desde la vista (inyección de listas de navegación) o mediante bloques en plantillas específicas para alumnos y profesores, evitando redirecciones implícitas y mostrando rutas coherentes.
3. Ajustar `PlayerAdminForm.clean()` para emitir mensajes guiados (p.ej. `self.add_error('user', ...)`) en lugar de `ValidationError` global, y ocultar el antiguo campo `players` en la interfaz para impedir falsos positivos.
4. Cambiar los `ForeignKey` de `Game` a `PROTECT`/`CASCADE` y añadir limpieza en cascada para que eliminar una asignatura no rompa la base de datos.
5. Normalizar `service.name` (`slugify`/`lower()`) en el serializer y bloquear caracteres inválidos antes de construir etiquetas Docker.
6. Gestionar respuestas HTMX con `htmx:responseError` mostrando errores en el modal y limpiando los campos tras cada intento (exitoso o no) para evitar estados inconsistentes.
7. Extraer el ZIP a un directorio temporal en modo catálogo o deshabilitar el campo `code` cuando no se construye imagen personalizada.
8. Permitir subir `docker-compose` junto a un bundle de contexto (ZIP con Dockerfile) o modificar la validación para aceptar ambos ficheros cuando el compose declare `build`.
9. Extender `_sync_service` para consultar `docker_client.containers.get(...).status` y sincronizar `running/stopped/error`, además de refrescar datos tras `login` mediante una recarga inmediata del `tbody`.
10. Migrar el consumidor a `AsyncWebsocketConsumer` con `asyncio` + `create_task`, gestionando keep-alive y reconexiones controladas.
11. Mover las etiquetas `<script>` fuera del fragmento refrescado y reducir la frecuencia del `hx-trigger` para evitar recarga de estáticos.
12. Actualizar `README.md` con el flujo ASGI (Daphne) y dependencias Docker/Compose para QA.

## 🧠 Impacto estimado
Aplicar estas correcciones estabilizará el acceso bajo ASGI, garantizará que cada rol reciba menús y permisos consistentes, y evitará que los contenedores queden en estados fantasma o sin logs. También reducirá fricciones en el panel de administración y permitirá a QA reproducir los pasos exactos para validar la plataforma.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.

## 📊 Resultados de validaciones
- `python -m compileall app_passify containers paasify tests security templates` → **OK**
- `pytest` → **1 prueba pasada, 1 omitida (Docker no disponible)**
