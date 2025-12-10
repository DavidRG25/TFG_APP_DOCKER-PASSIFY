# Plan de Testing y Mejoras Docker Compose
**Fecha**: 2025-11-28 18:56  
**Tipo**: Testing + Mejoras Críticas

---

## 🧪 PLAN DE TESTING

### **Test 1: Servicio Simple con Dockerfile**
**Objetivo**: Verificar funcionalidad básica

**Pasos**:
1. Crear servicio con Dockerfile personalizado
2. Subir código ZIP con `requirements.txt` y `app.py`
3. Hacer clic en "Iniciar"
4. **Verificar**:
   - [SI] Build exitoso
   - [SI] Contenedor inicia (estado RUNNING)
   - [SI] Nombre del contenedor es descriptivo (ej: `proyecto-nombre_ctr`)
   - [SI] Botón "Dockerfile" muestra contenido
   - [SI] Botón "Logs" muestra logs del build
   - [SOLUCION-FUTURA] Botón "Terminal" abre shell
   - [SI] Botón "Acceder" abre la aplicación
5. Hacer clic en "Detener"
6. **Verificar**:
   - [SI] Contenedor se detiene (estado STOPPED)
7. Hacer clic en "Eliminar"
8. **Verificar**:
   - [SI] Contenedor eliminado
   - [SI] Imagen eliminada de Docker
   - [SI] Volumen eliminado
   - [SI] Workspace limpiado

**Resultado Esperado**: ✅ Todo funciona sin errores

---

### **Test 2: Servicio Simple con Catálogo**
**Objetivo**: Verificar compatibilidad con imágenes del catálogo

**Pasos**:
1. Crear servicio con imagen `nginx:latest`
2. Hacer clic en "Iniciar"
3. **Verificar**:
   - [SI] Contenedor inicia
   - [SI] Nombre descriptivo
   - [SI] Terminal funciona
   - [SI] Acceder funciona
4. Detener y eliminar
5. **Verificar**:
   - [SI] Limpieza completa (NO debe eliminar imagen de catálogo)

**Resultado Esperado**: ✅ Funciona, imagen de catálogo NO se elimina

---

### **Test 3: Servicio Docker Compose (2 contenedores)**
**Objetivo**: Verificar multicontenedor básico

**Archivo `docker-compose.yml`**:
```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

**Pasos**:
1. Subir `docker-compose.yml` + código ZIP con Dockerfile
2. **ANTES de crear**:
   - [NO-IMPLEMENTADO] Sistema detecta 2 contenedores
   - [NO-IMPLEMENTADO] Muestra 2 campos de puerto personalizado
   - [NO-IMPLEMENTADO] Muestra 2 campos de puerto interno
3. Crear servicio
4. Hacer clic en "Iniciar servicio"
5. **Verificar**:
   - [SI] Ambos contenedores inician
   - [SI] NO aparece contenedor "principal"
   - [SI] Aparecen 2 tarjetas: "web" y "redis"
   - [SI] Nombres descriptivos en Docker Desktop
   - [SI] Botón "Compose" muestra YAML
6. **Por cada contenedor**:
   - [SI] Botón "Iniciar" funciona
   - [SI] Botón "Detener" funciona
   - [SI] Botón "Logs" muestra logs específicos
   - [SI] Botón "Terminal" abre shell del contenedor
   - [SI] Botón "Acceder" abre puerto correcto
7. Hacer clic en "Detener servicio"
8. **Verificar**:
   - [SI] AMBOS contenedores se detienen simultáneamente
   - [SI] Estado actualiza correctamente
9. Hacer clic en "Iniciar servicio"
10. **Verificar**:
    - [SI] AMBOS contenedores inician
    - [SI] Estado actualiza rápidamente
11. Hacer clic en "Eliminar"
12. **Verificar**:
    - [SI] Ambos contenedores eliminados
    - [SI] Imagen web eliminada
    - [SI] Volúmenes eliminados
    - [SI] Workspace limpiado

**Resultado Esperado**: ✅ Multicontenedor funciona perfectamente

---

### **Test 4: Docker Compose con 5 contenedores (límite)**
**Objetivo**: Verificar límite máximo

**Archivo `docker-compose.yml`**:
```yaml
services:
  web:
    build: .
  redis:
    image: redis:7
  db:
    image: postgres:15
  cache:
    image: memcached:1.6
  worker:
    build: .
    command: celery worker
