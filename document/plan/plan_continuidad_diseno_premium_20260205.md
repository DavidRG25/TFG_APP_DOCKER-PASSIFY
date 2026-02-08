# Plan de Continuidad: Diseño Premium Unificado

**Fecha de Creación:** 05/02/2026  
**Referencia de Estilo:** `profile.html` (v2026)  
**Estado:** PENDIENTE  
**Prioridad:** MEDIA-ALTA (Post-Rediseño Base)

---

## 🚩 PRE-REQUISITO CRÍTICO

Este plan **SOLO** debe ejecutarse una vez haya finalizado completamente el [Plan de Rediseño UI/UX (2025-12-13)](./plan_rediseno_ui_ux_20251213.md). Este documento actúa como la **"Fase de Pulido Premium"** para elevar la estética de toda la aplicación al estándar alcanzado en la página de perfil.

---

## 🎨 LÍNEA ESTÉTICA (SISTEMA DE DISEÑO)

Se utilizarán los tokens definidos en el "lavado de cara" del perfil:

- **Sombras:** `0 10px 15px -3px rgba(0, 0, 0, 0.07)` (Efecto flotante).
- **Bordes:** `1rem` (16px) para cards principales.
- **Micro-interacciones:** Escalamiento suave (`scale 1.02`) y levitación (`translateY(-5px)`) en hover.
- **Contenedores de Iconos:** Fondos con 10% de opacidad del color de acento.
- **Tipografía:** Jerarquía clara con títulos `fw-bold` y etiquetas `text-uppercase small fw-semibold`.

---

## 📋 FASES DE IMPLEMENTACIÓN

### Fase 1: Header y Navegación Premium

**Objetivo:** Eliminar la apariencia plana de la barra superior.

- [ ] Aplicar degradado `glassmorphism` suave con `backdrop-filter: blur(10px)`.
- [ ] Sustituir los links de texto del menú por botones con estados active/hover más definidos.
- [ ] Rediseñar el dropdown de usuario para que coincida con las nuevas cards premium.
- [ ] Añadir animaciones de entrada a los elementos del menú.

### Fase 2: Proyectos (Panel de Estudiante)

**Objetivo:** Transformar la tabla de servicios en un Grid de Cards Interactivas.

- [ ] Implementar el diseño de "Cards de Servicio" con iconos tecnológicos grandes (Node, Python, Docker).
- [ ] Añadir el indicador de estado pulsante (verde para Running).
- [ ] Botones de acción (Play, Stop, Terminal) estilizados como iconos en círculos flotantes.
- [ ] **Rediseño de Botones de Despliegue (Header del Panel)**:
  - Sustituir iconos estándar por `fas fa-rocket` (Web) y `fas fa-code` (API).
  - Aplicar efecto `glassmorphism` al botón de API (borde sutil, fondo semi-transparente).
  - Implementar micro-animación `hover: scale(1.05)` para mejorar el feedback visual.
- [ ] Barra de progreso de recursos (CPU/RAM) con estética premium (delgada y redondeada).

### Fase 3: Mis Asignaturas y Cursos

**Objetivo:** Pasar de listas simples a un catálogo visual.

- [ ] Crear tarjetas de asignatura con "Avatar de Materia" (iniciales o icono temático).
- [ ] Usar las "Year Badges" (estilo 2024/2026) en todas las menciones de fechas.
- [ ] Añadir mini-gráficos o barras de progreso de completitud del proyecto dentro de la card.

### Fase 4: Dashboard de Profesor

**Objetivo:** Visualización de datos de alto impacto.

- [ ] Rediseñar las cards de métricas (CPU Global, Alumnos Activos) usando el estilo de bordes y sombras premium.
- [ ] Tabla de alumnos con "Semáforos UX": iconos de estado suaves y redondeados.
- [ ] Vista expandible de servicios del alumno usando el mismo grid de la Fase 2 pero a escala reducida.

### Fase 5: Estilización de la Administración (Admin Custom)

**Objetivo:** Consistencia en las herramientas internas.

- [ ] Sobrescribir los estilos del Django Admin para usar la misma paleta de azules y redondez de bordes.
- [ ] Crear vistas personalizadas para la gestión de usuarios y proyectos si el Admin por defecto es demasiado rígido.

---

## 🚀 CRITERIOS DE ÉXITO

1. La aplicación debe sentirse como una **Single Page Application (SPA)** moderna en cuanto a fluidez visual.
2. Todas las páginas deben mantener la misma relación de aspecto en márgenes, espaciado (`gap-4`) y sombras.
3. El uso de **SweetAlert2** debe ser el estándar para todas las confirmaciones (Borrado, Parada, Error).
4. El tiempo de carga visual no debe verse afectado (uso óptimo de CSS).
