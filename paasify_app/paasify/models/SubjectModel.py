import os
import uuid
from django.conf import settings
from django.db import models

def get_logo_upload_path(instance, filename):
    """
    Genera una ruta única para cada logo: logos/<hash>_<nombre>.ext
    """
    ext = filename.split('.')[-1]
    name_no_ext = os.path.splitext(filename)[0]
    # Usamos un hash de 8 caracteres para evitar colisiones
    unique_id = uuid.uuid4().hex[:8]
    final_filename = f"{unique_id}_{name_no_ext}.{ext}"
    return os.path.join('logos', final_filename)


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
        verbose_name="Año",
    )

    category = models.CharField(
        max_length=100,
        verbose_name="Categoria",
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
        upload_to=get_logo_upload_path,
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

    def save(self, *args, **kwargs):
        """Limpieza de logo antiguo al actualizar."""
        try:
            this = Subject.objects.get(id=self.id)
            if this.logo and this.logo != self.logo:
                if os.path.isfile(this.logo.path):
                    os.remove(this.logo.path)
        except Exception:
            pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Eliminar logo físico al borrar asignatura."""
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        super().delete(*args, **kwargs)
