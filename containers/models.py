from django.conf import settings
from django.db import models, transaction
from django.db.utils import IntegrityError

# Rango de puertos expuestos hacia el host
PORT_RANGE_START = 40000
PORT_RANGE_END = 50000


class PortReservation(models.Model):
    """Reserva logica de puertos para evitar colisiones entre servicios."""

    port = models.PositiveIntegerField(unique=True)
    reserved_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def reserve_free_port(cls) -> int:
        """Devuelve un puerto libre dentro del rango y lo marca como reservado."""
        for port in range(PORT_RANGE_START, PORT_RANGE_END):
            try:
                with transaction.atomic():
                    cls.objects.create(port=port)
                return port
            except IntegrityError:
                continue
        raise RuntimeError("No free ports available")

    def __str__(self) -> str:
        return str(self.port)


class Service(models.Model):
    """Servicio o contenedor desplegado por un usuario."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Propietario",
    )
    subject = models.ForeignKey(
        "paasify.Subject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="services",
        verbose_name="Asignatura",
    )
    name = models.CharField("Nombre", max_length=100)
    image = models.CharField("Imagen", max_length=200)
    container_id = models.CharField("ID de contenedor", max_length=100, blank=True, null=True)
    assigned_port = models.PositiveIntegerField("Puerto asignado", null=True, blank=True)
    internal_port = models.PositiveIntegerField("Puerto interno", default=80)
    status = models.CharField("Estado", max_length=20, default="stopped")
    logs = models.TextField("Logs", blank=True)
    dockerfile = models.FileField("Dockerfile", upload_to="dockerfiles/", blank=True, null=True)
    compose = models.FileField("docker-compose.yml", upload_to="compose_files/", blank=True, null=True)
    code = models.FileField("Codigo fuente (zip)", upload_to="user_code/", blank=True, null=True)
    volumes = models.JSONField("Volumenes", blank=True, null=True)
    env_vars = models.JSONField("Variables de entorno", blank=True, null=True)
    build_context_dir = models.CharField("Directorio de build (tmp)", max_length=300, blank=True, null=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    # Opciones
    volume_name = models.CharField("Nombre del volumen", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        subject_suffix = f" -> {self.subject.name}" if getattr(self, "subject", None) else ""
        return f"{self.name} ({self.owner.username}){subject_suffix}"


class AllowedImage(models.Model):
    """Catalogo de imagenes permitidas para el modo catalogo."""

    name = models.CharField(max_length=80)
    tag = models.CharField(max_length=40, default="latest")
    description = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = ("name", "tag")
        verbose_name = "Imagen permitida"
        verbose_name_plural = "Imagenes permitidas"
        ordering = ("name", "tag")

    def __str__(self) -> str:
        return f"{self.name}:{self.tag}"
