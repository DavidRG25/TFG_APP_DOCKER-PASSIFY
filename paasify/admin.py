# paasify/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model

from paasify.models.StudentModel import UserProfile
from paasify.models.SportModel import Sport
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


#  Inlines (UserProject dentro de Sport/UserProfile)

class UserProjectInlineForSubject(admin.TabularInline):
    model = UserProject
    fk_name = "sport"
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
    autocomplete_fields = ("sport",)


#  Sport (Asignaturas)

class SportAdminForm(forms.ModelForm):
    class Meta:
        model = Sport
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
        ).distinct()
        self.fields["teacher_user"].required = True

        # students: solo usuarios del grupo Student (case-insensitive)
        self.fields["students"].queryset = User.objects.filter(
            groups__name__in=[*STUDENT_GROUP_NAMES, DEFAULT_STUDENT_GROUP]
        ).distinct()
        self.fields["sexo"].required = False
        sexo_choices = UserProfile._meta.get_field("sexo").choices
        if sexo_choices:
            self.fields["sexo"].initial = sexo_choices[0][0]

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


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    form = SportAdminForm
    list_display = ("name", "category", "genero", "teacher_user")
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

    # Auto-matricular: si en el inline se añade un UserProject, matriculamos al user del alumno
    def save_formset(self, request, form, formset, change):
        objs = formset.save(commit=False)
        formset.save_m2m()

        for obj in objs:
            obj.save()

        if formset.model is UserProject:
            sport = form.instance
            for obj in objs:
                profile = getattr(obj, "user_profile", None)
                user = getattr(profile, "user", None) if profile else None
                if user:
                    sport.students.add(user)

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
        fields = ["user", "nombre", "year", "sexo"]

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
        if not cleaned.get("sexo"):
            sexo_choices = UserProfile._meta.get_field("sexo").choices
            cleaned["sexo"] = sexo_choices[0][0] if sexo_choices else "Masculino"

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
    list_display = ("nombre", "year", "sexo", "user", "es_usuario_alumno")
    search_fields = ("nombre", "year", "user__username", "user__email")
    list_filter = ("sexo",)
    autocomplete_fields = ("user",)
    inlines = [UserProjectInlineForProfile]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            user__isnull=False,
            user__groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES],
        ).distinct()

    def es_usuario_alumno(self, obj):
        return bool(
            obj.user
            and obj.user.groups.filter(
                name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES]
            ).exists()
        )
    es_usuario_alumno.boolean = True
    es_usuario_alumno.short_description = "Es alumno"


# UserProject (Proyectos)

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ("place", "user_profile", "sport", "date", "time")
    list_filter = ("sport", "date")
    search_fields = ("place", "user_profile__nombre", "sport__name")
    autocomplete_fields = ("user_profile", "sport")

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
            obj.sport.students.add(user)








