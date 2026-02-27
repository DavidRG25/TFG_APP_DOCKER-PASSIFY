# Cambio: estilo landing y dashboards

## Alcance
- Landing page rediseñada con hero en dos columnas (CTA, checklist, stats) y secciones de features/pasos/roles alineadas al nuevo look.
- Dashboards de alumno y profesor con banda hero en gradiente, cards elevadas y métricas con iconos.
- Mejoras de legibilidad en badges (texto blanco sobre fondos de color) y separación de iconos en “Mis asignaturas”.
- Cabeceras estilizadas en vistas de profesor (dashboard, detalle de asignatura, detalle de proyecto).

## Archivos clave
- `templates/index.html`
- `templates/base.html`
- `templates/containers/student_panel.html`
- `templates/containers/subjects.html`
- `templates/professor/dashboard.html`
- `templates/professor/subject_detail.html`
- `templates/professor/project_detail.html`
- `app_passify/urls.py`
- `paasify/static/assets/css/landing.css` (nuevo)
- `paasify/static/assets/css/dashboard.css` (nuevo)

## Notas
- El logo ahora lleva a la landing si no hay sesión y al post_login si estás autenticado.
- `dashboard.css` se carga desde `base.html` para unificar estilos en páginas de alumno y profesor.
- Contadores de “Mis servicios” y “Mis asignaturas” incluyen iconos; badges de color usan texto blanco.
