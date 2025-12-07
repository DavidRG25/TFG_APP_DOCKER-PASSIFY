# Feature Request - Rama: dev2
> Resumen: Permitir actualizar codigo fuente sin redesplegar contenedor

## 🟡 Feature Request detectado durante testing

**Fase de testing:** Test 3.x - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)  
**Tipo:** UX Improvement / Missing Feature

---

## 📋 Descripcion del problema

Si un usuario sube un **codigo fuente (.zip/.rar)** y luego quiere **actualizarlo** (ej: corregir un bug, agregar funcionalidad), debe **redesplegar el contenedor completo**, lo cual es lento e ineficiente.

### Escenario actual:

1. Usuario crea servicio con Dockerfile + codigo.zip
2. Contenedor se construye y arranca
3. Usuario encuentra un bug en el codigo
4. Corrige el bug localmente
5. **Debe eliminar y recrear el servicio completo** para subir el nuevo codigo
6. Proceso completo: 2-5 minutos (build + deploy)

### Comportamiento esperado:

Deberia existir una opcion para **actualizar solo el codigo fuente** sin redesplegar:

1. Usuario hace click en "Actualizar codigo"
2. Sube nuevo archivo .zip
3. Sistema:
   - Descomprime nuevo codigo en el volumen del contenedor
   - Reinicia el contenedor (o hot-reload si es posible)
4. Tiempo: 10-30 segundos

---

## 🔍 Analisis tecnico

### Arquitectura actual:

El codigo fuente se descomprime durante el **build** del contenedor:

```python
# En _run_container_internal (services.py, linea 352-353)
if service.code:
    _unpack_code_archive_to(builddir, service.code)
```

**Problema:** El codigo queda **dentro de la imagen Docker**, no en un volumen accesible.

### Solucion tecnica:

Para permitir actualizacion de codigo sin rebuild, el codigo debe estar en un **volumen montado**:

```
Contenedor:
  /app  →  Volumen: svc_{id}_code
```

De esta forma:
1. Codigo esta en volumen (no en imagen)
2. Se puede actualizar el volumen sin tocar el contenedor
3. Reiniciar contenedor carga el nuevo codigo

---

## 💡 Solucion propuesta

### Opcion A: Volumen de codigo + Boton "Actualizar codigo" (RECOMENDADA)

**Cambios en arquitectura:**

1. **Crear volumen separado para codigo:**
   ```python
   code_volume = f"svc_{service.id}_{slug}_code"
   volumes = {
       volume_name: {"bind": "/data", "mode": "rw"},
       code_volume: {"bind": "/app", "mode": "rw"}  # Nuevo
   }
   ```

2. **Descomprimir codigo en volumen (no en imagen):**
   ```python
   # Despues de crear el contenedor
   _unpack_code_to_volume(docker_client, code_volume, service.code)
   ```

3. **Nueva funcion para actualizar codigo:**
   ```python
   def update_service_code(service: Service, new_code_file):
       """
       Actualiza el codigo fuente sin redesplegar el contenedor.
       """
       docker_client = get_docker_client()
       code_volume = f"svc_{service.id}_{_service_slug(service)}_code"
       
       # Limpiar volumen
       _clear_volume(docker_client, code_volume)
       
       # Descomprimir nuevo codigo
       _unpack_code_to_volume(docker_client, code_volume, new_code_file)
       
       # Reiniciar contenedor para cargar nuevo codigo
       if service.container_id:
           container = docker_client.containers.get(service.container_id)
           container.restart()
       
       # Actualizar archivo en BD
       service.code = new_code_file
       service.save()
   ```

**UI propuesta:**

```html
<!-- En el panel del servicio -->
<div class="code-section">
    <h4>Codigo fuente</h4>
    <p>Archivo actual: <code>{{ service.code.name }}</code></p>
    
    <button class="btn btn-primary" data-toggle="modal" data-target="#updateCodeModal">
        📦 Actualizar codigo
    </button>
</div>

<!-- Modal -->
<div class="modal" id="updateCodeModal">
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="new_code" accept=".zip,.rar">
        <button type="submit">Subir y actualizar</button>
    </form>
</div>
```

**Ventajas:**
- ✅ Actualizacion rapida (10-30 segundos vs 2-5 minutos)
- ✅ No se pierde configuracion
- ✅ No se reconstruye imagen
- ✅ Ideal para desarrollo iterativo

**Desventajas:**
- ⚠️ Requiere cambio en arquitectura (volumenes)
- ⚠️ Compatibilidad: solo funciona si el codigo esta en volumen

### Opcion B: Hot-reload automatico (AVANZADA)

Para frameworks que soportan hot-reload (Node.js, Python Flask/Django):

1. Montar codigo en volumen
2. Configurar watcher en el contenedor
3. Codigo se recarga automaticamente al detectar cambios

**Ejemplo con Node.js:**
```dockerfile
FROM node:latest
WORKDIR /app
VOLUME /app
CMD ["nodemon", "index.js"]  # nodemon detecta cambios
```

