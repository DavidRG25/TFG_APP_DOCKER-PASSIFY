Implementacion - Mini ajustes rar tool (20251118-0210)

Problema
- La descompresion de RAR fallaba con errores de lectura parcial (req=200 got=124) por lectura en memoria y falta de herramienta externa.

Solucion aplicada
- Se elimina el uso de rarfile para extraer; ahora se guarda el RAR en disco y se llama a la herramienta externa definida en UNRAR_TOOL_PATH con comandos `t` (test) y `x` (extract) entrecomillados.
- Si UNRAR_TOOL_PATH no esta definido o apunta a una ruta inexistente se lanza un error claro; si el RAR esta danado se devuelve mensaje explicitando que esta danado o incompleto.
- Se elevan los limites de subida en Django a 50 MB para evitar recortes de archivo.

Archivos modificados
- containers/services.py
- app_passify/settings.py

Notas de configuracion
- Define en tu entorno (o .env) la ruta al ejecutable: `UNRAR_TOOL_PATH="C:\\Program Files\\7-Zip\\7z.exe"` (ajusta segun tu instalacion).
- Instala 7-Zip/unrar y asegurate de que el binario existe.

Pruebas sugeridas
- Subir RAR valido con Dockerfile: debe testear y extraer sin errores.
- Subir RAR danado: debe mostrar mensaje claro de archivo danado o incompleto.
- Subir ZIP: sigue funcionando con shutil.unpack_archive.
