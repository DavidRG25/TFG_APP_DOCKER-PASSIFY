from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("paasify", "0029_alter_game_time"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Player",
            new_name="UserProfile",
        ),
        migrations.RenameModel(
            old_name="Game",
            new_name="UserProject",
        ),
        migrations.RenameField(
            model_name="userproject",
            old_name="student",
            new_name="user_profile",
        ),
        migrations.AlterModelOptions(
            name="userprofile",
            options={
                "managed": True,
                "verbose_name": "Perfil de usuario",
                "verbose_name_plural": "Perfiles de usuario",
            },
        ),
        migrations.AlterModelOptions(
            name="userproject",
            options={
                "managed": True,
                "ordering": ("-date", "-time"),
                "verbose_name": "Proyecto asignado",
                "verbose_name_plural": "Proyectos asignados",
            },
        ),
        migrations.AlterModelTable(
            name="userprofile",
            table="user_profile",
        ),
        migrations.AlterModelTable(
            name="userproject",
            table="user_project",
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="user_profile",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuario (auth)",
            ),
        ),
    ]