**Ventajas:**
- ✅ Desarrollo super rapido
- ✅ No requiere reiniciar manualmente

**Desventajas:**
- ⚠️ Solo funciona con frameworks compatibles
- ⚠️ Mas complejo de configurar

### Opcion C: Rebuild rapido (HIBRIDA)

Optimizar el rebuild para que sea mas rapido:

1. Cachear layers de Docker
2. Solo reconstruir layer de codigo
3. Usar multi-stage builds

**Ventajas:**
- ✅ No requiere cambios grandes
- ✅ Compatible con arquitectura actual

**Desventajas:**
- ⚠️ Sigue siendo mas lento que actualizar volumen
- ⚠️ Requiere Dockerfile optimizado

---

## 🎯 Recomendacion

**Implementar Opcion A (Volumen de codigo + Boton actualizar):**

**Fase 1 (Corto plazo):**
1. Modificar `_run_container_internal` para usar volumen de codigo
2. Agregar funcion `update_service_code()`
3. Agregar boton "Actualizar codigo" en UI

**Fase 2 (Medio plazo):**
4. Agregar soporte para hot-reload (Opcion B) para frameworks compatibles
5. Detectar automaticamente si el framework soporta hot-reload

**Prioridad:** Media-Alta (mejora significativa de UX para desarrollo)

---

## 📝 Pasos para reproducir

1. Login como alumno
2. Crear servicio con Dockerfile + codigo.zip
3. Esperar a que se construya (2-5 min)
4. Encontrar bug en el codigo
5. Corregir bug localmente
6. Intentar actualizar codigo
7. **Resultado:** No hay opcion, debe eliminar y recrear servicio

---

## 📊 Impacto

### Usuarios afectados:
- ✅ Alumnos desarrollando aplicaciones web
- ✅ Alumnos probando/debugeando codigo
- ✅ Profesores revisando trabajos de alumnos

### Severidad:
- **Media-Alta:** Workaround existe pero es muy lento e ineficiente

### Workaround actual:
1. Eliminar servicio
2. Crear nuevo servicio
3. Subir nuevo codigo
4. Esperar rebuild completo (2-5 min)
5. **Problema:** Muy lento para desarrollo iterativo

### Beneficio de la mejora:

**Antes:**
- Cambio de codigo → 2-5 minutos (rebuild completo)
- 10 cambios → 20-50 minutos perdidos

**Despues:**
- Cambio de codigo → 10-30 segundos (solo actualizar volumen)
- 10 cambios → 2-5 minutos total
- **Ahorro:** 15-45 minutos por sesion de desarrollo

---

## 🔧 Archivos afectados

- `containers/services.py`:
  - Modificar `_run_container_internal` (agregar volumen de codigo)
  - Nueva funcion `update_service_code()`
  - Nueva funcion `_unpack_code_to_volume()`
  - Nueva funcion `_clear_volume()`

- `paasify/views.py`:
  - Nueva vista `update_service_code_view()`

- `paasify/templates/paasify/services.html`:
  - Boton "Actualizar codigo"
  - Modal para subir nuevo archivo

- `paasify/urls.py`:
  - Nueva ruta para actualizar codigo

---

## 📌 Notas adicionales

### Implementacion sugerida de funciones auxiliares:

```python
def _unpack_code_to_volume(docker_client, volume_name, code_file):
    """
    Descomprime codigo en un volumen Docker.
    """
    # Crear contenedor temporal para acceder al volumen
    container = docker_client.containers.run(
        "alpine:latest",
        command="sleep 3600",
        volumes={volume_name: {"bind": "/code", "mode": "rw"}},
        detach=True
    )
    
    try:
        # Descomprimir codigo localmente
        with tempfile.TemporaryDirectory() as tmpdir:
            _unpack_code_archive_to(tmpdir, code_file)
            
            # Copiar al volumen via contenedor temporal
            import tarfile
            tar_path = f"{tmpdir}/code.tar"
            with tarfile.open(tar_path, "w") as tar:
                tar.add(tmpdir, arcname=".")
            
            with open(tar_path, "rb") as tar_file:
                container.put_archive("/code", tar_file.read())
    finally:
        container.remove(force=True)

def _clear_volume(docker_client, volume_name):
    """
    Limpia el contenido de un volumen Docker.
    """
    container = docker_client.containers.run(
        "alpine:latest",
        command="sh -c 'rm -rf /code/*'",
        volumes={volume_name: {"bind": "/code", "mode": "rw"}},
        remove=True
    )
```

### Consideraciones de seguridad:

1. **Validar archivo:**
   - Verificar extension (.zip, .rar)
   - Verificar tamano maximo
   - Escanear contenido (opcional)

2. **Permisos:**
   - Solo el owner del servicio puede actualizar codigo
   - Verificar autenticacion

3. **Backup:**
   - Opcional: guardar version anterior del codigo
   - Permitir rollback si algo falla

---

**Estado:** 🟡 Feature Request  
**Asignado a:** Por definir  
**Relacionado con:** Feature cambiar puerto interno  
**Relacionado con:** Plan de Testing Admin - Fase 3
