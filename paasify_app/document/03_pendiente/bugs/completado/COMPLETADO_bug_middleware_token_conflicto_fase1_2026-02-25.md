# Bug: Conflicto entre TokenAuthMiddleware y SimpleJWT

**Fase de Prueba:** FASE 1: Autenticación y Seguridad

## Descripción

Al ejecutar el primer paso del plan de pruebas (Obtener Token mediante `/api/token/`), la API devuelve correctamente un token JWT (estado 200). Sin embargo, al intentar usar ese token `Bearer` en cualquier otro endpoint (como `/api/containers/`), el sistema devuelve un error `401 Unauthorized: "Token invalido o expirado"`.

## Causa Raíz

El `TokenAuthMiddleware` modificado el 18 de Enero intercepta **todas** las peticiones a `/api/` que empiezan por `Bearer ` e intenta buscar ese token exacto en la base de datos dentro del modelo `ExpiringToken`.
Como los tokens JWT generados en `/api/token/` no se guardan en la base de datos (son self-contained), el middleware explota bloqueando la petición y no deja que Django Rest Framework (DRF) procese el JWT.

Esto significa que `/api/token/` es actualmente inaccesible para la API porque ambas tecnologías (ExpiringToken y Simple JWT) usan la palabra clave `Bearer`.

## Soluciones Posibles

Se necesita aplicar una de las siguientes antes de poder continuar fluidamente con el Test de la API:

1. **(Recomendado)** Hacer que `TokenAuthMiddleware` derive a DRF si el token no tiene 40 caracteres. (Los tokens `ExpiringToken` siempre tienen 40 caracteres, mientras que los JWT tienen más de 200 caracteres).
2. Cambiar la cabecera esperada para el token de base de datos a `Token <clave>` o `Api-Key <clave>` en vez de `Bearer` en el Middleware.

He dejado el testeo pausado a la espera de que decidas cómo aplicar este fix.
