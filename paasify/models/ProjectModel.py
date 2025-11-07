from django.db import models
from django.utils import timezone

from paasify.models.SubjectModel import Subject
from paasify.models.StudentModel import UserProfile


def current_time():
    return timezone.localtime().time()


class UserProject(models.Model):
    place = models.CharField(
        max_length=100,
        verbose_name="Nombre del Proyecto",
    )
    user_profile = models.ForeignKey(
        to=UserProfile,
        on_delete=models.DO_NOTHING,
        verbose_name="Alumno Asignado",
        related_name="projects",
    )
    subject = models.ForeignKey(
        to=Subject,
        on_delete=models.DO_NOTHING,
        verbose_name="Asignatura Asociada",
        related_name="projects",
    )
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    time = models.TimeField(default=current_time, verbose_name="Hora")

    class Meta:
        managed = True
        db_table = "user_project"
        verbose_name = "Proyecto asignado"
        verbose_name_plural = "Proyectos asignados"
        ordering = ("-date", "-time")

    def __str__(self):
        return f"{self.place} -> {self.subject} -> {self.user_profile}"
