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
            # Usuarios en grupos de estudiantes
            return queryset.filter(
                groups__name__in=[DEFAULT_STUDENT_GROUP, *STUDENT_GROUP_NAMES]
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
