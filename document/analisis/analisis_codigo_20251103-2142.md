# Informe de revisión del flujo de alumnos en admin
**Resumen**: Evaluación del formulario de alumnos y del menú principal bajo ejecución ASGI.
---
# Análisis de Código — Rama: codigo-y-analisis
## 🧩 Objetivo
Revisar la creación de alumnos desde el panel de administración y el fallo de plantillas al renderizar el login en Daphne.

## 📂 Archivos revisados
- `paasify/admin.py` — Formulario y listado de alumnos.
- `paasify/models/StudentModel.py` — Restricciones del modelo `Player`.
- `templates/base.html` y `templates/registration/login.html` — Renderizado del menú superior.
- `security/views/SecurityViews.py` — Contexto del login.
- `app_passify/settings.py` — Procesadores de contexto.

## ⚠️ Problemas detectados
- El template base evalúa `user.groups.filter(...).exists` directamente, lo que provoca `TemplateSyntaxError` en Daphne.
- El formulario de alumno solo añade al usuario al grupo `Student`, ignorando el grupo `alumno`, por lo que los listados y permisos quedan inconsistentes con los datos existentes.
- No existe sincronización automática entre los usuarios del grupo Alumno y el modelo `Player`, lo que impide que nuevos usuarios aparezcan en “PaaSify → Alumnos”.

## 💡 Propuestas de solución
- Introducir un procesador de contexto (o variables de vista) que calcule los flags `is_student`, `is_teacher` y `is_admin`, y actualizar `base.html` para usar dichas banderas en lugar de llamar a métodos en el template.
- Normalizar la asignación de grupos en el formulario del admin para aceptar tanto “Student” como “alumno”, añadiendo al menos un grupo válido y reutilizando la lógica desde un helper común.
- Implementar un helper y señales que creen automáticamente la entidad `Player` cuando un usuario entra al grupo de alumnos, evitando duplicados y rellenando valores por defecto.

## 🧠 Impacto estimado
- La navegación en login se renderizará correctamente bajo Daphne y cualquier backend ASGI.
- Los alumnos creados desde el admin o importados desde “Usuarios” quedarán enlazados con `Player`, asegurando listados y permisos coherentes.
- Las vistas basadas en roles tendrán datos consistentes, reduciendo incidencias al gestionar contenedores o asignaturas.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.
---
