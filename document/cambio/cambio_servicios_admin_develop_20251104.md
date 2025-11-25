# Cambio — Gestión de alumnos y servicios (Rama develop)
_Registro de ajustes aplicados el 2025-11-04 para mejorar la administración de alumnos y la UX de servicios._

## 🛠️ Qué cambió
- `paasify/admin.py`: creación de usuarios desde el admin garantiza la pertenencia al grupo Student, rellena datos obligatorios por defecto y elimina referencias a constantes inexistentes (`STUDENT_GROUP`).
- `containers/views.py`, `templates/containers/_service_rows.html`, `templates/containers/student_panel.html`: los endpoints HTMX devuelven fragmentos HTML con eventos personalizados, cierran el modal al crear un servicio y muestran toasts amigables; los estados se renderizan con badges de alto contraste.

## 🎯 Por qué se hizo
- El formulario “Agregar Alumno” lanzaba `NameError` y exigía campos redundantes al crear un usuario nuevo.
- El panel de servicios mostraba mensajes JSON crudos, etiquetas de estado poco legibles y mantenía abierto el modal tras crear un servicio.

## 🧩 Qué problema resuelve
- Permite crear alumnos directamente desde el admin sin errores ni pasos adicionales.
- Unifica la experiencia HTMX: acciones de iniciar/detener/eliminar muestran toasts y refrescan la tabla sin mostrar JSON, mejorando feedback visual.

## ✅ Validación
- `python manage.py create_demo_users` para verificar asignación de grupos y contraseñas de los usuarios demo.
- Pruebas manuales en `/admin/paasify/player/add/` y en el panel de alumno (`/paasify/containers/`) confirmando cierre de modal, actualización de filas y toasts correctos.
