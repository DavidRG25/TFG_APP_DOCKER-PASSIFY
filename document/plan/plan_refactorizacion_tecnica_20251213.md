# Plan de Refactorización Técnica - PaaSify

**Fecha de Creación:** 2025-12-13  
**Prioridad:** MEDIA - Mejora de Calidad y Mantenibilidad

---

## FASE 3: REFACTORIZACIÓN TÉCNICA

### 3.1 Frontend

**Objetivos:**
- Migrar a Tailwind CSS o variables CSS custom
- Eliminar dependencias conflictivas de Bootstrap
- Crear `base.html` con sidebar oscuro y responsivo
- Mejorar terminal xterm.js (100% altura disponible)

**Tareas:**
- Separar JavaScript inline a archivos externos
- Implementar sistema de build (Webpack/Vite)
- Aplicar Content Security Policy (CSP) estricta
- Optimizar assets (minificación, compresión)

---

### 3.2 Backend

**Objetivos:**
- Separar lógica de negocio de presentación
- Implementar CSP estricta en headers
- Eliminar sesiones redundantes (confiar en Django auth)
- Sanitizar descompresión de archivos (prevenir Zip Slip)

**Tareas:**
- Extraer servicios de vistas (Docker operations, validaciones)
- Simplificar gestión de sesiones
- Validar rutas en archivos comprimidos
- Implementar logging estructurado

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
3. Implementar paleta de colores
4. Componentes base

### Sprint 3: Vistas (2 semanas)
1. Rediseñar Login
2. Rediseñar Dashboard Alumno
3. Rediseñar Dashboard Profesor
4. Wizard de creación

### Sprint 4: Polish (1 semana)
1. Terminal mejorada (fullscreen, tema custom)
2. Animaciones y microinteracciones
3. Testing final (usabilidad, performance, accesibilidad)
4. Documentación

---

## Tareas de Refactorización

### Frontend

**Semana 1:**
- [ ] Migrar JavaScript inline a archivos externos
- [ ] Configurar herramienta de build (Vite recomendado)
- [ ] Implementar CSP estricta
- [ ] Eliminar `unsafe-inline` y `unsafe-eval`

**Semana 2:**
- [ ] Migrar a Tailwind CSS o CSS custom
- [ ] Eliminar clases conflictivas de Bootstrap
- [ ] Crear sistema de componentes reutilizables
- [ ] Optimizar bundle (tree-shaking, code splitting)

---

### Backend

**Semana 1:**
- [ ] Extraer lógica de Docker a servicios separados
- [ ] Simplificar gestión de sesiones (eliminar manual)
- [ ] Implementar validación de archivos ZIP/TAR
- [ ] Prevenir Zip Slip (path traversal)

**Semana 2:**
- [ ] Implementar logging estructurado (JSON)
- [ ] Configurar monitoreo de errores (Sentry opcional)
- [ ] Separar responsabilidades (vistas delgadas)
- [ ] Tests unitarios para servicios

---

## NOTAS IMPORTANTES

### Compatibilidad
- **NO desplegar a producción** hasta completar Sprint 1 (Seguridad)
- Testing continuo en cada fase
- Documentar todos los cambios de seguridad

### Testing
- Tests de regresión obligatorios
- Cobertura mínima del 80% en código refactorizado
- No degradar performance
- Benchmarks antes/después

### Documentación
- Actualizar documentación con cada cambio
- Comentar código complejo
- Mantener CHANGELOG.md
- Guías de desarrollo actualizadas

### Performance
- Lighthouse score > 90 en todas las métricas
- Tiempo de build < 30 segundos
- Hot reload en desarrollo
- Cache busting en producción

### Despliegue
- Revisión de código requerida antes de merge
- Despliegue gradual (feature flags si es necesario)
- Rollback plan preparado
- Monitoreo activo post-despliegue
