"""Procesadores de contexto personalizados para menús y roles."""
from .roles import user_is_admin, user_is_student, user_is_teacher


def role_flags(request):
    user = getattr(request, "user", None)
    return {
        "nav_is_student": user_is_student(user),
        "nav_is_teacher": user_is_teacher(user),
        "nav_is_admin": user_is_admin(user),
    }
