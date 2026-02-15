# Modificar Servicio

Actualiza la configuración de un servicio existente mediante la API.

---

## Restricciones Importantes

⚠️ **Solo se pueden modificar servicios desplegados con:**

- **DockerHub** (`mode: "dockerhub"`)
- **Personalizado** (`mode: "custom"`)

❌ **NO se pueden modificar servicios del catálogo oficial** (`mode: "default"`). Si necesitas cambios en un servicio del catálogo, debes eliminarlo y crear uno nuevo.

---

## Endpoint de Modificación

**Método:** `PATCH /api/containers/{id}/`

Este endpoint permite actualizar campos específicos de un servicio sin necesidad de enviar todos los datos.

### Comportamiento del Sistema

Cuando modificas un servicio mediante PATCH:

1. ✅ **Se guardan los cambios** en la base de datos
2. 🔄 **Se procesa cualquier archivo nuevo** (Dockerfile, Compose, código ZIP)
3. 🗑️ **Se elimina el contenedor actual**
4. 🚀 **Se reconstruye y reinicia** el contenedor con la nueva configuración

> **Nota:** Este proceso es equivalente a editar el servicio desde la interfaz web.

---

## Diferencias por Modo de Despliegue

### 🐳 Modo DockerHub

En servicios desplegados desde DockerHub (`mode: "dockerhub"`):

#### ✅ Campos Modificables:

- `name` - Nombre del servicio
- `internal_port` - Puerto interno del contenedor
- `env_vars` - Variables de entorno (JSON)
- `container_type` - Tipo (`web`, `api`, `database`, `misc`)
- `is_web` - Visibilidad web (`true`/`false`)

#### ❌ Campos NO Modificables:

- `image` - **La imagen NO se puede cambiar** en modo DockerHub
  - Para cambiar la imagen, debes crear un nuevo servicio
- `dockerfile` - No aplica en este modo
- `compose` - No aplica en este modo
- `code` - No aplica en este modo

#### 📝 Ejemplo: Actualizar Puerto y Variables

```bash
curl -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "internal_port": 3000,
    "env_vars": {
      "NODE_ENV": "production",
      "API_KEY": "nueva-clave"
    }
  }'
```

---

### 🛠️ Modo Custom - Dockerfile

En servicios personalizados con Dockerfile (`mode: "custom"`, sin `compose`):

#### ✅ Campos Modificables:

- `name` - Nombre del servicio
- `internal_port` - Puerto interno
- `env_vars` - Variables de entorno (JSON)
- `container_type` - Tipo de servicio
- `is_web` - Visibilidad web
- `dockerfile` - **Reemplazar Dockerfile** (archivo)
- `code` - **Reemplazar código fuente** (.zip)

#### ❌ Campos NO Modificables:

- `image` - No aplica (se construye desde Dockerfile)
- `compose` - No aplica en este modo

#### 📝 Ejemplo: Actualizar Dockerfile y Código

```bash
curl -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -F "dockerfile=@/ruta/a/nuevo-Dockerfile" \
  -F "code=@/ruta/a/codigo-actualizado.zip" \
  -F "env_vars={\"DEBUG\":\"false\"}"
```

---

### 📦 Modo Custom - Docker Compose

En servicios personalizados con Docker Compose (`mode: "custom"`, con `compose`):

#### ✅ Campos Modificables:

- `name` - Nombre del servicio
- `env_vars` - Variables de entorno globales (JSON)
- `compose` - **Reemplazar docker-compose.yml** (archivo)
- `code` - **Reemplazar código fuente** (.zip)
- Configuración de contenedores individuales (tipo y visibilidad)

#### ❌ Campos NO Modificables:

- `image` - No aplica (se define en compose)
- `internal_port` - Se define en el compose
- `dockerfile` - No aplica en este modo

#### ⚠️ Consideraciones Especiales:

- Los puertos se gestionan automáticamente desde el `docker-compose.yml`
- Cada contenedor del stack puede tener su propio `container_type` e `is_web`
- Para cambiar puertos internos, edita el archivo `docker-compose.yml`

#### 📝 Ejemplo: Actualizar Compose y Código

```bash
curl -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -F "compose=@/ruta/a/docker-compose-v2.yml" \
  -F "code=@/ruta/a/proyecto-actualizado.zip"
```

---

## Tabla Comparativa de Campos Editables

