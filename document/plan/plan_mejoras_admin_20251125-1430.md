# Plan de Implementacion: Mejoras del Panel de Administracion Django
_Fecha de creacion: 2025-11-25 14:30_

## Objetivo General

Mejorar significativamente la experiencia de administracion en el panel Django de PaaSify, agregando funcionalidades avanzadas de gestion de usuarios, imagenes Docker, servicios, asignaturas y proyectos. El objetivo es hacer el admin mas intuitivo, informativo y eficiente para los administradores del sistema.

---

## Estructura del Plan

El plan se divide en **6 fases principales**, cada una enfocada en un modelo/seccion especifica del admin:

1. **Fase 1:** Mejoras en Admin de Usuarios (`auth.User`)
2. **Fase 2:** Mejoras en AllowedImage
3. **Fase 3:** Mejoras en Service
4. **Fase 4:** Mejoras en Subject
5. **Fase 5:** Mejoras en UserProfile
6. **Fase 6:** Mejoras en UserProject

---

## FASE 1: Mejoras en Admin de Usuarios

### Objetivo
Mejorar la gestion de usuarios del sistema, facilitando la creacion, busqueda y filtracion por roles.

### 1.1. Mejoras en Lista de Usuarios
**URL:** `http://127.0.0.1:8000/admin/auth/user/`

#### Cambios en `list_display`:
```python
list_display = [
    'username',
    'email',
    'get_full_name_display',  # Nuevo
    'get_role_display',       # Nuevo
    'get_subjects_count',     # Nuevo
    'get_active_services',    # Nuevo
    'date_joined',            # Nuevo
    'is_active',
    'is_staff',
]
```

#### Nuevos metodos a implementar:

**`get_role_display(obj)`**
- Retorna: "Admin", "Teacher", "Student" o "Sin rol"
- Logica: Verificar grupos del usuario
- Color: Badge con color segun rol (rojo=admin, azul=teacher, verde=student)

**`get_subjects_count(obj)`**
- Retorna: Numero de asignaturas
- Logica:
  - Si es Teacher: `Subject.objects.filter(teacher_user=obj).count()`
  - Si es Student: `obj.subject_set.count()`
  - Otros: "-"

**`get_active_services(obj)`**
- Retorna: Numero de servicios activos (status='running')
- Logica: `Service.objects.filter(owner=obj, status='running').count()`

**`get_full_name_display(obj)`**
- Retorna: `f"{obj.first_name} {obj.last_name}".strip() or "-"`

#### Filtros (`list_filter`):
```python
list_filter = [
    'is_active',
    'is_staff',
    'is_superuser',
    'date_joined',
    RoleFilter,  # Nuevo filtro personalizado
]
```

**`RoleFilter` (Custom Filter):**
```python
class RoleFilter(admin.SimpleListFilter):
    title = 'Rol'
    parameter_name = 'role'
    
    def lookups(self, request, model_admin):
        return [
            ('admin', 'Administrador'),
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
            ('none', 'Sin rol'),
        ]
    
    def queryset(self, request, queryset):
        # Filtrar por grupo
```

#### Busqueda mejorada (`search_fields`):
```python
search_fields = [
    'username',
    'email',
    'first_name',
    'last_name',
    'user_profile__nombre',  # Buscar por nombre de perfil
]
```

---

### 1.2. Mejoras en Creacion/Edicion de Usuario
**URL:** `http://127.0.0.1:8000/admin/auth/user/add/`

#### Crear `UserAdminForm` personalizado:

**Campos adicionales:**
```python
class UserAdminForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[
            ('', '--- Seleccionar rol ---'),
            ('admin', 'Administrador'),
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
        ],
        required=True,
        label='Rol del usuario',
        help_text='Selecciona el rol que tendra este usuario en el sistema'
    )
    
    auto_generate_password = forms.BooleanField(
        required=False,
        initial=True,
        label='Generar contraseña automaticamente',
        help_text='Si se marca, se generara una contraseña aleatoria segura'
    )
    
    first_name = forms.CharField(
        required=True,
        label='Nombre',
        help_text='Nombre del usuario'
    )
    
    last_name = forms.CharField(
        required=True,
        label='Apellidos',
        help_text='Apellidos del usuario'
    )
```

