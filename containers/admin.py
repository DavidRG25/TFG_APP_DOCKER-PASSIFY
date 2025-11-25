import requests
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from docker.errors import APIError

from .docker_client import get_docker_client
from .forms import AllowedImageForm
from .models import AllowedImage, Service


# Acción: Probar imagen (pull & run) y MOSTRAR LOG en una página
@admin.action(description="Probar imagen (pull & run) y mostrar log")
def probar_imagen_con_log(modeladmin, request, queryset):
    local_client = get_docker_client()
    if local_client is None:
        messages.error(
            request,
            "No se pudo conectar con el daemon de Docker. Verifica que el servicio esté activo.",
        )
        context = {
            **modeladmin.admin_site.each_context(request),
            "results": [],
        }
        return TemplateResponse(request, "admin/allowedimage_test_logs.html", context)
    results = []

    for img in queryset:
        full = f"{img.name}:{img.tag}"
        log_lines = []
        status = "ok"
        error = None

        # 1) Pull
        try:
            log_lines.append(f"$ docker pull {full}")
            local_client.images.pull(img.name, tag=img.tag)
            log_lines.append("✔ Imagen descargada correctamente.")
        except Exception as e:
            status = "error"
            error = f"Error en pull: {e}"
            log_lines.append(error)

        # 2) Run de prueba (solo si el pull fue bien)
        if status == "ok":
            # Intento A: con sh -lc (para imágenes que tienen shell)
            try:
                if "mysql" in img.name:
                    cmd = "mysql --version"
                else:
                    cmd = "echo PASSED"
                log_lines.append(f"$ docker run --rm {full} sh -lc '{cmd}'")
                out = local_client.containers.run(
                    full, ["sh", "-lc", cmd], remove=True, detach=False
                )
                if isinstance(out, (bytes, bytearray)):
                    out = out.decode(errors="replace")
                log_lines.append(out.strip() or "(sin salida)")
            except Exception as e1:
                # Intento B: sin shell (fallback para alpine/distroless/windows, etc.)
                try:
                    log_lines.append(f"$ docker run --rm {full} echo PASSED")
                    out = local_client.containers.run(
                        full, ["echo", "PASSED"], remove=True, detach=False
                    )
                    if isinstance(out, (bytes, bytearray)):
                        out = out.decode(errors="replace")
                    log_lines.append(out.strip() or "(sin salida)")
                except Exception as e2:
                    status = "error"
                    error = f"Error al ejecutar contenedor: {e1} | fallback: {e2}"
                    log_lines.append(error)

        results.append({
            "image": full,
            "status": status,
            "log": log_lines,
            "error": error,
        })

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": "Resultado de prueba de imágenes",
        "results": results,
    }
    return TemplateResponse(request, "admin/allowedimage_test_logs.html", context)



