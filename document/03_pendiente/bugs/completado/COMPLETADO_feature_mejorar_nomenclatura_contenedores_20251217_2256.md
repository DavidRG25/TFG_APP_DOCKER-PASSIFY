# Feature: Mejorar Nomenclatura de Project Name en Docker Compose

**Fecha:** 17/12/2025 23:00  
**Tipo:** Feature Request / Mejora de Sistema  
**Prioridad:** Media  
**Estado:** ✅ COMPLETADO (17/12/2025 23:58)  
**Versión afectada:** v5.0

---

## 📋 Descripción

Mejorar el **project name** de Docker Compose (flag `-p`) para que sea descriptivo en lugar del actual `svc{id}`. También mejorar los nombres de contenedores simples (Dockerfile/imagen).

## 🔍 Problema Actual

### Según Docker Desktop:

**Contenedores Dockerfile:**

- `prueba-dockerfile_ctr` ✅ Aceptable
- `prueba-dockerfile1_ctr` ✅ Aceptable

**Docker Compose:**

- **Project name**: `svc100` ❌ **NO descriptivo**
- Contenedores resultantes:
  - `svc100_web-1` (el prefijo `svc100` no dice nada)
  - `svc100_redis-1`

### ⚠️ Aclaración Importante

**NO necesitamos modificar los nombres de servicios individuales** (`web`, `redis`) porque:

- ✅ Los define el usuario en su `docker-compose.yml`
- ✅ Docker Compose añade automáticamente el prefijo del project name
- ✅ **No hay colisiones**: Si dos usuarios tienen un servicio `web`:
  - Usuario 1 con project `proyecto1`: `proyecto1_web-1`
  - Usuario 2 con project `proyecto2`: `proyecto2_web-1`

**Solo necesitamos mejorar el PROJECT NAME** (`-p` flag)

## ✅ Solución Propuesta

### Formato para Project Name y Contenedores Simples

```
{usuario}_{proyecto}_{servicio}
```

**Componentes:**

- `usuario`: Username (max 10 chars, slugified)
- `proyecto`: Nombre del proyecto UserProject (max 15 chars, slugified)
- `servicio`: Nombre del servicio (max 20 chars, slugified)

### Ejemplos

#### Caso 1: Dockerfile Simple

**Antes:**

```bash
# Contenedor: prueba-dockerfile_ctr
```

**Después:**

```bash
# Contenedor: alumno_proyecto1_mi-app
```

#### Caso 2: Docker Compose

**Antes:**

```bash
# Project name: svc100
docker compose -p svc100 -f docker-compose.yml up -d

# Contenedores resultantes:
svc100_web-1
svc100_redis-1
```

**Después:**

```bash
# Project name: alumno_proyecto3_stack
docker compose -p alumno_proyecto3_stack -f docker-compose.yml up -d

# Contenedores resultantes:
alumno_proyecto3_stack_web-1
alumno_proyecto3_stack_redis-1
```

**Ventajas:**

- ✅ Se identifica al dueño (`alumno`)
- ✅ Se identifica el proyecto (`proyecto3`)
- ✅ Nombre descriptivo (`stack`)
- ✅ Los nombres de servicios del usuario se mantienen (`web`, `redis`)

## 🔧 Implementación

### Función de Generación

**Archivo:** `containers/services.py`

```python
from django.utils.text import slugify

def generate_project_name(service):
    """
    Genera nombre de proyecto/contenedor descriptivo.
    Formato: {usuario}_{proyecto}_{servicio}

    Returns:
        str: Nombre (max 63 chars)

    Ejemplos:
        - alumno_proyecto1_nginx
        - alumno_proyecto2_stack
    """
    username = slugify(service.owner.username)[:10]

    if service.project:
        project_name = slugify(service.project.place)[:15]
    else:
        project_name = "general"

    service_name = slugify(service.name)[:20]

    name = f"{username}_{project_name}_{service_name}"

    # Truncar si excede 63 caracteres
    if len(name) > 63:
        # Recalcular con límites más estrictos
        max_service_len = 63 - len(username) - len(project_name) - 2
        service_name = service_name[:max_service_len]
        name = f"{username}_{project_name}_{service_name}"

    return name
```

### Actualizar Dockerfile/Imagen Simple

