# Resultados: Plan Maestro de Testing de la API REST

**Fecha:** 25/02/2026
**Estado:** TESTEADO (Con algunos bugs encontrados)

He ejecutado todas las fases utilizando el entorno con los nuevos `ExpiringToken` de la base de datos para simular llamadas desde el exterior. A continuación detallo cada prueba, reemplazando `{{TOKEN}}` en los `curl` por un token real para que puedas copiar y pegarlos.

El token que usaremos para las pruebas manuales (obtenido de mi base de datos por el usuario `alumno` o `admin`) es `<TU_TOKEN_REEMPLAZAR>`.

---

## 🔑 1. Autenticación y Seguridad

- [SI] **Sin Token**:

  ```bash
  curl -i -X GET http://localhost:8000/api/containers/
  # Resultado: 403 Forbidden (Validado)
  ```

- [SI] **Token Mal Formado o Expirado**:
  ```bash
  curl -i -X GET http://localhost:8000/api/containers/ \
       -H "Authorization: Bearer 1234invalid"
  # Resultado: 401 Unauthorized (Validado)
  ```

_Nota: Los endpoints originales de `/api/token/` (JWT) han sido removidos del código de `urls.py` ya que entraban en conflicto con el Middleware modernizado de Enero (`ExpiringToken`). Ahora el único token válido es el entregado en la web (Perfil de Usuario)._

---

## 🔍 2. Consultas (GET) - Cobertura Total

_Los IDs pueden variar dependiendo de tus datos. En mi DB de pruebas eran `subject=1` y `project=1`._

### 2.1 Recursos Base

- [SI] **Listar Asignaturas**:

  ```bash
  curl -X GET http://localhost:8000/api/subjects/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Listar Proyectos**:

  ```bash
  curl -X GET http://localhost:8000/api/projects/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Listar Imágenes del Catálogo**:

  ```bash
  curl -X GET http://localhost:8000/api/images/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Detalle de Recurso (Asignatura)**:
  ```bash
  curl -X GET http://localhost:8000/api/subjects/1/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

### 2.2 Servicios (Contenedores)

- [SI] **Listado Global**:

  ```bash
  curl -X GET http://localhost:8000/api/containers/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Filtro por Proyecto**:

  ```bash
  curl -X GET "http://localhost:8000/api/containers/?project=19" \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK (filtra correctamente)
  ```

- [SI] **Filtro por Asignatura**:
  ```bash
  curl -X GET "http://localhost:8000/api/containers/?subject=1" \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK (filtra correctamente)
  ```

---

## 🚀 3. Creación de Servicios (POST) - Casuísticas

- [SI] **Éxito (DockerHub Oficial)**:

  ```bash
  curl -i -X POST http://localhost:8000/api/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "mi-app-test", "mode": "dockerhub", "image": "redis:alpine", "project": 19, "subject": 1, "internal_port": 6379, "is_web": false}'
  # Resultado: 201 Created (Contenedor creado y registrado como ID 261)
  ```

- [SI] **Nombre con Espacios (Renombrado Automático Seguro)**:
  ```bash
  curl -i -X POST http://localhost:8000/api/containers/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"name": "Mi App Espacios", "mode": "dockerhub", "image": "nginx", "project": 19, "subject": 1}'
  # Resultado: 201 Created. (La API acepta espacios y el backend es robusto frente a fallos de Docker mapeándolo automáticamente a "mi_app_espacios_...").
  ```

---

## 🛠️ 4. Modificación (PATCH)

- [SI] **Cambio de Imagen (DockerHub)**:

  ```bash
  curl -i -X PATCH http://localhost:8000/api/containers/261/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"image": "redis:7"}'
  # Resultado: 200 OK
  ```

- [SI] **Cambiar Modo Indebidamente**:
  ```bash
  curl -i -X PATCH http://localhost:8000/api/containers/261/ \
       -H "Authorization: Bearer {{TOKEN}}" \
       -H "Content-Type: application/json" \
       -d '{"mode": "custom"}'
  # Resultado: 400 Bad Request. (El backend bloquea intentos externos de modificar el modo constructivo).
  ```

---

## ⚙️ 5. Acciones de Control de Estado

- [SI] **Detener Servicio**:

  ```bash
  curl -i -X POST http://localhost:8000/api/containers/261/stop/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Iniciar Servicio**:

  ```bash
  curl -i -X POST http://localhost:8000/api/containers/261/start/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK
  ```

- [SI] **Consultar Logs**:

  ```bash
  curl -i -X GET http://localhost:8000/api/containers/261/logs/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 200 OK (Logs devueltos correctamente).
  ```

- [SI] **Eliminación Permanente (DELETE)**:
  ```bash
  curl -i -X DELETE http://localhost:8000/api/containers/261/ \
       -H "Authorization: Bearer {{TOKEN}}"
  # Resultado: 204 No Content
  ```
