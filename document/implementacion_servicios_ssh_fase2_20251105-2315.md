# Implementación — Servicios SSH Fase 2 (2025-11-05 23:15)

## 1. Alcance de la fase
1. Activar SSH por defecto sin intervención del usuario, reutilizando volúmenes persistentes `svc_{service_id}`.
2. Proporcionar credenciales gestionadas por la plataforma (usuario/contraseña) y exponer el comando a través del modal HTMX.
3. Garantizar la limpieza de recursos asociados al servicio (sidecar, puertos, volúmenes) al eliminar o reiniciar contenedores.

## 2. Acciones realizadas
1. Añadí el campo `ssh_password` al modelo `Service` (migración `0009`) para conservar la credencial generada automáticamente.
2. Implementé `_run_ssh_sidecar` con la imagen `linuxserver/openssh-server`, montando el volumen del servicio y reservando un puerto dinámico. Se genera una contraseña aleatoria (sin PEM) y se registra mediante `_append_log`.
3. Actualicé `ServiceViewSet.ssh_uri` para mostrar comando, usuario y contraseña (HTML/JSON) reutilizando el usuario configurable `SSH_USERNAME`.
4. Extendí `remove_container` para eliminar el sidecar, liberar el puerto SSH, desmontar el volumen y limpiar la contraseña.
5. Expuse los parámetros `SERVICE_SSH_IMAGE` y `SERVICE_SSH_USER` como variables de entorno opcionales y añadí una verificación en `scripts/run.sh` y `scripts/start.sh` para descargar automáticamente la imagen requerida en cada despliegue.

## 3. Archivos afectados
1. `containers/models.py` + `containers/migrations/0009_service_ssh_password.py` — nuevo campo `ssh_password`.
2. `containers/services.py` — generación de credenciales, sidecar real, helper `_append_log`, limpieza mejorada.
3. `containers/views.py` — modal SSH enriquecido y respuesta JSON consistente.
4. `templates/_service_rows.html` y alias en `templates/containers/` — botón SSH deshabilitado si no hay puerto asignado (heredado de Fase 1, verificación).

## 4. Verificación
1. Revisión manual del flujo `ServiceViewSet.ssh_uri` en modo HTMX para confirmar que el modal muestra comando y contraseña.
2. Validación estática de la migración (`python manage.py makemigrations --check` pendiente de ejecutar cuando Docker/DB estén disponibles).
3. No se ejecutaron pruebas automáticas por las limitaciones actuales de acceso al daemon Docker; queda programado para la Fase 3.

## 5. Riesgos y siguientes pasos
1. El sidecar depende de la imagen `linuxserver/openssh-server`; documentar en despliegues que debe estar accesible o pre-descargada.
2. Si Docker no permite mapear el volumen compartido (entornos restringidos), el modal indicará credenciales pero la conexión puede fallar; registrar bloqueos en `document/` cuando ocurra.
3. Fase 3 abordará la restauración de tests, comandos auxiliares y documentación adicional (`cambio_`, `testing_`) para cerrar el ciclo.
