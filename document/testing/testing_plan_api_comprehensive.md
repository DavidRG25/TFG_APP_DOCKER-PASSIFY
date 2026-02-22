# Plan de Testing Maestro: Verificación Total de la API REST

Este documento es una lista de verificación exhaustiva para validar cada endpoint, parámetro y caso de error de la API de PaaSify, incluyendo comandos `curl` detallados para su rápida ejecución.

_Nota:_ Asegúrate de sustituir `{{API_URL}}` por la URL real de la API (ej. `http://localhost:8000/api`) y `{{TOKEN}}` por un token JWT válido.

---

## 🔑 1. Autenticación y Seguridad

- [ ] **Sin Token**:

  ```bash
  curl -i -X GET {{API_URL}}/containers/
  # Esperado: 401 Unauthorized
  ```

- [ ] **Token Mal Formado**:

  ```bash
  curl -i -X GET {{API_URL}}/containers/ \
       -H "Authorization: Bearer 12345invalid"
  # Esperado: 401 Unauthorized
  ```

- [ ] **Obtener Token**:

  ```bash
  curl -i -X POST {{API_URL}}/token/ \
       -H "Content-Type: application/json" \
       -d '{"username": "admin", "password": "password123"}'
  # Esperado: 200 OK con 'access' y 'refresh'
  ```

- [ ] **Refrescar Token**:
  ```bash
  curl -i -X POST {{API_URL}}/token/refresh/ \
       -H "Content-Type: application/json" \
       -d '{"refresh": "TU_REFRESH_TOKEN"}'
  # Esperado: 200 OK con nuevo token 'access'
  ```

---

## 🔍 2. Consultas (GET) - Cobertura Total

### 2.1 Recursos Base

- [ ] **Listar Asignaturas**:

  ```bash
  curl -X GET {{API_URL}}/subjects/ \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Listar Proyectos**:

  ```bash
  curl -X GET {{API_URL}}/projects/ \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Listar Imágenes del Catálogo**:

  ```bash
  curl -X GET {{API_URL}}/images/ \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Detalle de Recurso (Asignatura)**:
  ```bash
  curl -X GET {{API_URL}}/subjects/1/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Verificar: nombres, categorías y relaciones correctas.
  ```

### 2.2 Servicios (Contenedores)

- [ ] **Listado Global**:

  ```bash
  curl -X GET {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Filtro por Proyecto**:

  ```bash
  curl -X GET "{{API_URL}}/containers/?project=1" \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Filtro por Asignatura**:

  ```bash
  curl -X GET "{{API_URL}}/containers/?subject=1" \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Búsqueda por Nombre**:

  ```bash
  curl -X GET "{{API_URL}}/containers/?search=mi-app" \
       -H "Authorization: Bearer {{TOKEN}}"
  ```

- [ ] **Detalle Completo**:
  ```bash
  curl -X GET {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Verificar: debe incluir 'assigned_port', 'status' y 'container_configs'.
  ```

---

## 🚀 3. Creación de Servicios (POST) - Todos los Modos

### 3.1 Modo Catálogo (Éxito y Error)

- [ ] **Éxito (DockerHub Oficial)**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "mysql-db", "mode": "dockerhub", "image": "mysql:8", "project": 1, "subject": 1, "env_vars": {"MYSQL_ROOT_PASSWORD": "root"}}'
  # Esperado: 201 Created
  ```

- [ ] **Error Nombre (Espacios o Mayúsculas)**:
  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "Mi App", "mode": "dockerhub", "image": "nginx", "project": 1, "subject": 1}'
  # Esperado: 400 Bad Request
  ```

### 3.2 Modo DockerHub

- [ ] **Éxito con Puerto y Entorno**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "api-python", "mode": "dockerhub", "image": "python:3.9", "project": 1, "subject": 1, "internal_port": 8000, "is_web": true}'
  # Esperado: 201 Created
  ```

- [ ] **Error Imagen Inexistente**:
  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "fake-app", "mode": "dockerhub", "image": "esto-no-existe-en-dockerhub:latest", "project": 1, "subject": 1}'
  # Esperado: Puede requerir validación asíncrona o devolver error dependiendo de la implementación.
  ```

