# containers/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Service, AllowedImage, ServiceContainer
from paasify.models.SubjectModel import Subject
from paasify.models.ProjectModel import UserProject


class ServiceSimpleSerializer(serializers.ModelSerializer):
    """Versión ligera para listados."""
    has_compose = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = (
            "id", "name", "image", "assigned_port", "status", "mode", 
            "subject", "project", "created_at", "has_compose",
        )
        read_only_fields = fields


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
