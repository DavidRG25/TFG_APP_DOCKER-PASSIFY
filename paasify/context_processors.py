"""Procesadores de contexto personalizados para menús y roles."""
from .roles import user_is_admin, user_is_student, user_is_teacher


def role_flags(request):
    user = getattr(request, "user", None)
    return {
        "nav_is_student": user_is_student(user),
        "nav_is_teacher": user_is_teacher(user),
        "nav_is_admin": user_is_admin(user),
    }


def global_settings(request):
    """Configuraciones globales disponibles en todos los templates."""
    from django.conf import settings
    
    # Prioridad: 1. Variable de settings (env) 2. Detección dinámica
    base_url = settings.PAASIFY_BASE_URL
    if not base_url:
        base_url = f"{request.scheme}://{request.get_host()}"
    
    return {
        "PAASIFY_BASE_URL": base_url,
        "PAASIFY_API_URL": f"{base_url}/api",
    }