### 3.3 Modo Custom (Código Propio mediante multipart/form-data)

- [ ] **Dockerfile**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -F "name=mi-web" \
       -F "mode=custom" \
       -F "project=1" \
       -F "subject=1" \
       -F "internal_port=3000" \
       -F "code=@path/to/codigo.zip" \
       -F "dockerfile=@path/to/Dockerfile"
  # Esperado: 201 Created, inicializa build.
  ```

- [ ] **Docker Compose con Configuración**:
  ```bash
  curl -i -X POST {{API_URL}}/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -F "name=mi-stack" \
       -F "mode=custom" \
       -F "project=1" \
       -F "subject=1" \
       -F "code=@path/to/stack.zip" \
       -F "compose=@path/to/docker-compose.yml" \
       -F "container_configs={\"frontend\":{\"is_web\":true,\"container_type\":\"web\"}}"
  # Esperado: 201 Created
  ```

---

## 🛠️ 4. Modificación (PATCH) - Casuística Completa

### 4.1 Modificaciones Permitidas

- [ ] **Cambio de Imagen (DockerHub)**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"image": "nginx:latest"}'
  # Esperado: 200 OK y actualización de la imagen del contenedor.
  ```

- [ ] **Actualización con Retención de Volúmenes (keep_volumes=True)**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"keep_volumes": true, "env_vars": {"NEW": "VAL"}}'
  # Esperado: 200 OK. El contenedor se recrea pero los datos del volumen persisten.
  ```

- [ ] **Actualización con Eliminación de Volúmenes (keep_volumes=False)**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"keep_volumes": false, "env_vars": {"NEW": "VAL"}}'
  # Esperado: 200 OK. El contenedor se recrea desde cero y se pierden los datos anteriores.
  ```

- [ ] **Cambio de Nombre y Tipo**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "nuevo-nombre", "container_type": "database", "is_web": false}'
  # Esperado: 200 OK
  ```

- [ ] **Cambio de Entorno (Reemplazo de Variables)**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"env_vars": {"NEW_KEY": "NEW_VAL", "DEBUG": "True"}}'
  # Esperado: 200 OK y reinicio/recreación de contenedor si aplica.
  ```

- [ ] **Actualización de Código/Archivos (Custom)**:
  ```bash
  curl -i -X PATCH {{API_URL}}/containers/2/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -F "compose=@path/to/new-docker-compose.yml" \
       -F "code=@path/to/new-code.zip"
  # Esperado: Purgado de volumen antiguo, reconstrucción y 200 OK.
  ```

### 4.2 Restricciones (Validación de Seguridad)

- [ ] **Editar Catálogo (Default)**:

  ```bash
  # Supongamos que el ID 3 es un servicio auto-gestionado de catálogo restringido
  curl -i -X PATCH {{API_URL}}/containers/3/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "hacked-name"}'
  # Esperado: 403 Forbidden o mensaje explicativo.
  ```

- [ ] **Cambiar Modo Indebidamente**:

  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"mode": "custom"}'
  # Esperado: 400 Bad Request
  ```

- [ ] **Cambiar Proyecto/Asignatura**:
  ```bash
  curl -i -X PATCH {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"project": 99}'
  # Esperado: 400 Bad Request
  ```

---

## ⚙️ 5. Acciones de Control de Estado

- [ ] **Detener Servicio**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/1/stop/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Esperado: 200 OK
  ```

- [ ] **Iniciar Servicio**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/1/start/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Esperado: 200 OK
  ```

- [ ] **Reiniciar Servicio**:

  ```bash
  curl -i -X POST {{API_URL}}/containers/1/restart/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Esperado: 200 OK
  ```

- [ ] **Consultar Logs**:

  ```bash
  curl -s -X GET {{API_URL}}/containers/1/logs/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Esperado: 200 OK con texto plano o JSON de logs.
  ```

- [ ] **Eliminación Permanente (DELETE)**:
  ```bash
  curl -i -X DELETE {{API_URL}}/containers/1/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Esperado: 204 No Content
  ```

---

**Firmado:** PaaSify Master QA  
**Última Actualización:** 2026-02-21
