# Documentación de Ajustes de Espacios, Paneles y Nomenclaturas

**Fecha:** 09/03/2026

## 1. Documentación 'Renombrar panel'

Se ha realizado el cambio en `base.html` y en las cards de estadísticas dentro del panel de los estudiantes, renombrando "Proyectos" por "Mis servicios" e inyectando un icono más adecuado (`fas fa-layer-group`) asociado a contenedores y recursos apilados. Esta modificación alinea mejor las expectativas de lo que gestiona directamente un estudiante de forma proactiva. Adicionalmente, se descartó añadir un panel intermedio extra de "Mis proyectos" para evitar fricción en la navegación.

## 2. Documentación 'Personalización más pequeña'

Se han refactorizado y optimizado los componentes de interfaces de modales (como el de Edición de Proyecto, Nueva Asignatura) y el Terminal/Logs viewer haciéndolos más compactos. Esto incluye la mejora del alineamiento horizontal y la reducción del padding nativo en Bootstrap para aprovechar los espacios libres de forma inteligente en todas las pantallas (especificando anchos máximos (`max-width`) prudentes y separaciones relativas).

## 3. Ajustes consistentes de iconos y márgenes nativos

A lo largo de múltiples pantallas (`_service_rows.html`, `_status.html`, `project_detail.html`, `terminal_v2.html`, `logs_page.html`, y landing page (`index.html`)) se han erradicado las dependencias al margen `me-*` inoperativo de la versión de diseño presente para iconos y se han forzado márgenes CSS directos (`margin-right: 8px !important;` y `margin-left`) dando una respiración real entre recursos/texto y emoticonos.

Se solventó también la opacidad y visibilidad de los badges del ID de asignatura sobre cabeceras oscuras.
