"""
app_passify URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from containers.views import ServiceViewSet, AllowedImageViewSet
from containers import views as container_views
from paasify.views import ProfileView

# Django REST framework & JWT
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Router de la API REST
router = routers.DefaultRouter()
router.register(r'containers', ServiceViewSet, basename='service')
router.register(r'images', AllowedImageViewSet, basename='allowed-image')

urlpatterns = [
    # Vistas públicas / HTML
    path('', RedirectView.as_view(url='/paasify/login/', permanent=False), name='index'),
    path('paasify/', include('paasify.urls', namespace='paasify')),

    # Auth
    path('accounts/', include('django.contrib.auth.urls')),

    # App "containers" con namespace único
    path('paasify/containers/', include('containers.urls', namespace='containers')),

    # Roles (en raíz para compatibilidad con LOGIN_REDIRECT_URL)
    path('post-login/', container_views.post_login, name='post_login'),
    path('professor/',  container_views.professor_dashboard, name='professor_dashboard'),
    path('professor/subjects/<int:subject_id>/', container_views.professor_subject_detail, name='professor_subject_detail'),
    path('professor/projects/<int:project_id>/', container_views.professor_project_detail, name='professor_project_detail'),

    # Perfil de usuario
    path('profile/', ProfileView.profile_view, name='profile'),
    path('profile/change-password/', ProfileView.change_password_view, name='change_password'),
    path('profile/generate-token/', ProfileView.generate_token_view, name='generate_token'),
    path('profile/refresh-token/', ProfileView.refresh_token_view, name='refresh_token'),
    path('profile/copy-token/', ProfileView.copy_token_view, name='copy_token'),

    # Admin
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include(router.urls)),
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),
    path('api/schema/',  SpectacularAPIView.as_view(),        name='schema'),
    path('api/docs/',    SpectacularSwaggerView.as_view(url_name='schema')),
]

# Servir estáticos en desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_url = None
admin.site.site_header = "PaaSify Administration"
admin.site.site_title = "PaaSify Admin"
