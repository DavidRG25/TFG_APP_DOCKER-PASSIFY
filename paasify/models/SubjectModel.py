from django.conf import settings
from django.db import models


class Subject(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        verbose_name="Nombre",
    )

    # Campo legacy para compatibilidad (no usar en logica nueva).
    players = models.CharField(
        max_length=100,
        verbose_name="Profesor asignado",
    )

    genero = models.CharField(
        max_length=100,
        verbose_name="Ano",
        choices=[
            ("2024", "2024"),
            ("2025", "2025"),
            ("2026", "2026"),
        ],
    )

    category = models.CharField(
        max_length=100,
        verbose_name="Categoria",
        choices=[
            ("Asignatura obligatorias", "Asignatura obligatorias"),
            ("Asignatura optativa", "Asignatura optativa"),
            ("Asignatura electiva", "Asignatura electiva"),
        ],
    )

    teacher_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="subjects_as_teacher",
        verbose_name="Profesor asignado (usuario)",
    )

    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="subjects_as_student",
        verbose_name="Alumnos matriculados (usuarios)",
    )

    logo = models.ImageField(
        upload_to="logos/",
        null=True,
        blank=True,
        verbose_name="Logo de la asignatura",
    )

    color = models.CharField(
        max_length=7,
        default="#4e73df",
        verbose_name="Color de la asignatura",
    )

    class Meta:
        managed = True
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        db_table = "subject"

    def __str__(self) -> str:
        return self.name
