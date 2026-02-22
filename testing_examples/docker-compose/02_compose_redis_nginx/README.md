# Compose Example: Redis + Nginx

Este ejemplo muestra un despliegue multi-contenedor usando **Docker Compose**.

## Componentes

- `web`: Un servidor Nginx Alpine.
- `worker`: Un servicio de base de datos en memoria Redis.

## Qué probar

Este ejemplo es ideal para verificar:

1. La creación de múltiples registros en la base de datos de PaaSify bajo un mismo servicio padre.
2. La visualización de logs independientes por cada contenedor del stack.
3. El estado agregado del servicio (2/2 funcionando).

## Cómo desplegar

1. Sube el archivo `docker-compose.yml`.
2. Observa cómo PaaSify orquestra ambos contenedores simultáneamente.
