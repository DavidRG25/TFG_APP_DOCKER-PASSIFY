# Cambio — Renombrado de modelos `Player`/`Game` (Rama develop)
_Registro de la transición a `UserProfile` y `UserProject` realizada el 2025-11-04._

## 🛠️ Qué cambió
- `paasify/models/StudentModel.py`: el modelo `Player` pasa a llamarse `UserProfile`, con `db_table` homónimo y `related_name="user_profile"`; se actualizan etiquetas y `__str__`.
- `paasify/models/ProjectModel.py`: el modelo `Game` pasa a `UserProject`, con campo `user_profile` (antes `student`) y tabla `user_project`.
- `paasify/admin.py`, `paasify/views/NavigationViews.py`, `containers/views.py`, plantillas (`table.html`, `professor/*.html`, `containers/_service_rows.html`, `student_panel.html`) y comandos de gestión ajustados para usar los nuevos nombres.
- Se añade la migración `0030_rename_player_game.py` que renombra modelos/tablas y actualiza las opciones de metadatos.

## 🎯 Por qué se hizo
- Reducir la ambigüedad provocada por los nombres legacy “Player/Game”, alineándolos con el dominio real de la plataforma (perfiles de usuario y proyectos asignados).
- Facilitar el onboarding de nuevos colaboradores y mejorar la coherencia entre modelos, vistas y documentación.

## 🧩 Qué problema resuelve
- Los modelos y mensajes de la aplicación ahora reflejan correctamente su propósito (perfiles de usuario y proyectos). Se evita confusión en admin, vistas HTMX y documentación.

## ✅ Validación
- `python manage.py create_demo_users`
- Pruebas manuales:
  - Alta de alumno desde `/admin/paasify/userprofile/add/` con creación de usuario nuevo.
  - Revisión de la lista de proyectos en `/paasify/containers/subjects/` y `/professor/subjects/<id>/` comprobando que los enlaces y textos usan los nombres actualizados.
