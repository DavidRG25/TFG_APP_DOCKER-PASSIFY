# AnÃ¡lisis de CÃ³digo â€” Rama: feature/analisis-codigo
*Nota 2025-11-05: el modelo `Sport` fue renombrado a `Subject` y las referencias históricas se conservan sólo como contexto.*
_Resumen: RevisiÃ³n completa tras los Ãºltimos tests funcionales y ejecuciÃ³n ASGI con Daphne, identificando los regresos pendientes en permisos, plantillas y orquestaciÃ³n de contenedores._

## ðŸ§© Objetivo
Reevaluar la rama `feature/analisis-codigo` despuÃ©s de las mejoras aplicadas por el usuario, contrastÃ¡ndola con los hallazgos de los tres checks funcionales y la prueba final con Daphne.

## ðŸ“‚ Archivos revisados
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

## âš ï¸ Problemas detectados
1. **Fallo crÃ­tico en el login bajo Daphne.** `templates/base.html` evalÃºa expresiones como `user.groups.filter(name__iexact='student')` dentro de `{% if %}`, lo que Django prohÃ­be y provoca el `TemplateSyntaxError` reproducido en la ejecuciÃ³n ASGI. AdemÃ¡s, `security/views/SecurityViews.login` no aÃ±ade banderas de rol al contexto, obligando a la plantilla a invocar consultas directas.
2. **Matriz de navegaciÃ³n dependiente de lÃ³gica de plantilla.** Las secciones "Proyectos" y "Mis asignaturas" se pintan Ãºnicamente con condicionales en `base.html`; los profesores acaban en redirecciones cÃ­clicas (panel alumno â†’ dashboard profesor) y los alumnos ven ambos enlaces apuntar a vistas HTMX que comparten plantilla (`student_panel.html`) generando confusiÃ³n.
3. **GestiÃ³n de alumnos en admin inestable.** `paasify/admin.py` mantiene campos extra (`players`) y obliga a escoger usuario existente o crear uno nuevo. Cuando no se marca la casilla "Crear usuario nuevo" la validaciÃ³n lanza un `ValidationError` genÃ©rico que el admin reporta como "Este campo es obligatorio" aunque todos los campos estÃ©n rellenados, reproduciendo el bug descrito en el CHECK 3.
4. **Borrado de asignaturas rompe integridad referencial.** `Game` (paasify/models/ProjectModel.py) usa `on_delete=models.DO_NOTHING`, por lo que al eliminar un `Sport` se dispara `IntegrityError` y deja registros huÃ©rfanos.
5. **Alta de servicios sin normalizar nombres.** En `containers/services.py` y `ServiceSerializer` no se valida que `service.name` sea slug/`lowercase`; Docker rechaza repositorios con mayÃºsculas (`repository name must be lowercase`).
6. **Modal HTMX sin limpiar tras errores.** El flujo de creaciÃ³n (`student_panel.html`) solo oculta y resetea el modal cuando la respuesta es 2xx. Ante respuestas 4xx/5xx (Dockerfile ausente, compose fallido, nombre invÃ¡lido) el formulario queda abierto sin feedback visible y mantiene archivos seleccionados.
7. **Carga de ZIP en modo catÃ¡logo.** Para imÃ¡genes del catÃ¡logo se monta el ZIP original como volumen (`service.code.path` â†’ `/app`). Docker espera un directorio y responde "not a directory", reproduciendo el fallo de CHECK 2.
8. **docker-compose sin soporte de Dockerfile de contexto.** El validador obliga a subir *solo* Dockerfile o *solo* docker-compose. Muchos `docker-compose.yml` referencian un Dockerfile (`build: .`), por lo que la acciÃ³n actual lanza `open Dockerfile: no such file or directory`.
9. **SincronizaciÃ³n de estado limitada.** `_sync_service` Ãºnicamente marca `removed` cuando el contenedor no existe. Contenedores pausados/fallidos siguen figurando como `running`, coincidiendo con los sÃ­ntomas del CHECK 3 y con la desapariciÃ³n temporal de servicios tras re-login.
10. **WebSocket inestable.** `TerminalConsumer` crea un `threading.Thread` que cierra el socket al primer `recv()` vacÃ­o sin reenlazar; no hay keep-alive ni reintentos. Esto explica las desconexiones constantes registradas en CHECK 3.
11. **Carga de estÃ¡ticos en bucle.** El `tbody` de `student_panel.html` refresca cada 5 s con HTMX, pero tambiÃ©n reinserta los scripts de Bootstrap/HTMX provocando flashes y recarga de recursos en navegaciÃ³n prolongada.
12. **DocumentaciÃ³n desactualizada.** `README.md` no describe el arranque con Daphne (`python -m daphne ...`), paso imprescindible para reproducir el error crÃ­tico reportado.

