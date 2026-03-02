# Plan de Testing: Nuevos Ejemplos Docker (Mega Stack) - COMPLETADO ✅

- **Estado:** Finalizado
- **Fecha:** 2026-02-15

Este documento sirve para validar manualmente que los nuevos ejemplos funcionan correctamente en PaaSify.

## 1. Validación de Dockerfile (Modo Simple)

- [SI] Subida de ZIP con Dockerfile.
- [SI] Despliegue correcto.
- [SI] Puerto asignado funcional.

## 2. Validación de Docker Compose (Mega Stack)

- [SI] Subida de ZIP con docker-compose.yml.
- [SI] Detección de múltiples servicios (4 contenedores).
- [SI] Comunicación Postgres <-> API.
- [SI] Comunicación Redis <-> API.
- [SI] Nginx actuando como Proxy.

## 3. Logs y Pipeline

- [SI] Los logs muestran el flujo de datos.
- [SI] Los logs de cada contenedor son accesibles.

### [SI] Filtrado

- [SI] El filtro "Últimos 5 min" oculta logs antiguos.
- [SI] El filtrado por texto (ej: "Running") funciona con el nuevo formato.
- [SI] Los logs de sistema aparecen marcados como `[SISTEMA]` en caso de error.
