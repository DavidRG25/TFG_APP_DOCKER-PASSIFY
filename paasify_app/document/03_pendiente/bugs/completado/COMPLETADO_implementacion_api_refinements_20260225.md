# Plan de Implementación: Refinamiento de API y Experiencia de Usuario (UI)

**Objetivo:** Implementar mejoras de calidad de vida, documentación y mantenimiento en la aplicación PaaSify, asegurando que la API esté correctamente documentada, el sistema se mantenga limpio de imágenes huérfanas y la interfaz gráfica proporcione feedback claro e inmediato.

---

## 🏗️ Fase 1: Documentación Profesional de API (Swagger / drf-spectacular)

Actualmente, las protecciones y comportamientos robustos de la API no están reflejados en la documentación interactiva provista por Swagger/ReDoc.

**Acciones a realizar:**

1. **Actualizar `containers/serializers.py`**:
   - Usar `@extend_schema_field` o decoradores equivalentes para explicar que el campo `name` es tolerante a espacios y fallos de formato.
2. **Actualizar `containers/views.py`**:
   - Importar `extend_schema` y `OpenApiResponse` de `drf_spectacular.utils`.
   - Decorar `create` (POST) indicando que soporta nombres flexibles.
   - Decorar `update` y `partial_update` (PATCH) indicando explícitamente que devolverán `400 Bad Request` si se intenta alterar el campo `mode`.
   - Decorar las acciones `@action` de `start`, `stop`, `restart` y `logs` para documentar sus códigos de respuesta (Ej: 200 OK, 404 No Encontrado, 500 Error de Docker).
3. **Autenticación en Swagger**:
   - Garantizar que la configuración de Swagger (en `settings.py` o vistas) indica que se usa `ExpiringToken` bajo el formato `Bearer <token>`.

---

## 🧹 Fase 2: Recolección de Basura (Limpieza de Imágenes Huérfanas)

Cuando un usuario elimina un Servicio que fue construido a partir de un código fuente (Dockerfile), la imagen subyacente (`svc_ID_slug_image`) se queda atascada ocupando megabytes/gigabytes en el disco duro del servidor host.

**Acciones a realizar:**

1. **Actualizar `containers/services.py`**:
   - En la función `_delete_service_internal(service: Service, docker_client)`, después de atrapar y borrar el contenedor (`container.remove(force=True)`).
   - Añadir lógica para verificar si `service.mode == 'custom'` o si existe `service.dockerfile`.
   - Ejecutar `docker_client.images.remove(image=service.image, force=True)` capturando y silenciando excepciones como `NotFound` o `ImageNotFound`.
   - Con esto, al pulsar la "papelera", la imagen generada localmente también se borrará, recuperando almacenamiento vital.

---

## 🔔 Fase 3: Notificaciones UI Dinámicas (Feedback Visual)

La aplicación usa HTMX / llamadas asíncronas para el inicio/parada/borrado. A veces los errores se muestran como un volcado de log, o cuesta apreciar que algo ha tenido éxito. Implementaremos un sistema global de alertas modernas no bloqueantes.

**Acciones a realizar:**

1. **Actualizar Plantilla Base / Dashboard UI (`base.html` o `dashboard.html`)**:
   - Incluir una librería ligera de notificaciones como **Toastr.js** o **SweetAlert2** vía CDN (o aprovechar Bootstrap Toasts si ya está configurado).
   - Inyectar un `<script>` que escuche los eventos de intercepción HTMX (`htmx:afterRequest` o `htmx:responseError`).
   - Si el estatus es 200/201, disparar un Pop-up verde: "✅ Acción completada con éxito".
   - Si el estatus es 4xx/5xx, disparar un Pop-up rojo capturando el mensaje de error para mostrar al usuario.
2. **Ajuste de Vistas HTMX**:
   - Asegurarnos que las respuestas enviadas por HTMX incluyan el mensaje de error parseable para las notificaciones.

---

## 🚀 Siguiente Paso

Una vez validado este plan, se comenzará a editar el código en Python y HTML para inyectar todas las propiedades. El Testing de estas funcionalidades está descrito en el documento `testing_plan_api_refinements.md`.
