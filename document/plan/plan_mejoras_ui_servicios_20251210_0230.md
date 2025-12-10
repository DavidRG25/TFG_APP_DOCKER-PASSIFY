# Plan de Mejoras UI - Servicios y API
**Fecha creación**: 2025-12-09  
**Prioridad**: MEDIA  
**Estado**: PENDIENTE

---

## 🎯 OBJETIVO

Mejorar la experiencia de usuario al crear servicios y proporcionar capacidades de despliegue vía API/comandos para integración continua.

---

## 📋 FASE 1: Página Dedicada "Nuevo Servicio"

### **Objetivo:**
Convertir el modal actual en una página dedicada con mejor organización y más espacio.

### **Tareas:**

#### **1.1 Crear nueva vista y template**
- [ ] Crear vista `new_service_page` en `containers/views.py`
- [ ] Crear template `containers/new_service.html`
- [ ] Añadir ruta en `containers/urls.py`

**Archivo**: `containers/views.py`
```python
@login_required
def new_service_page(request):
    """Página dedicada para crear nuevo servicio"""
    if request.method == "POST":
        # Lógica de creación (reutilizar del modal)
        pass
    
    images = AllowedImage.objects.all()
    subjects = Subject.objects.filter(students=request.user)
    
    return render(request, "containers/new_service.html", {
        "images": images,
        "subjects": subjects,
    })
```

#### **1.2 Diseñar layout de 2 columnas**
- [ ] Columna izquierda: Formulario
- [ ] Columna derecha: Ayuda contextual / Preview
- [ ] Breadcrumbs: Inicio > Servicios > Nuevo Servicio
- [ ] Botones: Cancelar (volver) / Crear Servicio

**Estructura propuesta**:
```
┌─────────────────────────────────────────────────┐
│ Breadcrumb: Inicio > Servicios > Nuevo Servicio│
└─────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────┐
│  FORMULARIO          │  AYUDA / PREVIEW         │
│                      │                          │
│ □ Nombre             │ 💡 Consejos:             │
│ □ Asignatura         │ - Usa nombres cortos     │
│ □ Tipo despliegue    │ - Sin espacios           │
│   ○ Default          │                          │
│   ○ Custom           │ 📄 Preview Dockerfile:   │
│                      │ [código preview]         │
│ □ Imagen/Dockerfile  │                          │
│ □ Puertos            │                          │
│ □ Código fuente      │                          │
│                      │                          │
│ [Cancelar] [Crear]   │                          │
└──────────────────────┴──────────────────────────┘
```

#### **1.3 Mejorar validación y feedback**
- [ ] Validación en tiempo real (HTMX)
- [ ] Mensajes de error más claros
- [ ] Preview del Dockerfile antes de crear
- [ ] Indicador de progreso al crear

#### **1.4 Actualizar navegación**
- [ ] Cambiar botón "Nuevo servicio" para redirigir a página
- [ ] Añadir enlace en menú lateral (opcional)

**Estimación**: 4-6 horas

---

## 📋 FASE 2: Sistema de API REST con Tokens

### **Objetivo:**
Permitir a los alumnos crear/gestionar servicios vía API REST usando tokens de autenticación.

### **Tareas:**

#### **2.1 Implementar sistema de tokens**
- [ ] Instalar `djangorestframework.authtoken`
- [ ] Crear modelo de token o usar Token de DRF
- [ ] Migración de base de datos

**Archivo**: `settings.py`
```python
INSTALLED_APPS += [
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

#### **2.2 Crear endpoints API**
- [ ] Crear `containers/api_views.py`
- [ ] Endpoints:
  - `POST /api/services/` - Crear servicio
  - `GET /api/services/` - Listar servicios
  - `GET /api/services/{id}/` - Detalle servicio
  - `PUT /api/services/{id}/` - Actualizar servicio
  - `DELETE /api/services/{id}/` - Eliminar servicio
  - `POST /api/services/{id}/start/` - Iniciar
  - `POST /api/services/{id}/stop/` - Detener

**Archivo**: `containers/api_views.py`
```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class ServiceAPIViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        return Service.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        service = self.get_object()
        run_container(service)
        return Response({'status': 'started'})
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        service = self.get_object()
        stop_container(service)
        return Response({'status': 'stopped'})
```

#### **2.3 Gestión de tokens en UI**
- [ ] Vista para generar/regenerar token
- [ ] Mostrar token en perfil de usuario
- [ ] Botón "Copiar token"
- [ ] Advertencia de seguridad

**Archivo**: `containers/views.py`
```python
@login_required
def manage_api_token(request):
    """Gestionar token API del usuario"""
    if request.method == "POST":
        # Regenerar token
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
    else:
        token, created = Token.objects.get_or_create(user=request.user)
    
    return render(request, "containers/api_token.html", {
        "token": token.key
    })