#### Logica en `save()`:

1. **Si `auto_generate_password=True`:**
   ```python
   import secrets
   import string
   
   def generate_password():
       alphabet = string.ascii_letters + string.digits + "!@#$%"
       password = ''.join(secrets.choice(alphabet) for i in range(12))
       return password
   ```

2. **Asignar grupo segun rol:**
   ```python
   if role == 'admin':
       user.is_staff = True
       user.is_superuser = True
   elif role == 'teacher':
       ensure_user_group(user, DEFAULT_TEACHER_GROUP)
   elif role == 'student':
       ensure_user_group(user, DEFAULT_STUDENT_GROUP)
   ```

3. **Crear UserProfile automaticamente:**
   ```python
   if role in ['student', 'teacher']:
       UserProfile.objects.get_or_create(
           user=user,
           defaults={
               'nombre': f"{user.first_name} {user.last_name}",
               'year': user.email,
           }
       )
   ```

4. **Mostrar contraseña generada:**
   ```python
   messages.success(
       request,
       f"Usuario creado. Contraseña generada: {password}"
   )
   ```

---

## FASE 2: Mejoras en AllowedImage

### Objetivo
Facilitar la gestion de imagenes Docker permitidas, con integracion con DockerHub y categorizacion por tipo.

### 2.1. Mejoras en Lista de Imagenes
**URL:** `http://127.0.0.1:8000/admin/containers/allowedimage/`

#### Agregar campo `image_type` al modelo:
```python
class AllowedImage(models.Model):
    IMAGE_TYPES = [
        ('web', 'Web / Frontend'),
        ('database', 'Base de Datos'),
        ('backend', 'Backend / API'),
        ('misc', 'Miscelanea'),
    ]
    
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES,
        default='misc',
        verbose_name='Tipo de imagen',
        help_text='Categoria de la imagen Docker'
    )
```

#### Migracion requerida:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Cambios en `list_display`:
```python
list_display = [
    'name',
    'tag',
    'get_type_icon',      # Nuevo
    'image_type',         # Nuevo
    'description',
    'created_at',         # Nuevo
]
```

#### Metodo `get_type_icon(obj)`:
```python
def get_type_icon(self, obj):
    icons = {
        'web': '🌐',
        'database': '🗄️',
        'backend': '⚙️',
        'misc': '📦',
    }
    return icons.get(obj.image_type, '📦')
get_type_icon.short_description = 'Tipo'
```

#### Filtros:
```python
list_filter = [
    'image_type',
    'created_at',
]
```

---

### 2.2. Mejoras en Creacion/Edicion de Imagen
**URL:** `http://127.0.0.1:8000/admin/containers/allowedimage/add/`

#### Modificar `AllowedImageForm`:

**Agregar campo de tipo:**
```python
class AllowedImageForm(forms.ModelForm):
    image_type = forms.ChoiceField(
        choices=AllowedImage.IMAGE_TYPES,
        required=True,
        label='Tipo de imagen',
        widget=forms.RadioSelect,
    )
    
    suggested_tags = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'readonly': True}),
        required=False,
        label='Tags disponibles en DockerHub',
        help_text='Tags encontrados automaticamente'
    )
```

#### Funcionalidad de consulta a DockerHub:

