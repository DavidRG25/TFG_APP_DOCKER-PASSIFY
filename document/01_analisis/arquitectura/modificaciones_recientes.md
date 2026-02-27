# Modificaciones Recientes

En este documento se detallan las últimas modificaciones realizadas en el proyecto PaaSify.

## Mejoras en las Pruebas

Se ha realizado una revisión exhaustiva del sistema de pruebas, añadiendo nuevas pruebas y refactorizando las existentes para mejorar la cobertura y la fiabilidad.

### Creación de Servicios

Se han añadido pruebas para `ServiceViewSet` que cubren todos los escenarios de creación de servicios:

- Creación de un servicio con una imagen por defecto.
- Creación de un servicio con un `Dockerfile` y código fuente.
- Creación de un servicio con un archivo `docker-compose.yml`.
- Validación de errores (p. ej., enviar `Dockerfile` y `compose` a la vez).
- Pruebas para la asignación de puertos personalizados.

### Visualización de Registros

Se ha añadido una prueba específica para la funcionalidad de visualización de registros, que verifica que los registros se recuperan correctamente de los contenedores de Docker.

### Terminal Interactivo

Se han añadido pruebas para el `TerminalConsumer` usando el `WebsocketCommunicator` de Channels. Estas pruebas simulan una conexión de cliente, el envío de comandos y la recepción de la salida, asegurando que el terminal interactivo funcione como se espera.

## Nuevas Funcionalidades

### Conexión Local con `docker exec`

Se ha añadido un nuevo botón "Conexión Local" en la pantalla de servicios del estudiante. Al hacer clic, se muestra un modal con el comando `docker exec -it <container_id> /bin/sh` listo para ser copiado, facilitando la conexión directa al contenedor desde la terminal local del usuario.

### Conexión Remota con SSH

Se ha implementado una nueva funcionalidad para permitir la conexión remota a los contenedores a través de SSH.

- **Habilitación de SSH**: En el formulario de creación de servicios, se ha añadido una opción para habilitar el acceso por SSH.
- **Generación de Claves**: Si se habilita SSH, la plataforma genera un par de claves SSH (pública y privada).
- **Inyección de Clave Pública**: La clave pública se inyecta automáticamente en el archivo `authorized_keys` del contenedor.
- **Exposición del Puerto 22**: El puerto 22 del contenedor se expone en un puerto aleatorio y seguro del servidor.
- **Modal con Clave Privada**: Al crear el servicio, se muestra un modal con la clave privada y el comando de conexión. La clave privada solo se muestra una vez y debe ser guardada por el usuario.

## Mejoras en el Panel de Administrador

### Gestión de Imágenes de Docker

Se ha mejorado la pantalla de administración de `AllowedImage` con las siguientes funcionalidades:

- **Verificación en Docker Hub**: Al guardar una nueva imagen permitida, la plataforma verifica si la imagen y el tag existen en Docker Hub.
- **Sugerencia de Tags**: En el formulario de edición de una imagen permitida, se muestra una lista de los tags disponibles para esa imagen en Docker Hub.

### Pantalla de Pruebas de Contenedores

Se ha mejorado la acción "Probar imagen (pull & run) y mostrar log" para que realice pruebas de "sanidad" más específicas. Por ejemplo, para una imagen de `mysql`, ahora se ejecuta `mysql --version` para verificar que el cliente de MySQL está instalado y funciona.
