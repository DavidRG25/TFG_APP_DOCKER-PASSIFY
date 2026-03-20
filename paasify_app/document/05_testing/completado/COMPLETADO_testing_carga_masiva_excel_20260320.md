# Checklist de Pruebas: Carga Masiva (Excel)

Este documento servirá de batería de validación manual para verificar la integridad, funcionamientos frontend/backend de los sub-sistemas de carga por Excel (Profesor vs Admin).

---

## 1. Panel Profesor (Advanced Wizard) 👨‍🏫

### 1.1 UI y Flujos Básicos

- [SI] Entrar al panel de profesor -> Seleccionar Asignatura.
- [SI] Hacer clic en el nuevo botón `Importar` (junto a "Nuevo Alumno").
- [SI] Verificar que se abre el modal "Carga Masiva de Alumnos y Proyectos".
- [SI] Hacer clic en "Descargar Plantilla.xlsx".
- [SI] Comprobar que el archivo se descarga correctamente indicando `Email, Nombre, Apellido, Proyecto y Contraseña`.

### 1.2 Casos Correctos

- [SI] **Caso 1 — Alumno mínimo válido**: Rellenar solo `Nombre de usuario` y `Email`. Se crea el usuario, se le configura el email como contraseña por defecto y se activa `must_change_password`.
- [SI] **Caso 2 — Alumno válido con contraseña explícita**: Rellenar contraseña custom. Se usa esa indicada directamente. ✅ _Comprobado: Funciona el login sin forzar cambio._
- [SI] **Caso 3 — Alumno válido con proyecto**: Indicar "Nombre Proyecto". El sistema lo procesa, inyecta y vincula del tirón.
- [SI] **Caso 4 — Alumno sin nombre/apellidos**: Dejar Nombre y Apellido vacíos. El sistema traga limpiamente al ser opcionales.
- [SI] **Caso 5 — Varios alumnos mezclados**: Bloque con algunos alumnos que tienen contraseña, otros no; unos con proyecto, otros no. 100% Correctos.

### 1.3 Casos Erróneos (Interceptación de Filas)

- [SI] **Caso 6 — Falta nombre de usuario**: Fila marcada como inválida en ROJO.
- [SI] **Caso 7 — Falta email**: Fila marcada como inválida en ROJO.
- [SI] **Caso 8 — Faltan ambos obligatorios**: Ídem, el parser levanta bandera de falta grave.
- [SI] **Caso 9 — Email inválido**: Usuario rellenado pero email tipo `no_es_email`. Formato no aceptado.
- [SI] **Caso 10 — Username duplicado (en Excel)**: El mismo username escrito 2 veces en filas distintas. El inspector de colisiones en RAM lo debe cazar.
- [SI] **Caso 11 — Email duplicado (en Excel)**: El mismo correo clonado 2 veces en filas distintas. Caza idéntica a la anterior.

### 1.4 Casos Existentes y Frontera

- [SI] **Caso 12 — Usuario ya existente en sistema (No matriculado)**: Subir un usuario que ya existe en la plataforma pero no en esta asignatura. Debe marcar en AMARILLO el badge de `Vinculación`.
- [SI] **Fila Redundante (Ya matriculado)**: Subir un usuario que ya está en la asignatura. Ahora se muestra en **AZUL CLARITO** como `Matriculado` (antes era Error) y permite continuar la importación. ✅ _Ajustado según feedback._
- [SI] **Caso 13 — Trim de espacios**: Celda tipo `  usuario_trim  `. El backend debe barrer los espacios extra y sanearlos (Trim automático).
- [SI] **Caso 14 — Espacios en el Proyecto**: Ejemplo "Proyecto Final TFG". Lo aceptará como nombre string literal.
- [SI] **Caso 15 — Caracteres UTF-8 (Tildes/eñes)**: Rellenar celdas con eñes para garantizar que no peta la serialización de Preview (Ej: `Peña`).

### 1.5 Caso Maestro Mixto (El Batiburrillo)

- [SI] **Caso Final (Mixed)**: Tabla que contenga de todo. Usuarios OK, Usuarios sin correo, usuarios existentes.
  - _Validación Exigida:_ El botón Confirmar **tiene que estar 100% deshabilitado**. La validación de PaaSify protege el Rollback total; si hay _una_ fila en rojo, no deja importar a nadie de forma parcial hasta que el profesor arregle su Excel.

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
