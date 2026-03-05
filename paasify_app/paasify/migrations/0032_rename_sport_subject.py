from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("paasify", "0031_alter_userproject_time"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Sport",
            new_name="Subject",
        ),
        migrations.RenameField(
            model_name="userproject",
            old_name="sport",
            new_name="subject",
        ),
        migrations.AlterModelOptions(
            name="subject",
            options={
                "managed": True,
                "verbose_name": "Asignatura",
                "verbose_name_plural": "Asignaturas",
            },
        ),
        migrations.AlterModelTable(
            name="subject",
            table="subject",
        ),
    ]
