# 🚀 Crear Servicio

Endpoint para desplegar servicios en PaaSify. Soporta tres modos principales de despliegue.

**Endpoint:** `POST /api/containers/`

---

## 📋 Parámetros Comunes

Campos disponibles en **todos** los modos de despliegue:

| Campo              | Tipo   | Obligatorio | Descripción                                                                                                                             |
| :----------------- | :----- | :---------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| **name**           | string | ✅ **Sí**   | Nombre del servicio. **Tolerante a fallos humanos**: Convierte espacios y caracteres no válidos a formato `snake_case` automáticamente. |
| **project**        | int    | ✅ **Sí**   | ID del proyecto.                                                                                                                        |
| **subject**        | int    | ✅ **Sí**   | ID de la asignatura.                                                                                                                    |
| **container_type** | string | ⭕ No       | Clasificación del servicio. Valores: `web` (default), `api`, `database`, `misc`.                                                        |
| **is_web**         | bool   | ⭕ No       | `true` (default) o `false`. Si es `true`, aparece el botón "Acceder" en la interfaz.                                                    |
| **keep_volumes**   | bool   | ⭕ No       | `true` (default) o `false`. Conserva los datos en futuras recargas si hay volúmenes.                                                    |

> 💡 **Nota sobre Tipos:**
>
> - 🌐 **web**: Frontends, sitios estáticos, proxies (Nginx, React, Vue).
> - ⚙️ **api**: Backends, servicios REST/GraphQL (Django, Node, Spring).
> - 🗄️ **database**: Motores de base de datos (Postgres, MySQL, Mongo).
> - 📦 **misc**: Workers, caches (Redis), scripts o herramientas.

---

## 🎯 Modos de Despliegue

### 📚 Modo Catálogo (Default)

Despliega una imagen pre-aprobada del catálogo oficial de PaaSify.

#### Parámetros Específicos:

| Campo              | Tipo   | Valor                            | Descripción                                                                                                                     |
| :----------------- | :----- | :------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **mode**           | string | `default`                        | (Opcional, es el valor por defecto).                                                                                            |
| **image**          | string |                                  | Nombre de la imagen del catálogo (ej: `wordpress:latest`). Accede a la documentación técnica para ver las imágenes disponibles. |
| **container_type** | string | `web`, `api`, `database`, `misc` | (Opcional).                                                                                                                     |
| **is_web**         | bool   | `true` o `false`                 | (Opcional).                                                                                                                     |

#### 📝 Ejemplo cURL:

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-blog",
    "image": "wordpress:latest",
    "project": 1,
    "subject": 1,
    "container_type": "web"
  }'
```

#### ✅ Ventajas:

- ⚡ Despliegue rápido
- 🔒 Imágenes verificadas y seguras
- 📖 Documentación incluida

---

### 🐳 Modo DockerHub

Despliega **cualquier imagen pública** desde DockerHub.

#### Parámetros Específicos:

| Campo              | Valor            | Descripción                                       |
| :----------------- | :--------------- | :------------------------------------------------ |
| **mode**           | `dockerhub`      | ✅ **Requerido**.                                 |
| **image**          | ej: `python:3.9` | Imagen pública (usuario/imagen:tag o imagen:tag). |
| **env_vars**       | objeto           | Variables de entorno (opcional).                  |
| **internal_port**  | entero           | Puerto donde escucha el contenedor (ej: 3000).    |
| **container_type** | string           | `web`, `api`, `database`, `misc` (opcional).      |
| **is_web**         | bool             | `true` o `false` (opcional).                      |

#### 📝 Ejemplo cURL:

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-api-python",
    "mode": "dockerhub",
    "image": "python:3.9-slim",
    "internal_port": 5000,
    "env_vars": {
      "DEBUG": "True",
      "SECRET_KEY": "xyz"
    },
    "project": 1,
    "subject": 1,
    "container_type": "api"
  }'
```

#### ✅ Ventajas:

- 🌍 Acceso a millones de imágenes públicas
- 🔄 Actualizaciones automáticas disponibles
- 🎨 Flexibilidad total

#### ⚠️ Consideraciones:

- La imagen debe existir y ser pública en DockerHub
- PaaSify verificará la existencia antes de desplegar
- **No se puede cambiar la imagen después** (crear nuevo servicio)

---

### 🛠️ Modo Custom: Código Propio

Sube tu código fuente (`.zip`) y define cómo construirlo. Requiere `multipart/form-data`.

#### Parámetros Base:

- **mode**: `custom` ✅
- **code**: Archivo `.zip` con el código ✅

---

#### 🔧 Opción A: Dockerfile Único

Para servicios simples definidos en un `Dockerfile`.

| Campo          | Tipo   | Descripción                                                          |
| :------------- | :----- | :------------------------------------------------------------------- |
| **dockerfile** | File   | Archivo `Dockerfile` (debe estar en la raíz o coincidir con el zip). |
| **code**       | File   | Archivo `.zip` con tu código fuente.                                 |
| **env_vars**   | objeto | Variables de entorno (opcional, en formato JSON).                    |

#### 📝 Ejemplo 1: Básico (Sin variables)