**Metodo `_get_docker_hub_tags()` mejorado:**
```python
def _get_docker_hub_tags(self, name):
    """
    Consulta DockerHub para obtener tags disponibles.
    Soporta imagenes oficiales (library/) y de usuarios.
    """
    # Intentar primero como imagen oficial
    url = f"https://hub.docker.com/v2/repositories/library/{name}/tags/"
    response = requests.get(url, params={'page_size': 50})
    
    if response.status_code != 200:
        # Intentar como imagen de usuario (ej: bitnami/nginx)
        if '/' in name:
            url = f"https://hub.docker.com/v2/repositories/{name}/tags/"
            response = requests.get(url, params={'page_size': 50})
    
    if response.status_code != 200:
        return []
    
    results = response.json().get('results', [])
    tags = [r['name'] for r in results]
    
    # Ordenar: latest primero, luego numericos, luego alfabeticos
    def sort_key(tag):
        if tag == 'latest':
            return (0, tag)
        elif tag.replace('.', '').isdigit():
            return (1, tag)
        else:
            return (2, tag)
    
    return sorted(tags, key=sort_key)
```

#### JavaScript para autocompletar tag:
```javascript
// Agregar en Media class del form
class Media:
    js = ('admin/js/allowedimage_autocomplete.js',)
```

**Archivo `allowedimage_autocomplete.js`:**
```javascript
django.jQuery(document).ready(function($) {
    $('#id_name').on('blur', function() {
        var imageName = $(this).val();
        if (!imageName) return;
        
        // Llamar a endpoint custom para obtener tags
        $.get('/admin/containers/allowedimage/get-tags/', {name: imageName}, function(data) {
            $('#id_suggested_tags').val(data.tags.join('\\n'));
            
            // Actualizar selector de tag si existe
            if (data.tags.length > 0 && !$('#id_tag').val()) {
                $('#id_tag').val(data.tags[0]);
            }
        });
    });
});
```

#### Estructura preparada para funcionalidades futuras:

**Nota en el formulario:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # Agregar help_text segun tipo
    type_help = {
        'web': 'Funcionalidad futura: Editor HTML/CSS/JS integrado',
        'database': 'Funcionalidad futura: Configuracion de usuario/password',
        'backend': 'Funcionalidad futura: Terminal interactiva y logs en tiempo real',
        'misc': 'Sin funcionalidades adicionales',
    }
    
    self.fields['image_type'].help_text = (
        'Selecciona el tipo de imagen. '
        'Esto habilitara funcionalidades especificas en el futuro.'
    )
```

---

## FASE 3: Mejoras en Service

### Objetivo
Mejorar la visualizacion y edicion de servicios/contenedores, agregando informacion util y tooltips explicativos.

### 3.1. Mejoras en Lista de Servicios
**URL:** `http://127.0.0.1:8000/admin/containers/service/`

#### Cambios en `list_display`:
```python
list_display = [
    'name',
    'owner',
    'image',
    'get_image_type',      # Nuevo
    'assigned_port',
    'status',
    'get_volume_info',     # Nuevo
    'created_at',
]
```

#### Nuevos metodos:

**`get_image_type(obj)`:**
```python
def get_image_type(self, obj):
    # Buscar AllowedImage correspondiente
    try:
        allowed = AllowedImage.objects.get(
            name=obj.image.split(':')[0],
            tag=obj.image.split(':')[1] if ':' in obj.image else 'latest'
        )
        icons = {'web': '🌐', 'database': '🗄️', 'backend': '⚙️', 'misc': '📦'}
        return f"{icons.get(allowed.image_type, '📦')} {allowed.get_image_type_display()}"
    except AllowedImage.DoesNotExist:
        return "❓ Desconocido"
get_image_type.short_description = 'Tipo'
```

**`get_volume_info(obj)`:**
```python
def get_volume_info(self, obj):
    if obj.volumes:
        count = len(obj.volumes) if isinstance(obj.volumes, dict) else 0
        return f"📁 {count} volumenes"
    return "-"
get_volume_info.short_description = 'Volumenes'
```

---

### 3.2. Mejoras en Creacion/Edicion de Servicio
**URL:** `http://127.0.0.1:8000/admin/containers/service/<id>/change/`

#### Crear `ServiceAdminForm`:

