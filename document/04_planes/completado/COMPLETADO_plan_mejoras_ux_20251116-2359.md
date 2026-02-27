# Plan — Mejoras UX (Fase E) - 20251116-2359

## Objetivo
Completar la experiencia de usuario para la creacion/gestion de servicios personalizados:
- Mensajes claros durante la validacion HTMX.
- Instrucciones visibles para Dockerfile, docker-compose y ZIP.
- Feedback inmediato en logs/terminal/estados.

## Acciones planificadas
1. Refinar tooltips/modales de ayuda con ejemplos concretos y enlaces a la documentacion.
2. Añadir un checklist visual en el modal "Nuevo servicio" indicando pasos completados (asignatura seleccionada, archivos adjuntos, etc.).
3. Extender el contenedor de errores #form-errors para mostrar mensajes de exito (por ejemplo al adjuntar correctamente los archivos).
4. Incluir hx-indicator para mostrar spinner al enviar el formulario y botones de accion.
5. Actualizar 	esting_servicios_... con los nuevos pasos manuales para verificar la UX.

## Pruebas previas a cierre
- Crear servicio completo y verificar que el checklist y los tooltips se muestran correctamente.
- Simular errores frecuentes (sin ZIP, ZIP sin Dockerfile, etc.) y comprobar que los mensajes guian al usuario.
- Revisar la accesibilidad (tabindex, aria-label) de los iconos de ayuda y botones deshabilitados.
