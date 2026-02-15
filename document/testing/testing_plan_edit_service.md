# Plan de Testing: Edición de Servicios (UI y API)

Este documento detalla las pruebas necesarias para validar la funcionalidad de modificación de servicios en PaaSify, asegurando que las restricciones por modo y la reconstrucción de contenedores funcionen correctamente.

## 1. Pruebas de Interfaz de Usuario (UI)

### 1.1 Restricción de acceso

**Caso**: Intentar editar un servicio del catálogo oficial.

- [ ] El sistema debe denegar el acceso con un mensaje explicativo (HTTP 403) indicando que los servicios oficiales no son editables.

### 1.2 Modo DockerHub

**Caso**: Editar un servicio desplegado desde DockerHub.

- [SI] Cambiar el puerto externo de "Auto" a un número específico (ej: 40123).
- [SI] Cambiar el puerto interno de 80 a 8080.
- [SI] Añadir una variable de entorno en el JSON: `{"TEST": "RELOAD"}`.
- [SI] **Resultado**: El contenedor se detiene y se recrea. La tabla de servicios muestra el nuevo puerto externo.
- [SI] **Verificación**: Al entrar al terminal (`/sh`), `env | grep TEST` muestra `RELOAD`.

### 1.3 Modo Personalizado (Dockerfile)

**Caso**: Editar un servicio con Dockerfile propio.

- [ ] Cambiar el tipo de "Database" a "Web" y activar el switch "¿Es una web accesible?".
- [ ] Subir un nuevo archivo `Dockerfile` (ej: cambiando la imagen base de alpine a debian) sin usar filtros de extensión en el explorador de archivos.
- [ ] Subir un nuevo `.zip` de código.
- [ ] **Resultado**: El sistema purga los archivos antiguos del workspace.
- [ ] **Resultado**: El contenedor se reconstruye (build) con el nuevo Dockerfile.
- [ ] **Resultado**: La URL del host es accesible si el servicio es tipo web.

### 1.4 Modo Personalizado (Docker Compose)

**Caso**: Editar un stack multi-contenedor.

- [ ] En la tabla de gestión de contenedores, cambiar un servicio de tipo "Misc" a "API".
- [ ] Subir un nuevo `docker-compose.yml` que añada un tercer servicio (ej: un `redis`).
- [ ] **Resultado**: El JSON `container_configs` se actualiza automáticamente.
- [ ] **Resultado**: Tras guardar, aparecen los 3 contenedores en la tabla principal.
- [ ] **Resultado**: Los campos de tipo y web de cada contenedor reflejan lo configurado en la tabla de edición.

---

## 2. Pruebas de API (Terminal)

### 2.1 Actualización parcial (PATCH)

**Comando**:

```bash
curl -X PATCH {{API_URL}}/containers/{id}/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "is_web=true" \
  -F "container_type=web"
```

- [ ] Respuesta 200 OK.
- [ ] El servicio pasa a estado `restarting` y luego `running`.

### 2.2 Reemplazo de archivos

**Comando**:

```bash
curl -X PATCH {{API_URL}}/containers/{id}/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "dockerfile=@Update.Dockerfile" \
  -F "code=@NewCode.zip"
```

- [ ] El logs del servicio muestra el proceso de build nuevamente.

---

## 3. Verificación de Integridad de Datos

- [ ] **Persistencia**: Verificar que tras la edición, los campos `internal_port`, `env_vars` y `container_configs` se mantienen correctamente en la base de datos tras futuros reinicios.
- [ ] **Limpieza (Purga)**: Verificar manualmente en el sistema de archivos del servidor que la carpeta `media/services/{id}` solo contiene los archivos nuevos y no restos de los anteriores tras una subida de archivos.

---

**Firmado:** PaaSify AI QA Team
**Fecha:** 2026-02-15
