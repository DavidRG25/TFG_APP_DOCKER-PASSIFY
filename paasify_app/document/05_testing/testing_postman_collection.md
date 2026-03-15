# Plan de Testing: Colección Postman Exportable

**Tarea**: Integración de mecanismo de descarga de colección API para Postman.
**Contexto**: Plan de reunión de seguimiento.

---

## 🔍 Objetivos del Test
Verificar que los alumnos pueden descargar el esquema de la API en formato JSON e importarlo correctamente en Postman, asegurando que las peticiones estén pre-configuradas y listas para usar tras añadir el token.

## 🛠️ Pasos de Verificación Manual

### 1. Acceso y Descarga
1.  Entrar en la plataforma con una cuenta de alumno o profesor.
2.  Navegar a la sección **API Docs**.
3.  En la página de **Introducción**, verificar que aparece un nuevo bloque informativo sobre **Postman**.
4.  Hacer clic en el botón **"Descargar para Postman"**.
5.  Comprobar que se descarga un archivo llamado `paasify_api_collection.json`.

### 2. Importación en Postman
1.  Abrir la aplicación **Postman**.
2.  Hacer clic en el botón **"Import"**.
3.  Arrastrar el archivo cargado anteriormente.
4.  Verificar que Postman reconoce el archivo como un esquema **OpenAPI 3.0**.
5.  Confirmar la importación. Se debería crear una nueva carpeta/colección llamada "PaaSify API".

### 3. Prueba de Petición (Auth)
1.  Seleccionar una petición (ej: `GET /api/subjects/`).
2.  Ir a la pestaña **Authorization**.
3.  Verificar que el tipo está configurado como **Bearer Token**.
4.  Poner el token personal en la variable o directamente en el campo.
5.  Ejecutar la petición (**Send**) y verificar que devuelve un `200 OK`.

## 📈 Resultados Esperados
- El botón de descarga es visible y funcional.
- El archivo JSON contiene la definición completa de los endpoints (GET, POST, DELETE, etc.).
- Postman importa correctamente todos los métodos, descripciones y ejemplos de respuesta.
