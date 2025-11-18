# Implementacion y Fase A Validacion ( 20251116-2326 )

## Problema
- El formulario personalizado permitda enviar Dockerfile/compose sin ZIP obligatorio y los archivos no se subian correctamente.
- El serializer devolvia 400 generico que HTMX no mostraba.
- No existian instrucciones sobre los archivos requeridos.

## Soluci�n
1. ServiceSerializer.validate exige code cuando se elige Dockerfile o compose y mantiene mensajes por campo.
2. ServiceViewSet.create captura ValidationError y devuelve un fragmento HTML dirigido a #form-errors usando HX-Retarget/HX-Reswap.
3. student_panel.html incorpora contenedor de errores, amploa accepta para Dockerfile, añade iconos pin con modales de ayuda y detalla que el ZIP es obligatorio.

## Ficheros modificados
- containers/serializers.py
- containers/views.py
- templates/containers/student_panel.html

## Flujo antes/despues
- *Antes*: al seleccionar "Configuracion personalizada" sin ZIP, el formulario enviaba la peticion, recibia un 400 y la UI quedaba en blanco; los botones "Dockerfile" no abran nada porque no se guardaba el archivo.
- *Despues*: la validacion se realiza antes de guardar; los errores aparecen en el mismo modal, el usuario ve por que falta el ZIP y cuenta con modales informativos. Solo al cumplir los requisitos se lanza el proceso.

## Consideraciones de seguridad
- Los mensajes de error son sanitizados al generar el HTML (contenido controlado por DRF). No se exponen rutas internas.
- Los modales solo muestran texto estetico.

## Pruebas
- [ ] Crear servicio con Dockerfile + ZIP -> pasa validacion y se lanza contenedor.
- [ok] Intentar Dockerfile sin ZIP -> modal muestra error "Debes adjuntar el codigo fuente".
- [ok] Adjuntar ZIP sin Dockerfile/compose -> error controlado.
- [ok] Verificar iconos de ayuda y contenedor de errores en la UI.
