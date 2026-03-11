"""
Filtros personalizados para el admin de Django.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model

from paasify.roles import (
    DEFAULT_STUDENT_GROUP,
    DEFAULT_TEACHER_GROUP,
    STUDENT_GROUP_NAMES,
    TEACHER_GROUP_NAMES,
)

User = get_user_model()


class RoleFilter(admin.SimpleListFilter):
    """
    Filtro personalizado para filtrar usuarios por rol.
    Permite filtrar por: Admin, Teacher, Student, Sin rol.
    """
    title = 'Rol'
    parameter_name = 'role'
    
    def lookups(self, request, model_admin):
        """Define las opciones del filtro"""
        return [
            ('admin', 'Administrador'),
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
            ('none', 'Sin rol'),
        ]
    
    def queryset(self, request, queryset):
        """Filtra el queryset según el valor seleccionado"""
        if self.value() == 'admin':
            # Usuarios con is_staff=True o is_superuser=True
            return queryset.filter(is_staff=True) | queryset.filter(is_superuser=True)
        
        elif self.value() == 'teacher':
            # Usuarios en grupos de profesores
            return queryset.filter(
                groups__name__in=[DEFAULT_TEACHER_GROUP, *TEACHER_GROUP_NAMES]
            ).distinct()
        
        elif self.value() == 'student':
            # Usuarios en grupos de estudiantes, pero EXCLUYENDO profesores (para evitar solapamiento)
            return queryset.filter(
                groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES]
            ).exclude(
                groups__name__in=[DEFAULT_TEACHER_GROUP, *TEACHER_GROUP_NAMES]
            ).distinct()
        
        elif self.value() == 'none':
            # Usuarios sin grupos y sin permisos de staff
            return queryset.filter(
                groups__isnull=True,
                is_staff=False,
                is_superuser=False
            )
        
        return queryset


class UserRoleFilter(admin.SimpleListFilter):
    """
    Filtro personalizado para UserProfile por rol del usuario.
    Similar a RoleFilter pero para el modelo UserProfile.
    """
    title = 'Rol del Usuario'
    parameter_name = 'user_role'
    
    def lookups(self, request, model_admin):
        """Define las opciones del filtro"""
        return [
            ('teacher', 'Profesor'),
            ('student', 'Alumno'),
        ]
    
    def queryset(self, request, queryset):
        """Filtra el queryset según el valor seleccionado"""
        if self.value() == 'teacher':
            return queryset.filter(
                user__groups__name__in=[DEFAULT_TEACHER_GROUP, *TEACHER_GROUP_NAMES]
            ).distinct()
        
        elif self.value() == 'student':
            return queryset.filter(
                user__groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES]
            ).distinct()
        
        return queryset


class ProjectStatusFilter(admin.SimpleListFilter):
    """
    Filtro personalizado para UserProject por estado de sus servicios.
    Mejora 6.1 del plan de mejoras adicionales.
    """
    title = 'Estado del Proyecto'
    parameter_name = 'project_status'

    def lookups(self, request, model_admin):
        return [
            ('active', '✅ Todos activos'),
            ('partial', '⚠️ Parcialmente activo'),
            ('stopped', '❌ Detenido'),
            ('empty', '⚪ Sin servicios'),
        ]

    def queryset(self, request, queryset):
        from containers.models import Service
        from django.db.models import Q

        if self.value() is None:
            return queryset

        active_ids = []
        partial_ids = []
        stopped_ids = []
        empty_ids = []

        for project in queryset.select_related('user_profile__user', 'subject'):
            if not project.user_profile or not project.user_profile.user:
                empty_ids.append(project.pk)
                continue

            services = Service.objects.filter(
                owner=project.user_profile.user,
                subject=project.subject
            ).exclude(status='removed')

            total = services.count()
            if total == 0:
                empty_ids.append(project.pk)
            else:
                running = services.filter(status='running').count()
                if running == total:
                    active_ids.append(project.pk)
                elif running > 0:
                    partial_ids.append(project.pk)
                else:
                    stopped_ids.append(project.pk)

        mapping = {
            'active': active_ids,
            'partial': partial_ids,
            'stopped': stopped_ids,
            'empty': empty_ids,
        }
        return queryset.filter(pk__in=mapping.get(self.value(), []))


class ServiceImageTypeFilter(admin.SimpleListFilter):
    """
    Filtro personalizado para Service por tipo de imagen.
    Mejora 3.1 del plan de mejoras adicionales.
    """
    title = 'Tipo de imagen'
    parameter_name = 'image_type'

    def lookups(self, request, model_admin):
        return [
            ('web', '🌐 Web / Frontend'),
            ('database', '🗄️ Base de Datos'),
            ('api', '🚀 Generador de API'),
            ('misc', '📦 Miscelánea'),
            ('custom', '⚙️ Personalizado (Dockerfile/Compose)'),
        ]

    def queryset(self, request, queryset):
        from containers.models import AllowedImage

        if self.value() == 'custom':
            from django.db.models import Q
            return queryset.filter(Q(dockerfile__isnull=False) | Q(compose__isnull=False)).exclude(
                dockerfile='', compose=''
            )

        if self.value() in ('web', 'database', 'api', 'misc'):
            # Obtener nombres de imágenes de este tipo
            allowed = AllowedImage.objects.filter(image_type=self.value())
            image_names = [f"{img.name}:{img.tag}" for img in allowed]
            return queryset.filter(image__in=image_names)

        return queryset
