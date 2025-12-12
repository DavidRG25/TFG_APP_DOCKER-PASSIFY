# Feature Request: Permitir Nombres en Campos project y subject del API

**Fecha:** 11/12/2025 15:32  
**Tipo:** Feature Request / Mejora de Usabilidad  
**Prioridad:** Media  
**Estado:** Pendiente  
**Versión afectada:** v5.0

---

## 📋 Descripción

Actualmente, el API REST solo acepta **IDs numéricos** para los campos `project` y `subject`. Esto dificulta la usabilidad ya que el usuario debe conocer o buscar los IDs antes de hacer la petición.

**Propuesta:** Permitir que el usuario pueda usar **nombres** (strings) además de IDs, y que el backend resuelva automáticamente el ID correspondiente.

## 🔍 Comportamiento Actual

```bash
# ✅ Funciona (con ID)
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

# ❌ Falla (con nombre)
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "mi-servicio",
    "image": "nginx:latest",
    "project": "A1 - Prueba 1",
    "subject": "Asignatura 1"
  }'

# Error: {"subject":["Tipo incorrecto. Se esperaba valor de clave primaria y se recibió str."]}
```

## ✅ Comportamiento Deseado

El API debería aceptar **ambos formatos**:

### Opción 1: Por ID (actual)

```json
{
  "project": 1,
  "subject": 1
}
```

### Opción 2: Por nombre (nuevo)

```json
{
  "project": "A1 - Prueba 1",
  "subject": "Asignatura 1"
}
```

### Opción 3: Mixto

```json
{
  "project": 1,
  "subject": "Asignatura 1"
}
```

## 🎯 Beneficios

1. **Mejor DX (Developer Experience)**: Más intuitivo y legible
2. **Scripts más mantenibles**: No necesitas actualizar IDs si cambias de proyecto
3. **Menos errores**: Nombres son más fáciles de recordar que IDs
4. **Consistencia**: Otros APIs modernos permiten ambos formatos

## 🔧 Implementación Sugerida

### Modificar el Serializer

**Archivo:** `containers/serializers.py`

```python
from rest_framework import serializers
from paasify.models.ProjectModel import UserProject
from paasify.models.SubjectModel import Subject

class ServiceSerializer(serializers.ModelSerializer):
    # Campos flexibles que aceptan ID o nombre
    project = serializers.CharField(required=False, allow_null=True)
    subject = serializers.CharField(required=False, allow_null=True)

    # ... resto del código ...

    def validate_project(self, value):
        """
        Acepta ID numérico o nombre del proyecto.
        Retorna la instancia de UserProject.
        """
        if value is None:
            return None

        user = self.context['request'].user

        # Intentar como ID numérico
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            try:
                return UserProject.objects.get(
                    pk=int(value),
                    user_profile__user=user
                )
            except UserProject.DoesNotExist:
                raise serializers.ValidationError(
                    f"No tienes un proyecto con ID {value}"
                )

        # Intentar como nombre (campo 'place')
        if isinstance(value, str):
            try:
                return UserProject.objects.get(
                    place=value,
                    user_profile__user=user
                )
            except UserProject.DoesNotExist:
                raise serializers.ValidationError(
                    f"No tienes un proyecto llamado '{value}'"
                )
            except UserProject.MultipleObjectsReturned:
                raise serializers.ValidationError(
                    f"Tienes múltiples proyectos llamados '{value}'. Usa el ID en su lugar."
                )

        raise serializers.ValidationError("Formato inválido para proyecto")

    def validate_subject(self, value):
        """
        Acepta ID numérico o nombre de la asignatura.
        Retorna la instancia de Subject.
        """
        if value is None:
            return None

        user = self.context['request'].user

        # Intentar como ID numérico
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            try:
                subject = Subject.objects.get(pk=int(value))
                # Verificar que el usuario está matriculado
                if not subject.students.filter(pk=user.id).exists():
                    raise serializers.ValidationError(
                        f"No estás matriculado en la asignatura con ID {value}"
                    )
                return subject
            except Subject.DoesNotExist:
                raise serializers.ValidationError(
                    f"No existe asignatura con ID {value}"
                )

        # Intentar como nombre
        if isinstance(value, str):
            try:
                subject = Subject.objects.get(
                    name=value,
                    students=user
                )
                return subject
            except Subject.DoesNotExist:
                raise serializers.ValidationError(
                    f"No estás matriculado en '{value}'"
                )
            except Subject.MultipleObjectsReturned:
                raise serializers.ValidationError(
                    f"Hay múltiples asignaturas llamadas '{value}'. Usa el ID en su lugar."
                )

        raise serializers.ValidationError("Formato inválido para asignatura")

    def to_representation(self, instance):
        """
        En la respuesta, siempre devolver IDs (para consistencia)
        """
        representation = super().to_representation(instance)
        if instance.project:
            representation['project'] = instance.project.id
        if instance.subject:
            representation['subject'] = instance.subject.id
        return representation
```

