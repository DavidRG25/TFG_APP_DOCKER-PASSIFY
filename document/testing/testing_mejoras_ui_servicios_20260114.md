# Plan de Testing - Mejoras UI Servicios y API

**Fecha**: 14/01/2026 22:12  
**Tipo**: Testing + Implementación  
**Estado**: EN PROGRESO (50% completado)

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
   - [ ] Selector de imagen se deshabilita
   - [ ] Campos custom se habilitan (sin opacity-50)
   - [ ] Campo de código fuente se habilita
4. Completar formulario:
   - Nombre: "test-flask-ui"
   - Proyecto: Seleccionar proyecto
   - Modo: Custom
   - Dockerfile: Subir archivo
   - Código fuente: Subir ZIP
   - Puerto interno: 5000
   - Puerto personalizado: 45200
5. **Verificar**:
   - [ ] Archivos se suben correctamente
   - [ ] Nombres de archivos se muestran
6. Hacer clic en "Crear Servicio"
7. **Verificar**:
   - [ ] Servicio se crea
   - [ ] Build se ejecuta correctamente
   - [ ] Servicio inicia
   - [ ] Puerto correcto (45200)
   - [ ] Botón "Acceder" muestra "Hello from UI Test!"

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
   - [ ] Campo Dockerfile se deshabilita automáticamente
5. Intentar subir Dockerfile también
6. **Verificar**:
   - [ ] No permite (exclusividad funciona)
7. Completar formulario:
   - Nombre: "test-compose-ui"
   - Proyecto: Seleccionar proyecto
   - Compose: Subir archivo
   - Código: Subir ZIP
8. Hacer clic en "Crear Servicio"
9. **Verificar**:
   - [ ] Servicio se crea
   - [ ] Ambos contenedores inician
   - [ ] Se muestran 2 tarjetas (web y redis)
   - [ ] Botón "Compose" muestra el YAML

**Resultado Esperado**: ✅ Docker Compose se crea desde nueva página

---

### **Test 6: Ayuda Contextual y UX**

**Objetivo**: Verificar que la ayuda contextual es útil

**Pasos**:

1. Acceder a `/paasify/containers/new/`
2. **Verificar columna derecha**:
   - [ ] Se muestra card "Consejos"
   - [ ] Se muestran 4 consejos con iconos
   - [ ] Se muestra card "Ejemplos"
   - [ ] Se muestran 3 ejemplos (Nginx, Node.js, Compose)
3. Hacer hover sobre icono de ayuda (ℹ️) en "Puerto personalizado"
4. **Verificar**:
   - [ ] Aparece popover con información
   - [ ] Información es clara y útil
5. Hacer hover sobre icono de ayuda en "Puerto interno"
6. **Verificar**:
   - [ ] Aparece popover con ejemplos (Flask 5000, Django 8000, etc.)
7. Cambiar entre modo Default y Custom
8. **Verificar**:
   - [ ] Transiciones son suaves
   - [ ] Campos se habilitan/deshabilitan correctamente
   - [ ] No hay errores en consola

**Resultado Esperado**: ✅ Ayuda contextual funciona y es útil

---

### **Test 7: Responsive Design**

**Objetivo**: Verificar que la página funciona en diferentes resoluciones

**Pasos**:

1. **Desktop (1920x1080)**:
   - [ ] Layout de 2 columnas se muestra correctamente
   - [ ] Formulario ocupa ~66% del ancho
   - [ ] Ayuda ocupa ~33% del ancho
   - [ ] Todo es legible y espaciado

2. **Tablet (768x1024)**:
   - [ ] Columnas se mantienen lado a lado
   - [ ] Formulario se adapta correctamente
   - [ ] Ayuda sigue visible

3. **Móvil (375x667)**:
   - [ ] Columnas se apilan verticalmente
   - [ ] Formulario primero, ayuda después
   - [ ] Breadcrumbs se adaptan
   - [ ] Botones son tocables (min 44x44px)
   - [ ] No hay scroll horizontal

