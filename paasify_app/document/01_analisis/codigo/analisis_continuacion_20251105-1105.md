# Continuación Codex Análisis — 2025-11-05 11:05

1. **Resumen Ejecutivo**
   - No se encontró la migración `0031_alter_userproject_time`; el modelo `UserProject` ya espera el nuevo default y dejarla pendiente mantiene inconsistencias entre código y base de datos.
   - La señal `sync_profile_on_group_change` sigue alineada con `UserProfile`, pero el módulo `containers/views.py` arrastra duplicaciones completas de helpers y vistas que complican el mantenimiento y pueden introducir regresiones sutiles.
   - El ruteo principal (login, panel estudiante/profesor) funciona con los nuevos nombres, aunque falta una derogación explícita para superusuarios en las vistas orientadas a alumnos.

2. **Cambios o migraciones recientes detectadas**
   - Última migración registrada en el repositorio: renombrado `0030_rename_player_game.py`, que consolida `UserProfile`/`UserProject` (paasify/migrations/0030_rename_player_game.py:1).
   - El modelo `UserProject` ya depende de `UserProfile` mediante `ForeignKey` y mantiene el ordenamiento por fecha y hora descendente (paasify/models/ProjectModel.py:14, paasify/models/ProjectModel.py:34).
   - No existe archivo `0031_alter_userproject_time.py`, a pesar de que el modelo define `time = models.TimeField(default=datetime.now)` (paasify/models/ProjectModel.py:27), por lo que `makemigrations` volverá a detectar un cambio pendiente.

3. **Análisis de consistencia y dependencias**
   - La señal `sync_profile_on_group_change` continúa invocando `ensure_user_profile` tras cada adhesión al grupo de alumnos y ambos apuntan a los nuevos modelos (`UserProfile`) sin dependencias circulares detectadas (paasify/signals.py:14, paasify/roles.py:59).
   - `student_services_in_subject` redirige a profesores, pero devuelve 403 a superusuarios que no estén matriculados, impidiendo verificaciones administrativas rápidas (containers/views.py:369, containers/views.py:374).
   - El archivo `containers/views.py` quedó con tres copias idénticas de los helpers `user_is_student/user_is_teacher` y de las vistas de detalle del profesor; aunque la última definición prevalece, la duplicidad multiplica los puntos de edición y puede causar divergencias futuramente (containers/views.py:59, containers/views.py:67, containers/views.py:75, containers/views.py:470, containers/views.py:521, containers/views.py:572).
   - Servicios auxiliares heredan las nuevas FK (`subject.projects`, `user_profile.projects`) y se renderizan en los templates correspondientes (`professor/subject_detail.html`, `professor/project_detail.html`), por lo que la integración de `UserProject` en los paneles es consistente.

4. **Pruebas simuladas (login, vistas, contenedores)**
   - **Login**: autenticar con un alumno y validar que `post_login` redirige a `containers:student_subjects`, comprobando que las banderas de contexto `nav_is_*` habilitan el menú correcto.
   - **Panel alumno**: crear/recargar servicios vía HTMX (`service-start`, `service-stop`, `service-remove`) y revisar que se disparen los toasts y se refresque `#service-table`.
   - **Panel profesor**: autenticar con un profesor asignado y navegar a `professor_dashboard`, `professor_subject_detail` y `professor_project_detail` verificando la presencia de proyectos y servicios relacionados.
   - **Terminal WebSocket**: abrir la terminal desde un servicio en ejecución y confirmar la conexión WS vía Channels.
   - No se ejecutaron pruebas automáticas (pytest, manage.py) porque la sandbox actual es de solo lectura y el pipeline depende de Docker en tiempo de ejecución.

5. **Errores o advertencias detectadas**
   - **Alta** – Falta aplicar/commitear la migración que acompaña al nuevo default de `UserProject.time`; `makemigrations` generará `0031_alter_userproject_time.py` para alinear el modelo con la base (paasify/models/ProjectModel.py:27, paasify/migrations/0030_rename_player_game.py:1).
   - **Media** – `student_services_in_subject` debería permitir bypass para superusuarios o al menos mostrar un mensaje contextualizado para auditoría (containers/views.py:369, containers/views.py:374).
   - **Media** – Duplicaciones de helpers y vistas en `containers/views.py` (containers/views.py:59, containers/views.py:67, containers/views.py:75, containers/views.py:470, containers/views.py:521, containers/views.py:572) elevan el riesgo de modificaciones incoherentes.
   - **Media** – Constantes `MAX_UPLOAD_SIZE` y conjuntos de extensiones se declararon tres veces en `containers/services.py`, dificultando ajustes futuros y generando falsas diferencias en revisiones (containers/services.py:16, containers/services.py:20, containers/services.py:24).
   - **Baja** – Las representaciones `__str__` de `UserProject`, `UserProfile` y `Service` contienen el glifo `�`, probablemente producto de una conversión de encoding; conviene reemplazarlo por separadores visibles (`→`, `|`, etc.) para evitar artefactos en Django Admin (paasify/models/ProjectModel.py:37, paasify/models/StudentModel.py:39, containers/models.py:110).

6. **Plan de corrección priorizado (Alta, Media, Baja)**
   - **Alta**
     1. Generar y aplicar `0031_alter_userproject_time` para actualizar el default del campo `time`, utilizando una función timezone-aware (`timezone.localtime().time()`) y verificar migraciones pendientes con `python manage.py makemigrations` / `migrate`.
   - **Media**
     1. Consolidar los helpers y vistas duplicados en `containers/views.py`, garantizando que solo exista una definición por función y añadiendo pruebas unitarias mínimas para el flujo profesor/alumno.
     2. Ajustar `student_services_in_subject` para permitir lectura por superusuarios (o ruta de soporte) sin exigir matriculación, manteniendo la redirección para profesores.
     3. Unificar las constantes de tamaño/extensiones en `containers/services.py` en una única sección para evitar divergencias.
   - **Baja**
     1. Sustituir el glifo `�` en las cadenas `__str__` por separadores legibles y verificar la visualización en el admin y plantillas asociadas.
\n- [2025-11-05] Se agregaron scripts scripts/start.sh y scripts/run.sh para facilitar el inicio con Daphne y runserver local; recuerdan exportar DJANGO_SECRET_KEY cuando se use start.sh.
