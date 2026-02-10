# Docker testing examples (para PaaSify / TFG)

Este directorio contiene 2 ejemplos "más complejos" para probar despliegues:

## 01_dockerfile_static_landing_nginx
Landing estática con Nginx:
- Non-root
- Healthcheck
- Cabeceras básicas
- Puerto 8080

## 02_compose_landing_flask_postgres
Docker Compose con aplicación web + base de datos:
- Flask + Gunicorn (web)
- Postgres (db)
- Volumen persistente
- Healthchecks y depends_on

Cada ejemplo incluye su propio README con comandos de prueba.
