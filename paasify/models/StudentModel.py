from django.conf import settings  # enlaza con auth.User
from django.db import models


class UserProfile(models.Model):
    """Perfil academico asociado a un ``auth.User`` (antiguo Player)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_profile",
        verbose_name="Usuario (auth)",
    )
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
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"
        db_table = "user_profile"

    def __str__(self) -> str:
        usuario = f" -> @{self.user.username}" if self.user else ""
        return f"{self.nombre}{usuario}"
