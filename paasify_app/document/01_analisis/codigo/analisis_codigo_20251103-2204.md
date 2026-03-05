---
*Nota 2025-11-05: el modelo `Sport` fue renombrado a `Subject` y las referencias históricas se conservan sólo como contexto.*
# AnÃ¡lisis de CÃ³digo â€” Rama: feature/analisis-codigo
**Resumen:** EvaluaciÃ³n del alcance del renombrado de Sport a Subject, revisando dependencias de modelos, admin y pruebas.
## ðŸ§© Objetivo
Revisar el impacto del renombrado global de "Sport" a "Subject" en modelos, admin, vistas y pruebas, validando las dependencias actuales y el flujo de creaciÃ³n de alumnos tras las Ãºltimas correcciones de login.

## ðŸ“‚ Archivos revisados
- `paasify/models/SportModel.py`
- `paasify/models/ProjectModel.py`
- `paasify/models/StudentModel.py`
- `paasify/admin.py`
- `containers/views.py`
- `containers/serializers.py`
- `tests/test_containers.py`
- `templates/base.html`
- Migraciones iniciales (`paasify/migrations/0001_initial.py`)

## âš ï¸ Problemas detectados
1. **Dependencias directas del modelo `Sport`:** El modelo `Game` (proyectos) y mÃºltiples vistas/serializadores importan `Sport` con rutas absolutas (`from paasify.models.SportModel import Sport`). Cualquier renombrado requiere actualizar imports, `related_name`, `verbose_name` y el `db_table` (`sport`).
2. **Integridad referencial en proyectos:** `Game.sport` mantiene `on_delete=models.DO_NOTHING`, de modo que borrar una asignatura seguirÃ¡ provocando `IntegrityError`. El renombrado no resolverÃ¡ este comportamiento; habrÃ¡ que replantear la polÃ­tica de borrado o documentar el uso de `PROTECT`/`CASCADE` segÃºn el dominio.
3. **Contexto de plantillas/login:** El login ahora depende de banderas `is_student`, `is_teacher`, `is_admin` calculadas en `SecurityViews.login`. Cualquier refactor debe preservar estas claves en el contexto para evitar el `TemplateSyntaxError` observado con Daphne.
4. **Fixtures y pruebas:** `tests/test_containers.py` y el serializer de servicios referencian `Sport` tanto en consultas como en fixtures; un renombrado exige modificar los datos de prueba y las etiquetas HTMX que filtran por `subject_id`.
5. **Migrations y compatibilidad:** La migraciÃ³n `0001_initial` crea la tabla `sport`. Renombrarla a `subject` en cÃ³digo sin migraciÃ³n de datos romperÃ­a la carga de modelos. Hay que emitir una migraciÃ³n que renombre tabla y constraint, o mantener `db_table="sport"` para compatibilidad.
6. **Comandos administrativos:** No existe un `management command` que sincronice renombrados. La operaciÃ³n manual sobre producciÃ³n podrÃ­a dejar entradas huÃ©rfanas si no se automatiza.

## ðŸ’¡ Propuestas de soluciÃ³n
1. **Plan de renombrado en capas:**
   - Crear `paasify/models/SubjectModel.py` con clase `Subject` derivada de `Sport`, reutilizando `db_table="sport"` para evitar migraciÃ³n inmediata; luego refactorizar imports progresivamente.
   - Actualizar `paasify/models/__init__.py`, vistas, serializers y admin para usar `Subject`.
   - Generar migraciÃ³n que use `migrations.RenameModel` y `migrations.RenameField` si se desea cambiar el nombre en la base de datos (o mantener `db_table` temporalmente).
2. **Revisar on_delete y related_name:** Evaluar cambiar `Game.sport.on_delete` a `models.PROTECT` y renombrar `related_name` a `projects` â†’ `subject_projects` para mayor claridad. Documentar cualquier cambio en el informe de implementaciÃ³n.
3. **Context processor/roles:** Consolidar la lÃ³gica de banderas en un procesador de contexto (`paasify/context_processors.py`) para que todas las plantillas mantengan `is_student`/`is_teacher`/`is_admin`, evitando dependencias en vistas individuales.
4. **Comando de gestiÃ³n opcional:** Implementar `python manage.py rename_sport_to_subject` que:
   - Actualice referencias textuales en la base de datos (si procede) y sincronice grupos/relaciones.
   - Verifique integridad tras el renombrado (contar asignaturas, proyectos y servicios vinculados).
5. **Actualizar documentaciÃ³n y fixtures:** Revisar `README.md`, `tests/test_containers.py` y cualquier fixture que use `sport`/`sports`, reemplazando por `subject`/`subjects` para mantener coherencia funcional.

## ðŸ§  Impacto estimado
- El renombrado coherente eliminarÃ¡ ambigÃ¼edades de dominio, mejorarÃ¡ la mantenibilidad y reducirÃ¡ errores de mapeo al usuario final.
- Centralizar las banderas de rol mantendrÃ¡ estable el login bajo ASGI y evitarÃ¡ regresiones en plantillas.
- Ajustar las polÃ­ticas de borrado (`PROTECT`/`CASCADE`) reducirÃ¡ los `IntegrityError` al gestionar asignaturas desde el admin.
- El comando de gestiÃ³n facilitarÃ¡ despliegues controlados y reproducibles del refactor, minimizando riesgo en producciÃ³n.

## ðŸ§¾ ConfirmaciÃ³n requerida
âš ï¸ No realices ningÃºn cambio en el cÃ³digo sin la aprobaciÃ³n explÃ­cita del usuario.
---
