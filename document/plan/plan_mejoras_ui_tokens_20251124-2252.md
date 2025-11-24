# Plan de Implementacion: Mejoras UI/UX y Sistema de Tokens API
### Fase 1: Sistema de Perfil de Usuario y Bearer Token

#### [MODIFY] [StudentModel.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/paasify/models/StudentModel.py)

**Cambios:**
- Agregar campo `api_token` (CharField, max_length=64, unique=True, null=True, blank=True)
- Agregar campo `token_created_at` (DateTimeField, null=True, blank=True)
- Agregar metodo `generate_token()` que crea UUID4 y guarda fecha
- Agregar metodo `refresh_token()` que regenera token
- Agregar metodo `get_masked_token()` que retorna ultimos 8 caracteres

**Justificacion:**
- UUID4 es suficientemente seguro para tokens de API
- Campo nullable permite migracion sin afectar datos existentes
- Metodos encapsulan logica de generacion/refresh

---

#### [NEW] [ProfileView.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/paasify/views/ProfileView.py)

**Contenido:**
- Vista `profile_view(request)` que renderiza perfil del usuario
- Vista `change_password_view(request)` que procesa cambio de contrasena
- Vista `generate_token_view(request)` que genera token inicial
- Vista `refresh_token_view(request)` que regenera token
- Decoradores `@login_required` en todas las vistas
- Validacion de permisos (solo el propio usuario puede ver su perfil)

**Justificacion:**
- Separacion de responsabilidades (perfil != navegacion)
- Reutilizable para alumnos y profesores
- Seguridad: solo el usuario puede modificar su perfil

---

#### [NEW] [profile.html](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/templates/profile.html)

**Estructura:**
```html
{% extends "base.html" %}
- Seccion: Datos personales (username, nombre, email) - readonly
- Seccion: Cambio de contrasena (form con old_password, new_password1, new_password2)
- Seccion: Bearer Token API
  - Mostrar token (completo o parcial segun decision)
  - Boton "Copiar token"
  - Boton "Refrescar token" con confirmacion
  - Fecha de creacion del token
  - Instrucciones de uso del token
- Seccion: Asignaturas (alumno) o Asignaturas impartidas (profesor)
```

**Justificacion:**
- Interfaz centralizada para gestion de perfil
- HTMX para refresh de token sin recargar pagina
- Instrucciones claras para uso del token

---

#### [MODIFY] [admin.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/paasify/admin.py)

**Cambios en UserProfileAdmin:**
- Agregar `api_token` a `readonly_fields`
- Agregar `token_created_at` a `readonly_fields`
- Agregar metodo `display_token(obj)` que muestra token parcial
- Agregar action `refresh_api_tokens` para seleccionados
- Agregar `display_token` y `token_created_at` a `list_display`

**Justificacion:**
- Administradores pueden ver y refrescar tokens
- Token no editable manualmente (solo via action)
- Visibilidad de cuando fue creado el token

---

#### [MODIFY] [urls.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/app_passify/urls.py)

**Cambios:**
- Agregar ruta `path('profile/', profile_view, name='profile')`
- Agregar ruta `path('profile/change-password/', change_password_view, name='change_password')`
- Agregar ruta `path('profile/generate-token/', generate_token_view, name='generate_token')`
- Agregar ruta `path('profile/refresh-token/', refresh_token_view, name='refresh_token')`

**Justificacion:**
- Rutas RESTful para operaciones de perfil
- Separacion de endpoints por funcionalidad

---

### Fase 2: Mejora de Landing Page

#### [MODIFY] [index.html](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/templates/index.html)

**Cambios:**
- Hero section con gradiente de fondo (linear-gradient azul → morado)
- Animaciones CSS (fade-in, slide-up) en carga
- Cards de features con efecto hover (transform: translateY, box-shadow)
- Seccion de roles con badges de colores diferenciados
- Footer con enlaces y version
- Responsive design mejorado (media queries)

**Justificacion:**
- Primera impresion profesional
- Engagement visual sin sacrificar rendimiento
- Accesibilidad (contraste, tamaños de fuente)

---

#### [NEW] [landing.css](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/staticfiles/css/landing.css)

**Contenido:**
- Variables CSS para colores (--primary, --secondary, --gradient)
- Animaciones @keyframes (fadeIn, slideUp)
- Clases de utilidad (.hero-gradient, .card-hover)
- Media queries para responsive

**Justificacion:**
- Separacion de estilos especificos de landing
- Reutilizable en otras paginas
- Mantenibilidad

---

### Fase 3: Mejora de Dashboards

#### [MODIFY] [student_panel.html](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/templates/student_panel.html)

**Cambios:**
- Agregar header con informacion del alumno (nombre, email)
- Agregar seccion "Mis asignaturas" con cards
- Agregar seccion "Mis proyectos" con estado
- Mejorar tabla de servicios (iconos de estado, colores)
- Agregar boton "Mi perfil" en navbar

