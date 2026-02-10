# Bug: Página API Token muestra JWT en lugar de DRF Token

**Fecha:** 18/01/2026  
**Severidad:** MEDIA  
**Estado:** ✅ **RESUELTO**  
**Descubierto en:** Testing de Seguridad Crítica (Test 1.2)  
**Resuelto en:** 18/01/2026 22:00  
**Tiempo de resolución:** ~2 horas

---

## 🐛 DESCRIPCIÓN DEL BUG

La página `/paasify/containers/api-token/` muestra el **JWT token** (`UserProfile.bearer_token`) en lugar del **DRF Token** (`rest_framework.authtoken.Token`).

### **Problema:**

- Los endpoints de API (`/api/containers/`) usan **DRF Token Authentication**
- La página de tokens muestra **JWT tokens** (que no funcionan con la API)
- Los usuarios no pueden obtener su DRF token desde la UI

---

## 📸 EVIDENCIA

**Token mostrado en UI:**

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImFsdW1ubyIsInByb2ZpbGVfaWQiOjEsImlhdCI6MTc2ODc2NzY3NiwiZXhwIjoxODAwMzAzNjc2fQ.tHIcQIKFb46db1WRHYEHD26DcM1rTbfn_SGrFpKXDJA
```

**Tipo:** JWT (largo, con puntos)

**Token esperado:**

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

**Tipo:** DRF Token (40 caracteres hexadecimales)

**Error al usar JWT token:**

```json
{ "detail": "Token invalido o expirado.", "code": "token_not_valid" }
```

---

## 🔍 CAUSA RAÍZ

**Archivo:** `containers/views.py`  
**Vista:** `manage_api_token` (líneas ~866-888)

La vista está usando:

```python
token = user_profile.bearer_token  # JWT token ❌
```

Debería usar:

```python
from rest_framework.authtoken.models import Token
token, created = Token.objects.get_or_create(user=request.user)
token = token.key  # DRF token ✅
```

---

## 🔧 SOLUCIÓN PROPUESTA

### **Modificar vista `manage_api_token`:**

```python
@login_required
def manage_api_token(request):
    """Gestión de tokens API para usuarios"""
    from rest_framework.authtoken.models import Token

    if request.method == 'POST':
        # Regenerar token DRF
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass

        token = Token.objects.create(user=request.user)
        messages.success(request, 'Token regenerado exitosamente')
        return redirect('containers:manage_api_token')

    # Obtener o crear token DRF
    token, created = Token.objects.get_or_create(user=request.user)

    return render(request, 'containers/api_token.html', {
        'token': token.key,  # DRF token de 40 caracteres
    })
```

### **Actualizar template `api_token.html`:**

El template ya está correcto, solo necesita recibir el token DRF en lugar del JWT.

---

## ✅ WORKAROUND TEMPORAL

Mientras se arregla el bug, los usuarios pueden:

1. Ir al admin: `/admin/authtoken/tokenproxy/`
2. Crear token manualmente para su usuario
3. Copiar el token de 40 caracteres
4. Usar ese token en la API

---

## 🧪 TESTING

**Test afectado:** Test 1.2 - API - Rechazar Campo Volumes

**Para validar el fix:**

1. Acceder a `/paasify/containers/api-token/`
2. Verificar que el token tiene 40 caracteres (no es JWT)
3. Copiar token
4. Usar en curl: `curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/containers/`
5. Debe funcionar (200 OK)

---

## 📊 IMPACTO

**Severidad:** MEDIA

- ❌ Los usuarios no pueden usar la API desde la UI
- ❌ Confusión sobre qué token usar
- ✅ Workaround disponible (admin)
- ✅ No afecta seguridad (solo UX)

**Usuarios afectados:** Todos los que quieran usar la API

---

## 🚀 PRIORIDAD

**MEDIA** - Arreglar después del testing de seguridad crítica

**Razón:**

- No es bloqueante para testing
- Hay workaround disponible
- Afecta UX pero no seguridad

---

## 📝 NOTAS

Este bug se descubrió durante el testing del Plan de Seguridad Crítica, específicamente al intentar ejecutar el Test 1.2 que requiere usar la API con tokens.

El bug existe porque en el Plan de Mejoras UI Servicios se implementaron DOS sistemas de tokens:

1. JWT tokens en `UserProfile.bearer_token`
2. DRF tokens en `rest_framework.authtoken`

La vista `manage_api_token` está usando el sistema incorrecto.

---

**Creado por:** Testing de Seguridad Crítica  
**Fecha:** 2026-01-18  
**Resuelto por:** Sistema de ExpiringToken con caducidad de 30 días

---

## ✅ SOLUCIÓN IMPLEMENTADA

**Fecha de resolución:** 18/01/2026 22:00

### **Decisión de diseño:**

En lugar de arreglar el bug usando DRF Token estándar, se implementó un **sistema mejorado** con tokens que expiran automáticamente.

### **Cambios realizados:**

#### **1. Nuevo modelo: ExpiringToken**

**Archivo:** `paasify/models/TokenModel.py`

```python
class ExpiringToken(models.Model):
    """Token de API con caducidad de 30 días"""
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        return super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def days_until_expiration(self):
        if self.is_expired():
            return 0
        delta = self.expires_at - timezone.now()
        return delta.days
```

#### **2. Admin personalizado**

**Archivo:** `paasify/admin.py` (líneas 1304-1369)

- Lista tokens con usuario, fecha creación y expiración
- Indicador visual de estado (✅ Activo / ❌ Expirado)
- Días restantes con colores (rojo ≤7, naranja ≤15, verde >15)

#### **3. Middleware actualizado**

**Archivo:** `paasify/middleware/TokenAuthMiddleware.py`

- Valida ExpiringToken en requests a `/api/`
- Verifica expiración automáticamente
- Mensaje claro si el token expiró

#### **4. Vista de perfil actualizada**

**Archivo:** `paasify/views/ProfileView.py`

- `refresh_token_view`: Usa ExpiringToken
- `profile_view`: Pasa datos de expiración al template

#### **5. Template mejorado**

**Archivo:** `templates/profile.html`

- Muestra fecha de creación y caducidad
- Días restantes con alerta verde/roja
- Título cambiado de "Bearer Token API" a "Token de API"

#### **6. Configuración**

**Archivo:** `app_passify/settings.py`

- Deshabilitado `rest_framework.authtoken` (comentado)
- Removido `TokenAuthentication` de DRF

---

### **Características del nuevo sistema:**

✅ **Token de 40 caracteres** (estándar industria)  
✅ **Caducidad automática** (30 días)  
✅ **Revocable** (desde admin o perfil)  
✅ **UI mejorada** (muestra fechas y días restantes)  
✅ **Seguro** (160 bits de entropía, `os.urandom`)  
✅ **Admin integrado** (gestión completa desde admin)

---

### **Resultado:**

- ✅ Test 1.2 completado exitosamente
- ✅ Token funciona en API
- ✅ Sistema más seguro que el original (caducidad)
- ✅ Mejor UX (información clara de expiración)

---

### **Archivos modificados:**

1. `paasify/models/TokenModel.py` (nuevo)
2. `paasify/admin.py` (añadido ExpiringTokenAdmin)
3. `paasify/middleware/TokenAuthMiddleware.py` (actualizado)
4. `paasify/views/ProfileView.py` (actualizado)
5. `templates/profile.html` (actualizado)
6. `app_passify/settings.py` (configuración)
7. `paasify/models/__init__.py` (import)

---

**Estado final:** ✅ **RESUELTO Y MEJORADO**
