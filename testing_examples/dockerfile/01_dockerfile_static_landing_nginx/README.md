# 01 - Dockerfile (Landing estática)

## Qué valida este ejemplo
- Construcción de imagen con Dockerfile
- Servir una landing estática en Nginx
- Ejecución como usuario no root
- Healthcheck (/healthz)
- Cabeceras y cache básicas

## Comandos de prueba (local)
```bash
docker build -t paasify-landing:local .
docker run --rm -p 8080:8080 --name paasify-landing paasify-landing:local
```

### Verificaciones
- Abrir: http://localhost:8080
- Healthcheck: http://localhost:8080/healthz
- Revisar cabeceras (opcional):
```bash
curl -I http://localhost:8080
```

## Criterios de aceptación
- Responde 200 en `/` y `/healthz`
- Nginx escucha en 8080
- Contenedor corre como usuario no root
