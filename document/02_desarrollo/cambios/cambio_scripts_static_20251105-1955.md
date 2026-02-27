# Cambio — Scripts ejecutan collectstatic automáticamente (2025-11-05 19:55)

## Alcance
- `scripts/run.sh`: añade `python manage.py collectstatic --noinput` tras las migraciones para evitar el warning de `STATIC_ROOT` en desarrollo.
- `scripts/start.sh`: ejecuta `migrate` y `collectstatic` antes de arrancar Daphne en entornos de despliegue.

## Observaciones
- Se mantiene la carga previa de `.env` para respetar la configuración de cada entorno.
- El comando `collectstatic` no requiere intervención (`--noinput`), por lo que los scripts siguen siendo non-interactive.

## Próximos pasos
- Si se personaliza `STATIC_ROOT`, verificar que la ruta exista o que el entorno tenga permisos de escritura antes de ejecutar los scripts.
