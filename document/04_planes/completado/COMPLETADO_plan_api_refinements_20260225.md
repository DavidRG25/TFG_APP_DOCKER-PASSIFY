# Plan Maestro: Refinamiento de API y Experiencia de Usuario (UI)

**Objetivo:** Implementar mejoras de calidad de vida, documentación y mantenimiento en la aplicación PaaSify, asegurando que la API esté correctamente documentada, el sistema se mantenga limpio de imágenes huérfanas y la interfaz gráfica proporcione feedback claro e inmediato.

Este plan detalla las funcionalidades de pulido que se han conceptualizado y desarrollado en la versión 8.3 de PaaSify.

---

## 🏗️ Fase 1: Documentación Profesional de API (Swagger / drf-spectacular)

**Problema:** Las protecciones robustas de la API (saneamiento de nombres, bloqueos en PATCH de campos inmutables) implementadas recientemente no estaban reflejadas en nuestra documentación auto-generada Swagger UI ni en el ReDoc, dejando a los desarrolladores de Frontend o integradores a ciegas.

**Estrategia de Desarrollo:**

- **Serializadores (`containers/serializers.py`)**: Añadir soporte de `help_text` inyectando descripciones precisas dentro de los campos sensibles (`name`, `mode`) explicando sus tolerancias y bloqueos de seguridad anti-edición.
- **Controladores (`containers/views.py`)**: Utilizar el decorador especializado `@extend_schema` de la librería `drf-spectacular`. Se documentarán específicamente las rutas de acción custom (`/start`, `/stop`, `/restart`, `/logs`) y se detallarán los estatus HTTP de respuesta (200 Éxito, 400 Bad Request, 500 Conflicto Interno de Docker).

---

## 🧹 Fase 2: Recolección de Basura (Limpieza de Imágenes Huérfanas de Docker)

**Problema:** Cuando el usuario elimina un servicio alojado en modo "Custom" (Construido a partir de un Dockerfile), PaaSify elimina el contenedor, pero la _Imagen Docker_ compilada permanece en el disco del equipo host, ocupando un almacenamiento vital y generando fugas de memoria con el paso de los meses.

**Estrategia de Desarrollo:**

- **Servicios Docker (`containers/services.py`)**: Intervenir la función de borrado para que una vez que finalice la destrucción del Contenedor físico y la desvinculación de volumen, se ejecute `docker_client.images.remove` buscando por el sufijo autogenerado de imagen del proyecto.
- **Dangling Prune**: Implementar una ejecución pasiva de limpieza `prune(filters={'dangling': True})` que elimina fragmentos de imágenes temporales etiquetadas como `<none>:<none>` en cada reconstrucción.

---

## 🔔 Fase 3: Notificaciones UI Dinámicas (Feedback Visual)

**Problema:** Cuando ocurren errores de configuración de un contenedor (ej: PostgreSQL suicidándose por no tener variables de entorno), o simplemente se inician contenedores mediante solicitudes HTMX asíncronas, el usuario no recibe un feedback visual en la GUI de lo que acaba de suceder, obligando a recargar la página ciegamente.

**Estrategia de Desarrollo:**

- **Inyección Frontend (`templates/base.html`)**: Incorporar la librería `SweetAlert2` mediante CDN al esquema global.
- Crear funciones globales Javascript (`showToast`) configuradas estéticamente para generar notificaciones tipo _Toast Popup_.
- Enganchar _Event Listeners_ Javascript que operen nativamente sobre las respuestas de de la trama de red de **HTMX**.
- Interpretar respuestas `200/201` para disparar una notificación de finalización con éxito verde de la parte inferior-derecha.
- Interpretar y decodificar el esquema de error (texto de Exception) enviado por las respuestas HTTP `4xx` y `5xx` de la API para mostrar una alerta roja legible y amigable sobre qué fue mal directamente a los ojos del Usuario Administrador.
