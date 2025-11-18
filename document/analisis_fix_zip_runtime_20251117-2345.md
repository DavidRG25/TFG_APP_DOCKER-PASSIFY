Analisis - Fix zip runtime (20251117-2345)

Problema
- El ZIP de codigo se montaba como volumen en runtime sobre /app, provocando errores de arranque (mount not a directory) y estados false positives en running.
- Imagen, contenedor y volumen usaban nombres dispares sin prefijo comun.
- El boton Dockerfile dependia de que el archivo se hubiera guardado; cuando fallaba el build no habia forma de servirlo.

Causa tecnica
- En _run_container_internal se anadia service.code.path al diccionario volumes y se fijaba working_dir=/app, pese a que el ZIP solo debia usarse en el build.
- Los nombres se generaban con patrones diferentes (volume_name=svc_<id>, container=name por usuario, image_tag gratuito).
- La persistencia montaba /home/user/data en lugar de un punto fijo.

Alcance de cambio propuesto
- Runtime sin ZIP: solo volumen persistente fijo y user_vols.
- Coherencia de nombres: svc_<id>_image, svc_<id>_ctr, svc_<id>_data.
- Ajuste del sidecar para usar el mismo volumen montado en /data.
- Confirmar que Dockerfile se guarda antes del build y que la vista para servirlo mantiene fallback.

Riesgos
- Cambios de naming pueden dejar volumenes viejos sin limpiar; remove_container sigue borrando el volume_name guardado, pero no toca los historicos con el nombre antiguo.
- Servicios existentes en running con naming previo deberan reiniciarse para adoptar el nuevo nombre.

Pruebas previstas
- Crear servicio con Dockerfile+ZIP: build debe usar ZIP como contexto y contenedor debe arrancar montando solo /data.
- Inspeccionar contenedor: nombre svc_<id>_ctr, volumen svc_<id>_data montado en /data, sin bind a /app.
- Caso sin code: contenedor arranca con volumen vacio /data, sin /app bind.
- Boton Dockerfile: modal muestra contenido o mensaje "(archivo no disponible)" si falta.
