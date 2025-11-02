# paasify/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from paasify.models.StudentModel import Player
from paasify.models.SportModel import Sport
from paasify.models.ProjectModel import Game

User = get_user_model()

# Nombres “canónicos”
TEACHER_GROUP = "Teacher"
STUDENT_GROUP = "Student"

admin.site.site_header = "PaaSify · Admin"
admin.site.index_title = "Panel de administración"
admin.site.site_title = "PaaSify"


#  Inlines (Game dentro de Sport/Player)

class GameInlineForSubject(admin.TabularInline):
    model = Game
    fk_name = "sport"
    extra = 1
    autocomplete_fields = ("student",)

    # Solo Players cuyo user ∈ grupo Student
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = (
                Player.objects
                .filter(user__isnull=False, user__groups__name__iexact=STUDENT_GROUP)
                .select_related("user")
                .distinct()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class GameInlineForPlayer(admin.TabularInline):
    model = Game
    fk_name = "student"
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
            groups__name__in=["profesor", TEACHER_GROUP]
        ).distinct()
        self.fields["teacher_user"].required = True

        # students: solo usuarios del grupo Student (case-insensitive)
        self.fields["students"].queryset = User.objects.filter(
            groups__name__iexact=STUDENT_GROUP
        ).distinct()

    def clean_teacher_user(self):
        u = self.cleaned_data.get("teacher_user")
        if not u:
            raise forms.ValidationError("Debes asignar un profesor.")
        if not u.groups.filter(name__in=["profesor", TEACHER_GROUP]).exists():
            raise forms.ValidationError(
                "El usuario seleccionado no pertenece al grupo Profesor/Teacher."
            )
        return u

    def clean_students(self):
        qs = self.cleaned_data.get("students")
        if not qs:
            return qs
        bad = qs.exclude(groups__name__iexact=STUDENT_GROUP)
        if bad.exists():
            raise forms.ValidationError("Todos los alumnos deben pertenecer al grupo Student.")
        return qs


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    form = SportAdminForm
    list_display = ("name", "category", "genero", "teacher_user")
    search_fields = ("name", "teacher_user__username", "teacher_user__email")
    list_filter = ("category", "genero")
    autocomplete_fields = ("teacher_user",)
    filter_horizontal = ("students",)
    inlines = [GameInlineForSubject]
    exclude = ("players",)  # oculta campo legacy

    # Defensa extra si se cambia el form
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher_user":
            kwargs["queryset"] = User.objects.filter(
                groups__name__in=["profesor", TEACHER_GROUP]
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Auto-matricular: si en el inline se añade un Game, matriculamos al user del alumno
    def save_formset(self, request, form, formset, change):
        objs = formset.save(commit=False)
        formset.save_m2m()

        for obj in objs:
            obj.save()

        if formset.model is Game:
            sport = form.instance
            for obj in objs:
                if getattr(obj, "student", None) and getattr(obj.student, "user", None):
                    sport.students.add(obj.student.user)

        for obj in formset.deleted_objects:
            obj.delete()


#  Player (Alumnos)

class PlayerAdminForm(forms.ModelForm):
    """
    - Elegir usuario existente (sin Player) o crear uno nuevo → añade a grupo Student.
    - Al editar, si ya tiene user, no obliga a elegir uno.
    """
    create_new_user = forms.BooleanField(required=False, label="Crear usuario nuevo")
    new_username = forms.CharField(required=False, label="Usuario")
    new_email = forms.EmailField(required=False, label="Email")
    new_password1 = forms.CharField(required=False, widget=forms.PasswordInput, label="Contraseña")
    new_password2 = forms.CharField(required=False, widget=forms.PasswordInput, label="Confirmar contraseña")

    class Meta:
        model = Player
        fields = ["user", "nombre", "year", "sexo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Users sin Player; si estamos editando, incluir también el user actual
        base_qs = User.objects.filter(student_profile__isnull=True)
        if self.instance and self.instance.pk and self.instance.user_id:
            base_qs = (base_qs | User.objects.filter(pk=self.instance.user_id)).distinct()
        self.fields["user"].required = False
        self.fields["user"].queryset = base_qs

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
        else:
            if not selected_user:
                raise forms.ValidationError(
                    "Seleccione un usuario existente o marque 'Crear usuario nuevo'."
                )
        return cleaned

    def save(self, commit=True):
        player = super().save(commit=False)
        create = self.cleaned_data.get("create_new_user")
        student_group, _ = Group.objects.get_or_create(name=STUDENT_GROUP)

        if create:
            u = User(username=self.cleaned_data["new_username"], email=self.cleaned_data["new_email"])
            u.set_password(self.cleaned_data["new_password1"])
            u.save()
            u.groups.add(student_group)
            player.user = u
        else:
            u = self.cleaned_data.get("user") or self.instance.user
            if u:
                u.groups.add(student_group)
                player.user = u

        # Autocompletar nombre/email si faltan
        if player.user:
            if not player.nombre:
                player.nombre = player.user.get_username()
            if not player.year:
                player.year = player.user.email

        if commit:
            player.save()
            self.save_m2m()
        return player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    form = PlayerAdminForm
    list_display = ("nombre", "year", "sexo", "user", "es_usuario_alumno")
    search_fields = ("nombre", "year", "user__username", "user__email")
    list_filter = ("sexo",)
    autocomplete_fields = ("user",)
    inlines = [GameInlineForPlayer]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            user__isnull=False,
            user__groups__name__iexact=STUDENT_GROUP
        ).distinct()

    def es_usuario_alumno(self, obj):
        return bool(obj.user and obj.user.groups.filter(name__iexact=STUDENT_GROUP).exists())
    es_usuario_alumno.boolean = True
    es_usuario_alumno.short_description = "Es alumno"


# Game (Proyectos)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("place", "student", "sport", "date", "time")
    list_filter = ("sport", "date")
    search_fields = ("place", "student__nombre", "sport__name")
    autocomplete_fields = ("student", "sport")

    # Solo Players cuyo user pertenece al grupo Student
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            qs = (
                Player.objects
                .filter(user__isnull=False, user__groups__name__iexact=STUDENT_GROUP)
                .select_related("user")
                .distinct()
            )
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Al guardar un Game, matricula automáticamente al user del alumno en la asignatura
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if getattr(obj, "student", None) and getattr(obj.student, "user", None):
            obj.sport.students.add(obj.student.user)