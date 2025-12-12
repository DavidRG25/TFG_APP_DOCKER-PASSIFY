# Feature: Mostrar IDs en Panel de Admin para Asignaturas y Proyectos

**Fecha:** 11/12/2025 15:34  
**Tipo:** Feature Request / Mejora de Admin  
**Prioridad:** Baja  
**Estado:** Pendiente  
**Versión afectada:** v5.0

---

## 📋 Descripción

Los administradores necesitan ver los **IDs** de asignaturas y proyectos en el panel de administración de Django para poder comunicarlos a los usuarios del API o para debugging.

Actualmente, el admin muestra nombres pero no IDs de forma visible, lo que dificulta ayudar a los usuarios que necesitan estos valores para usar el API REST.

## 🔍 Problema Actual

### Panel de Asignaturas (`/admin/paasify/subject/`)

- ✅ Muestra: Nombre, Profesor, Año, Categoría
- ❌ **No muestra**: ID (solo visible en la URL al editar)

### Panel de Proyectos (`/admin/paasify/userproject/`)

- ✅ Muestra: Nombre del proyecto, Usuario, Asignatura
- ❌ **No muestra**: ID (solo visible en la URL al editar)

## ✅ Comportamiento Deseado

### Lista de Asignaturas

| **ID** | Nombre          | Profesor     | Año  | Categoría   | Alumnos |
| ------ | --------------- | ------------ | ---- | ----------- | ------- |
| 1      | Asignatura 1    | Prof. García | 2024 | Obligatoria | 25      |
| 2      | DevOps Avanzado | Prof. López  | 2025 | Optativa    | 18      |

### Lista de Proyectos

| **ID** | Proyecto       | Usuario     | Asignatura              | Fecha Creación |
| ------ | -------------- | ----------- | ----------------------- | -------------- |
| 1      | A1 - Prueba 1  | alumno      | Asignatura 1 (ID: 1)    | 10/12/2025     |
| 5      | Proyecto Final | estudiante2 | DevOps Avanzado (ID: 2) | 11/12/2025     |

## 🔧 Implementación Sugerida

### Modificar Admin de Subject

**Archivo:** `paasify/admin.py`

```python
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'id',           # ← Añadir ID
        'name',
        'teacher_user',
        'genero',
        'category',
        'get_students_count',
    )

    list_display_links = ('id', 'name')  # Hacer ID clickeable también

    search_fields = ('id', 'name', 'teacher_user__username')  # Buscar por ID

    def get_students_count(self, obj):
        """Mostrar número de alumnos matriculados"""
        count = obj.students.count()
        return f"{count} alumno{'s' if count != 1 else ''}"
    get_students_count.short_description = "Alumnos"
```

### Modificar Admin de UserProject

**Archivo:** `paasify/admin.py`

```python
@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id',                    # ← Añadir ID
        'place',                 # Nombre del proyecto
        'user_profile',
        'get_subject_with_id',   # ← Mostrar asignatura con su ID
        'created_at',
    )

    list_display_links = ('id', 'place')

    search_fields = ('id', 'place', 'user_profile__user__username', 'subject__name')

    list_filter = ('subject', 'created_at')

    readonly_fields = ('id', 'created_at')

    def get_subject_with_id(self, obj):
        """Mostrar asignatura con su ID entre paréntesis"""
        if obj.subject:
            return f"{obj.subject.name} (ID: {obj.subject.id})"
        return "-"
    get_subject_with_id.short_description = "Asignatura"
    get_subject_with_id.admin_order_field = 'subject__name'
```

### Añadir Acción de Admin para Copiar IDs

**Bonus:** Acción para copiar IDs al portapapeles

```python
from django.contrib import admin, messages

@admin.action(description="Mostrar IDs seleccionados")
def show_selected_ids(modeladmin, request, queryset):
    """Muestra los IDs de los elementos seleccionados"""
    ids = list(queryset.values_list('id', flat=True))
    ids_str = ', '.join(map(str, ids))

    messages.success(
        request,
        f"IDs seleccionados: {ids_str}"
    )

# Añadir a SubjectAdmin y UserProjectAdmin
class SubjectAdmin(admin.ModelAdmin):
    actions = [show_selected_ids]
    # ...

class UserProjectAdmin(admin.ModelAdmin):
    actions = [show_selected_ids]
    # ...
```

## 📊 Casos de Uso

### Caso 1: Soporte a Usuario del API

**Escenario:**
Un alumno pregunta: _"¿Cuál es el ID de mi proyecto 'Trabajo Final'?"_

**Solución con el feature:**

1. Admin accede a `/admin/paasify/userproject/`
2. Busca "Trabajo Final" en el buscador
3. Ve directamente: **ID: 42**
4. Comunica al alumno: `"project": 42`

### Caso 2: Debugging de Servicios

**Escenario:**
Un servicio falla y en los logs aparece `project_id=15`

**Solución con el feature:**

1. Admin ve en la lista que ID 15 = "Proyecto Beta"
2. Identifica rápidamente el contexto del error
3. Contacta al alumno correcto

### Caso 3: Migración de Datos

**Escenario:**
Necesitas crear un script para migrar proyectos

**Solución con el feature:**

1. Exportar desde admin con IDs visibles
2. Usar IDs en scripts de migración
3. Verificar resultados comparando IDs

## 🎨 Mejoras Visuales Opcionales

### Destacar ID con Badge

```python
from django.utils.html import format_html

def get_id_badge(self, obj):
    """Mostrar ID con badge de color"""
    return format_html(
        '<span style="background: #4e73df; color: white; padding: 3px 8px; '
        'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
        obj.id
    )
get_id_badge.short_description = "ID"
```

### Copiar ID al Hacer Click

```python
def get_id_copyable(self, obj):
    """ID con botón de copiar"""
    return format_html(
        '<span id="id-{}" style="font-family: monospace; font-weight: bold;">{}</span> '
        '<button onclick="navigator.clipboard.writeText(\'{}\'); '
        'alert(\'ID {} copiado!\');" style="cursor: pointer; border: none; '
        'background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; '
        'font-size: 10px;">📋</button>',
        obj.id, obj.id, obj.id, obj.id
    )
get_id_copyable.short_description = "ID"
```

## 📝 Beneficios

1. **Soporte más rápido**: Admin puede responder preguntas sobre IDs inmediatamente
2. **Debugging mejorado**: Correlación rápida entre IDs en logs y recursos
3. **Documentación**: Facilita crear guías con ejemplos reales
4. **Transparencia**: Usuarios pueden ver sus IDs si tienen acceso al admin

## ⚙️ Configuración Adicional

### Hacer ID Filtrable

```python
list_filter = (
    'subject',
    ('id', admin.EmptyFieldListFilter),  # Filtrar por rango de IDs
)
```

### Ordenar por ID por Defecto

```python
ordering = ('-id',)  # Más recientes primero
```

## 🔗 Features Relacionados

- `feature_permitir_nombres_project_subject_20251211_1532.md` - Complementario
- `bug_falta_endpoint_listar_proyectos_20251211_1529.md` - Resuelve parte del problema

---

**Reportado por:** Sistema  
**Asignado a:** Pendiente  
**Etiquetas:** `feature-request`, `admin`, `usabilidad`, `soporte`
