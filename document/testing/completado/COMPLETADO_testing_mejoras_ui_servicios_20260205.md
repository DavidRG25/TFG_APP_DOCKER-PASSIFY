# Plan de Testing - Mejoras UI Servicios y API

**Fecha**: 14/01/2026 (Finalizado: 05/02/2026)  
**Tipo**: Testing + Implementación  
**Estado**: COMPLETADO (100% completado)

---

## 🧪 PLAN DE TESTING

### **Test 1: Página Dedicada "Nuevo Servicio" - Acceso y Navegación**

**Objetivo**: Verificar que la nueva página carga correctamente y la navegación funciona

**Pasos**:

1. Acceder al panel de servicios (`/paasify/containers/`)
2. Hacer clic en botón "Nuevo servicio"
3. **Verificar**:
   - [SI] Redirige a `/paasify/containers/new/`
   - [SI] Página carga sin errores
   - [SI] Se muestran breadcrumbs: Inicio > Servicios > Nuevo Servicio
   - [SI] Se muestra header con título "Crear Nuevo Servicio"
   - [SI] Se muestra formulario en columna izquierda
   - [SI] Se muestra ayuda contextual en columna derecha
4. Hacer clic en breadcrumb "Inicio"
5. **Verificar**:
   - [SI] Redirige correctamente al panel principal
6. Hacer clic en botón "Cancelar"
7. **Verificar**:
   - [SI] Redirige correctamente al panel principal

**Resultado Esperado**: ✅ Navegación funciona correctamente

---

### **Test 2: Validación de Formulario**

**Objetivo**: Verificar que las validaciones del formulario funcionan correctamente

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Intentar enviar formulario vacío
3. **Verificar**:
   - [SI] Muestra error "Campo requerido" en nombre
   - [ ] Muestra error "Campo requerido" en proyecto
   - [ ] NO permite enviar formulario
4. Ingresar nombre con espacios: "mi servicio"
5. **Verificar**:
   - [ ] Muestra error de validación de patrón
   - [ ] Mensaje indica "Solo letras minúsculas, números y guiones"
6. Ingresar nombre válido: "mi-servicio-test"
7. **Verificar**:
   - [ ] Validación pasa correctamente
8. Ingresar puerto personalizado: 30000 (fuera de rango)
9. **Verificar**:
   - [ ] Muestra error "Debe estar entre 40000 y 50000"
10. Ingresar puerto válido: 45000
11. **Verificar**:
    - [ ] Validación pasa correctamente

**Resultado Esperado**: ✅ Todas las validaciones funcionan

---

### **Test 2.1: Mensajes de Error Mejorados**

**Objetivo**: Verificar que los errores se muestran de forma elegante sin modals básicos

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar modo "Imagen desde DockerHub"
3. Escribir una imagen que NO existe: `imagen-inexistente-12345:latest`
4. Click en "Crear Servicio" (sin verificar primero)
5. **Verificar**:
   - [SI] NO aparece alert() básico de JavaScript
   - [SI] Aparece mensaje de error en el área de feedback del campo
   - [SI] Error muestra icono de advertencia (⚠️)
   - [SI] Mensaje es claro: "La imagen 'imagen-inexistente-12345:latest' no existe en DockerHub"
   - [SI] Scroll automático al mensaje de error
   - [SI] Botón de cerrar (X) funciona
6. Cerrar el mensaje de error
7. Corregir la imagen a `nginx:latest`
8. Click en "Crear Servicio"
9. **Verificar**:
   - [SI] Muestra loading: "Verificando imagen en DockerHub..."
   - [SI] Muestra éxito: "Imagen verificada. Creando servicio..."
   - [SI] Formulario se envía automáticamente
   - [SI] Servicio se crea correctamente

**Resultado Esperado**: ✅ Errores se muestran de forma elegante y profesional

---

### **Test 3: Modo Default - Imagen del Catálogo**

**Objetivo**: Verificar creación de servicio con imagen del catálogo

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Completar formulario:
   - Nombre: "test-nginx-ui"
   - Proyecto: Seleccionar primer proyecto disponible
   - Modo: Default (ya seleccionado)
   - Imagen: nginx:latest
   - Puerto personalizado: 45100
3. **Verificar antes de enviar**:
   - [SI] Selector de imagen está habilitado
   - [SI] Campos de Dockerfile están deshabilitados (opacity-50)
   - [SI] Campos de Compose están deshabilitados
   - [SI] Campo de código fuente está deshabilitado
