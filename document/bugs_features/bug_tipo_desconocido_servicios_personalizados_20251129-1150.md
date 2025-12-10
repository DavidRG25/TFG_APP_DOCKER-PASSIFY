# Bug Report - Rama: dev2
> Resumen: Servicios personalizados muestran tipo "Desconocido" en lugar de "Personalizado"

## 🐛 Bug detectado durante testing

**Fase de testing:** Test 3.1 - Service Admin  
**Fecha:** 2025-11-29  
**Reportado por:** Usuario (testing manual)

---

## 📋 Descripcion del problema

Los servicios creados con **Dockerfile personalizado** o **docker-compose** muestran **"❓ Desconocido"** en la columna "Tipo" del admin, cuando deberian mostrar **"📦 Personalizado"** o similar.

### Comportamiento observado:

**En el admin (`/admin/containers/service/`):**
- Servicio con imagen del catalogo (nginx:latest) → ✅ "🌐 Web / Frontend"
- Servicio con Dockerfile personalizado → ❌ "❓ Desconocido"
- Servicio con docker-compose → ❌ "❓ Desconocido"

### Comportamiento esperado:

- Servicio con imagen del catalogo → "🌐 Web / Frontend" (o tipo correspondiente)
- Servicio con Dockerfile personalizado → "📦 Personalizado (Dockerfile)"
- Servicio con docker-compose → "🐳 Personalizado (Compose)"

---

## 🔍 Causa raiz

En `containers/admin.py`, metodo `get_image_type` (lineas 275-292):

```python
def get_image_type(self, obj):
    """Muestra el tipo de imagen con icono"""
    try:
        image_name = obj.image.split(':')[0]
        image_tag = obj.image.split(':')[1] if ':' in obj.image else 'latest'
        
        allowed = AllowedImage.objects.get(name=image_name, tag=image_tag)
        icons = {
            'web': '🌐',
            'database': '🗄️',
            'api': '🚀',
            'misc': '📦',
        }
        icon = icons.get(allowed.image_type, '📦')
        return f"{icon} {allowed.get_image_type_display()}"
    except AllowedImage.DoesNotExist:
        return "❓ Desconocido"  # <-- PROBLEMA
```

**Problema:** 
- Servicios personalizados (Dockerfile/compose) **no tienen entrada en AllowedImage**
- El campo `obj.image` contiene el tag de la imagen construida (ej: `svc_6_prueba-dockerfile_image`)
- Esta imagen no existe en el catalogo → `AllowedImage.DoesNotExist` → "❓ Desconocido"

---

## 💡 Solucion propuesta

Modificar `get_image_type` para detectar servicios personalizados:

```python
def get_image_type(self, obj):
    """Muestra el tipo de imagen con icono"""
    # Detectar si es servicio personalizado
    if obj.dockerfile:
        return "📦 Personalizado (Dockerfile)"
    
    if obj.compose:
        return "🐳 Personalizado (Compose)"
    
    # Servicio con imagen del catalogo
    try:
        image_name = obj.image.split(':')[0]
        image_tag = obj.image.split(':')[1] if ':' in obj.image else 'latest'
        
        allowed = AllowedImage.objects.get(name=image_name, tag=image_tag)
        icons = {
            'web': '🌐',
            'database': '🗄️',
            'api': '🚀',
            'misc': '📦',
        }
        icon = icons.get(allowed.image_type, '📦')
        return f"{icon} {allowed.get_image_type_display()}"
    except AllowedImage.DoesNotExist:
        # Imagen no catalogada (puede ser imagen custom sin Dockerfile/compose)
        return "❓ No catalogada"
```

**Mejora adicional:** Agregar colores/estilos:

```python
from django.utils.html import format_html

def get_image_type(self, obj):
    """Muestra el tipo de imagen con icono"""
    if obj.dockerfile:
        return format_html(
            '<span style="color: #9c27b0; font-weight: bold;">📦 Personalizado (Dockerfile)</span>'
        )
    
    if obj.compose:
        return format_html(
            '<span style="color: #00bcd4; font-weight: bold;">🐳 Personalizado (Compose)</span>'
        )
    
    # ... resto del codigo ...
```

---

## 📊 Impacto

### Usuarios afectados:
- ✅ Profesores revisando servicios de alumnos
- ✅ Administradores gestionando servicios

### Severidad:
- **Baja:** Es solo visual, no afecta funcionalidad
- **UX:** Confuso ver "Desconocido" en servicios validos

---

## 🔧 Archivos afectados

- `containers/admin.py` (metodo `get_image_type`, lineas 275-292)

---

**Estado:** 🔴 Pendiente de correccion  
**Prioridad:** Baja (cosmético)  
**Relacionado con:** Test 3.1 - Service Admin
