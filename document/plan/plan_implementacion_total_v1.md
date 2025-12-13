# Plan Maestro de Implementación Total - PaaSify v1.0

**Fecha de Creación:** 2025-12-13  
**Rama Objetivo:** dev2  
**Prioridad:** CRÍTICA - Seguridad y Rediseño Completo

---

## FASE 1: SEGURIDAD CRÍTICA (OBLIGATORIA - Antes de Producción)

### 1.1 Escalada de Privilegios - Volúmenes Docker
**Severidad:** CRÍTICA  
**Archivos:** `containers/views.py`, `containers/services.py`

**Acción:**
- Eliminar capacidad de usuarios para definir volúmenes arbitrarios
- Implementar volúmenes gestionados internamente
- Validar y sanitizar cualquier input de volúmenes

```python
# Solución propuesta en services.py
volumes = {service.volume_name: {"bind": "/data", "mode": "rw"}}
# NO permitir volumes.update(service.volumes) desde input de usuario
```

### 1.2 Inyección Docker Compose
**Severidad:** CRÍTICA  
**Archivos:** `containers/services.py` (`_run_compose_service`)

**Acción:**
- Implementar parser YAML con validación estricta
- Prohibir: `volumes` (host), `privileged`, `network_mode: host`, `pid: host`
- Forzar límites de recursos (`cpus`, `memory`)

### 1.3 Tokens JWT Irrevocables
**Severidad:** ALTA  
**Archivos:** `paasify/middleware/TokenAuthMiddleware.py`

**Acción:**
- Verificar token contra BD en cada request
- Implementar revocación efectiva de tokens

```python
if user.user_profile.api_token != token:
    return JsonResponse({"detail": "Token revocado"}, status=401)
```

### 1.4 Terminal Web RCE
**Severidad:** CRÍTICA  
**Archivos:** `containers/consumers.py`

**Acción:**
- Implementar restricciones de comandos
- Aislar red Docker
- Limitar capacidades del contenedor

---

## FASE 2: REDISEÑO UI/UX

### 2.1 Sistema de Diseño
**Paleta Dark Tech:**
- Fondo: `#0f172a` (Slate 900)
- Paneles: `#1e293b` (Slate 800)
- Acento: `#3b82f6` → `#60a5fa` (hover)
- Éxito: `#10b981` (Emerald 500)
- Error: `#ef4444` (Red 500)
- Tipografía: Inter/Roboto

### 2.2 Componentes Clave
- Botones: Planos con glow en hover
- Tablas → Card Grids (móvil)
- Terminal: Modal fullscreen, fondo negro, Fira Code

### 2.3 Vistas a Rediseñar

**Login (`login.html`):**
- Pantalla dividida
- Logo grande + slogan
- Formulario flotante minimalista
- Toast notifications

**Dashboard Alumno (`student_panel.html`):**
- Header con métricas (CPU, RAM, Contenedores)
- Grid de tarjetas por servicio
- Wizard lateral para crear servicio (3 pasos)

**Dashboard Profesor:**
- Gráficos de actividad por asignatura
- Tarjetas grandes con imágenes de fondo
- Semáforos de estado en tiempo real

---

## FASE 3: REFACTORIZACIÓN TÉCNICA

### 3.1 Frontend
- Migrar a Tailwind CSS o variables CSS custom
- Eliminar Bootstrap conflictivo
- Crear `base.html` con sidebar oscuro
- Mejorar terminal xterm.js (100% altura)

### 3.2 Backend
- Separar lógica de presentación
- Implementar CSP estricta
- Eliminar sesiones redundantes
- Sanitizar descompresión de archivos (Zip Slip)

---

## ORDEN DE EJECUCIÓN

### Sprint 1: Seguridad (1-2 semanas)
1. Fix volúmenes Docker
2. Fix JWT tokens
3. Parser Docker Compose
4. Restricciones terminal

### Sprint 2: UI Base (1 semana)
1. Instalar Tailwind/CSS custom
2. Crear `base.html` nuevo
3. Paleta de colores

### Sprint 3: Vistas (2 semanas)
1. Login
2. Dashboard Alumno
3. Dashboard Profesor

### Sprint 4: Polish (1 semana)
1. Terminal mejorada
2. Animaciones
3. Testing final

---

## CRITERIOS DE ACEPTACIÓN

**Seguridad:**
- [ ] Auditoría de penetración pasada
- [ ] Tokens revocables funcionando
- [ ] Volúmenes restringidos
- [ ] Compose validado

**UI/UX:**
- [ ] Tema oscuro aplicado
- [ ] Responsive en móvil
- [ ] Wizard de creación funcional
- [ ] Terminal fullscreen

---

## NOTAS IMPORTANTES

- **NO desplegar a producción** hasta completar Sprint 1
- Mantener rama `dev2` para desarrollo
- Testing continuo en cada fase
- Documentar cambios de seguridad

**Responsable de Ejecución:** Agente Antigravity futuro  
**Revisión:** Requerida antes de merge a main
