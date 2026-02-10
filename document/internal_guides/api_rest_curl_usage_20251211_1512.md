# Guía de Uso del API REST de PaaSify con curl

**Fecha:** 11/12/2025 15:12  
**Versión:** 5.0  
**Propósito:** Documentación interna para despliegue de contenedores vía API REST

---

## 📋 Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Despliegue con Imagen del Catálogo](#despliegue-con-imagen-del-catálogo)
3. [Despliegue con Dockerfile Personalizado](#despliegue-con-dockerfile-personalizado)
4. [Despliegue con Docker Compose](#despliegue-con-docker-compose)
5. [Gestión de Servicios](#gestión-de-servicios)
6. [Consulta de Imágenes Disponibles](#consulta-de-imágenes-disponibles)
7. [Códigos de Respuesta](#códigos-de-respuesta)

---

## 🔑 Autenticación

### Obtener tu Bearer Token

1. **Vía Web UI:**

   - Accede a `http://localhost:8000/profile/`
   - Copia tu token desde la sección "Bearer Token API"

2. **Generar nuevo token:**
   ```bash
   # Desde la UI: Click en "Refrescar Token"
   # O vía curl (requiere sesión activa):
   curl --request POST \
     --url http://localhost:8000/profile/generate-token/ \
     --cookie "sessionid=TU_SESSION_ID"
   ```

### Usar el Token en Requests

Todas las peticiones al API deben incluir el header:

```bash
Authorization: Bearer TU_TOKEN_AQUI
```

**Ejemplo:**

```bash
curl --request GET \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer eyJhbGc...GYTNuNds'
```

### Ver Códigos de Estado HTTP

Por defecto, curl solo muestra el cuerpo de la respuesta. Para ver el código de estado HTTP (200, 201, 400, etc.), usa una de estas opciones:

**Opción 1: Mostrar código de estado con `-w`**

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{"name": "test", "image": "nginx:latest"}' \
  --write-out '\nHTTP Status: %{http_code}\n'
```

**Salida:**

```json
{"id":102,"name":"test",...}
HTTP Status: 201
```

**Opción 2: Mostrar headers completos con `-i`**

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{"name": "test", "image": "nginx:latest"}' \
  --include
```

**Salida:**

```
HTTP/1.1 201 Created
Content-Type: application/json
...

{"id":102,"name":"test",...}
```

**Opción 3: Solo el código de estado con `-s` y `-o`**

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{"name": "test", "image": "nginx:latest"}' \
  --silent --output /dev/null --write-out '%{http_code}\n'
```

**Salida:**

```
201
```

> 💡 **Tip:** Para debugging, usa siempre `-w '\nHTTP Status: %{http_code}\n'` para ver el código de estado junto con la respuesta.

---

## 📦 Despliegue con Imagen del Catálogo

### Caso 1: Despliegue Básico (nginx)

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "prueba-curl",
    "image": "nginx:latest",
    "mode": "default"
  }' \
  --write-out '\nHTTP Status: %{http_code}\n'
```

**Respuesta (201 Created):**

```json
{
  "id": 1,
  "name": "prueba-curl",
  "image": "nginx:latest",
  "status": "creating",
  "assigned_port": 45001,
  "internal_port": 80,
  "logs": "",
  "has_compose": false
}
HTTP Status: 201
```

> ⚠️ **Nota importante:** Aunque técnicamente el campo `project` es opcional en el API, se **recomienda encarecidamente** incluirlo para mantener consistencia con la interfaz web. En futuras versiones (v6.0+) será obligatorio. Ver: `document/bugs_features/bug_inconsistencia_validacion_proyecto_20251211_1520.md`

### Caso 2: Con Proyecto Asignado

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "web-proyecto1",
    "image": "nginx:latest",
    "mode": "default",
    "project": 1,
    "subject": 1
  }'
```

> 📝 **Nota:** Los campos `project` y `subject` deben ser **IDs numéricos** (claves primarias), no nombres.

**¿Cómo obtener los IDs de tus proyectos?**

> ⚠️ **Limitación actual (v5.0):** No existe un endpoint del API para listar proyectos y asignaturas. Ver bug: `document/bugs_features/bug_falta_endpoint_listar_proyectos_20251211_1529.md`

**Workarounds temporales:**

**Opción 1 - Vía Web UI:**

1. Accede a `http://localhost:8000/paasify/containers/`
2. Abre el modal "Nuevo servicio"
3. Inspecciona el selector de proyectos (F12 → Elements)
4. Los IDs están en `<option value="1">Nombre Proyecto</option>`

**Opción 2 - Vía consola del navegador:**

```javascript
// Abre cualquier página de PaaSify, presiona F12 y ejecuta:
console.table(
  Array.from(document.querySelectorAll('select[name="project"] option'))
    .filter((o) => o.value)
    .map((o) => ({ id: parseInt(o.value), proyecto: o.textContent.trim() }))
);
```

**Opción 3 - Hardcodear temporalmente:**
Si solo tienes un proyecto, probablemente su ID sea `1`. Puedes intentar:

```bash
# Listar tus servicios para ver qué project_id tienen
curl --request GET \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN'
# Busca el campo "project" en la respuesta
```

### Caso 3: Con Puerto Personalizado

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mi-app",
    "image": "nginx:latest",
    "mode": "default",
    "custom_port": 8080
  }'
```

### Caso 4: Con Variables de Entorno

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mysql-db",
    "image": "mysql:8.0",
    "mode": "default",
    "env_vars": {
      "MYSQL_ROOT_PASSWORD": "secret123",
      "MYSQL_DATABASE": "myapp"
    },
    "internal_port": 3306
  }'
```

### Caso 5: Configuración Completa

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "app-completa",
    "image": "nginx:latest",
    "mode": "default",
    "project": 1,
    "subject": 1,
    "custom_port": 8080,
    "internal_port": 80,
    "env_vars": {
      "ENV": "production",
      "DEBUG": "false"
    }
  }'
```

---

## 🐳 Despliegue con Dockerfile Personalizado

### Preparación

**1. Crea tu Dockerfile:**

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 3000
CMD ["node", "server.js"]
```

**2. Empaqueta tu código:**

```bash
# Incluye todos los archivos necesarios
zip -r mi-app.zip . -x "*.git*" -x "node_modules/*"
```

### Despliegue Básico

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --form 'name=node-app' \
  --form 'mode=custom' \
  --form 'dockerfile=@./Dockerfile' \
  --form 'code=@./mi-app.zip'
```

### Con Puerto Interno Específico

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --form 'name=node-app-3000' \
  --form 'mode=custom' \
  --form 'dockerfile=@./Dockerfile' \
  --form 'code=@./mi-app.zip' \
  --form 'internal_port=3000'
```

### Con Proyecto y Puerto Personalizado

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --form 'name=proyecto-custom' \
  --form 'mode=custom' \
  --form 'project=1' \
  --form 'dockerfile=@./Dockerfile' \
  --form 'code=@./codigo.zip' \
  --form 'custom_port=8080' \
  --form 'internal_port=3000'
```

---

## 🐙 Despliegue con Docker Compose

### Preparación

**1. Crea tu docker-compose.yml:**

```yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "5000:5000"
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

**2. Empaqueta todo:**

```bash
zip -r mi-compose-app.zip . -x "*.git*"
```

### Despliegue Básico

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --form 'name=compose-stack' \
  --form 'mode=custom' \
  --form 'compose=@./docker-compose.yml' \
  --form 'code=@./mi-compose-app.zip'
```

### Con Proyecto Asignado

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN' \
  --form 'name=stack-proyecto2' \
  --form 'mode=custom' \
  --form 'project=2' \
  --form 'compose=@./docker-compose.yml' \
  --form 'code=@./app.zip'
```

---

## 🎮 Gestión de Servicios

### Listar Todos tus Servicios

```bash
curl --request GET \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "mi-nginx",
    "image": "nginx:latest",
    "status": "running",
    "assigned_port": 45001,
    "has_compose": false
  },
  {
    "id": 2,
    "name": "compose-stack",
    "status": "running",
    "has_compose": true,
    "containers": [
      { "name": "web", "status": "running" },
      { "name": "redis", "status": "running" }
    ]
  }
]
```

### Obtener Detalles de un Servicio

```bash
curl --request GET \
  --url http://localhost:8000/api/containers/1/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

### Iniciar un Servicio

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/1/start/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

### Detener un Servicio

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/1/stop/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

### Eliminar un Servicio

```bash
curl --request DELETE \
  --url http://localhost:8000/api/containers/1/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

**O usando la acción remove:**

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/1/remove/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

---

## 🖼️ Consulta de Imágenes Disponibles

### Listar Catálogo de Imágenes

```bash
curl --request GET \
  --url http://localhost:8000/api/images/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "nginx",
    "tag": "latest",
    "description": "Servidor web de alto rendimiento"
  },
  {
    "id": 2,
    "name": "mysql",
    "tag": "8.0",
    "description": "Base de datos relacional"
  }
]
```

---

## 📊 Códigos de Respuesta

| Código | Significado  | Descripción                               |
| ------ | ------------ | ----------------------------------------- |
| 200    | OK           | Operación exitosa (GET, actualización)    |
| 201    | Created      | Servicio creado exitosamente              |
| 204    | No Content   | Eliminación exitosa                       |
| 400    | Bad Request  | Datos inválidos o falta campo obligatorio |
| 401    | Unauthorized | Token inválido o ausente                  |
| 403    | Forbidden    | No tienes permisos para esta operación    |
| 404    | Not Found    | Servicio o recurso no encontrado          |
| 500    | Server Error | Error interno (revisar logs del servicio) |

---

## 🛠️ Ejemplos de Scripts Completos

### Script Bash: Desplegar Múltiples Servicios

```bash
#!/bin/bash

TOKEN="TU_TOKEN_AQUI"
API_URL="http://localhost:8000/api/containers/"

# Función para crear servicio
create_service() {
  local name=$1
  local image=$2

  curl --request POST \
    --url "$API_URL" \
    --header "Authorization: Bearer $TOKEN" \
    --header 'Content-Type: application/json' \
    --data "{
      \"name\": \"$name\",
      \"image\": \"$image\",
      \"mode\": \"default\"
    }"
  echo ""
}

# Desplegar servicios
create_service "web-frontend" "nginx:latest"
create_service "api-backend" "node:18-alpine"
create_service "database" "mysql:8.0"

echo "Servicios desplegados!"
```

### Script Python: Gestión Completa

```python
import requests

TOKEN = "TU_TOKEN_AQUI"
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def create_service(name, image):
    response = requests.post(
        f"{BASE_URL}/containers/",
        headers=HEADERS,
        json={"name": name, "image": image, "mode": "default"}
    )
    return response.json()

def list_services():
    response = requests.get(f"{BASE_URL}/containers/", headers=HEADERS)
    return response.json()

def start_service(service_id):
    response = requests.post(
        f"{BASE_URL}/containers/{service_id}/start/",
        headers=HEADERS
    )
    return response.status_code == 200

# Uso
service = create_service("mi-app", "nginx:latest")
print(f"Servicio creado: {service['id']}")

services = list_services()
print(f"Total servicios: {len(services)}")
```

---

## 📝 Notas Importantes

1. **Proyecto Obligatorio (v5.0+)**: Desde la versión 5.0, todos los servicios deben estar asociados a un proyecto. Asegúrate de incluir el campo `project` en tus requests.

2. **Límites de Puertos**: Los puertos disponibles están en el rango 40000-50000. Si no especificas `custom_port`, se asignará uno automáticamente.

3. **Tamaño de Archivos**: Los archivos ZIP/RAR no deben superar 100MB.

4. **Timeout**: Las operaciones de build pueden tardar varios minutos. El servicio quedará en estado `creating` hasta completarse.

5. **Logs**: Puedes consultar los logs de build/ejecución en el campo `logs` del servicio.

---

## 🔮 Futuras Mejoras

Esta guía será ampliada en futuras versiones con:

- [ ] Comandos para gestión de volúmenes
- [ ] Endpoints de métricas y monitoreo
- [ ] Webhooks para notificaciones
- [ ] CLI oficial de PaaSify
- [ ] Integración con CI/CD

---

**Última actualización:** 11/12/2025  
**Mantenedor:** Equipo PaaSify  
**Feedback:** Reportar issues en el repositorio del proyecto