## ðŸ’¡ Propuestas de soluciÃ³n
1. Exponer flags de rol (`is_student`, `is_teacher`, `is_admin`) desde `SecurityViews.login` y sustituir las llamadas a QuerySet por dichas banderas o por filtros precalculados en un `context_processor`/etiqueta personalizada.
2. Separar menÃºs por rol desde la vista (inyecciÃ³n de listas de navegaciÃ³n) o mediante bloques en plantillas especÃ­ficas para alumnos y profesores, evitando redirecciones implÃ­citas y mostrando rutas coherentes.
3. Ajustar `PlayerAdminForm.clean()` para emitir mensajes guiados (p.ej. `self.add_error('user', ...)`) en lugar de `ValidationError` global, y ocultar el antiguo campo `players` en la interfaz para impedir falsos positivos.
4. Cambiar los `ForeignKey` de `Game` a `PROTECT`/`CASCADE` y aÃ±adir limpieza en cascada para que eliminar una asignatura no rompa la base de datos.
5. Normalizar `service.name` (`slugify`/`lower()`) en el serializer y bloquear caracteres invÃ¡lidos antes de construir etiquetas Docker.
6. Gestionar respuestas HTMX con `htmx:responseError` mostrando errores en el modal y limpiando los campos tras cada intento (exitoso o no) para evitar estados inconsistentes.
7. Extraer el ZIP a un directorio temporal en modo catÃ¡logo o deshabilitar el campo `code` cuando no se construye imagen personalizada.
8. Permitir subir `docker-compose` junto a un bundle de contexto (ZIP con Dockerfile) o modificar la validaciÃ³n para aceptar ambos ficheros cuando el compose declare `build`.
9. Extender `_sync_service` para consultar `docker_client.containers.get(...).status` y sincronizar `running/stopped/error`, ademÃ¡s de refrescar datos tras `login` mediante una recarga inmediata del `tbody`.
10. Migrar el consumidor a `AsyncWebsocketConsumer` con `asyncio` + `create_task`, gestionando keep-alive y reconexiones controladas.
11. Mover las etiquetas `<script>` fuera del fragmento refrescado y reducir la frecuencia del `hx-trigger` para evitar recarga de estÃ¡ticos.
12. Actualizar `README.md` con el flujo ASGI (Daphne) y dependencias Docker/Compose para QA.

## ðŸ§  Impacto estimado
Aplicar estas correcciones estabilizarÃ¡ el acceso bajo ASGI, garantizarÃ¡ que cada rol reciba menÃºs y permisos consistentes, y evitarÃ¡ que los contenedores queden en estados fantasma o sin logs. TambiÃ©n reducirÃ¡ fricciones en el panel de administraciÃ³n y permitirÃ¡ a QA reproducir los pasos exactos para validar la plataforma.

## ðŸ§¾ ConfirmaciÃ³n requerida
âš ï¸ No realices ningÃºn cambio en el cÃ³digo sin la aprobaciÃ³n explÃ­cita del usuario.

## ðŸ“Š Resultados de validaciones
- `python -m compileall app_passify containers paasify tests security templates` â†’ **OK**
- `pytest` â†’ **1 prueba pasada, 1 omitida (Docker no disponible)**
