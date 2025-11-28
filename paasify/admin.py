# paasify/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from paasify.models.StudentModel import UserProfile
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
    extra = 1
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
    extra = 1
    autocomplete_fields = ("subject",)


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
    autocomplete_fields = ("teacher_user",)
    filter_horizontal = ("students",)
    inlines = [UserProjectInlineForSubject]
    exclude = ("players",)  # oculta campo legacy

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
    - Elegir usuario existente (sin UserProfile) o crear uno nuevo → añade a grupo Student.
    - Al editar, si ya tiene user, no obliga a elegir uno.
    """
    create_new_user = forms.BooleanField(required=False, label="Crear usuario nuevo")
    new_username = forms.CharField(required=False, label="Usuario")
    new_email = forms.EmailField(required=False, label="Email")
    new_password1 = forms.CharField(required=False, widget=forms.PasswordInput, label="Contraseña")
    new_password2 = forms.CharField(required=False, widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = UserProfile
        fields = ["user", "nombre", "year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Users sin UserProfile; si estamos editando, incluir también el user actual
        base_qs = User.objects.filter(user_profile__isnull=True)
        if self.instance and self.instance.pk and self.instance.user_id:
            base_qs = (base_qs | User.objects.filter(pk=self.instance.user_id)).distinct()
        self.fields["user"].required = False
        self.fields["user"].queryset = base_qs

        # Permitir autocompletado cuando se crea o vincula un usuario
        self.fields["nombre"].required = False
        self.fields["year"].required = False

    def clean(self):
        cleaned = super().clean()
        create = cleaned.get("create_new_user")
        selected_user = cleaned.get("user")

        # Si ya hay user enlazado y no se crea uno nuevo, permitir sin select
        if self.instance and self.instance.pk and self.instance.user_id and not create:
            return cleaned

        if create:
            for f in ("new_username", "new_email", "new_password1", "new_password2"):
                if not cleaned.get(f):
                    self.add_error(f, "Requerido")
            if cleaned.get("new_password1") != cleaned.get("new_password2"):
                self.add_error("new_password2", "Las contraseñas no coinciden")
            if cleaned.get("new_username") and User.objects.filter(
                username=cleaned["new_username"]
            ).exists():
                self.add_error("new_username", "Este usuario ya existe")
            if not cleaned.get("nombre"):
                cleaned["nombre"] = cleaned.get("new_username") or cleaned.get("new_email")
            if not cleaned.get("year"):
                cleaned["year"] = cleaned.get("new_email") or f"{cleaned.get('new_username') or 'alumno'}@pendiente.local"
        else:
            if not selected_user:
                raise forms.ValidationError(
                    "Seleccione un usuario existente o marque 'Crear usuario nuevo'."
                )
            if selected_user and not cleaned.get("nombre"):
                cleaned["nombre"] = (
                    selected_user.get_full_name()
                    or selected_user.get_username()
                    or selected_user.email
                    or f"alumno-{selected_user.pk}"
                )
            if selected_user and not cleaned.get("year"):
                cleaned["year"] = selected_user.email or f"{selected_user.get_username()}@pendiente.local"

        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        create = self.cleaned_data.get("create_new_user")
        if create:
            u = User(username=self.cleaned_data["new_username"], email=self.cleaned_data["new_email"])
            u._skip_user_profile_autocreate = True
            u.set_password(self.cleaned_data["new_password1"])
            u.save()
            ensure_user_group(u, STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP)
            profile.user = u
        else:
            u = self.cleaned_data.get("user") or self.instance.user
            if u:
                ensure_user_group(u, STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP)
                profile.user = u

        # Autocompletar nombre/email si faltan
        if profile.user:
            if not profile.nombre:
                profile.nombre = profile.user.get_username()
            if not profile.year:
                profile.year = profile.user.email

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
    autocomplete_fields = ("user",)
    inlines = [UserProjectInlineForProfile]
    readonly_fields = ("api_token", "token_created_at")
    actions = ["refresh_api_tokens"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            user__isnull=False,
            user__groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES],
        ).distinct()
    
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
    display_token.short_description = "Token API"
    
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


# UserProject (Proyectos)

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ("place", "user_profile", "subject", "date", "time")
    list_filter = ("subject", "date")
    search_fields = ("place", "user_profile__nombre", "subject__name")
    autocomplete_fields = ("user_profile", "subject")

    # Solo UserProfiles cuyo user pertenece al grupo Student
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

    # Al guardar un UserProject, matricula automáticamente al user del alumno en la asignatura
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        profile = getattr(obj, "user_profile", None)
        user = getattr(profile, "user", None) if profile else None
        if user:
            obj.subject.students.add(user)




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
    )
    search_fields = (
        'place',
        'user_profile__nombre',
        'user_profile__user__username',
        'subject__name',
    )
    list_filter = ('subject',)
    autocomplete_fields = ('user_profile', 'subject')
    
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
                '<span style="color: orange; font-weight: bold;">⚠️ Parcialmente activo ({}/{})</span>',
                running, total
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">❌ Detenido (0/{})</span>',
                total
            )
    get_project_status.short_description = 'Estado'


# Desregistrar el UserAdmin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

