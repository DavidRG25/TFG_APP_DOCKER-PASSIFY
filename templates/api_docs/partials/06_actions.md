# ⚡ Acciones del Servicio

Endpoints específicos para controlar el ciclo de vida de tus contenedores.

---

## ▶️ Iniciar Servicio

Arranca un servicio que está detenido o en error.

**Endpoint:** `POST /api/containers/{id}/start/`

### 📝 Ejemplo:

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/start/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

### ✅ Respuesta Exitosa:

```json
{
  "status": "success",
  "message": "Servicio iniciado correctamente",
  "container_status": "running"
}
```

### 💡 Casos de Uso:

- 🔄 Reiniciar un servicio después de mantenimiento
- 🚀 Activar un servicio que estaba pausado
- 🔧 Recuperar de un estado de error

<details class="api-errors">
<summary>❌ Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> 🔒 No autenticado.<br>
    <strong>403 Forbidden:</strong> 🚫 No eres el propietario de este servicio.<br>
    <strong>404 Not Found:</strong> 🔍 El ID del servicio no existe.<br>
    <strong>400 Bad Request:</strong> ⚠️ El contenedor ya está iniciado o en un estado no válido.<br>
    <strong>500 Internal Server Error:</strong> 💥 Error al intentar ejecutar el comando de inicio en Docker.
</div>
</details>

---

## ⏸️ Detener Servicio

Detiene el contenedor pero conserva su configuración (estado `stopped`).

**Endpoint:** `POST /api/containers/{id}/stop/`

### 📝 Ejemplo:

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/stop/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

### ✅ Respuesta Exitosa:

```json
{
  "status": "success",
  "message": "Servicio detenido correctamente",
  "container_status": "stopped"
}
```

### 💡 Casos de Uso:

- 💾 Ahorrar recursos cuando no se usa el servicio
- 🔧 Realizar mantenimiento o actualizaciones
- 🛑 Pausar temporalmente sin perder configuración

> ⚠️ **Nota:** Los datos y configuración se mantienen. Puedes reiniciar el servicio en cualquier momento.

<details class="api-errors">
<summary>❌ Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> 🔒 Token inválido.<br>
    <strong>403 Forbidden:</strong> 🚫 Acceso denegado al recurso.<br>
    <strong>404 Not Found:</strong> 🔍 Servicio no encontrado.<br>
    <strong>400 Bad Request:</strong> ⚠️ El contenedor ya está detenido.<br>
    <strong>500 Internal Server Error:</strong> 💥 Fallo al detener el proceso.
</div>
</details>

---

## 🗑️ Eliminar Servicio

Elimina **permanentemente** el servicio de la plataforma.

**Endpoint:** `POST /api/containers/{id}/remove/`

### 📝 Ejemplo:

```bash
curl -X POST "{{ PAASIFY_API_URL }}/containers/{id}/remove/" \
  -H "Authorization: Bearer <TU_API_TOKEN>"
```

### ✅ Respuesta Exitosa:

```json
{
  "status": "success",
  "message": "Servicio eliminado correctamente",
  "container_status": "removed"
}
```

### ⚠️ ADVERTENCIA:

Esta acción es **irreversible**. Se eliminarán:

- 🗄️ El contenedor y sus datos
- 📁 Archivos de configuración
- 🔌 Puertos asignados (liberados para otros servicios)
- 📊 Logs históricos

> 💡 **Recomendación:** Haz backup de datos importantes antes de eliminar.

<details class="api-errors">
<summary>❌ Códigos de error de este endpoint</summary>
<div class="api-error-content">
    <strong>401 Unauthorized:</strong> 🔒 Token inválido.<br>
    <strong>403 Forbidden:</strong> 🚫 No puedes eliminar un servicio que no te pertenece.<br>
    <strong>404 Not Found:</strong> 🔍 Servicio ya eliminado o inexistente.<br>
    <strong>500 Internal Server Error:</strong> 💥 Error al limpiar los recursos.
</div>
</details>

---

## 🔄 Transiciones de Estado

El ciclo de vida de un servicio sigue estas reglas:

| Estado Actual   | Acción Posible | Nuevo Estado | Descripción                                    |
| :-------------- | :------------- | :----------- | :--------------------------------------------- |
| 🔴 `stopped`    | **start**      | 🟢 `running` | El contenedor arranca y ejecuta tu aplicación. |
| 🟢 `running`    | **stop**       | 🔴 `stopped` | El contenedor se detiene ordenadamente.        |
| ⚠️ `error`      | **start**      | 🟢 `running` | Intenta reiniciar el servicio tras un fallo.   |
| 🔄 _Cualquiera_ | **remove**     | 🗑️ `removed` | Eliminación definitiva (irreversible).         |

---

## 💡 Buenas Prácticas

1. 🔄 **Detén antes de eliminar** - Asegúrate de que el servicio esté detenido antes de eliminarlo
2. 💾 **Haz backup** - Exporta datos importantes antes de eliminar
3. 🔍 **Verifica el estado** - Usa `GET /api/containers/{id}/` para confirmar el estado actual
4. ⏱️ **Espera entre acciones** - Dale tiempo al sistema para completar cada operación
5. 📊 **Revisa los logs** - Antes de eliminar, descarga los logs si los necesitas

---

## 🎯 Ejemplos de Automatización

### Script Bash: Reiniciar Servicio

```bash
#!/bin/bash
TOKEN="tu-token-aqui"
SERVICE_ID=123

# Detener
curl -X POST "{{ PAASIFY_API_URL }}/containers/$SERVICE_ID/stop/" \
  -H "Authorization: Bearer $TOKEN"

# Esperar 5 segundos
sleep 5

# Iniciar
curl -X POST "{{ PAASIFY_API_URL }}/containers/$SERVICE_ID/start/" \
  -H "Authorization: Bearer $TOKEN"

echo "✅ Servicio reiniciado"
```

### Python: Eliminar Múltiples Servicios

```python
import requests

TOKEN = "tu-token-aqui"
BASE_URL = "{{ PAASIFY_API_URL }}"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

services_to_remove = [123, 124, 125]

for service_id in services_to_remove:
    response = requests.post(
        f"{BASE_URL}/containers/{service_id}/remove/",
        headers=HEADERS
    )
    if response.status_code == 200:
        print(f"✅ Servicio {service_id} eliminado")
    else:
        print(f"❌ Error al eliminar {service_id}: {response.text}")
```

---
