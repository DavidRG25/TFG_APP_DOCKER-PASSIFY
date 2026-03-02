# 🔮 MEJORA FUTURA - Soporte para Imágenes Privadas de DockerHub

**Fecha de documentación:** 01/02/2026  
**Prioridad:** BAJA (No primordial)  
**Estado:** PENDIENTE  
**Tipo:** Feature Enhancement

---

## 📋 DESCRIPCIÓN

Actualmente, PaaSify permite a los usuarios desplegar servicios usando imágenes de DockerHub, pero **solo imágenes públicas**. Esta mejora permitiría usar **imágenes privadas** almacenadas en repositorios privados de DockerHub.

---

## 🎯 OBJETIVO

Permitir que los usuarios puedan:

1. Configurar sus credenciales de DockerHub (usuario + token)
2. Desplegar servicios usando sus imágenes privadas
3. Gestionar múltiples cuentas de DockerHub si es necesario

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### **1. Backend - Modelo de Credenciales**

```python
# containers/models.py
from cryptography.fernet import Fernet
from django.conf import settings

class DockerHubCredentials(models.Model):
    """Almacena credenciales de DockerHub por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    encrypted_token = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    last_validated = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_token(self, token):
        """Encripta y guarda el token"""
        cipher = Fernet(settings.DOCKERHUB_ENCRYPTION_KEY)
        self.encrypted_token = cipher.encrypt(token.encode()).decode()

    def get_token(self):
        """Desencripta y devuelve el token"""
        cipher = Fernet(settings.DOCKERHUB_ENCRYPTION_KEY)
        return cipher.decrypt(self.encrypted_token.encode()).decode()

    def validate_credentials(self):
        """Valida que las credenciales funcionen"""
        import docker
        try:
            client = docker.from_env()
            client.login(
                username=self.username,
                password=self.get_token(),
                registry='https://index.docker.io/v1/'
            )
            self.last_validated = timezone.now()
            self.is_active = True
            self.save()
            return True
        except Exception as e:
            self.is_active = False
            self.save()
            return False
```

---

### **2. Backend - Vista para Gestionar Credenciales**

```python
# containers/views.py
@login_required
def dockerhub_credentials(request):
    """Página para gestionar credenciales de DockerHub"""
    credentials, created = DockerHubCredentials.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        username = request.POST.get('username')
        token = request.POST.get('token')

        credentials.username = username
        credentials.set_token(token)

        # Validar credenciales
        if credentials.validate_credentials():
            messages.success(request, '✅ Credenciales guardadas y validadas correctamente')
        else:
            messages.error(request, '❌ Error: Credenciales inválidas')

        return redirect('containers:dockerhub_credentials')

    return render(request, 'containers/dockerhub_credentials.html', {
        'credentials': credentials,
        'has_credentials': credentials.username is not None
    })
```

---

### **3. Backend - Modificar Creación de Servicios**

```python
# containers/services.py
def pull_docker_image(image_name, user):
    """Pull de imagen, soporta privadas si el usuario tiene credenciales"""
    client = docker.from_env()

    # Intentar pull sin autenticación (imagen pública)
    try:
        client.images.pull(image_name)
        return True
    except docker.errors.APIError:
        # Si falla, intentar con credenciales del usuario
        try:
            credentials = DockerHubCredentials.objects.get(user=user, is_active=True)
            client.login(
                username=credentials.username,
                password=credentials.get_token(),
                registry='https://index.docker.io/v1/'
            )
            client.images.pull(image_name)
            return True
        except DockerHubCredentials.DoesNotExist:
            raise Exception("Imagen privada detectada. Configura tus credenciales de DockerHub.")
        except Exception as e:
            raise Exception(f"Error al hacer pull de la imagen: {str(e)}")
```

---

### **4. Frontend - Página de Configuración**

