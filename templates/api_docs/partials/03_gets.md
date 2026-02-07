# Consultas (GET)

## Consultas (GET)

Endpoints para obtener información sobre tus recursos en PaaSify.

### Listar Servicios

Recupera la lista detallada de todos tus servicios activos y sus estados actuales.

**Endpoint:** `GET /containers/`

```bash
curl -X GET {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Permiso denegado. Token faltante o inválido.<br>
    <strong>500 Internal Server Error:</strong> Error interno del servidor al consultar la base de datos o Docker.
</div>
</details>

### Listar Asignaturas

Muestra las asignaturas en las que estás matriculado. Necesitarás el `id` para asociarla a nuevos servicios.

**Endpoint:** `GET /subjects/`

```bash
curl -X GET {{ PAASIFY_API_URL }}/subjects/ \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Token inválido.<br>
    <strong>500 Internal Server Error:</strong> Error de conexión con el servicio de gestión académica.
</div>
</details>

### Listar Proyectos

Muestra los proyectos que tienes asignados. Útil para enlazar despliegues a entregas específicas.

**Endpoint:** `GET /projects/`

```bash
curl -X GET {{ PAASIFY_API_URL }}/projects/ \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Token inválido.<br>
    <strong>500 Internal Server Error:</strong> No se pudo recuperar la lista de proyectos.
</div>
</details>

---
