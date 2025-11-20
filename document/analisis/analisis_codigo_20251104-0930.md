---
# Análisis de Código — Rama: feature/analisis-codigo
> Resumen: Diagnóstico del flujo de alta de alumnos en el admin y sincronización con usuarios del grupo Student.

## 🧩 Objetivo
Revisar el formulario y la configuración del admin de `Player` para explicar por qué la opción «Crear usuario nuevo» no permite guardar el registro y garantizar que los usuarios marcados como alumnos aparezcan en la lista de `PaaSify → Alumnos`.

## 📂 Archivos revisados
- `paasify/admin.py`
- `paasify/models/StudentModel.py`
- `paasify/roles.py`
- `paasify/signals.py`
- `templates/admin/player/change_form.html` (estructura general del admin de Django)

## ⚠️ Problemas detectados
1. **Validaciones estrictas en campos obligatorios**: el `ModelForm` obliga a rellenar `nombre` y `year` antes de validar, aunque después se completan automáticamente en `save`. Si el personal administrativo confía en la casilla «Crear usuario nuevo» y deja esos campos vacíos, el formulario marca errores de «Este campo es requerido», reproduciendo la incidencia reportada. 【F:paasify/admin.py†L107-L150】
2. **Sin autocompletado previo al guardado**: la lógica que copia `username` y `email` al modelo sólo se ejecuta tras pasar la validación, por lo que no cubre el escenario anterior. 【F:paasify/admin.py†L134-L146】
3. **Sincronización con usuarios existentes dependiente de grupos**: la aparición automática de alumnos en el listado funciona cuando se añade al usuario al grupo `Student`, gracias a la señal `sync_player_on_group_change`. Sin embargo, si se crea el usuario sin asignar el grupo o se usa una denominación distinta (por ejemplo «Alumno»), no se dispara la autocreación. 【F:paasify/roles.py†L1-L46】【F:paasify/signals.py†L1-L18】

**Ejecución de validaciones:**
- `python -m compileall app_passify containers paasify security templates tests` → compilación sin errores. 【1f9f70†L1-L30】
- `pytest` → 1 prueba pasada, 1 omitida por ausencia de daemon Docker. 【b9c1f4†L1-L4】

## 💡 Propuestas de solución
1. Relajar la obligatoriedad de `nombre` y `year` en el formulario cuando se cree un usuario nuevo, generando valores por defecto desde `new_username` y `new_email` en `clean()` antes de validar el modelo.
2. En `clean()`, completar automáticamente los campos vacíos con datos del usuario seleccionado (existente o recién creado) para evitar errores de validación y permitir guardados consistentes.
3. Asegurar que `ensure_user_group` acepte variantes de nombre (`alumno`, `Alumno`, `student`, `Student`) y documentar en el admin que el grupo debe seleccionarse durante la creación de usuarios para que la señal cree la ficha de alumno.

## 🧠 Impacto estimado
Aplicar los ajustes anteriores permitirá registrar alumnos desde el admin sin fricción, reducirá incidencias para el personal administrativo y garantizará que el listado de alumnos permanezca sincronizado con los usuarios del grupo `Student`.

## 🧾 Confirmación requerida
⚠️ No realices ningún cambio en el código sin la aprobación explícita del usuario.
---
