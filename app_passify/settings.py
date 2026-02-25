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
    # Jazzmin Admin UI
    'jazzmin',

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
    # 'rest_framework.authtoken',  # DESHABILITADO: Ahora usamos ExpiringToken (paasify.models.TokenModel)
    'drf_spectacular',
    'channels',
]

# ---------------------------------------------------------------------
# Middleware (aÃ±adimos WhiteNoise para estÃ¡ticos en prod)
# ---------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <â€” IMPORTANTE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'paasify.middleware.TokenAuthMiddleware',  # <â€” Token JWT para API
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'paasify.middleware.must_change_password.ForcePasswordChangeMiddleware',
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
# Configuración de Base de Datos Híbrida (SQLite / PostgreSQL)
DB_NAME = os.environ.get('DB_NAME')
if DB_NAME:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,  # Aumentamos el timeout para evitar bloqueos en SQLite
            }
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
# ConfiguraciÃ³n de URL Base (para API y DocumentaciÃ³n)
# ---------------------------------------------------------------------
# Permite fijar el dominio/IP de la plataforma (ej: https://passify-urjc.es)
# Si se deja vacÃ­o, se detectarÃ¡ dinÃ¡micamente desde la peticiÃ³n.
PAASIFY_BASE_URL = os.environ.get("PAASIFY_BASE_URL", "").rstrip("/")


# ---------------------------------------------------------------------
# Archivos estÃ¡ticos (CSS/JS/ImÃ¡genes)
# ---------------------------------------------------------------------
# URL pÃºblica
STATIC_URL = '/static/'

# Carpeta real donde tienes "assets" (paasify/static/assets/â€¦)
STATICFILES_DIRS = [
    BASE_DIR / "paasify" / "static",
]

# Carpeta a la que colecta en despliegue
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: compresiÃ³n y versionado (recomendado)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True  # Ãºtil en dev para localizar estÃ¡ticos dentro de apps

# Silenciar warnings de archivos estÃ¡ticos duplicados (no afectan funcionalidad)
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
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}

# ---------------------------------------------------------------------
# Redirecciones tras login/logout
# ---------------------------------------------------------------------
LOGIN_URL = '/paasify/login/'
LOGIN_REDIRECT_URL = '/post-login/'
LOGOUT_REDIRECT_URL = '/paasify/login/'

# ---------------------------------------------------------------------
# Jazzmin (Django Admin Premium UI)
# ---------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "PaaSify Admin",
    "site_header": "PaaSify Administrador",
    "site_brand": "☁️ PaaSify Admin",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-fluid",
    "site_icon": None,
    "welcome_sign": "Centro de Control PaaSify",
    "copyright": "PaaSify Education Platform",
    "search_model": ["auth.User", "paasify.Subject", "containers.Service"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Volver a PaaSify", "url": "index", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "paasify", "containers"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "paasify.Subject": "fas fa-book",
        "paasify.UserProfile": "fas fa-id-card",
        "paasify.TeacherProfile": "fas fa-chalkboard-teacher",
        "paasify.TokenModel": "fas fa-key",
        "paasify.UserProject": "fas fa-folder-open",
        "containers.Service": "fas fa-server",
        "containers.AllowedImage": "fas fa-box-open",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

# Configuración extendida de Jazzmin: activar autocompletado en filtros sin botón "Buscar"
JAZZMIN_SETTINGS["show_ui_builder"] = False
JAZZMIN_SETTINGS["changeform_format"] = "single"
JAZZMIN_SETTINGS["hide_apps"] = []
JAZZMIN_SETTINGS["hide_models"] = []

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-white",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "lumen",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

APPEND_SLASH=False