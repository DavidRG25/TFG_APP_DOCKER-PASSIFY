---
# Análisis de Código — Rama: feature/analisis-codigo
**Resumen:** Evaluación del alcance del renombrado de Sport a Subject, revisando dependencias de modelos, admin y pruebas.
## 🧩 Objetivo
Revisar el impacto del renombrado global de "Sport" a "Subject" en modelos, admin, vistas y pruebas, validando las dependencias actuales y el flujo de creación de alumnos tras las últimas correcciones de login.

## 📂 Archivos revisados
- `paasify/models/SportModel.py`
- `paasify/models/ProjectModel.py`
- `paasify/models/StudentModel.py`
- `paasify/admin.py`
- `containers/views.py`
- `containers/serializers.py`
- `tests/test_containers.py`
- `templates/base.html`
- Migraciones iniciales (`paasify/migrations/0001_initial.py`)

## ⚠️ Problemas detectados
1. **Dependencias directas del modelo `Sport`:** El modelo `Game` (proyectos) y múltiples vistas/serializadores importan `Sport` con rutas absolutas (`from paasify.models.SportModel import Sport`). Cualquier renombrado requiere actualizar imports, `related_name`, `verbose_name` y el `db_table` (`sport`).
2. **Integridad referencial en proyectos:** `Game.sport` mantiene `on_delete=models.DO_NOTHING`, de modo que borrar una asignatura seguirá provocando `IntegrityError`. El renombrado no resolverá este comportamiento; habrá que replantear la política de borrado o documentar el uso de `PROTECT`/`CASCADE` según el dominio.
3. **Contexto de plantillas/login:** El login ahora depende de banderas `is_student`, `is_teacher`, `is_admin` calculadas en `SecurityViews.login`. Cualquier refactor debe preservar estas claves en el contexto para evitar el `TemplateSyntaxError` observado con Daphne.
4. **Fixtures y pruebas:** `tests/test_containers.py` y el serializer de servicios referencian `Sport` tanto en consultas como en fixtures; un renombrado exige modificar los datos de prueba y las etiquetas HTMX que filtran por `subject_id`.
5. **Migrations y compatibilidad:** La migración `0001_initial` crea la tabla `sport`. Renombrarla a `subject` en código sin migración de datos rompería la carga de modelos. Hay que emitir una migración que renombre tabla y constraint, o mantener `db_table="sport"` para compatibilidad.
6. **Comandos administrativos:** No existe un `management command` que sincronice renombrados. La operación manual sobre producción podría dejar entradas huérfanas si no se automatiza.

## 💡 Propuestas de solución
1. **Plan de renombrado en capas:**
   - Crear `paasify/models/SubjectModel.py` con clase `Subject` derivada de `Sport`, reutilizando `db_table="sport"` para evitar migración inmediata; luego refactorizar imports progresivamente.
   - Actualizar `paasify/models/__init__.py`, vistas, serializers y admin para usar `Subject`.
   - Generar migración que use `migrations.RenameModel` y `migrations.RenameField` si se desea cambiar el nombre en la base de datos (o mantener `db_table` temporalmente).
2. **Revisar on_delete y related_name:** Evaluar cambiar `Game.sport.on_delete` a `models.PROTECT` y renombrar `related_name` a `projects` → `subject_projects` para mayor claridad. Documentar cualquier cambio en el informe de implementación.
3. **Context processor/roles:** Consolidar la lógica de banderas en un procesador de contexto (`paasify/context_processors.py`) para que todas las plantillas mantengan `is_student`/`is_teacher`/`is_admin`, evitando dependencias en vistas individuales.
4. **Comando de gestión opcional:** Implementar `python manage.py rename_sport_to_subject` que:
   - Actualice referencias textuales en la base de datos (si procede) y sincronice grupos/relaciones.
   - Verifique integridad tras el renombrado (contar asignaturas, proyectos y servicios vinculados).
5. **Actualizar documentación y fixtures:** Revisar `README.md`, `tests/test_containers.py` y cualquier fixture que use `sport`/`sports`, reemplazando por `subject`/`subjects` para mantener coherencia funcional.

## 🧠 Impacto estimado
- El renombrado coherente eliminará ambigüedades de dominio, mejorará la mantenibilidad y reducirá errores de mapeo al usuario final.
- Centralizar las banderas de rol mantendrá estable el login bajo ASGI y evitará regresiones en plantillas.
- Ajustar las políticas de borrado (`PROTECT`/`CASCADE`) reducirá los `IntegrityError` al gestionar asignaturas desde el admin.
- El comando de gestión facilitará despliegues controlados y reproducibles del refactor, minimizando riesgo en producción.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.
---