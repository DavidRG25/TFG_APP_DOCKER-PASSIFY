# Plan de Testing: Edición de Servicios (UI y API)

Este documento detalla las pruebas necesarias para validar la funcionalidad de modificación de servicios en PaaSify, asegurando que las restricciones por modo y la reconstrucción de contenedores funcionen correctamente.

## 1. Pruebas de Interfaz de Usuario (UI)

### 1.1 Restricción de acceso

- **Caso**: Intentar editar un servicio del catálogo oficial.
- **Resultado esperado**: El sistema debe denegar el acceso con un mensaje explicativo (HTTP 403) indicando que los servicios oficiales no son editables.

### 1.2 Modo DockerHub

- **Caso**: Editar un servicio desplegado desde DockerHub.
- **Acciones**:
  1.  Cambiar el puerto externo de "Auto" a un número específico (ej: 40123).
  2.  Cambiar el puerto interno de 80 a 8080.
  3.  Añadir una variable de entorno en el JSON: `{"TEST": "RELOAD"}`.
- **Resultado esperado**: El contenedor se detiene y se recrea. La tabla de servicios debe mostrar el nuevo puerto externo. Al entrar al terminal (`/sh`), `env | grep TEST` debe mostrar `RELOAD`.

### 1.3 Modo Personalizado (Dockerfile)

- **Caso**: Editar un servicio con Dockerfile propio.
- **Acciones**:
  1.  Cambiar el tipo de "Database" a "Web" y activar el switch "¿Es una web accesible?".
  2.  Subir un nuevo archivo `Dockerfile` (ej: cambiando la imagen base de alpine a debian).
  3.  Subir un nuevo `.zip` de código.
- **Resultado esperado**: El sistema debe purgar los archivos antiguos del workspace. El contenedor debe reconstruirse (build) con el nuevo Dockerfile. La URL del host ahora debe ser accesible si el servicio es tipo web.

### 1.4 Modo Personalizado (Docker Compose)

- **Caso**: Editar un stack multi-contenedor.
- **Acciones**:
  1.  En la tabla de gestión de contenedores, cambiar un servicio de tipo "Misc" a "API".
  2.  Subir un nuevo `docker-compose.yml` que añada un tercer servicio (ej: un `redis`).
- **Resultado esperado**:
  1.  El JSON `container_configs` debe actualizarse automáticamente.
  2.  Tras guardar, deben aparecer los 3 contenedores en la tabla principal.
  3.  Los campos de tipo y web de cada contenedor deben reflejar lo configurado en la tabla de edición.

---

## 2. Pruebas de API (Terminal)

### 2.1 Actualización parcial (PATCH)

- **Comando**:
  ```bash
  curl -X PATCH {{API_URL}}/containers/{id}/ \
    -H "Authorization: Bearer <TOKEN>" \
    -F "is_web=true" \
    -F "container_type=web"
  ```
- **Resultado esperado**: Respuesta 200 OK. El servicio debe pasar a estado `restarting` y luego `running`.

### 2.2 Reemplazo de archivos

- **Comando**:
  ```bash
  curl -X PATCH {{API_URL}}/containers/{id}/ \
    -H "Authorization: Bearer <TOKEN>" \
    -F "dockerfile=@Update.Dockerfile" \
    -F "code=@NewCode.zip"
  ```
- **Resultado esperado**: El logs del servicio debe mostrar el proceso de build nuevamente.

---

## 3. Verificación de Integridad de Datos

- **Persistencia**: Verificar que tras la edición, los campos `internal_port`, `env_vars` y `container_configs` se mantienen correctamente en la base de datos tras futuros reinicios.
- **Limpieza (Purga)**: Verificar manualmente en el sistema de archivos del servidor que la carpeta `media/workspaces/{id}` solo contiene los archivos nuevos y no restos de los anteriores tras una subida de archivos.

---

**Firmado:** PaaSify AI QA Team
**Fecha:** {% now "Y-m-d" %}
