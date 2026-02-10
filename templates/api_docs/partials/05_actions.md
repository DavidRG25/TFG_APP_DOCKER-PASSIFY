# Acciones del Servicio

Endpoints específicos para controlar el ciclo de vida de tus contenedores.

---

### Iniciar Servicio

Arranca un servicio que está detenido o en error.

**Endpoint:** `POST /api/containers/{id}/start/`

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/start/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> No autenticado.<br>
    <strong>403 Forbidden:</strong> No eres el propietario de este servicio.<br>
    <strong>404 Not Found:</strong> El ID del servicio no existe.<br>
    <strong>400 Bad Request:</strong> El contenedor ya está iniciado o en un estado no válido.<br>
    <strong>500 Internal Server Error:</strong> Error al intentar ejecutar el comando de inicio en Docker.
</div>
</details>

---

### Detener Servicio

Detiene el contenedor pero conserva su configuración (estado `stopped`).

**Endpoint:** `POST /api/containers/{id}/stop/`

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/stop/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Token inválido.<br>
    <strong>403 Forbidden:</strong> Acceso denegado al recurso.<br>
    <strong>404 Not Found:</strong> Servicio no encontrado.<br>
    <strong>400 Bad Request:</strong> El contenedor ya está detenido.<br>
    <strong>500 Internal Server Error:</strong> Fallo al detener el proceso.
</div>
</details>

---

### Eliminar Servicio

Elimina permanentemente el servicio de la plataforma.

**Endpoint:** `POST /api/containers/{id}/remove/`

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/remove/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> Token inválido.<br>
    <strong>403 Forbidden:</strong> No puedes eliminar un servicio que no te pertenece.<br>
    <strong>404 Not Found:</strong> Servicio ya eliminado o inexistente.<br>
    <strong>500 Internal Server Error:</strong> Error al limpiar los recursos.
</div>
</details>

---
