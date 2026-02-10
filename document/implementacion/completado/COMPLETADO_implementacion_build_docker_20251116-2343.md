# Implementacion — Fase C Build Docker (20251116-2343)

## Problema
- Los builds con Dockerfile no guardaban la salida de docker build, por lo que no habia logs accesibles.
- Cuando el build fallaba, el servicio quedaba en estado ERROR pero sin detalle.
- El modal "Logs" consultaba solo los contenedores, devolviendo "(sin logs)" si no habia container_id.

## Cambios aplicados
1. containers/services.py
   - Captura stdout y stderr de docker build tanto en exito como en error. Los logs se almacenan en service.logs y se marcan los estados con update_fields.
2. containers/views.py::logs
   - Si no existe contenedor, devuelve service.logs como fallback para mostrar el historial de build.
3. Documentacion: document/analisis_build_docker_*.md y document/implementacion_build_docker_*.md se agregan al historial.

## Flujo antes/despues
- *Antes*: un Dockerfile invalido dejaba el servicio en ERROR pero el modal mostraba "(sin logs)".
- *Despues*: los logs de docker build se guardan y se muestran a traves del modal, aun cuando no se creo contenedor.

## Seguridad
- Los logs se guardan como texto plano en BD; revisar tamanos si se vuelven muy grandes.

## Pruebas
- [ ] Dockerfile con error -> logs del build visibles.
- [ ] Dockerfile correcto -> modal muestra la salida del build.
- [ ] Endpoint /logs sin contenedor debe devolver service.logs.