# AllowedImage Admin
@admin.register(AllowedImage)
class AllowedImageAdmin(admin.ModelAdmin):
    form = AllowedImageForm
    
    # Lista mejorada con tipo e iconos
    list_display = ('name', 'tag', 'get_type_icon', 'image_type', 'description', 'created_at')
    search_fields = ('name', 'tag', 'description')
    list_filter = ('image_type', 'created_at')
    
    # Incluimos ambas acciones: la tuya (solo pull) y la nueva (con log)
    actions = [probar_imagen_con_log, 'probar_imagen']
    
    def get_type_icon(self, obj):
        """Muestra icono según el tipo de imagen"""
        icons = {
            'web': '🌐',
            'database': '🗄️',
            'api': '🚀',
            'misc': '📦',
        }
        return icons.get(obj.image_type, '📦')
    get_type_icon.short_description = 'Icono'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.name:
            tags = self._get_docker_hub_tags(obj.name)
            form.base_fields['suggested_tags'].initial = "\\n".join(tags)
        return form

    def _get_docker_hub_tags(self, name):
        """
        Consulta DockerHub para obtener tags disponibles.
        Soporta imágenes oficiales (library/) y de usuarios.
        """
        # Intentar primero como imagen oficial
        url = f"https://hub.docker.com/v2/repositories/library/{name}/tags/"
        try:
            response = requests.get(url, params={'page_size': 50}, timeout=5)
        except requests.RequestException:
            return []
        
        if response.status_code != 200:
            # Intentar como imagen de usuario (ej: bitnami/nginx)
            if '/' in name:
                url = f"https://hub.docker.com/v2/repositories/{name}/tags/"
                try:
                    response = requests.get(url, params={'page_size': 50}, timeout=5)
                except requests.RequestException:
                    return []
        
        if response.status_code != 200:
            return []
        
        results = response.json().get('results', [])
        tags = [r['name'] for r in results]
        
        # Ordenar: latest primero, luego numéricos, luego alfabéticos
        def sort_key(tag):
            if tag == 'latest':
                return (0, tag)
            elif tag.replace('.', '').replace('-', '').isdigit():
                return (1, tag)
            else:
                return (2, tag)
        
        return sorted(tags, key=sort_key)[:50]  # Limitar a 50 tags

    def save_model(self, request, obj, form, change):
        name = form.cleaned_data.get('name')
        tag = form.cleaned_data.get('tag')
        url = f"https://hub.docker.com/v2/repositories/library/{name}/tags/{tag}"
        
        try:
            response = requests.get(url, timeout=5)
        except requests.RequestException:
            messages.error(request, f"No se pudo verificar la imagen '{name}:{tag}' en Docker Hub.")
            return
        
        if response.status_code != 200:
            # Intentar como imagen de usuario
            if '/' in name:
                url = f"https://hub.docker.com/v2/repositories/{name}/tags/{tag}"
                try:
                    response = requests.get(url, timeout=5)
                except requests.RequestException:
                    messages.error(request, f"No se pudo verificar la imagen '{name}:{tag}' en Docker Hub.")
                    return
                
                if response.status_code != 200:
                    messages.error(request, f"La imagen '{name}:{tag}' no existe en Docker Hub.")
                    return
            else:
                messages.error(request, f"La imagen '{name}:{tag}' no existe en Docker Hub.")
                return
        
        super().save_model(request, obj, form, change)
        
        # Mensaje informativo sobre funcionalidades futuras según tipo
        type_messages = {
            'web': '🌐 Imagen Web guardada. Funcionalidad a nivel de servicio: Editor HTML/CSS/JS integrado.',
            'database': '🗄️ Base de Datos guardada. Funcionalidad a nivel de servicio: Configuración de credenciales.',
            'api': '🚀 Generador de API guardado. Funcionalidad a nivel de servicio: Generación rápida de APIs.',
            'misc': '📦 Imagen guardada correctamente.',
        }
        messages.info(request, type_messages.get(obj.image_type, 'Imagen guardada correctamente.'))

    def probar_imagen(self, request, queryset):
        """
        Acción original: SOLO pull + mensajes en la parte superior del admin.
        """
        docker_client = get_docker_client()
        if docker_client is None:
            self.message_user(
                request,
                "Docker no está disponible. Inicia el daemon antes de ejecutar la acción.",
                level=messages.ERROR,
            )
            return

        for img in queryset:
            image_full = f"{img.name}:{img.tag}"
            try:
                docker_client.images.pull(img.name, tag=img.tag)
                messages.success(request, f"Imagen {image_full} cargada correctamente.")
            except APIError as e:
                messages.error(request, f"Error al cargar {image_full}: {e}")
    probar_imagen.short_description = "Probar (solo pull) imagen seleccionada"



# Service Admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'image',
        'assigned_port',
        'status',
        'created_at',
    )
    search_fields = ('name', 'owner__username', 'image')
    list_filter = ('status', 'created_at')
    readonly_fields = ('logs', 'container_id', 'created_at', 'updated_at')
