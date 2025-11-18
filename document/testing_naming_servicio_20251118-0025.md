Testing - Naming servicio (20251118-0025)

Objetivo
Validar que el nuevo esquema de nombres Docker usa el slug del servicio y que se mantiene la compatibilidad con servicios previos.

Casos
1) Servicio nuevo con nombre complejo
   - Crear servicio con nombre "Servicio Nuevo 123 !".
   - Esperado: imagen `svc_<id>_servicio-nuevo-123_image`, contenedor `svc_<id>_servicio-nuevo-123_ctr`, volumen `svc_<id>_servicio-nuevo-123_data`.
   - Sidecar: `ssh_<id>_servicio-nuevo-123` montando `/data`.
   - Verificar `docker inspect` muestra el mount `/data` -> volumen indicado.

2) Servicio antiguo con volume_name ya guardado
   - Tomar un servicio que ya tenga volume_name distinto de null.
   - Arrancar: debe conservar el mismo volume_name; no debe recrearse con el nuevo slug.
   - Sidecar debe montar el volume_name existente en `/data`.

3) Servicio sin ZIP en runtime
   - Confirmar que no se montan rutas de ZIP en contenedor ni sidecar; solo `/data` y los user_vols.

4) Limpieza y limites
   - Revisar que los nombres no contienen caracteres fuera de [a-z0-9-_] y no hay guiones duplicados.

Notas
- Compose sigue con el naming actual (project compose), fuera del alcance.
- Si se reinicia un servicio con volume_name vacio, adoptara el nuevo naming basado en slug (comportamiento esperado).