```

**Pasos**:
1. Subir docker-compose con 5 servicios
2. **Verificar**:
   - [ ] Sistema detecta 5 contenedores
   - [ ] Permite crear servicio
3. Iniciar y verificar que todos funcionan

**Resultado Esperado**: ✅ 5 contenedores es el límite permitido

---

### **Test 5: Docker Compose con 6 contenedores (excede límite)**
**Objetivo**: Verificar validación de límite

**Pasos**:
1. Subir docker-compose con 6 servicios
2. **Verificar**:
   - [ ] Sistema detecta 6 contenedores
   - [ ] Muestra error: "Máximo 5 contenedores permitidos"
   - [ ] NO permite crear servicio

**Resultado Esperado**: ✅ Validación funciona

---

### **Test 6: Errores y Edge Cases**

**6.1 Dockerfile con error de sintaxis**:
- [ ] Muestra error de build en logs
- [ ] Estado = "error"
- [ ] Puertos liberados

**6.2 Docker Compose con servicio que falla**:
- [ ] Muestra error en logs
- [ ] Otros contenedores siguen funcionando

**6.3 Puerto ya en uso**:
- [ ] Muestra error claro
- [ ] Sugiere puerto alternativo

---

## 🔧 MEJORAS CRÍTICAS NECESARIAS

### **Mejora 1: Nombres de Contenedores Descriptivos**
**Problema**: `svc_88_dockerfile-default_ctr` no es descriptivo  
**Solución**: Usar nombre del proyecto/servicio

**Cambio en `services.py`**:
```python
# Antes:
container_name = f"svc_{service.id}_{slug}_ctr"

# Después:
container_name = f"{service.name or slug}_ctr"
# Ejemplo: "mi-proyecto_ctr"
```

**Prioridad**: 🔴 ALTA

---

### **Mejora 2: Fix UnicodeDecodeError en Subprocess**
**Problema**: Error de encoding en Windows  
**Solución**: Forzar UTF-8 en subprocess

**Cambio en `services.py`**:
```python
proc = subprocess.run(
    cmd,
    cwd=str(workspace),
    check=True,
    capture_output=True,
    text=True,
    encoding='utf-8',  # ← AÑADIR
    errors='replace'    # ← AÑADIR
)
```

**Prioridad**: 🔴 ALTA

---

### **Mejora 3: Botones Dockerfile/Compose Funcionales**
**Problema**: No muestran contenido  
**Diagnóstico**: Probablemente problema de modal o HTMX

**Solución**: Verificar que la modal existe en el template base

**Archivo**: `templates/base.html` o similar  
**Verificar**:
```html
<!-- Modal para código -->
<div class="modal fade" id="codeModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div id="code-body"></div>
    </div>
  </div>
</div>
```

**Prioridad**: 🟡 MEDIA

---

### **Mejora 4: UI Desplegable para Docker Compose**
**Problema**: No muestra tarjetas de contenedores  
**Causa**: Template no renderiza correctamente

**Verificar en `_service_rows.html`**:
- `{% if s.has_compose %}` está funcionando
- `s.containers.all` devuelve los ServiceContainer
- Tarjetas se renderizan correctamente

**Solución**: Añadir debug en template:
```django
{% if s.has_compose %}
  <p>DEBUG: has_compose = True</p>
  <p>DEBUG: containers count = {{ s.containers.all|length }}</p>
  {% for c in s.containers.all %}
    <p>DEBUG: container {{ c.name }}</p>
  {% endfor %}
{% endif %}
```

**Prioridad**: 🔴 ALTA

---

### **Mejora 5: Stop/Start Síncrono para Compose**
**Problema**: Detener solo detiene un contenedor, luego el otro  
**Solución**: Usar `docker compose stop` en lugar de detener individualmente

**Cambio en `services.py`**:
```python
def stop_container(service: Service):
    if service.has_compose:
        # Usar docker compose stop
        workspace = ensure_service_workspace(service)
        compose_path = workspace / "docker-compose.yml"
        project = f"svc{service.id}"
        cmd = _compose_cmd() + ["-p", project, "-f", str(compose_path), "stop"]
        subprocess.run(cmd, cwd=str(workspace), check=True)
        
        # Actualizar todos los ServiceContainer
        for sc in service.containers.all():
            sc.status = "stopped"
            sc.save()
        
        service.status = "stopped"
        service.save()
    else:
        # Modo simple (actual)
        ...
