# Plan de Testing Maestro: Verificación Total de la API REST

Este documento es una lista de verificación exhaustiva para validar cada endpoint, parámetro y caso de error de la API de PaaSify.

---

## 🔑 1. Autenticación y Seguridad

- [ ] **Sin Token**: `curl -I {{API_URL}}/containers/` -> Esperado: `401 Unauthorized`.
- [ ] **Token Mal Formado**: `Authorization: Bearer 12345` -> Esperado: `401 Unauthorized`.
- [ ] **Obtener Token**: `POST {{API_URL}}/token/` con credenciales válidas.
- [ ] **Refrescar Token**: `POST {{API_URL}}/token/refresh/` con un refresh token válido.

---

## 🔍 2. Consultas (GET) - Cobertura Total

### 2.1 Recursos Base

- [ ] **Listar Asignaturas**: `GET {{API_URL}}/subjects/`
- [ ] **Listar Proyectos**: `GET {{API_URL}}/projects/`
- [ ] **Listar Imágenes del Catálogo**: `GET {{API_URL}}/images/`
- [ ] **Detalle de Recurso**: `GET {{API_URL}}/subjects/{{ID}}/` (Verificar nombres y categorías).

### 2.2 Servicios (Contenedores)

- [ ] **Listado Global**: `GET {{API_URL}}/containers/`
- [ ] **Filtro por Proyecto**: `GET {{API_URL}}/containers/?project={{ID}}`
- [ ] **Filtro por Asignatura**: `GET {{API_URL}}/containers/?subject={{ID}}`
- [ ] **Búsqueda por Nombre**: `GET {{API_URL}}/containers/?search=mi-app`
- [ ] **Detalle Completo**: `GET {{API_URL}}/containers/{{ID}}/` (Verificar que incluye `assigned_port`, `status` y `container_configs`).

---

## 🚀 3. Creación de Servicios (POST) - Todos los Modos

### 3.1 Modo Catálogo (Éxito y Error)

- [ ] **Éxito**: Crear con imagen válida del catálogo.
- [ ] **Error Imagen**: Intentar crear con imagen no permitida -> Esperado: `400 Bad Request`.
- [ ] **Error Nombre**: Nombre con espacios o mayúsculas -> Esperado: `400 Bad Request`.

### 3.2 Modo DockerHub

- [ ] **Éxito Simple**: `{"name": "h-py", "mode": "dockerhub", "image": "python:3.9", "project": 1, "subject": 1}`
- [ ] **Éxito con Puerto**: Definir `internal_port: 8080`.
- [ ] **Error Imagen Inexistente**: Poner una imagen que no existe en DockerHub.

### 3.3 Modo Custom (Código Propio)

- [ ] **Dockerfile**: Enviar `code` (.zip) y `dockerfile`.
- [ ] **Docker Compose**: Enviar `code` (.zip) y `compose` (.yml).
- [ ] **Compose con Configuración**: Enviar `container_configs` como string JSON en el mismo POST.

---

## 🛠️ 4. Modificación (PATCH) - Casuística Completa

### 4.1 Modificaciones Permitidas (DockerHub/Custom)

- [ ] **Cambio de Nombre**: `PATCH {"name": "nuevo-nombre"}`
- [ ] **Cambio de Metadatos**: `PATCH {"container_type": "database", "is_web": false}`
- [ ] **Cambio de Red**: `PATCH {"internal_port": 3000}` (Solo DockerHub/Dockerfile).
- [ ] **Cambio de Entorno**: `PATCH {"env_vars": {"KEY": "VAL"}}`
- [ ] **Reemplazo de Archivos**: Enviar nuevo `code` (.zip) o `compose` (.yml).

### 4.2 Restricciones (Lo que NO debe permitir)

- [ ] **Editar Catálogo**: `PATCH` sobre servicio `default` -> Esperado: `403 Forbidden`.
- [ ] **Cambiar Modo**: `PATCH {"mode": "custom"}` sobre un servicio DockerHub -> Esperado: `400 Bad Request`.
- [ ] **Cambiar Imagen (DockerHub)**: `PATCH {"image": "nginx"}` sobre DockerHub -> Esperado: `400 Bad Request`.
- [ ] **Cambiar Proyecto/Asignatura**: Intentar mover un servicio de proyecto -> Esperado: `400 Bad Request`.

---

## ⚙️ 5. Acciones y Control (Acciones Especiales)

- [ ] **Detener**: `POST {{API_URL}}/containers/{{ID}}/stop/`
- [ ] **Iniciar**: `POST {{API_URL}}/containers/{{ID}}/start/`
- [ ] **Reiniciar**: `POST {{API_URL}}/containers/{{ID}}/restart/`
- [ ] **Logs (Texto)**: `GET {{API_URL}}/containers/{{ID}}/logs/`
- [ ] **Eliminar**: `DELETE {{API_URL}}/containers/{{ID}}/` (Verificar que devuelve `204 No Content`).

---

## 📋 6. Matriz de Comandos de Prueba (Cheat Sheet)

| Caso          | Método  | Endpoint                          | Payload sugerido                                                              |
| :------------ | :------ | :-------------------------------- | :---------------------------------------------------------------------------- |
| Login         | `POST`  | `/api/token/`                     | `{"username": "...", "password": "..."}`                                      |
| Listar Todo   | `GET`   | `/api/containers/`                | -                                                                             |
| Crear Hub     | `POST`  | `/api/containers/`                | `{"name":"test","mode":"dockerhub","image":"alpine","project":1,"subject":1}` |
| Editar Web    | `PATCH` | `/api/containers/{{ID}}/`         | `{"is_web": true, "container_type": "web"}`                                   |
| Editar Env    | `PATCH` | `/api/containers/{{ID}}/`         | `{"env_vars": {"FOO": "BAR"}}`                                                |
| Subir Compose | `PATCH` | `/api/containers/{{ID}}/`         | `-F "compose=@docker-compose.yml" -F "code=@src.zip"`                         |
| Restart       | `POST`  | `/api/containers/{{ID}}/restart/` | -                                                                             |
| Ver Logs      | `GET`   | `/api/containers/{{ID}}/logs/`    | -                                                                             |

---

**Firmado:** PaaSify Master QA
**Última Actualización:** 2026-02-18
