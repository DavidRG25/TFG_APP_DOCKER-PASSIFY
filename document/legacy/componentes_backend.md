# Componentes backend detallados

## ConfiguraciÃ³n central (`app_passify/settings.py`)
- Define `INSTALLED_APPS` mezclando aplicaciones nativas, apps propias (`paasify`, `containers`, `security`) y paquetes externos como `rest_framework`, `channels` y `whitenoise`.
- Habilita almacenamiento comprimido de archivos estÃ¡ticos mediante `CompressedManifestStaticFilesStorage` y declara `STATICFILES_DIRS` apuntando a `paasify/static`.
- Configura autenticaciÃ³n con sesiones y JWT simultÃ¡neos, y define rutas de login/logout personalizadas.
- Mantiene `DEBUG=True` y una `SECRET_KEY` fija, lo que resalta la necesidad de variables de entorno para producciÃ³n.

## Modelos de dominio acadÃ©mico (`paasify/models`)
- `StudentModel.Player` enlaza usuarios de `auth` con registros legacy y conserva campos heredados como `nombre`, `year` (email) y `sexo`. (`StudentModel.py`)
- `SubjectModel.Subject` representa asignaturas, incorpora relaciÃ³n 1:N con `teacher_user` y M:N con `students`, ademÃ¡s de campos legacy como `players`. (`SubjectModel.py`)
- `ProjectModel.UserProject` vincula asignaturas y alumnos para gestionar proyectos con sello temporal. (`ProjectModel.py`)
- `SubjectModel.Subject` parece ser un remanente no integrado con usuarios, manteniendo profesor y categorÃ­a como `CharField`.

## GestiÃ³n de contenedores (`containers`)
### Modelos (`containers/models.py`)
- `PortReservation` mantiene puertos ocupados dentro del rango 40000-50000 para evitar colisiones.
- `Service` describe un despliegue: propietario (`AUTH_USER_MODEL`), asignatura opcional (`Subject`), imagen/catalogo, `Dockerfile`, `docker-compose`, `code` (ZIP), puertos, variables de entorno y volÃºmenes.
- `AllowedImage` actÃºa como catÃ¡logo de imÃ¡genes aprobadas (`unique_together` sobre `name` y `tag`).

### Serializadores (`containers/serializers.py`)
- `ServiceSerializer` centraliza reglas de negocio diferenciando modo catÃ¡logo vs. personalizado, valida JSON (`env_vars`, `volumes`) y permisos sobre asignaturas.
- `AllowedImageSerializer` expone el catÃ¡logo.

### Servicios Docker (`containers/services.py`)
- `_compose_cmd` detecta automÃ¡ticamente si usar `docker compose` v2 o `docker-compose` v1.
- `_reserve_free_port` y `_release_port` coordinan reservas directas en BD, complementadas por `PortReservation.reserve_free_port`.
- `run_container` prioriza despliegue segÃºn `compose` â†’ `Dockerfile` â†’ imagen: maneja temporales, compilaciÃ³n de imagen, asignaciÃ³n de puertos, montaje de volÃºmenes y propagaciÃ³n de errores/logs al modelo.
- `stop_container` y `remove_container` sincronizan estado y liberan puertos.

### Vistas y API (`containers/views.py`)
- `ServiceViewSet` ofrece CRUD restringido al propietario, aplica reglas de subida de archivos y lanza `run_container` tras crear un servicio.
- Acciones extra `start`, `stop`, `remove`, `logs`, `dockerfile`, `compose` complementan la gestiÃ³n del ciclo de vida.
- Vistas HTML (`student_panel`, `student_subjects`, `professor_dashboard`, etc.) filtran servicios segÃºn rol y asignatura.
- `terminal_view` valida que el servicio tenga contenedor activo antes de mostrar la terminal.

### WebSocket (`containers/consumers.py`)
- `TerminalConsumer` valida propiedad del servicio, abre un `exec_create` con `/bin/sh` y retransmite datos entre Docker y el navegador mediante hilos para lectura asÃ­ncrona.

## NavegaciÃ³n general (`paasify/views/NavigationViews.py`)
- Proporciona portada (`index`), tablas paginadas de proyectos (`table`) y una vista de configuraciÃ³n restringida a usuarios autenticados.
- `get_notifications` retorna una lista vacÃ­a, indicando funcionalidad pendiente.

## Rutas y Channels
- `routing.py` define el `ProtocolTypeRouter` para WebSockets utilizando `containers.routing.websocket_urlpatterns`.
- `containers/routing.py` expone la ruta `/ws/terminal/<service_id>/` asociada al consumidor `TerminalConsumer`.

## AplicaciÃ³n `security`
- Actualmente contiene solo estructuras base (`AppConfig`, archivos vacÃ­os), sin modelos ni vistas implementadas, lo que sugiere una futura extensiÃ³n para controles adicionales.

