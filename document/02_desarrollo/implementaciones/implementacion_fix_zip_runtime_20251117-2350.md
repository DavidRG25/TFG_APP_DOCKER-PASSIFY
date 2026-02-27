Implementacion - Fix zip runtime (20251117-2350)

Problema
- El ZIP subido por el alumno se montaba en runtime sobre /app, causando errores OCI al no ser un directorio y dejando el servicio marcado como running aunque el contenedor fallara.
- Los recursos Docker no seguian un naming consistente (imagen, contenedor, volumen).
- El sidecar montaba /home/.../data en lugar de compartir el punto unico del volumen persistente.

Solucion aplicada
1) Runtime sin ZIP
   - Eliminado el bind mount del ZIP en _run_container_internal; el ZIP solo se usa en build si existe.
2) Nombres coherentes
   - Imagen: svc_<id>_image
   - Contenedor: svc_<id>_ctr
   - Volumen persistente: svc_<id>_data
3) Punto de montaje unico
   - Volumen persistente montado en /data tanto para el contenedor principal como para el sidecar SSH.
4) Working dir
   - Eliminado working_dir=/app al no montarse codigo en runtime.

Ficheros modificados
- containers/services.py

Codigo relevante (fragmentos)
- Runtime volumes: solo volumen persistente /data, sin service.code.bind.
- Docker build: image_tag = f"svc_{service.id}_image"; contenedor name f"svc_{service.id}_ctr"; volume_name f"svc_{service.id}_data".
- Sidecar: monta volume_name en /data.

Flujo antes
- Build con Dockerfile usaba ZIP como contexto, pero en runtime montaba el propio ZIP en /app y fijaba working_dir=/app; nombres heterogeneos.

Flujo despues
- Build usa el ZIP descomprimido como contexto y guarda la imagen svc_<id>_image.
- Runtime arranca contenedor svc_<id>_ctr con volumen svc_<id>_data en /data, sin bind del ZIP.
- Sidecar comparte el mismo volumen en /data.

Pruebas sugeridas
- Crear servicio con Dockerfile+ZIP: debe construir y arrancar; `docker inspect svc_<id>_ctr` muestra mount /data -> svc_<id>_data, sin /app.
- Caso sin ZIP: contenedor arranca, monto /data, sin fallos de mount.
- Boton Dockerfile: modal devuelve contenido si existe o "(archivo no disponible)" si no.
