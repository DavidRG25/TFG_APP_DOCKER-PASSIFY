import os
from pathlib import Path

# ---------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# Seguridad / Debug
# ---------------------------------------------------------------------
def _get_bool(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-placeholder-secret-key-change-me",
)

DEBUG = _get_bool("DJANGO_DEBUG", "false")

if not DEBUG and SECRET_KEY == "django-insecure-placeholder-secret-key-change-me":
    raise RuntimeError("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false.")

DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://127.0.0.1,http://127.0.0.1:8000,http://localhost,http://localhost:8000",
    ).split(",")
    if origin.strip()
]

# ---------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps propias
    'paasify.apps.PaasifysConfig',
    'security.apps.SecurityConfig',
    'containers',

    # Terceros
    'colorfield',
    'rest_framework',
    'rest_framework_simplejwt',
    # 'rest_framework.authtoken',  # DESHABILITADO: Ahora usamos ExpiringToken (paasify.models.TokenModel)
    'drf_spectacular',
    'channels',
]

# ---------------------------------------------------------------------
# Middleware (añadimos WhiteNoise para estáticos en prod)
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <— IMPORTANTE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'paasify.middleware.TokenAuthMiddleware',  # <— Token JWT para API
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------------------------------------------------
# ASGI / WSGI
# ---------------------------------------------------------------------
ASGI_APPLICATION = "app_passify.asgi.application"
WSGI_APPLICATION = 'app_passify.wsgi.application'

# ---------------------------------------------------------------------
# URLs / Templates
# ---------------------------------------------------------------------
ROOT_URLCONF = 'app_passify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'paasify.context_processors.role_flags',
                'paasify.context_processors.global_settings',
            ],
        },
    },
]

# ---------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------
# Password validators
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------
# I18N / TZ
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Configuración de URL Base (para API y Documentación)
# ---------------------------------------------------------------------
# Permite fijar el dominio/IP de la plataforma (ej: https://passify-urjc.es)
# Si se deja vacío, se detectará dinámicamente desde la petición.
PAASIFY_BASE_URL = os.environ.get("PAASIFY_BASE_URL", "").rstrip("/")


# ---------------------------------------------------------------------
# Archivos estáticos (CSS/JS/Imágenes)
# ---------------------------------------------------------------------
# URL pública
STATIC_URL = '/static/'

# Carpeta real donde tienes "assets" (paasify/static/assets/…)
STATICFILES_DIRS = [
    BASE_DIR / "paasify" / "static",
]

# Carpeta a la que colecta en despliegue
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: compresión y versionado (recomendado)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True  # útil en dev para localizar estáticos dentro de apps

# Silenciar warnings de archivos estáticos duplicados (no afectan funcionalidad)
SILENCED_SYSTEM_CHECKS = ['staticfiles.W004']

# ---------------------------------------------------------------------
# Archivos de usuario (media)
# ---------------------------------------------------------------------
MEDIA_URL = os.environ.get("DJANGO_MEDIA_URL", "/media/")
_default_media_root = BASE_DIR / "media"
MEDIA_ROOT = Path(os.environ.get("DJANGO_MEDIA_ROOT", _default_media_root))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------
# DRF / JWT / Schema
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',  # DESHABILITADO: Usamos middleware personalizado
    ),
}

# ---------------------------------------------------------------------
# Redirecciones tras login/logout
# ---------------------------------------------------------------------
LOGIN_URL = '/paasify/login/'
LOGIN_REDIRECT_URL = '/post-login/'
LOGOUT_REDIRECT_URL = '/paasify/login/'

# ---------------------------------------------------------------------
# Jazzmin (si lo usas)
# ---------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "welcome_sign": "Bienvenido"
}
