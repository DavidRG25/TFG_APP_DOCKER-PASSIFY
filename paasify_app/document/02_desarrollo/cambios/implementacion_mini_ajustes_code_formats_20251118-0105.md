Implementacion - Mini ajustes code formats (20251118-0105)

Problema
- El formulario solo aceptaba ZIP como codigo fuente, pero los alumnos tambien suben RAR.
- La validacion de backend rechazaba extensiones distintas de .zip.

Cambios realizados
- Backend: ampliada la lista de extensiones permitidas a {".zip", ".rar"} en `containers/services.py`.
- Frontend: el input de archivo en `templates/containers/student_panel.html` ahora acepta `.zip,.rar,*/*` para permitir seleccionar RAR y mantener compatibilidad con Dockerfile sin extension.

Archivos modificados
- containers/services.py
- templates/containers/student_panel.html

Pruebas sugeridas
- Crear servicio personalizado adjuntando `archivos_dockerfile.rar`: debe pasar la validacion y crear el servicio.
- Probar con ZIP: sigue aceptado.
- Probar con extension no permitida (ej. .7z): debe mostrar error de validacion.
