# Checklist de Testing: Colección Postman 🚀

**Tarea**: Integración de mecanismo de descarga de colección API para Postman e Importación.
**Contexto**: Plan de reunión de seguimiento - Funcionalidad de Exportación OAS/Postman.

---

## 📋 Checklist de Verificación Manual

### 🌐 1. Interfaz y Descarga (UI/UX)

- [SI] **Visibilidad**: El nuevo apartado "Recursos API" es visible en el menú lateral de API Docs.
- [SI] **Estética**: El panel lateral tiene el borde naranja animado y el logo de Postman.
- [SI] **Separación**: Los iconos (cohete y logo Postman) tienen el espaciado correcto respecto al texto.
- [SI] **Acción de Descarga**: Al hacer clic en el botón naranja "Descargar para Postman", el navegador inicia la descarga del archivo `.json`.
- [SI] **Nombre de Archivo**: El archivo descargado se llama exactamente `paasify_api_collection.json`.

### 🎉 Testing: Importación y Uso de Colección Postman

Esta checklist detalla el proceso para verificar que la funcionalidad de exportación e importación de la configuración de Postman funciona correctamente y con la mejor Experiencia de Desarrollador (DevEx) posible para el alumno, **respetando la doble autenticación (Cookie/Bearer) que proporciona la API**.

### 1. 🔥 Exportación del Esquema

- [SI] Iniciar sesión en PaaSify como alumno.
- [SI] Navegar a **API Docs** en el panel lateral.
- [SI] Hacer clic en el botón naranja **"Descargar para Postman"**.
- [SI] Verificar que se descarga un archivo llamado `paasify_api_collection.json`.
- [SI] Abrir el archivo con un editor de texto y comprobar que en `components.securitySchemes` existen tanto `cookieAuth` como `Bearer`.
- [SI] Verificar que el array `servers` contiene `{{baseUrl}}/api`.

### 2. 🧲 Importación en Postman

- [SI] Abrir la aplicación de Postman.
- [SI] Hacer clic en **Import** y seleccionar el archivo `paasify_api_collection.json` recién descargado.
- [SI] **IMPORTANTE:** Cuando Postman pregunte cómo importar, elegir estrictamente **"Postman Collection"** (ignorar la opción OpenAPI 3.0 con Postman Collection).
- [SI] Confirmar que al lado izquierdo se ha creado una colección llamada **"PaaSify API"**.

### 3. 📂 Comprobación de Estructura (DevEx)

- [SI] Expandir la colección **PaaSify API**.
- [SI] Verificar que **NO** existe una carpeta molesta llamada `api/` en medio.
- [SI] Comprobar que en la raíz aparecen directamente las carpetas limpias: `Containers`, `Images`, `Projects`, `Subjects`.
- [SI] Desplegar la carpeta `Containers` y verificar que los nombres de las peticiones son naturales (ej. `List containers`, `Start container`, `Create container`) en lugar de `api_containers_list`.

### 4. ⚙️ Configuración Automática de Colección

- [SI] Hacer clic derecho en la raíz de la colección **PaaSify API** y seleccionar **Edit**.
- [SI] Ir a la pestaña **Auth** y verificar que el tipo seleccionado es **Bearer Token**.
- [SI] En esa misma pestaña de Auth, pegar el token de alumno directamente en el campo Token.
- [SI] Ir a la pestaña **Variables** y comprobar que existe `baseUrl` configurado por defecto (ej. `http://localhost:8000/api`).
- [SI] Guardar los cambios en la colección (Ctrl+S / Cmd+S).

### 5. 🚀 Pruebas de Peticiones Reales

- [SI] **Probar GET:** Seleccionar la petición `List containers` en la carpeta `Containers`.
- [SI] En la URL debe aparecer `{{baseUrl}}/api/containers/`.
- [SI] Pulsar **Send**. Debe devolver `200 OK` y una lista de los contenedores del alumno.
- [SI] **Verificar falta de Auth:** Desmarcar heredar Auth o borrar temporalmente la variable `paasifyToken` y lanzar un `GET` cualquiera. Debe dar un error `401` de autenticación de Django.
- [SI] **Comprobar Documentación Interna:** En una petición como `Get container details`, abrir el panel derecho de Postman (Documentation) y verificar que aparecen las posibles respuestas (200 Éxito, 404 Recurso no encontrado, etc.) con sentido humano.

### 6. 🔒 Revisión de Documentación en PaaSify

- [SI] Volver a la web de PaaSify en la pestaña **API Docs -> Postman**.
- [SI] Asegurarse de que el panel de **Recomendación de Seguridad** (con borde e icono de bombilla) sobre cómo regenerar tokens robados se lee bien.
- [SI] Verificar que las instrucciones escritas para el alumno cuadran con el proceso de importar como "Postman Collection" y configurar `{{baseUrl}}` y `{{paasifyToken}}`.

---

## 📊 Resultados y Observaciones

- **Fecha de Test**: `16-03-2026`
- **Resultado**: [PENDIENTE]
- **Notas**:
