# Implementación — Servicios SSH Fase 1 (2025-11-05 23:00)

## 1. Alcance de la fase
1. Sustituir dependencias legacy (`Sport`, `enable_ssh`) en los módulos activos de contenedores.
2. Normalizar plantillas duplicadas (`templates/_service_rows.html` ↔ `templates/containers/_service_rows.html`, `student_panel.html`) para que sólo reflejen la UI vigente.
3. Restituir la compatibilidad del cliente Docker en entornos Windows/WSL eliminando llamadas `sudo`.

## 2. Acciones realizadas
1. Refactoricé `containers/views.py` para usar exclusivamente `Subject`/`subject__` en dashboards, detalle de asignaturas y proyectos.
2. Eliminé la lógica basada en `enable_ssh` en `containers/services.py` y añadí `_append_log` para mantener el histórico sin depender de campos obsoletos.
3. Sincronizé los partials HTMX de servicios, retirando el botón de conexión local y condicionando el botón SSH a `ssh_port`.
4. Reescribí `get_docker_client()` para que valide la conexión con `client.ping()` sin ejecutar `sudo docker ps`.
5. Documenté el plan maestro (`document/plan_mejoras_servicios_ssh_20251105.md`) con la estructura numerada acordada.

## 3. Archivos afectados
1. `containers/views.py` — queries y filtros actualizados a `Subject`.
2. `containers/services.py` — limpieza de `enable_ssh`, helper `_append_log`, placeholder controlado para sidecar.
3. `templates/_service_rows.html`, `templates/containers/_service_rows.html`, `templates/student_panel.html`, `templates/containers/student_panel.html` — UI consistente sin la opción legacy.
4. `containers/docker_client.py` — cliente multiplataforma sin llamadas privilegiadas.
5. `document/plan_mejoras_servicios_ssh_20251105.md` — formato estándar de planificación.

## 4. Verificación
1. Revisión manual de `git diff` para asegurar la ausencia de referencias a `Sport` fuera de migraciones/documentos históricos.
2. Comprobación de que las plantillas compiladas no contienen `enable_ssh` ni el bloque de “Conexión Local”.
3. Sin ejecución de tests automáticos (pendiente para fases siguientes) debido a las restricciones de Docker en el entorno actual.

## 5. Riesgos y siguientes pasos
1. El placeholder `_run_ssh_sidecar` todavía no habilita SSH; se abordará en la Fase 2 al definir la estrategia definitiva.
2. Es necesario restaurar la batería de tests y comandos (`create_test_user`, `add_allowed_image`) en la Fase 3.
3. Documentación técnica adicional (cambio/testing) se emitirá tras culminar las fases pendientes.
