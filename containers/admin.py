import requests
from django import forms
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from docker.errors import APIError

from .docker_client import get_docker_client
from .forms import AllowedImageForm
from .models import AllowedImage, Service
from paasify.models.ProjectModel import UserProject


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
    
    # Fieldsets con diseño similar a Service
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'tag', 'description')
        }),
        ('Clasificación', {
            'fields': ('image_type',),
            'description': 'Selecciona el tipo de imagen según las funcionalidades que necesitarás'
        }),
        ('Tags Disponibles en DockerHub', {
            'fields': ('suggested_tags',),
            'description': 'Selecciona un tag de la lista para actualizar automáticamente el campo Tag'
        }),
        ('Información del Sistema', {
            'fields': ('id', 'created_at', 'get_services_count'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'get_services_count')
    
    
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
    
    def get_services_count(self, obj):
        """Muestra cuántos servicios usan esta imagen"""
        if not obj.pk:
            return "-"
        
        from .models import Service
        image_full = f"{obj.name}:{obj.tag}"
        count = Service.objects.filter(image=image_full).count()
        
        if count == 0:
            return "No hay servicios usando esta imagen"
        
        return f"📊 {count} servicio{'s' if count != 1 else ''} usando esta imagen"
    get_services_count.short_description = 'Uso en servicios'
    
    def get_fieldsets(self, request, obj=None):
        """Muestra diferentes fieldsets según si es creación o edición"""
        # Fieldsets base (siempre visibles)
        base_fieldsets = [
            ('Información Básica', {
                'fields': ('name', 'tag', 'description')
            }),
            ('Clasificación', {
                'fields': ('image_type',),
                'description': 'Selecciona el tipo de imagen según las funcionalidades que necesitarás'
            }),
        ]
        
        # Si es edición (obj existe), agregar secciones adicionales
        if obj:
            base_fieldsets.append(
                ('Tags Disponibles en DockerHub', {
                    'fields': ('suggested_tags',),
                    'description': 'Selecciona un tag de la lista para actualizar automáticamente el campo Tag'
                })
            )
            base_fieldsets.append(
                ('Información del Sistema', {
                    'fields': ('id', 'created_at', 'get_services_count'),
                    'classes': ('collapse',),
                })
            )
        
        return base_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Solo procesar suggested_tags si estamos editando una imagen existente
        if obj and obj.name:
            # Imagen existente: mostrar selector de tags
            tags = self._get_docker_hub_tags(obj.name)
            if tags:
                # Poblar choices del select con los tags disponibles
                choices = [('', '--- Selecciona un tag para actualizar el campo Tag ---')]
                choices.extend([(tag, tag) for tag in tags])
                
                # Asegurarse de que el campo existe antes de modificarlo
                if 'suggested_tags' in form.base_fields:
                    form.base_fields['suggested_tags'].choices = choices
                    
                    # Pre-seleccionar el tag actual si existe en la lista
                    if obj.tag in tags:
                        form.base_fields['suggested_tags'].initial = obj.tag
            else:
                # Si no hay tags disponibles, mostrar mensaje informativo
                if 'suggested_tags' in form.base_fields:
                    form.base_fields['suggested_tags'].widget = forms.TextInput(attrs={
                        'readonly': 'readonly',
                        'value': 'No se encontraron tags en DockerHub para esta imagen',
                        'style': 'width: 100%; max-width: 400px; background: #fff3cd; border-color: #ffc107;'
                    })
                    form.base_fields['suggested_tags'].help_text = 'Verifica que el nombre de la imagen sea correcto'
        else:
            # Imagen nueva: ocultar el campo suggested_tags completamente
            if 'suggested_tags' in form.base_fields:
                form.base_fields['suggested_tags'].widget = forms.HiddenInput()
                form.base_fields['suggested_tags'].label = ''
                form.base_fields['suggested_tags'].help_text = ''
        
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
        'get_project_name',    # Nuevo: Proyecto
        'owner',
        'image',
        'get_image_type',      # Nuevo
        'assigned_port',
        'status',
        'get_volume_info',     # Nuevo
        'created_at',
    )
    search_fields = ('name', 'owner__username', 'image', 'project__place')
    list_filter = ('status', 'created_at')
    readonly_fields = (
        'logs',
        'container_id',
        'created_at',
        'updated_at',
        'get_image_display',    # Nuevo
        'get_port_info',        # Nuevo
        'get_volume_details',   # Nuevo
        'get_image_options',    # Nuevo
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'owner', 'project', 'get_image_display', 'image', 'subject')
        }),
        ('Configuración de Red', {
            'fields': ('assigned_port', 'internal_port', 'get_port_info'),
            'description': 'Configuración de puertos y acceso al servicio'
        }),
        ('Configuración Avanzada', {
            'fields': ('env_vars', 'volumes', 'get_volume_details'),
            'classes': ('collapse',),
        }),
        ('Archivos de Configuración', {
            'fields': ('dockerfile', 'compose', 'code'),
            'classes': ('collapse',),
        }),
        ('Estado y Logs', {
            'fields': ('status', 'container_id', 'logs'),
        }),
        ('Opciones de Imagen', {
            'fields': ('get_image_options',),
            'description': 'Funcionalidades disponibles según el tipo de imagen'
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Personalizar widgets de campos"""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        
        # Reducir tamaño de textareas para env_vars y volumes
        if db_field.name in ['env_vars', 'volumes']:
            formfield.widget.attrs['rows'] = 3
            formfield.widget.attrs['style'] = 'font-family: monospace; width: 100%; max-width: 600px;'
        
        return formfield
    
    def get_image_type(self, obj):
        """Muestra el tipo de imagen con icono"""
        # Detectar si es servicio personalizado
        if obj.dockerfile:
            return "📦 Personalizado (Dockerfile)"
        
        if obj.compose:
            return "🐳 Personalizado (Compose)"
        
        # Servicio con imagen del catálogo
        try:
            image_name = obj.image.split(':')[0] if obj.image else ''
            image_tag = obj.image.split(':')[1] if ':' in (obj.image or '') else 'latest'
            
            allowed = AllowedImage.objects.get(name=image_name, tag=image_tag)
            icons = {
                'web': '🌐',
                'database': '🗄️',
                'api': '🚀',
                'misc': '📦',
            }
            icon = icons.get(allowed.image_type, '📦')
            return f"{icon} {allowed.get_image_type_display()}"
        except AllowedImage.DoesNotExist:
            return "❓ Desconocido"
    get_image_type.short_description = 'Tipo'

    def get_project_name(self, obj):
        """Muestra el nombre del proyecto asociado"""
        if obj.project:
            return obj.project.place
        return "-"
    get_project_name.short_description = "Proyecto"
    get_project_name.admin_order_field = 'project__place'
    
    def get_image_display(self, obj):
        """Muestra el tipo de imagen de forma clara en Información Básica"""
        from django.utils.html import format_html
        
        # Detectar si es servicio personalizado con Dockerfile
        if obj.dockerfile:
            return format_html(
                '<span style="background: #f3e5f5; padding: 5px 10px; border-radius: 4px; color: #4a148c; font-weight: bold;">'
                '📦 Imagen Personalizada (Dockerfile)'
                '</span>'
            )
        
        # Detectar si es servicio personalizado con docker-compose
        if obj.compose:
            return format_html(
                '<span style="background: #e1f5fe; padding: 5px 10px; border-radius: 4px; color: #01579b; font-weight: bold;">'
                '🐳 Imagen Personalizada (Compose)'
                '</span>'
            )
        
        # Servicio con imagen del catálogo
        if obj.image:
            return format_html(
                '<span style="background: #e8f5e9; padding: 5px 10px; border-radius: 4px; color: #2e7d32; font-weight: bold;">'
                '📚 Imagen del Catálogo'
                '</span>'
            )
        
        return format_html(
            '<span style="color: #999;">No especificada</span>'
        )
    get_image_display.short_description = 'Tipo de Imagen'
    
    def get_volume_info(self, obj):
        """Muestra información resumida de volúmenes"""
        count = 0
        
        # Contar volumen automático
        if obj.volume_name:
            count += 1
        
        # Contar volúmenes adicionales del usuario
        if obj.volumes:
            try:
                import json
                volumes = json.loads(obj.volumes) if isinstance(obj.volumes, str) else obj.volumes
                if isinstance(volumes, dict):
                    count += len(volumes)
            except:
                pass
        
        if count == 0:
            return "-"
        
        return f"📁 {count} volumen{'es' if count != 1 else ''}"
    get_volume_info.short_description = 'Volúmenes'
    
    def get_port_info(self, obj):
        """Muestra información detallada del puerto"""
        from django.utils.html import format_html
        
        if obj.assigned_port:
            return format_html(
                '<div style="background: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50;">'
                '<strong style="color: #2e7d32;">Puerto asignado:</strong> {}<br>'
                '<strong style="color: #2e7d32;">Puerto interno:</strong> {}<br>'
                '<strong style="color: #2e7d32;">URL de acceso:</strong> '
                '<a href="http://localhost:{}" target="_blank" style="color: #1976d2; text-decoration: none;">'
                'http://localhost:{}</a>'
                '</div>',
                obj.assigned_port,
                obj.internal_port or 80,
                obj.assigned_port,
                obj.assigned_port
            )
        return format_html('<span style="color: #999;">Puerto no asignado</span>')
    get_port_info.short_description = 'Información de Puerto'
    
    def get_volume_details(self, obj):
        """Muestra detalles de los volúmenes configurados"""
        from django.utils.html import format_html
        
        html_parts = []
        
        # Mostrar volumen automático
        if obj.volume_name:
            html_parts.append(
                f'<li><strong>Volumen automático:</strong> '
                f'<code style="background: #e8f5e9; padding: 2px 6px; border-radius: 3px;">{obj.volume_name}</code> → '
                f'<code style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px;">/data</code></li>'
            )
        
        # Mostrar volúmenes adicionales del usuario
        if obj.volumes:
            try:
                import json
                volumes = json.loads(obj.volumes) if isinstance(obj.volumes, str) else obj.volumes
                
                if isinstance(volumes, dict) and volumes:
                    for host_path, container_path in volumes.items():
                        html_parts.append(
                            f'<li><strong>Volumen adicional:</strong> '
                            f'<code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{host_path}</code> → '
                            f'<code style="background: #e3f2fd; padding: 2px 6px; border-radius: 3px;">{container_path}</code></li>'
                        )
            except:
                pass
        
        if not html_parts:
            return format_html('<span style="color: #999;">Sin volúmenes configurados</span>')
        
        html = '<ul style="margin: 0; padding-left: 20px;">' + ''.join(html_parts) + '</ul>'
        return format_html(html)
    get_volume_details.short_description = 'Detalles de Volúmenes'
    
    def get_image_options(self, obj):
        """Muestra opciones disponibles según el tipo de imagen (placeholder para futuras funcionalidades)"""
        from django.utils.html import format_html
        
        # Detectar si es servicio personalizado con Dockerfile
        if obj.dockerfile:
            return format_html(
                '<div style="background: #f3e5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #9c27b0;">'
                '<strong style="color: #4a148c;">📦 Servicio Personalizado (Dockerfile)</strong><br>'
                '<em style="color: #666;">Imagen construida a partir del Dockerfile subido por el alumno</em><br>'
                '<small style="color: #999;">Tag de imagen: <code>{}</code></small>'
                '</div>'.format(obj.image or 'No disponible')
            )
        
        # Detectar si es servicio personalizado con docker-compose
        if obj.compose:
            return format_html(
                '<div style="background: #e1f5fe; padding: 15px; border-radius: 5px; border-left: 4px solid #0288d1;">'
                '<strong style="color: #01579b;">🐳 Servicio Personalizado (Docker Compose)</strong><br>'
                '<em style="color: #666;">Configuración multi-contenedor definida por el alumno</em><br>'
                '<small style="color: #999;">Archivo compose subido por el usuario</small>'
                '</div>'
            )
        
        # Servicio con imagen del catálogo
        try:
            image_name = obj.image.split(':')[0] if obj.image else ''
            image_tag = obj.image.split(':')[1] if ':' in (obj.image or '') else 'latest'
            
            allowed = AllowedImage.objects.get(name=image_name, tag=image_tag)
            
            if allowed.image_type == 'web':
                return format_html(
                    '<div style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;">'
                    '<strong style="color: #e65100;">🌐 Imagen Web / Frontend</strong><br>'
                    '<em style="color: #666;">Funcionalidad futura: Editor HTML/CSS/JS integrado en el panel del alumno</em><br>'
                    '<small style="color: #999;">Permitirá editar archivos web directamente desde el navegador</small>'
                    '</div>'
                )
            elif allowed.image_type == 'database':
                return format_html(
                    '<div style="background: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50;">'
                    '<strong style="color: #1b5e20;">🗄️ Base de Datos</strong><br>'
                    '<em style="color: #666;">Funcionalidad futura: Configuración de credenciales en el panel del alumno</em><br>'
                    '<small style="color: #999;">Permitirá configurar usuario/contraseña al crear el servicio</small>'
                    '</div>'
                )
            elif allowed.image_type == 'api':
                return format_html(
                    '<div style="background: #f3e5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #9c27b0;">'
                    '<strong style="color: #4a148c;">🚀 Generador de API</strong><br>'
                    '<em style="color: #666;">Funcionalidad futura: Generación rápida de APIs en el panel del alumno</em><br>'
                    '<small style="color: #999;">Permitirá generar estructura base y configurar endpoints</small>'
                    '</div>'
                )
            else:
                return format_html(
                    '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid #9e9e9e;">'
                    '<strong style="color: #424242;">📦 Imagen Miscelánea</strong><br>'
                    '<em style="color: #666;">Sin funcionalidades especiales</em>'
                    '</div>'
                )
        except AllowedImage.DoesNotExist:
            return format_html(
                '<div style="background: #fafafa; padding: 15px; border-radius: 5px; border-left: 4px solid #bdbdbd;">'
                '<strong style="color: #616161;">❓ Imagen no catalogada</strong><br>'
                '<em style="color: #999;">Esta imagen no está en el catálogo de imágenes permitidas</em>'
                '</div>'
            )
    get_image_options.short_description = 'Opciones de Imagen'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and 'project' in form.base_fields:
            # Filtrar proyectos para mostrar solo los del dueño del servicio
            form.base_fields['project'].queryset = UserProject.objects.filter(user_profile__user=obj.owner)
        return form