**Resultado Esperado**: ✅ Responsive funciona en todas las resoluciones

---

### **Test 8: Sistema de Tokens - Generación**

**Objetivo**: Verificar que el sistema de tokens funciona

**Pasos**:

1. Acceder a `/paasify/containers/api-token/`
2. **Verificar**:
   - [ ] Página carga correctamente
   - [ ] Se muestra breadcrumb: Inicio > API Token
   - [ ] Se muestra header con título "Token de API"
   - [ ] Token se genera automáticamente
   - [ ] Token se muestra en input readonly
   - [ ] Token tiene 40 caracteres hexadecimales
3. Copiar token manualmente
4. Hacer clic en botón "Copiar"
5. **Verificar**:
   - [ ] Token se copia al portapapeles
   - [ ] Aparece toast "Token copiado al portapapeles"
   - [ ] Toast desaparece después de 3 segundos

**Resultado Esperado**: ✅ Token se genera y copia correctamente

---

### **Test 9: Sistema de Tokens - Regeneración**

**Objetivo**: Verificar que la regeneración de tokens funciona

**Pasos**:

1. Acceder a `/paasify/containers/api-token/`
2. Copiar token actual
3. Hacer clic en "Regenerar Token"
4. **Verificar**:
   - [ ] Aparece confirmación "¿Estás seguro?"
5. Confirmar regeneración
6. **Verificar**:
   - [ ] Página recarga
   - [ ] Se muestra mensaje "Token regenerado exitosamente"
   - [ ] Nuevo token es diferente al anterior
   - [ ] Nuevo token tiene 40 caracteres
7. Intentar usar token antiguo en API
8. **Verificar**:
   - [ ] Token antiguo ya no funciona (401 Unauthorized)

**Resultado Esperado**: ✅ Regeneración invalida token anterior

---

### **Test 10: Documentación de API**

**Objetivo**: Verificar que la documentación es completa y funcional

**Pasos**:

1. Acceder a `/paasify/containers/api-token/`
2. Scroll hasta sección "Documentación de la API"
3. **Verificar información básica**:
   - [ ] Se muestra Base URL correcta
   - [ ] Se muestra formato de autenticación con token real
   - [ ] Se muestra Content-Type
4. **Verificar acordeones**:
   - [ ] Acordeón "Crear Servicio" está expandido por defecto
   - [ ] Se muestra badge verde "POST"
   - [ ] Se muestra ejemplo de curl completo
   - [ ] Token en ejemplo es el token real del usuario
   - [ ] URL en ejemplo es correcta
5. Hacer clic en "Copiar comando"
6. **Verificar**:
   - [ ] Comando se copia al portapapeles
   - [ ] Toast confirma "Comando copiado"
7. Expandir acordeón "Listar Servicios"
8. **Verificar**:
   - [ ] Badge azul "GET"
   - [ ] Ejemplo de curl correcto
   - [ ] Token incluido
9. Verificar todos los endpoints:
   - [ ] POST Crear Servicio
   - [ ] GET Listar Servicios
   - [ ] POST Iniciar Servicio
   - [ ] POST Detener Servicio
   - [ ] POST Eliminar Servicio
10. Scroll hasta ejemplo de GitHub Actions
11. **Verificar**:
    - [ ] YAML es válido
    - [ ] Usa secrets.PAASIFY_TOKEN
    - [ ] URL es correcta

**Resultado Esperado**: ✅ Documentación es completa y funcional

---

### **Test 11: API con Token - Crear Servicio**

**Objetivo**: Verificar que la API funciona con Token Authentication

**Preparación**:

- Obtener token desde `/paasify/containers/api-token/`
- Tener ID de proyecto y asignatura

**Pasos**:

