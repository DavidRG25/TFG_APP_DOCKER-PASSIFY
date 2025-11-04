from django.db import models
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, verbose_name="Nombre")
    teacher = models.CharField(max_length=100, verbose_name="Profesor asignado")
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    category = models.CharField(
        max_length=100,
        verbose_name="Categoría",
        choices=[
            ("Asignatura obligatoria", "Asignatura obligatoria"),
            ("Asignatura optativa", "Asignatura optativa"),
            ("Asignatura electiva", "Asignatura electiva"),
        ],
    )

    class Meta:
        managed = True
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        db_table = "subject"

    def __str__(self):
        return self.name
