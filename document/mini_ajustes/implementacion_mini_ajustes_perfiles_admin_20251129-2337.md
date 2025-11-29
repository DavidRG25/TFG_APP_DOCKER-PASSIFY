# Implementacion: Mejoras en Perfiles de Alumnos y Profesores - Admin Panel

**Fecha:** 2025-11-29 23:37  
**Tipo:** Mini ajustes y mejoras UX  
**Modulos afectados:** `paasify/admin.py`, `paasify/models/StudentModel.py`, `paasify/models/__init__.py`

---

## Contexto

Durante el testing del Admin Panel, se identificaron varias areas de mejora en la gestion de perfiles de alumnos:

1. Formulario confuso que requeria vincular usuarios existentes
2. Falta de seccion dedicada para perfiles de profesores
3. Campos de perfil editables cuando deberian ser readonly
4. Formularios vacios obligatorios en inlines
5. Filtros de profesores no funcionando correctamente

---

## Cambios Implementados

### 1. Formulario de Creacion Directa de Usuarios

**Problema:**
- El formulario de "Agregar Perfil de Alumno" requeria seleccionar un usuario existente
- Flujo de 2 pasos: crear usuario → crear perfil
- Confuso para administradores

**Solucion:**
- Formulario completo de creacion de usuario integrado
- Rol "Student" asignado automaticamente
- Todo en un solo paso

**Archivos modificados:**
- `paasify/admin.py`: `UserProfileAdminForm`

**Campos del formulario:**
```python
# Campos de usuario
username = forms.CharField(label="Nombre de usuario")
email = forms.EmailField(label="Direccion de email")
first_name = forms.CharField(label="Nombre", required=False)
last_name = forms.CharField(label="Apellido", required=False)

# Generacion de contraseña
generate_password = forms.BooleanField(
    label="Generar contraseña automaticamente",
    required=False,
    help_text="Si se marca, se generara una contraseña aleatoria segura"
)
password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
password2 = forms.CharField(label="Confirmacion de contraseña", widget=forms.PasswordInput)
```

**Fieldsets dinamicos:**
- **Al crear:** Solo muestra "Datos de Usuario" y "Contraseña"
- **Al editar:** Muestra todos los fieldsets incluyendo "Informacion del Perfil" y "Token API"

---

### 2. Generacion Automatica de Contraseña

**Funcionalidad:**
- Checkbox "Generar contraseña automaticamente"
- Genera contraseñas aleatorias de 12 caracteres
- Usa `make_random_password()` de Django

**Validacion:**
```python
if generate_password:
    random_password = make_random_password(length=12)
    cleaned["password1"] = random_password
    cleaned["password2"] = random_password
else:
    if not password1 or not password2:
        raise forms.ValidationError(
            "Debes proporcionar una contraseña o marcar 'Generar contraseña automaticamente'"
        )
```

---

### 3. Nueva Seccion: Perfiles de Profesores

**Implementacion:**
- Modelo proxy `TeacherProfile` basado en `UserProfile`
- Admin separado `TeacherProfileAdmin`
- Mismo formulario pero asigna rol "Teacher" automaticamente

**Archivos modificados:**
- `paasify/models/StudentModel.py`: Agregado `TeacherProfile`
- `paasify/models/__init__.py`: Exportado `TeacherProfile`
- `paasify/admin.py`: Agregado `TeacherProfileAdminForm` y `TeacherProfileAdmin`

**Modelo proxy:**
```python
class TeacherProfile(UserProfile):
    """
    Modelo proxy para perfiles de profesores.
    Usa la misma tabla que UserProfile pero con un admin separado.
    """
    
    class Meta:
        proxy = True
        verbose_name = "Perfil de profesor"
        verbose_name_plural = "Perfiles de profesores"
```

**Diferencias con UserProfileAdmin:**
- Asigna rol "Teacher" en lugar de "Student"
- Sin inlines de proyectos
- Cuenta asignaturas que imparte (en lugar de asignaturas matriculadas)
- Filtro por grupos Teacher

---

### 4. Campos Readonly con Diseño Bonito

**Problema:**
- Campos `nombre` y `year` eran editables
- Causaba inconsistencias con datos del usuario

**Solucion:**
- Convertidos a readonly fields
- Diseño visual mejorado con cajas de colores

**Implementacion:**

**Perfiles de Alumnos:**
```python
def get_nombre_display(self, obj):
    """Muestra el nombre completo del alumno de forma bonita"""
    from django.utils.html import format_html
    if obj and obj.nombre:
        return format_html(
            '<div style="background: #e3f2fd; padding: 10px; border-radius: 4px; border-left: 3px solid #2196f3;">'
            '<strong style="color: #1976d2;">👤 {}</strong>'
            '</div>',
            obj.nombre
        )
    return format_html('<span style="color: #999;">No especificado</span>')
```

**Perfiles de Profesores:**
- Caja verde con icono 👨‍🏫 para nombre
- Caja naranja con icono 📧 para email

---

### 5. Actualizacion Automatica de Campos de Perfil

**Problema:**
- Al editar `first_name` o `last_name` del usuario, el campo `nombre` del perfil no se actualizaba
- Causaba datos desincronizados

**Solucion:**
- Modificado metodo `save()` para SIEMPRE actualizar `nombre` y `year`

**Antes:**
```python
if not profile.nombre:
    profile.nombre = user.get_full_name() or user.username
```

**Despues:**
```python
# SIEMPRE actualizar nombre/year desde los datos del usuario
profile.nombre = user.get_full_name() or user.username
profile.year = user.email or f"{user.username}@pendiente.local"
```

---

### 6. Fix: Formularios Vacios Obligatorios en Inlines

