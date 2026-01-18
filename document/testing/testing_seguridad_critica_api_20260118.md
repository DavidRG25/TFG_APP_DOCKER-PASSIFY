# Plan de Testing - Seguridad Crítica (API)

**Fecha**: 18/01/2026  
**Tipo**: Testing de Seguridad - Parte 2 (API)  
**Estado**: PENDIENTE

---

## ⚠️ **PREREQUISITOS**

**ESTE TESTING SE REALIZARÁ POSTERIOR A:**

1. ✅ Completar testing de `testing_seguridad_critica_core_20260118.md`
2. ✅ Completar desarrollo del plan de Mejoras UI Servicios
3. ✅ Completar testing de `testing_mejoras_ui_servicios_20260114.md`
4. ✅ Tener la página de documentación API completamente funcional

**Razón:** Estos tests requieren la interfaz de API completa y documentada para poder ejecutarse correctamente.

---

## 📋 **ALCANCE DE ESTE DOCUMENTO**

Este documento cubre los tests de seguridad que **SÍ requieren API**:

- ✅ Tokens JWT Revocables (Mejora 3)
- ✅ Validación de autenticación
- ✅ Validación de permisos

**Tests Core (sin API)** → Ver: `testing_seguridad_critica_core_20260118.md` (completar primero)

---

## 🧪 TESTING MEJORA 3: TOKENS JWT REVOCABLES

### **Test 3.1: Token Válido**

**Objetivo**: Verificar que token válido funciona

**Pasos**:

1. Acceder a `/paasify/containers/api-token/`
2. Copiar token
3. Ejecutar curl:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN'
   ```
4. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] Devuelve lista de servicios
   - [ ] Usuario autenticado correctamente

**Resultado Esperado**: ✅ Token válido funciona

---

### **Test 3.2: Regenerar Token Invalida Anterior** ⭐ CRÍTICO

**Objetivo**: Verificar que regenerar token invalida el anterior inmediatamente

**Este es el test MÁS IMPORTANTE de la Mejora 3 de Seguridad**

**Pasos**:

1. Obtener token actual (TOKEN_1)
2. Probar TOKEN_1 con API (debe funcionar):
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_1'
   ```
3. **Verificar**: Status 200 OK ✅

4. Regenerar token desde `/paasify/containers/api-token/` (obtener TOKEN_2)

5. Intentar usar TOKEN_1 nuevamente:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_1'
   ```
6. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje: "Token inválido o expirado"
   - [ ] TOKEN_1 ya no funciona ⭐

7. Probar TOKEN_2:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_2'
   ```
8. **Verificar**:
   - [ ] Status code: 200 OK
   - [ ] TOKEN_2 funciona correctamente ✅

**Resultado Esperado**: ✅ Token antiguo invalidado inmediatamente

**Importancia**: Este test valida que la Mejora 3 de Seguridad funciona correctamente.

---

### **Test 3.3: Token Modificado**

**Objetivo**: Verificar que token modificado es rechazado

**Pasos**:

1. Obtener token válido
2. Modificar algunos caracteres del token (ej: cambiar los últimos 5 caracteres)
3. Intentar usar token modificado:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_MODIFICADO'
   ```
4. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Token modificado rechazado

**Resultado Esperado**: ✅ Token modificado rechazado

---

### **Test 3.4: Sin Token**

**Objetivo**: Verificar que requests sin token son rechazados

**Pasos**:

1. Ejecutar curl sin header Authorization:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/
   ```
2. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Mensaje de error apropiado

**Resultado Esperado**: ✅ Sin token rechazado

---

## 📋 TESTS ADICIONALES DE SEGURIDAD API

### **Test 3.5: Permisos de Usuario**

**Objetivo**: Verificar que usuarios solo pueden acceder a sus propios servicios

**Preparación**:

- Tener 2 usuarios diferentes (Usuario A y Usuario B)
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

### **Test 3.6: Token en Admin Panel**

**Objetivo**: Verificar que eliminar token desde admin lo revoca

**Pasos**:

1. Generar token para un usuario
2. Verificar que funciona con API
3. Como admin, ir a `/admin/authtoken/tokenproxy/`
4. Eliminar el token del usuario
5. Intentar usar el token eliminado:
   ```bash
   curl --request GET \
     http://localhost:8000/api/containers/ \
     --header 'Authorization: Bearer TOKEN_ELIMINADO'
   ```
6. **Verificar**:
   - [ ] Status code: 401 Unauthorized
   - [ ] Token eliminado ya no funciona

**Resultado Esperado**: ✅ Eliminar token desde admin lo revoca inmediatamente

---

## 📊 RESUMEN DE TESTING

### **Total de Tests en este documento**: 6

**Por Mejora:**

- Mejora 3 (Tokens JWT): 4 tests
- Tests adicionales de seguridad: 2 tests

**Estado:**

- Tests ejecutados: 0/6
- Tests pasados: 0/6
- Tests fallidos: 0/6

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### **Seguridad:**

- [ ] Tokens revocables funcionan correctamente
- [ ] Regenerar token invalida el anterior INMEDIATAMENTE
- [ ] Tokens modificados son rechazados
- [ ] Sin token = sin acceso
- [ ] Permisos de usuario funcionan correctamente
- [ ] Admin puede revocar tokens

### **Funcionalidad:**

- [ ] API funciona correctamente con tokens válidos
- [ ] Mensajes de error claros
- [ ] Performance aceptable

---

## 🚀 WORKFLOW COMPLETO

### **Orden de Ejecución:**

1. ✅ **Primero:** `testing_seguridad_critica_core_20260118.md` (20 tests)
   - Volúmenes Docker
   - Configuraciones Compose
   - Terminal Web

2. ✅ **Segundo:** `testing_mejoras_ui_servicios_20260114.md` (17 tests)
   - Página nueva servicio
   - Sistema de tokens
   - Documentación API

3. ✅ **Tercero:** `testing_seguridad_critica_api_20260118.md` (6 tests) ← **ESTE DOCUMENTO**
   - Tokens JWT revocables
   - Seguridad API

---

## 📝 NOTAS IMPORTANTES

### **¿Por qué este orden?**

1. **Core primero** porque no depende de nada
2. **UI Servicios segundo** porque implementa la interfaz de API
3. **API Security tercero** porque requiere que todo lo anterior funcione

### **Test Crítico:**

El **Test 3.2: Regenerar Token Invalida Anterior** es el MÁS IMPORTANTE porque valida que la Mejora 3 de Seguridad Crítica funciona correctamente. Si este test falla, hay un problema grave de seguridad.

---

## 🔗 REFERENCIAS

**Documentos relacionados:**

- Testing Core: `testing_seguridad_critica_core_20260118.md`
- Testing UI: `testing_mejoras_ui_servicios_20260114.md`
- Implementación: `implementacion_seguridad_critica_20260114.md`
- Plan: `plan_seguridad_critica_20251213.md`

**Código fuente:**

- Validación de tokens: `paasify/models/StudentModel.py` (líneas 133-171)
- Middleware: `paasify/middleware/TokenAuthMiddleware.py`

---

**Última actualización**: 2026-01-18 21:17  
**Estado**: PENDIENTE - Ejecutar después de completar testing de UI Servicios  
**Próximo paso**: Completar testing core y UI primero
