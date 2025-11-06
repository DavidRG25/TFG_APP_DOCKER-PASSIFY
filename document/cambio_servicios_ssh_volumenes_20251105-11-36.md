# Cambios en Servicios, SSH y Volúmenes

## 1. Resumen de Cambios

- **SSH por Defecto**: Se ha eliminado la opción de habilitar SSH al crear un servicio. Ahora, todos los servicios se crean con SSH habilitado por defecto, asignando un puerto dinámico en el rango 40000-50000.
- **Volúmenes Persistentes**: Cada servicio crea automáticamente un volumen persistente con el nombre `svc_{service_id}`, que se monta en `/home/user/data` dentro del contenedor.
- **Conexión Local Eliminada**: Se ha eliminado por completo la funcionalidad de "Conexión Local".
- **Nueva Interfaz de Usuario**: Se ha rediseñado la interfaz de "Mis servicios" para incluir un nuevo modal que muestra el comando de conexión SSH.
- **Terminal Web Mejorada**: Se ha implementado una nueva terminal web basada en `xterm.js` y `WebSockets`.
- **Refactorización de Docker**: Se ha refactorizado la interacción con Docker para utilizar `subprocess` con `sudo`, solucionando los problemas de permisos en el entorno de ejecución.

## 2. Cambios en el Código

### 2.1. `containers/models.py`

- Se ha eliminado el campo `enable_ssh` del modelo `Service`.
- Se ha añadido el campo `volume_name` al modelo `Service` para almacenar el nombre del volumen persistente.

### 2.2. `containers/services.py`

- Se ha modificado la función `_run_container_internal` para:
    - Habilitar SSH por defecto en todos los contenedores.
    - Crear un volumen persistente para cada servicio.
    - Utilizar `subprocess` con `sudo` para todas las interacciones con Docker.
- Se ha modificado la función `remove_container` para:
    - Eliminar el volumen persistente al eliminar el servicio.
    - Liberar el puerto SSH asignado.
    - Utilizar `subprocess` con `sudo` para todas las interacciones con Docker.

### 2.3. `containers/views.py`

- Se ha eliminado la lógica relacionada con `enable_ssh` en el `ServiceViewSet`.
- Se ha añadido un nuevo endpoint `ssh-uri` al `ServiceViewSet` para obtener el comando de conexión SSH.
- Se ha mejorado el endpoint `logs` para mostrar los logs en un modal.
- Se ha actualizado la vista `terminal_view` para utilizar la nueva terminal web.
- Se han actualizado los permisos para permitir a los `Teachers` y `Admins` acceder a los servicios de otros usuarios.

### 2.4. `containers/urls.py`

- Se han añadido las nuevas rutas para los endpoints de la API.

### 2.5. `containers/routing.py`

- Se ha creado este nuevo archivo para gestionar el enrutamiento de los `WebSockets` de la terminal.

### 2.6. `templates/containers/student_panel.html`

- Se ha eliminado el bloque de "Conexión Local" y el interruptor de SSH.
- Se ha añadido un nuevo modal genérico para mostrar los logs y el comando de conexión SSH.

### 2.7. `templates/containers/_service_rows.html`

- Se ha reemplazado el botón de "Conexión Local" por un nuevo botón de "SSH".
- Se han actualizado los botones de acciones para utilizar el nuevo modal genérico y mejorar la experiencia de usuario con `htmx`.

### 2.8. `templates/containers/terminal.html`

- Se ha actualizado la plantilla para utilizar `xterm.js` y `WebSockets`.
