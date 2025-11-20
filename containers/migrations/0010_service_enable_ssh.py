from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("containers", "0009_service_ssh_password"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="enable_ssh",
            field=models.BooleanField(default=False, verbose_name="Wrapper SSH integrado"),
        ),
    ]

