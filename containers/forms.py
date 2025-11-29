from django import forms

from .models import AllowedImage


class AllowedImageForm(forms.ModelForm):
    suggested_tags = forms.ChoiceField(
        choices=[('', '--- Selecciona un tag para actualizar el campo Tag ---')],
        required=False,
        label='Tags disponibles en DockerHub',
        help_text='Selecciona un tag de la lista para actualizar automáticamente el campo Tag',
        widget=forms.Select(attrs={
            'id': 'id_suggested_tags',
            'style': 'width: 100%; max-width: 400px;',
            'onchange': 'document.getElementById("id_tag").value = this.value; if(this.value) { this.style.background = "#e8f5e9"; } else { this.style.background = ""; }'
        })
    )
    
    image_type = forms.ChoiceField(
        choices=AllowedImage.IMAGE_TYPES,
        required=True,
        label='Tipo de imagen',
        widget=forms.RadioSelect,
        help_text=(
            '<div style="margin-top: 10px; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">'
            '<h4 style="margin-top: 0; color: #007bff;">Funcionalidades a nivel de Servicio</h4>'
            '<p style="margin-bottom: 15px;">Selecciona el tipo de imagen según las funcionalidades que necesitarás cuando un usuario cree un servicio con esta imagen:</p>'
            
            '<div style="margin-bottom: 12px; padding: 10px; background: white; border-radius: 4px;">'
            '<strong style="color: #17a2b8;">🌐 Web / Frontend:</strong><br>'
            '<span style="color: #666;">Editor HTML/CSS/JS integrado en el servicio. Ideal para: nginx, apache, httpd.</span>'
            '</div>'
            
            '<div style="margin-bottom: 12px; padding: 10px; background: white; border-radius: 4px;">'
            '<strong style="color: #28a745;">🗄️ Base de Datos:</strong><br>'
            '<span style="color: #666;">Configuración de credenciales (usuario/contraseña) al crear el servicio. Ideal para: mysql, postgres, mongodb, redis.</span>'
            '</div>'
            
            '<div style="margin-bottom: 12px; padding: 10px; background: white; border-radius: 4px;">'
            '<strong style="color: #fd7e14;">🚀 Generador de API:</strong><br>'
            '<span style="color: #666;">Generación rápida de APIs con configuración simplificada. Ideal para: strapi, hasura, postgrest, json-server.</span>'
            '</div>'
            
            '<div style="margin-bottom: 0; padding: 10px; background: white; border-radius: 4px;">'
            '<strong style="color: #6c757d;">📦 Miscelánea:</strong><br>'
            '<span style="color: #666;">Sin funcionalidades especiales. Para imágenes genéricas o especializadas.</span>'
            '</div>'
            '</div>'
        )
    )

    class Meta:
        model = AllowedImage
        fields = '__all__'
        help_texts = {
            'name': 'Nombre de la imagen Docker (ej: nginx, mysql, bitnami/wordpress)',
            'tag': 'Tag de la imagen (ej: latest, 8.0, 1.2.3)',
            'description': 'Descripción breve de la imagen y su propósito',
        }