```

**Prioridad**: 🔴 ALTA

---

### **Mejora 6: Limpieza Completa al Eliminar**
**Problema**: Imágenes y volúmenes no se eliminan  
**Solución**: Usar `docker compose down --rmi local --volumes`

**Cambio en `services.py`**:
```python
def remove_container(service: Service):
    if service.has_compose:
        workspace = ensure_service_workspace(service)
        compose_path = workspace / "docker-compose.yml"
        project = f"svc{service.id}"
        
        # Eliminar todo: contenedores, imágenes locales, volúmenes
        cmd = _compose_cmd() + [
            "-p", project,
            "-f", str(compose_path),
            "down",
            "--rmi", "local",  # Solo imágenes construidas localmente
            "--volumes"         # Eliminar volúmenes
        ]
        subprocess.run(cmd, cwd=str(workspace), check=True)
        
        # Limpiar workspace
        cleanup_service_workspace(service)
        
        # Eliminar ServiceContainer records
        service.containers.all().delete()
        
        service.status = "removed"
        service.save()
    else:
        # Modo simple: eliminar imagen si fue construida
        if service.dockerfile:
            slug = _service_slug(service)
            image_tag = f"svc_{service.id}_{slug}_image"
            try:
                docker_client.images.remove(image_tag, force=True)
            except:
                pass
        
        # Resto del código actual...
```

**Prioridad**: 🟡 MEDIA

---

### **Mejora 7: Validación Pre-Deploy**
**Problema**: No detecta número de contenedores antes de crear  
**Solución**: Añadir validación en el formulario de creación

**Nuevo archivo**: `containers/validators.py`
```python
import yaml

def validate_compose_file(compose_file):
    """Valida docker-compose.yml antes de crear servicio"""
    try:
        data = yaml.safe_load(compose_file.read())
        compose_file.seek(0)  # Reset file pointer
        
        services = data.get('services', {})
        num_services = len(services)
        
        if num_services > 5:
            raise ValidationError(
                f"Máximo 5 contenedores permitidos. "
                f"Tu docker-compose tiene {num_services} servicios."
            )
        
        return services  # Retornar para usar en el formulario
    except yaml.YAMLError as e:
        raise ValidationError(f"Error en docker-compose.yml: {e}")
```

**Cambio en `serializers.py`**:
```python
def validate_compose(self, value):
    if value:
        from .validators import validate_compose_file
        services = validate_compose_file(value)
        # Guardar info para mostrar en UI
        self.context['compose_services'] = services
    return value
```

**Prioridad**: 🟡 MEDIA

---

### **Mejora 8: Campos de Puerto Dinámicos**
**Problema**: No muestra campos por contenedor  
**Solución**: JavaScript dinámico en el formulario

**Nuevo archivo**: `static/js/compose-form.js`
```javascript
// Al cargar docker-compose.yml
document.getElementById('id_compose').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  const text = await file.text();
  const data = jsyaml.load(text);
  const services = Object.keys(data.services || {});
  
  if (services.length > 5) {
    alert(`Máximo 5 contenedores. Tu compose tiene ${services.length}.`);
    e.target.value = '';
    return;
  }
  
  // Mostrar campos de puerto por servicio
  const portsContainer = document.getElementById('ports-container');
  portsContainer.innerHTML = '';
  
  services.forEach(svc => {
    portsContainer.innerHTML += `
      <div class="mb-3">
        <label>Puerto externo para ${svc}</label>
        <input type="number" name="port_${svc}" class="form-control">
      </div>
    `;
  });
});
```

**Prioridad**: 🟢 BAJA (nice to have)

---

## 📊 RESUMEN DE PRIORIDADES

### 🔴 ALTA (Hacer YA)
1. Nombres de contenedores descriptivos
2. Fix UnicodeDecodeError
3. UI desplegable para compose
4. Stop/Start síncrono

### 🟡 MEDIA (Hacer pronto)
5. Botones Dockerfile/Compose
6. Limpieza completa
7. Validación pre-deploy

### 🟢 BAJA (Opcional)
8. Campos de puerto dinámicos

---

## 📝 ORDEN DE IMPLEMENTACIÓN

1. **Fix UnicodeDecodeError** (5 min)
2. **Nombres descriptivos** (10 min)
3. **Stop/Start síncrono** (20 min)
4. **UI desplegable** (30 min)
5. **Limpieza completa** (15 min)
6. **Validación pre-deploy** (30 min)
7. **Botones Dockerfile/Compose** (20 min)

**Tiempo total estimado**: ~2.5 horas

---

**Última actualización**: 2025-11-28 18:56
