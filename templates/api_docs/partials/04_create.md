# Crear Servicio

Endpoint para desplegar servicios. Soporta tres modos principales: **Catálogo**, **DockerHub** y **Custom** (Código propio).

**Endpoint:** `POST /api/containers/`

---

### 1. Parámetros Comunes

Campos disponibles en todos los modos de despliegue.

| Campo              | Tipo   | Obligatorio | Descripción                                                                          |
| :----------------- | :----- | :---------- | :----------------------------------------------------------------------------------- |
| **name**           | string | **Sí**      | Nombre del servicio (slug: minúsculas, números y guiones).                           |
| **project**        | int    | **Sí**      | ID del proyecto.                                                                     |
| **subject**        | int    | **Sí**      | ID de la asignatura.                                                                 |
| **container_type** | string | No          | Clasificación del servicio. Valores: `web` (default), `api`, `database`, `misc`.     |
| **is_web**         | bool   | No          | `true` (default) o `false`. Si es `true`, aparece el botón "Acceder" en la interfaz. |

> ℹ️ **Nota sobre Tipos:**
>
> - `web`: Frontends, sitios estáticos, proxies (Nginx, React).
> - `api`: Backends, servicios REST/GraphQL (Django, Node, Spring).
> - `database`: Motores de base de datos (Postgres, MySQL, Mongo).
> - `misc`: Workers, caches (Redis), scripts o herramientas.

---

### 2. Modo Catálogo (Default)

Despliega una imagen pre-aprobada del catálogo de PaaSify.

**Parámetros Específicos:**

| Campo     | Valor              | Descripción                                |
| :-------- | :----------------- | :----------------------------------------- |
| **mode**  | `default`          | (Opcional, es el valor por defecto).       |
| **image** | ej: `nginx:latest` | Nombre exacto de la imagen en el catálogo. |

**Ejemplo cURL:**

```bash
curl -X POST {{ host }}/api/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json"
  -d '{
    "name": "mi-blog",
    "image": "wordpress:latest",
    "project": 1,
    "subject": 1,
    "container_type": "web"
  }'
```

---

### 3. Modo DockerHub

Despliega cualquier imagen pública desde DockerHub.

**Parámetros Específicos:**

| Campo             | Valor            | Descripción                                          |
| :---------------- | :--------------- | :--------------------------------------------------- |
| **mode**          | `dockerhub`      | **Requerido**.                                       |
| **image**         | ej: `python:3.9` | Imagen pública (usuario/imagen:tag o imagen:tag).    |
| **environment**   | Objeto JSON      | Variables de entorno necesarias.                     |
| **internal_port** | Entero           | Puerto donde escucha el contenedor (ej: 3000, 8080). |

**Ejemplo cURL:**

```bash
curl -X POST {{ host }}/api/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json"
  -d '{
    "name": "mi-api-python",
    "mode": "dockerhub",
    "image": "python:3.9-slim",
    "internal_port": 5000,
    "environment": { "DEBUG": "True", "SECRET_KEY": "xyz" },
    "project": 1,
    "subject": 1,
    "container_type": "api"
  }'
```

---

### 4. Modo Custom: Código Propio

Sube tu código fuente (`.zip`) y define cómo construirlo. Requiere `multipart/form-data`.

**Parámetros Base:**

- **mode**: `custom`
- **code**: Archivo `.zip` con el código.

#### Opción A: Dockerfile Único

Para servicios simples definidos en un `Dockerfile`.

| Campo          | Tipo | Descripción                                                          |
| :------------- | :--- | :------------------------------------------------------------------- |
| **dockerfile** | File | Archivo `Dockerfile` (debe estar en la raíz o coincidir con el zip). |

**Ejemplo:**

```bash
curl -X POST {{ host }}/api/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-app-node" \
  -F "mode=custom" \
  -F "code=@app.zip" \
  -F "dockerfile=@Dockerfile" \
  -F "project=1" \
  -F "subject=1" \
  -F "container_type=web"
```

#### Opción B: Docker Compose (Multi-contenedor)

Para stacks completos definidos en `docker-compose.yml`.

| Campo                 | Tipo        | Obligatorio | Descripción                          |
| :-------------------- | :---------- | :---------- | :----------------------------------- |
| **compose**           | File        | **Sí**      | Archivo `docker-compose.yml` válido. |
| **container_configs** | JSON String | No          | Configuración manual por servicio.   |

**Autoconfiguración Inteligente:**
Si no envías `container_configs`, PaaSify analizará tu YAML y detectará automáticamente:

- **Tipo de servicio**: Basado en nombres de imagen y servicio (ej: `postgres` -> database).
- **Visibilidad Web**: Determina si aparecerá el botón **"Acceder"** en la interfaz (`is_web=true`). Si se desactiva, el servicio seguirá siendo accesible vía terminal, logs o conectando al puerto asignado por la plataforma.

**Ejemplo 1: Configuración Automática (Recomendado)**
Simplemente sube el archivo, el sistema se encargará del resto.

```bash
curl -X POST {{ host }}/api/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-stack-auto" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

**Ejemplo 2: Configuración Manual (Avanzado)**
Si deseas forzar tipos específicos o visibilidad (ej: ocultar un panel de administración), usa `container_configs`.

```bash
curl -X POST {{ host }}/api/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=stack-custom" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1" \
  -F 'container_configs={"frontend":{"container_type":"web"},"db":{"container_type":"database","is_web":false}}'
```

---

### Códigos de Respuesta

- **201 Created**: Servicio validado y encolado para despliegue.
- **400 Bad Request**: Faltan archivos, nombre inválido o configuración errónea.
- **401 Unauthorized**: Token no válido.
- **500 Server Error**: Error interno al procesar la solicitud.
