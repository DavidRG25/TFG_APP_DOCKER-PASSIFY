# Compose Example: Node.js + MariaDB

Un ejemplo complejo que combina una base de datos relacional con una aplicación de backend personalizada.

## Componentes

- `app`: Aplicación Node.js (se construye usando `Dockerfile.node`).
- `db`: Base de datos **MariaDB** con credenciales preconfiguradas.

## Configuración

La aplicación Node.js está configurada para conectarse al host `db`. El `docker-compose.yml` define variables de entorno para inicializar la base de datos automáticamente.

## Archivos incluidos

- `app.js`: Servidor HTTP minimalista en Node.
- `Dockerfile.node`: Receta para construir el entorno Node.js.
- `docker-compose.yml`: El archivo de orquestación central.

## Cómo desplegar

1. Sube los tres archivos juntos.
2. Nota que este proceso puede tardar un poco más mientras se descarga la imagen de MariaDB y se construye la de Node.
3. Verifica los logs de la base de datos para asegurar el arranque exitoso del motor SQL.
