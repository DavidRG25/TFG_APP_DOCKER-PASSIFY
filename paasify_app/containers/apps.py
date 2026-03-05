from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.dispatch import receiver

@receiver(connection_created)
def set_sqlite_pragma(sender, connection, **kwargs):
    """Configura SQLite para máxima concurrencia cada vez que se crea una conexión."""
    if connection.vendor == 'sqlite':
        try:
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA synchronous=NORMAL;')
        except:
            pass

class ContainersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'containers'

    def ready(self):
        # El signal @receiver se encarga de todo de forma segura
        pass
