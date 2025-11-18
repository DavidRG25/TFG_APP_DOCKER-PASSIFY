Implementacion - Naming servicio (20251118-0020)

Resumen
- Se introduce un slug seguro derivado de service.name (minusculas, solo [a-z0-9-_], reemplazo por -, colapso de multiples guiones).
- Los nombres Docker ahora incluyen el slug: imagen `svc_<id>_<slug>_image`, contenedor `svc_<id>_<slug>_ctr`, volumen `svc_<id>_<slug>_data`, sidecar `ssh_<id>_<slug>`.
- Compatibilidad: si un servicio ya tiene volume_name, se respeta y no se sobrescribe; el nuevo esquema aplica a servicios nuevos o sin volume_name previo.

Detalles tecnicos
- Nuevo helper `_service_slug(service)` en `containers/services.py` genera el slug seguro.
- _sidecar_name usa el slug del servicio en lugar del username.
- En `_run_container_internal`:
  - image_tag con slug: `svc_<id>_<slug>_image`.
  - Volumen persistente: si no existe, se crea `svc_<id>_<slug>_data` y se monta en `/data`.
  - Contenedor principal: nombre `svc_<id>_<slug>_ctr`.
  - Sidecar monta el mismo volumen en `/data`.

Compatibilidad y alcance
- volume_name existente se mantiene; solo si esta vacio se asigna el nuevo nombre.
- Compose no se toca; mantiene su naming actual.
- No se cambia la logica de montaje (/data) ni la eliminacion (usa service.volume_name).

Ficheros modificados
- containers/services.py

Comportamiento antes
- Nombres genericos sin el nombre del servicio, y sidecar basado en username.

Comportamiento despues
- Nombres trazables por servicio, con slug seguro y consistente para imagen, contenedor, volumen y sidecar.

Pruebas sugeridas
- Crear servicio con nombre "Mi Servicio 01": inspeccionar que imagen/cont/vol/sidecar usan `svc_<id>_mi-servicio-01_*`.
- Servicio antiguo con volume_name ya poblado: al arrancar no debe cambiar el nombre de volumen; sidecar levanta con ese volumen.
- Validar que el sidecar sigue montando `/data` y comparte volumen con el contenedor principal.
