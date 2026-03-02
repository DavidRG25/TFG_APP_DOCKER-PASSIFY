# Plan de Implementación: Funcionalidades Extra por Tipo de Imagen

**Fecha:** 2025-11-25 19:45  
**Versión:** 4.3.0  
**Estado:** 📋 Planificación

---

## 🎯 Objetivo

Implementar funcionalidades **EXTRA** y **ADITIVAS** en el panel del alumno según el tipo de imagen del servicio, **SIN MODIFICAR** las funcionalidades base existentes.

---

## ⚠️ Reglas Fundamentales

### 1. **NO TOCAR Funcionalidades Base**
El panel del alumno SIEMPRE debe mantener:
- ✅ Iniciar / Detener / Eliminar
- ✅ Logs
- ✅ Acceder (puerto)
- ✅ Terminal
- ✅ Información de puerto y estado

**Estas funciones son OBLIGATORIAS y NO se modifican.**

### 2. **Funcionalidades Extra son ADITIVAS**
- Se muestran como **botones extra** o **secciones extra**
- Solo aparecen si el servicio usa una `AllowedImage` con `image_type` específico
- Si la imagen es `misc` o no está en `AllowedImage`, solo se muestran funciones base

### 3. **Compatibilidad Total**
- Nada del panel actual puede romperse
- Imágenes `misc` funcionan exactamente como antes
- Todas las funcionalidades extra son opcionales

---

## 📦 Funcionalidades Extra por Tipo

### 🌐 Tipo: Web / Frontend
**Imágenes:** nginx, apache, httpd

**Funcionalidades Extra:**
1. **Botón "📝 Editar HTML/CSS/JS"**
   - Abre editor de código integrado
   - Permite editar archivos en `/usr/share/nginx/html/` o `/var/www/html/`
   - Guarda cambios en tiempo real

2. **Botón "📁 Subir Archivos Web"**
   - Permite subir archivos .html, .css, .js, imágenes
   - Los copia a la carpeta web del contenedor
   - Muestra lista de archivos actuales

**Ubicación en UI:**
```
┌─────────────────────────────────────┐
│ [Iniciar] [Detener] [Eliminar]     │ ← Funciones base (siempre)
│ [Logs] [Acceder] [Terminal]        │
├─────────────────────────────────────┤
│ 🌐 Funcionalidades Web              │ ← Sección extra (solo si type=web)
│ [📝 Editar HTML/CSS/JS]             │
│ [📁 Subir Archivos Web]             │
└─────────────────────────────────────┘
```

---

### 🗄️ Tipo: Base de Datos
**Imágenes:** mysql, postgres, mongo, redis

**Funcionalidades Extra:**
1. **Botón "🔐 Configurar Credenciales"**
   - Modal para configurar usuario/contraseña
   - Actualiza variables de entorno del contenedor
   - Reinicia el servicio si es necesario

2. **Botón "💾 Cliente de Base de Datos"**
   - Abre terminal preconfigurada con cliente (mysql, psql, mongosh, redis-cli)
   - Conecta automáticamente con las credenciales configuradas

3. **Botón "📊 Ver Estadísticas"**
   - Muestra uso de memoria, conexiones activas
   - Tamaño de la base de datos

**Ubicación en UI:**
```
┌─────────────────────────────────────┐
│ [Iniciar] [Detener] [Eliminar]     │ ← Funciones base (siempre)
│ [Logs] [Acceder] [Terminal]        │
├─────────────────────────────────────┤
│ 🗄️ Funcionalidades Base de Datos   │ ← Sección extra (solo si type=database)
│ [🔐 Configurar Credenciales]        │
│ [💾 Cliente de Base de Datos]       │
│ [📊 Ver Estadísticas]               │
└─────────────────────────────────────┘
```

---

### 🚀 Tipo: Generador de API
**Imágenes:** strapi, hasura, postgrest, fastapi, express

**Funcionalidades Extra:**
1. **Botón "🏗️ Generar Estructura Base"**
   - Crea estructura de carpetas para API
   - Genera archivos base (routes, controllers, models)
   - Configura dependencias básicas

2. **Botón "✏️ Editor de API"**
   - Editor de código para rutas y endpoints
   - Sintaxis highlighting según framework
   - Hot reload automático

3. **Botón "🔍 Ver Rutas Expuestas"**
   - Lista todas las rutas/endpoints disponibles
   - Muestra métodos HTTP (GET, POST, PUT, DELETE)
   - Permite probar endpoints directamente

4. **Botón "📚 Documentación API"**
   - Genera documentación automática (Swagger/OpenAPI)
   - Muestra ejemplos de uso

