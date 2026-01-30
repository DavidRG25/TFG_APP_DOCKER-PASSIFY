# Plan de Mejoras UI - Servicios y API

**Fecha creación**: 2025-12-09  
**Última actualización**: 2026-01-30  
**Prioridad**: MEDIA  
**Estado**: EN PROGRESO (60% completado - 3/5 fases)

---

## 🎯 OBJETIVO

Mejorar la experiencia de usuario al crear servicios y proporcionar capacidades de despliegue vía API/comandos para integración continua.

---

## 📋 FASE 1: Página Dedicada "Nuevo Servicio" ✅ COMPLETADA

### **Objetivo:**

Convertir el modal actual en una página dedicada con mejor organización y más espacio.

### **Tareas:**

#### **1.1 Crear nueva vista y template** ✅

- [x] Crear vista `new_service_page` en `containers/views.py`
- [x] Crear template `containers/new_service.html`
- [x] Añadir ruta en `containers/urls.py`

**Implementado en**: `containers/views.py` (líneas 838-863)

#### **1.2 Diseñar layout de 2 columnas** ✅

- [x] Columna izquierda: Formulario
- [x] Columna derecha: Ayuda contextual con consejos y ejemplos
- [x] Breadcrumbs: Inicio > Servicios > Nuevo Servicio
- [x] Botones: Cancelar (volver) / Crear Servicio

**Implementado en**: `templates/containers/new_service.html`

#### **1.3 Mejorar validación y feedback** ✅

- [x] Validación de formulario con HTML5
- [x] Mensajes de error claros
- [x] Validación de nombre (solo minúsculas, números y guiones)
- [x] Validación de puerto (40000-50000)
- [x] Feedback visual con HTMX

**Nota**: Preview de Dockerfile e indicador de progreso quedan como mejoras futuras opcionales.

#### **1.4 Actualizar navegación** ✅

- [x] Cambiar botón "Nuevo servicio" para redirigir a página dedicada
- [x] Breadcrumbs funcionales

**Modificado**: `templates/containers/student_panel.html` (línea 13)

**Tiempo real**: 2 horas  
**Estado**: ✅ COMPLETADO (14/01/2026)

---

## 📋 FASE 2: Sistema de API REST con Tokens ✅ COMPLETADA

### **Objetivo:**

Permitir a los alumnos crear/gestionar servicios vía API REST usando tokens de autenticación.

### **Tareas:**

#### **2.1 Implementar sistema de tokens** ✅

- [x] Añadir `rest_framework.authtoken` a INSTALLED_APPS
- [x] Añadir `TokenAuthentication` a REST_FRAMEWORK
- [x] Aplicar migraciones de base de datos

**Modificado**: `app_passify/settings.py` (líneas 65, 186)

**Migraciones aplicadas**:

```
Applying authtoken.0001_initial... OK
Applying authtoken.0002_auto_20160226_1747... OK
Applying authtoken.0003_tokenproxy... OK
Applying authtoken.0004_alter_tokenproxy_options... OK
```

#### **2.2 Crear endpoints API** ✅

**Nota**: Los endpoints ya existían en `ServiceViewSet` (containers/views.py):

- [x] `POST /api/containers/` - Crear servicio
- [x] `GET /api/containers/` - Listar servicios
- [x] `GET /api/containers/{id}/` - Detalle servicio
- [x] `POST /api/containers/{id}/start/` - Iniciar
- [x] `POST /api/containers/{id}/stop/` - Detener
- [x] `POST /api/containers/{id}/remove/` - Eliminar

**Estado**: Ya implementados, ahora funcionan con Token Authentication.

#### **2.3 Gestión de tokens en UI** ✅

- [x] Vista `manage_api_token` para generar/regenerar token
- [x] Template `api_token.html` con visualización de token
- [x] Botón "Copiar token" funcional
- [x] Botón "Regenerar token" con confirmación
- [x] Advertencia de seguridad

