# Implementacion Mini Ajuste - Rama: dev2
_Resumen: Mejora de UX en formulario AllowedImage con fieldsets dinamicos_

## 📂 Archivos modificados

- `containers/admin.py` - AllowedImageAdmin

## 🎯 Contexto

Durante el testing del Plan de Mejoras del Admin (Fase 2), se detecto que el formulario de AllowedImage tenia un diseño plano y poco organizado comparado con el formulario de Service.

**Solicitud del usuario:**
> "Este diseño que hay editar y agregar una imagen permitida podría tener el mismo diseño que hay en la pantalla de editar y agregar un servicio, que va con franjas..."

---

## ✅ Mejora 1: Fieldsets con diseño de franjas azules

### Problema:
El formulario de AllowedImage mostraba todos los campos en una lista plana, sin organizacion visual.

### Solucion:
Agregar `fieldsets` con diseño similar a Service (franjas azules colapsables):

```python
fieldsets = (
    ('Informacion Basica', {
        'fields': ('name', 'tag', 'description')
    }),
    ('Clasificacion', {
        'fields': ('image_type',),
        'description': 'Selecciona el tipo de imagen segun las funcionalidades que necesitaras'
    }),
    ('Tags Disponibles en DockerHub', {
        'fields': ('suggested_tags',),
        'description': 'Selecciona un tag de la lista para actualizar automaticamente el campo Tag'
    }),
    ('Informacion del Sistema', {
        'fields': ('id', 'created_at', 'get_services_count'),
        'classes': ('collapse',),
    }),
)
```

**Resultado:**
- ✅ Diseño consistente con Service
- ✅ Mejor organizacion visual
- ✅ Seccion "Informacion del Sistema" colapsable

---

## ✅ Mejora 2: Informacion del Sistema enriquecida

### Campos agregados:

1. **ID** (readonly)
   - Identificador unico de la imagen
   - Util para debugging

2. **Fecha de creacion** (readonly)
   - Ya existia, ahora en seccion organizada

3. **Uso en servicios** (readonly, calculado) ⭐ **NUEVO**
   - Muestra cuantos servicios usan esta imagen
   - Implementacion:

```python
def get_services_count(self, obj):
    """Muestra cuantos servicios usan esta imagen"""
    if not obj.pk:
        return "-"
    
    from .models import Service
    image_full = f"{obj.name}:{obj.tag}"
    count = Service.objects.filter(image=image_full).count()
    
    if count == 0:
        return "No hay servicios usando esta imagen"
    
    return f"📊 {count} servicio{'s' if count != 1 else ''} usando esta imagen"
```

**Utilidad:**
- Antes de eliminar una imagen, ver si hay servicios activos usandola
- Identificar imagenes no utilizadas

---

## ✅ Mejora 3: Fieldsets dinamicos segun contexto

### Problema detectado:
Al **crear** una imagen nueva:
- Campo "Tags Disponibles en DockerHub" aparecia vacio (no hay nombre para consultar)
- Campo "Informacion del Sistema" mostraba valores vacios (ID, fecha aun no existen)

**Solicitud del usuario:**
> "Se puede hacer que al agregar una imagen, estos dos campos no aparezca?"

### Solucion:
Implementar `get_fieldsets()` para mostrar diferentes secciones segun creacion/edicion:

```python
def get_fieldsets(self, request, obj=None):
    """Muestra diferentes fieldsets segun si es creacion o edicion"""
    # Fieldsets base (siempre visibles)
    base_fieldsets = [
        ('Informacion Basica', {
            'fields': ('name', 'tag', 'description')
        }),
        ('Clasificacion', {
            'fields': ('image_type',),
            'description': 'Selecciona el tipo de imagen segun las funcionalidades que necesitaras'
        }),
    ]
    
    # Si es edicion (obj existe), agregar secciones adicionales
    if obj:
        base_fieldsets.append(
            ('Tags Disponibles en DockerHub', {
                'fields': ('suggested_tags',),
                'description': 'Selecciona un tag de la lista para actualizar automaticamente el campo Tag'
            })
        )
        base_fieldsets.append(
            ('Informacion del Sistema', {
                'fields': ('id', 'created_at', 'get_services_count'),
                'classes': ('collapse',),
            })
        )
    
    return base_fieldsets
```

