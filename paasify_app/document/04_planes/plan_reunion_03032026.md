# Plan de Tareas - Reunión 03/03/2026

**Fecha**: 04-03-2026
**Estado**: Pendiente
**Origen**: Feedback de revisión final con el profesor.

---

## 📋 Lista de Tareas y Ajustes

### UI / Presentación

- [ ] **Texto y emoticonos separados**: Revisar todos los paneles para asegurar que los emoticonos y los textos no están unidos sin espacios, asegurando una estética limpia.
- [ ] **Renombrar panel**: Cambiar el nombre del panel superior/lateral de "Proyectos" a "Mis Servicios".
- [ ] **Panel de personalización más pequeño**: Ajustar el tamaño del panel de diseño/personalización para que no ocupe demasiado espacio en pantalla.
- [ ] **Panel "No estás matriculado" visual**: Mejorar el diseño del panel vacío que se muestra cuando un alumno no tiene asignaturas, haciéndolo más amigable/visual y validando correctamente el estado de su sesión.
- [ ] **Visualización de proyectos vacíos**: Permitir que los profesores/alumnos puedan ver y entrar en proyectos que todavía no tienen servicios asociados.
- [ ] **Cerrar botón cerrar sesión**: Arreglar/Ajustar el comportamiento o estilo del botón de cerrar sesión.

### Funcionalidades de Carga (Excel)

- [ ] **Carga masiva por Excel**: Implementar/afinar la importación de datos.
- [ ] **Creación de alumnos por Excel**: Cargar una lista de alumnos a partir de un archivo Excel.
- [ ] **Generación de proyectos desde Excel**: A partir de la carga de alumnos, auto-generar sus proyectos/espacios de trabajo automáticamente.
- [ ] **Selección múltiple de alumnos**: Permitir que al vincular alumnos existentes a un proyecto/asignatura se puedan seleccionar múltiples a la vez en lugar de uno por uno.

### APIs y Documentación

- [ ] **Colección Postman exportable**: A partir de nuestra documentación OAS (Swagger/drf-spectacular), generar un JSON de Postman o un mecanismo que permita descargar un archivo directo para importarlo en Postman.
- [ ] **Menú Profesor - API Docs**: El enlace a `API-DOCS` debe estar visible también en el panel del profesor, no solo en el del admin o alumno.

### Seguridad y Sesiones

- [ ] **Timeout de sesión**: Ajustar la configuración de la sesión en Django para que caduque automáticamente por inactividad.
- [ ] **Cambio de contraseña forzado del Admin**: Al hacer login por primera vez con el superusuario (admin), el sistema debe forzar obligatoriamente el cambio de contraseña por seguridad.

### Bugs / Fixes detectados

- [ ] **Bug ZIP Docker Compose**: Resolver problema de validación frontend donde el formulario exige falsamente subir un archivo ZIP al desplegar una configuración `docker-compose.yml`.
- [ ] **Admin de profesores**: Resolver el bug en el panel de administrador donde los "Perfiles de profesores" no están cargando correctamente los usuarios asociados.
- [ ] **Despliegue README hardcodeado**: Revisar `deploy/README.md` (o la conf real) porque actualmente figura un `server_name` quemado ("a cañón") con una URL específica en lugar de una variable.

### CI / CD

- [ ] **Montar el modelo GitHub Action**: Establecer y configurar los flujos de GitHub Actions para el empaquetado y subida del contenedor directamente desde el refactor realizado.

---

## 🛠 Plan de Acción

1. **Fase 1: Fixes Rápidos y Textos** (UI, Bugs directos, renombres).
2. **Fase 2: Autenticación y Seguridad** (Sesiones inactivas, Cambio forzado de clave Admin).
3. **Fase 3: Importaciones Excel y Gestión Múltiple** (Lógica de pandas/openpyxl, lógica de BD masiva).
4. **Fase 4: Documentación y CI/CD** (Postman, README deploy, GH Actions).
