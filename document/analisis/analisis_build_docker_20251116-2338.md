# Analisis — Build Docker (Fase C) - 20251116-2338

## Problemas detectados
1. Al crear un servicio con Dockerfile+ZIP el contenedor no se genera y no se registra ningun log de build.
2. /logs siempre responde "(sin logs)" cuando no existe container_id.
3. El boton "Dockerfile" no muestra contenido porque el archivo no esta guardado/confirma su ruta en MEDIA_ROOT.
4. La terminal muestra error _PipeSocket cuando el contenedor no existe.

## Causas probables
- _run_container_internal guarda los archivos en un directorio temporal, ejecuta docker build y solo registra logs en casos especificos. Si subprocess.run lanza CalledProcessError, se setea service.status="error" pero los logs no se anexan y el contenedor no se crea.
- /logs solo consulta Docker y no cae sobre service.logs cuando no hay container.
- _serve_code asume que el FileField esta almacenado; si se construyó desde un ZIP, la version final del Dockerfile se consume durante el build y no queda persistente.

## Plan de accion Fase C
1. **registro de logs**
   - Guardar stdout/stderr de docker build y anexarlos en service.logs tanto en exito como en error.
   - Si el build falla, marcar status="error" y abortar sin intentar correr el contenedor.
2. **endpoint /logs**
   - Si service.container_id es None, retornar service.logs para mostrar build/trazas.
3. **persistencia Dockerfile**
   - Mantener una copia del Dockerfile/Docker-compose en MEDIA_ROOT para que _serve_code lo muestre.
4. **terminal**
   - Deshabilitar la terminal cuando service.container_id sea None o no exista contenedor (ya se requiere running, pero reforzar la comprobacion).
5. **pruebas**
   - Dockerfile con error de sintaxis -> service.status=error y logs visibles.
   - Dockerfile correcto -> se genera la imagen, Dockerfile se visualiza y /logs muestra el historial.
