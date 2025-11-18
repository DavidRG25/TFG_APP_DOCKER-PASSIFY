Implementacion - Soporte zip rar (20251118-0135)

Problema
- Solo se aceptaba ZIP como codigo fuente; alumnos suben RAR y fallaba la creacion de servicio.

Motivo del cambio
- Permitir ZIP y RAR tanto en validacion como en extraccion del archivo de codigo.

Validacion actualizada
- Mensaje de error en serializer: "Debes adjuntar un archivo .zip o .rar con el codigo fuente."

Cambios en serializer
- `containers/serializers.py`: valida duplicados por alumno y ahora exige zip o rar con el nuevo mensaje cuando usa Dockerfile/compose.

Cambios en service
- `containers/services.py`: CODE_EXTENSIONS incluye .zip y .rar; nueva rutina `_unpack_code_archive_to` que usa `rarfile` para RAR y `shutil.unpack_archive` para ZIP; errores amigables si falta rarfile o falla la extraccion.
- `requirements.txt`: se anade `rarfile==4.2`.

Frontend
- `templates/containers/student_panel.html`: input de codigo acepta `.zip,.rar`.

Manejo de rarfile
- Se importa bajo demanda; si no esta instalado se lanza `RuntimeError` indicando que falta `rarfile`.

Pruebas manuales sugeridas
- ZIP valido: crear servicio con Dockerfile+ZIP y comprobar build OK.
- RAR valido: crear servicio con Dockerfile+RAR y comprobar build OK.
- Archivo incorrecto (ej. .7z): debe fallar validacion de extension.
- Dockerfile+RAR y compose+RAR: debe construir y arrancar si los archivos son correctos.
