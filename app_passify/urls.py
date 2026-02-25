"""
app_passify URL Configuration
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.conf.urls.static import static

from containers.views import ServiceViewSet, AllowedImageViewSet, SubjectViewSet, ProjectViewSet
from containers import views as container_views
from paasify.views import ProfileView
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_admin_logout(request):
    """Solución para Django 5.1 donde no se permite GET en logout.
    Especialmente necesario porque django-jazzmin envía un simple GET en el enlace Navbar"""
    if request.user.is_authenticated:
        logout(request)
    return redirect('paasify:login')


from django.conf.urls import handler404, handler500, handler403

handler404 = 'paasify.views.ErrorViews.handler404'
handler500 = 'paasify.views.ErrorViews.handler500'
handler403 = 'paasify.views.ErrorViews.handler403'

# Django REST framework
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Router de la API REST
router = routers.DefaultRouter()
router.register(r'containers', ServiceViewSet, basename='service')
router.register(r'images', AllowedImageViewSet, basename='allowed-image')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    # Vistas públicas / HTML
    path('', RedirectView.as_view(url='/paasify/', permanent=False), name='index'),
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
    path('profile/update/', ProfileView.update_profile_view, name='update_profile'),
    path('profile/change-password/', ProfileView.change_password_view, name='change_password'),
    path('profile/generate-token/', ProfileView.generate_token_view, name='generate_token'),
    path('profile/refresh-token/', ProfileView.refresh_token_view, name='refresh_token'),
    path('profile/copy-token/', ProfileView.copy_token_view, name='copy_token'),

    # Admin Logout workaround para Django 5.1 (GET no permitido por defecto)
    path('admin/logout/', custom_admin_logout, name='custom_admin_logout'),
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include(router.urls)),
    
    # Silenciar peticiones de navegador (Chrome DevTools / SourceMaps)
    path('.well-known/appspecific/com.chrome.devtools.json', lambda r: HttpResponse(status=204)),
    path('static/assets/bootstrap/js/bootstrap.bundle.min.js.map', lambda r: HttpResponse(status=204)),
    
    # Docs restringidas a STAFF (Admin)
    path('api/schema/',  staff_member_required(SpectacularAPIView.as_view()),        name='schema'),
    path('api/docs/',    staff_member_required(SpectacularSwaggerView.as_view(url_name='schema')), name='docs'),

]

# Servir estáticos y media en desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_url = None
admin.site.site_header = "PaaSify Administration"
admin.site.site_title = "PaaSify Admin"
