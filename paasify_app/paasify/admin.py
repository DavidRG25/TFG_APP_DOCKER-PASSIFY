# paasify/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from paasify.models.StudentModel import UserProfile, TeacherProfile
from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject
from paasify.roles import (
    DEFAULT_STUDENT_GROUP,
    DEFAULT_TEACHER_GROUP,
    STUDENT_GROUP_NAMES,
    TEACHER_GROUP_NAMES,
    ensure_user_group,
)

User = get_user_model()

admin.site.site_header = "PaaSify · Admin"
admin.site.index_title = "Panel de administración"
admin.site.site_title = "PaaSify"


#  Inlines (UserProject dentro de Subject/UserProfile)

class UserProjectInlineForSubject(admin.TabularInline):
    model = UserProject
    fk_name = "subject"
    extra = 0  # No crear formularios vacíos automáticamente
    autocomplete_fields = ("user_profile",)

    # Solo perfiles cuyo usuario pertenece al grupo Student
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user_profile":
            kwargs["queryset"] = (
                UserProfile.objects
                .filter(
                    user__isnull=False,
                    user__groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES],
                )
                .select_related("user")
                .distinct()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class UserProjectInlineForProfile(admin.TabularInline):
    model = UserProject
    fk_name = "user_profile"
    extra = 0  # No crear formularios vacíos automáticamente
    autocomplete_fields = ("subject",)
    readonly_fields = ('get_services_deployed',)
    
    def get_services_deployed(self, obj):
        """Muestra los servicios desplegados en este proyecto"""
        if not obj or not obj.pk:
            return "-"
        
        from containers.models import Service
        from django.utils.html import format_html
        
        # Obtener servicios del proyecto (mismo usuario y asignatura)
        services = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed')
        
        count = services.count()
        
        if count == 0:
            return format_html('<span style="color: gray;">Sin servicios</span>')
        
        # Crear lista de servicios con iconos de estado
        services_html = []
        for service in services:
            if service.status == 'running':
                icon = '🟢'
                color = 'green'
            elif service.status == 'stopped':
                icon = '🔴'
                color = 'red'
            else:
                icon = '🟡'
                color = 'orange'
            
            services_html.append(
                f'<span style="color: {color};">{icon} {service.name}</span>'
            )
        
        return format_html('<br>'.join(services_html))
    
    get_services_deployed.short_description = 'Servicios Desplegados'



#  Subject (Asignaturas)

class SubjectAdminForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ocultar campo legacy "players" para no duplicar profesor
        if "players" in self.fields:
            self.fields["players"].widget = forms.HiddenInput()
            self.fields["players"].required = False

        # teacher_user: solo usuarios en grupos profesor/Teacher
        self.fields["teacher_user"].queryset = User.objects.filter(
            groups__name__in=[*TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP]
        ).distinct().order_by('username')
        self.fields["teacher_user"].required = True
        
        # Mejorar label del profesor
        self.fields["teacher_user"].label_from_instance = lambda obj: (
            f"{obj.username} - {obj.get_full_name() or 'Sin nombre'}"
        )
        
        # Help text mejorado para teacher_user
        self.fields["teacher_user"].help_text = (
            'Selecciona el profesor responsable de esta asignatura. '
            'Solo se muestran usuarios con rol de Profesor.'
        )

        # students: solo usuarios del grupo Student (case-insensitive)
        self.fields["students"].queryset = User.objects.filter(
            groups__name__in=[*STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP]
        ).distinct().order_by('username')
        
        # Help text mejorado para students
        self.fields["students"].help_text = (
            'Selecciona los alumnos matriculados en esta asignatura. '
            'Solo se muestran usuarios con rol de Alumno.'
        )

    def clean_teacher_user(self):
        u = self.cleaned_data.get("teacher_user")
        if not u:
            raise forms.ValidationError("Debes asignar un profesor.")
        if not any(u.groups.filter(name__iexact=name).exists() for name in TEACHER_GROUP_NAMES):
            raise forms.ValidationError(
                "El usuario seleccionado no pertenece al grupo Profesor/Teacher."
            )
        return u

    def clean_students(self):
        qs = self.cleaned_data.get("students")
        if not qs:
            return qs
        allowed = list(STUDENT_GROUP_NAMES) + [DEFAULT_STUDENT_GROUP]
        bad = [
            user for user in qs
            if not any(user.groups.filter(name__iexact=name).exists() for name in allowed)
        ]
        if bad:
            raise forms.ValidationError("Todos los alumnos deben pertenecer al grupo Student/Alumno.")
        return qs


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = (
        "name",
        "teacher_user",
        "category",
        "genero",
        "get_students_count",    # Nuevo
        "get_services_count",    # Nuevo
    )
    search_fields = ("name", "teacher_user__username", "teacher_user__email")
    list_filter = ("category", "genero")
    # autocomplete_fields = ("teacher_user",)  # QUITADO: ignora el queryset del formulario
    filter_horizontal = ("students",)
    inlines = [UserProjectInlineForSubject]
    exclude = ("players",)  # oculta campo legacy
    
    # Fieldsets con diseño de franjas
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'genero', 'category')
        }),
        ('Profesor Asignado', {
            'fields': ('teacher_user',),
            'description': 'Selecciona el profesor responsable de esta asignatura'
        }),
        ('Alumnos Matriculados', {
            'fields': ('students',),
            'description': 'Selecciona los alumnos que cursarán esta asignatura'
        }),
    )

    # Defensa extra si se cambia el form
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher_user":
            kwargs["queryset"] = User.objects.filter(
                groups__name__in=[*TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP]
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_students_count(self, obj):
        """Muestra el número de alumnos matriculados"""
        count = obj.students.count()
        return f"👥 {count}"
    get_students_count.short_description = 'Alumnos'
    
    def get_services_count(self, obj):
        """Muestra el número de servicios activos en esta asignatura"""
        from containers.models import Service
        count = Service.objects.filter(subject=obj).exclude(status='removed').count()
        if count == 0:
            return "-"
        return f"🐳 {count}"
    get_services_count.short_description = 'Servicios'

    # Auto-matricular: si en el inline se añade un UserProject, matriculamos al user del alumno
    def save_formset(self, request, form, formset, change):
        objs = formset.save(commit=False)
        formset.save_m2m()

        for obj in objs:
            obj.save()

        if formset.model is UserProject:
            subject_instance = form.instance
            for obj in objs:
                profile = getattr(obj, "user_profile", None)
                user = getattr(profile, "user", None) if profile else None
                if user:
                    subject_instance.students.add(user)

        for obj in formset.deleted_objects:
            obj.delete()



#  UserProfile (Alumnos)

class UserProfileAdminForm(forms.ModelForm):
    """
    Formulario para crear perfiles de alumno.
    Crea automáticamente el usuario con rol Student.
    """
    
    # Campos para crear el usuario
    username = forms.CharField(
        label="Nombre de usuario",
        help_text="Nombre de usuario único para iniciar sesión"
    )
    email = forms.EmailField(
        label="Dirección de email",
        help_text='Email del usuario (será usado como campo "year" en el perfil)'
    )
    first_name = forms.CharField(
        label="Nombre",
        required=False,
        help_text="Nombre del usuario"
    )
    last_name = forms.CharField(
        label="Apellido",
        required=False,
        help_text="Apellido del usuario"
    )
    
    # Checkbox para generar contraseña automáticamente
    generate_password = forms.BooleanField(
        label="Generar contraseña automáticamente",
        required=False,
        initial=False,
        help_text="Si se marca, se generará una contraseña aleatoria segura (recomendado)"
    )
    
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        required=False,
        help_text="Su contraseña no puede ser similar a otros componentes de su información personal.<br>"
                  "Su contraseña debe contener por lo menos 8 caracteres.<br>"
                  "Su contraseña no puede ser una contraseña usada muy comúnmente.<br>"
                  "Su contraseña no puede estar formada exclusivamente por números."
    )
    password2 = forms.CharField(
        label="Confirmación de contraseña",
        widget=forms.PasswordInput,
        required=False,
        help_text="Introduzca la misma contraseña nuevamente, para poder verificar la misma."
    )
    
    class Meta:
        model = UserProfile
        fields = ["username", "email", "first_name", "last_name", "generate_password", "password1", "password2", "nombre", "year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, pre-poblar campos del usuario
        if self.instance and self.instance.pk and self.instance.user:
            self.fields["username"].initial = self.instance.user.username
            self.fields["username"].disabled = True
            self.fields["username"].help_text = "No se puede cambiar el nombre de usuario"
            
            self.fields["email"].initial = self.instance.user.email
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            
            # Ocultar checkbox de generar contraseña al editar
            self.fields["generate_password"].widget = forms.HiddenInput()
            
            # No requerir contraseñas al editar
            self.fields["password1"].help_text = "Dejar en blanco si no desea cambiar la contraseña"
            self.fields["password2"].help_text = "Dejar en blanco si no desea cambiar la contraseña"
        
        # Autocompletar nombre si no existe (solo si el campo está en el formulario)
        if "nombre" in self.fields:
            if not self.instance.nombre and self.instance.user:
                self.fields["nombre"].initial = (
                    self.instance.user.get_full_name() 
                    or self.instance.user.username
                )
            self.fields["nombre"].help_text = "Nombre completo del alumno"
        
        # Autocompletar year si no existe (solo si el campo está en el formulario)
        if "year" in self.fields:
            if not self.instance.year and self.instance.user:
                self.fields["year"].initial = (
                    self.instance.user.email 
                    or f"{self.instance.user.username}@pendiente.local"
                )
            self.fields["year"].help_text = "Email o curso del alumno"

    def clean_username(self):
        username = self.cleaned_data.get("username")
        
        # Si estamos editando, permitir el username actual
        if self.instance and self.instance.pk and self.instance.user:
            if username == self.instance.user.username:
                return username
        
        # Verificar que no exista
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe")
        
        return username
    
    def clean(self):
        cleaned = super().clean()
        
        # Validar contraseñas
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        generate_password = cleaned.get("generate_password")
        
        # Si estamos creando un nuevo perfil
        if not self.instance.pk:
            # Si se marca generar contraseña, no requerir password1/password2
            if generate_password:
                # Generar contraseña aleatoria segura
                from django.contrib.auth.hashers import make_random_password
                random_password = make_random_password(length=12)
                cleaned["password1"] = random_password
                cleaned["password2"] = random_password
            else:
                # Si no se genera automáticamente, las contraseñas son obligatorias
                if not password1 or not password2:
                    raise forms.ValidationError(
                        "Debes proporcionar una contraseña o marcar 'Generar contraseña automáticamente'"
                    )
                
                # Validar que coincidan
                if password1 != password2:
                    raise forms.ValidationError("Las contraseñas no coinciden")
        else:
            # Al editar, solo validar si se proporcionaron contraseñas
            if password1 or password2:
                if password1 != password2:
                    raise forms.ValidationError("Las contraseñas no coinciden")

        # --- VALIDACIÓN DE UNICIDAD DE NOMBRE ---
        # Calculamos el nombre final que tendrá el perfil para evitar duplicados
        first_name = cleaned.get("first_name", "").strip()
        last_name = cleaned.get("last_name", "").strip()
        username = cleaned.get("username", "")
        
        if first_name or last_name:
            full_name = f"{first_name} {last_name}".strip()
        else:
            full_name = username
            
        # Comprobar si ya existe alguien CON USUARIO ACTIVO con ese nombre (case-insensitive)
        # Nota: Usamos UserProfile importado arriba. Ignoramos perfiles huérfanos (user__isnull=True).
        qs = UserProfile.objects.filter(nombre__iexact=full_name, user__isnull=False)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise forms.ValidationError(
                f"Ya existe un usuario registrado con el nombre '{full_name}'. "
                "El sistema requiere nombres únicos. Por favor, añade una inicial o segundo apellido."
            )

        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Crear o actualizar usuario
        if self.instance.pk and self.instance.user:
            # Editando: actualizar usuario existente
            user = self.instance.user
            user.email = self.cleaned_data["email"]
            user.first_name = self.cleaned_data.get("first_name", "")
            user.last_name = self.cleaned_data.get("last_name", "")
            
            # Cambiar contraseña solo si se proporcionó
            if self.cleaned_data.get("password1"):
                user.set_password(self.cleaned_data["password1"])
            
            user.save()
        else:
            # Creando: crear nuevo usuario
            user = User(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email"],
                first_name=self.cleaned_data.get("first_name", ""),
                last_name=self.cleaned_data.get("last_name", "")
            )
            user._skip_user_profile_autocreate = True
            user.set_password(self.cleaned_data["password1"])
            user.save()
            
            # Asignar rol Student
            ensure_user_group(user, STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP)
            
            profile.user = user
        
        # SIEMPRE actualizar nombre/year desde los datos del usuario (tanto al crear como al editar)
        profile.nombre = (
            user.get_full_name() 
            or user.username
        )
        
        profile.year = (
            user.email 
            or f"{user.username}@pendiente.local"
        )

        if commit:
            profile.save()
            self.save_m2m()
        
        return profile




@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileAdminForm
    list_display = (
        "nombre",
        "user",
        "get_role",              # Nuevo
        "year",
        "get_subjects_count",    # Nuevo
        "display_token",
        "token_created_at"
    )
    search_fields = ("nombre", "year", "user__username", "user__email")
    list_filter = (
        'token_created_at',
    )
    # autocomplete_fields = ("user",)  # QUITADO: interfiere con el queryset del formulario
    inlines = [UserProjectInlineForProfile]
    readonly_fields = ("display_token", "token_created_at", "get_nombre_display", "get_year_display")
    actions = ["refresh_api_tokens"]
    
    # Fieldsets con diseño de franjas
    fieldsets = (
        ('Datos de Usuario', {
            'fields': ('username', 'email', 'first_name', 'last_name'),
            'description': 'Información de la cuenta de usuario. El rol se asigna automáticamente como "Student".'
        }),
        ('Contraseña', {
            'fields': ('generate_password', 'password1', 'password2'),
            'description': 'Contraseña para iniciar sesión. Puedes generarla automáticamente o introducirla manualmente.'
        }),
        ('Información del Perfil', {
            'fields': ('get_nombre_display', 'get_year_display'),
            'description': 'Información adicional del alumno (generada automáticamente)'
        }),
        ('Token API', {
            'fields': ('display_token', 'token_created_at'),
            'description': 'Token JWT para autenticación en API. Se genera automáticamente.',
            'classes': ('collapse',)
        }),
    )
    
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
    get_nombre_display.short_description = 'Nombre completo'
    
    def get_year_display(self, obj):
        """Muestra el email/curso del alumno de forma bonita"""
        from django.utils.html import format_html
        if obj and obj.year:
            return format_html(
                '<div style="background: #f3e5f5; padding: 10px; border-radius: 4px; border-left: 3px solid #9c27b0;">'
                '<strong style="color: #7b1fa2;">📧 {}</strong>'
                '</div>',
                obj.year
            )
        return format_html('<span style="color: #999;">No especificado</span>')
    get_year_display.short_description = 'Email / Curso'
    
    def get_fieldsets(self, request, obj=None):
        """Mostrar fieldsets dinámicamente según si estamos creando o editando"""
        if obj is None:
            # Creando: ocultar "Información del Perfil" y "Token API"
            return (
                ('Datos de Usuario', {
                    'fields': ('username', 'email', 'first_name', 'last_name'),
                    'description': 'Información de la cuenta de usuario. El rol se asigna automáticamente como "Student".'
                }),
                ('Contraseña', {
                    'fields': ('generate_password', 'password1', 'password2'),
                    'description': 'Contraseña para iniciar sesión. Puedes generarla automáticamente o introducirla manualmente.'
                }),
            )
        else:
            # Editando: mostrar todos los fieldsets
            return self.fieldsets

    def get_queryset(self, request):
        """Filtrar solo perfiles con usuarios Student, excluyendo explícitamente a los profesores."""
        from django.db.models import Q
        qs = super().get_queryset(request)
        
        # Filtro positivo: debe estar en algún grupo de alumnos
        student_filter = Q()
        for group_name in [DEFAULT_STUDENT_GROUP] + list(STUDENT_GROUP_NAMES):
            student_filter |= Q(user__groups__name__iexact=group_name)
            
        # Filtro negativo: NO debe estar en ningún grupo de profesores
        teacher_filter = Q()
        for group_name in [DEFAULT_TEACHER_GROUP] + list(TEACHER_GROUP_NAMES):
            teacher_filter |= Q(user__groups__name__iexact=group_name)
            
        return qs.filter(
            user__isnull=False
        ).filter(student_filter).exclude(teacher_filter).distinct()
    
    def get_role(self, obj):
        """Muestra el rol del usuario con badge de color"""
        from django.utils.html import format_html
        
        if not obj.user:
            return "-"
        
        # Verificar si es profesor
        if obj.user.groups.filter(name__in=TEACHER_GROUP_NAMES).exists():
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">👨‍🏫 Profesor</span>'
            )
        # Verificar si es alumno
        elif obj.user.groups.filter(name__in=STUDENT_GROUP_NAMES).exists():
            return format_html(
                '<span style="background: #2196f3; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">👨‍🎓 Alumno</span>'
            )
        else:
            return format_html(
                '<span style="background: #9e9e9e; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Sin rol</span>'
            )
    get_role.short_description = 'Rol'
    
    def get_subjects_count(self, obj):
        """Muestra el número de asignaturas del alumno"""
        if not obj.user:
            return "-"
        
        # Contar asignaturas donde el usuario es estudiante
        count = obj.user.subjects_as_student.count()
        if count == 0:
            return "-"
        return f"📚 {count}"
    get_subjects_count.short_description = 'Asignaturas'

    def es_usuario_alumno(self, obj):
        return bool(
            obj.user
            and obj.user.groups.filter(
                name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES]
            ).exists()
        )
    es_usuario_alumno.boolean = True
    es_usuario_alumno.short_description = "Es alumno"
    
    def display_token(self, obj):
        """Muestra el token parcialmente oculto (ultimos 8 caracteres)."""
        if obj.api_token:
            return obj.get_masked_token()
        return "-"
    display_token.short_description = "Token API (JWT)"
    
    @admin.action(description="Refrescar tokens API de usuarios seleccionados")
    def refresh_api_tokens(self, request, queryset):
        """Action para refrescar tokens de multiples usuarios."""
        from django.contrib import messages
        
        count = 0
        for profile in queryset:
            if profile.user:
                try:
                    profile.refresh_token(expiration_days=365)
                    count += 1
                except Exception as e:
                    messages.error(request, f"Error al refrescar token de {profile.nombre}: {e}")
        
        if count > 0:
            messages.success(request, f"Se refrescaron {count} token(es) exitosamente.")


