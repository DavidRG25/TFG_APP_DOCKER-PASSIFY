# containers/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Service, AllowedImage
from paasify.models.SubjectModel import Subject


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializador de Service con reglas de negocio:

    Modo CATÁLOGO:
      - image: obligatoria
      - dockerfile/compose: no permitidos
      - code: ignorado (no tiene sentido en runtime si no se construye imagen)

    Modo CUSTOM:
      - EXACTAMENTE uno de: dockerfile | compose
      - image: no permitida
      - code: opcional (se usará como contexto de build o se montará en /app)
    """
    # Importante: permitir que image no sea obligatoria en modo CUSTOM
    image = serializers.CharField(required=False, allow_blank=True)

    # Extras de entrada
    custom_port = serializers.IntegerField(required=False, write_only=True)
    env_vars = serializers.JSONField(required=False)
    volumes = serializers.JSONField(required=False)

    # Permitir enlazar asignatura
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "image",
            "dockerfile",
            "compose",
            "code",
            "assigned_port",
            "status",
            "logs",
            "custom_port",
            "env_vars",
            "volumes",
            "subject",
        )
        read_only_fields = ("id", "assigned_port", "status", "logs")

    # ---- Validaciones de alto nivel ----

    def validate_env_vars(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(_("Debe ser un objeto JSON (dict)."))
        return value

    def validate_volumes(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(_("Debe ser un objeto JSON (dict)."))
        return value

    def validate_image(self, value: str) -> str:
        """
        En modo catálogo validamos que la imagen esté permitida (name:tag).
        En modo custom (cuando hay dockerfile/compose) 'image' no debe venir.
        Aquí solo normalizamos; la lógica de modo se hace en validate().
        """
        if value:
            parts = value.split(":")
            name = parts[0]
            tag = parts[1] if len(parts) > 1 else "latest"
            # Guardamos normalizado (side effect inocuo si luego es modo custom).
            return f"{name}:{tag}"
        return value

    def validate(self, attrs):
        """
        Reglas de modo y subject.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        image = attrs.get("image")
        dockerfile = attrs.get("dockerfile")
        compose = attrs.get("compose")
        subject = attrs.get("subject")

        has_image = bool(image)
        has_dockerfile = bool(dockerfile)
        has_compose = bool(compose)
        has_code = bool(attrs.get("code"))

        # ---- Reglas de modo ----
        # Custom: exactamente uno entre dockerfile / compose
        if has_dockerfile or has_compose:
            # No permitir imagen en custom
            if has_image:
                raise serializers.ValidationError(
                    {"image": _("No debe indicar imagen cuando usa Dockerfile o docker-compose.")}
                )
            if has_dockerfile and has_compose:
                raise serializers.ValidationError(
                    {"compose": _("Use Dockerfile o docker-compose, pero no ambos a la vez.")}
                )
            if not has_code:
                raise serializers.ValidationError(
                    {"code": _("Debes adjuntar el código fuente (.zip) cuando usas Dockerfile o docker-compose.")}
                )
        else:
            # Catálogo: requiere image
            if not has_image:
                raise serializers.ValidationError(
                    {"image": _("Debe seleccionar una imagen del catálogo o aportar Dockerfile/compose.")}
                )
            # Validar AllowedImage SOLO en modo catálogo
            name, tag = image.split(":")
            if not AllowedImage.objects.filter(name=name, tag=tag).exists():
                raise serializers.ValidationError(
                    {"image": _("Imagen no permitida. Seleccione una del catálogo disponible.")}
                )

        # ---- Subject: si se indica, el usuario debe tener permiso ----
        # - Si el usuario está en el grupo 'teacher/profesor' y es el teacher de la asignatura, OK.
        # - Si es alumno, debe estar matriculado en esa asignatura.
        if subject and user and user.is_authenticated:
            is_teacher_of_subject = subject.teacher_user_id == user.id
            is_enrolled = subject.students.filter(pk=user.id).exists()
            if not (is_teacher_of_subject or is_enrolled or user.is_superuser or user.is_staff):
                raise serializers.ValidationError(
                    {"subject": _("No tienes permisos sobre esta asignatura.")}
                )

        return attrs

    # ---- create/update ----

    def create(self, validated_data):
        """
        ¡Ojo! 'owner' y 'status' se pasan desde la view mediante
        serializer.save(owner=request.user, status="creating").
        Si también los añadiéramos aquí, chocaría y lanzaría:
        TypeError: QuerySet.create() got multiple values for 'owner'
        """
        return Service.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Evitar que alguien cambie el owner
        validated_data.pop("owner", None)
        return super().update(instance, validated_data)


class AllowedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedImage
        fields = ("id", "name", "tag", "description")