```python
def run_container(service: Service, custom_port=None):
    """Crear contenedor simple"""

    # Generar nombre descriptivo
    container_name = generate_project_name(service)

    # Construir o usar imagen
    if service.dockerfile:
        image_tag = f"{container_name}_image"
        # ... build ...
    else:
        image_tag = service.image

    # Crear contenedor
    container = docker_client.containers.run(
        image_tag,
        name=container_name,  # ← Nombre mejorado
        detach=True,
        # ...
    )

    service.container_id = container.id
    service.save()
```

### Actualizar Docker Compose

```python
def run_compose(service: Service):
    """Ejecutar docker-compose con project name descriptivo"""

    workspace = ensure_service_workspace(service)
    compose_path = workspace / "docker-compose.yml"

    # Generar project name descriptivo
    project_name = generate_project_name(service)

    # Ejecutar compose con project name mejorado
    cmd = _compose_cmd() + [
        "-p", project_name,  # ← Project name mejorado
        "-f", str(compose_path),
        "up", "-d"
    ]

    subprocess.run(cmd, cwd=str(workspace), check=True)

    # Los contenedores tendrán nombres como:
    # {project_name}_web-1
    # {project_name}_redis-1
    # etc.
```

## 📊 Comparación

### Antes (Docker Desktop)

```
svc100_web-1
svc100_redis-1
prueba-dockerfile_ctr
svc105_db-1
```

❌ `svc100` no es descriptivo

### Después (Docker Desktop)

```
alumno_proyecto1_stack_web-1
alumno_proyecto1_stack_redis-1
alumno_proyecto2_nginx
alumno_proyecto3_api_db-1
```

✅ Claro quién es el dueño y qué proyecto es

### Comandos Mejorados

```bash
# Ver todos mis contenedores
docker ps --filter "name=alumno_"

# Ver contenedores de un proyecto
docker ps --filter "name=alumno_proyecto1_"

# Logs de un servicio específico
docker logs alumno_proyecto1_stack_web-1

# Detener todo un proyecto
docker stop $(docker ps -q --filter "name=alumno_proyecto1_stack_")
```

## 🎯 Beneficios

1. **Identificación inmediata** del dueño y proyecto
2. **Filtrado fácil** con `docker ps --filter`
3. **No hay colisiones** entre usuarios
4. **Debugging más rápido**
5. **Compatible con herramientas** (Portainer, etc.)

## ⚠️ Consideraciones

- **Límite**: 63 caracteres (Docker)
- **Caracteres permitidos**: a-z, A-Z, 0-9, `_`, `-`, `.`
- **Migración**: Aplicar solo a nuevos servicios (más seguro)

## 📝 Tareas

- [x] Crear función `_get_compose_project_name()` ✅
- [x] Actualizar `run_container()` (ya usaba `service.name`) ✅
- [x] Actualizar `run_compose()` (project name) ✅
- [x] Actualizar `stop_container()` ✅
- [x] Actualizar `remove_container()` ✅
- [x] Sanitización mejorada (sin guiones al inicio, sin múltiples guiones) ✅
- [ ] Actualizar tests (opcional)
- [ ] Documentar en guía de usuario (opcional)

---

## ✅ IMPLEMENTACIÓN COMPLETADA

**Fecha:** 17/12/2025 23:58

### Cambios Realizados

**Archivo:** `containers/services.py`

1. **Nueva función `_get_compose_project_name()`** (líneas 145-177):

   - Formato: `{usuario}_{proyecto}_{servicio}`
   - Sanitización mejorada:
     - Elimina guiones/guiones bajos al inicio y final
     - Reemplaza múltiples guiones consecutivos por uno solo
     - Convierte a minúsculas
     - Solo permite `a-z`, `0-9`, `_`, `-`
   - Fallback a `svc{id}` si falla

2. **Aplicado en 3 lugares**:

   - `run_compose()` - línea 632
   - `stop_container()` - línea 950
   - `remove_container()` - línea 1034

3. **Fix adicional**: Añadido `encoding='utf-8'` a subprocess (Mejora 2 del testing)

### Resultado

**Antes:**

```
Project name: svc100
Contenedores: svc100_web-1, svc100_redis-1
```

**Después:**

```
Project name: alumno_a1_prueba_2_prueba_dockercompose
Contenedores: alumno_a1_prueba_2_prueba_dockercompose_web-1, alumno_a1_prueba_2_prueba_dockercompose_redis-1
```

✅ **Verificado en Docker Desktop** - Funciona correctamente

---

**Reportado por:** Sistema  
**Implementado por:** Sistema  
**Etiquetas:** `feature-request`, `docker`, `compose`, `nomenclatura`, `completado`
