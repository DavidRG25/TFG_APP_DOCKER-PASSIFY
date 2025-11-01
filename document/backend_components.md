# Componentes backend detallados

## Configuración central (`app_passify/settings.py`)
- Define `INSTALLED_APPS` mezclando aplicaciones nativas, apps propias (`paasify`, `containers`, `security`) y paquetes externos como `rest_framework`, `channels` y `whitenoise`.
- Habilita almacenamiento comprimido de archivos estáticos mediante `CompressedManifestStaticFilesStorage` y declara `STATICFILES_DIRS` apuntando a `paasify/static`.
- Configura autenticación con sesiones y JWT simultáneos, y define rutas de login/logout personalizadas.
- Mantiene `DEBUG=True` y una `SECRET_KEY` fija, lo que resalta la necesidad de variables de entorno para producción.

## Modelos de dominio académico (`paasify/models`)
- `StudentModel.Player` enlaza usuarios de `auth` con registros legacy y conserva campos heredados como `nombre`, `year` (email) y `sexo`. (`StudentModel.py`)
- `SportModel.Sport` representa asignaturas, incorpora relación 1:N con `teacher_user` y M:N con `students`, además de campos legacy como `players`. (`SportModel.py`)
- `ProjectModel.Game` vincula asignaturas y alumnos para gestionar proyectos con sello temporal. (`ProjectModel.py`)
- `SubjectModel.Subject` parece ser un remanente no integrado con usuarios, manteniendo profesor y categoría como `CharField`.

## Gestión de contenedores (`containers`)
### Modelos (`containers/models.py`)
- `PortReservation` mantiene puertos ocupados dentro del rango 40000-50000 para evitar colisiones.
- `Service` describe un despliegue: propietario (`AUTH_USER_MODEL`), asignatura opcional (`Sport`), imagen/catalogo, `Dockerfile`, `docker-compose`, `code` (ZIP), puertos, variables de entorno y volúmenes.
- `AllowedImage` actúa como catálogo de imágenes aprobadas (`unique_together` sobre `name` y `tag`).

### Serializadores (`containers/serializers.py`)
- `ServiceSerializer` centraliza reglas de negocio diferenciando modo catálogo vs. personalizado, valida JSON (`env_vars`, `volumes`) y permisos sobre asignaturas.
- `AllowedImageSerializer` expone el catálogo.

### Servicios Docker (`containers/services.py`)
- `_compose_cmd` detecta automáticamente si usar `docker compose` v2 o `docker-compose` v1.
- `_reserve_free_port` y `_release_port` coordinan reservas directas en BD, complementadas por `PortReservation.reserve_free_port`.
- `run_container` prioriza despliegue según `compose` → `Dockerfile` → imagen: maneja temporales, compilación de imagen, asignación de puertos, montaje de volúmenes y propagación de errores/logs al modelo.
- `stop_container` y `remove_container` sincronizan estado y liberan puertos.

### Vistas y API (`containers/views.py`)
- `ServiceViewSet` ofrece CRUD restringido al propietario, aplica reglas de subida de archivos y lanza `run_container` tras crear un servicio.
- Acciones extra `start`, `stop`, `remove`, `logs`, `dockerfile`, `compose` complementan la gestión del ciclo de vida.
- Vistas HTML (`student_panel`, `student_subjects`, `professor_dashboard`, etc.) filtran servicios según rol y asignatura.
- `terminal_view` valida que el servicio tenga contenedor activo antes de mostrar la terminal.

### WebSocket (`containers/consumers.py`)
- `TerminalConsumer` valida propiedad del servicio, abre un `exec_create` con `/bin/sh` y retransmite datos entre Docker y el navegador mediante hilos para lectura asíncrona.

## Navegación general (`paasify/views/NavigationViews.py`)
- Proporciona portada (`index`), tablas paginadas de proyectos (`table`) y una vista de configuración restringida a usuarios autenticados.
- `get_notifications` retorna una lista vacía, indicando funcionalidad pendiente.

## Rutas y Channels
- `routing.py` define el `ProtocolTypeRouter` para WebSockets utilizando `containers.routing.websocket_urlpatterns`.
- `containers/routing.py` expone la ruta `/ws/terminal/<service_id>/` asociada al consumidor `TerminalConsumer`.

## Aplicación `security`
- Actualmente contiene solo estructuras base (`AppConfig`, archivos vacíos), sin modelos ni vistas implementadas, lo que sugiere una futura extensión para controles adicionales.
