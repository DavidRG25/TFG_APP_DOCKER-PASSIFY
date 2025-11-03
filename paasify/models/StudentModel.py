from django.db import models
from django.conf import settings  # enlaza con auth.User


class Player(models.Model):
    # Vínculo al usuario real (auth). Se usa en permisos y listados.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="student_profile",
        verbose_name="Usuario (auth)",
    )

    # Campos “legacy” conservados para no romper datos existentes
    nombre = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        verbose_name="Nombre y apellidos",
    )
    year = models.CharField(
        max_length=100,
        verbose_name="Email",
    )
    sexo = models.CharField(
        max_length=100,
        verbose_name="Sexo",
        choices=[("Masculino", "M"), ("Femenino", "F")],
    )

    class Meta:
        managed = True
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"
        db_table = "player"

    def __str__(self) -> str:
        u = f" · @{self.user.username}" if self.user else ""
        return f"{self.nombre}{u}"


