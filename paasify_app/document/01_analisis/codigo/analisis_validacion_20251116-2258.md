# Analisis y Validacion de servicios (20251116-2258)

## Problema
- La opcion de despliegue personalizado no detecta los ficheros Dockerfile/compose y responde con 400 gen�rico.
- Se crean servicios en estado `ERROR` sin logs ni archivos asociados, dejando al alumno sin feedback.
- Falta una regla que obligue a adjuntar el ZIP de codigo cuando se usa Dockerfile/docker-compose.
- No existen mensajes informativos ni instrucciones en la UI sobre como preparar los archivos requeridos.

## Causas probables
1. **Restricciones de entrada**: el campo `<input type="file">` tiene `accept=".dockerfile,.Dockerfile,.txt"`, lo que impide seleccionar ficheros llamados simplemente `Dockerfile` (sin extension) en Windows.
2. **Serializer insuficiente**: `ServiceSerializer.validate` solo comprueba la presencia de Dockerfile/compose, pero no exige `code`. El 400 proviene de `ValidationError` no gestionada.
3. **Vista HTMX**: `ServiceViewSet.create` no captura `ValidationError` para devolver feedback en el formulario; HTMX muestra pagina vacia.
4. **Persistencia de archivos**: los `FileField` se asignan despues de `serializer.save` y, si ocurre un error, el servicio queda sin Dockerfile/compose registrados.
5. **Logs**: `_run_container_internal` no guarda la salida de `docker build` cuando falla y `/logs` solo consulta `container_id`, por eso el modal dice �(sin logs)�.
6. **Bot�n Dockerfile**: al no haberse guardado el `FileField`, `_serve_code` lanza `Http404` y la UI no muestra nada.

## Plan de accion (Fase A)
1. **Validaciones en serializer**
   - En modo custom: exigir `code` y exactamente uno entre `dockerfile`/`compose`.
   - Normalizar mensajes por campo (`{"dockerfile": "..."}`) para mostrarlos en el formulario.
2. **Vista `ServiceViewSet.create`**
   - Capturar `ValidationError` y, si viene de HTMX, renderizar un fragmento con alertas en lugar de 400 generico.
   - Mover la asignacion de `service.dockerfile|compose|code` antes de guardar o asegurarse de que se persistan aunque falle el build.
3. **Formulario HTMX**
   - Ajustar `accept` para permitir seleccionar Dockerfile sin extension (`accept=".dockerfile,.txt,text/plain,*/*"`).
   - A�adir indicadores de error junto a cada campo y descripciones cuando falte el ZIP.
4. **UX**
   - Incorporar iconos y con instrucciones (contenido minimo del Dockerfile, requisitos del ZIP, etc.).
5. **Testing previsto**
   - Crear servicio con Dockerfile + ZIP ? deberia validar y crear.
   - Intentar Dockerfile sin ZIP ? mostrar error inmediato en modal.
   - Enviar ZIP sin Dockerfile/compose ? error controlado.

Este analisis servira como guia para la implementacion de la Fase A antes de pasar a las siguientes.
