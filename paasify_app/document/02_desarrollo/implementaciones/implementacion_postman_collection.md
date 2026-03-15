# Implementación: Colección Postman Exportable

**Tarea**: Generación y exportación de esquema API para Postman.
**Contexto**: Parte del plan de reunión de seguimiento.
**Estado**: En desarrollo.

---

## 📝 Descripción Técnica
Se ha implementado un mecanismo para facilitar a los estudiantes el uso de herramientas externas de testing (como Postman o Insomnia) mediante la exportación del esquema OpenAPI de la plataforma.

### Cambios Realizados:

#### 1. Backend (`containers/views.py`)
- Creación de una vista específica `export_api_schema` que utiliza el generador de `drf-spectacular`.
- Configuración de cabeceras `Content-Disposition` para forzar la descarga del archivo como `paasify_api_collection.json`.

#### 2. Frontend (`templates/api_docs/partials/01_intro/intro.md`)
- Adición de un componente visual "Premium Card" con estética orientada a herramientas de desarrollo.
- Guía rápida de importación y configuración de variables de entorno en Postman.
- Inclusión del botón de descarga directa vinculado a la nueva ruta del backend.

#### 3. Rutas (`containers/urls.py`)
- Registro de la URL `/paasify/containers/api-docs/export/` para gestionar la descarga.

---

## 💡 Notas de Implementación
- Se ha optado por exportar el estándar **OpenAPI 3.0** ya que Postman lo soporta de forma nativa y permite una mejor sincronización de tipos de datos y esquemas que el formato antiguo de colecciones de Postman.
- El archivo generado incluye toda la documentación de parámetros, códigos de error y ejemplos de respuesta definidos en los Serializers del proyecto.
