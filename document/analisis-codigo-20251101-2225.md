# Análisis de Código — Rama: codigo-y-analisis
_Resumen: Inspección de los fallos funcionales reportados en el último check y de la lógica de roles vinculada a contenedores._

## 🧩 Objetivo
Revisar el flujo de despliegue de contenedores y las vistas enlazadas desde el panel del alumno/profesor para identificar las causas de los errores detectados durante las pruebas funcionales.

## 📂 Archivos revisados
- `containers/admin.py`
- `containers/services.py`
- `containers/views.py`
- `containers/serializers.py`
- `templates/containers/_service_rows.html`
- `templates/containers/student_panel.html`
- `templates/professor/dashboard.html`
- `templates/admin/allowedimage_test_logs.html`
- `app_passify/urls.py`
- `paasify/urls.py`
- `tests/test_containers.py`

## ⚠️ Problemas detectados
1. **Duplicación del encabezado "Resultado de prueba de imágenes"**: la vista administrativa añade `title = "Resultado de prueba de imágenes"` al contexto mientras que la plantilla fija el mismo texto en un `<h1>`, generando el mensaje duplicado en pantalla (`containers/admin.py` y `templates/admin/allowedimage_test_logs.html`).
2. **Error `NoReverseMatch` para `terminal_view`**: los enlaces generados en `templates/containers/_service_rows.html` y en componentes asociados usan `{% url 'terminal_view' %}` sin el namespace `containers:`. Al estar la app namespaced, Django no encuentra la URL cuando se renderiza el panel del alumno.
3. **Bloqueo al gestionar contenedores Docker**: existen instancias globales de `docker.from_env()` en `containers/admin.py`, `containers/services.py` y `containers/views.py`. Cuando el daemon no está accesible (como en los tests), la importación lanza `DockerException` y aborta tanto la administración como las vistas y la ejecución de pruebas (`pytest` termina por error de conexión).
4. **Subida de `Dockerfile`/`docker-compose.yml` poco robusta**: la lógica de `_save_filefield_to` vuelve a abrir el `FieldFile` sin usar el gestor de contexto (`with ff.open("rb") as fh:`), lo que deja delegada la lectura en el objeto `FieldFile` y puede provocar problemas con ficheros grandes o almacenamientos remotos. Además, toda la preparación de archivos se ejecuta con permisos del proceso web, sin comprobaciones previas del tamaño/extension más allá del front-end, lo que explica los fallos observados durante el testing manual.
5. **Profesores con capacidad de crear contenedores**: la vista `student_panel` solo exige autenticación (`@login_required`) y el menú principal apunta siempre a esa URL, por lo que cualquier profesor termina en la pantalla de creación de servicios. La API `ServiceViewSet` tampoco filtra por rol y, de hecho, permite crear servicios a un profesor siempre que sea docente de la asignatura seleccionada.
6. **Accesos que dependen del panel de administración**: en `templates/professor/dashboard.html` se enlaza a `/admin/paasify/sport/<id>/change/` y `/admin/paasify/game/<id>/change/`. Estos enlaces solo funcionan si el usuario es `staff`, de lo contrario el profesor recibe un error de autorización.
7. **Lógica de roles incompleta**: aunque `post_login` separa redirecciones para superusuarios, profesores y alumnos, no existen vistas específicas para que el profesor gestione alumnos/proyectos sin pasar por el admin, y tampoco hay separación entre panel de estudiante y panel de profesor. Los enlaces de la navegación (`templates/base.html`) dirigen siempre a vistas pensadas para alumnos, rompiendo la matriz de permisos esperada.
8. **Tests imposibles de ejecutar en entornos sin Docker**: `tests/test_containers.py` crea contenedores reales usando `docker.from_env()`. Sin un daemon disponible, las pruebas fallan de inmediato y contaminan cualquier pipeline sin Docker, como quedó patente en la ejecución de `pytest`.

## 💡 Propuestas de solución
1. Centralizar el título del informe de imágenes en un único lugar (contexto o plantilla) para evitar la duplicación visual.
2. Actualizar los `href` y `hx-get` en las plantillas para usar los nombres cualificados (`containers:terminal_view`, etc.) y revisar que las rutas registradas en `containers/urls.py` concuerden con los namespaces utilizados.
3. Sustituir los clientes Docker globales por fábricas perezosas (por ejemplo, `get_docker_client()`) que manejen `DockerException` y permitan continuar cuando el daemon esté caído; en los tests se pueden utilizar dobles/mocks.
4. Refactorizar `_save_filefield_to` para que opere con manejadores explícitos (`with ff.open("rb") as in_fh:`) y añadir validaciones de extensión/tamaño antes de escribir en disco. También conviene registrar los errores en el modelo (`service.logs`) para facilitar el diagnóstico.
5. Limitar el acceso a `student_panel` y a los endpoints de creación mediante verificaciones de grupo (`in_group(request.user, "student")`) o permisos específicos, redirigiendo a los profesores a su dashboard sin formularios de alta de contenedores.
6. Proporcionar vistas dedicadas para profesores (por ejemplo, listados de asignaturas y proyectos dentro del propio sitio) y reemplazar los enlaces al admin por rutas propias que no requieran privilegios de `staff`.
7. Revisar la navegación principal (`templates/base.html`) para que las opciones visibles dependan del rol activo y añadir comprobaciones de rol adicionales en `ServiceViewSet` y vistas relacionadas, asegurando que los alumnos no necesiten permisos elevados para operar.
8. Adaptar la suite de tests para que use `pytest.mark.skipif` cuando no haya daemon Docker, o introducir mocks/fakes del cliente Docker. De esta forma, `pytest` podrá ejecutarse como parte de la validación continua sin fallar por ausencia de infraestructura.

## 🧠 Impacto estimado
Aplicar estas correcciones permitirá que las pruebas automatizadas se ejecuten sin bloqueos, mejorará la experiencia de alumnos y profesores al respetar los límites de cada rol y reducirá los fallos de usabilidad en la administración. Además, la gestión de archivos Docker será más segura y predecible incluso en despliegues con almacenamiento remoto.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.
