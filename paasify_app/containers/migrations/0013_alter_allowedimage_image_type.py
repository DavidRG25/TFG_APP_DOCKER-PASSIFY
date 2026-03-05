# Generated manually for actualizar tipo 'backend' a 'api'

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0012_allowedimage_image_type_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allowedimage',
            name='image_type',
            field=models.CharField(
                choices=[
                    ('web', 'Web / Frontend'),
                    ('database', 'Base de Datos'),
                    ('api', 'Generador de API'),
                    ('misc', 'Miscelánea')
                ],
                default='misc',
                help_text='Categoría de la imagen Docker. Define las funcionalidades disponibles a nivel de servicio.',
                max_length=20,
                verbose_name='Tipo de imagen'
            ),
        ),
    ]
