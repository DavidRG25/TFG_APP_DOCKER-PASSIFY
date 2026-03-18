# Implementación Carga Masiva (Excel)

## Objetivo General
Proveer una solución robusta y de doble capa para importar cuentas de usuario, asignarlas a grupos de permisos (estudiantes o profesores) y, opcionalmente, vincularlas a asignaturas y automatizar la creación de proyectos (Workspace).

---

## Estructura Implementada

### 1. `excel_importer.py` (Capa Servicio / Motor Central)
Se ha creado el módulo `paasify.services.excel_importer.ExcelImporterService` como única fuente de verdad transaccional.
- **Generación de Plantillas (`generate_template`)**: Crea al vuelo archivos `.xlsx` rellenados previamente con cabeceras, bloqueado de dimensiones y con 2 ejemplos descriptivos (uno para profesor y otro para admin).
- **Importación Admin (`process_admin_import`)**:
  - Validaciones estrictas.
  - Generación de usuarios y contraseñas.
  - Integración del mapeo de Grupos/Roles `(Student, Teacher, Admin)`.
  - Envuelto en una transacción atómica `todo_o_nada`.
- **Importación Profesor (`process_professor_import`)**:
  - Modalidad de previsualización (Dry-Run de validación) sin interactuar con la Base de datos de forma persistente.
  - Creación de Proyectos (UserProjects) en la asignatura en cuestión.
  - Clasificación del estado mediante tags (`ok` => Todo nuevo, `warning` => alumno pre-existente, `error` => colisión o formato incorrecto).

### 2. Panel Profesor (Vistas y Plantillas Drag & Drop)
- **Rutas API**: `SubjectViewSet` ampliado con acciones decoradas explícitamente (`import_template`, `import_preview`, `import_confirm`) en `paasify_app/containers/views.py`.
- **Frontend y UX**: Inyectado en `subject_detail.html` (Panel Profesor):
  - Modal dinámico utilizando promesas `fetch` asíncronas para evaluar en tiempo real el Excel y dibujar el *Table Preview* en Javascript nativo.

### 3. Panel de Administración (Django Admin Native Integration)
- Se ha sobreescrito `UserProfileAdmin` inyectando dinámicamente un custom `get_urls` y mapeándolo con `change_list_template`.
- Incorporado `import_excel.html` dentro de `paasify_app/templates/admin/paasify/userprofile/` integrándose con la estética nativa (breadcrumbs, user messages, theme styling Django Admin).

---

## Archivos Impactados
| Archivo | Nivel | Acción |
|---|---|---|
| `requirements.txt` | Core | Añadida dependencia `openpyxl`. |
| `paasify/services/excel_importer.py` | Servicio | **CREADO** |
| `paasify/admin.py` | App Admin | Modificado para soportar vistas personalizadas de URLs |
| `containers/views.py` | API REST | Creados 3 endpoints bajo la entidad `@action` (`SubjectViewSet`) |
| `templates/professor/subject_detail.html` | Frontend | Modal *ImportExcelModal*, JS AJAX incorporado y botones UI |
| `templates/admin/paasify/userprofile/change_list.html` | Plantillas | **CREADO/EXTENDIDO** (Object-Tools button overwrite) |
| `templates/admin/paasify/userprofile/import_excel.html` | Plantillas | **CREADO** (Layout subida de CSV/Excel nativo) |

---

## Decisiones Técnicas Destacadas
- **AJAX sobre Formularios POST tradicionales**: En la previsualización del profesor, se evitan pantallazos blancos al validar datos.
- **Transaccionalidad (ACID)**: Todo el bloque transaccional del profesor y del Admin está resguardado bajo un bloque `try/except: transaction.atomic()` garantizando que, si un usuario falla, ninguno entra al sistema evitando datos basura.
- **Doble Persistencia de Plantilla**: Con el objetivo de mantener los diseños uniformes sin colisionar columnas, se utilizan identificadores lógicos `professor` vs `admin` a la hora de generar el xlsx en RAM sin guardar disco puro (HttpResponse bytes stream).
