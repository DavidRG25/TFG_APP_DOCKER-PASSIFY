# Bug: Inconsistencia en Validación de Campo Proyecto

**Fecha:** 11/12/2025 15:20  
**Tipo:** Bug de Validación / Inconsistencia  
**Prioridad:** Media  
**Estado:** COMPLETADO  
**Versión afectada:** v5.0

---

## 📋 Descripción

Existe una inconsistencia entre la validación del campo `project` en la interfaz web y el API REST. La UI web requiere que todos los servicios tengan un proyecto asignado, pero el API REST permite crear servicios sin proyecto.

## 🔍 Comportamiento Actual

### Web UI (Formulario)

```html
<!-- templates/containers/_partials/panels/_modals.html -->
<select name="project" class="form-select" required>
  <!-- Proyecto OBLIGATORIO -->
</select>
```

- ✅ Campo marcado como `required`
- ✅ No permite enviar formulario sin seleccionar proyecto
- ✅ Muestra advertencia si el usuario no tiene proyectos

### API REST

```python
# containers/models.py
project = models.ForeignKey(
    "paasify.UserProject",
    null=True,      # ← Permite NULL
    blank=True,     # ← Permite vacío
    ...
)
```

- ⚠️ Campo **opcional** a nivel de modelo
- ⚠️ No hay validación en el serializer
- ⚠️ Se pueden crear servicios sin proyecto vía API

## 🐛 Problema

**Inconsistencia de reglas de negocio:**

- Usuario web: **Obligado** a asignar proyecto
- Usuario API: **Puede omitir** proyecto

**Consecuencias:**

1. Servicios "huérfanos" sin proyecto en la base de datos
2. Confusión en la documentación del API
3. Posibles errores en vistas que asumen que todos los servicios tienen proyecto
4. Dificultad para filtrar/organizar servicios por proyecto

## 📊 Ejemplo de Reproducción

### Vía Web UI (Falla correctamente)

```bash
# Intentar crear servicio sin proyecto
# → Error: "Campo requerido"
```

### Vía API REST (Permite incorrectamente)

```bash
curl --request POST \
  --url http://localhost:8000/api/containers/ \
  --header 'Authorization: Bearer TOKEN' \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "servicio-sin-proyecto",
    "image": "nginx:latest",
    "mode": "default"
  }'

# → 201 Created (Debería fallar)
```

## ✅ Comportamiento Esperado

Ambas interfaces (Web y API) deben aplicar las mismas reglas:

- Campo `project` **obligatorio** en todos los casos
- Validación consistente en modelo, serializer y formularios
- Mensajes de error claros cuando falta el proyecto

## 🔧 Soluciones Propuestas

### Opción 1: Hacer proyecto obligatorio a nivel de modelo (Recomendado)

**Cambios en `containers/models.py`:**

```python
project = models.ForeignKey(
    "paasify.UserProject",
    null=False,           # ← Cambiar
    blank=False,          # ← Cambiar
    on_delete=models.CASCADE,  # ← Cambiar (si se borra proyecto, borrar servicios)
    related_name="services",
    verbose_name="Proyecto",
)
```

**Pasos:**

1. Crear migración de datos: Asignar proyecto por defecto a servicios existentes sin proyecto
2. Aplicar migración de esquema
3. Actualizar documentación del API

**Ventajas:**

- ✅ Consistencia total
- ✅ Imposible crear servicios sin proyecto
- ✅ Mejor integridad de datos

**Desventajas:**

- ⚠️ Requiere migración de datos existentes
- ⚠️ Breaking change para usuarios del API

### Opción 2: Validar solo en el serializer

**Cambios en `containers/serializers.py`:**

```python
class ServiceSerializer(serializers.ModelSerializer):
    # ...

    def validate(self, attrs):
        # Validación existente...

        # Añadir validación de proyecto
        if not attrs.get('project'):
            raise serializers.ValidationError({
                "project": "El campo proyecto es obligatorio."
            })

        return attrs
```

**Ventajas:**

- ✅ No requiere migración
- ✅ Fácil de implementar

**Desventajas:**

- ⚠️ Inconsistencia entre modelo (permite NULL) y validación
- ⚠️ Administradores podrían crear servicios sin proyecto desde Django Admin

### Opción 3: Hacer proyecto opcional en Web UI

**NO RECOMENDADO** - Contradice la decisión de diseño actual de v5.0

## 📝 Notas Adicionales

- **Contexto histórico:** El campo `project` se añadió en v5.0 como parte de la integración de proyectos
- **Decisión de diseño:** Se decidió que todos los servicios deben pertenecer a un proyecto para mejor organización
- **Impacto:** Afecta a usuarios que usen el API REST para automatización

## 🎯 Plan de Acción Sugerido

1. **Corto plazo (Workaround):**
   - Actualizar documentación del API indicando que `project` es **recomendado**
   - Añadir nota de advertencia en la guía de API

2. **Medio plazo (Fix definitivo):**
   - Implementar Opción 1 (modelo obligatorio)
   - Crear script de migración de datos
   - Actualizar tests
   - Versionar como breaking change (v6.0)

## 📚 Referencias

- Archivo afectado: `containers/models.py` (líneas 49-56)
- Archivo afectado: `templates/containers/_partials/panels/_modals.html` (línea 41)
- Documentación: `document/internal_guides/api_rest_curl_usage_20251211_1512.md`
- Commit relacionado: Integración de proyectos v5.0

---

**Reportado por:** Sistema  
**Asignado a:** Pendiente  
**Etiquetas:** `bug`, `validación`, `api`, `consistencia`, `proyecto`
