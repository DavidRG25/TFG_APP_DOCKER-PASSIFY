from django.contrib import admin, messages
from django.template.response import TemplateResponse
from .models import AllowedImage, Service
import docker
from docker.errors import APIError

# Cliente global (usado por la acción "solo pull")
client = docker.from_env()


# Acción: Probar imagen (pull & run) y MOSTRAR LOG en una página
@admin.action(description="Probar imagen (pull & run) y mostrar log")
def probar_imagen_con_log(modeladmin, request, queryset):
    local_client = docker.from_env()
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
    list_display = ('name', 'tag', 'description')
    search_fields = ('name', 'tag', 'description')

    # Incluimos ambas acciones: la tuya (solo pull) y la nueva (con log)
    actions = [probar_imagen_con_log, 'probar_imagen']

    def probar_imagen(self, request, queryset):
        """
        Acción original: SOLO pull + mensajes en la parte superior del admin.
        """
        for img in queryset:
            image_full = f"{img.name}:{img.tag}"
            try:
                client.images.pull(img.name, tag=img.tag)
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
