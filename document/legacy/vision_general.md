# Visión general del repositorio PaaSify

## Propósito del proyecto
PaaSify es una plataforma educativa basada en Django que permite a docentes y estudiantes desplegar servicios Docker desde una interfaz web. La aplicación combina vistas HTML tradicionales con endpoints REST y soporte WebSocket para proporcionar gestión de contenedores, logs y una terminal interactiva dentro del navegador.

## Estructura principal
| Ruta | Descripción |
| --- | --- |
| `app_passify/` | Configuración base de Django (settings, URLs, ASGI/WSGI). |
| `containers/` | App que encapsula la lógica de contenedores Docker, APIs REST, vistas HTML y consumidores WebSocket. |
| `paasify/` | App con modelos legacy (alumnos, asignaturas, proyectos) y vistas de navegación generales. |
| `security/` | App placeholder para funcionalidades de seguridad (actualmente vacía). |
| `templates/` | Plantillas Django para paneles, formularios y dashboards. |
| `staticfiles/`, `paasify/static/` | Activos estáticos y carpeta objetivo para `collectstatic`. |
| `dockerfiles/`, `compose_files/`, `containers/edit_service.html` | Recursos usados para pruebas o ejemplos de despliegue. |
| `tests/`, `pytest.ini` | Pruebas automatizadas (principalmente para la app `containers`). |

## Dependencias relevantes
- **Django** y **Django REST Framework** gestionan el backend web y la API. (`app_passify/settings.py`)
- **Django Channels** habilita WebSockets para la terminal en vivo (`routing.py`, `containers/consumers.py`).
- **docker SDK para Python** se usa para gestionar contenedores (`containers/services.py`, `containers/consumers.py`).
- **whitenoise** sirve archivos estáticos en producción (`app_passify/settings.py`).
- **rest_framework_simplejwt** provee autenticación JWT complementaria a las sesiones.

## Flujo funcional resumido
1. El usuario inicia sesión y es redirigido según su rol (`containers/views.py::post_login`).
2. Los alumnos pueden crear servicios desde la API REST (`containers/views.py::ServiceViewSet.create`).
3. `containers/services.py` interpreta la configuración aportada (imagen catalogada, Dockerfile o docker-compose), prepara ficheros temporales y ejecuta el contenedor vía Docker.
4. Los profesores consultan dashboards con asignaturas y proyectos asociados (`containers/views.py::professor_dashboard`, `paasify/models`).
5. La terminal web utiliza Channels para abrir una shell `/bin/sh` en el contenedor (`containers/consumers.py`).
6. Las reservas de puertos se coordinan con el modelo `PortReservation` para evitar colisiones (`containers/models.py`).

## Consideraciones destacadas
- `DEBUG` está activado y la clave secreta se encuentra en texto plano; esto es aceptable para desarrollo pero debe externalizarse en producción (`app_passify/settings.py`).
- El rango de puertos expuestos a servicios se limita a 40000-50000 (`containers/models.py`).
- El repositorio incluye `db.sqlite3`, útil para pruebas locales pero no recomendado para despliegue.
- Varias plantillas y vistas legacy siguen utilizando modelos antiguos (`paasify/models/*`), coexistiendo con los nuevos campos basados en usuarios de `auth`.
- Existe una app `security` sin lógica implementada, lo que indica trabajo pendiente en esa área.
