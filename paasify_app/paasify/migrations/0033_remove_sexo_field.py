from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('paasify', '0032_rename_sport_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='sexo',
        ),
    ]