**Implementado en**:

- `containers/views.py` (líneas 866-888)
- `templates/containers/api_token.html`
- `containers/urls.py` (línea 22)

**Tiempo real**: 2 horas  
**Estado**: ✅ COMPLETADO (14/01/2026)

---

## 📋 FASE 3: Página de Documentación API ✅ COMPLETADA

### **Objetivo:**

Crear una página dedicada con documentación completa de la API y ejemplos de comandos curl.

### **Tareas:**

#### **3.1 Crear página de documentación** ✅

- [x] Template `api_token.html` con documentación integrada
- [x] Vista `manage_api_token` sirve la documentación
- [x] Ruta `/paasify/containers/api-token/`

**Implementado en**: `templates/containers/api_token.html`

#### **3.2 Funcionalidades interactivas** ✅

- [x] Botón "Copiar comando" para cada ejemplo
- [x] Token del usuario insertado automáticamente en ejemplos
- [x] URL correcta en todos los ejemplos
- [x] Secciones colapsables (acordeones) para cada endpoint

**Implementado con**: Bootstrap 5 Accordion + JavaScript

#### **3.3 Ejemplos incluidos** ✅

- [x] Crear servicio (POST /api/containers/)
- [x] Listar servicios (GET /api/containers/)
- [x] Iniciar servicio (POST /api/containers/{id}/start/)
- [x] Detener servicio (POST /api/containers/{id}/stop/)
- [x] Eliminar servicio (POST /api/containers/{id}/remove/)
- [x] Ejemplo de integración con GitHub Actions

**Tiempo real**: Incluido en FASE 2  
**Estado**: ✅ COMPLETADO (14/01/2026)

---

## 📋 FASE 4: Página Dedicada Documentación API 🔄 PENDIENTE

### **Objetivo:**

Crear una página dedicada y completa de documentación de la API REST, estilo Swagger/Postman, con todos los endpoints, ejemplos interactivos y casos de uso.

**⚡ CONCEPTO CLAVE:** Esta página debe ser el **equivalente en comandos curl** de todo lo que se puede hacer en la UI de "Nuevo Servicio". Es decir:

```
┌──────────────────────────────────────────────────────────────┐
│  UI: Nuevo Servicio          ←→   API Docs: Comandos curl    │
├──────────────────────────────────────────────────────────────┤
│  Formulario web              ←→   POST /api/containers/      │
│  Click en "Crear"            ←→   curl con JSON              │
│  Seleccionar imagen          ←→   "image": "nginx"           │
│  Configurar puertos          ←→   "custom_port": 45000       │
│  Subir Dockerfile            ←→   "dockerfile": "..."        │
│  Subir docker-compose        ←→   "compose": "..."           │
│  Variables de entorno        ←→   "environment": {...}       │
│  Asignar a proyecto          ←→   "project_id": 123          │
└──────────────────────────────────────────────────────────────┘
```

**Resultado:** El usuario puede automatizar **TODO** lo que hace manualmente en la UI.

### **Tareas:**

#### **4.1 Crear página dedicada de API** 🔄

- [ ] Nueva ruta `/paasify/api/docs/` o `/paasify/containers/api-docs/`
- [ ] Template `api_documentation.html` dedicado
- [ ] Vista `api_documentation_view` en `containers/views.py`
- [ ] Añadir enlace en navbar principal

**Ubicación sugerida**: Navbar → "API" o "Documentación API"

#### **4.2 Diseño de la página** 🔄

**Layout:**

```
┌─────────────────────────────────────────────────┐
│ 📚 Documentación API REST                       │
├─────────────────────────────────────────────────┤
│ Sidebar (izq)         │ Contenido principal     │
│ ─────────────────     │ ─────────────────────── │
│ • Introducción        │ [Sección activa]        │
│ • Autenticación       │                         │
│ • Endpoints:          │ Título                  │
│   - Servicios         │ Descripción             │
│   - Proyectos         │                         │
│   - Usuarios          │ Ejemplo curl:           │
│ • Ejemplos CI/CD      │ [código copiable]       │
│ • Códigos de error    │                         │
│ • Rate limiting       │ Respuesta:              │
│                       │ [JSON formateado]       │
└───────────────────────┴─────────────────────────┘
```

