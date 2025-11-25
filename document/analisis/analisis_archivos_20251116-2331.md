# Analisis — Manejo de archivos (Fase B) - 20251116-2331

## Problema
- Dockerfile y docker-compose no se guardan de forma fiable.
- El endpoint /api/containers/ devuelve 400 al subir archivos validos.
- No se generan logs de build ni se muestra el contenido de los archivos en la UI.

## Observaciones iniciales
1. Los campos FileField se asignan despues de serializer.save, por lo que si ocurre una excepcion los archivos no quedan asociados al servicio.
2. _save_filefield_to copia el Dockerfile a una carpeta temporal, pero no se guarda una copia persistente en MEDIA_ROOT.
3. _serve_code depende de que service.dockerfile exista; actualmente muchos servicios quedan con None y el boton falla.
4. El ZIP se descomprime en un directorio temporal, pero no se valida que contenga Dockerfile/docker-compose.

## Plan Fase B
1. **Persistencia de FileField**
   - Guardar dockerfile/compose/zip en MEDIA_ROOT antes de iniciar el build. Comprobar que service.dockerfile.path exista.
2. **Validacion del ZIP**
   - Verificar que el archivo contenga al menos el Dockerfile/compose requerido, o actualizar instrucciones para que el usuario los incluya.
3. **End points y logs**
   - Ajustar /logs para devolver service.logs si no existe contenedor.
   - Asegurar que _run_container_internal llena service.logs con el resultado del build.
4. **UI Dockerfile**
   - Confirmar que el boton abre un modal incluso si el archivo se cargó desde ZIP (leer desde MEDIA_ROOT).

Este analisis servira como guia antes de las implementaciones en Fase B.
