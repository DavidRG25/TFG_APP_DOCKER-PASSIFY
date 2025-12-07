from django.conf import settings  # enlaza con auth.User
from django.db import models
from django.utils import timezone
import jwt
import datetime


class UserProfile(models.Model):
    """Perfil academico asociado a un ``auth.User`` (antiguo Player)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_profile",
        verbose_name="Usuario (auth)",
    )
    nombre = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        verbose_name="Nombre y apellidos",
    )
    year = models.CharField(
        max_length=100,
        verbose_name="Email",
    )
    
    # Campos para Bearer Token API (JWT)
    api_token = models.TextField(
        null=True,
        blank=True,
        verbose_name="Token API (JWT)",
        help_text="Token JWT para autenticacion en API. Se genera automaticamente.",
    )
    token_created_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha creacion token",
        help_text="Fecha y hora en que se genero el token actual.",
    )

    class Meta:
        managed = True
        verbose_name = "Perfil de alumno"
        verbose_name_plural = "Perfiles de alumnos"
        db_table = "user_profile"

    def __str__(self) -> str:
        usuario = f" -> @{self.user.username}" if self.user else ""
        return f"{self.nombre}{usuario}"
    
    def generate_token(self, expiration_days=365):
        """
        Genera un nuevo token JWT para el usuario.
        
        Args:
            expiration_days (int): Dias de validez del token (default: 365)
        
        Returns:
            str: Token JWT generado
        """
        if not self.user:
            raise ValueError("No se puede generar token sin usuario asociado")
        
        # Payload del JWT
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'profile_id': self.id,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiration_days),
        }
        
        # Generar token JWT
        secret_key = settings.SECRET_KEY
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # Guardar token y fecha
        self.api_token = token
        self.token_created_at = timezone.now()
        self.save()
        
        return token
    
    def refresh_token(self, expiration_days=365):
        """
        Regenera el token JWT (invalida el anterior).
        
        Args:
            expiration_days (int): Dias de validez del nuevo token (default: 365)
        
        Returns:
            str: Nuevo token JWT generado
        """
        return self.generate_token(expiration_days=expiration_days)
    
    def get_masked_token(self):
        """
        Retorna el token parcialmente oculto (solo ultimos 8 caracteres).
        
        Returns:
            str: Token enmascarado (ej: "********abc12345")
        """
        if not self.api_token:
            return None
        
        if len(self.api_token) <= 8:
            return self.api_token
        
        return "..." + self.api_token[-8:]
    
    def verify_token(self):
        """
        Verifica si el token actual es valido (no expirado).
        
        Returns:
            bool: True si el token es valido, False si esta expirado o no existe
        """
        if not self.api_token:
            return False
        
        try:
            secret_key = settings.SECRET_KEY
            jwt.decode(self.api_token, secret_key, algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    
    @staticmethod
    def get_user_from_token(token):
        """
        Obtiene el usuario asociado a un token JWT.
        
        Args:
            token (str): Token JWT a validar
        
        Returns:
            User: Usuario asociado al token, o None si el token es invalido
        """
        try:
            secret_key = settings.SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                return User.objects.get(id=user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
            return None
        
        return None


class TeacherProfile(UserProfile):
    """
    Modelo proxy para perfiles de profesores.
    Usa la misma tabla que UserProfile pero con un admin separado.
    """
    
    class Meta:
        proxy = True
        verbose_name = "Perfil de profesor"
        verbose_name_plural = "Perfiles de profesores"
