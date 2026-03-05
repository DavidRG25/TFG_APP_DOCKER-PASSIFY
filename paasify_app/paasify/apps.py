from django.apps import AppConfig
from django.template.defaultfilters import register

@register.filter(is_safe=False)
def length_is(value, arg):
    """Return a boolean of whether the value's length is the argument."""
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return ""

class PaasifysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paasify'

    def ready(self) -> None:
        # Importa señales para sincronizar perfiles de alumno tras la carga de la app.
        from . import signals  # noqa: F401

        return super().ready()