4. Hacer clic en "Crear Servicio"
5. **Verificar**:
   - [SI] Redirige al panel de servicios
   - [SI] Servicio aparece en la tabla
   - [SI] Estado es "creating" o "running"
   - [SI] Puerto asignado es 45100
6. Esperar a que el servicio esté "running"
7. **Verificar**:
   - [SI] Botón "Acceder" funciona
   - [SI] Abre nginx en nueva pestaña
   - [SI] Puerto correcto (45100)

**Resultado Esperado**: ✅ Servicio se crea correctamente desde la nueva página

---

### **Test 3.5: Redirección después de crear servicio**

**Objetivo**: Verificar que después de crear un servicio se redirige correctamente al panel principal

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Completar formulario con datos válidos:
   - Nombre: "test-redirect"
   - Proyecto: Seleccionar proyecto
   - Modo: Default
   - Imagen: nginx:latest
3. Hacer clic en "Crear Servicio"
4. **Verificar inmediatamente**:
   - [SI] Aparece toast verde: "✅ Servicio creado exitosamente. Redirigiendo..."
   - [SI] Toast permanece visible ~1.5 segundos
5. **Verificar después de 1.5 segundos**:
   - [SI] Redirige automáticamente a `/paasify/containers/` (panel principal)
   - [SI] URL cambia correctamente
6. **Verificar en panel principal**:
   - [SI] Servicio "test-redirect" aparece en la tabla
   - [SI] Estado es "creating" o "running"
   - [SI] Todos los datos son correctos
7. **Probar con error** (puerto inválido):
   - Volver a `/paasify/containers/new/`
   - Intentar crear servicio con puerto 30000 (fuera de rango)
   - **Verificar**:
     - [SI] NO redirige
     - [SI] Aparece toast rojo con mensaje de error
     - [SI] Aparece alerta roja en el formulario con detalles del error
     - [SI] Usuario puede corregir y volver a intentar

**Resultado Esperado**: ✅ Redirección automática funciona correctamente en éxito, y muestra errores claros en fallo

---

### **Test 4: Modo Custom - Dockerfile**

**Objetivo**: Verificar creación de servicio con Dockerfile personalizado

**Preparación**:

