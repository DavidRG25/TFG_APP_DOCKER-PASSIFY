# Implementación: Mejoras Modales Asignatura (Dashboard Profesor)

**Fecha:** 2026-03-08
**Origen:** Identificado "al vuelo" durante la sesión de QA (añadido al Plan de tareas "Reunión 03/03/2026").

## 🎯 Objetivos Implementados

Se han detectado y solucionado varios comportamientos anómalos (bugs) y oportunidades de mejora de usabilidad (UX) en los modales de "Nueva Asignatura" y "Personalizar Asignatura" del panel del profesor.

Los objetivos específicos fueros:

1. **Previsualización de Imagen**: Mostrar el logo subido antes de confirmar la creación/edición.
2. **Eliminación y Limpieza**: Permitir quitar la imagen recién subida y restaurar el formulario.
3. **Reseteo de Datos Residuales**: Evitar que al cerrar y reabrir el modal de creación persistan los datos antiguos.
4. **Validación de Archivos y Error Django**: Prevenir el error de base de datos (`DataError`) cuando el string del nombre del archivo subido superaba los 100 caracteres.

## 🛠 Cambios Realizados

### 1. Reseteo del Modal "Nueva Asignatura"

- **Problema**: El manejador de Vanilla JS (`modal.addEventListener('hidden.bs.modal', ...)`) no estaba interceptando de forma fiable el evento proveniente de la librería de jQuery de Bootstrap al cerrar el modal, dejando texto y archivos cargados.
- **Solución**: Refactorizado el EventListener para utilizar jQuery puro (`$('.modal').on('hidden.bs.modal')`). Ahora, iterativamente limpia cualquier campo del formulario y dispara un reset del selector de imagen.
- **Archivo Modificado**: `paasify_app/templates/professor/dashboard.html`

### 2. Controles de Imagen: Previsualización y Borrado (Ambos modales)

- **Problema**: Los modales solo permitían subir el archivo con el `input type=file` nativo pero no permitían cancelar, dar marcha atrás o ver el diseño subido.
- **Solución**:
  - Se han añadido contenedores HTML dinámicos (`#new-sub-display-container`, `#logo-preview-container-new`).
  - Lógica JS con `FileReader` que lee el buffer de imagen y genera un tag `<img>`.
  - Botón específico rojo "Quitar imagen" que elimina cualquier visualización temporal, limpiando la cola del envío al servidor.
- **Archivos Modificados**:
  - `paasify_app/templates/professor/dashboard.html` (Nueva Asignatura)
  - `paasify_app/templates/professor/subject_detail.html` (Editar Asignatura)

### 3. Evitar Error Crítico 500: Validación JS Max Length

- **Problema**: Django impone que `models.ImageField` tiene un límite estricto en BD (ej. `max_length=100`). Si un profesor es arrastraba un archivo con un nombre muy largo, la app lanzaba un error 500 no gestionado amigablemente.
- **Solución**: En ambas funciones `previewLogo(input)` y `previewNewSubjectLogo(input)` se intercepta el fichero justo antes de montarlo y previsualizarlo:
  - Condicional: `if (fileName.length > 90) { ... }`
  - Acción: Se aborta la carga, se vacía el selector para que no vaya al backend y se notifica con un `showToast()` amarillo amigable instruyendo al profesor a re-nombrar el archivo localmente.

## ✅ Resultado Final

- Los modales ahora son resilientes frente a errores de longitud de archivos.
- Interfaz WYSIWYG robusta al jugar con fotos.
- Cero retención de datos en memoria para los modales de creación (no hay datos cruzados).
