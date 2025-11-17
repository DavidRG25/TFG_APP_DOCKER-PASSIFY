# Implementacion � Mini ajustes iconos info (20251117-2256)

## Problema
- Los iconos "i" eran poco visibles y abrir la ayuda cerraba el modal de nuevo servicio.

## Solucion
- Se reemplazo el uso de modales secundarios por popovers de Bootstrap en los campos Dockerfile, docker-compose y ZIP.
- Se uso un estilo btn-sm btn-outline-info con aria-label y contraste para mejorar la visibilidad.
- Se inicializan los popovers en DOMContentLoaded sin cerrar el modal principal.

## Archivos modificados
- templates/containers/student_panel.html

## Flujo antes/despues
- *Antes*: al tocar la "i" se cerraba el formulario y la ayuda era poco visible.
- *Despues*: los popovers se muestran sobre el mismo modal sin cerrarlo, con texto ASCII y mejor contraste.

## Pruebas
- [ ] Abrir popover de Dockerfile sin que se cierre el modal.
- [ ] Revisar visibilidad del boton "i" en cada campo.