```

**Estimación**: 6-8 horas

---

## 📋 FASE 3: Página de Documentación API

### **Objetivo:**
Crear una página dedicada con documentación completa de la API y ejemplos de comandos curl.

### **Tareas:**

#### **3.1 Crear página de documentación**
- [ ] Crear template `containers/api_docs.html`
- [ ] Vista `api_documentation`
- [ ] Añadir ruta

**Estructura propuesta**:
```
┌─────────────────────────────────────────────────┐
│ 🔑 Tu Token de API                              │
│ ┌─────────────────────────────────────────────┐ │
│ │ eyJhbGc...  [📋 Copiar] [🔄 Regenerar]      │ │
│ └─────────────────────────────────────────────┘ │
│ ⚠️ Mantén tu token seguro. No lo compartas.     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 📚 Documentación de la API                      │
│                                                 │
│ Base URL: https://paasify.com/api/             │
│ Autenticación: Bearer Token                     │
└─────────────────────────────────────────────────┘

▼ Crear Servicio
  POST /api/services/
  
  Ejemplo:
  ┌───────────────────────────────────────────────┐
  │ curl --request POST \                         │
  │   https://paasify.com/api/services/ \         │
  │   --header 'Authorization: Bearer YOUR_TOKEN'\│
  │   --header 'Content-Type: application/json' \ │
  │   --data '{                                   │
  │     "name": "mi-nginx",                       │
  │     "image": "nginx:latest",                  │
  │     "subject": 1                              │
  │   }'                                          │
  │                                               │
  │ [📋 Copiar comando]                           │
  └───────────────────────────────────────────────┘
  
  Respuesta:
  ┌───────────────────────────────────────────────┐
  │ {                                             │
  │   "id": 42,                                   │
  │   "name": "mi-nginx",                         │
  │   "status": "pending",                        │
  │   "created_at": "2025-12-09T22:00:00Z"        │
  │ }                                             │
  └───────────────────────────────────────────────┘

▼ Listar Servicios
  GET /api/services/
  [ejemplos...]

▼ Iniciar Servicio
  POST /api/services/{id}/start/
  [ejemplos...]

▼ Detener Servicio
  POST /api/services/{id}/stop/
  [ejemplos...]

▼ Eliminar Servicio
  DELETE /api/services/{id}/
  [ejemplos...]
```

#### **3.2 Funcionalidades interactivas**
- [ ] Botón "Copiar comando" para cada ejemplo
- [ ] Reemplazar `YOUR_TOKEN` automáticamente con el token del usuario
- [ ] Reemplazar `{id}` con IDs de servicios reales del usuario
- [ ] Secciones colapsables para cada endpoint

#### **3.3 Ejemplos avanzados**
- [ ] Crear servicio con Dockerfile
- [ ] Crear servicio con docker-compose
- [ ] Subir código fuente (multipart/form-data)
- [ ] Variables de entorno
- [ ] Volúmenes

**Estimación**: 4-5 horas

---

## 📋 FASE 4: Testing y Documentación

### **Tareas:**
- [ ] Testing de endpoints API
- [ ] Testing de autenticación con tokens
- [ ] Documentación de usuario
- [ ] Ejemplos de integración con CI/CD (GitHub Actions, GitLab CI)

**Ejemplo GitHub Actions**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to PaaSify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to PaaSify
        run: |
          curl --request POST \
            https://paasify.com/api/services/ \
            --header 'Authorization: Bearer ${{ secrets.PAASIFY_TOKEN }}' \
            --header 'Content-Type: application/json' \
            --data '{
              "name": "my-app",
              "image": "myapp:latest"
            }'
```

**Estimación**: 3-4 horas

---

## 📊 RESUMEN

### **Tiempo total estimado**: 17-23 horas

### **Fases**:
1. ✅ Página dedicada "Nuevo Servicio" (4-6h)
2. ✅ Sistema de API REST con Tokens (6-8h)
3. ✅ Página de documentación API (4-5h)
4. ✅ Testing y documentación (3-4h)

### **Beneficios**:
- ✅ Mejor UX para crear servicios
- ✅ Capacidad de CI/CD
- ✅ Automatización de despliegues
- ✅ Integración con pipelines
- ✅ Documentación clara y ejemplos

### **Dependencias**:
- Django REST Framework
- djangorestframework.authtoken

---

## 🔄 PRÓXIMOS PASOS

1. Revisar y aprobar plan
2. Implementar Fase 1 (Nuevo Servicio)
3. Implementar Fase 2 (API + Tokens)
4. Implementar Fase 3 (Documentación)
5. Testing completo
6. Documentación de usuario

---

**Estado**: PENDIENTE DE APROBACIÓN  
**Prioridad**: MEDIA (después de testing Docker Compose)
