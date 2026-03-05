# Feature: Mejora del Flujo de Despliegue y Logs Avanzados

**Fecha:** 15/02/2026
**Estado:** COMPLETADO
**Autor:** David RG

## 1. Descripción

Se ha rediseñado el proceso de creación de nuevos servicios y la visualización de logs para ofrecer una experiencia más guiada, precisa y profesional, enfocada en la usabilidad para el entorno académico.

## 2. Mejoras de Interfaz (UI/UX)

- **Selector de Sub-tipo Personalizado**: Nueva jerarquía visual que permite elegir entre "Dockerfile Único" y "Docker Compose" mediante tarjetas interactivas antes de configurar el servicio.
- **Configuración de Puertos Inteligente**:
  - Los campos de puertos ahora se agrupan en un bloque visual tipo "Card".
  - Se ocultan automáticamente al seleccionar Docker Compose (gestión interna).
  - Incluyen un aviso destacado (`alert-info`) sobre el puerto por defecto.
- **Sidebar Contextual Dinámico**:
  - Los **Ejemplos** de la derecha cambian en tiempo real según el modo seleccionado (Default, DockerHub, Dockerfile o Compose).
  - El sidebar se alinea automáticamente con la sección de configuración mediante espaciadores dinámicos.
- **Transiciones Fluidas**: Implementación de animaciones CSS para evitar saltos bruscos al mostrar u ocultar secciones.

## 3. Sistema de Logs Avanzado

- **Timestamps en Tiempo Real**: Inclusión de fecha y hora local de España `[DD/MM/YYYY HH:MM:SS]` en todos los logs (estáticos y streaming por WebSocket).
- **Filtrado Robusto**:
  - Parámetro `since` (ej: `5m`, `1h`) para filtrar por tiempo relativo.
  - Parámetro `tail` para limitar el número de líneas.
  - Filtrado por contenedor específico dentro de un stack Compose.
- **Depuración de Errores Críticos**:
  - Marcado especial `[SISTEMA]` para errores de despliegue (fallos de build, errores de descompresión RAR, etc.).
  - Documentación actualizada con ejemplos reales de `ModuleNotFoundError` y fallos en `Dockerfile`.

## 4. Archivos Modificados

- `templates/containers/new_service.html`: Estructura del formulario y sidebar.
- `templates/containers/_partials/panels/_scripts.html`: Lógica JavaScript de visibilidad y filtros.
- `containers/utils.py`: Lógica de obtención y formateo de logs.
- `containers/consumers.py`: Formateo de logs en streaming.
- `templates/api_docs/partials/06_logs.md`: Documentación técnica de la API.

## 5. Verificación

- Plan de pruebas entregado en: `document/testing/testing_nuevos_ejemplos_docker.md`.
- 4 nuevos ejemplos de prueba creados en `testing_examples/`.
