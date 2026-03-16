# Plan de Implementación: Mejora de Experiencia (DevEx) en Exportación Postman

## 🎯 Objetivo General
Mejorar radicalmente la experiencia del alumno al importar el esquema de la API en Postman (Developer Experience - DevEx), optimizando la estructura, nombres y variables, **manteniendo intacta y fiel la semántica de autenticación real de la API**.

## 🛡️ Principio Fundamental Aplicado
**Fidelidad del Esquema vs. Comodidad del Cliente:**
*   La API de PaaSify soporta legítimamente tanto autenticación por Sesión (`cookieAuth`) como por Token personalizado (`Bearer` vía `TokenAuthMiddleware`).
*   Se ha garantizado que el esquema base generado por `drf-spectacular` publique de forma oficial **ambos métodos**, asegurando que herramientas estrictas como Swagger o Redoc no pierdan funcionalidad.
*   En paralelo, se ha inyectado un post-procesado exclusivo para el endpoint de descarga JSON (`/api-docs/export/`) para que Postman, siendo un cliente HTTP externo, se auto-configure de fábrica priorizando la opción más sensata para tests manuales (Bearer Token) y una estructura de carpetas útil.

---

## 🛠️ Archivos Modificados

### 1. `app_passify/settings.py`
**Razón:** Hacer oficial el soporte dual de autenticación.
**Cambio:** Actualización del parámetro `SPECTACULAR_SETTINGS['SECURITY']` para declarar explícitamente `[{'cookieAuth': []}, {'Bearer': []}]`. Esto garantiza que la API no esconda su soporte de sesiones por querer agradar a Postman.

### 2. `containers/views.py` (Vista `export_api_schema`)
**Razón:** El núcleo de la mejora DevEx post-generación.
**Cambios:**
*   **Aparición de Variables Nativas:** Se ha forzado el uso de la variable `{{baseUrl}}` a nivel de servidor en el esquema, definiendo valores por defecto (`http://localhost:8000`). Esto permite que el JSON exportado cree automáticamente variables de colección en Postman.
*   **Prioridad Bearer Inteligente:** Se ordena la configuración de seguridad (`schema['security']`) para que `Bearer` esté en posición cero. Postman toma el primero de la lista para auto-configurar la pestaña "Auth" del padre, sin eliminar `cookieAuth` de las tripas del contrato.
*   **Summaries Humanos:** Se usa un diccionario (`summary_map`) para traducir OperationIds ilegibles (`api_containers_destroy`) a frases naturales (`Delete container`), lo que mejora enormemente la barra lateral izquierda en Postman.
*   **Limpieza de Carpetas Estériles (Opción A):** Retiramos el prefijo de URI `/api/` de los "paths" exportados (compensado por el Server `{{baseUrl}}/api`) y limpiamos los `tags`. Esto evita que Postman colapse todo bajo una carpeta inútil llamada "api" y, en su lugar, genere categorías raíz directas: "Containers", "Projects", "Subjects".
*   **Mejoras de Description:** Rellenamos los códigos de respuesta vacíos (200, 400, 404...) con descripciones coloquiales y entendibles para un alumno.

### 3. `document/05_testing/testing_postman_collection.md`
**Razón:** Reflejar el nuevo y simplificado flujo de pruebas.
**Cambios:** Se ha añadido el paso crítico para el usuario: Al dar clic en "Importar", se debe seleccionar explícitamente **"Postman Collection"** (y no "OpenAPI 3.0"). Esto evita que Postman intente forzar un ciclo de vida entero de la API y lo trate simplemente como una librería de peticiones listas para usar.

### 4. `templates/api_docs/partials/00_postman/postman.md`
**Razón:** Enseñar al alumno el camino corto de configuración.
**Cambios:** Se actualizó la checklist de "Cómo empezar en Postman" detallando claramente que sólo necesitan editar dos variables de la colección (`baseUrl` y `paasifyToken`) y seleccionar "Postman Collection" al importar.

---

## 🚦 Limitaciones Actuales y Consideraciones
1.  **Imprevisibilidad de Postman con OpenAPI:** Al ser una herramienta propietaria, Postman reserva el derecho a cambiar cómo reacciona al leer esquemas OpenAPI. Dependemos de su motor de importación para que priorizar `Bearer` en posición `index[0]` funcione, pero el esquema exportado es totalmente válido según el estándar OAI.
2.  **Tokens vs. Sesiones:** Aunque el Postman quede configurado para Tokens, un usuario malicioso que intente interceptar cookies para probar endpoints (`cookieAuth`) se encontrará con que el esquema lo certifica como válido. Hemos mejorado la UI sin fingir seguridad falsa.
