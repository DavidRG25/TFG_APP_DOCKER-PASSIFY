from django.apps import AppConfig


class PaasifysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paasify'

    def ready(self) -> None:
        # Importa señales para sincronizar perfiles de alumno tras la carga de la app.
        from . import signals  # noqa: F401

        return super().ready()