```python
class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        help_texts = {
            'name': 'Nombre unico del servicio. Debe ser descriptivo y sin espacios.',
            'image': 'Imagen Docker a utilizar (ej: nginx:latest, mysql:8.0)',
            'assigned_port': 'Puerto externo asignado automaticamente (40000-50000)',
            'status': 'Estado actual del contenedor',
            'env_vars': 'Variables de entorno en formato JSON: {"KEY": "value"}',
            'volumes': 'Volumenes montados en formato JSON: {"/host/path": "/container/path"}',
            'dockerfile': 'Archivo Dockerfile personalizado (opcional)',
            'compose': 'Archivo docker-compose.yml (opcional)',
            'code': 'Codigo fuente comprimido (.zip)',
        }
        widgets = {
            'logs': forms.Textarea(attrs={'rows': 10, 'readonly': True}),
            'env_vars': forms.Textarea(attrs={'rows': 5}),
            'volumes': forms.Textarea(attrs={'rows': 5}),
        }
```

#### Agregar campos readonly informativos:

```python
readonly_fields = [
    'logs',
    'container_id',
    'created_at',
    'updated_at',
    'get_port_info',        # Nuevo
    'get_volume_details',   # Nuevo
    'get_image_options',    # Nuevo (placeholder)
]
```

**`get_port_info(obj)`:**
```python
def get_port_info(self, obj):
    if obj.assigned_port:
        return format_html(
            '<div style="background: #e8f5e9; padding: 10px; border-radius: 5px;">'
            '<strong>Puerto asignado:</strong> {}<br>'
            '<strong>Puerto interno:</strong> {}<br>'
            '<strong>URL de acceso:</strong> <a href="http://localhost:{}" target="_blank">'
            'http://localhost:{}</a>'
            '</div>',
            obj.assigned_port,
            obj.internal_port or 80,
            obj.assigned_port,
            obj.assigned_port
        )
    return "Puerto no asignado"
get_port_info.short_description = 'Informacion de Puerto'
```

**`get_volume_details(obj)`:**
```python
def get_volume_details(self, obj):
    if not obj.volumes:
        return "Sin volumenes configurados"
    
    html = '<ul>'
    for host_path, container_path in obj.volumes.items():
        html += f'<li><code>{host_path}</code> → <code>{container_path}</code></li>'
    html += '</ul>'
    return format_html(html)
get_volume_details.short_description = 'Detalles de Volumenes'
```

**`get_image_options(obj)` (Placeholder):**
```python
def get_image_options(self, obj):
    try:
        allowed = AllowedImage.objects.get(
            name=obj.image.split(':')[0],
            tag=obj.image.split(':')[1] if ':' in obj.image else 'latest'
        )
        
        if allowed.image_type == 'web':
            return format_html(
                '<div style="background: #fff3e0; padding: 10px; border-radius: 5px;">'
                '🌐 <strong>Imagen Web</strong><br>'
                '<em>Funcionalidad futura: Editor HTML/CSS/JS</em>'
                '</div>'
            )
        elif allowed.image_type == 'database':
            return format_html(
                '<div style="background: #e3f2fd; padding: 10px; border-radius: 5px;">'
                '🗄️ <strong>Base de Datos</strong><br>'
                '<em>Funcionalidad futura: Configuracion de credenciales</em>'
                '</div>'
            )
        elif allowed.image_type == 'backend':
            return format_html(
                '<div style="background: #f3e5f5; padding: 10px; border-radius: 5px;">'
                '⚙️ <strong>Backend/API</strong><br>'
                '<em>Funcionalidad futura: Terminal interactiva</em>'
                '</div>'
            )
    except AllowedImage.DoesNotExist:
        pass
    
    return "Sin opciones especiales"
get_image_options.short_description = 'Opciones de Imagen'
```

---

## FASE 4: Mejoras en Subject

### Objetivo
Mejorar la gestion de asignaturas, mostrando estadisticas relevantes y filtrando correctamente profesores.

### 4.1. Mejoras en Lista de Asignaturas
**URL:** `http://127.0.0.1:8000/admin/paasify/subject/`

