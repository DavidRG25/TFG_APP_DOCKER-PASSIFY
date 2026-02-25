# Recopilación de Bugs API (Testing Exhaustivo 25/02/2026)

Durante la ejecución del Plan de Testing de la API Completo (`testing_plan_api_comprehensive.md`), se han documentado y/o solucionado los siguientes fallos de seguridad o lógica:

## 🐛 1. Bug: Conflicto de Middleware vs JWT

- **Estado:** ✅ Solucionado (Eliminado del sistema)
- **Fase Encontrado:** Fase 1 (Autenticación)
- **Descripción:** El plan y los tests originales usaban JWT puro. Sin embargo, en actualizaciones pasadas la app añadió el `TokenAuthMiddleware` estricto que solo acepta `ExpiringToken` (40 caracteres). Mandar el token JWT original generaba un error `401 Unauthorized` constante para el endpoint de `/containers/`.
- **Solución Aplicada:** Se limpiaron las dependencias de `rest_framework_simplejwt` de URLs y Configuración. Se unificó el sistema forzando el uso exclusivo del token de desarrollador moderno creado en enero para todas las peticiones API.

## 🐛 2. Bug: Logs 500 TypeError de 'since'

- **Estado:** ✅ Solucionado
- **Fase Encontrado:** Fase 5 (Control de Estado - GET /logs/)
- **Descripción:** Al solicitar los logs de un contenedor a través de la API `containers/ID/logs/?since=xxx`, el servidor respondía con error `500 Internal Server Error`.
- **Causa:** En `containers/views.py` había una colisión de nombres de importación. Estaba importando la versión acotada de `fetch_container_logs` desde `containers.services` en lugar de la versión mejorada desde `containers.utils` que soporta el argumento `since=`.
- **Solución Aplicada:** Corregido el `import` en `views.py`.

## 🐛 3. Bug: Nombres con Espacios Permitidos (POST)

- **Estado:** ✅ Solucionado (Considerado Feature Seguro)
- **Fase Encontrado:** Fase 3 (Creación de Servicios)
- **Descripción:** Si se envía una petición `POST` con `"name": "Mi App Invalida"`, en lugar de rechazarla (`400 Bad Request`), la API devuelve un código `201 Created` y guarda el servicio en la base de datos.
- **Riesgo:** Originalmente se pensó que Docker daría fallo al recibir nombres con espacios, pero el backend gestiona la transposición convirtiendo espacios a guiones bajos de forma oculta (`mi_app_espacios_...`). Por lo tanto, no es un error sino una capa de resiliencia exitosa de la aplicación que previene fallos ante inputs humanos.

## 🐛 4. Bug: Alteración del Campo 'Mode' en Caliente (PATCH)

- **Estado:** ✅ Solucionado
- **Fase Encontrado:** Fase 4 (Modificación PATCH)
- **Descripción:** Si en la API envías un `PATCH` modificando el valor `"mode": "custom"` a un servicio que originalmente fue creado como `"dockerhub"`, el sistema lo permite (devuelve `200 OK`) silenciosamente.
- **Solución Aplicada:** Añadido un blindaje explícito en el `update()` del `ServiceSerializer`. Si un atacante intenta inyectar `"mode": "custom"` a un contenedor de DockerHub, se lanza un `400 Bad Request` indicando: _"No se puede cambiar el modo constructivo de un servicio existente."_
