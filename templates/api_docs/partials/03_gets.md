# Consultas (GET)

Endpoints para obtener información sobre tus recursos en PaaSify de forma clara y concisa.

---

### Proyectos

#### 1. Listar todos mis proyectos

Recupera la lista de proyectos que tienes asignados.

**Endpoint:** `GET /api/projects/`

**Ejemplo de respuesta:**

```json
[
  {
    "id": 5,
    "name": "Proyecto Final Docker",
    "subject": 1,
    "subject_name": "Asignatura1",
    "date": "2026-06-15"
  }
]
```

```bash
curl -X GET "{{ PAASIFY_API_URL }}/projects/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

#### 2. Listar servicios de un proyecto específico

Filtra tus despliegues para ver solo los servicios asociados a un proyecto concreto.

**Endpoint:** `GET /api/containers/?project={id}`

---

### Asignaturas

#### 1. Listar todas mis asignaturas

Muestra las asignaturas en las que estás matriculado.

**Endpoint:** `GET /api/subjects/`

**Ejemplo de respuesta:**

```json
[
  {
    "id": 1,
    "name": "Asignatura1",
    "category": "Asignatura obligatorias",
    "year": "2026"
  }
]
```

#### 2. Listar servicios de una asignatura específica

Filtra tus despliegues para ver solo los servicios asociados a una asignatura.

**Endpoint:** `GET /api/containers/?subject={id}`

---

### Servicios

#### 1. Listar todos mis servicios

Recupera la lista completa de todos tus servicios activos y sus estados. No incluye logs ni detalles pesados.

**Endpoint:** `GET /api/containers/`

#### 2. Consultar información de un servicio

Obtén toda la información técnica y de red de un único servicio.

> 💡 **Nota**: Este endpoint devuelve la configuración e información de estado. Para ver la salida de consola (logs), usa el endpoint específico de Logs en la sección de [Acciones](#logs).

**Endpoint:** `GET /api/containers/{id}/`

```bash
curl -X GET "{{ PAASIFY_API_URL }}/containers/{id}/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

---

### Códigos de Respuesta Comunes

<details class="api-errors">
<summary>Posibles errores en consultas GET</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado. Token faltante o inválido.<br>
    <strong>500 Internal Server Error:</strong> Error interno del servidor.
</div>
</details>
