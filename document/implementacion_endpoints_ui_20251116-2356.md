# Implementacion — Fase D Endpoints y UI (20251116-2356)

## Cambios
1. 	emplates/containers/_service_rows.html
   - Boton "Eliminar" usa cadena ASCII y la terminal ahora se deshabilita cuando no existe container_id o el servicio no esta en RUNNING, mostrando un tooltip aclaratorio.
2. containers/views.py::_serve_code
   - Devuelve mensaje (archivo no disponible) en lugar de Http404 cuando no existe Dockerfile/compose.
3. containers/views.py::terminal_view
   - Valida que el contenedor exista y este en ejecucion usando Docker Python; devuelve mensajes claros si no esta accesible.

## Flujo antes/despues
- *Antes*: el boton "Terminal" aparecia habilitado aunque el contenedor no existiera, produciendo error _PipeSocket. El endpoint Dockerfile retornaba 404.
- *Despues*: la terminal solo se habilita cuando hay contenedor activo y las respuestas informan al usuario si Docker no esta disponible. El boton Dockerfile muestra un mensaje amigable cuando falta el archivo.

## Pruebas
- [ ] Servicio en estado ERROR: boton Terminal deshabilitado.
- [ ] Abrir Dockerfile inexistente: aparece el mensaje (archivo no disponible).
- [ ] Apagar contenedor manualmente y abrir terminal: la vista responde "El contenedor no existe".
