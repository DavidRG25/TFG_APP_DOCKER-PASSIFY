# containers/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Service, AllowedImage, ServiceContainer
from paasify.models.SubjectModel import Subject


class ServiceContainerSerializer(serializers.ModelSerializer):
    """Serializer para contenedores individuales en servicios docker-compose"""
    class Meta:
        model = ServiceContainer
        fields = (
            "id",
            "name",
            "container_id",
            "status",
            "internal_ports",
            "assigned_ports",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields  # Todos son de solo lectura


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
    internal_port = serializers.IntegerField(required=False, allow_null=True)

    # Permitir enlazar asignatura
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )

    # Campo calculado para indicar si usa docker-compose
    has_compose = serializers.ReadOnlyField()
    
    # Relación con contenedores (para modo compose)
    containers = ServiceContainerSerializer(many=True, read_only=True)

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
            "internal_port",
            "has_compose",  # Añadido
            "containers",    # Añadido
        )
        read_only_fields = ("id", "assigned_port", "status", "logs", "has_compose", "containers")

    # ---- Validaciones de alto nivel ----

    def validate_env_vars(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError(_("Debe ser un objeto JSON (dict)."))
        return value

    def validate_volumes(self, value):
        # SEGURIDAD CRÍTICA: Rechazar completamente el campo volumes
        # Los volúmenes solo se permiten en Docker Compose con validación estricta
        if value is not None:
            raise serializers.ValidationError(
                "Por razones de seguridad, no se permiten volúmenes en contenedores simples. "
                "Los volúmenes solo están disponibles en Docker Compose con validación estricta."
            )
        return None

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

    def validate_compose(self, value):
        """
        Validar docker-compose.yml:
        - Máximo 5 contenedores permitidos
        - Al menos 1 servicio definido
        - Sintaxis YAML válida
        """
        if not value:
            return value
        
        import yaml
        
        try:
            # Leer contenido del archivo
            content = value.read()
            value.seek(0)  # Reset file pointer para uso posterior
            
            # Parsear YAML
            compose_data = yaml.safe_load(content)
            
            if not compose_data or not isinstance(compose_data, dict):
                raise serializers.ValidationError(
                    "El archivo docker-compose.yml no tiene un formato válido."
                )
            
            # Obtener servicios
            services = compose_data.get('services', {})
            
            if not isinstance(services, dict):
                raise serializers.ValidationError(
                    "La sección 'services' debe ser un diccionario."
                )
            
            num_services = len(services)
            
            # Validar mínimo
            if num_services == 0:
                raise serializers.ValidationError(
                    "El docker-compose debe tener al menos 1 servicio definido."
                )
            
            # Validar máximo
            MAX_CONTAINERS = 5
            if num_services > MAX_CONTAINERS:
                service_names = ', '.join(services.keys())
                raise serializers.ValidationError(
                    f"Máximo {MAX_CONTAINERS} contenedores permitidos. "
                    f"Tu docker-compose tiene {num_services} servicios: {service_names}"
                )
            
            # SEGURIDAD CRÍTICA: Validar volúmenes para prevenir bind mounts
            for service_name, service_config in services.items():
                if not isinstance(service_config, dict):
                    continue
                
                volumes_list = service_config.get('volumes', [])
                if not volumes_list:
                    continue
                
                # Validar cada volumen
                for volume in volumes_list:
                    if isinstance(volume, str):
                        # Detectar bind mounts (rutas absolutas o relativas)
                        if volume.startswith('/') or volume.startswith('./') or volume.startswith('../'):
                            raise serializers.ValidationError(
                                f"SEGURIDAD: Bind mounts no permitidos en servicio '{service_name}'. "
                                f"Volumen rechazado: '{volume}'. "
                                f"Solo se permiten volúmenes nombrados (ej: 'mi_volumen:/path')."
                            )
                        
                        # Detectar bind mounts con : (ej: /host/path:/container/path)
                        if ':' in volume:
                            parts = volume.split(':')
                            host_part = parts[0]
                            # Si la parte del host es una ruta (empieza con / o .), es bind mount
                            if host_part.startswith('/') or host_part.startswith('.'):
                                raise serializers.ValidationError(
                                    f"SEGURIDAD: Bind mounts no permitidos en servicio '{service_name}'. "
                                    f"Volumen rechazado: '{volume}'. "
                                    f"Solo se permiten volúmenes nombrados (ej: 'mi_volumen:/path')."
                                )
                    elif isinstance(volume, dict):
                        # Formato largo de volúmenes
                        volume_type = volume.get('type', 'volume')
                        source = volume.get('source', '')
                        
                        # Rechazar bind mounts explícitos
                        if volume_type == 'bind':
                            raise serializers.ValidationError(
                                f"SEGURIDAD: Bind mounts no permitidos en servicio '{service_name}'. "
                                f"Solo se permiten volúmenes nombrados (type: volume)."
                            )
                        
                        # Validar que source no sea una ruta
                        if source and (source.startswith('/') or source.startswith('.')):
                            raise serializers.ValidationError(
                                f"SEGURIDAD: Rutas de host no permitidas en servicio '{service_name}'. "
                                f"Source rechazado: '{source}'. "
                                f"Solo se permiten nombres de volúmenes."
                            )
            
            # SEGURIDAD CRÍTICA: Validar configuraciones peligrosas
            DANGEROUS_CONFIGS = {
                'privileged': 'Modo privilegiado no permitido (escalada de privilegios)',
                'network_mode': 'Network mode host no permitido (acceso a red del host)',
                'pid': 'PID mode host no permitido (acceso a procesos del host)',
                'ipc': 'IPC mode host no permitido (acceso a IPC del host)',
            }
            
            for service_name, service_config in services.items():
                if not isinstance(service_config, dict):
                    continue
                
                # Validar privileged
                if service_config.get('privileged', False):
                    raise serializers.ValidationError(
                        f"SEGURIDAD: Servicio '{service_name}' usa 'privileged: true'. "
                        f"{DANGEROUS_CONFIGS['privileged']}"
                    )
                
                # Validar network_mode
                network_mode = service_config.get('network_mode', '')
                if network_mode == 'host':
                    raise serializers.ValidationError(
                        f"SEGURIDAD: Servicio '{service_name}' usa 'network_mode: host'. "
                        f"{DANGEROUS_CONFIGS['network_mode']}"
                    )
                
                # Validar pid
                pid_mode = service_config.get('pid', '')
                if pid_mode == 'host':
                    raise serializers.ValidationError(
                        f"SEGURIDAD: Servicio '{service_name}' usa 'pid: host'. "
                        f"{DANGEROUS_CONFIGS['pid']}"
                    )
                
                # Validar ipc
                ipc_mode = service_config.get('ipc', '')
                if ipc_mode == 'host':
                    raise serializers.ValidationError(
                        f"SEGURIDAD: Servicio '{service_name}' usa 'ipc: host'. "
                        f"{DANGEROUS_CONFIGS['ipc']}"
                    )
                
                # Validar cap_add (capabilities peligrosas)
                DANGEROUS_CAPS = [
                    'SYS_ADMIN',      # Administración del sistema
                    'SYS_MODULE',     # Cargar módulos del kernel
                    'SYS_RAWIO',      # Acceso directo a I/O
                    'SYS_PTRACE',     # Debugging de procesos
                    'SYS_BOOT',       # Reiniciar sistema
                    'NET_ADMIN',      # Administración de red
                    'DAC_OVERRIDE',   # Bypass de permisos
                    'DAC_READ_SEARCH',# Bypass de lectura
                ]
                
                cap_add = service_config.get('cap_add', [])
                if cap_add:
                    if isinstance(cap_add, list):
                        for cap in cap_add:
                            cap_upper = str(cap).upper()
                            if cap_upper in DANGEROUS_CAPS:
                                raise serializers.ValidationError(
                                    f"SEGURIDAD: Servicio '{service_name}' intenta añadir capability '{cap}'. "
                                    f"Capabilities peligrosas no permitidas: {', '.join(DANGEROUS_CAPS)}"
                                )
                
                # Validar devices (acceso a dispositivos del host)
                if 'devices' in service_config:
                    raise serializers.ValidationError(
                        f"SEGURIDAD: Servicio '{service_name}' intenta montar dispositivos del host. "
                        f"Acceso a dispositivos no permitido."
                    )
            
        except yaml.YAMLError as e:
            raise serializers.ValidationError(
                f"Error al parsear docker-compose.yml: {str(e)}"
            )
        
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
        name = attrs.get("name") or getattr(self.instance, "name", None)
        internal_port = attrs.get("internal_port", None)

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
                    {"code": "Debes adjuntar un archivo .zip o .rar con el codigo fuente."}
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

        # ---- Nombre unico por alumno (excluyendo servicios eliminados) ----
        if name and user and user.is_authenticated:
            qs = Service.objects.filter(owner=user, name=name).exclude(status="removed")
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"name": "Ya existe un servicio tuyo con este nombre."}
                )

        # ---- Puerto interno opcional ----
        if internal_port is None:
            attrs["internal_port"] = 80
        else:
            try:
                ip = int(internal_port)
            except (TypeError, ValueError):
                raise serializers.ValidationError({"internal_port": "Debe ser un numero entre 1 y 65535."})
            if not (1 <= ip <= 65535):
                raise serializers.ValidationError({"internal_port": "Debe estar entre 1 y 65535."})
            attrs["internal_port"] = ip

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
