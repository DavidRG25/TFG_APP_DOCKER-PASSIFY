# 🔍 Consultas (GET)

Endpoints para obtener información sobre tus recursos en PaaSify de forma clara y concisa.

---

## 📂 Proyectos

### 1. Listar todos mis proyectos

Recupera la lista de proyectos que tienes asignados.

**Endpoint:** `GET /api/projects/`

#### 📝 Ejemplo de respuesta:

```json
[
  {
    "id": 5,
    "name": "Proyecto Final Docker",
    "subject": 1,
    "subject_name": "Asignatura1",
    "end_date": "2026-06-15"
  }
]
```

#### 💻 Ejemplo cURL:

```bash
curl -X GET "{{ PAASIFY_API_URL }}/projects/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

### 2. Listar servicios de un proyecto específico

Filtra tus despliegues para ver solo los servicios asociados a un proyecto concreto.

**Endpoint:** `GET /api/containers/?project={id}`

---

## 📚 Asignaturas

### 1. Listar todas mis asignaturas

Muestra las asignaturas en las que estás matriculado.

**Endpoint:** `GET /api/subjects/`

#### 📝 Ejemplo de respuesta:

```json
[
  {
    "id": 1,
    "name": "Despliegue de Aplicaciones Web",
    "category": "Obligatoria",
    "year": "2026"
  }
]
```

### 2. Listar servicios de una asignatura específica

Filtra tus despliegues para ver solo los servicios asociados a una asignatura.

**Endpoint:** `GET /api/containers/?subject={id}`

---

## 🐳 Servicios (Contenedores)

### 1. Listar todos mis servicios

Recupera la lista completa de todos tus servicios activos y sus estados.

**Endpoint:** `GET /api/containers/`

### 2. Consultar información detallada de un servicio

Obtén toda la información técnica, de red y de estado de un único servicio.

**Endpoint:** `GET /api/containers/{id}/`

#### 💻 Ejemplo cURL:

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

#### 📝 Ejemplo de respuesta detallada:

```json
{
  "id": 123,
  "name": "mi-app-react",
  "image": "node:18-alpine",
  "status": "running",
  "internal_port": 3000,
  "assigned_port": 40123,
  "container_type": "web",
  "is_web": true,
  "env_vars": {
    "NODE_ENV": "production"
  },
  "created_at": "2026-02-15T10:00:00Z"
}
```

> 💡 **Nota:** Este endpoint devuelve la configuración y estado. Para ver la salida de consola (logs), usa el endpoint específico de [Logs](#logs).

---

## 📬 Códigos de Respuesta Comunes

<details class="api-errors">
<summary>ℹ️ Posibles respuestas en consultas GET</summary>
<div class="api-error-content">
    <strong>200 OK:</strong> ✅ Consulta exitosa. Se devuelve el recurso o listado solicitado.<br>
    <strong>400 Bad Request:</strong> ❌ Parámetros de filtrado incorrectos (ej: ID no numérico).<br>
    <strong>401 Unauthorized:</strong> 🔒 Permiso denegado. Token faltante o inválido.<br>
    <strong>403 Forbidden:</strong> 🚫 Intentas acceder a recursos que no te pertenecen.<br>
    <strong>404 Not Found:</strong> 🔍 El recurso específico no existe.<br>
    <strong>500 Internal Server Error:</strong> 💥 Error interno del servidor.
</div>
</details>

---