#### Cambios en `list_display`:
```python
list_display = [
    'name',
    'teacher_user',
    'get_category_display',
    'genero',
    'get_students_count',    # Nuevo
    'get_services_count',    # Nuevo
    'created_at',            # Nuevo (agregar al modelo)
]
```

#### Nuevos metodos:

**`get_students_count(obj)`:**
```python
def get_students_count(self, obj):
    count = obj.students.count()
    return f"👥 {count}"
get_students_count.short_description = 'Alumnos'
```

**`get_services_count(obj)`:**
```python
def get_services_count(self, obj):
    from containers.models import Service
    count = Service.objects.filter(subject=obj).exclude(status='removed').count()
    return f"🐳 {count}"
get_services_count.short_description = 'Servicios'
```

---

### 4.2. Mejoras en Creacion/Edicion de Asignatura

#### Modificar `SubjectAdminForm`:

**Filtro de profesores mejorado:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    # Solo usuarios con rol Teacher
    self.fields['teacher_user'].queryset = User.objects.filter(
        groups__name__in=[*TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP]
    ).distinct().order_by('username')
    
    self.fields['teacher_user'].label_from_instance = lambda obj: (
        f"{obj.username} - {obj.get_full_name() or 'Sin nombre'}"
    )
    
    # Mejorar help_text
    self.fields['teacher_user'].help_text = (
        'Selecciona el profesor responsable de esta asignatura. '
        'Solo se muestran usuarios con rol de Profesor.'
    )
    
    self.fields['students'].help_text = (
        'Selecciona los alumnos matriculados en esta asignatura. '
        'Solo se muestran usuarios con rol de Alumno.'
    )
```

---

## FASE 5: Mejoras en UserProfile

### Objetivo
Facilitar la creacion de perfiles de estudiantes y profesores directamente desde el admin, con auto-asignacion de grupos.

### 5.1. Mejoras en Lista de Perfiles
**URL:** `http://127.0.0.1:8000/admin/paasify/userprofile/`

#### Cambios en `list_display`:
```python
list_display = [
    'nombre',
    'user',
    'get_role',              # Nuevo
    'year',
    'get_subjects_count',    # Nuevo
    'display_token',
    'token_created_at',
]
```

#### Filtros:
```python
list_filter = [
    UserRoleFilter,  # Nuevo filtro personalizado
    'token_created_at',
]
```

**`UserRoleFilter`:**
```python
class UserRoleFilter(admin.SimpleListFilter):
    title = 'Rol'
    parameter_name = 'user_role'
    
    def lookups(self, request, model_admin):
        return [
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
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

### 5.2. Mejoras en Creacion/Edicion de Perfil

#### Crear `UserProfileAdminForm` mejorado:

```python
class UserProfileAdminForm(forms.ModelForm):
    # Opcion 1: Crear nuevo usuario
    create_new_user = forms.BooleanField(
        required=False,
        initial=False,
        label='Crear nuevo usuario',
        help_text='Marca esta opcion para crear un nuevo usuario junto con el perfil'
    )
    
    new_username = forms.CharField(
        required=False,
        label='Nombre de usuario',
        help_text='Username para el nuevo usuario'
    )
    
    new_email = forms.EmailField(
        required=False,
        label='Email',
        help_text='Email del nuevo usuario'
    )
    
    new_first_name = forms.CharField(
        required=False,
        label='Nombre'
    )
    
    new_last_name = forms.CharField(
        required=False,
        label='Apellidos'
    )
    
    new_role = forms.ChoiceField(
        choices=[
            ('', '--- Seleccionar ---'),
            ('student', 'Alumno'),
            ('teacher', 'Profesor'),
        ],
        required=False,
        label='Rol del nuevo usuario'
    )
    
    auto_generate_password = forms.BooleanField(
        required=False,
        initial=True,
        label='Generar contraseña automaticamente'
    )
    
    class Meta:
        model = UserProfile
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        create_new = cleaned_data.get('create_new_user')
        
        if create_new:
            # Validar que se proporcionen todos los campos necesarios
            required_fields = ['new_username', 'new_email', 'new_first_name', 'new_last_name', 'new_role']
            for field in required_fields:
                if not cleaned_data.get(field):
                    raise forms.ValidationError(
                        f'Si creas un nuevo usuario, debes completar todos los campos.'
                    )
            
            # Verificar que el username no exista
            if User.objects.filter(username=cleaned_data['new_username']).exists():
                raise forms.ValidationError('El nombre de usuario ya existe.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('create_new_user'):
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=self.cleaned_data['new_username'],
                email=self.cleaned_data['new_email'],
                first_name=self.cleaned_data['new_first_name'],
                last_name=self.cleaned_data['new_last_name'],
            )
            
            # Generar contraseña
            if self.cleaned_data.get('auto_generate_password'):
                password = generate_password()
                user.set_password(password)
                user.save()
                
                # Guardar mensaje para mostrar
                self._generated_password = password
            
            # Asignar grupo segun rol
            role = self.cleaned_data['new_role']
            if role == 'student':
                ensure_user_group(user, DEFAULT_STUDENT_GROUP)
            elif role == 'teacher':
                ensure_user_group(user, DEFAULT_TEACHER_GROUP)
            
            # Asignar usuario al perfil
            instance.user = user
            
            # Auto-rellenar nombre si esta vacio
            if not instance.nombre:
                instance.nombre = f"{user.first_name} {user.last_name}"
        
        if commit:
            instance.save()
        
        return instance