**Justificacion:**
- Contexto inmediato del usuario
- Navegacion mas intuitiva
- Informacion relevante a primera vista

---

#### [MODIFY] [dashboard.html](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/templates/professor/dashboard.html)

**Cambios:**
- Agregar seccion de estadisticas (total asignaturas, total alumnos)
- Agregar cards con metricas visuales
- Mejorar tabla de proyectos (filtros, paginacion)
- Agregar boton "Mi perfil" en navbar

**Justificacion:**
- Dashboard mas informativo
- Metricas clave a primera vista
- Mejor UX para profesores

---

#### [MODIFY] [base.html](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/templates/base.html)

**Cambios:**
- Agregar menu desplegable de usuario en navbar
- Opciones: "Mi perfil", "Mis asignaturas" (alumno), "Cerrar sesion"
- Mostrar nombre de usuario en navbar
- Agregar icono de usuario

**Justificacion:**
- Navegacion consistente en toda la app
- Acceso rapido a perfil
- UX estandar de aplicaciones web

---

### Fase 4: Autenticacion API con Bearer Token

#### [NEW] [TokenAuthMiddleware.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/paasify/middleware/TokenAuthMiddleware.py)

**Contenido:**
- Middleware que intercepta requests a `/api/`
- Extrae token de header `Authorization: Bearer <token>`
- Valida token contra `UserProfile.api_token`
- Asigna `request.user` si token valido
- Retorna 401 Unauthorized si token invalido

**Justificacion:**
- Autenticacion centralizada para API
- Compatible con autenticacion de sesion existente
- Estandar de la industria (Bearer Token)

---

#### [MODIFY] [settings.py](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/app_passify/settings.py)

**Cambios:**
- Agregar `paasify.middleware.TokenAuthMiddleware` a `MIDDLEWARE`
- Configurar orden correcto (despues de AuthenticationMiddleware)

**Justificacion:**
- Activar autenticacion por token
- No afecta autenticacion de sesion existente

---

#### [MODIFY] [ServiceViewSet](file:///c:/Users/david/OneDrive/Escritorio/TFG/TGF_APP_DOCKER-PASSIFY/containers/views.py)

**Cambios:**
- Agregar validacion de autenticacion en `create()`
- Permitir autenticacion por sesion O token
- Documentar endpoint en docstring

**Justificacion:**
- API funcional para despliegue programatico
- Retrocompatible con autenticacion de sesion

---

## Verification Plan

### Automated Tests

#### 1. Tests de modelo UserProfile

**Archivo:** `paasify/tests.py` (crear si no existe)

**Tests a crear:**
```python
class UserProfileTokenTests(TestCase):
    def test_generate_token_creates_uuid(self):
        # Verificar que generate_token() crea un UUID valido
        
    def test_refresh_token_changes_token(self):
        # Verificar que refresh_token() cambia el token
        
    def test_get_masked_token_returns_last_8_chars(self):
        # Verificar que get_masked_token() retorna ultimos 8 caracteres
        
    def test_token_is_unique(self):
        # Verificar que no se pueden crear dos tokens iguales
```

**Comando:**
```bash
python manage.py test paasify.tests.UserProfileTokenTests
```

---

#### 2. Tests de vistas de perfil

**Archivo:** `paasify/tests.py`

**Tests a crear:**
```python
class ProfileViewTests(TestCase):
    def test_profile_view_requires_login(self):
        # Verificar que redirige a login si no autenticado
        
    def test_profile_view_shows_user_data(self):
        # Verificar que muestra datos del usuario
        
    def test_change_password_works(self):
        # Verificar que cambio de contrasena funciona
        
    def test_generate_token_creates_token(self):
        # Verificar que genera token correctamente
        
    def test_refresh_token_changes_token(self):
        # Verificar que refresh cambia el token
```

**Comando:**
```bash
python manage.py test paasify.tests.ProfileViewTests
```

---

#### 3. Tests de autenticacion API

**Archivo:** `containers/tests.py` (ya existe)

**Tests a agregar:**
```python
class TokenAuthTests(TestCase):
    def test_api_accepts_valid_bearer_token(self):
        # Verificar que API acepta token valido
        
    def test_api_rejects_invalid_bearer_token(self):
        # Verificar que API rechaza token invalido
        
    def test_api_still_accepts_session_auth(self):
        # Verificar retrocompatibilidad con sesion
```

**Comando:**
```bash
python manage.py test containers.tests.TokenAuthTests
```

---

#### 4. Compilacion Python

**Comando:**
```bash
python -m compileall app_passify containers paasify security templates tests
```

**Resultado esperado:** Sin errores de sintaxis

---

#### 5. Suite completa de tests

**Comando:**
```bash
pytest
```

**Resultado esperado:** Todos los tests existentes + nuevos tests pasan

---

### Manual Verification

#### 1. Verificacion de perfil de usuario

