# Implementación de Código — Rama: feature/analisis-codigo
_Resumen: Corrección del `TemplateSyntaxError` en `base.html` mediante la creación de una etiqueta de plantilla personalizada para verificar la pertenencia a grupos._

## 🧩 Objetivo
Solucionar el error crítico `TemplateSyntaxError` que ocurre al intentar acceder a la página de login cuando la aplicación se ejecuta con un servidor ASGI como Daphne.

## 📂 Archivos modificados
- `security/functions.py` (nuevo)
- `templates/base.html`
- `app_passify/settings.py`

## ⚠️ Análisis del problema
El error es causado por la expresión `user.groups.filter(name__iexact='student').exists` dentro de una etiqueta `{% if %}` en el fichero `templates/base.html`. El motor de plantillas de Django no permite la ejecución de llamadas a métodos con parámetros, lo que provoca el fallo al renderizar la plantilla.

## 💡 Solución implementada
1.  **Creación de una función de plantilla personalizada:** Se ha creado el archivo `security/functions.py` que contiene un filtro de plantilla llamado `has_group`. Este filtro permite verificar si un usuario pertenece a un grupo específico de una manera que es compatible con el motor de plantillas de Django.
2.  **Modificación de la plantilla:** Se ha actualizado `templates/base.html` para reemplazar la lógica de filtrado de grupos con la nueva etiqueta de plantilla. Por ejemplo, la comprobación para el grupo de estudiantes ahora es `{% if user|has_group:'student' %}`.
3.  **Registro de la aplicación:** Se ha añadido la aplicación `security` al `INSTALLED_APPS` en `app_passify/settings.py` para que el nuevo filtro de plantilla esté disponible en todo el proyecto.

## 🧠 Impacto
Esta corrección resuelve el `TemplateSyntaxError`, permitiendo que la página de login y el resto de la aplicación funcionen correctamente bajo un servidor ASGI. Además, centraliza la lógica de comprobación de roles en una función reutilizable, mejorando la mantenibilidad del código.
