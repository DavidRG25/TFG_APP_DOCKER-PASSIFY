# Implementacion y Fase B Manejo de archivos (20251116-2335)

## Problema
- En modo personalizado los archivos Dockerfile/compose/ZIP no quedaban asociados al servicio cuando la validacion fallaba o el build no se ejecutaba.
- El formulario no mostraba errores claros ni instrucciones sobre los archivos requeridos.
- Los ficheros seleccionados en Windows no eran detectados debido al atributo ccept limitado.

## Solucion
1. ServiceSerializer.validate exige el ZIP en modo Dockerfile/docker-compose.
2. ServiceViewSet.create captura ValidationError para peticiones HTMX y muestra la lista de errores en #form-errors. Se mueve la carga de archivos a un helper _attach_uploaded_files que guarda cada FileField usando el nombre original y la storage de Django.
3. 	emplates/containers/student_panel.html agrega el contenedor de errores, amplia el ccept de Dockerfile para admitir cualquier extension y suma modales informativos (icono �i�) explicando como preparar los ficheros.

## Archivos modificados
- containers/serializers.py
- containers/views.py
- 	emplates/containers/student_panel.html

## Flujo antes/despues
- *Antes*: el formulario enviaba Dockerfile sin ZIP y el backend respondia 400 sin detalle; los archivos no se asociaban y el boton �Dockerfile� quedaba inutil.
- *Despues*: al faltar un archivo obligatorio el modal muestra la lista de errores (sin recargar). Los ficheros se guardan en MEDIA_ROOT antes de iniciar el build y el usuario recibe modales de ayuda con sus requisitos.

## Consideraciones de seguridad
- Los mensajes de error provienen de DRF (texto controlado). Los modales contienen informacion estatica.

## Pruebas
- [ ] Crear servicio con Dockerfile + ZIP valido
- [ ] Intentar enviar Dockerfile sin ZIP: el modal debe mostrar el error
- [ ] Adjuntar ZIP sin Dockerfile: error asociado al campo
- [ ] Abrir los modales de ayuda
- [ ] Verificar que el boton Dockerfile abre el contenido tras crear el servicio
