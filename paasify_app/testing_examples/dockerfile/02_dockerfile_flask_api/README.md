# Dockerfile Example: Flask API

Este ejemplo demuestra cómo desplegar una aplicación **Python Flask** sencilla en PaaSify.

## Archivos incluidos

- `app.py`: El código de la aplicación.
- `requirements.txt`: Dependencias necesarias (Flask).
- `Dockerfile`: Configuración para construir la imagen.

## Funcionalidad

La app expone una API en el puerto 5000:

- `/`: Información general del sistema.
- `/health`: Endpoint de salud para monitoreo.

## Cómo desplegar

1. Crea un nuevo servicio en PaaSify.
2. Selecciona el modo **Dockerfile**.
3. Sube los tres archivos de esta carpeta.
4. PaaSify instalará las dependencias automáticamente y levantará el servicio.