**Características:**

- [ ] Sidebar fijo con navegación por secciones
- [ ] Scroll suave entre secciones
- [ ] Sintaxis highlighting para código (Prism.js o highlight.js)
- [ ] Botones "Copiar" en todos los ejemplos
- [ ] Tema oscuro/claro (opcional)

#### **4.3 Secciones de contenido** 🔄

##### **4.3.1 Introducción**

- [ ] Qué es la API de PaaSify
- [ ] Casos de uso (CI/CD, automatización, integración)
- [ ] Requisitos previos
- [ ] URL base de la API

##### **4.3.2 Autenticación**

- [ ] Cómo obtener un token API
- [ ] Cómo usar el token en requests
- [ ] Ejemplo de autenticación
- [ ] Renovación de tokens
- [ ] Seguridad y mejores prácticas

##### **4.3.3 Endpoints - Servicios/Contenedores**

Para cada endpoint:

- [ ] **GET /api/containers/** - Listar servicios
  - Descripción
  - Parámetros (query params, filtros)
  - Ejemplo curl
  - Respuesta de ejemplo (JSON)
  - Códigos de estado

- [ ] **POST /api/containers/** - Crear servicio
  - Descripción: "Equivalente a crear un servicio desde la UI de 'Nuevo Servicio'"
  - Body parameters (JSON schema)
  - **Ejemplos por modo de creación:**

    **Modo 1: Imagen del catálogo** (equivalente a seleccionar del dropdown)

    ```bash
    curl -X POST http://localhost:8000/api/containers/ \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "mi-nginx",
        "image": "nginx:latest",
        "mode": "default",
        "custom_port": 45000
      }'
    ```

    **Modo 2: Dockerfile personalizado** (equivalente a subir Dockerfile)

    ```bash
    curl -X POST http://localhost:8000/api/containers/ \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "mi-app-python",
        "mode": "custom",
        "dockerfile": "FROM python:3.11\nWORKDIR /app\nCOPY . .\nCMD python app.py",
        "custom_port": 45001
      }'
    ```

    **Modo 3: Docker Compose** (equivalente a subir docker-compose.yml)

    ```bash
    curl -X POST http://localhost:8000/api/containers/ \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "mi-stack-completo",
        "mode": "compose",
        "compose": "services:\n  web:\n    image: nginx\n    ports:\n      - 8080:80\n  redis:\n    image: redis:7"
      }'
    ```

    **Modo 4: Con variables de entorno** (equivalente a añadir ENV vars en UI)

    ```bash
    curl -X POST http://localhost:8000/api/containers/ \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "mi-app-node",
        "image": "node:18",
        "mode": "default",
        "environment": {
          "NODE_ENV": "production",
          "PORT": "3000",
          "DATABASE_URL": "postgres://..."
        }
      }'
    ```

    **Modo 5: Asignar a proyecto y asignatura** (equivalente a seleccionar en dropdowns)

    ```bash
    curl -X POST http://localhost:8000/api/containers/ \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "practica-final",
        "image": "nginx:latest",
        "mode": "default",
        "project_id": 123,
        "subject_id": 456
      }'
    ```

  - Respuesta de ejemplo (JSON)
  - Validaciones y errores comunes
  - Códigos de estado (201 Created, 400 Bad Request, 401 Unauthorized)

- [ ] **GET /api/containers/{id}/** - Detalle de servicio
  - Descripción
  - Path parameters
  - Ejemplo curl
  - Respuesta de ejemplo

- [ ] **POST /api/containers/{id}/start/** - Iniciar servicio
  - Descripción
  - Ejemplo curl
  - Respuesta de ejemplo

- [ ] **POST /api/containers/{id}/stop/** - Detener servicio
  - Descripción
  - Ejemplo curl
  - Respuesta de ejemplo

- [ ] **POST /api/containers/{id}/restart/** - Reiniciar servicio
  - Descripción
  - Ejemplo curl
  - Respuesta de ejemplo

- [ ] **DELETE /api/containers/{id}/** - Eliminar servicio
  - Descripción
  - Ejemplo curl
  - Respuesta de ejemplo

##### **4.3.4 Endpoints - Proyectos** (si aplica)

- [ ] **GET /api/projects/** - Listar proyectos
- [ ] **POST /api/projects/** - Crear proyecto
- [ ] **GET /api/projects/{id}/** - Detalle de proyecto
- [ ] **DELETE /api/projects/{id}/** - Eliminar proyecto

##### **4.3.5 Ejemplos de Integración CI/CD**

- [ ] **GitHub Actions**
  - Workflow completo de ejemplo
  - Despliegue automático en push
  - Variables de entorno

- [ ] **GitLab CI**
  - Pipeline de ejemplo
  - Despliegue automático

- [ ] **Jenkins**
  - Jenkinsfile de ejemplo

- [ ] **Script Bash**
  - Script de despliegue simple

##### **4.3.6 Códigos de Error**

- [ ] Tabla de códigos HTTP
- [ ] Errores comunes y soluciones
- [ ] Formato de respuestas de error

##### **4.3.7 Rate Limiting** (si aplica)

- [ ] Límites de requests
- [ ] Headers de rate limit
- [ ] Qué hacer si se excede el límite

#### **4.4 Funcionalidades interactivas** 🔄

- [ ] **Botón "Copiar" en todos los ejemplos**
  - Feedback visual al copiar
  - Icono cambia a ✓ por 2 segundos

- [ ] **Token del usuario insertado automáticamente**
  - Reemplazar `YOUR_TOKEN_HERE` con token real
  - Opción para mostrar/ocultar token

- [ ] **URL correcta en ejemplos**
  - Detectar URL actual (localhost, producción)
  - Reemplazar automáticamente en ejemplos

- [ ] **Try it out** (opcional, avanzado)
  - Formulario para probar endpoints desde la UI
  - Ejecutar request y mostrar respuesta
  - Similar a Swagger UI

#### **4.5 Diseño visual** 🔄

- [ ] **Estilo moderno y profesional**
  - Inspiración: Stripe API Docs, Twilio Docs
  - Colores consistentes con PaaSify
  - Tipografía legible (monospace para código)

- [ ] **Responsive**
  - Sidebar colapsable en móvil
  - Código con scroll horizontal si es necesario

- [ ] **Accesibilidad**
  - Contraste adecuado
  - Navegación por teclado
  - ARIA labels

**Tiempo estimado**: 6-8 horas  
**Estado**: 🔄 PENDIENTE

---

## 📋 FASE 5: Testing y Documentación 🔄 PENDIENTE

### **Objetivo:**

Validar que todas las funcionalidades implementadas funcionan correctamente.

### **Tareas:**

#### **5.1 Testing de funcionalidades** 🔄

- [ ] Ejecutar tests de página "Nuevo Servicio" (Tests 1-7)
- [ ] Ejecutar tests de sistema de tokens (Tests 8-10)
- [ ] Ejecutar tests de API con tokens (Tests 11-16)
- [ ] Ejecutar test de seguridad (Test 17)
- [ ] Probar página de documentación API (navegación, copiar, ejemplos)

**Documento de testing**: `document/testing/testing_mejoras_ui_servicios_20260114.md`  
**Total de tests definidos**: 17  
**Tests ejecutados**: 0/17

#### **5.2 Documentación de usuario** 🔄

- [ ] Actualizar README con información sobre nueva página
- [ ] Actualizar README con información sobre API
- [ ] Enlace a documentación API desde README
- [ ] Ejemplos de integración con CI/CD (ya incluidos en la UI)

#### **5.3 Ajustes según resultados de testing** 🔄

- [ ] Corregir bugs encontrados durante testing
- [ ] Mejorar UX según feedback
- [ ] Optimizar performance si es necesario

**Tiempo estimado**: 4-6 horas  
**Estado**: 🔄 PENDIENTE

---

## 📊 RESUMEN DE PROGRESO

### **Fases Completadas:**

1. ✅ **Página dedicada "Nuevo Servicio"** (4-6h estimado, 2h real)

### **Archivos Creados:**

1. `templates/containers/new_service.html` (~300 líneas)
2. `templates/containers/api_token.html` (~300 líneas)
3. `document/implementacion/implementacion_mejoras_ui_servicios_20260114.md`
4. `document/testing/testing_mejoras_ui_servicios_20260114.md`

### **Archivos Modificados:**

1. `containers/views.py` (+51 líneas)
   - Vista `new_service_page` (líneas 838-863)
   - Vista `manage_api_token` (líneas 866-888)
2. `containers/urls.py` (+6 líneas)
   - Ruta `new/` (línea 19)
   - Ruta `api-token/` (línea 22)
3. `app_passify/settings.py` (+2 líneas)
   - `rest_framework.authtoken` en INSTALLED_APPS (línea 65)
   - `TokenAuthentication` en REST_FRAMEWORK (línea 186)
4. `templates/containers/student_panel.html` (1 línea)
   - Botón "Nuevo servicio" actualizado (línea 13)

### **Migraciones Aplicadas:**

- `authtoken.0001_initial`
- `authtoken.0002_auto_20160226_1747`
- `authtoken.0003_tokenproxy`
- `authtoken.0004_alter_tokenproxy_options`

---

## ✅ BENEFICIOS IMPLEMENTADOS

### **UX Mejorada:**

- ✅ Página dedicada con más espacio para crear servicios
- ✅ Ayuda contextual y ejemplos en tiempo real
- ✅ Mejor organización del formulario
- ✅ Breadcrumbs para navegación clara
- ✅ Validación mejorada con mensajes claros

### **Automatización:**

- ✅ Bearer Tokens para acceso a API
- ✅ Documentación completa con ejemplos curl
- ✅ Ejemplos de integración con CI/CD
- ✅ Regeneración segura de tokens
- ✅ Endpoints funcionando con Token Authentication

---

## 🔄 PRÓXIMOS PASOS

1. **Ejecutar testing manual** (Tests 1-17)
   - Documento: `document/testing/testing_mejoras_ui_servicios_20260114.md`
2. **Marcar tests como pasados/fallidos**
   - Actualizar documento de testing con resultados

3. **Corregir bugs encontrados** (si los hay)
   - Ajustar código según resultados de testing

4. **Actualizar README** (opcional)
   - Añadir sección sobre nueva página de servicio
   - Añadir sección sobre API REST

5. **Mover a completado**
   - Mover documento de testing a `testing/completado/` cuando esté 100%
   - Actualizar este plan con estado COMPLETADO

6. **Commit final**
   - Crear commit con todos los cambios
   - Merge a develop

---

## 📚 REFERENCIAS

**Documentos relacionados:**

- Plan original: Este documento
- Implementación: `document/implementacion/implementacion_mejoras_ui_servicios_20260114.md`
- Testing: `document/testing/testing_mejoras_ui_servicios_20260114.md`

**Endpoints API:**

- Página nueva servicio: `/paasify/containers/new/`
- Gestión de tokens: `/paasify/containers/api-token/`
- API base: `/api/containers/`

---

**Estado**: EN PROGRESO (50% completado)  
**Última actualización**: 2026-01-14 22:15  
**Próxima acción**: Ejecutar testing manual