#  TeacherProfile (Profesores)

class TeacherProfileAdminForm(UserProfileAdminForm):
    """
    Formulario para crear perfiles de profesor.
    Hereda de UserProfileAdminForm pero asigna rol Teacher automáticamente.
    """
    
    def save(self, commit=True):
        profile = forms.ModelForm.save(self, commit=False)
        
        # Crear o actualizar usuario
        if self.instance.pk and self.instance.user:
            # Editando: actualizar usuario existente
            user = self.instance.user
            user.email = self.cleaned_data["email"]
            user.first_name = self.cleaned_data.get("first_name", "")
            user.last_name = self.cleaned_data.get("last_name", "")
            
            # Cambiar contraseña solo si se proporcionó
            if self.cleaned_data.get("password1"):
                user.set_password(self.cleaned_data["password1"])
            
            user.save()
        else:
            # Creando: crear nuevo usuario
            user = User(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email"],
                first_name=self.cleaned_data.get("first_name", ""),
                last_name=self.cleaned_data.get("last_name", "")
            )
            user._skip_user_profile_autocreate = True
            user.set_password(self.cleaned_data["password1"])
            user.save()
            
            # Asignar rol Teacher (diferencia con UserProfileAdminForm)
            ensure_user_group(user, TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP)
            
            profile.user = user
        
        # SIEMPRE actualizar nombre/year desde los datos del usuario (tanto al crear como al editar)
        profile.nombre = (
            user.get_full_name() 
            or user.username
        )
        
        profile.year = (
            user.email 
            or f"{user.username}@pendiente.local"
        )

        if commit:
            profile.save()
            self.save_m2m()
        
        return profile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    form = TeacherProfileAdminForm
    list_display = (
        "nombre",
        "user",
        "get_role",
        "year",
        "get_subjects_count",
        "display_token",
        "token_created_at"
    )
    search_fields = ("nombre", "year", "user__username", "user__email")
    list_filter = (
        'token_created_at',
    )
    inlines = []  # Sin inlines para profesores
    readonly_fields = ("display_token", "token_created_at", "get_nombre_display", "get_year_display")
    actions = ["refresh_api_tokens"]
    
    # Fieldsets con diseño de franjas
    fieldsets = (
        ('Datos de Usuario', {
            'fields': ('username', 'email', 'first_name', 'last_name'),
            'description': 'Información de la cuenta de usuario. El rol se asigna automáticamente como "Teacher".'
        }),
        ('Contraseña', {
            'fields': ('generate_password', 'password1', 'password2'),
            'description': 'Contraseña para iniciar sesión. Puedes generarla automáticamente o introducirla manualmente.'
        }),
        ('Información del Perfil', {
            'fields': ('get_nombre_display', 'get_year_display'),
            'description': 'Información adicional del profesor (generada automáticamente)'
        }),
        ('Token API', {
            'fields': ('display_token', 'token_created_at'),
            'description': 'Token JWT para autenticación en API. Se genera automáticamente.',
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_display(self, obj):
        """Muestra el nombre completo del profesor de forma bonita"""
        from django.utils.html import format_html
        if obj and obj.nombre:
            return format_html(
                '<div style="background: #e8f5e9; padding: 10px; border-radius: 4px; border-left: 3px solid #4caf50;">'
                '<strong style="color: #2e7d32;">👨‍🏫 {}</strong>'
                '</div>',
                obj.nombre
            )
        return format_html('<span style="color: #999;">No especificado</span>')
    get_nombre_display.short_description = 'Nombre completo'
    
    def get_year_display(self, obj):
        """Muestra el email/curso del profesor de forma bonita"""
        from django.utils.html import format_html
        if obj and obj.year:
            return format_html(
                '<div style="background: #fff3e0; padding: 10px; border-radius: 4px; border-left: 3px solid #ff9800;">'
                '<strong style="color: #e65100;">📧 {}</strong>'
                '</div>',
                obj.year
            )
        return format_html('<span style="color: #999;">No especificado</span>')
    get_year_display.short_description = 'Email / Curso'
    
    def get_fieldsets(self, request, obj=None):
        """Mostrar fieldsets dinámicamente según si estamos creando o editando"""
        if obj is None:
            # Creando: ocultar "Información del Perfil" y "Token API"
            return (
                ('Datos de Usuario', {
                    'fields': ('username', 'email', 'first_name', 'last_name'),
                    'description': 'Información de la cuenta de usuario. El rol se asigna automáticamente como "Teacher".'
                }),
                ('Contraseña', {
                    'fields': ('generate_password', 'password1', 'password2'),
                    'description': 'Contraseña para iniciar sesión. Puedes generarla automáticamente o introducirla manualmente.'
                }),
            )
        else:
            # Editando: mostrar todos los fieldsets
            return self.fieldsets

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
    
    def get_role(self, obj):
        """Muestra el rol del usuario con badge de color"""
        from django.utils.html import format_html
        
        if not obj.user:
            return "-"
        
        # Verificar si es profesor
        if obj.user.groups.filter(name__in=TEACHER_GROUP_NAMES).exists():
            return format_html(
                '<span style="background: #4caf50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">👨‍🏫 Profesor</span>'
            )
        else:
            return format_html(
                '<span style="background: #9e9e9e; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Sin rol</span>'
            )
    get_role.short_description = 'Rol'
    
    def get_subjects_count(self, obj):
        """Muestra el número de asignaturas que imparte el profesor"""
        if not obj.user:
            return "-"
        
        # Contar asignaturas donde el usuario es profesor
        count = Subject.objects.filter(teacher_user=obj.user).count()
        if count == 0:
            return "-"
        return f"📚 {count}"
    get_subjects_count.short_description = 'Asignaturas'
    
    def display_token(self, obj):
        """Muestra el token parcialmente oculto (ultimos 8 caracteres)."""
        if obj.api_token:
            return obj.get_masked_token()
        return "-"
    display_token.short_description = "Token API (JWT)"
    
    @admin.action(description="Refrescar tokens API de usuarios seleccionados")
    def refresh_api_tokens(self, request, queryset):
        """Action para refrescar tokens de multiples usuarios."""
        from django.contrib import messages
        count = 0
        for profile in queryset:
            if profile.user:
                try:
                    profile.refresh_token(expiration_days=365)
                    count += 1
                except Exception as e:
                    messages.error(request, f"Error al refrescar token de {profile.nombre}: {e}")
        
        if count > 0:
            messages.success(request, f"Se refrescaron {count} token(es) exitosamente.")



# ============================================================================
# Custom User Admin - Mejoras Fase 1
# ============================================================================

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import format_html
from paasify.admin_filters import RoleFilter
from paasify.utils import generate_password


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios con selección de rol"""
    
    role = forms.ChoiceField(
        choices=[
            ('', '--- Seleccionar rol ---'),
            ('admin', 'Administrador'),
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
        ],
        required=True,
        label='Rol del usuario',
        help_text='Selecciona el rol que tendrá este usuario en el sistema',
        widget=forms.RadioSelect,
    )
    
    auto_generate_password = forms.BooleanField(
        required=False,
        initial=True,
        label='Generar contraseña automáticamente',
        help_text='Si se marca, se generará una contraseña aleatoria segura (recomendado)',
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos obligatorios
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Mejorar help_texts
        self.fields['username'].help_text = 'Nombre de usuario único para iniciar sesión'
        self.fields['email'].help_text = 'Email del usuario (será usado como campo "year" en el perfil)'
        self.fields['first_name'].help_text = 'Nombre del usuario'
        self.fields['last_name'].help_text = 'Apellidos del usuario'
        
        # Si auto_generate_password está marcado, hacer password1 y password2 opcionales
        if self.data.get('auto_generate_password'):
            self.fields['password1'].required = False
            self.fields['password2'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        auto_gen = cleaned_data.get('auto_generate_password')
        password1 = cleaned_data.get('password1')
        
        # Si auto_generate está marcado, generar contraseña
        if auto_gen:
            password = generate_password()
            cleaned_data['password1'] = password
            cleaned_data['password2'] = password
            # Guardar para mostrar después
            self._generated_password = password
        elif not password1:
            raise forms.ValidationError(
                'Debes proporcionar una contraseña o marcar "Generar contraseña automáticamente"'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        
        # Asignar permisos según rol
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif role in ['teacher', 'student']:
            user.is_staff = False
            user.is_superuser = False
        
        if commit:
            user.save()
            # La asignación de grupos y creación de UserProfile se hace en save_model del admin
        
        return user


class CustomUserAdmin(BaseUserAdmin):
    """Admin personalizado para el modelo User con mejoras de Fase 1"""
    
    add_form = CustomUserCreationForm
    
    # Campos a mostrar en la lista
    list_display = [
        'username',
        'email',
        'get_full_name_display',
        'get_role_display',
        'get_subjects_count',
        'get_active_services',
        'date_joined',
        'is_active',
    ]
    
    # Filtros
    list_filter = [
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        RoleFilter,  # Filtro personalizado
    ]
    
    # Búsqueda mejorada
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'user_profile__nombre',
    ]
    
    # Fieldsets para edición
    fieldsets = BaseUserAdmin.fieldsets
    
    # Fieldsets para creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'auto_generate_password',
                'password1',
                'password2',
            ),
        }),
    )
    
    def get_full_name_display(self, obj):
        """Muestra el nombre completo del usuario"""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or "-"
    get_full_name_display.short_description = 'Nombre Completo'
    
    def get_role_display(self, obj):
        """Muestra el rol del usuario con badge de color"""
        if obj.is_superuser:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">🔑 ADMIN</span>'
            )
        
        # Verificar grupos
        groups = obj.groups.values_list('name', flat=True)
        
        if any(name.lower() in [g.lower() for g in groups] for name in TEACHER_GROUP_NAMES):
            return format_html(
                '<span style="background: #007bff; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">👨‍🏫 PROFESOR</span>'
            )
        
        if any(name.lower() in [g.lower() for g in groups] for name in STUDENT_GROUP_NAMES):
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">👨‍🎓 ALUMNO</span>'
            )
        
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">Sin rol</span>'
        )
    get_role_display.short_description = 'Rol'
    
    def get_subjects_count(self, obj):
        """Muestra el número de asignaturas del usuario"""
        # Si es profesor
        teacher_subjects = Subject.objects.filter(teacher_user=obj).count()
        if teacher_subjects > 0:
            return format_html('📚 {} (profesor)', teacher_subjects)
        
        # Si es estudiante (usar related_name correcto)
        student_subjects = obj.subjects_as_student.count()
        if student_subjects > 0:
            return format_html('📚 {} (alumno)', student_subjects)
        
        return "-"
    get_subjects_count.short_description = 'Asignaturas'
    
    def get_active_services(self, obj):
        """Muestra el número de servicios activos del usuario"""
        try:
            from containers.models import Service
            running_count = Service.objects.filter(
                owner=obj,
                status='running'
            ).count()
            total_count = Service.objects.filter(owner=obj).exclude(status='removed').count()
            
            if total_count == 0:
                return "-"
            
            if running_count == total_count:
                color = 'green'
            elif running_count > 0:
                color = 'orange'
            else:
                color = 'gray'
            
            return format_html(
                '<span style="color: {};">🐳 {}/{}</span>',
                color,
                running_count,
                total_count
            )
        except Exception:
            return "-"
    get_active_services.short_description = 'Servicios Activos'
    
    def save_model(self, request, obj, form, change):
        """Guardar modelo y mostrar contraseña generada si aplica"""
        # Si es un usuario nuevo (no change), ejecutar lógica del formulario
        if not change and hasattr(form, 'cleaned_data'):
            role = form.cleaned_data.get('role')
            
            # Guardar usuario primero
            super().save_model(request, obj, form, change)
            
            # Asignar grupo según rol
            if role == 'teacher':
                ensure_user_group(obj, TEACHER_GROUP_NAMES, DEFAULT_TEACHER_GROUP)
            elif role == 'student':
                ensure_user_group(obj, STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP)
            
            # Crear UserProfile automáticamente para student y teacher
            if role in ['student', 'teacher']:
                UserProfile.objects.get_or_create(
                    user=obj,
                    defaults={
                        'nombre': f"{obj.first_name} {obj.last_name}".strip(),
                        'year': obj.email,
                    }
                )
        else:
            # Si es edición, solo guardar
            super().save_model(request, obj, form, change)
        
        # Si se generó una contraseña, mostrarla
        if hasattr(form, '_generated_password'):
            from django.contrib import messages
            messages.success(
                request,
                format_html(
                    '<strong>Usuario creado exitosamente.</strong><br>'
                    'Contraseña generada: <code style="background: #f0f0f0; padding: 5px; '
                    'font-size: 14px; color: #d63384;">{}</code><br>'
                    '<em>Guarda esta contraseña, no se volverá a mostrar.</em>',
                    form._generated_password
                )
            )



#  UserProject (Proyectos de Alumnos)

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = (
        'place',
        'get_student_name',      # Nuevo
        'subject',
        'get_services_count',    # Nuevo
        'get_project_status',    # Nuevo
        'date',                  # De version anterior
        'time',                  # De version anterior
    )
    search_fields = (
        'place',
        'user_profile__nombre',
        'user_profile__user__username',
        'subject__name',
    )
    list_filter = ('subject', 'date')  # Agregado 'date' de version anterior
    autocomplete_fields = ('user_profile', 'subject')
    readonly_fields = ('get_services_list',)
    
    # Fieldsets con diseño de franjas
    fieldsets = (
        ('Información del Proyecto', {
            'fields': ('place',),
            'description': 'Nombre identificativo del proyecto'
        }),
        ('Asignación', {
            'fields': ('user_profile', 'subject'),
            'description': 'Alumno y asignatura asociados al proyecto'
        }),
        ('Servicios Desplegados', {
            'fields': ('get_services_list',),
            'description': 'Contenedores Docker desplegados en este proyecto',
            'classes': ('collapse',)
        }),
        ('Fecha y Hora', {
            'fields': ('date', 'time'),
            'description': 'Fecha y hora de creación del proyecto',
            'classes': ('collapse',)
        }),
    )
    
    def get_services_list(self, obj):
        """Muestra la lista de servicios desplegados en este proyecto"""
        from django.utils.html import format_html
        from django.utils.safestring import mark_safe
        
        # Verificar objeto
        if not obj:
            return format_html('<span style="color: red;">❌ Objeto no existe</span>')
        
        if not obj.user_profile:
            return format_html('<span style="color: orange;">⚠️ Sin perfil de usuario asignado</span>')
        
        if not obj.user_profile.user:
            return format_html('<span style="color: orange;">⚠️ Sin usuario asignado al perfil</span>')
        
        from containers.models import Service
        services = Service.objects.filter(
            owner=obj.user_profile.user,
            subject=obj.subject
        ).exclude(status='removed')
        
        count = services.count()
        
        if count == 0:
            return format_html(
                '<div style="padding: 10px; background: #f0f0f0; border-radius: 4px;">'
                '<span style="color: gray;">📦 No hay servicios desplegados para este proyecto</span><br>'
                '<small>Usuario: <strong>{}</strong> | Asignatura: <strong>{}</strong></small>'
                '</div>',
                obj.user_profile.user.username,
                obj.subject.name
            )
        
        # Construir tabla HTML
        try:
            html = f'<div style="margin: 10px 0;"><strong>🐳 {count} servicio(s) encontrado(s)</strong></div>'
            html += '<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">'
            html += '<thead><tr style="background: #417690; color: white;">'
            html += '<th style="padding: 8px; text-align: left;">Nombre</th>'
            html += '<th style="padding: 8px; text-align: left;">Imagen</th>'
            html += '<th style="padding: 8px; text-align: left;">Estado</th>'
            html += '<th style="padding: 8px; text-align: left;">Puertos</th>'
            html += '</tr></thead><tbody>'
            
            for service in services:
                # Color según estado
                if service.status == 'running':
                    status_color = 'green'
                    status_icon = '✅'
                elif service.status == 'stopped':
                    status_color = 'red'
                    status_icon = '❌'
                else:
                    status_color = 'orange'
                    status_icon = '🟡'
                
                # Formatear puertos
                if service.assigned_port and service.internal_port:
                    ports_display = f"{service.assigned_port}:{service.internal_port}"
                elif service.assigned_port:
                    ports_display = str(service.assigned_port)
                else:
                    ports_display = "-"
                
                html += '<tr style="border-bottom: 1px solid #ddd;">'
                html += f'<td style="padding: 8px;"><strong>{service.name}</strong></td>'
                html += f'<td style="padding: 8px;"><code>{service.image or "-"}</code></td>'
                html += f'<td style="padding: 8px; color: {status_color};">{status_icon} {service.status}</td>'
                html += f'<td style="padding: 8px;">{ports_display}</td>'
                html += '</tr>'
            
            html += '</tbody></table>'
            return mark_safe(html)
        except Exception as e:
            return format_html('<span style="color: red;">❌ Error: {}</span>', str(e))
    get_services_list.short_description = 'Servicios Desplegados'

    
    def get_student_name(self, obj):
        """Muestra el nombre completo del alumno"""
        if obj.user_profile and obj.user_profile.user:
            full_name = obj.user_profile.user.get_full_name()
            if full_name:
                return full_name
            return obj.user_profile.user.username
        return obj.user_profile.nombre if obj.user_profile else "-"
    get_student_name.short_description = 'Alumno'
    get_student_name.admin_order_field = 'user_profile__nombre'
    
    def get_services_count(self, obj):
        """Muestra el número de servicios del proyecto"""
        if obj.user_profile and obj.user_profile.user:
            from containers.models import Service
            count = Service.objects.filter(
                owner=obj.user_profile.user,
                subject=obj.subject
            ).exclude(status='removed').count()
            
            if count == 0:
                return "-"
            return f"🐳 {count}"
        return "0"
    get_services_count.short_description = 'Servicios'
    
    def get_project_status(self, obj):
        """Muestra el estado del proyecto según sus servicios"""
        from django.utils.html import format_html
        
        if not obj.user_profile or not obj.user_profile.user:
            return format_html('<span style="color: gray;">⚪ Sin usuario</span>')
        
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
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Todos activos ({}/{})</span>',
                running, total
            )
        elif running > 0:
            return format_html(
                '<span style="color: orange; font-weight: bold;">🟡 Algunos activos ({}/{} encendidos)</span>',
                running, total
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">❌ Todos detenidos (0/{})</span>',
                total
            )
    get_project_status.short_description = 'Estado'
    
    # De version anterior: filtrar solo alumnos en el selector de user_profile
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user_profile":
            qs = (
                UserProfile.objects
                .filter(
                    user__isnull=False,
                    user__groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES],
                )
                .select_related("user")
                .distinct()
            )
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # De version anterior: matricular automaticamente al alumno en la asignatura
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        profile = getattr(obj, "user_profile", None)
        user = getattr(profile, "user", None) if profile else None
        if user:
            obj.subject.students.add(user)


# Desregistrar el UserAdmin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Desregistrar el admin de DRF Token (usamos ExpiringToken en su lugar)
from rest_framework.authtoken.models import Token as DRFToken
try:
    admin.site.unregister(DRFToken)
except admin.sites.NotRegistered:
    pass  # Si no está registrado, no hacer nada


# =====================================================================
# ExpiringToken Admin (Tokens de API con expiración)
# =====================================================================

from paasify.models.TokenModel import ExpiringToken

@admin.register(ExpiringToken)
class ExpiringTokenAdmin(admin.ModelAdmin):
    """
    Admin para gestión de tokens de API con expiración de 30 días.
    """
    list_display = [
        'user',
        'key_preview',
        'created',
        'expires_at',
        'status_display',
        'days_remaining'
    ]
    list_filter = ['created', 'expires_at']
    search_fields = ['user__username', 'key']
    readonly_fields = ['key', 'created', 'expires_at']
    ordering = ['-created']
    
    def key_preview(self, obj):
        """Mostrar preview del token (primeros 10 caracteres)"""
        return f"{obj.key[:10]}..."
    key_preview.short_description = 'Token (preview)'
    
    def status_display(self, obj):
        """Mostrar estado del token (activo/expirado)"""
        if obj.is_expired():
            return format_html(
                '<span style="color: red; font-weight: bold;">❌ Expirado</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Activo</span>'
            )
    status_display.short_description = 'Estado'
    
    def days_remaining(self, obj):
        """Mostrar días restantes hasta expiración"""
        if obj.is_expired():
            return format_html('<span style="color: red;">0 días</span>')
        days = obj.days_until_expiration()
        if days is None:
            return 'Sin expiración'
        
        # Color según días restantes
        if days <= 7:
            color = 'red'
        elif days <= 15:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            f'<span style="color: {color}; font-weight: bold;">{days} días</span>'
        )
    days_remaining.short_description = 'Días restantes'
    
    def has_add_permission(self, request):
        """Permitir crear tokens desde admin"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar tokens (revocar)"""
        return True