### Actualizar el método create en la vista

**Archivo:** `containers/views.py`

```python
def create(self, request, *args, **kwargs):
    # ... código existente ...

    # Ya no necesitamos este bloque porque el serializer lo maneja:
    # project_id = request.data.get("project")
    # project = None
    # if project_id:
    #     project = get_object_or_404(UserProject, pk=project_id, ...)

    # El serializer ya validó y convirtió project/subject a instancias
    service = serializer.save(owner=request.user, status="creating")

    # ... resto del código ...
```

## 📊 Ejemplos de Uso Después del Fix

### Ejemplo 1: Por nombre (más legible)

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "web-frontend",
    "image": "nginx:latest",
    "mode": "default",
    "project": "Proyecto Final",
    "subject": "DevOps Avanzado"
  }'
```

**Respuesta:**

```json
{
  "id": 42,
  "name": "web-frontend",
  "project": 5,
  "subject": 2,
  "status": "creating"
}
```

### Ejemplo 2: Por ID (compatibilidad)

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "api-backend",
    "image": "node:18",
    "project": 5,
    "subject": 2
  }'
```

### Ejemplo 3: Script con nombres (más mantenible)

```bash
#!/bin/bash

TOKEN="mi_token"
PROJECT="Proyecto Final"
SUBJECT="DevOps Avanzado"

# Desplegar múltiples servicios del mismo proyecto
for service in web api database; do
  curl --request POST \
    --url http://localhost:8000/api/containers/ \
    --header "Authorization: Bearer $TOKEN" \
    --header 'Content-Type: application/json' \
    --data "{
      \"name\": \"$service\",
      \"image\": \"nginx:latest\",
      \"project\": \"$PROJECT\",
      \"subject\": \"$SUBJECT\"
    }"
done
```

## ⚠️ Consideraciones

### Manejo de Duplicados

Si un usuario tiene dos proyectos con el mismo nombre:

- **Solución:** Retornar error claro indicando que debe usar el ID
- **Mensaje:** `"Tienes múltiples proyectos llamados 'X'. Usa el ID en su lugar."`

### Rendimiento

- **Impacto mínimo:** La búsqueda por nombre usa índices de DB
- **Optimización:** Añadir `db_index=True` al campo `place` de `UserProject` y `name` de `Subject`

### Retrocompatibilidad

- ✅ **100% compatible**: El código actual (con IDs) seguirá funcionando
- ✅ **Sin breaking changes**: Solo añade funcionalidad nueva

## 📝 Documentación a Actualizar

Después de implementar, actualizar:

1. `document/internal_guides/api_rest_curl_usage_20251211_1512.md`
2. Swagger/OpenAPI schema (si existe)
3. Tests del API

## 🔗 Bugs Relacionados

- `bug_falta_endpoint_listar_proyectos_20251211_1529.md` - Complementario
- `bug_inconsistencia_validacion_proyecto_20251211_1520.md` - Relacionado

---

**Reportado por:** Sistema  
**Asignado a:** Pendiente  
**Etiquetas:** `feature-request`, `api`, `usabilidad`, `dx-improvement`
