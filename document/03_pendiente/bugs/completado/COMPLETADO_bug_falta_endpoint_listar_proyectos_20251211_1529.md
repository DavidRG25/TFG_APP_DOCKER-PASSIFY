# Bug: Falta Endpoint para Listar Proyectos y Asignaturas del Usuario

**Fecha:** 11/12/2025 15:29  
**Tipo:** Feature Faltante / Bug de Usabilidad  
**Prioridad:** Alta  
**Estado:** COMPLETADO  
**Versión afectada:** v5.0

---

## 📋 Descripción

No existe un endpoint en el API REST para que un usuario (alumno) pueda listar sus proyectos y asignaturas. Esto hace imposible usar el API de forma programática sin conocer previamente los IDs de proyectos y asignaturas.

## 🔍 Problema

Para crear un servicio vía API, el usuario debe proporcionar:

- `project`: ID numérico del proyecto
- `subject`: ID numérico de la asignatura

**Pero no hay forma de obtener estos IDs vía API.**

## 🐛 Impacto

### Caso de Uso Bloqueado

Un usuario que quiere automatizar el despliegue de servicios necesita:

1. **Obtener sus proyectos** → ❌ No hay endpoint
2. **Obtener sus asignaturas** → ❌ No hay endpoint
3. **Crear servicio con project y subject** → ✅ Funciona (si conoces los IDs)

**Workarounds actuales (poco prácticos):**

- Inspeccionar manualmente la UI web
- Usar la consola del navegador con JavaScript
- Consultar directamente la base de datos (no viable para usuarios)

## 📊 Ejemplo de Reproducción

### Intento de automatización (Falla)

```bash
# Paso 1: Intentar listar proyectos
curl --request GET \
  --url http://localhost:8000/api/projects/ \
  --header 'Authorization: Bearer TOKEN'

# → 404 Not Found (endpoint no existe)

# Paso 2: Intentar listar asignaturas
curl --request GET \
  --url http://localhost:8000/api/subjects/ \
  --header 'Authorization: Bearer TOKEN'

# → 404 Not Found (endpoint no existe)

# Paso 3: Crear servicio (sin saber los IDs)
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mi-servicio",
    "image": "nginx:latest",
    "project": ???,  # ← No sé qué poner aquí
    "subject": ???   # ← No sé qué poner aquí
  }'
```

## ✅ Solución Propuesta

### Crear Endpoints para Listar Recursos del Usuario

#### 1. Endpoint: Listar Proyectos del Usuario

**URL:** `GET /api/projects/`  
**Autenticación:** Bearer Token  
**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "A1 - Prueba 1",
    "subject": {
      "id": 1,
      "name": "Asignatura 1"
    }
  },
  {
    "id": 2,
    "name": "A1 - Prueba 2",
    "subject": {
      "id": 1,
      "name": "Asignatura 1"
    }
  }
]
```

#### 2. Endpoint: Listar Asignaturas del Usuario

**URL:** `GET /api/subjects/`  
**Autenticación:** Bearer Token  
**Respuesta:**

```json
[
  {
    "id": 1,
    "name": "Asignatura 1",
    "year": "2024",
    "category": "Asignatura obligatorias"
  },
  {
    "id": 2,
    "name": "Asignatura 2",
    "year": "2024",
    "category": "Asignatura optativa"
  }
]
```

## 🔧 Implementación Sugerida

### Paso 1: Crear Serializers

**Archivo:** `paasify/serializers.py` (crear si no existe)

```python
from rest_framework import serializers
from paasify.models.ProjectModel import UserProject
from paasify.models.SubjectModel import Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'genero', 'category')

class UserProjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = UserProject
        fields = ('id', 'place', 'subject')
```

### Paso 2: Crear ViewSets

**Archivo:** `paasify/views/ApiViews.py` (crear)

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from paasify.models.ProjectModel import UserProject
from paasify.models.SubjectModel import Subject
from paasify.serializers import UserProjectSerializer, SubjectSerializer

class UserProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listar proyectos del usuario autenticado.
    Solo lectura (GET).
    """
    serializer_class = UserProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProject.objects.filter(
            user_profile__user=self.request.user
        ).select_related('subject')

class UserSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para listar asignaturas del usuario autenticado.
    Solo lectura (GET).
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Asignaturas donde el usuario es alumno
        return Subject.objects.filter(
            students=self.request.user
        ).distinct()
```

### Paso 3: Registrar en URLs

**Archivo:** `app_passify/urls.py`

```python
from paasify.views.ApiViews import UserProjectViewSet, UserSubjectViewSet

# Añadir al router existente:
router.register(r'projects', UserProjectViewSet, basename='user-project')
router.register(r'subjects', UserSubjectViewSet, basename='user-subject')
```

## 🎯 Flujo Completo Después del Fix

```bash
# 1. Listar mis asignaturas
curl --request GET \
  --url http://localhost:8000/api/subjects/ \
  --header 'Authorization: Bearer TOKEN'
# → Obtengo: [{"id": 1, "name": "Asignatura 1"}, ...]

# 2. Listar mis proyectos
curl --request GET \
  --url http://localhost:8000/api/projects/ \
  --header 'Authorization: Bearer TOKEN'
# → Obtengo: [{"id": 1, "name": "A1 - Prueba 1", "subject": {...}}, ...]

# 3. Crear servicio con los IDs obtenidos
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mi-servicio",
    "image": "nginx:latest",
    "project": 1,
    "subject": 1
  }'
# → ✅ Funciona!
```

## 📝 Beneficios

1. **Automatización completa**: Scripts pueden descubrir proyectos dinámicamente
2. **Mejor DX (Developer Experience)**: No necesitas la UI web para usar el API
3. **Consistencia**: Todos los recursos accesibles vía API
4. **Documentación mejorada**: Ejemplos más realistas en la guía

## 🚀 Prioridad

**Alta** - Este es un bloqueador para cualquier automatización seria del API. Sin estos endpoints, el API REST está incompleto.

## 📚 Referencias

- Guía de API: `document/internal_guides/api_rest_curl_usage_20251211_1512.md`
- Modelos afectados: `paasify/models/ProjectModel.py`, `paasify/models/SubjectModel.py`
- Bug relacionado: `bug_inconsistencia_validacion_proyecto_20251211_1520.md`

---

**Reportado por:** Sistema  
**Asignado a:** Pendiente  
**Etiquetas:** `bug`, `api`, `feature-request`, `usabilidad`, `alta-prioridad`
