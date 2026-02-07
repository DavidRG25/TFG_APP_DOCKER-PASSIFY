# Crear Servicio

Permite desplegar nuevos servicios, ya sea desde imágenes del catálogo o usando DockerHub.

**Endpoint:** `POST /api/containers/`

### Parámetros del Body (JSON)

| Campo             | Tipo   | Obligatorio | Descripción                                           |
| :---------------- | :----- | :---------- | :---------------------------------------------------- |
| **name**          | string | **Sí**      | Nombre único para el servicio (minúsculas y guiones). |
| **image**         | string | **Sí**      | Imagen del catálogo o de DockerHub (nombre:tag).      |
| **mode**          | string | **Sí**      | `default` (catálogo) o `dockerhub`.                   |
| **internal_port** | int    | No          | Puerto interno que usa la app (ej: 80, 5000).         |
| **environment**   | object | No          | Mapa de variables de entorno (key: value).            |
| **project**       | int    | **Sí**      | ID del proyecto al que se asocia este despliegue.     |
| **subject**       | int    | **Sí**      | ID de la asignatura a la que pertenece este servicio. |

### Imagen de Catálogo

Si quieres desplegar una imagen estándar disponible en PaaSify.

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-app-catalogo",
    "image": "nginx:latest",
    "mode": "default",
    "internal_port": 80,
    "project": 1,
    "subject": 1
  }'
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Token inválido o expirado.<br>
    <strong>400 Bad Request:</strong> <br>
    - Nombre de servicio ya existe.<br>
    - Campos obligatorios ausentes.<br>
    - JSON mal formado.<br>
    <strong>404 Not Found:</strong> Imagen no encontrada en el catálogo.<br>
    <strong>500 Internal Server Error:</strong> Fallo al intentar levantar el contenedor en Docker.
</div>
</details>

### DockerHub Personalizado

Desplegar cualquier imagen pública desde DockerHub.

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-app-externa",
    "image": "python:3.9-slim",
    "mode": "dockerhub",
    "internal_port": 5000,
    "environment": { "ENV": "production" },
    "project": 1,
    "subject": 1
  }'
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado.<br>
    <strong>400 Bad Request:</strong> Parámetros inválidos o nombre duplicado.<br>
    <strong>404 Not Found:</strong> La imagen especificada no existe en DockerHub.<br>
    <strong>500 Internal Server Error:</strong> Error del sistema al contactar con DockerHub o Docker Daemon.
</div>
</details>

### Código Personalizado (ZIP)

Permite subir tu propio código y definir cómo se construye o despliega mediante un archivo de configuración.

**Endpoint:** `POST /api/containers/`

| Campo          | Tipo   | Obligatorio | Descripción                                                     |
| :------------- | :----- | :---------- | :-------------------------------------------------------------- |
| **mode**       | string | **Sí**      | `custom`                                                        |
| **name**       | string | **Sí**      | Nombre único para el servicio.                                  |
| **code**       | file   | **Sí**      | Archivo `.zip` o `.rar` con el código fuente.                   |
| **dockerfile** | file   | No\*        | Archivo `Dockerfile` para construir la imagen.                  |
| **compose**    | file   | No\*        | Archivo `docker-compose.yml` para despliegues multi-contenedor. |
| **project**    | int    | **Sí**      | ID del proyecto al que se asocia este despliegue.               |
| **subject**    | int    | **Sí**      | ID de la asignatura a la que pertenece este servicio.           |

_\*Se requiere exactamente uno de los dos: `dockerfile` o `compose`._

```bash
# Ejemplo usando Dockerfile y código fuente (multipart/form-data)
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>" \
  -F "name=mi-app-custom" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado.<br>
    <strong>400 Bad Request:</strong> <br>
    - Falta el archivo de código fuente.<br>
    - No se ha proporcionado ni Dockerfile ni Compose.<br>
    - El archivo Compose contiene configuraciones no permitidas (bind mounts).<br>
    <strong>500 Internal Server Error:</strong> Error al procesar los archivos o al iniciar el despliegue.
</div>
</details>

### Escenarios Avanzados

PaaSify soporta despliegues complejos que incluyen múltiples servicios, bases de datos y configuraciones de seguridad recomendadas.

#### Multi-contenedor (Docker Compose)

Puedes desplegar una arquitectura completa (ej: Web + Base de Datos) subiendo un archivo `docker-compose.yml`.

```bash
# Despliegue de una App Flask + Base de Datos Postgres
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>" \
  -F "name=mi-web-db" \
  -F "mode=custom" \
  -F "code=@proyecto_completo.zip" \
  -F "compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

> **Buenas Prácticas Incluidas**:
>
> - **Persistencia**: Uso de volúmenes nombrados para la base de datos.
> - **Orquestación**: Uso de `depends_on` con `condition: service_healthy`.
> - **Seguridad**: Los contenedores deben correr como usuarios no root (appuser).

#### Healthchecks y Robustez

Se recomienda incluir instrucciones `HEALTHCHECK` tanto en tu `Dockerfile` como en tu `docker-compose.yml`. PaaSify utiliza estos checks para monitorizar el estado real de tu aplicación y gestionar reinicios automáticos si el servicio deja de responder.

```dockerfile
# Ejemplo de Healthcheck en Dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
```

---
