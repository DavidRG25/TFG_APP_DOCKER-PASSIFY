# Guía de Uso del API REST de PaaSify con curl

**Fecha:** 10/02/2026  
**Versión:** 6.1.0  
**Propósito:** Documentación interna actualizada para despliegue de contenedores vía API REST

---

## 📋 Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Despliegue con Imagen del Catálogo](#despliegue-con-imagen-del-catálogo)
4. [Despliegue con Dockerfile Personalizado](#despliegue-con-dockerfile-personalizado)
5. [Despliegue con Docker Compose](#despliegue-con-docker-compose)
6. [Gestión de Servicios](#gestión-de-servicios)
7. [Consulta de Recursos](#consulta-de-recursos)
8. [Códigos de Respuesta](#códigos-de-respuesta)

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

**Opción 1: Mostrar código de estado con `-w`**

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{"name": "test", "image": "nginx:latest"}' \
  --write-out '\nHTTP Status: %{http_code}\n'
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

> 💡 **Tip:** Para debugging, usa siempre `-w '\nHTTP Status: %{http_code}\n'` para ver el código de estado junto con la respuesta.

---

## 🌐 Endpoints Disponibles

### **Base URL:** `http://localhost:8000/api/`

| Endpoint                        | Métodos                 | Descripción                        |
| ------------------------------- | ----------------------- | ---------------------------------- |
| `/api/containers/`              | GET, POST               | Listar y crear servicios           |
| `/api/containers/<id>/`         | GET, PUT, PATCH, DELETE | Detalles y gestión de servicio     |
| `/api/containers/<id>/start/`   | POST                    | Iniciar servicio                   |
| `/api/containers/<id>/stop/`    | POST                    | Detener servicio                   |
| `/api/containers/<id>/restart/` | POST                    | Reiniciar servicio                 |
| `/api/containers/<id>/remove/`  | POST                    | Eliminar servicio                  |
| `/api/images/`                  | GET                     | Listar imágenes del catálogo       |
| `/api/subjects/`                | GET                     | Listar asignaturas del usuario     |
| `/api/subjects/<id>/`           | GET                     | Detalles de asignatura             |
| `/api/projects/`                | GET                     | Listar proyectos del usuario       |
| `/api/projects/<id>/`           | GET                     | Detalles de proyecto               |
| `/api/docs/`                    | GET                     | Documentación Swagger (solo admin) |
| `/api/schema/`                  | GET                     | Esquema OpenAPI (solo admin)       |

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
  "has_compose": false,
  "owner": 1,
  "project": null,
  "subject": null
}
HTTP Status: 201
```

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

**✅ Ahora disponible (v6.0+):** Usa los endpoints del API:

```bash
# Listar tus proyectos
curl --request GET \
  --url http://localhost:8000/api/projects/ \
  --header 'Authorization: Bearer TU_TOKEN'

# Respuesta:
[
  {
    "id": 1,
    "name": "Proyecto Final",
    "subject": 1,
    "subject_name": "Desarrollo Web",
    "date": "2026-01-15"
  }
]

# Listar tus asignaturas
curl --request GET \
  --url http://localhost:8000/api/subjects/ \
  --header 'Authorization: Bearer TU_TOKEN'

# Respuesta:
[
  {
    "id": 1,
    "name": "Desarrollo Web",
    "category": "Informática",
    "year": "2025-2026"
  }
]
```

**Filtrar proyectos por asignatura:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/projects/?subject=1' \
  --header 'Authorization: Bearer TU_TOKEN'
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
    "internal_port": 80,
    "has_compose": false,
    "owner": 1,
    "project": 1,
    "subject": 1
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

### Filtrar Servicios

**Por proyecto:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/containers/?project=1' \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Por asignatura:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/containers/?subject=1' \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Por estado:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/containers/?status=running' \
  --header 'Authorization: Bearer TU_TOKEN'
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

### Reiniciar un Servicio

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/1/restart/ \
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

## 🔍 Consulta de Recursos

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
    "description": "Servidor web de alto rendimiento",
    "internal_port": 80
  },
  {
    "id": 2,
    "name": "mysql",
    "tag": "8.0",
    "description": "Base de datos relacional",
    "internal_port": 3306
  }
]
```

### Listar tus Asignaturas

```bash
curl --request GET \
  --url http://localhost:8000/api/subjects/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "Desarrollo Web",
    "category": "Informática",
    "year": "2025-2026"
  }
]
```

### Listar tus Proyectos

```bash
curl --request GET \
  --url http://localhost:8000/api/projects/ \
  --header 'Authorization: Bearer TU_TOKEN'
```

**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "Proyecto Final",
    "subject": 1,
    "subject_name": "Desarrollo Web",
    "date": "2026-01-15"
  }
]
```

**Filtrar proyectos por asignatura:**

```bash
curl --request GET \
  --url 'http://localhost:8000/api/projects/?subject=1' \
  --header 'Authorization: Bearer TU_TOKEN'
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

def list_projects():
    response = requests.get(f"{BASE_URL}/projects/", headers=HEADERS)
    return response.json()

def list_subjects():
    response = requests.get(f"{BASE_URL}/subjects/", headers=HEADERS)
    return response.json()

# Uso
service = create_service("mi-app", "nginx:latest")
print(f"Servicio creado: {service['id']}")

services = list_services()
print(f"Total servicios: {len(services)}")

projects = list_projects()
print(f"Proyectos disponibles: {projects}")
```

---

## 📝 Notas Importantes

1. **Autenticación Obligatoria**: Todos los endpoints requieren autenticación con Bearer Token.

2. **Permisos por Rol**:
   - **Alumnos**: Solo ven y gestionan sus propios servicios
   - **Profesores**: Ven servicios de sus asignaturas
   - **Administradores**: Acceso completo a todos los servicios

3. **Límites de Puertos**: Los puertos disponibles están en el rango 40000-50000. Si no especificas `custom_port`, se asignará uno automáticamente.

4. **Tamaño de Archivos**: Los archivos ZIP/RAR no deben superar 100MB.

5. **Timeout**: Las operaciones de build pueden tardar varios minutos. El servicio quedará en estado `creating` hasta completarse.

6. **Logs**: Puedes consultar los logs de build/ejecución en el campo `logs` del servicio.

7. **Documentación Swagger**: Disponible en `/api/docs/` (solo para administradores).

---

## 🆕 Novedades en v6.0+

- ✅ **Endpoints de Proyectos y Asignaturas**: Ya no necesitas workarounds para obtener IDs
- ✅ **Filtros Avanzados**: Filtra servicios por proyecto, asignatura o estado
- ✅ **Documentación Swagger**: Documentación interactiva del API
- ✅ **Mejor Manejo de Errores**: Mensajes de error más descriptivos
- ✅ **Soporte Compose Mejorado**: Mejor gestión de servicios multi-contenedor

---

## 🔮 Futuras Mejoras

Esta guía será ampliada en futuras versiones con:

- [ ] Comandos para gestión de volúmenes
- [ ] Endpoints de métricas y monitoreo
- [ ] Webhooks para notificaciones
- [ ] CLI oficial de PaaSify
- [ ] Integración con CI/CD
- [ ] Acceso a terminal vía API
- [ ] Streaming de logs en tiempo real

---

**Última actualización:** 10/02/2026  
**Versión:** 6.1.0  
**Mantenedor:** Equipo PaaSify  
**Feedback:** Reportar issues en el repositorio del proyecto