### Comportamiento:

**Al CREAR imagen nueva:**
- ✅ Informacion Basica
- ✅ Clasificacion
- ❌ Tags Disponibles en DockerHub (oculto)
- ❌ Informacion del Sistema (oculto)

**Al EDITAR imagen existente:**
- ✅ Informacion Basica
- ✅ Clasificacion
- ✅ Tags Disponibles en DockerHub (visible, con selector poblado)
- ✅ Informacion del Sistema (visible, colapsado)

**Ventajas:**
- ✅ Formulario mas limpio al crear
- ✅ Solo muestra campos relevantes segun contexto
- ✅ Evita confusion con campos vacios

---

## 📊 Impacto total

### Mejora de UX:
- ✅ Diseño consistente entre AllowedImage y Service
- ✅ Organizacion visual clara con fieldsets
- ✅ Formularios dinamicos segun contexto
- ✅ Informacion util sobre uso de imagenes

### Antes vs Despues:

**Antes (crear imagen):**
```
Name: [____]
Tag: [____]
Description: [____]
Tipo de imagen: ( ) Web ( ) DB ( ) API ( ) Misc
Tags disponibles: [campo vacio]
ID: [vacio]
Fecha creacion: [vacio]
Uso en servicios: [vacio]
```

**Despues (crear imagen):**
```
┌─ Informacion Basica ──────────────┐
│ Name: [____]                       │
│ Tag: [____]                        │
│ Description: [____]                │
└────────────────────────────────────┘

┌─ Clasificacion ───────────────────┐
│ Tipo de imagen:                    │
│ ( ) Web ( ) DB ( ) API ( ) Misc   │
└────────────────────────────────────┘
```

**Despues (editar imagen):**
```
┌─ Informacion Basica ──────────────┐
│ Name: nginx                        │
│ Tag: latest                        │
│ Description: Servidor web          │
└────────────────────────────────────┘

┌─ Clasificacion ───────────────────┐
│ Tipo de imagen: (•) Web           │
└────────────────────────────────────┘

┌─ Tags Disponibles en DockerHub ───┐
│ [▼ latest                    ]    │
│    latest                          │
│    1.25-alpine                     │
│    1.25                            │
│    ...                             │
└────────────────────────────────────┘

▶ Informacion del Sistema (click para expandir)
```

---

## 🧪 Validacion

### Compilacion Python:
```bash
python -m compileall containers/admin.py
# Resultado: ✅ Sin errores
```

### Testing manual:
- [x] Crear imagen nueva → Solo campos basicos visibles
- [x] Guardar imagen → Redirige a edicion
- [x] Editar imagen → Aparecen secciones adicionales
- [x] Selector de tags poblado con DockerHub
- [x] Contador de servicios funcional

---

## 📝 Codigo modificado

### Cambios en `containers/admin.py`:

1. **Agregado `fieldsets`** (lineas 104-120)
2. **Agregado `readonly_fields`** (linea 122)
3. **Agregado metodo `get_services_count()`** (lineas 135-147)
4. **Agregado metodo `get_fieldsets()`** (lineas 150-177)

**Total de lineas agregadas:** ~50 lineas

---

## 📁 Documentacion relacionada

### Mejoras relacionadas:
- `document/mini_ajustes/mejoras_admin_testing_20251129-1100.md` (selector tags DockerHub)

### Testing:
- `document/testing/plan_testing_admin_completo_20251128.md` (Fase 2)

---

**Fecha de implementacion:** 2025-11-29 16:52
**Rama:** dev2
**Estado:** ✅ Completado y validado
**Tipo:** Mini ajuste de UX
**Relacionado con:** Plan de Testing Admin (Fase 2)
