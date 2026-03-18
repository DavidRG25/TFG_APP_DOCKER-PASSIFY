# Plan Técnico: Importación Masiva Excel (Wizard de Carga)

**Fecha de creación:** 17/03/2026
**Objetivo:** Desarrollar un sistema robusto y profesional de carga masiva de alumnos a través de archivos Excel (`.xlsx`), con dos niveles de complejidad dependiendo del actor (Profesor vs Administrador).
**Estado:** Completado (18/03/2026)

---

## Nivel 1: Panel del Profesor (Wizard Avanzado y UX Premium)

Este es el núcleo duro y principal funcional de la carga masiva. Se requiere que el profesor tenga control absoluto y retroalimentación visual antes de realizar cambios definitivos en la base de datos.
La carga desde este panel admite la creación de alumnos con o sin proyectos simultáneos.

### Funcionalidad

1. **Botón y Modal:** Nuevo botón "Importación Masiva" en la vista de Asignatura que abre un modal ancho explicativo.
2. **Descarga de Plantilla:** Botón dentro del modal para descargar `plantilla_alumnos_proyectos_paasify.xlsx` (con cabeceras preparadas: Nombre, Apellidos, Email, Contraseña, Nombre Proyecto [Opcional]).
3. **Fase de Análisis (Preview)**:
   - El profesor sube el Excel rellenado.
   - El archivo se envía al backend vía AJAX/Fetch (Endpoint: `/api/subjects/<id>/preview_import/`).
   - El backend usa `openpyxl` para leer y validar el archivo línea por línea **sin guardar nada en la base de datos**.
   - El backend devuelve un JSON con el análisis estructurado, discerniendo si crear solo al alumno o también un proyecto específico.
4. **Tabla de Resultados (Frontend)**:
   - Se pinta una tabla en el modal con el reporte de cada fila del Excel.
   - 🟢 **Estado OK (Creación):** El alumno no existe. Se creará la cuenta y se vinculará a la asignatura. Si el Excel indica un proyecto, se creará usando ese nombre (en caso contrario, no se fuerza proyecto automático salvo que se requiera).
   - 🟡 **Estado Warning (Vinculación):** El alumno ya existe en el sistema. Solamente se matriculará en la asignatura y, si viene indicado, se le creará su proyecto.
   - 🔴 **Estado Error:** Faltan campos obligatorios (ej. email en blanco), email inválido o nombre de proyecto duplicado.
5. **Confirmación Segura:**
   - El botón final "Confirmar Importación" **solo se habilitará** si no existe ningún error rojo (🔴) en la tabla. Si hay errores, el profesor debe corregir su Excel y volver a subirlo.
   - Al confirmar, se lanza un segundo endpoint (`/api/subjects/<id>/confirm_import/`) que ejecuta las creaciones atómicas requeridas.

---

## Nivel 2: Panel de Administrador de Django (Carga Directa e Intransigente)

El panel de administrador de Django (Backend tradicional) requiere una vía rápida, funcional y directa sin la parafernalia del wizard AJAX, asumiendo un rol más técnico. La carga aquí es puramente de Usuarios y Roles (sin proyectos).

### Funcionalidad

1. **Botón en Interface Django:** Modificar el `change_list` del modelo `User` o `UserProfile` para añadir un botón "Carga Masiva (Básica)".
2. **Formulario Simple:** Una vista clásica de Django con un `<input type="file">` y un botón de descarga de una plantilla genérica `plantilla_admin_usuarios.xlsx` (Nombre, Apellidos, Email, Contraseña, Rol).
3. **Validación Bloqueante Transaccional**:
   - Al darle a "Subir". Se ejecuta la misma lógica validadora básica.
   - Si, al repasar el Excel, encuentra un solo error ("Ej: Fila 4 le falta email"), se cancela absolutamente toda la operación (Database Atomicity).
   - El admin verá el típico aviso de banner rojo en lo alto de la pantalla de Django.
   - Si no hay fallos, se crea la ristra de usuarios (con los roles indicados) y sale el banner verde de éxito. No hay creación de proyectos aquí.

---

## Librerías Recomendadas

- **Python**: `openpyxl`. (Muy ligero y no arrastra dependencias inmensas como pandas).
- **Base de datos**: `with transaction.atomic():` (Vital para evitar cargas a la mitad si un script falla).
