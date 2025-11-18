Implementacion - Mini ajustes nombre unico (20251118-0120)

Problema
- Un alumno podia crear multiples servicios con el mismo nombre, generando confusion en la lista y en los recursos Docker asociados.

Solucion
- Se valida en el serializer que un usuario autenticado no pueda repetir nombre de servicio, excluyendo los que tienen status "removed". En edicion, se excluye la instancia actual para permitir cambios de otros campos.

Archivos modificados
- containers/serializers.py

Comportamiento antes
- No habia restriccion de nombres duplicados por alumno.

Comportamiento despues
- Si el alumno intenta crear o guardar un servicio con un nombre que ya usa en servicios activos, recibe error de validacion en el campo name.

Pruebas sugeridas
- Crear servicio "demo" y luego intentar crear otro "demo" con el mismo usuario: debe mostrar error en name.
- Eliminar un servicio y volver a crear con el mismo nombre: debe permitirse porque se excluye status "removed".
- Editar un servicio cambiando otros campos pero manteniendo el mismo nombre: debe permitir la actualizacion.
