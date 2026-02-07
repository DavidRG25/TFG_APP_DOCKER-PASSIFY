
# Introducción

## Introducción

La API de PaaSify permite a los alumnos interactuar con la plataforma en formato **TERMINAL**. Todo lo que puedes hacer a través de la interfaz web (crear contenedores, reiniciarlos, ver logs) está disponible mediante peticiones HTTP.

Esta API está diseñada siguiendo los principios RESTful y devuelve respuestas en formato JSON.

### URL Base

Todas las peticiones deben realizarse a la siguiente URL base:

> **URL Base**: `{{ PAASIFY_API_URL }}`

### Recursos Disponibles

La API expone los siguientes recursos principales para los alumnos:

- `/containers`: Gestión completa del ciclo de vida de tus servicios.
- `/subjects`: Consulta de las asignaturas en las que estás matriculado.
- `/projects`: Consulta de los proyectos que tienes asignados.
- `/images`: Catálogo de imágenes permitidas por la universidad.

---