**Ubicación en UI:**
```
┌─────────────────────────────────────┐
│ [Iniciar] [Detener] [Eliminar]     │ ← Funciones base (siempre)
│ [Logs] [Acceder] [Terminal]        │
├─────────────────────────────────────┤
│ 🚀 Funcionalidades Generador de API │ ← Sección extra (solo si type=api)
│ [🏗️ Generar Estructura Base]        │
│ [✏️ Editor de API]                  │
│ [🔍 Ver Rutas Expuestas]            │
│ [📚 Documentación API]              │
└─────────────────────────────────────┘
```

---

### 📦 Tipo: Miscelánea
**Imágenes:** python, node, cualquier otra

**Funcionalidades Extra:**
- **Ninguna**
- Solo muestra funciones base
- Comportamiento idéntico al actual

**Ubicación en UI:**
```
┌─────────────────────────────────────┐
│ [Iniciar] [Detener] [Eliminar]     │ ← Funciones base (siempre)
│ [Logs] [Acceder] [Terminal]        │
└─────────────────────────────────────┘
```

---

## 🏗️ Arquitectura de Implementación

### 1. **Detección del Tipo de Imagen**

**En la vista `student_panel`:**
```python
def student_panel(request):
    services = Service.objects.filter(owner=request.user)
    
    # Para cada servicio, detectar tipo de imagen
    for service in services:
        service.extra_features = get_service_extra_features(service)
    
    return render(request, 'student_panel.html', {'services': services})
```

**Función auxiliar:**
```python
def get_service_extra_features(service):
    """
    Retorna las funcionalidades extra disponibles para un servicio.
    """
    try:
        # Extraer nombre e imagen del servicio
        image_name = service.image.split(':')[0]
        image_tag = service.image.split(':')[1] if ':' in service.image else 'latest'
        
        # Buscar en AllowedImage
        allowed_image = AllowedImage.objects.get(name=image_name, tag=image_tag)
        
        # Retornar tipo
        return {
            'type': allowed_image.image_type,
            'has_extras': allowed_image.image_type != 'misc',
            'icon': get_icon_for_type(allowed_image.image_type),
            'features': get_features_for_type(allowed_image.image_type)
        }
    except AllowedImage.DoesNotExist:
        # Si no está en AllowedImage, tratar como misc
        return {
            'type': 'misc',
            'has_extras': False,
            'icon': '📦',
            'features': []
        }
```

---

### 2. **Template Mejorado**

**En `student_panel.html`:**
```django
{% for service in services %}
<div class="card service-card">
  <div class="card-header">
    <h5>{{ service.name }}</h5>
    <span class="badge">{{ service.status }}</span>
  </div>
  
  <div class="card-body">
    <!-- FUNCIONES BASE (SIEMPRE PRESENTES) -->
    <div class="base-actions">
      <button class="btn btn-success" onclick="startService({{ service.id }})">
        <i class="fas fa-play"></i> Iniciar
      </button>
      <button class="btn btn-warning" onclick="stopService({{ service.id }})">
        <i class="fas fa-stop"></i> Detener
      </button>
      <button class="btn btn-danger" onclick="deleteService({{ service.id }})">
        <i class="fas fa-trash"></i> Eliminar
      </button>
      <button class="btn btn-info" onclick="viewLogs({{ service.id }})">
        <i class="fas fa-file-alt"></i> Logs
      </button>
      <button class="btn btn-primary" onclick="accessService({{ service.id }})">
        <i class="fas fa-external-link-alt"></i> Acceder
      </button>
      <button class="btn btn-secondary" onclick="openTerminal({{ service.id }})">
        <i class="fas fa-terminal"></i> Terminal
      </button>
    </div>
    
    <!-- FUNCIONES EXTRA (SOLO SI TIENE) -->
    {% if service.extra_features.has_extras %}
    <hr>
    <div class="extra-features">
      <h6>{{ service.extra_features.icon }} Funcionalidades {{ service.extra_features.type|title }}</h6>
      
      {% if service.extra_features.type == 'web' %}
        <button class="btn btn-outline-primary" onclick="editWebFiles({{ service.id }})">
          📝 Editar HTML/CSS/JS
        </button>
        <button class="btn btn-outline-primary" onclick="uploadWebFiles({{ service.id }})">
          📁 Subir Archivos Web
        </button>
      {% endif %}
      
      {% if service.extra_features.type == 'database' %}
        <button class="btn btn-outline-success" onclick="configureCredentials({{ service.id }})">
          🔐 Configurar Credenciales
        </button>
        <button class="btn btn-outline-success" onclick="openDbClient({{ service.id }})">
          💾 Cliente de Base de Datos
        </button>
        <button class="btn btn-outline-success" onclick="viewDbStats({{ service.id }})">
          📊 Ver Estadísticas
        </button>
      {% endif %}
      
      {% if service.extra_features.type == 'api' %}
        <button class="btn btn-outline-warning" onclick="generateApiStructure({{ service.id }})">
          🏗️ Generar Estructura Base
        </button>
        <button class="btn btn-outline-warning" onclick="editApi({{ service.id }})">
          ✏️ Editor de API
        </button>
        <button class="btn btn-outline-warning" onclick="viewRoutes({{ service.id }})">
          🔍 Ver Rutas Expuestas
        </button>
        <button class="btn btn-outline-warning" onclick="viewApiDocs({{ service.id }})">
          📚 Documentación API
        </button>
      {% endif %}
    </div>
    {% endif %}
  </div>
</div>
{% endfor %}
```