Para despliegues estándar que no requieren configuración externa:

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-app-node" \
  -F "mode=custom" \
  -F "code=@app.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1" \
  -F "container_type=web"
```

#### 📝 Ejemplo 2: Avanzado (Con variables de entorno)

Usa el campo `env_vars` con un objeto JSON para configurar tu aplicación:

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-app-configurada" \
  -F "mode=custom" \
  -F "code=@app.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1" \
  -F 'env_vars={"DEBUG":"true", "PORT":"8080", "API_KEY":"xyz789"}'
```

#### ✅ Ideal para:

- 🎯 Aplicaciones single-container
- 🚀 Microservicios individuales
- 📱 Apps Node.js, Python, Go, etc.

---

#### 📦 Opción B: Docker Compose (Multi-contenedor)

Para stacks completos definidos en `docker-compose.yml`.

| Campo                 | Tipo        | Obligatorio | Descripción                          |
| :-------------------- | :---------- | :---------- | :----------------------------------- |
| **compose**           | File        | ✅ **Sí**   | Archivo `docker-compose.yml` válido. |
| **code**              | File        | ✅ **Sí**   | Archivo `.zip` con tu código fuente. |
| **container_configs** | JSON String | ⭕ No       | Configuración manual por servicio.   |

#### 🤖 Autoconfiguración Inteligente:

Si no envías `container_configs`, PaaSify analizará tu YAML y detectará automáticamente:

- 🏷️ **Tipo de servicio**: Basado en nombres de imagen y servicio (ej: `postgres` → database).
- 👁️ **Visibilidad Web**: Determina si aparecerá el botón **"Acceder"** en la interfaz (`is_web=true`).

> 💡 **Nota:** Si `is_web=false`, el servicio seguirá siendo accesible vía terminal, logs o conectando al puerto asignado.

#### 📝 Ejemplo 1: Configuración Automática (Recomendado)

Simplemente sube el archivo, el sistema se encargará del resto.

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-stack-auto" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

#### 📝 Ejemplo 2: Configuración Manual (Avanzado)

Si deseas forzar tipos específicos o visibilidad (ej: ocultar un panel de administración):

```bash
curl -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=stack-custom" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1" \
  -F 'container_configs={"frontend":{"container_type":"web"},"db":{"container_type":"database","is_web":false}}'
```

#### ✅ Ideal para:

- 🏗️ Aplicaciones full-stack (frontend + backend + DB)
- 🔗 Servicios interdependientes
- 🌐 Arquitecturas de microservicios

---

## 📊 Tabla Comparativa de Modos

| Característica       | 📚 Catálogo | 🐳 DockerHub | 🛠️ Custom (Dockerfile) | 📦 Custom (Compose) |
| -------------------- | ----------- | ------------ | ---------------------- | ------------------- |
| **Velocidad**        | ⚡⚡⚡      | ⚡⚡         | ⚡                     | ⚡                  |
| **Flexibilidad**     | ⭐          | ⭐⭐⭐       | ⭐⭐⭐⭐               | ⭐⭐⭐⭐⭐          |
| **Complejidad**      | 🟢 Baja     | 🟡 Media     | 🟡 Media               | 🔴 Alta             |
| **Código propio**    | ❌          | ❌           | ✅                     | ✅                  |
| **Multi-contenedor** | ❌          | ❌           | ❌                     | ✅                  |

---

## 📬 Códigos de Respuesta

| Código               | Descripción                                                  |
| -------------------- | ------------------------------------------------------------ |
| **201 Created**      | ✅ Servicio validado y encolado para despliegue.             |
| **400 Bad Request**  | ❌ Faltan archivos, nombre inválido o configuración errónea. |
| **401 Unauthorized** | 🔒 Token no válido.                                          |
| **500 Server Error** | ⚠️ Error interno al procesar la solicitud.                   |

---

## 💡 Buenas Prácticas

1. 📝 **Nombres descriptivos** - Usa nombres claros como `frontend-react` en lugar de `app1`
2. 🏷️ **Clasifica correctamente** - Asigna el `container_type` adecuado para mejor organización
3. 🔐 **Variables de entorno** - Usa `env_vars` para configuración sensible
4. 📦 **Comprime eficientemente** - Excluye `node_modules`, `.git`, etc. del ZIP
5. 🧪 **Prueba localmente** - Valida tu Dockerfile/Compose antes de subir
6. 📖 **Documenta** - Incluye un README en tu código ZIP

---

## 🚨 Errores Comunes

<details class="api-errors">
<summary>Errores frecuentes y soluciones</summary>
<div class="api-error-content">
    <strong>❌ "Imagen no encontrada en DockerHub":</strong> Verifica que la imagen existe y es pública.<br>
    <strong>❌ "Nombre de servicio inválido":</strong> Solo usa minúsculas, números y guiones.<br>
    <strong>❌ "Puerto ya en uso":</strong> El puerto externo ya está ocupado, deja que PaaSify lo asigne automáticamente.<br>
    <strong>❌ "Archivo ZIP corrupto":</strong> Asegúrate de que el ZIP está bien formado.<br>
    <strong>❌ "Docker Compose inválido":</strong> Valida tu YAML con un linter antes de subir.
</div>
</details>

---
