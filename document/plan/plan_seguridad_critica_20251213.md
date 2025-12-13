# Plan de Seguridad Crítica - PaaSify

**Fecha de Creación:** 2025-12-13  
**Prioridad:** CRÍTICA - Bloqueante para Producción

---

## FASE 1: SEGURIDAD CRÍTICA (OBLIGATORIA - Antes de Producción)

### 1.1 Escalada de Privilegios - Volúmenes Docker
**Severidad:** CRÍTICA  
**Archivos:** `containers/views.py`, `containers/services.py`

**Acción:**
- Eliminar completamente la capacidad de crear volúmenes por defecto para contenedores simples
- Prohibir la definición de volúmenes en `containers/views.py`
- En Docker Compose, solo permitir volúmenes explícitos nombrados (prohibiendo montajes de host)
- Validar y sanitizar cualquier configuración de volúmenes en archivos Compose

**Implementación:**
- Remover campos de volúmenes de formularios y vistas
- Bloquear cualquier input de usuario relacionado con volúmenes
- Para Compose: Parser debe rechazar bind mounts y solo aceptar volúmenes nombrados
- Documentar política de volúmenes para usuarios

---

### 1.2 Inyección Docker Compose
**Severidad:** CRÍTICA  
**Archivos:** `containers/services.py` (`_run_compose_service`)

**Acción:**
- Implementar parser YAML con validación estricta
- Prohibir configuraciones peligrosas:
  - Montajes de host en `volumes` (solo permitir volúmenes nombrados)
  - `privileged: true`
  - `network_mode: host`
  - `pid: host`
  - `cap_add` con capacidades elevadas
- Forzar límites de recursos (`cpus`, `memory`)
- Registrar intentos de uso de configuraciones prohibidas

**Validación de Volúmenes en Compose:**
- Solo permitir sintaxis: `volume_name:/path/in/container`
- Rechazar: `/host/path:/container/path`
- Rechazar: `./relative/path:/container/path`
- Crear volúmenes nombrados automáticamente si no existen

---

### 1.3 Tokens JWT Irrevocables
**Severidad:** ALTA  
**Archivos:** `paasify/middleware/TokenAuthMiddleware.py`

**Acción:**
- Verificar token contra BD en cada request
- Implementar revocación efectiva de tokens
- Comparar token recibido con el almacenado en `UserProfile`
- Rechazar tokens que no coincidan

**Implementación:**
- Modificar middleware para consultar BD
- Agregar validación adicional después de decodificar JWT
- Implementar endpoint para revocar tokens manualmente
- Documentar proceso de revocación

---

### 1.4 Terminal Web RCE
**Severidad:** CRÍTICA  
**Archivos:** `containers/consumers.py`

**Acción:**
- Implementar restricciones de comandos peligrosos
- Aislar red Docker por usuario/asignatura
- Limitar capacidades del contenedor (capabilities)
- Implementar rate limiting en WebSocket
- Registrar todos los comandos ejecutados

**Restricciones:**
- Bloquear comandos: `rm -rf`, `dd`, fork bombs
- Limitar acceso a red (solo puertos asignados)
- Deshabilitar capabilities innecesarias
- Monitorear patrones sospechosos

---

## Sprint 1: Seguridad (1-2 semanas)

### Semana 1
1. **Volúmenes Docker:**
   - Eliminar inputs de volúmenes en vistas
   - Actualizar servicios para no usar volúmenes por defecto
   - Implementar validación en parser Compose

2. **JWT Tokens:**
   - Modificar middleware de autenticación
   - Implementar verificación contra BD
   - Tests de revocación

### Semana 2
3. **Parser Docker Compose:**
   - Desarrollar validador YAML
   - Implementar blacklist de configuraciones
   - Forzar límites de recursos
   - Tests con archivos maliciosos

4. **Restricciones Terminal:**
   - Implementar filtro de comandos
   - Configurar aislamiento de red
   - Rate limiting
   - Sistema de auditoría

---

## CRITERIOS DE ACEPTACIÓN

**Seguridad:**
- [ ] Auditoría de penetración pasada
- [ ] Tokens revocables funcionando correctamente
- [ ] Volúmenes completamente restringidos (solo nombrados en Compose)
- [ ] Compose validado y configuraciones peligrosas bloqueadas
- [ ] Terminal con restricciones de comandos activas
- [ ] Red Docker aislada por usuario
- [ ] Todos los tests de seguridad pasando
- [ ] Documentación de seguridad actualizada

**Validación de Volúmenes:**
- [ ] Contenedores simples NO tienen volúmenes
- [ ] Compose solo acepta volúmenes nombrados
- [ ] Bind mounts completamente bloqueados
- [ ] Tests confirman rechazo de montajes de host

**Tokens:**
- [ ] Regenerar token invalida inmediatamente el anterior
- [ ] Tokens robados pueden ser revocados manualmente
- [ ] Middleware consulta BD en cada request

**Terminal:**
- [ ] Comandos peligrosos bloqueados
- [ ] Rate limiting funcional
- [ ] Auditoría de comandos activa
- [ ] Alertas de seguridad configuradas

---

## NOTAS IMPORTANTES

- **NO desplegar a producción** hasta completar todas las tareas de Sprint 1
- Testing continuo en cada fase
- Documentar todos los cambios de seguridad
- Revisión de código requerida antes de merge
- Penetration testing obligatorio antes de producción
