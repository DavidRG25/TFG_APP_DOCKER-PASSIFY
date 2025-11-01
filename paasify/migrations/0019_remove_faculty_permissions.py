from django.db import migrations

def remove_faculty_permissions(apps, schema_editor):
    """Elimina los 4 permisos automáticos del modelo Faculty"""
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    try:
        content_type = ContentType.objects.get(app_label='paasify', model='faculty')
        # Elimina todos los permisos asociados al modelo
        Permission.objects.filter(content_type=content_type).delete()
    except ContentType.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [
        # Reemplaza con la última migración real de tu app
        ('paasify', '0018_alter_game_time'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(remove_faculty_permissions),
    ]