**Pasos:**
1. Iniciar servidor: `python manage.py runserver`
2. Acceder a `http://localhost:8000/login/`
3. Iniciar sesion como alumno (user: `alumno`, pass: `Alumno!2025`)
4. Navegar a "Mi perfil" desde navbar
5. **Verificar:** Se muestran datos personales (username, nombre, email)
6. **Verificar:** Formulario de cambio de contrasena visible
7. **Verificar:** Seccion de Bearer Token visible
8. Hacer clic en "Generar token"
9. **Verificar:** Token se genera y se muestra
10. Hacer clic en "Copiar token"
11. **Verificar:** Token copiado al portapapeles
12. Hacer clic en "Refrescar token"
13. **Verificar:** Token cambia y se muestra nuevo token

---

#### 2. Verificacion de cambio de contrasena

**Pasos:**
1. En pantalla de perfil, rellenar formulario de cambio de contrasena
2. Ingresar contrasena actual: `Alumno!2025`
3. Ingresar nueva contrasena: `NuevaPass!2025`
4. Confirmar nueva contrasena: `NuevaPass!2025`
5. Hacer clic en "Cambiar contrasena"
6. **Verificar:** Mensaje de exito
7. Cerrar sesion
8. Iniciar sesion con nueva contrasena
9. **Verificar:** Login exitoso

---

#### 3. Verificacion de autenticacion API

**Pasos:**
1. En pantalla de perfil, copiar Bearer Token
2. Abrir Postman o curl
3. Crear request POST a `http://localhost:8000/api/containers/`
4. Agregar header: `Authorization: Bearer <token-copiado>`
5. Agregar body JSON:
```json
{
  "name": "test-api-service",
  "mode": "default",
  "image": "nginx:latest"
}
```
6. Enviar request
7. **Verificar:** Respuesta 201 Created
8. **Verificar:** Servicio creado en panel de alumno

---

#### 4. Verificacion de landing page

**Pasos:**
1. Acceder a `http://localhost:8000/`
2. **Verificar:** Hero section con gradiente de fondo
3. **Verificar:** Animaciones de fade-in al cargar
4. **Verificar:** Cards de features con efecto hover
5. **Verificar:** Seccion de roles con badges de colores
6. **Verificar:** Footer con enlaces
7. Redimensionar ventana a mobile
8. **Verificar:** Diseño responsive funciona correctamente

---

#### 5. Verificacion de dashboards

**Pasos:**
1. Iniciar sesion como alumno
2. **Verificar:** Header con nombre y email del alumno
3. **Verificar:** Seccion "Mis asignaturas" visible
4. **Verificar:** Boton "Mi perfil" en navbar
5. Cerrar sesion
6. Iniciar sesion como profesor (user: `profesor`, pass: `Profesor!2025`)
7. **Verificar:** Estadisticas de asignaturas y alumnos
8. **Verificar:** Boton "Mi perfil" en navbar

---

#### 6. Verificacion de admin - Refresh de token

**Pasos:**
1. Iniciar sesion como admin (user: `admin`, pass: `Admin!123`)
2. Acceder a `/admin/paasify/userprofile/`
3. **Verificar:** Columna "Token API" visible (parcial)
4. **Verificar:** Columna "Fecha creacion token" visible
5. Seleccionar un alumno
6. En acciones, seleccionar "Refrescar token API"
7. Hacer clic en "Ejecutar"
8. **Verificar:** Mensaje de exito
9. **Verificar:** Token cambio (ultimos 8 caracteres diferentes)

---

## Notas de Implementacion

### Orden de implementacion sugerido:

1. **Migraciones de modelo** (UserProfile con campos de token)
2. **Vistas de perfil** (profile_view, change_password, generate/refresh token)
3. **Template de perfil** (profile.html)
4. **Modificaciones en admin** (readonly fields, action de refresh)
5. **Middleware de autenticacion** (TokenAuthMiddleware)
6. **Tests automatizados** (modelo, vistas, API)
7. **Mejora de landing page** (index.html, landing.css)
8. **Mejora de dashboards** (student_panel.html, dashboard.html)
9. **Modificaciones en base.html** (navbar con menu de usuario)
10. **Verificacion manual completa**

### Consideraciones de seguridad:

- Tokens deben ser UUID4 (128 bits de entropia)
- Tokens deben ser unicos en la base de datos
- Tokens deben transmitirse solo via HTTPS en produccion
- Tokens deben ser revocables (refresh genera nuevo token)
- Middleware debe validar token en cada request
- No loggear tokens en logs de aplicacion

### Consideraciones de UX:

- Instrucciones claras de uso del token en pantalla de perfil
- Confirmacion antes de refrescar token (invalida el anterior)
- Feedback visual al copiar token (toast o mensaje)
- Mostrar fecha de creacion del token para auditoria
- Opcion de ocultar/mostrar token completo (toggle)

---

**Fecha de creacion:** 2025-11-24 22:52
**Version:** 4.0
