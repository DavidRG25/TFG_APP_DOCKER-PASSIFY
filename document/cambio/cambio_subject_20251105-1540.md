# Cambio — Renombrado de Sport a Subject (2025-11-05 15:40)

## Alcance
- Sustitución del modelo `Sport` por `Subject` con nueva migración (`paasify/migrations/0032_rename_sport_subject.py`).
- Actualización de `UserProject` para referenciar `subject` en lugar de `sport`.
- Ajustes en admin, serializers, vistas y modelos de contenedores para usar `Subject`.
- Normalización de plantillas HTMX/Bootstrap que mostraban `project.sport`.

## Archivos relevantes
- `paasify/models/SubjectModel.py`, `paasify/models/ProjectModel.py`
- `paasify/admin.py`, `paasify/models/__init__.py`
- `paasify/migrations/0032_rename_sport_subject.py`
- `containers/models.py`, `containers/views.py`, `containers/serializers.py`
- `templates/user.html`, `templates/table.html`, `templates/professor/*.html`

## Próximos pasos
- Ejecutar `python manage.py makemigrations` (ya incluida la migración 0032) y `python manage.py migrate`.
- Revisar fixtures o documentación antigua que aún mencionen `Sport` para alinearlas con `Subject`.