```

---

### 5.3. Panel Separado para Profesores

#### Crear `TeacherProfileAdmin`:

```python
class TeacherProfileAdmin(admin.ModelAdmin):
    """Admin especifico para perfiles de profesores"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            user__groups__name__in=TEACHER_GROUP_NAMES
        ).distinct()
    
    list_display = [
        'nombre',
        'user',
        'year',
        'get_subjects_taught',
        'display_token',
    ]
    
    def get_subjects_taught(self, obj):
        if obj.user:
            count = Subject.objects.filter(teacher_user=obj.user).count()
            return f"📚 {count} asignaturas"
        return "-"
    get_subjects_taught.short_description = 'Asignaturas Impartidas'

# Registrar
admin.site.register(TeacherProfile, TeacherProfileAdmin)
```

**Nota:** Esto requiere crear un proxy model:
```python
class TeacherProfile(UserProfile):
    class Meta:
        proxy = True
        verbose_name = 'Perfil de Profesor'
        verbose_name_plural = 'Perfiles de Profesores'
```

---

## FASE 6: Mejoras en UserProject

### Objetivo
Mejorar la visualizacion de proyectos de alumnos, mostrando servicios asociados y facilitando la navegacion.

### 6.1. Mejoras en Lista de Proyectos
**URL:** `http://127.0.0.1:8000/admin/paasify/userproject/`

#### Cambios en `list_display`:
```python
list_display = [
    'place',
    'get_student_name',      # Nuevo
    'subject',
    'get_services_count',    # Nuevo
    'get_project_status',    # Nuevo
    'created_at',            # Nuevo (agregar al modelo)
]
```

#### Nuevos metodos:

**`get_student_name(obj)`:**
```python
def get_student_name(self, obj):
    if obj.user_profile and obj.user_profile.user:
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username
    return obj.user_profile.nombre if obj.user_profile else "-"
get_student_name.short_description = 'Alumno'
```

**`get_services_count(obj)`:**
```python
def get_services_count(self, obj):
    if obj.user_profile and obj.user_profile.user:
        from containers.models import Service
        count = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed').count()
        return f"🐳 {count}"
    return "0"
get_services_count.short_description = 'Servicios'
```

**`get_project_status(obj)`:**
```python
def get_project_status(self, obj):
    if obj.user_profile and obj.user_profile.user:
        from containers.models import Service
        services = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed')
        
        if not services.exists():
            return format_html('<span style="color: gray;">⚪ Sin servicios</span>')
        
        running = services.filter(status='running').count()
        total = services.count()
        
        if running == total:
            return format_html('<span style="color: green;">✅ Todos activos</span>')
        elif running > 0:
            return format_html('<span style="color: orange;">⚠️ Parcialmente activo</span>')
        else:
            return format_html('<span style="color: red;">❌ Detenido</span>')
    return "-"
get_project_status.short_description = 'Estado'
```

---

### 6.2. Mejoras en Detalle de Proyecto
**URL:** `http://127.0.0.1:8000/admin/paasify/userproject/<id>/change/`

#### Agregar campos readonly:

```python
readonly_fields = [
    'created_at',
    'get_student_info',
    'get_services_list',
]
```

**`get_student_info(obj)`:**
```python
def get_student_info(self, obj):
    if not obj.user_profile or not obj.user_profile.user:
        return "Sin alumno asignado"
    
    user = obj.user_profile.user
    profile = obj.user_profile
    
    return format_html(
        '<div style="background: #e8f5e9; padding: 15px; border-radius: 5px;">'
        '<h3>👤 Informacion del Alumno</h3>'
        '<p><strong>Nombre:</strong> {}</p>'
        '<p><strong>Username:</strong> {}</p>'
        '<p><strong>Email:</strong> {}</p>'
        '<p><strong>Perfil:</strong> <a href="/admin/paasify/userprofile/{}/change/">{}</a></p>'
        '</div>',
        user.get_full_name() or profile.nombre,
        user.username,
        user.email,
        profile.id,
        profile.nombre
    )
get_student_info.short_description = 'Informacion del Alumno'
```

**`get_services_list(obj)`:**
```python
def get_services_list(self, obj):
    if not obj.user_profile or not obj.user_profile.user:
        return "Sin servicios"
    
    from containers.models import Service
    services = Service.objects.filter(
        owner=obj.user_profile.user,
        subject=obj.subject
    ).exclude(status='removed')
    
    if not services.exists():
        return "No hay servicios asociados a este proyecto"
    
    html = '<div style="background: #fff3e0; padding: 15px; border-radius: 5px;">'
    html += '<h3>🐳 Servicios del Proyecto</h3>'
    html += '<table style="width: 100%; border-collapse: collapse;">'
    html += '<tr style="background: #f5f5f5;"><th>Nombre</th><th>Imagen</th><th>Puerto</th><th>Estado</th><th>Acciones</th></tr>'
    
    for service in services:
        status_colors = {
            'running': 'green',
            'stopped': 'orange',
            'error': 'red',
        }
        color = status_colors.get(service.status, 'gray')
        
        html += f'''
        <tr style="border-bottom: 1px solid #ddd;">
            <td>{service.name}</td>
            <td><code>{service.image}</code></td>
            <td>{service.assigned_port or "-"}</td>
            <td style="color: {color};">●  {service.status}</td>
            <td>
                <a href="/admin/containers/service/{service.id}/change/" target="_blank">
                    Ver detalles
                </a>
            </td>
        </tr>
        '''
    
    html += '</table></div>'
    return format_html(html)
get_services_list.short_description = 'Servicios Asociados'
```

---

## Resumen de Archivos a Modificar/Crear

### Archivos a Modificar:

1. **`paasify/admin.py`**
   - Modificar `SubjectAdmin`
   - Modificar `UserProfileAdmin`
   - Modificar `UserProjectAdmin`
   - Crear `UserAdminForm`
   - Crear `TeacherProfileAdmin`

2. **`containers/admin.py`**
   - Modificar `AllowedImageAdmin`
   - Modificar `ServiceAdmin`
   - Crear `ServiceAdminForm`

3. **`containers/models.py`**
   - Agregar campo `image_type` a `AllowedImage`
   - Agregar campo `created_at` a modelos si no existe

4. **`paasify/models/StudentModel.py`**
   - Crear proxy model `TeacherProfile`

5. **`django.contrib.auth.admin`** (override)
   - Crear `CustomUserAdmin` para reemplazar el default

### Archivos a Crear:

1. **`paasify/static/admin/js/allowedimage_autocomplete.js`**
   - JavaScript para autocompletar tags de DockerHub

2. **`paasify/utils/password_generator.py`**
   - Utilidad para generar contraseñas seguras

3. **`paasify/admin_filters.py`**
   - Filtros personalizados (`RoleFilter`, `UserRoleFilter`)

### Migraciones Requeridas:

```bash
# Agregar campo image_type a AllowedImage
python manage.py makemigrations containers

# Agregar campo created_at a modelos si no existe
python manage.py makemigrations paasify

# Aplicar migraciones
python manage.py migrate
```

---

## Estimacion de Tiempo

| Fase | Descripcion | Tiempo Estimado |
|------|-------------|-----------------|
| Fase 1 | Admin de Usuarios | 3-4 horas |
| Fase 2 | AllowedImage | 2-3 horas |
| Fase 3 | Service | 2-3 horas |
| Fase 4 | Subject | 1-2 horas |
| Fase 5 | UserProfile | 3-4 horas |
| Fase 6 | UserProject | 2-3 horas |
| **TOTAL** | | **13-19 horas** |

---

## Orden de Implementacion Sugerido

1. **Fase 2** (AllowedImage) - Agregar campo `image_type` y migracion
2. **Fase 1** (Usuarios) - Base para las demas fases
3. **Fase 4** (Subject) - Mejoras simples
4. **Fase 5** (UserProfile) - Depende de Fase 1
5. **Fase 3** (Service) - Depende de Fase 2
6. **Fase 6** (UserProject) - Depende de todas las anteriores

---

## Consideraciones Tecnicas

### Seguridad
- Validar permisos en todas las acciones
- No exponer contraseñas generadas en logs
- Sanitizar inputs de usuarios

### Performance
- Usar `select_related()` y `prefetch_related()` en queries
- Cachear resultados de DockerHub si es posible
- Limitar numero de tags consultados (max 50)

### UX
- Tooltips claros y concisos
- Mensajes de error descriptivos
- Confirmaciones antes de acciones destructivas

### Compatibilidad
- Mantener compatibilidad con Django 4.x
- Probar en navegadores modernos (Chrome, Firefox, Edge)
- Responsive design en admin (opcional)

---

## Tests Recomendados

### Tests Unitarios:
- Test de creacion de usuario con rol
- Test de generacion de contraseña
- Test de consulta a DockerHub
- Test de filtros personalizados

### Tests de Integracion:
- Test de creacion de UserProfile con nuevo usuario
- Test de asignacion automatica de grupos
- Test de visualizacion de servicios en proyecto

### Tests Manuales:
- Verificar todos los filtros funcionan
- Verificar tooltips se muestran correctamente
- Verificar enlaces a servicios funcionan
- Verificar generacion de contraseña es segura

---

## Documentacion a Generar

Despues de implementar cada fase:

1. **Documento de implementacion** en `document/implementacion/`
   - Cambios realizados
   - Capturas de pantalla
   - Problemas encontrados y soluciones

2. **Actualizacion del README** si es necesario
   - Nuevas funcionalidades del admin
   - Instrucciones de uso

3. **Changelog** en `CHANGELOG.md`
   - Version nueva
   - Features agregados
   - Breaking changes (si los hay)

---

**Fecha de creacion:** 2025-11-25 14:30
**Version del plan:** 1.0.0
**New Update:** 4.2.0
**Estado:** ⏳ Pendiente de aprobacion

---

## Proximos Pasos

1. **Revisar este plan** con el usuario
2. **Aprobar o solicitar cambios**
3. **Comenzar implementacion** de Fase 1 tras aprobacion
4. **Iterar** fase por fase con verificacion entre cada una

**¿Apruebas este plan para comenzar la implementacion?**
