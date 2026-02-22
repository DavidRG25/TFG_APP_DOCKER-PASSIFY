# Introducción a PaaSify API

La API de PaaSify permite a los alumnos interactuar programáticamente con la plataforma. Todo lo que puedes hacer a través de la interfaz web (crear servicios, reiniciarlos, ver logs) está disponible mediante peticiones HTTP.

Esta API sigue los principios **RESTful** y devuelve respuestas en formato **JSON**.

---

## 🌐 URL Base

Todas las peticiones deben realizarse a la siguiente URL base:

> `{{ PAASIFY_API_URL }}/`

Esta URL está configurada dinámicamente según el entorno (desarrollo o producción).

---

## 📦 Recursos Principales

La API expone los siguientes recursos para los alumnos:

| Recurso               | Descripción                                                             |
| :-------------------- | :---------------------------------------------------------------------- |
| 🐳 `/api/containers/` | Gestión del ciclo de vida de tus servicios (crear, modificar, detener). |
| 📚 `/api/subjects/`   | Consulta de las asignaturas en las que estás matriculado.               |
| 📂 `/api/projects/`   | Gestión de tus proyectos asignados.                                     |
| 🖼️ `/api/images/`     | Catálogo de imágenes permitidas por la universidad.                     |

---

## 🚀 ¿Por qué usar la API?

- **🔄 Automatización**: Crea scripts para desplegar tus entornos automáticamente.
- **⚡ CI/CD**: Integra PaaSify con GitHub Actions o GitLab CI.
- **🛠️ Herramientas personalizadas**: Construye tus propios dashboards o CLIs.
