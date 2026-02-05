# Plan de Testing - Continuidad API REST y Documentación Avanzada

**Fecha**: 05/02/2026  
**Tipo**: Testing + Continuidad  
**Estado**: PENDIENTE (Siguiente Fase)

---

## 🧪 TESTS DE CONTINUIDAD (FASE 2)

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
   - [ ] Click en sección hace scroll suave al contenido

4. **Verificar Sección: Introducción**:
   - [ ] Explica qué es la API de PaaSify
   - [ ] Menciona casos de uso (CI/CD, automatización)
   - [ ] Muestra URL base de la API

5. **Verificar Sección: Autenticación**:
   - [ ] Explica cómo obtener un token
   - [ ] Ejemplo de autenticación funcional

6. **Verificar Sección: POST /api/containers/ (Crear Servicio)**:
   - [ ] Muestra tabla de parámetros (name, image, mode, etc.)
   - [ ] **5 ejemplos de modos de creación** (Capa curl)
   - [ ] Botón "Copiar" funciona
   - [ ] Token del usuario insertado automáticamente en ejemplos

7. **Verificar otros endpoints de Servicios**:
   - [ ] GET /api/containers/ - Listar servicios
   - [ ] POST /api/containers/{id}/start/ - Iniciar
   - [ ] POST /api/containers/{id}/stop/ - Detener
   - [ ] DELETE /api/containers/{id}/ - Eliminar

8. **Verificar Sección: Ejemplos CI/CD**:
   - [ ] GitHub Actions (Workflow YAML)
   - [ ] GitLab CI
   - [ ] Script Bash

9. **Verificar funcionalidad interactivas**:
   - [ ] Feedback visual al copiar (icono cambia a ✓)
   - [ ] Token del usuario se inserta automáticamente en ejemplos
   - [ ] Sintaxis highlighting funciona

**Resultado Esperado**: ✅ Página de documentación API es completa, funcional y profesional

---

## 📊 ESTADO DE LA API (Staff Only)

**Vistas Swagger y Schema:**

- [SI] `/api/docs/` restringido a Staff
- [SI] `/api/schema/` restringido a Staff

**Próximos Pasos**:

1. Desarrollar la pantalla de "Comandos API" para el alumno (similar a 'Nuevo Servicio').
2. Implementar los tests 11 al 17 de forma exhaustiva.
