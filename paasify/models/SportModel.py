from django.db import models
from django.conf import settings  # para enlazar con auth.User


class Sport(models.Model):
    # Nombre único de la asignatura
    name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        verbose_name="Nombre",
    )

    # Campo legacy (se mantiene para no romper datos existentes)
    # NO usar en lógica nueva.
    players = models.CharField(
        max_length=100,
        verbose_name="Profesor Asignado",
    )

    # Año académico
    genero = models.CharField(
        max_length=100,
        verbose_name="Año",
        choices=[
            ("2024", "2024"),
            ("2025", "2025"),
            ("2026", "2026"),
        ],
    )

    # Tipo/categoría de asignatura
    category = models.CharField(
        max_length=100,
        verbose_name="Categoría",
        choices=[
            ("Asignatura obligatorias", "Asignatura obligatorias"),
            ("Asignatura optativa", "Asignatura optativa"),
            ("Asignatura electiva", "Asignatura electiva"),
        ],
    )

    # ─────────────────────────────────────────────────────────────
    # NUEVOS CAMPOS (usar estos en lógica de permisos y vistas)
    # ─────────────────────────────────────────────────────────────
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

    class Meta:
        managed = True
        verbose_name = "Gestión de Asignatura"
        verbose_name_plural = "Gestión de Asignaturas"
        db_table = "sport"

    def __str__(self) -> str:
        return self.name
       