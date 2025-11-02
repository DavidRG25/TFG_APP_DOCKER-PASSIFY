from django.conf import settings
from django.db import models

# Rango de puertos expuestos hacia el host
PORT_RANGE_START = 40000
PORT_RANGE_END = 50000


class PortReservation(models.Model):
    """
    Reserva lógica de puertos para evitar colisiones entre servicios.
    """
    port = models.PositiveIntegerField(unique=True)
    reserved_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def reserve_free_port(cls) -> int:
        """
        Devuelve un puerto libre dentro del rango y lo marca como reservado.
        """
        used = set(cls.objects.values_list("port", flat=True))
        for p in range(PORT_RANGE_START, PORT_RANGE_END):
            if p not in used:
                cls.objects.create(port=p)
                return p
        raise RuntimeError("No free ports available")

    def __str__(self) -> str:
        return str(self.port)


class Service(models.Model):
    """
    Servicio/Contenedor desplegado por un usuario.
    Puede pertenecer opcionalmente a una asignatura (subject).
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Propietario",
    )

    # Asignatura a la que pertenece el servicio (opcional)
    subject = models.ForeignKey(
        "paasify.Sport",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="services",
        verbose_name="Asignatura",
    )

    name = models.CharField("Nombre", max_length=100)

    # Imagen usada al ejecutar (modo catálogo). En modo custom se ignora y se
    # construye a partir de Dockerfile / docker-compose.
    image = models.CharField("Imagen", max_length=200)

    container_id = models.CharField("ID de contenedor", max_length=100, blank=True, null=True)

    # Puerto publicado en el host (si aplica). En docker-compose puede no usarse.
    assigned_port = models.PositiveIntegerField("Puerto asignado", null=True, blank=True)

    # Puerto interno del contenedor que se mapeará al host (por defecto 80).
    internal_port = models.PositiveIntegerField("Puerto interno", default=80)

    status = models.CharField("Estado", max_length=20, default="stopped")
    logs = models.TextField("Logs", blank=True)

    # Archivos opcionales para modo custom
    dockerfile = models.FileField(
        "Dockerfile",
        upload_to="dockerfiles/",
        blank=True,
        null=True,
    )
    compose = models.FileField(
        "docker-compose.yml",
        upload_to="compose_files/",
        blank=True,
        null=True,
    )
    code = models.FileField(  # ZIP de código fuente
        "Código fuente (zip)",
        upload_to="user_code/",
        blank=True,
        null=True,
    )

    # Extras (opcionales)
    volumes = models.JSONField("Volúmenes", blank=True, null=True)     # dict {host_path: {bind, mode}, ...}
    env_vars = models.JSONField("Variables de entorno", blank=True, null=True)  # dict {"KEY": "VAL", ...}
    build_context_dir = models.CharField(  # ruta temporal del contexto de build (si se usa)
        "Directorio de build (tmp)",
        max_length=300,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField("Creado", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        subj = f" · {self.subject.name}" if getattr(self, "subject", None) else ""
        return f"{self.name} ({self.owner.username}){subj}"


class AllowedImage(models.Model):
    """
    Catálogo de imágenes permitidas para el modo 'catálogo'.
    """
    name = models.CharField(max_length=80)
    tag = models.CharField(max_length=40, default="latest")
    description = models.CharField(max_length=150, blank=True)

    class Meta:
        unique_together = ("name", "tag")
        verbose_name = "Imagen permitida"
        verbose_name_plural = "Imágenes permitidas"
        ordering = ("name", "tag")

    def __str__(self) -> str:
        return f"{self.name}:{self.tag}"
