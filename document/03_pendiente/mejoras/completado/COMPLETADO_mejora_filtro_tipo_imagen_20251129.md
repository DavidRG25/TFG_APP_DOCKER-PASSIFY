# Feature Request - Rama: dev2

> Resumen: Agregar filtro por tipo de imagen en Service Admin

## 🟡 Feature Request detectado durante testing

**Fase de testing:** Test 3.1 - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)

---

## 📋 Descripcion

En el admin de servicios (`/admin/containers/service/`), **no existe un filtro por tipo de imagen** (Web, Database, API, Personalizado), lo cual dificulta encontrar servicios especificos cuando hay muchos.

### Comportamiento actual:

**Filtros disponibles:**

- ✅ Por estado (running, stopped, error, etc.)
- ✅ Por fecha de creacion

**Filtros faltantes:**

- ❌ Por tipo de imagen (Web, Database, API, Misc, Personalizado)

### Comportamiento esperado:

Agregar filtro en el sidebar:

```
FILTROS
-------
Por estado
  ○ Todos
  ○ Running
  ○ Stopped
  ○ Error

Por tipo de imagen    <-- NUEVO
  ○ Todos
  ○ Web / Frontend
  ○ Base de Datos
  ○ Generador de API
  ○ Miscelanea
  ○ Personalizado

Por fecha de creacion
  ○ Hoy
  ○ Ultimos 7 dias
  ...
```

---

## 💡 Solucion propuesta

### Opcion A: Filtro simple por tipo (RECOMENDADA)

Agregar `list_filter` en `ServiceAdmin`:

```python
# En containers/admin.py
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'image',
        'get_image_type',
        'assigned_port',
        'status',
        'get_volume_info',
        'created_at',
    )
    search_fields = ('name', 'owner__username', 'image')
    list_filter = (
        'status',
        'created_at',
        'get_image_type_filter',  # <-- NUEVO
    )

    # ... resto del codigo ...

    def get_image_type_filter(self, obj):
        """Devuelve el tipo para filtrado"""
        if obj.dockerfile:
            return "Personalizado (Dockerfile)"
        if obj.compose:
            return "Personalizado (Compose)"

        try:
            image_name = obj.image.split(':')[0]
            image_tag = obj.image.split(':')[1] if ':' in obj.image else 'latest'
            allowed = AllowedImage.objects.get(name=image_name, tag=image_tag)
            return allowed.get_image_type_display()
        except AllowedImage.DoesNotExist:
            return "No catalogada"

    get_image_type_filter.short_description = 'Tipo de imagen'
```

**Problema:** `list_filter` no acepta metodos directamente.

### Opcion B: Custom filter (CORRECTA)

Crear un filtro personalizado:

```python
# En containers/admin.py
from django.contrib.admin import SimpleListFilter

class ImageTypeFilter(SimpleListFilter):
    title = 'tipo de imagen'
    parameter_name = 'image_type'

    def lookups(self, request, model_admin):
        return (
            ('web', '🌐 Web / Frontend'),
            ('database', '🗄️ Base de Datos'),
            ('api', '🚀 Generador de API'),
            ('misc', '📦 Miscelanea'),
            ('dockerfile', '📦 Personalizado (Dockerfile)'),
            ('compose', '🐳 Personalizado (Compose)'),
            ('unknown', '❓ No catalogada'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'dockerfile':
            return queryset.exclude(dockerfile='')

        if self.value() == 'compose':
            return queryset.exclude(compose='')

        if self.value() in ['web', 'database', 'api', 'misc']:
            # Filtrar por tipo de AllowedImage
            allowed_images = AllowedImage.objects.filter(image_type=self.value())
            image_names = [f"{img.name}:{img.tag}" for img in allowed_images]
            return queryset.filter(image__in=image_names)

        if self.value() == 'unknown':
            # Servicios sin Dockerfile/Compose y sin imagen catalogada
            cataloged = AllowedImage.objects.all()
            cataloged_names = [f"{img.name}:{img.tag}" for img in cataloged]
            return queryset.filter(dockerfile='', compose='').exclude(image__in=cataloged_names)

        return queryset

# Agregar al ServiceAdmin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_filter = (
        'status',
        'created_at',
        ImageTypeFilter,  # <-- NUEVO
    )
```

**Ventajas:**

- ✅ Filtro funcional completo
- ✅ Iconos en las opciones
- ✅ Filtra correctamente por tipo

---

## 📊 Impacto

### Beneficio:

Con 50+ servicios en el sistema:

- **Antes:** Scroll manual para encontrar servicios de un tipo
- **Despues:** Click en filtro → Solo servicios del tipo deseado

### Casos de uso:

1. **Profesor revisa solo servicios web de alumnos**
   - Filtro: "Web / Frontend"
   - Resultado: Solo nginx, apache, httpd

2. **Admin busca servicios personalizados**
   - Filtro: "Personalizado (Dockerfile)"
   - Resultado: Solo servicios con Dockerfile

3. **Debug de bases de datos**
   - Filtro: "Base de Datos"
   - Resultado: Solo mysql, postgres, mongodb

---

## 🎯 Recomendacion

**Implementar Opcion B (Custom filter):**

1. Crear clase `ImageTypeFilter` en `containers/admin.py`
2. Agregar a `list_filter` de `ServiceAdmin`
3. Probar con diferentes tipos

**Prioridad:** Media (mejora de UX)

---

## 🔧 Archivos afectados

- `containers/admin.py` (nueva clase `ImageTypeFilter`, modificar `ServiceAdmin.list_filter`)

---

**Estado:** COMPLETADO  
**Prioridad:** Media  
**Relacionado con:** Test 3.1 - Service Admin
