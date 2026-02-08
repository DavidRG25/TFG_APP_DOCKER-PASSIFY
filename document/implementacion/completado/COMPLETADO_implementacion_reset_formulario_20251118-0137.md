Implementacion - Reset formulario nuevo servicio (20251118-0137)

Problema
- Al cerrar el modal de nuevo servicio (X, Cancelar o tras crear) los valores quedaban en el formulario: nombre, puerto, archivos y modo seleccionado.

Solucion
- Se agrega `resetNewServiceForm()` que resetea el formulario, limpia errores, reinicia archivos, re-aplica reglas de modo, cierra popovers y limpia exclusiones.
- Se engancha al evento `hidden.bs.modal`, al custom event `service:modal-close` y al `htmx:afterRequest` exitoso del formulario para resetear y cerrar el modal.

Archivos modificados
- `templates/containers/student_panel.html`

Antes
- Los datos persistian al reabrir el modal.

Despues
- Cada cierre o envio exitoso deja el formulario limpio y coherente con el modo por defecto.

Pruebas sugeridas
- Abrir modal, rellenar datos y cerrarlo con X: al reabrir debe estar vacio.
- Rellenar y pulsar Cancelar: al reabrir debe estar vacio.
- Crear servicio con exito: modal se cierra y, al reabrir, esta reseteado.
