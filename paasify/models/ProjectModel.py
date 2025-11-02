from django.db import models
from django.utils import timezone
from datetime import datetime

from paasify.models.SportModel import Sport
from paasify.models.StudentModel import Player


class Game(models.Model):
    place = models.CharField(
        max_length=100,
        verbose_name="Nombre del Proyecto",
    )
    student = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        verbose_name="Alumno Asignado",
        related_name="projects",
    )
    sport = models.ForeignKey(
        to=Sport,
        on_delete=models.DO_NOTHING,
        verbose_name="Asignatura Asociada",
        related_name="projects",
    )
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    time = models.TimeField(default=datetime.now().time(), verbose_name="Hora")

    class Meta:
        managed = True
        db_table = "game"
        verbose_name = "Gestión de Proyecto"
        verbose_name_plural = "Gestión de Proyectos"
        ordering = ("-date", "-time")

    def __str__(self):
        return f"{self.place} · {self.sport} · {self.student}"