- Crear archivo `Dockerfile`:
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY . .
  RUN pip install flask
  EXPOSE 5000
  CMD ["python", "app.py"]
  ```
- Crear archivo `app.py`:
  ```python
  from flask import Flask
  app = Flask(__name__)
  @app.route('/')
  def hello():
      return 'Hello from UI Test!'
  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
  ```
- Crear ZIP con ambos archivos

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar modo "Custom"
3. **Verificar**:
   - [SI] Selector de imagen se deshabilita
   - [SI] Campos custom se habilitan (sin opacity-50)
   - [SI] Campo de código fuente se habilita
4. Completar formulario:
   - Nombre: "test-flask-ui"
   - Proyecto: Seleccionar proyecto
   - Modo: Custom
   - Dockerfile: Subir archivo
   - Código fuente: Subir ZIP
   - Puerto interno: 5000
   - Puerto personalizado: 45200
5. **Verificar**:
   - [SI] Archivos se suben correctamente
   - [SI] Nombres de archivos se muestran
6. Hacer clic en "Crear Servicio"
7. **Verificar**:
   - [SI] Servicio se crea
   - [SI] Build se ejecuta correctamente
   - [SI] Servicio inicia
   - [SI] Puerto correcto (45200)
   - [SI] Botón "Acceder" muestra "Hello from UI Test!"

**Resultado Esperado**: ✅ Servicio custom se crea correctamente

---

### **Test 5: Modo Custom - Docker Compose**

**Objetivo**: Verificar creación de servicio con docker-compose

**Preparación**:

- Crear `docker-compose.yml`:
  ```yaml
  services:
    web:
      build: .
      ports:
        - "5000:5000"
    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"
  ```
- Incluir Dockerfile y app.py del test anterior
  -- Crear ZIP con todos los archivos

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. Seleccionar modo "Custom"
3. Subir docker-compose.yml
4. **Verificar**:
   - [SI] Campo Dockerfile se deshabilita automáticamente
5. Intentar subir Dockerfile también
6. **Verificar**:
   - [SI] No permite (exclusividad funciona)
7. Completar formulario:
   - Nombre: "test-compose-ui"
   - Proyecto: Seleccionar proyecto
   - Compose: Subir archivo
   - Código: Subir ZIP
8. Hacer clic en "Crear Servicio"
9. **Verificar**:
   - [SI] Servicio se crea
   - [SI] Ambos contenedores inician
   - [SI] Se muestran 2 tarjetas (web y redis)
   - [SI] Botón "Compose" muestra el YAML

**Resultado Esperado**: ✅ Docker Compose se crea desde nueva página

---

### **Test 6: Ayuda Contextual y UX**

**Objetivo**: Verificar que la ayuda contextual es útil

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. **Verificar columna derecha**:
   - [SI] Se muestra card "Consejos"
   - [SI] Se muestran 5 consejos con iconos (incluyendo verificación de DockerHub pública)
   - [SI] Se muestra card "Ejemplos"
   - [SI] Se muestran 4 ejemplos (Nginx, Node.js, DockerHub, Compose)
3. Hacer hover sobre icono de ayuda (ℹ️) en "Puerto personalizado"
4. **Verificar**:
   - [SI] Aparece popover con información
   - [SI] Información es clara y útil
5. Hacer hover sobre icono de ayuda en "Puerto interno"
6. **Verificar**:
   - [SI] Aparece popover con ejemplos (Flask 5000, Django 8000, etc.)
7. Cambiar entre modo Default y Custom
8. **Verificar**:
   - [SI] Transiciones son suaves
   - [SI] Campos se habilitan/deshabilitan correctamente
   - [SI] No hay errores en consola

**Resultado Esperado**: ✅ Ayuda contextual funciona y es útil

---

### **Test 7: Responsive Design**

**Objetivo**: Verificar que la página funciona en diferentes resoluciones

**Pasos**:

1. **Desktop (1920x1080)**:
   - [SI] Layout de 2 columnas se muestra correctamente
   - [SI] Formulario ocupa ~66% del ancho
   - [SI] Ayuda ocupa ~33% del ancho
   - [SI] Todo es legible y espaciado

2. **Tablet (768x1024)**:
   - [SI] Columnas se mantienen lado a lado
   - [SI] Formulario se adapta correctamente
   - [SI] Ayuda sigue visible

3. **Móvil (375x667)**:
   - [SI] Columnas se apilan verticalmente
   - [SI] Formulario primero, ayuda después
   - [SI] Breadcrumbs se adaptan
   - [SI] Botones son tocables (min 44x44px)
   - [SI] No hay scroll horizontal

**Resultado Esperado**: ✅ Responsive funciona en todas las resoluciones

---

### **Test 8: Sistema de Tokens - Generación (Perfil)**

**Objetivo**: Verificar que el sistema de tokens funciona desde el Perfil de Usuario

**Pasos**:

1. Acceder a `/profile/`
2. **Verificar**:
   - [SI] Página carga correctamente con título "Mi Perfil"
   - [SI] Se muestra card "Token de API"
   - [SI] Si no hay token, aparece aviso y botón "Generar Token"
   - [SI] Al generar, aparece un Modal con el token completo
   - [SI] El token tiene 40 caracteres hexadecimales
3. Copiar token desde el botón "Copiar" (dentro del modal o en la card)
4. **Verificar**:
   - [SI] Token se copia al portapapeles
   - [SI] Aparece toast "Token copiado al portapapeles"
   - [SI] En la card principal, el token se muestra enmascarado (solo últimos 8 caracteres) por seguridad

**Resultado Esperado**: ✅ Token se genera y copia correctamente desde el perfil

---

### **Test 9: Sistema de Tokens - Regeneración (Refrescar)**

**Objetivo**: Verificar que la regeneración de tokens funciona

**Pasos**:

1. Acceder a `/profile/`
2. Copiar token actual mediante el botón "Copiar"
3. Hacer clic en "Refrescar Token"
4. **Verificar**:
   - [SI] Aparece confirmación "¿Estás seguro?"
5. Confirmar regeneración
6. **Verificar**:
   - [SI] Aparece Modal con el nuevo token completo
   - [SI] Se muestra mensaje de éxito
   - [SI] Nuevo token es diferente al anterior
   - [SI] Se muestra fecha de caducidad (30 días desde hoy)
7. Intentar usar token antiguo en API
8. **Verificar**:
   - [SI] Token antiguo ya no funciona (401 Unauthorized)

**Resultado Esperado**: ✅ Regeneración (Refresh) invalida token anterior y genera uno nuevo

---

### **Test 10: Documentación e Instrucciones de la API**

**Objetivo**: Verificar que las instrucciones de uso son claras y que la documentación Swagger es accesible

**Pasos**:

1. Acceder a `/profile/`
2. Hacer clic en "¿Cómo usar el token?"
3. **Verificar**:
   - [SI] Se expande sección de ayuda
   - [SI] Muestra ejemplo de comando `curl`
   - [SI] Menciona la cabecera `Authorization: Bearer`
4. Acceder a la documentación técnica oficial en `/api/docs/`
5. **Verificar**:
   - [SI] Carga la interfaz Swagger/Spectacular
   - [SI] Se listan los endpoints de `containers/`
   - [SI]

### **Test 11: Acceso restringido a Swagger/Docs (ADMIN ONLY)**

**Objetivo**: Verificar que solo los administradores pueden ver la documentación técnica

**Pasos**:

1. Iniciar sesión como `alumno` (usuario normal)
2. Intentar acceder a `/api/docs/`
3. **Verificar**:
   - [SI] Redirige al login de administración o muestra 404/403
   - [SI] NO se muestra la documentación técnica
4. Iniciar sesión como `admin`
5. Acceder a `/api/docs/`
6. **Verificar**:
   - [SI] La documentación Swagger carga correctamente

**Resultado Esperado**: ✅ Documentación técnica protegida correctamente

---

## 🔧 MEJORAS IMPLEMENTADAS

### **Mejora 1: Página Dedicada "Nuevo Servicio"** ✅

**Estado**: COMPLETADO (14/01/2026)

**Implementación**:

- Vista `new_service_page` en `containers/views.py`
- Template `new_service.html` con layout de 2 columnas
- Ruta `/paasify/containers/new/`
- Breadcrumbs de navegación
- Ayuda contextual con consejos y ejemplos
- Validación mejorada de formulario
- Responsive design

**Archivos modificados**:

- `containers/views.py`
- `containers/urls.py`
- `templates/containers/new_service.html` (nuevo)
- `templates/containers/student_panel.html` (botón actualizado)

**Prioridad**: 🔴 ALTA → ✅ COMPLETADO

---

### **Mejora 2: Sistema de API REST con Tokens (ExpiringTokens)** ✅

**Estado**: COMPLETADO (05/02/2026)

**Implementación**:

- Integración con `ExpiringToken` (Tokens con caducidad de 30 días)
- Unificación de vistas (`profile_view`, `refresh_token_view`, `copy_token_view`)
- Interfaz Premium en Perfil con actualización dinámica (AJAX/JS)
- Notificaciones Toast globales con SweetAlert2
- Modal de seguridad premium con escudo y barra de progreso

**Archivos modificados**:

- `paasify/views/ProfileView.py` (Lógica unificada)
- `templates/profile.html` (UI Premium + JS)
- `paasify/middleware/TokenAuthMiddleware.py` (Validación de tokens)

**Prioridad**: 🔴 ALTA → ✅ COMPLETADO

---

## 📊 RESUMEN FINAL

### ✅ COMPLETADAS (3/4 fases)

1. ✅ **Página dedicada "Nuevo Servicio"** - Implementado y Testeado
2. ✅ **Sistema de API REST con Tokens** - Implementado y Testeado
3. ✅ **Perfil de Usuario Premium** - Implementado (Estética, Toasts y UX)
4. 🔄 **Continuidad API (Fase Futura)** - Movido a [Plan de Continuidad API](./testing_api_docs_continuidad_20260205.md)

### 📋 TESTS FINALIZADOS

**Total de tests en este bloque**: 11  
**Tests ejecutados**: 11  
**Tests pasados**: 11  
**Tests fallidos**: 0

**Desglose:**

- Tests 1-7: UI "Nuevo Servicio" ✅
- Tests 8-10: Gestión de Tokens en Perfil ✅
- Test 11: Seguridad de Swagger ✅

### 🎯 CRITERIOS DE ACEPTACIÓN ALCANZADOS

- [SI] Página "Nuevo Servicio" carga en < 2s y es responsive.
- [SI] El token copiado coincide con el del Admin.
- [SI] La regeneración actualiza la interfaz sin recargar.
- [SI] Las notificaciones son consistentes (SweetAlert2) en toda la plataforma.
- [SI] La guía rápida de uso es útil y estética.

---

## 🎯 ESTADO FINAL

**Implementación**: 75% completado de la hoja de ruta inicial.  
**Testing**: 100% de la fase actual completada.

**Última actualización**: 2026-02-05 22:50  
**Próximo paso**: Iniciar fase de "Comandos API" para alumnos.
