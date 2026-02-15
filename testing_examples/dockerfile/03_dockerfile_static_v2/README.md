# Dockerfile Example: Static Landing v2

Ejemplo de una página web estática servida por **Nginx**.

## Archivos incluidos

- `index.html`: Página principal con HTML5, CSS interno y un pequeño script de JavaScript.
- `Dockerfile`: Usa la imagen base `nginx:alpine` para máxima ligereza y seguridad.

## Funcionalidad

Muestra una tarjeta de bienvenida y utiliza JavaScript para obtener la hora local del navegador al cargar. Es el ejemplo perfecto para probar despliegues rápidos de frontend.

## Cómo desplegar

1. Sube el `index.html` y el `Dockerfile`.
2. Al finalizar el "Building", accede a la URL para ver tu sitio estático en línea.
