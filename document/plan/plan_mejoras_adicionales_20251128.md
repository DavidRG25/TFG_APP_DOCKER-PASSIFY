# Plan de Mejoras Adicionales: Admin Panel PaaSify

**Fecha:** 2025-11-28  
**Versión:** 4.4.0 (Futuro)  
**Estado:** 📋 Planificado

---

## 🎯 Objetivo

Documentar mejoras adicionales identificadas durante la implementación de las Fases 1-6 que pueden implementarse en futuras iteraciones.

---

## 📊 Mejoras por Módulo

### 🔐 User Admin (Fase 1)

#### Mejora 1.1: Exportación de Usuarios
**Prioridad:** Media  
**Complejidad:** Baja

**Descripción:**
Agregar acción para exportar lista de usuarios a CSV/Excel con filtros aplicados.

**Beneficios:**
- Facilita reportes para administradores
- Permite análisis externo de datos

**Implementación:**
```python
@admin.action(description="Exportar usuarios seleccionados a CSV")
def export_users_csv(self, request, queryset):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Nombre', 'Rol', 'Fecha Registro'])
    
    for user in queryset:
        writer.writerow([
            user.username,
            user.email,
            user.get_full_name(),
            # ... rol, fecha
        ])
    
    return response
```

---

#### Mejora 1.2: Gráfico de Distribución de Roles
**Prioridad:** Baja  
**Complejidad:** Media

**Descripción:**
Agregar widget en el dashboard del admin mostrando distribución de usuarios por rol.

**Beneficios:**
- Visualización rápida de estadísticas
- Mejor comprensión de la base de usuarios

**Tecnologías:**
- Chart.js o similar
- Django admin dashboard customization

---

#### Mejora 1.3: Última Conexión del Usuario
**Prioridad:** Alta  
**Complejidad:** Baja

**Descripción:**
Agregar columna `last_login` en list_display con formato amigable.

**Implementación:**
```python
def get_last_login(self, obj):
    if obj.last_login:
        from django.utils import timezone
        diff = timezone.now() - obj.last_login
        if diff.days == 0:
            return "Hoy"
        elif diff.days == 1:
            return "Ayer"
        else:
            return f"Hace {diff.days} días"
    return "Nunca"
get_last_login.short_description = 'Última conexión'
```

---

### 🐳 Service Admin (Fase 3)

#### Mejora 3.1: Filtro por Tipo de Imagen
**Prioridad:** Alta  
**Complejidad:** Baja

**Descripción:**
Agregar filtro en sidebar para filtrar servicios por tipo de imagen.

**Implementación:**
```python
class ServiceImageTypeFilter(admin.SimpleListFilter):
    title = 'Tipo de imagen'
    parameter_name = 'image_type'
    
    def lookups(self, request, model_admin):
        return [
            ('web', '🌐 Web'),
            ('database', '🗄️ Database'),
            ('api', '🚀 API'),
            ('misc', '📦 Misc'),
        ]
    
    def queryset(self, request, queryset):
        # Filtrar servicios según tipo de AllowedImage
        pass

list_filter = ('status', 'created_at', ServiceImageTypeFilter)
```

---

#### Mejora 3.2: Acción Bulk: Reiniciar Servicios
**Prioridad:** Alta  
**Complejidad:** Media

**Descripción:**
Agregar acción para reiniciar múltiples servicios seleccionados.

**Beneficios:**
- Ahorra tiempo en mantenimiento
- Útil para actualizaciones masivas

**Implementación:**
```python
@admin.action(description="Reiniciar servicios seleccionados")
def restart_services(self, request, queryset):
    from .docker_client import get_docker_client
    client = get_docker_client()
    
    success = 0
    errors = 0
    
    for service in queryset:
        try:
            container = client.containers.get(service.container_id)
            container.restart()
            success += 1
        except Exception as e:
            errors += 1
    
    self.message_user(
        request,
        f"Reiniciados: {success}, Errores: {errors}"
    )
```

---

#### Mejora 3.3: Logs en Tiempo Real
**Prioridad:** Media  
**Complejidad:** Alta

**Descripción:**
Integrar visor de logs en tiempo real usando WebSockets.

