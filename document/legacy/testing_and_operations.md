# Pruebas, operaciones y recomendaciones

## Automatización existente
- `tests/test_containers.py` contiene pruebas integradas con Docker que verifican la unicidad de reservas de puertos y el ciclo completo `run → stop → remove` de los servicios. Estas pruebas requieren un daemon Docker accesible y un usuario `django_user_model` para crear servicios de prueba.
- Los módulos `containers/tests.py` y `security/tests.py` están vacíos, evidenciando áreas sin cobertura.
- No existe configuración de CI documentada; sería conveniente añadir workflows que lancen `pytest` y validen formato.

## Operaciones con Docker
- El módulo `containers/services.py` invoca Docker mediante la librería oficial y subprocessos (`docker build`, `docker compose`). Esto implica que el servidor debe contar con acceso al socket Docker y herramientas de línea de comandos instaladas.
- Las cargas de archivos (`dockerfile`, `compose`, `code`) se almacenan temporalmente en disco antes de construir o ejecutar contenedores.
- Los puertos se asignan dinámicamente dentro del rango 40000-50000, con posibilidad de puerto personalizado (`custom_port`) siempre que no esté reservado.

## Terminal WebSocket
- `containers/consumers.py` abre una shell interactiva `/bin/sh` y utiliza un hilo dedicado para reenviar la salida hacia el cliente vía WebSocket. Es fundamental proteger el acceso a este canal mediante autenticación y validaciones de propietario, tal como hace `get_object_or_404(Service, owner=user)`.

## Riesgos y mejoras sugeridas
1. **Configuración sensible en settings**: externalizar `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` a variables de entorno para despliegues reales.
2. **Manejo de archivos**: validar tamaño y tipo de `code` (ZIP) al subirlo, y limpiar directorios temporales tras ejecutar `docker compose` o builds fallidos.
3. **Resiliencia Docker**: capturar excepciones adicionales (`docker.errors.APIError`) al detener/eliminar contenedores para evitar estados inconsistentes.
4. **Cobertura de tests**: extender pruebas a serializadores, vistas y consumidores. Incluir tests unitarios para permisos sobre asignaturas y validación de modos catálogo/custom.
5. **App Security**: definir responsabilidades (por ejemplo, auditorías, reglas de contraseña, rate limiting) o considerar su eliminación hasta que exista funcionalidad concreta.

## Ejecución local recomendada
1. Crear entorno virtual y instalar dependencias (`pip install -r requirements.txt`).
2. Ejecutar migraciones (`python manage.py migrate`).
3. Arrancar servidor Django (`python manage.py runserver`) y, en paralelo, asegurar que Docker Desktop/Engine está activo.
4. Para probar la API, autenticarse en el panel y utilizar la vista de estudiante para crear servicios.
5. Ejecutar `pytest` con Docker disponible para validar la lógica de contenedores.