| Campo            | DockerHub | Custom (Dockerfile) | Custom (Compose)  |
| ---------------- | --------- | ------------------- | ----------------- |
| `name`           | ✅        | ✅                  | ✅                |
| `image`          | ❌        | ❌                  | ❌                |
| `internal_port`  | ✅        | ✅                  | ❌ (en compose)   |
| `env_vars`       | ✅        | ✅                  | ✅                |
| `container_type` | ✅        | ✅                  | ✅ (por servicio) |
| `is_web`         | ✅        | ✅                  | ✅ (por servicio) |
| `dockerfile`     | ❌        | ✅                  | ❌                |
| `compose`        | ❌        | ❌                  | ✅                |
| `code`           | ❌        | ✅                  | ✅                |

---

## Campos Inmutables (Todos los Modos)

Estos campos **NUNCA** se pueden modificar después de crear el servicio:

- ❌ `owner` - El propietario no puede cambiar
- ❌ `mode` - El modo de despliegue es inmutable
- ❌ `subject` - La asignatura asociada
- ❌ `project` - El proyecto asociado

> **💡 Importante:** NO es necesario enviar el campo `mode` en tus peticiones PATCH. El sistema verifica automáticamente el modo del servicio antes de permitir la modificación.

---

## Ejemplos Adicionales

### Actualizar Solo Variables de Entorno

```bash
curl -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "env_vars": {
      "DB_HOST": "10.5.0.2",
      "DEBUG": "false",
      "API_KEY": "nueva-clave-secreta"
    }
  }'
```

### Cambiar Tipo y Visibilidad

```bash
curl -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "container_type": "database",
    "is_web": false
  }'
```

---

## Respuesta Exitosa

```json
{
  "id": 123,
  "name": "mi-servicio",
  "mode": "dockerhub",
  "image": "nginx:latest",
  "status": "creating",
  "internal_port": 3000,
  "assigned_port": 45678,
  "container_type": "web",
  "is_web": true,
  "env_vars": {
    "DB_HOST": "10.5.0.2",
    "DEBUG": "false"
  },
  "created_at": "2026-02-15T20:00:00Z",
  "updated_at": "2026-02-15T22:15:00Z"
}
```

> **Estado:** Después de la actualización, el servicio quedará en estado `creating` mientras se reconstruye. Luego pasará a `running` o `error` según el resultado.

---

## Errores Comunes

<details class="api-errors">
<summary>Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>400 Bad Request:</strong> Datos inválidos, campos no modificables, o intentas modificar la imagen en modo DockerHub.<br>
    <strong>401 Unauthorized:</strong> Token de autenticación inválido o ausente.<br>
    <strong>403 Forbidden:</strong> Intentas modificar un servicio del catálogo oficial o no eres el propietario.<br>
    <strong>404 Not Found:</strong> El servicio con ese ID no existe.<br>
    <strong>500 Internal Server Error:</strong> Error al reiniciar el contenedor después de la actualización.
</div>
</details>

### Ejemplo de Error: Servicio del Catálogo

```json
{
  "detail": "Los servicios del catálogo oficial no se pueden editar."
}
```

### Ejemplo de Error: Intentar Cambiar Imagen en DockerHub

```json
{
  "image": [
    "La imagen no se puede modificar en servicios DockerHub. Crea un nuevo servicio si necesitas cambiar la imagen."
  ]
}
```

### Ejemplo de Error: Campo No Modificable

```json
{
  "mode": ["Este campo no puede ser modificado después de la creación."]
}
```

---

## Buenas Prácticas

1. 📝 **Actualiza solo lo necesario** - PATCH permite enviar únicamente los campos que deseas cambiar
2. 🔄 **Espera a que termine** - El reinicio puede tardar unos segundos
3. 📊 **Verifica el estado** - Usa `GET /api/containers/{id}/` para confirmar que el servicio está `running`
4. 💾 **Haz backup** - Si subes nuevos archivos, guarda los anteriores por si necesitas revertir
5. 🧪 **Prueba en desarrollo** - Valida los cambios antes de aplicarlos en producción
6. 🚫 **No intentes cambiar la imagen en DockerHub** - Crea un nuevo servicio en su lugar
7. 📦 **En Compose, edita el YAML** - Para cambiar puertos o servicios, actualiza el `docker-compose.yml`

---
