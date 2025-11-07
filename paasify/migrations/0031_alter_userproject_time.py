from django.db import migrations, models

import paasify.models.ProjectModel


class Migration(migrations.Migration):

    dependencies = [
        ("paasify", "0030_rename_player_game"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userproject",
            name="time",
            field=models.TimeField(
                default=paasify.models.ProjectModel.current_time,
                verbose_name="Hora",
            ),
        ),
    ]