1. Ejecutar comando curl:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_AQUI' \
     --header 'Content-Type: application/json' \
     --data '{
       "name": "test-api-token",
       "image": "nginx:latest",
       "mode": "default",
       "project": 1,
       "subject": 1
     }'
   ```
2. **Verificar respuesta**:
   - [ ] Status code: 201 Created
   - [ ] JSON con id, name, status, assigned_port
   - [ ] status es "creating"
3. Acceder al panel de servicios
4. **Verificar**:
   - [ ] Servicio "test-api-token" aparece en la tabla
   - [ ] Se está creando o ya está running
5. Esperar a que esté running
6. **Verificar**:
   - [ ] Puerto asignado coincide con el de la respuesta API
   - [ ] Servicio funciona correctamente

**Resultado Esperado**: ✅ API crea servicio correctamente con token

---

### **Test 12: API con Token - Sin Autenticación**

**Objetivo**: Verificar que la API rechaza requests sin token

**Pasos**:

1. Ejecutar comando curl SIN token:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Content-Type: application/json'
   ```
2. **Verificar respuesta**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje de error apropiado
3. Ejecutar POST sin token:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ \
     --header 'Content-Type: application/json' \
     --data '{"name": "test", "image": "nginx:latest"}'
   ```
4. **Verificar respuesta**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Servicio NO se crea

**Resultado Esperado**: ✅ API rechaza requests sin autenticación

---

### **Test 13: API con Token - Token Inválido**

**Objetivo**: Verificar que la API rechaza tokens inválidos

**Pasos**:

1. Ejecutar comando con token falso:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_FALSO_123456'
   ```
2. **Verificar respuesta**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje indica token inválido

**Resultado Esperado**: ✅ API rechaza tokens inválidos

---

### **Test 14: API - Listar Servicios**

**Objetivo**: Verificar endpoint GET /api/containers/

**Pasos**:

1. Crear 2-3 servicios desde la UI
2. Ejecutar curl:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_AQUI'
   ```
3. **Verificar respuesta**:
   - [ ] Status code: 200 OK
   - [ ] Array de servicios
   - [ ] Solo servicios del usuario autenticado
   - [ ] Cada servicio tiene: id, name, status, image, assigned_port
   - [ ] JSON bien formateado

**Resultado Esperado**: ✅ Lista solo servicios del usuario

---

### **Test 15: API - Iniciar/Detener Servicio**

**Objetivo**: Verificar endpoints de control de servicios

**Pasos**:

1. Crear servicio y obtener su ID
2. Detener servicio si está running
3. Ejecutar curl para iniciar:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ID/start/ \
     --header 'Authorization: Bearer TOKEN_AQUI'
   ```
4. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] Servicio inicia
   - [ ] Estado cambia a "running"
5. Ejecutar curl para detener:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ID/stop/ \
     --header 'Authorization: Bearer TOKEN_AQUI'
   ```
6. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] Servicio se detiene
   - [ ] Estado cambia a "stopped"

**Resultado Esperado**: ✅ Control de servicios funciona vía API

---

### **Test 16: API - Eliminar Servicio**

**Objetivo**: Verificar endpoint de eliminación

**Pasos**:

1. Crear servicio de prueba
2. Obtener su ID
3. Ejecutar curl:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ID/remove/ \
     --header 'Authorization: Bearer TOKEN_AQUI'
   ```
4. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] Servicio se elimina de la base de datos
   - [ ] Contenedor Docker se elimina
   - [ ] Workspace se limpia
5. Intentar listar servicios
6. **Verificar**:
   - [ ] Servicio eliminado no aparece en la lista

**Resultado Esperado**: ✅ Eliminación funciona correctamente

---

### **Test 17: Seguridad - Permisos de Usuario**

**Objetivo**: Verificar que usuarios no pueden acceder a servicios de otros

**Preparación**:

- Tener 2 usuarios diferentes
- Usuario A crea un servicio

**Pasos**:

