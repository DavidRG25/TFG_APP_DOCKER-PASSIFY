import os
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


def get_service_upload_path(instance, filename):
    """
    Ruta centralizada: services/<id>/<filename>
    Si no hay ID todavía, se guarda en services/tmp/ para ser movido luego.
    Se usa basename para evitar anidamientos accidentales como services/1/services/1/file.
    """
    import os
    sid = instance.id if instance.id else "tmp"
    pure_filename = os.path.basename(filename)
    return f"services/{sid}/{pure_filename}"

# Aliases para compatibilidad con migraciones antiguas
def get_dockerfile_path(instance, filename): return get_service_upload_path(instance, filename)
def get_compose_path(instance, filename): return get_service_upload_path(instance, filename)
def get_code_path(instance, filename): return get_service_upload_path(instance, filename)

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
    project = models.ForeignKey(
        "paasify.UserProject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="services",
        verbose_name="Proyecto",
    )
    name = models.CharField("Nombre", max_length=100)
    image = models.CharField("Imagen", max_length=200, blank=True)
    container_id = models.CharField("ID de contenedor", max_length=100, blank=True, null=True)
    assigned_port = models.PositiveIntegerField("Puerto asignado", null=True, blank=True)
    assigned_ports = models.JSONField("Puertos asignados (compose)", blank=True, null=True, help_text="Lista de puertos para servicios docker-compose")
    internal_port = models.PositiveIntegerField("Puerto interno", default=80)
    status = models.CharField("Estado", max_length=20, default="stopped")
    logs = models.TextField("Logs", blank=True)
    dockerfile = models.FileField("Dockerfile", upload_to=get_service_upload_path, blank=True, null=True)
    compose = models.FileField("docker-compose.yml", upload_to=get_service_upload_path, blank=True, null=True)
    code = models.FileField("Codigo fuente (zip)", upload_to=get_service_upload_path, blank=True, null=True)
    volumes = models.JSONField("Volumenes", blank=True, null=True)
    env_vars = models.JSONField("Variables de entorno", blank=True, null=True)
    build_context_dir = models.CharField("Directorio de build (tmp)", max_length=300, blank=True, null=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    # Opciones de tipado y visibilidad
    container_type = models.CharField("Tipo de contenedor", max_length=20, default='misc')
    is_web = models.BooleanField("¿Es una web accesible?", default=True)
    volume_name = models.CharField("Nombre del volumen", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        subject_suffix = f" -> {self.subject.name}" if getattr(self, "subject", None) else ""
        return f"{self.name} ({self.owner.username}){subject_suffix}"

    @property
    def has_compose(self) -> bool:
        """
        Indica si el servicio tiene docker-compose asociado.
        Verifica que tenga un archivo compose asignado O que tenga ServiceContainers asociados.
        """
        # Si tiene contenedores registrados, definitivamente es Compose
        if self.containers.exists():
            return True
            
        # Si tiene un archivo compose asignado, es Compose
        # (incluso si el archivo aún no ha sido procesado)
        return bool(self.compose)
    
    
    def get_compose_status_summary(self):
        """Retorna estado agregado: running 2/3, stopped 0/2, etc."""
        if not self.has_compose:
            return ""
        total = self.containers.count()
        if total == 0:
            return ""
        running = self.containers.filter(status="running").count()
        return f"{running}/{total}"

class ServiceContainer(models.Model):
    """
    Representa cada contenedor individual en un servicio docker-compose.
    Para servicios simples, no se usa este modelo.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="containers",
        verbose_name="Servicio",
    )
    name = models.CharField("Nombre del contenedor", max_length=100)
    container_id = models.CharField("ID Docker", max_length=100, blank=True, null=True)
    status = models.CharField("Estado", max_length=20, default="unknown")
    container_type = models.CharField("Tipo de contenedor", max_length=20, default='misc')
    is_web = models.BooleanField("¿Es una web accesible?", default=False)
    internal_ports = models.JSONField("Puertos internos", blank=True, null=True)
    assigned_ports = models.JSONField("Puertos asignados", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("service", "name")
        ordering = ("service", "name")
        verbose_name = "Contenedor de Servicio"
        verbose_name_plural = "Contenedores de Servicio"

    def __str__(self) -> str:
        return f"{self.service.name}:{self.name}"


class AllowedImage(models.Model):
    """Catalogo de imagenes permitidas para el modo catalogo."""
    
    IMAGE_TYPES = [
        ('web', 'Web / Frontend'),
        ('database', 'Base de Datos'),
        ('api', 'Generador de API'),
        ('misc', 'Miscelánea'),
    ]
    
    name = models.CharField(max_length=80)
    tag = models.CharField(max_length=40, default="latest")
    description = models.CharField(max_length=150, blank=True)
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES,
        default='misc',
        verbose_name='Tipo de imagen',
        help_text='Categoría de la imagen Docker. Define las funcionalidades disponibles a nivel de servicio.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        null=True,  # Para permitir migración de datos existentes
        blank=True
    )

    class Meta:
        unique_together = ("name", "tag")
        verbose_name = "Imagen permitida"
        verbose_name_plural = "Imagenes permitidas"
        ordering = ("name", "tag")

    def __str__(self) -> str:
        return f"{self.name}:{self.tag}"


# ==================== SIGNALS PARA LIMPIEZA AUTOMÁTICA ====================
from django.db.models.signals import post_delete
from django.dispatch import receiver
import shutil
from pathlib import Path

@receiver(post_delete, sender=Service)
def auto_cleanup_service_files(sender, instance, **kwargs):
    """
    Limpia todos los rastro físicos de un servicio al borrarlo de la BD.
    Ahora centralizado en una única carpeta por servicio.
    """
    try:
        from .services import cleanup_service_workspace
        cleanup_service_workspace(instance)
    except Exception:
        pass