**Tecnologías:**
- Django Channels
- WebSockets
- Xterm.js (ya usado en terminal)

**Beneficios:**
- Debugging más eficiente
- No necesita refrescar página

---

#### Mejora 3.4: Gráfico de Uso de Recursos
**Prioridad:** Baja  
**Complejidad:** Alta

**Descripción:**
Mostrar gráfico de CPU/RAM del contenedor en el formulario de edición.

**Tecnologías:**
- Docker stats API
- Chart.js
- Actualización periódica con AJAX

---

### 📚 Subject Admin (Fase 4)

#### Mejora 4.1: Gráfico de Distribución de Alumnos
**Prioridad:** Baja  
**Complejidad:** Media

**Descripción:**
Mostrar gráfico de barras con número de alumnos por asignatura.

**Ubicación:**
- Dashboard del admin
- O en la vista de lista de asignaturas

---

#### Mejora 4.2: Exportar Lista de Alumnos
**Prioridad:** Media  
**Complejidad:** Baja

**Descripción:**
Acción para exportar lista de alumnos de una asignatura a CSV.

**Campos a exportar:**
- Nombre completo
- Email
- Username
- Servicios activos
- Última conexión

---

#### Mejora 4.3: Enviar Email a Alumnos
**Prioridad:** Media  
**Complejidad:** Media

**Descripción:**
Acción bulk para enviar email a todos los alumnos de asignaturas seleccionadas.

**Funcionalidades:**
- Template de email personalizable
- Variables dinámicas (nombre, asignatura, etc.)
- Envío asíncrono con Celery

---

### 👤 UserProfile Admin (Fase 5)

#### Mejora 5.1: Filtro por Rol
**Prioridad:** Alta  
**Complejidad:** Baja

**Descripción:**
Agregar filtro personalizado para filtrar perfiles por rol del usuario.

**Implementación:**
```python
class UserRoleFilter(admin.SimpleListFilter):
    title = 'Rol'
    parameter_name = 'user_role'
    
    def lookups(self, request, model_admin):
        return [
            ('teacher', '👨‍🏫 Profesor'),
            ('student', '👨‍🎓 Alumno'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'teacher':
            return queryset.filter(
                user__groups__name__in=TEACHER_GROUP_NAMES
            ).distinct()
        elif self.value() == 'student':
            return queryset.filter(
                user__groups__name__in=STUDENT_GROUP_NAMES
            ).distinct()
        return queryset
```

---

#### Mejora 5.2: Acción: Resetear Tokens
**Prioridad:** Media  
**Complejidad:** Baja

**Descripción:**
Acción bulk para regenerar tokens API de usuarios seleccionados.

**Nota:** Ya existe `refresh_api_tokens`, pero puede mejorarse con confirmación.

---

#### Mejora 5.3: Mostrar Última Conexión
**Prioridad:** Alta  
**Complejidad:** Baja

**Descripción:**
Agregar columna con última conexión del usuario del perfil.

---

### 📁 UserProject Admin (Fase 6)

#### Mejora 6.1: Filtro por Estado del Proyecto
**Prioridad:** Alta  
**Complejidad:** Media

**Descripción:**
Filtro para mostrar solo proyectos activos, parcialmente activos, detenidos o sin servicios.

**Implementación:**
```python
class ProjectStatusFilter(admin.SimpleListFilter):
    title = 'Estado del proyecto'
    parameter_name = 'project_status'
    
    def lookups(self, request, model_admin):
        return [
            ('active', '✅ Todos activos'),
            ('partial', '⚠️ Parcialmente activo'),
            ('stopped', '❌ Detenido'),
            ('empty', '⚪ Sin servicios'),
        ]
    
    def queryset(self, request, queryset):
        # Lógica compleja para filtrar según estado
        pass
```

---

#### Mejora 6.2: Progreso del Proyecto
**Prioridad:** Baja  
**Complejidad:** Alta

**Descripción:**
Mostrar barra de progreso del proyecto basada en:
- Servicios creados vs esperados
- Servicios funcionando vs totales
- Tareas completadas (si se implementa sistema de tareas)

**Visualización:**
```
Progreso: [████████░░] 80%
```

---

