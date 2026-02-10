# Mejora: Inline de Proyectos en Perfil de Alumno

**Fecha:** 2025-12-13  
**Ubicación:** `paasify/admin.py` - `UserProjectInlineForProfile`  
**Prioridad:** BAJA - Mejora de UX  
**Estado:** PROPUESTA

---

## Contexto

Actualmente, el inline de "Proyectos Asignados" en el perfil del alumno muestra una lista simple de servicios desplegados. Se propone mejorar la visualización para hacerla más compacta, informativa y profesional.

---

## Propuesta de Mejora

### Cambios en la Tabla Inline

**Estructura actual:**
- Nombre del Proyecto
- Asignatura Asociada
- Servicios Desplegados (lista completa con iconos)
- Fecha
- Hora
- ¿Eliminar?

**Estructura propuesta:**
- Nombre del Proyecto
- Asignatura Asociada
- **Servicios** (resumen compacto)
- **Estado** (estado general del proyecto)
- Fecha

---

## Implementación Propuesta

### 1. Resumen Compacto de Servicios

**Campo:** `get_services_summary`

**Visualización:**
```
🐳 2 total
🟢 1 running | 🔴 1 stopped
```

**Ventajas:**
- Más compacto (2 líneas vs lista completa)
- Información agregada de un vistazo
- Mantiene iconos visuales

---

### 2. Estado General del Proyecto

**Campo:** `get_project_status`

**Estados posibles:**
- ✅ **Activo** (verde) - Todos los servicios running
- 🟡 **Parcial** (naranja) - Algunos servicios running
- ❌ **Detenido** (rojo) - Ningún servicio running
- ⚪ **Sin servicios** (gris) - No hay servicios desplegados

**Ventajas:**
- Estado del proyecto de un vistazo
- Colores consistentes con el resto del admin
- Ayuda a identificar problemas rápidamente

---

### 3. Reorganización de Columnas

**Eliminar:**
- Columna "Hora" (redundante con Fecha)
- Columna "¿Eliminar?" (se puede usar el botón de eliminar estándar)

**Mantener:**
- Nombre del Proyecto
- Asignatura
- Fecha

**Agregar:**
- Servicios (resumen)
- Estado (general)

---

## Código Propuesto

```python
class UserProjectInlineForProfile(admin.TabularInline):
    model = UserProject
    fk_name = "user_profile"
    extra = 0
    autocomplete_fields = ("subject",)
    readonly_fields = ('get_services_summary', 'get_project_status')
    fields = ('place', 'subject', 'get_services_summary', 'get_project_status', 'date')
    
    def get_services_summary(self, obj):
        """Muestra resumen de servicios desplegados"""
        if not obj or not obj.pk:
            return "-"
        
        from containers.models import Service
        from django.utils.html import format_html
        
        services = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed')
        
        total = services.count()
        running = services.filter(status='running').count()
        stopped = services.filter(status='stopped').count()
        
        if total == 0:
            return format_html('<span style="color: gray;">📦 0 servicios</span>')
        
        return format_html(
            '<span style="font-weight: bold;">🐳 {} total</span><br>'
            '<span style="color: green;">🟢 {} running</span> | '
            '<span style="color: red;">🔴 {} stopped</span>',
            total, running, stopped
        )
    
    get_services_summary.short_description = 'Servicios'
    
    def get_project_status(self, obj):
        """Muestra estado general del proyecto"""
        if not obj or not obj.pk:
            return "-"
        
        from containers.models import Service
        from django.utils.html import format_html
        
        services = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed')
        
        total = services.count()
        running = services.filter(status='running').count()
        
        if total == 0:
            return format_html('<span style="color: gray;">⚪ Sin servicios</span>')
        
        if running == total:
            return format_html('<span style="color: green; font-weight: bold;">✅ Activo</span>')
        elif running > 0:
            return format_html('<span style="color: orange; font-weight: bold;">🟡 Parcial</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">❌ Detenido</span>')
    
    get_project_status.short_description = 'Estado'
```

---

## Beneficios

### UX
- **Más compacta:** Menos espacio vertical, más información visible
- **Más clara:** Estado del proyecto de un vistazo
- **Más profesional:** Diseño consistente con el resto del admin

### Performance
- **Mismas queries:** No aumenta el número de consultas a BD
- **Agregación eficiente:** Usa `.count()` y `.filter()` de Django

### Mantenibilidad
- **Código limpio:** Métodos bien documentados
- **Reutilizable:** Lógica puede usarse en otros inlines
- **Consistente:** Mismos iconos y colores que en UserProjectAdmin

---

## Alternativas Consideradas

### Opción 1: Lista completa de servicios (ACTUAL)
**Pros:** Muestra todos los nombres de servicios  
**Contras:** Ocupa mucho espacio, difícil de escanear visualmente

### Opción 2: Solo contador (MUY SIMPLE)
**Pros:** Muy compacto  
**Contras:** Pierde información de estado (running vs stopped)

### Opción 3: Resumen + Estado (PROPUESTA) ✅
**Pros:** Balance perfecto entre información y espacio  
**Contras:** Ninguno significativo

---

## Criterios de Aceptación

- [ ] Inline muestra resumen de servicios (total, running, stopped)
- [ ] Inline muestra estado general del proyecto
- [ ] Columnas reorganizadas (sin Hora ni Eliminar)
- [ ] Iconos y colores consistentes
- [ ] Performance no degradado
- [ ] Tests de usabilidad positivos

---

## Notas de Implementación

- Mantener compatibilidad con proyectos sin servicios
- Manejar casos edge (proyectos nuevos, sin pk)
- Usar `format_html` para seguridad (prevenir XSS)
- Documentar métodos con docstrings claros

---

## Prioridad y Timing

**Prioridad:** BAJA (mejora cosmética, no bloqueante)  
**Esfuerzo:** 30 minutos  
**Impacto:** MEDIO (mejora UX para profesores/admins)  
**Cuándo implementar:** Después de completar features críticas