---

### 3. **Endpoints API para Funcionalidades Extra**

**Nuevos endpoints en `containers/views.py`:**

```python
# Web Features
@login_required
def edit_web_files(request, service_id):
    """Editor de archivos HTML/CSS/JS"""
    pass

@login_required
def upload_web_files(request, service_id):
    """Subir archivos web al contenedor"""
    pass

# Database Features
@login_required
def configure_db_credentials(request, service_id):
    """Configurar credenciales de base de datos"""
    pass

@login_required
def open_db_client(request, service_id):
    """Abrir cliente de base de datos"""
    pass

# API Features
@login_required
def generate_api_structure(request, service_id):
    """Generar estructura base de API"""
    pass

@login_required
def edit_api(request, service_id):
    """Editor de API"""
    pass

@login_required
def view_api_routes(request, service_id):
    """Ver rutas expuestas de la API"""
    pass
```

---

## 📋 Orden de Implementación

### Fase 1: Preparación (Completada ✅)
- [x] Actualizar modelo AllowedImage con `image_type`
- [x] Crear migración
- [x] Actualizar admin con iconos y filtros
- [x] Crear comando `populate_example_images`

### Fase 2: Detección de Tipo (Próxima)
- [ ] Crear función `get_service_extra_features()`
- [ ] Modificar vista `student_panel` para agregar info de tipo
- [ ] Probar detección con imágenes de ejemplo

### Fase 3: UI - Funciones Web
- [ ] Agregar sección extra en template
- [ ] Implementar botón "Editar HTML/CSS/JS"
- [ ] Implementar botón "Subir Archivos Web"
- [ ] Crear editor de código (Monaco Editor o CodeMirror)

### Fase 4: UI - Funciones Database
- [ ] Implementar botón "Configurar Credenciales"
- [ ] Implementar botón "Cliente de Base de Datos"
- [ ] Implementar botón "Ver Estadísticas"

### Fase 5: UI - Funciones API
- [ ] Implementar botón "Generar Estructura Base"
- [ ] Implementar botón "Editor de API"
- [ ] Implementar botón "Ver Rutas Expuestas"
- [ ] Implementar botón "Documentación API"

### Fase 6: Testing
- [ ] Probar con imagen Web (nginx)
- [ ] Probar con imagen Database (mysql)
- [ ] Probar con imagen API (strapi)
- [ ] Probar con imagen Misc (python)
- [ ] Verificar que funciones base siguen funcionando

---

## 🧪 Casos de Prueba

### Caso 1: Servicio con Imagen Web
```
Servicio: nginx:latest
Tipo detectado: web
Funciones base: ✅ Todas presentes
Funciones extra: ✅ Editar HTML/CSS/JS, Subir Archivos
```

### Caso 2: Servicio con Imagen Database
```
Servicio: mysql:latest
Tipo detectado: database
Funciones base: ✅ Todas presentes
Funciones extra: ✅ Configurar Credenciales, Cliente DB, Estadísticas
```

### Caso 3: Servicio con Imagen API
```
Servicio: strapi/strapi:latest
Tipo detectado: api
Funciones base: ✅ Todas presentes
Funciones extra: ✅ Generar Estructura, Editor, Ver Rutas, Docs
```

### Caso 4: Servicio con Imagen Misc
```
Servicio: python:3.12
Tipo detectado: misc
Funciones base: ✅ Todas presentes
Funciones extra: ❌ Ninguna (comportamiento actual)
```

### Caso 5: Servicio con Imagen No en AllowedImage
```
Servicio: custom-image:1.0
Tipo detectado: misc (fallback)
Funciones base: ✅ Todas presentes
Funciones extra: ❌ Ninguna (comportamiento actual)
```

---

## 📝 Notas Importantes

1. **Retrocompatibilidad Total:**
   - Todos los servicios existentes siguen funcionando
   - Imágenes no clasificadas se tratan como `misc`
   - Ninguna función base se elimina o modifica

2. **Progresividad:**
   - Se pueden implementar las funcionalidades extra de forma incremental
   - Empezar por tipo Web (más simple)
   - Luego Database, luego API

3. **Futuro:**
   - Selector de tags con paginación (pendiente)
   - Más tipos de imagen si es necesario
   - Más funcionalidades extra por tipo

---

**Fecha de creación:** 2025-11-25 19:45  
**Versión:** 4.3.0  
**Estado:** 📋 Planificación completa, listo para implementación