**Problema:**
- `UserProjectInlineForSubject` tenia `extra = 1`
- Creaba formulario vacio obligatorio al agregar/editar asignatura
- Usuario debia rellenarlo o eliminarlo manualmente

**Solucion:**
```python
class UserProjectInlineForSubject(admin.TabularInline):
    model = UserProject
    fk_name = "subject"
    extra = 0  # No crear formularios vacios automaticamente
```

**Aplicado tambien a:**
- `UserProjectInlineForProfile`

---

### 7. Fix: Filtro de Profesores Case-Insensitive

**Problema:**
- Filtro de `TeacherProfileAdmin` era case-sensitive
- No encontraba profesores con grupos "Teacher", "teacher", "Profesor", etc.

**Solucion:**
```python
def get_queryset(self, request):
    """Filtrar solo perfiles con usuarios Teacher"""
    from django.db.models import Q
    qs = super().get_queryset(request)
    
    # Construir filtro OR para todos los nombres de grupos Teacher
    teacher_filter = Q()
    for group_name in [DEFAULT_TEACHER_GROUP] + list(TEACHER_GROUP_NAMES):
        teacher_filter |= Q(user__groups__name__iexact=group_name)
    
    return qs.filter(
        user__isnull=False
    ).filter(teacher_filter).distinct()
```

---

### 8. Fix: KeyError en Formulario

**Problema:**
- `KeyError: 'nombre'` al acceder a campos en `__init__`
- Campos no estaban en `Meta.fields` cuando se ocultaban con `get_fieldsets`

**Solucion:**
1. Agregados todos los campos a `Meta.fields`
2. Protegido acceso con `if "nombre" in self.fields:`

```python
class Meta:
    model = UserProfile
    fields = ["username", "email", "first_name", "last_name", 
              "generate_password", "password1", "password2", "nombre", "year"]

# Proteger acceso
if "nombre" in self.fields:
    self.fields["nombre"].help_text = "Nombre completo del alumno"
```

---

### 9. Mejoras en Subject Admin

**Cambios:**
- Quitado `autocomplete_fields = ("teacher_user",)` que ignoraba el queryset del formulario
- Agregados fieldsets con diseño de franjas:
  - Informacion Basica
  - Profesor Asignado
  - Alumnos Matriculados

**Filtro de profesores funcionando:**
```python
self.fields["teacher_user"].queryset = User.objects.filter(
    groups__name__in=[*TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP]
).distinct().order_by('username')
```

---

## Resumen de Archivos Modificados

### Archivos Modificados:
1. `paasify/admin.py`
   - `UserProfileAdminForm`: Formulario completo de creacion
   - `UserProfileAdmin`: Fieldsets dinamicos, readonly fields bonitos
   - `TeacherProfileAdminForm`: Formulario para profesores
   - `TeacherProfileAdmin`: Admin completo para profesores
   - `SubjectAdmin`: Fieldsets y filtros mejorados
   - `UserProjectInlineForSubject`: `extra = 0`
   - `UserProjectInlineForProfile`: `extra = 0`

2. `paasify/models/StudentModel.py`
   - Agregado modelo proxy `TeacherProfile`

3. `paasify/models/__init__.py`
   - Exportado `UserProfile` y `TeacherProfile`

---

## Beneficios

### UX Mejorada:
- ✅ Creacion de perfiles en un solo paso
- ✅ Generacion automatica de contraseñas
- ✅ Campos readonly con diseño visual claro
- ✅ Fieldsets organizados con franjas azules
- ✅ Sin formularios vacios obligatorios

### Consistencia de Datos:
- ✅ Campos de perfil siempre sincronizados con usuario
- ✅ Rol asignado automaticamente (Student/Teacher)
- ✅ Validacion robusta de contraseñas

### Organizacion:
- ✅ Seccion separada para profesores
- ✅ Filtros funcionando correctamente
- ✅ Contador de asignaturas por perfil

---

## Testing Realizado

### Casos Probados:
1. ✅ Crear perfil de alumno con contraseña manual
2. ✅ Crear perfil de alumno con contraseña automatica
3. ✅ Editar perfil de alumno (nombre se actualiza)
4. ✅ Crear perfil de profesor
5. ✅ Filtro de profesores muestra solo Teachers
6. ✅ Crear asignatura sin formularios vacios
7. ✅ Selector de profesor muestra solo Teachers

### Bugs Corregidos:
1. ✅ KeyError al crear perfil
2. ✅ Nombre no se actualiza al editar
3. ✅ Formularios vacios obligatorios
4. ✅ Filtro de profesores case-sensitive
5. ✅ Perfiles de profesores vacio

---

## Notas Importantes

### Usuarios Existentes:
- Usuarios Teacher creados antes de esta implementacion NO tienen UserProfile
- Solucion: Crear perfil manualmente desde "Perfiles de profesores"
- Alternativa: Crear comando de migracion para asociar automaticamente

### Campos Autocompletados:
- `nombre` = `first_name + last_name` o `username`
- `year` = `email` o `username@pendiente.local`
- Se actualizan automaticamente al editar usuario

### Modelo Proxy:
- `TeacherProfile` usa la misma tabla que `UserProfile`
- Permite admin separado sin duplicar datos
- Filtrado automatico por rol

---

## Proximos Pasos Sugeridos

1. Crear comando de migracion para usuarios Teacher existentes
2. Agregar validacion de email unico
3. Implementar notificacion de contraseña generada
4. Agregar exportacion de credenciales en PDF
5. Implementar cambio masivo de contraseñas

---

**Documentado por:** Antigravity AI  
**Fecha:** 2025-11-29 23:37  
**Sesion:** Testing Admin Panel - Checkpoint 6