1. Con token de Usuario B, intentar acceder a servicio de Usuario A:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ID_DE_A/ \
     --header 'Authorization: Bearer TOKEN_DE_B'
   ```
2. **Verificar**:
   - [ ] Status code: 404 Not Found o 403 Forbidden
   - [ ] No se muestra información del servicio
3. Intentar detener servicio de Usuario A con token de B:
   ```bash
   curl --request POST \
     http://localhost:8000/api/containers/ID_DE_A/stop/ \
     --header 'Authorization: Bearer TOKEN_DE_B'
   ```
4. **Verificar**:
   - [ ] Status code: 404 Not Found o 403 Forbidden
   - [ ] Servicio NO se detiene

**Resultado Esperado**: ✅ Usuarios solo pueden acceder a sus propios servicios

---

### **Test 18: Página Dedicada de Documentación API**

**Objetivo**: Verificar que la nueva página de documentación API es completa, funcional y fácil de usar

**Pasos**:

1. Acceder a `/paasify/api/docs/` o `/paasify/containers/api-docs/`
2. **Verificar estructura básica**:
   - [ ] Página carga correctamente
   - [ ] Se muestra breadcrumb: Inicio > Documentación API
   - [ ] Header con título "Documentación API REST"
   - [ ] Layout con sidebar izquierdo + contenido principal derecho

3. **Verificar sidebar de navegación**:
   - [ ] Sidebar es fijo (no se mueve al hacer scroll)
   - [ ] Se muestran todas las secciones:
     - Introducción
     - Autenticación
     - Endpoints: Servicios
     - Endpoints: Proyectos
     - Ejemplos CI/CD
     - Códigos de error
     - Rate limiting (si aplica)
   - [ ] Click en sección hace scroll suave al contenido

4. **Verificar Sección: Introducción**:
   - [ ] Explica qué es la API de PaaSify
   - [ ] Menciona casos de uso (CI/CD, automatización)
   - [ ] Muestra URL base de la API
   - [ ] Menciona requisitos previos

5. **Verificar Sección: Autenticación**:
   - [ ] Explica cómo obtener un token
   - [ ] Enlace a `/paasify/containers/api-token/`
   - [ ] Muestra formato de header: `Authorization: Bearer TOKEN`
   - [ ] Ejemplo de autenticación funcional
   - [ ] Menciona seguridad y mejores prácticas

6. **Verificar Sección: POST /api/containers/ (Crear Servicio)**:
   - [ ] Badge verde "POST" visible
   - [ ] Descripción clara: "Equivalente a crear desde UI"
   - [ ] Muestra tabla de parámetros (name, image, mode, etc.)
   - [ ] **5 ejemplos de modos de creación**:

     **Ejemplo 1: Imagen del catálogo**
     - [ ] Código curl completo
     - [ ] Parámetros: name, image, mode: "default"
     - [ ] Botón "Copiar" funciona
     - [ ] Token del usuario insertado automáticamente
     - [ ] URL correcta (localhost o producción)

     **Ejemplo 2: Dockerfile personalizado**
     - [ ] Código curl con mode: "custom"
     - [ ] Muestra campo "dockerfile" con contenido
     - [ ] Botón "Copiar" funciona

     **Ejemplo 3: Docker Compose**
     - [ ] Código curl con mode: "compose"
     - [ ] Muestra campo "compose" con YAML
     - [ ] Botón "Copiar" funciona

     **Ejemplo 4: Con variables de entorno**
     - [ ] Muestra objeto "environment" con múltiples vars
     - [ ] Ejemplo realista (NODE_ENV, DATABASE_URL, etc.)

     **Ejemplo 5: Asignar a proyecto/asignatura**
     - [ ] Muestra campos project_id y subject_id
     - [ ] Explica cómo obtener los IDs

   - [ ] Muestra respuesta de ejemplo (JSON formateado)
   - [ ] Lista códigos de estado (201, 400, 401)
   - [ ] Menciona validaciones y errores comunes

7. **Verificar otros endpoints de Servicios**:
   - [ ] GET /api/containers/ - Listar servicios
   - [ ] GET /api/containers/{id}/ - Detalle
   - [ ] POST /api/containers/{id}/start/ - Iniciar
   - [ ] POST /api/containers/{id}/stop/ - Detener
   - [ ] POST /api/containers/{id}/restart/ - Reiniciar
   - [ ] DELETE /api/containers/{id}/ - Eliminar

   Para cada uno:
   - [ ] Badge de método correcto (GET azul, POST verde, DELETE rojo)
   - [ ] Descripción clara
   - [ ] Ejemplo curl completo
   - [ ] Respuesta de ejemplo
   - [ ] Botón "Copiar" funciona

8. **Verificar Sección: Endpoints de Proyectos** (si aplica):
   - [ ] GET /api/projects/
   - [ ] POST /api/projects/
   - [ ] GET /api/projects/{id}/
   - [ ] DELETE /api/projects/{id}/

9. **Verificar Sección: Ejemplos CI/CD**:

   **GitHub Actions**:
   - [ ] Workflow YAML completo y válido
   - [ ] Usa secrets.PAASIFY_TOKEN
   - [ ] Ejemplo de despliegue automático en push
   - [ ] Botón "Copiar" funciona

   **GitLab CI**:
   - [ ] Pipeline YAML completo
   - [ ] Usa variables de entorno
   - [ ] Botón "Copiar" funciona

   **Jenkins**:
   - [ ] Jenkinsfile de ejemplo
   - [ ] Botón "Copiar" funciona

   **Script Bash**:
   - [ ] Script simple y funcional
   - [ ] Comentarios explicativos
   - [ ] Botón "Copiar" funciona

10. **Verificar Sección: Códigos de Error**:
    - [ ] Tabla con códigos HTTP (200, 201, 400, 401, 403, 404, 500)
    - [ ] Descripción de cada código
    - [ ] Ejemplos de errores comunes
    - [ ] Soluciones sugeridas

11. **Verificar Sección: Rate Limiting** (si aplica):
    - [ ] Explica límites de requests
    - [ ] Muestra headers de rate limit
    - [ ] Qué hacer si se excede

12. **Verificar funcionalidades interactivas**:
    - [ ] Todos los botones "Copiar" funcionan
    - [ ] Feedback visual al copiar (icono cambia a ✓)
    - [ ] Toast de confirmación aparece
    - [ ] Token del usuario se inserta automáticamente en ejemplos
    - [ ] URL se detecta correctamente (localhost vs producción)
    - [ ] Sintaxis highlighting funciona (código coloreado)

13. **Verificar diseño y UX**:
    - [ ] Diseño moderno y profesional
    - [ ] Colores consistentes con PaaSify
    - [ ] Tipografía legible (monospace para código)
    - [ ] Espaciado adecuado
    - [ ] Sin errores visuales

14. **Verificar responsive**:

    **Desktop (1920x1080)**:
    - [ ] Sidebar fijo a la izquierda (~25% ancho)
    - [ ] Contenido principal a la derecha (~75% ancho)
    - [ ] Todo legible y bien espaciado

    **Tablet (768x1024)**:
    - [ ] Sidebar se mantiene visible
    - [ ] Contenido se adapta

    **Móvil (375x667)**:
    - [ ] Sidebar se colapsa (hamburger menu)
    - [ ] Contenido ocupa todo el ancho
    - [ ] Código con scroll horizontal si es necesario
    - [ ] Botones "Copiar" son tocables (min 44x44px)

15. **Verificar accesibilidad**:
    - [ ] Contraste adecuado (WCAG AA)
    - [ ] Navegación por teclado funciona
    - [ ] Tab order lógico
    - [ ] ARIA labels en elementos interactivos
    - [ ] Screen reader puede leer el contenido

16. **Verificar performance**:
    - [ ] Página carga en menos de 2 segundos
    - [ ] Scroll es suave
    - [ ] No hay lag al copiar código
    - [ ] Sintaxis highlighting no afecta performance

17. **Comparar con UI "Nuevo Servicio"**:
    - [ ] Cada opción de la UI tiene su equivalente en comandos
    - [ ] Ejemplos cubren todos los modos (default, custom, compose)
    - [ ] Parámetros coinciden con los del formulario web
    - [ ] Usuario puede hacer TODO lo de la UI desde comandos

**Resultado Esperado**: ✅ Página de documentación API es completa, funcional y profesional

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

- `containers/views.py` (+25 líneas)
- `containers/urls.py` (+3 líneas)
- `templates/containers/new_service.html` (nuevo, ~300 líneas)
- `templates/containers/student_panel.html` (botón actualizado)

**Prioridad**: 🔴 ALTA → ✅ COMPLETADO

---

### **Mejora 2: Sistema de API REST con Tokens** ✅

**Estado**: COMPLETADO (14/01/2026)

**Implementación**:

- Configuración de `rest_framework.authtoken` en settings
- Migraciones aplicadas para modelo Token
- Vista `manage_api_token` para gestión de tokens
- Template `api_token.html` con documentación completa
- Ejemplos de curl para todos los endpoints
- Ejemplo de integración con GitHub Actions
- Funcionalidad de copiar y regenerar tokens

**Archivos modificados**:

- `app_passify/settings.py` (+2 líneas)
- `containers/views.py` (+26 líneas)
- `containers/urls.py` (+3 líneas)
- `templates/containers/api_token.html` (nuevo, ~300 líneas)

**Migraciones aplicadas**:

```
Applying authtoken.0001_initial... OK
Applying authtoken.0002_auto_20160226_1747... OK
Applying authtoken.0003_tokenproxy... OK
Applying authtoken.0004_alter_tokenproxy_options... OK
```

**Prioridad**: 🔴 ALTA → ✅ COMPLETADO

---

## 📊 RESUMEN FINAL

### ✅ COMPLETADAS (2/4 fases)

1. ✅ **Página dedicada "Nuevo Servicio"** - Implementado
2. ✅ **Sistema de API REST con Tokens** - Implementado
3. 🔄 **Endpoints API** - Ya existen, pendiente verificación
4. 🔄 **Testing y Documentación** - En progreso

### 📋 TESTS PENDIENTES

**Total de tests definidos**: 19  
**Tests ejecutados**: 0  
**Tests pasados**: 0  
**Tests fallidos**: 0

**Desglose por categoría:**

- Tests 1-7: Página "Nuevo Servicio" y UX (incluye Test 3.5 de redirección)
- Tests 8-10: Sistema de Tokens
- Tests 11-17: API REST funcionando
- Test 18: Página Dedicada Documentación API

### 🎯 CRITERIOS DE ACEPTACIÓN

**Página "Nuevo Servicio":**

- [ ] Página carga en menos de 2 segundos
- [ ] Formulario es intuitivo y fácil de usar
- [ ] Validación funciona correctamente
- [ ] Ayuda contextual es útil y clara
- [ ] Responsive en todas las resoluciones
- [ ] Accesible (navegación por teclado, screen readers)

**Sistema de Tokens:**

- [ ] Token se genera automáticamente al primer acceso
- [ ] Token se puede copiar fácilmente
- [ ] Regeneración de token funciona correctamente
- [ ] Documentación es completa y clara
- [ ] Ejemplos de curl son correctos y funcionales

**API REST:**

- [ ] Todos los endpoints funcionan con Token Authentication
- [ ] Autenticación es segura
- [ ] Respuestas son consistentes y bien formateadas
- [ ] Errores son descriptivos
- [ ] Performance es aceptable (< 500ms por request)

---

## 🎯 ESTADO FINAL

**Implementación**: 50% completado (2/4 fases)  
**Testing**: 0% ejecutado (0/17 tests)  
**Documentación**: 100% actualizada

**Tiempo total invertido**: ~4 horas  
**Tiempo estimado restante**: ~4 horas (testing + ajustes)

---

**Última actualización**: 2026-01-14 22:12  
**Próximo paso**: Ejecutar tests manuales (Tests 1-17)