#### Mejora 6.3: Acción Bulk: Reiniciar Servicios del Proyecto
**Prioridad:** Media  
**Complejidad:** Media

**Descripción:**
Reiniciar todos los servicios de los proyectos seleccionados.

---

## 🎨 Mejoras Generales de UX

### Mejora G.1: Dark Mode
**Prioridad:** Baja  
**Complejidad:** Media

**Descripción:**
Agregar modo oscuro al admin panel.

**Tecnologías:**
- Django admin theming
- CSS variables
- LocalStorage para preferencia

---

### Mejora G.2: Breadcrumbs Mejorados
**Prioridad:** Baja  
**Complejidad:** Baja

**Descripción:**
Mejorar breadcrumbs con iconos y mejor navegación.

---

### Mejora G.3: Tooltips Informativos
**Prioridad:** Media  
**Complejidad:** Baja

**Descripción:**
Agregar tooltips con información adicional en columnas complejas.

**Tecnología:**
- Bootstrap tooltips
- Django admin Media class

---

### Mejora G.4: Búsqueda Avanzada
**Prioridad:** Media  
**Complejidad:** Alta

**Descripción:**
Implementar búsqueda avanzada con múltiples criterios.

**Funcionalidades:**
- Búsqueda por rango de fechas
- Búsqueda por múltiples campos simultáneamente
- Guardar búsquedas frecuentes

---

## 🔒 Mejoras de Seguridad

### Mejora S.1: Auditoría de Cambios
**Prioridad:** Alta  
**Complejidad:** Media

**Descripción:**
Registrar todos los cambios realizados en el admin.

**Tecnología:**
- Django Simple History
- O implementación custom con signals

**Información a registrar:**
- Usuario que hizo el cambio
- Fecha y hora
- Campos modificados
- Valores anteriores y nuevos

---

### Mejora S.2: Confirmación de Acciones Críticas
**Prioridad:** Alta  
**Complejidad:** Baja

**Descripción:**
Agregar confirmación para acciones destructivas:
- Eliminar usuario
- Eliminar servicio
- Resetear tokens

---

### Mejora S.3: Permisos Granulares
**Prioridad:** Media  
**Complejidad:** Alta

**Descripción:**
Implementar permisos más específicos:
- Ver pero no editar
- Editar solo sus propios objetos
- Permisos por campo

---

## 📊 Priorización de Mejoras

### Alta Prioridad (Implementar próximamente):
1. Filtro por tipo de imagen (Service)
2. Acción bulk: Reiniciar servicios
3. Última conexión del usuario
4. Filtro por rol (UserProfile)
5. Filtro por estado del proyecto
6. Auditoría de cambios
7. Confirmación de acciones críticas

### Media Prioridad (Considerar):
1. Exportación de usuarios
2. Exportar lista de alumnos
3. Enviar email a alumnos
4. Resetear tokens mejorado
5. Reiniciar servicios del proyecto
6. Tooltips informativos
7. Búsqueda avanzada

### Baja Prioridad (Futuro lejano):
1. Gráficos de distribución
2. Logs en tiempo real
3. Gráfico de uso de recursos
4. Progreso del proyecto
5. Dark mode
6. Breadcrumbs mejorados

---

## 📅 Roadmap Sugerido

### Versión 4.4.0 (Próxima)
- Filtros adicionales (tipo imagen, estado proyecto, rol)
- Última conexión
- Acción bulk: Reiniciar servicios
- Confirmación de acciones críticas

### Versión 4.5.0
- Exportaciones (usuarios, alumnos)
- Enviar emails
- Tooltips
- Auditoría de cambios

### Versión 4.6.0
- Gráficos y visualizaciones
- Búsqueda avanzada
- Permisos granulares

### Versión 5.0.0 (Major)
- Logs en tiempo real
- Dark mode
- Dashboard completamente rediseñado
- Progreso de proyectos

---

## ✅ Conclusión

Este plan documenta **30+ mejoras adicionales** identificadas durante la implementación de las Fases 1-6.

**Próximos pasos:**
1. Revisar y priorizar con el equipo
2. Estimar esfuerzo de cada mejora
3. Planificar sprints futuros
4. Implementar mejoras de alta prioridad

---

**Estado:** 📋 Planificado y documentado
