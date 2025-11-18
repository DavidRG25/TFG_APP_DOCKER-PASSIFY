Analisis - Naming servicio (20251118-0015)

Problema
- Los recursos Docker (imagen, contenedor, volumen, sidecar) usan nombres genericos sin incluir el nombre del servicio del alumno, dificultando trazabilidad.
- No existia un slug controlado del campo service.name, por lo que los nombres no reflejan el servicio y podrian contener caracteres no seguros si se reutilizaban.

Causa tecnica
- _run_container_internal generaba nombres fijos `svc_<id>_image`, `svc_<id>_ctr`, `svc_<id>_data` y el sidecar usaba el username slug, no el nombre del servicio.
- No havia una rutina de normalizacion de service.name que garantizara solo [a-z0-9-_], ni colapsara guiones.

Objetivo de cambio
- Incorporar un slug seguro basado en service.name en todos los nombres Docker: imagen, contenedor, volumen y sidecar.
- Mantener compatibilidad con servicios ya creados (no sobrescribir volume_name existente).

Alcance previsto
- helpers de naming en containers/services.py
- rutas de sidecar y volumen en containers/services.py

Riesgos
- Servicios antiguos conservan volume_name previo; si se reinician y tenian volume_name vacio, adoptaran el nuevo nombre (se considera aceptable).
- Nombres mas largos podrian acercarse al limite de Docker (63 chars); se recorta en sidecar a 63 como antes.

Pruebas planificadas
- Crear servicio nuevo con nombre con espacios y caracteres especiales; verificar via docker inspect que los recursos usan slug limpio.
- Reiniciar servicio existente con volume_name ya asignado; debe conservar el nombre previo.
- Verificar sidecar usa el mismo prefix svc_<id>_<slug> y monta el volumen correspondiente.
