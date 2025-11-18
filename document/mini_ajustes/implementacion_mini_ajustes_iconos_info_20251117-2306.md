# Implementacion � Mini ajustes iconos info (20251117-2306)

## Problema
- Iconos poco visibles que cerraban el modal al abrir la ayuda. El file picker de Windows no dejaba seleccionar Dockerfile sin extension salvo eligiendo "Todos los archivos".

## Solucion
- Popovers de Bootstrap en Dockerfile, docker-compose, ZIP y puerto personalizado (no cierran el modal principal).
- Icono oficial bi-info-circle con estilo btn-sm btn-outline-info, aria-label y mayor contraste.
- Textos mas claros: compose (version 3 o superior), Dockerfile (FROM/COPY/CMD), ZIP (codigo sin venv), puerto (40000-50000). Popovers inicializados en DOMContentLoaded.
- Entrada Dockerfile con accept="*/*" para permitir seleccionar archivos sin extension en Windows.

## Archivos modificados
- templates/containers/student_panel.html

## Flujo antes/despues
- Antes: al tocar la "i" se cerraba el formulario y la ayuda era poco visible.
- Despues: los popovers se muestran en el mismo modal y son mas legibles.

## Pruebas
- [ok] Abrir popover de Dockerfile sin que se cierre el modal.
- [ok] Revisar visibilidad del icono en todos los campos (Dockerfile, compose, ZIP, puerto).
- [ok] Confirmar textos en ASCII y popovers funcionales.
- [ok] En Windows, seleccionar un archivo llamado "Dockerfile" sin activar "Todos los archivos".
