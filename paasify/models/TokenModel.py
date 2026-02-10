"""
Modelo personalizado de Token con fecha de expiración.
Extiende rest_framework.authtoken.models.Token para añadir caducidad.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token


class ExpiringToken(models.Model):
    """
    Token de API con fecha de expiración.
    
    Características:
    - Caducidad de 30 días desde creación
    - Asociado a un usuario
    - Revocable manualmente
    - Visible en admin con fecha de expiración
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_token',
        verbose_name='Usuario'
    )
    key = models.CharField(
        'Token',
        max_length=40,
        unique=True,
        db_index=True
    )
    created = models.DateTimeField(
        'Fecha de creación',
        auto_now_add=True
    )
    expires_at = models.DateTimeField(
        'Fecha de expiración',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Token de API'
        verbose_name_plural = 'Tokens de API'
        ordering = ['-created']
    
    def save(self, *args, **kwargs):
        """Generar token y fecha de expiración si no existen"""
        if not self.key:
            self.key = self.generate_key()
        if not self.expires_at:
            # Caducidad de 30 días
            self.expires_at = timezone.now() + timedelta(days=30)
        return super().save(*args, **kwargs)
    
    def generate_key(self):
        """Generar token único de 40 caracteres"""
        import binascii
        import os
        return binascii.hexlify(os.urandom(20)).decode()
    
    def is_expired(self):
        """Verificar si el token ha expirado"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def days_until_expiration(self):
        """Días restantes hasta expiración"""
        if not self.expires_at:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    def __str__(self):
        return f"Token de {self.user.username} (expira: {self.expires_at.strftime('%d/%m/%Y')})"
