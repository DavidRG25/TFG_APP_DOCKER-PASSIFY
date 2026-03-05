# Bug Report - Rama: dev2

> Resumen: Imagenes Docker no se eliminan al borrar servicio personalizado

## 🐛 Bug detectado durante testing

**Fase de testing:** Test 3.x - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)
**Estado:** COMPLETADO

---

## 📋 Descripcion del problema

Al **eliminar un servicio** creado con **Dockerfile personalizado** o **docker-compose**, la imagen Docker construida **no se elimina**, quedando como imagen huerfana en el sistema.

### Comportamiento observado:

1. Usuario crea servicio con Dockerfile personalizado
2. Docker build crea imagen con tag: `svc_{id}_{slug}_image`
3. Usuario elimina el servicio
4. Se eliminan:
   - ✅ Contenedor
   - ✅ Volumen
   - ✅ Reserva de puerto
5. **NO se elimina:**
   - ❌ Imagen Docker construida
   - ❌ Archivos en `archivos_dockerfile/`

### Comportamiento esperado:

Al eliminar un servicio personalizado, deberia eliminarse:

- ✅ Contenedor
- ✅ Volumen
- ✅ Puerto reservado
- ✅ **Imagen Docker construida** (si es personalizada)
- ✅ **Archivos subidos** (Dockerfile, compose, code)

---

## 🔍 Causa raiz

En `containers/services.py`, funcion `remove_container` (lineas 517-551):

```python
def remove_container(service: Service):
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no esta disponible para eliminar el servicio.")

    # Eliminar contenedor principal
    if service.container_id:
        try:
            container = docker_client.containers.get(service.container_id)
            container.remove(force=True)
        except NotFound:
            pass
        except DockerException as exc:
            _append_log(service, f"Error al eliminar el contenedor: {exc}")
            service.save(update_fields=["logs"])

    # Liberar puertos
    _release_port(service.assigned_port)

    # Eliminar volumen
    if service.volume_name:
        try:
            volume = docker_client.volumes.get(service.volume_name)
            volume.remove(force=True)
        except NotFound:
            pass
        except DockerException as exc:
            _append_log(service, f"Error al eliminar el volumen: {exc}")
            service.save(update_fields=["logs"])

    # ❌ FALTA: Eliminar imagen personalizada
    # ❌ FALTA: Eliminar archivos subidos

    service.container_id = None
    service.assigned_port = None
    service.volume_name = None
    service.status = "removed"
    service.save()
```

**Problema:** No hay logica para:

1. Detectar si el servicio tiene imagen personalizada
2. Eliminar la imagen Docker construida
3. Eliminar archivos subidos (Dockerfile, compose, code)

---

## 💡 Solucion propuesta

### Paso 1: Eliminar imagen Docker personalizada

Agregar logica para eliminar imagenes construidas con Dockerfile:

```python
def remove_container(service: Service):
    docker_client = get_docker_client()
    if docker_client is None:
        raise RuntimeError("Docker no esta disponible para eliminar el servicio.")

    # ... codigo existente para contenedor y volumen ...

    # Eliminar imagen personalizada (si existe)
    if service.dockerfile:
        slug = _service_slug(service)
        image_tag = f"svc_{service.id}_{slug}_image"
        try:
            docker_client.images.remove(image_tag, force=True)
            _append_log(service, f"Imagen personalizada '{image_tag}' eliminada.")
        except NotFound:
            pass  # La imagen ya no existe
        except DockerException as exc:
            _append_log(service, f"Error al eliminar imagen: {exc}")
            service.save(update_fields=["logs"])

    # Eliminar imagenes de docker-compose (si existen)
    if service.compose:
        project = f"svc{service.id}"
        try:
            # Listar imagenes del proyecto compose
            images = docker_client.images.list(filters={"label": f"com.docker.compose.project={project}"})
            for img in images:
                try:
                    docker_client.images.remove(img.id, force=True)
                except DockerException:
                    pass
        except DockerException as exc:
            _append_log(service, f"Error al eliminar imagenes de compose: {exc}")
            service.save(update_fields=["logs"])

    # ... resto del codigo ...
```

### Paso 2: Eliminar archivos subidos

Los archivos se guardan en `MEDIA_ROOT` via FileField. Django los elimina automaticamente al hacer `service.delete()`, pero si quieres forzarlo:

```python
# Eliminar archivos subidos
if service.dockerfile:
    service.dockerfile.delete(save=False)
if service.compose:
    service.compose.delete(save=False)
if service.code:
    service.code.delete(save=False)
```

**Nota:** Esto ya deberia ocurrir automaticamente cuando se elimina el objeto Service, pero es buena practica hacerlo explicito.

---

## 📊 Impacto

### Problema actual:

Cada servicio personalizado deja una imagen huerfana:

- **Espacio en disco:** 100MB - 1GB por imagen (dependiendo del Dockerfile)
- **Acumulacion:** Si se crean/eliminan muchos servicios, el disco se llena
- **Confusion:** `docker images` muestra muchas imagenes sin usar

### Ejemplo:

Despues de crear y eliminar 10 servicios con nginx personalizado:

```bash
$ docker images
REPOSITORY                    TAG       SIZE
svc_1_prueba-nginx_image     latest    150MB
svc_2_test-web_image         latest    145MB
svc_3_mi-servidor_image      latest    148MB
...
# 10 imagenes huerfanas = ~1.5GB de espacio perdido
```

### Severidad:

- **Alta:** Puede llenar el disco en entornos de produccion
- **Media:** En desarrollo/testing es molesto pero manejable

---

## 🎯 Recomendacion

**Implementar limpieza completa en `remove_container`:**

1. ✅ Eliminar contenedor (ya existe)
2. ✅ Eliminar volumen (ya existe)
3. ✅ Liberar puerto (ya existe)
4. ➕ **Eliminar imagen personalizada** (nuevo)
5. ➕ **Eliminar imagenes de compose** (nuevo)
6. ➕ **Eliminar archivos subidos** (opcional, Django lo hace automaticamente)

**Prioridad:** Alta (afecta espacio en disco)

---

## 📝 Pasos para reproducir

1. Login como alumno
2. Crear servicio con Dockerfile personalizado
3. Esperar a que se construya la imagen
4. Verificar imagen creada: `docker images | grep svc_`
5. Eliminar el servicio desde el panel
6. Verificar que la imagen sigue existiendo: `docker images | grep svc_`
7. **Resultado:** Imagen huerfana presente

---

## 🔧 Archivos afectados

- `containers/services.py` (funcion `remove_container`, lineas 517-551)

---

## 📌 Notas adicionales

### Caso especial: docker-compose

Para docker-compose, las imagenes tienen labels del proyecto:

```
com.docker.compose.project=svc{id}
```

Se pueden eliminar filtrando por este label.

### Workaround actual:

Limpiar manualmente con:

```bash
# Eliminar imagenes huerfanas
docker image prune -a

# O especificamente las de servicios
docker images | grep "svc_.*_image" | awk '{print $3}' | xargs docker rmi -f
```

---

**Estado:** COMPLETADO  
**Asignado a:** Por definir  
**Relacionado con:** Plan de Testing Admin - Fase 3  
**Relacionado con:** Bug logs vacios Dockerfile
