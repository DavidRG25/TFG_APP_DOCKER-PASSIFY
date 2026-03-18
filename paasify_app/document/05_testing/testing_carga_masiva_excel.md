# Checklist de Pruebas: Carga Masiva (Excel)

Este documento servirá de batería de validación manual para verificar la integridad, funcionamientos frontend/backend de los sub-sistemas de carga por Excel (Profesor vs Admin).

---

## 1. Panel Profesor (Advanced Wizard) 👨‍🏫

### 1.1 UI y Flujos Básicos

- [ ] Entrar al panel de profesor -> Seleccionar Asignatura.
- [ ] Hacer clic en el nuevo botón `Importar` (junto a "Nuevo Alumno").
- [ ] Verificar que se abre el modal "Carga Masiva de Alumnos y Proyectos".
- [ ] Hacer clic en "Descargar Plantilla.xlsx".
- [ ] Comprobar que el archivo se descarga correctamente indicando `Email, Nombre, Apellido, Proyecto y Contraseña`.

### 1.2 Importación de Estudiantes Nuevos (Status: OK)

- [ ] Rellenar la plantilla con un par de emails únicos. Dejar Proyecto en blanco.
- [ ] Subir el Excel.
- [ ] **Validación Frontend**: Se despliega tabla de Previsualización: "Estado Nuevo, Verde" y las Rows coinciden con las filas leídas.
- [ ] Pulsar `Confirmar y Ejecutar...` -> Confirmar en base de datos la matriculación exitosa de los usuarios.

### 1.3 Alumnos Existentes (Status: WARNING)

- [ ] Utilizar un correo de un estudiante YA existente en otra asignatura (o creado previamente) en una fila.
- [ ] Rellenar otra fila con un estudiante nuevo.
- [ ] Subir archivo -> Verificar que la tabla muestra en amarillo "Vinculación" para el caso existente, y el total de "Vinculados" sube en el summary (Badge Superior).
- [ ] Confirmar importación y comprobar que no hay colisión ni doble inserción de Profile, solo de relaciones `subject.students.add()`.

### 1.4 Auto-Generación de Proyectos simultánea

- [ ] En la plantilla, añadir datos en la columna opcional **Proyecto** (Ej: _Espacio Ciberseguridad A_).
- [ ] Tras importar y confirmar, navegar a "Proyectos de la Asignatura" y confirmar su creación en la lista de paneles lateral de PaaSify vinculando correctamente a ese estudiante.

### 1.5 Colisión y Errores (Status: ERROR)

- [ ] Subir archivo Excel adulterado (ej. fila sin correo, o correo sin formato válido).
- [ ] El preview marca en rojo `ERROR` e inhabilita el botón verde "Confirmar...".
- [ ] Tratar de duplicar un email internamente en la propia hoja Excel. Confirmar notificación de "Duplicados encontrados".

---

## 2. Panel Admin (Simple Direct Upload) 👑

### 2.1 UI y Descarga Plantilla

- [SI] Acceder al Panel de Admninistración Nativo de Django (`/admin`).
- [SI] Ir a **Usuarios/Carga Masiva (Excel)**.
- [SI] Pulsar arriba en el nuevo botón "Carga Masiva (Excel)".
- [SI] Hacer clic en Descargar Plantilla. Comprobar que contiene el campo "Rol" adicional.
- [SI] Modificar una línea como `admin, student` intencionadamente para ver soporte multi-grupo.

### 2.2 Validación Atómica y Crash Transaccional

- [SI] En el mismo excel, colocar 2 usuarios bien formados y 1 tercer usuario con campo email en blanco.
- [SI] Subir al panel -> Confirmar mensaje de "Error Transaccional Abortado: La fila X no contiene un Email válido...".
- [SI] Ir a la lista de usuarios y confirmar que NINGUNO de los otros 2 estudiantes bien formados se inyectaron en el sistema (Rollback Correcto DB).
- [SI] Interceptar intento de multi-rol o rol no admitido (ej. `rector` o `admin, student`), mostrando el Error Transaccional de "Rol no válido".
- [SI] Cargar un mismo usuario/email duplicado dentro del archivo Excel lo bloquea de inmediato antes de tocar la BBDD.

### 2.3 Importación Satisfactoria

- [SI] Subir únicamente un lote de 10 usuarios puros, con roles válidos (`student`, `teacher`, `admin`).
- [SI] Recibir Toast nativo en Django Admin de "Operación Completada: 10 usuarios".
- [SI] Verificar que han escalado correctamente en la lista visual del admin y tienen sus roles marcados con el badge de color nativo.
- [SI] Validar que a todos se les registra correctamente en su grupo de permisos de Django mediante `ensure_user_group`.

### 2.4 Auto-Password e Integridad (Mejoras QA)

- [SI] Si un usuario se sube con el campo de Contraseña en blanco, el sistema asigna su propio Email como contraseña automatizada.
- [SI] Se activa internamente el super-flag `must_change_password=True` en su `UserProfile` vinculante.
- [SI] Evita colisiones de `UNIQUE constraint` (Signals de perfiles subyacentes) usando un seguro `update_or_create`.

---

> **Nota para el Tester:** Cualquier inconsistencia descubierta en esta matriz de control deberá ser notificada y anexada para corrección (Bugfix).
