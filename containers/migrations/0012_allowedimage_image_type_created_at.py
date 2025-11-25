# Generated manually for Fase 2: AllowedImage improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers', '0011_remove_service_enable_ssh_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='allowedimage',
            name='image_type',
            field=models.CharField(
                choices=[
                    ('web', 'Web / Frontend'),
                    ('database', 'Base de Datos'),
                    ('backend', 'Backend / API'),
                    ('misc', 'Miscelánea')
                ],
                default='misc',
                help_text='Categoría de la imagen Docker',
                max_length=20,
                verbose_name='Tipo de imagen'
            ),
        ),
        migrations.AddField(
            model_name='allowedimage',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                blank=True,
                null=True,
                verbose_name='Fecha de creación'
            ),
        ),
    ]