```html
<!-- templates/containers/dockerhub_credentials.html -->
{% extends 'base.html' %} {% block content %}
<div class="container mt-4">
  <div class="row justify-content-center">
    <div class="col-md-8">
      <div class="card shadow-sm">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">
            <i class="fab fa-docker me-2"></i>Credenciales de DockerHub
          </h4>
        </div>
        <div class="card-body">
          {% if has_credentials %}
          <div class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            Credenciales configuradas para:
            <strong>{{ credentials.username }}</strong>
            <br />
            <small
              >Última validación: {{ credentials.last_validated|date:"d/m/Y H:i"
              }}</small
            >
          </div>
          {% else %}
          <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            No tienes credenciales configuradas. Añádelas para usar imágenes
            privadas.
          </div>
          {% endif %}

          <form method="POST">
            {% csrf_token %}
            <div class="mb-3">
              <label for="username" class="form-label fw-semibold">
                Usuario de DockerHub <span class="text-danger">*</span>
              </label>
              <input
                type="text"
                class="form-control"
                id="username"
                name="username"
                value="{{ credentials.username }}"
                placeholder="tu-usuario"
                required
              />
            </div>

            <div class="mb-3">
              <label for="token" class="form-label fw-semibold">
                Personal Access Token <span class="text-danger">*</span>
              </label>
              <input
                type="password"
                class="form-control"
                id="token"
                name="token"
                placeholder="dckr_pat_xxxxxxxxxxxxx"
                required
              />
              <small class="text-muted">
                Genera un token en:
                <a
                  href="https://hub.docker.com/settings/security"
                  target="_blank"
                >
                  DockerHub → Account Settings → Security
                </a>
              </small>
            </div>

            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary">
                <i class="fas fa-save me-2"></i>Guardar Credenciales
              </button>
              <a
                href="{% url 'containers:student_panel' %}"
                class="btn btn-outline-secondary"
              >
                <i class="fas fa-arrow-left me-2"></i>Volver
              </a>
            </div>
          </form>
        </div>
      </div>

      <div class="card shadow-sm mt-4">
        <div class="card-header bg-info text-white">
          <h5 class="mb-0">
            <i class="fas fa-question-circle me-2"></i>¿Cómo obtener un Personal
            Access Token?
          </h5>
        </div>
        <div class="card-body">
          <ol>
            <li>
              Ve a
              <a href="https://hub.docker.com/settings/security" target="_blank"
                >DockerHub Security Settings</a
              >
            </li>
            <li>Haz clic en "New Access Token"</li>
            <li>Dale un nombre descriptivo (ej: "PaaSify")</li>
            <li>Selecciona permisos: <strong>Read, Write, Delete</strong></li>
            <li>Copia el token generado y pégalo aquí</li>
          </ol>
          <div class="alert alert-warning mb-0">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Importante:</strong> Guarda el token en un lugar seguro. No
            podrás verlo de nuevo.
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

### **5. Seguridad - Configuración**

```python
# settings.py
import os
from cryptography.fernet import Fernet

# Generar clave de encriptación (una sola vez, guardar en .env)
# DOCKERHUB_ENCRYPTION_KEY = Fernet.generate_key().decode()

DOCKERHUB_ENCRYPTION_KEY = os.getenv('DOCKERHUB_ENCRYPTION_KEY', Fernet.generate_key().decode())
```

---

## 📊 BENEFICIOS

✅ **Mayor flexibilidad:** Usuarios pueden usar sus propias imágenes privadas  
✅ **Seguridad:** Tokens encriptados en base de datos  
✅ **Validación:** Sistema verifica que las credenciales funcionen  
✅ **UX mejorada:** Interfaz clara para gestionar credenciales

---

## ⚠️ CONSIDERACIONES

❌ **Complejidad adicional:** Requiere gestión de credenciales y encriptación  
❌ **Seguridad:** Almacenar tokens requiere medidas de seguridad robustas  
❌ **Mantenimiento:** Los tokens pueden expirar y necesitan renovación

---

## 🗓️ ESTIMACIÓN DE DESARROLLO

- **Backend (modelos + vistas):** 4-6 horas
- **Frontend (interfaz):** 2-3 horas
- **Testing:** 2-3 horas
- **Documentación:** 1-2 horas

**Total estimado:** 9-14 horas

---

## 📝 NOTAS ADICIONALES

- Esta funcionalidad NO es primordial para el funcionamiento básico de PaaSify
- Se puede implementar en una versión futura post-TFG
- Alternativa: Usar solo imágenes públicas (solución actual)
- Documentar en memoria del TFG como "Trabajo Futuro"

---

**Estado actual:** DOCUMENTADO COMO MEJORA FUTURA  
**Prioridad:** BAJA  
**Fecha:** 01/02/2026
