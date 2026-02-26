# 📂 Listar Proyectos

Recupera la lista de proyectos que tienes asignados como alumno.

**Endpoint:** `GET /api/projects/`

---

#### 📝 Ejemplo de consulta CURL:

```bash
# La URL de PaaSify en este entorno es: {{ PAASIFY_API_URL }}
CURL -X GET "{{ PAASIFY_API_URL }}/projects/" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

---

### Propiedades del Recurso

| Campo            | Tipo   | Descripción                               |
| :--------------- | :----- | :---------------------------------------- |
| **id**           | int    | Identificador único del proyecto.         |
| **name**         | string | Nombre del proyecto académico.            |
| **subject_name** | string | Nombre legible de la asignatura asociada. |

#### 📝 Ejemplo de respuesta (JSON):

```json
[
  {
    "id": 5,
    "name": "Proyecto Final de Grado",
    "subject": 1,
    "subject_name": "Ingeniería del Software",
    "end_date": "2026-06-15"
  }
]
```

#### ✅ Integración:

Necesitarás el campo `id` de esta respuesta para filtrar tus contenedores o crear nuevos dentro de este proyecto.
