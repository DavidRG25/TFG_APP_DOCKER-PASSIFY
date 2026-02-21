# Plan Maestro: UI/UX Premium Unificado

**Fecha de Creación:** 2026-02-21 23:08  
**Versión:** 1.0.0  
**Estado:** 📋 PENDIENTE  
**Prioridad:** MEDIA (Pospuesto hasta completar Panel del Profesor)

---

## 🎯 OBJETIVO PRINCIPAL

Este documento fusiona y reemplaza los antiguos planes de rediseño (`plan_rediseno_ui_ux_20251213.md` y `plan_continuidad_diseno_premium_20260205.md`). La meta es centralizar todas las tareas pendientes de "Pulido Visual" (UI Premium, Componentes modernos, Micro-animaciones y Navegación) que deben aplicarse globalmente a PaaSify **una vez que la base lógica/funcional (como el Panel del Profesor) esté completada**.

Dado que componentes masivos (como las alertas con SweetAlert2, el diseño del Modal de Creación y el Perfil) ya cuentan con una estética limpia, este plan aborda la "Última Milla Visual".

---

## 🎨 SISTEMA DE DISEÑO BASE "PaaSify 2026"

Toda la aplicación debe compartir los siguientes tokens de diseño consistentes:

- **Fondo General:** Gris ultra-suave (`#f8fafc`).
- **Sombras Base (Cards):** Elevación levitante (`box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.07)`).
- **Semáforos UX (Estados):**
  - 🟢 **Success:** Verde Esmeralda (`#10b981`)
  - 🟡 **Warning:** Naranja/Amarillo Claro (`#f59e0b`)
  - 🔴 **Error/Stop:** Rojo (`#ef4444`)
- **Micro-interacciones:** Escalamiento en hover (`scale(1.02)`) y traslación arriba (`translateY(-5px)`) con transición `ease-in-out` de 200ms a 300ms.
- **Tipografía y Componentes:** Evitar "Glow" (brillo agresivo), optar por bordes curvos (`rounded-4`, `rounded-pill`) y tipografía sin serifa moderna (Inter o Roboto).

---

## 📋 FASES DE IMPLEMENTACIÓN PENDIENTES

### FASE 1: Navegación y Header Principal (El "Cascarón")

**Objetivo:** Modernizar la barra superior y elementos fijos.

- [ ] Sustituir la Topbar plana por un efecto `glassmorphism` (desenfoque de fondo parcial con degradado sutil de azules).
- [ ] Transformar botones de texto del menú (ej. Panel Estudiante) en píldoras (pill) o pestañas indicadoras de página activa con hover azul claro.
- [ ] Mejorar los elementos colapsables de usuario (Dropdowns) para que tengan las mismas sombras premium y bordes redondeados que la pantalla de perfil (`profile.html`).

### FASE 2: Premiumización del Panel del Estudiante (Dashboard)

**Objetivo:** Que la visión general y las tarjetas de contenedores parezcan de una SPA de producción, no una tabla básica.

- [ ] **Métricas Principales:** Añadir una fila inicial de `Cards` en la parte superior con números grandes que lean del backend (ej. `[4 Contenedores Activos] [RAM: 2GB]`).
- [ ] **Tarjetas de Servicios:** Convertir las filas de servicio ("Mis Servicios") a `Cards` o a una tabla puramente `hover` con iconos más grandes (reconocimiento automático: un logo de Postgres/Python) y el punto verde/rojo que pulse dinámicamente.
- [ ] **Botones Flotantes de Acción:** Las opciones de "Play", "Stop", "Eliminar" e ir a "API/Web" deben ser botones de icono limpios con Tooltips.

### FASE 3: El Panel del Profesor

**Objetivo:** Datos visuales y resumen académico.
_(Nota: Este paso se aplicará a la par o justo después de programar la funcionalidad lógica del profesor)_.

- [ ] Aplicar tarjetas (Cards) masivas con número de Alumnos y Servicios totales en la cuenta de dicho profesor.
- [ ] Aplicar el Semáforo de UX en las listas de alumnos (🟢 si sus servicios corren, 🔴 si hay múltiples errores).
- [ ] Integrar un gráfico visual mínimo (ej. `Chart.js`) para ver la distribución de memoria/alumnos por clase.

### FASE 4: Vistas Menores y Unificación CSS

**Objetivo:** Evitar componentes Legacy (de la época inicial de Django).

- [ ] Página "Mis Asignaturas": Dejar de usar listas base en favor de cajas redondeadas donde la asignatura tiene un icono/color decorativo y se muestra qué profesor las dicta.
- [ ] Centralizar el CSS extra en una capa única (ej. `base_premium.css`) para evitar repetición `style="..."` en todo el HTML, optimizando tiempos de carga y estandarizando.

---

## 🚩 METODOLOGÍA Y SIGUIENTE PASO

Este plan se activará en formato "Pasada de Pulido" a las vistas que primero deben crearse estructuralmente.

**Próximo Proyecto Crítico:** Construir la base lógica/funcional del PANEL DEL PROFESOR.
