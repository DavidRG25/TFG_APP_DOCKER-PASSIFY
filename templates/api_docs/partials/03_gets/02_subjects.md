# 📚 Listar Asignaturas

Muestra las asignaturas en las que estás matriculado como alumno según tu perfil del Grado.

**Endpoint:** `GET /api/subjects/`

---

#### 📝 Ejemplo de consulta CURL:

```bash
# La URL de PaaSify en este entorno es: {{ PAASIFY_API_URL }}
CURL -X GET "{{ PAASIFY_API_URL }}/subjects/" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

---

### Propiedades del Recurso

| Campo        | Tipo   | Descripción                                           |
| :----------- | :----- | :---------------------------------------------------- |
| **id**       | int    | Identificador único de la asignatura.                 |
| **name**     | string | Nombre completo (ej: Despliegue de Aplicaciones Web). |
| **category** | string | Tipo: `Obligatoria`, `Optativa`, etc.                 |
| **year**     | int    | Año académico actual.                                 |

#### 📝 Ejemplo de respuesta (JSON):

```json
[
  {
    "id": 1,
    "name": "Despliegue de Aplicaciones Web",
    "category": "Obligatoria",
    "year": 2026
  }
]
```

#### ✅ Integración:

Al crear un servicio (`POST /api/containers/`), el campo `subject` es obligatorio y debe coincidir con un `id` de esta lista.
