# 🐳 Listar mis Servicios

Recupera la lista completa de todos los contenedores y servicios que tienes desplegados en PaaSify.

**Endpoint:** `GET /api/containers/`

---

#### 📝 Ejemplo de consulta CURL:

```bash
# Obtener todos tus servicios activos
CURL -X GET "{{ PAASIFY_API_URL }}/containers/" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

---

#### ⚙️ Filtrado de Servicios (Queries)

Acepta los siguientes parámetros opcionales para acotar el listado:

| Parámetro | Tipo | Descripción                                      |
| :-------- | :--- | :----------------------------------------------- |
| `project` | int  | Ver solo servicios de un proyecto específico.    |
| `subject` | int  | Ver solo servicios de una asignatura específica. |

#### 📝 Ejemplo CURL con filtro:

```bash
# Ver servicios solo del proyecto 5
CURL -X GET "{{ PAASIFY_API_URL }}/containers/?project=5" \
  -H "Authorization: Bearer <TU_TOKEN>"
```

#### 🐳 Propiedades Principales de Respuesta:

- `id`: Identificador del servidor (para usar en PATCH o DELETE).
- `status`: Estado actual: `running`, `creating`, `stopped`, `error`.
- `assigned_port`: Puerto externo desde el que puedes acceder a tu app (ej: 40123).
- `internal_port`: Puerto interno donde escucha tu app (ej: 3000).
- `is_web`: Indica si la app tiene visibilidad externa.
