# 02 - Docker Compose (Landing + Postgres con persistencia)

## Qué valida este ejemplo
- Orquestación de servicios con docker-compose
- Dependencias y healthchecks (web espera a db)
- Persistencia con volumen (los mensajes no se pierden)
- Healthcheck del servicio web (/healthz) y del Postgres

## Arranque
```bash
docker compose up --build
```

## Uso
- Web: http://localhost:8081
- Guarda mensajes con el formulario

## Prueba de persistencia (importante)
1) Guarda 2-3 mensajes.
2) Para todo:
```bash
docker compose down
```
3) Vuelve a levantar:
```bash
docker compose up
```
4) Los mensajes deben seguir estando.

## Limpieza total (borra datos)
```bash
docker compose down -v
```
