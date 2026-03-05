# Testing y Validación: Edición Avanzada y Persistencia de Volúmenes

Este documento recoge los resultados teóricos y los pasos de verificación a seguir por el equipo QA o el usuario para certificar que la Fase 1 (Backend) y Fase 2 (Frontend) de la edición avanzada se han completado y operan de forma estable y robusta.

## Resumen de Cambios Verificables

1. **Catálogo**: Protegidos por defecto. El backend intercepta cualquier cambio en `perform_update()`.
2. **DockerHub**: El UI ahora expone y desbloquea el _tag_ de la imagen. La URL de actualización (PATCH) permite reemplazar esta imagen libremente.
3. **Persistencia (Volúmenes)**: Se introdujo un control cruzado llamado `keep_volumes` (UI en forma de switch y JSON boolean field). Evita el reseteo de BDD o pérdida de storage anclado si es verdadero.

---

## Suite de QA y Casos de Uso (Por ejecutar por el Usuario)

### 1. Interfaz de Usuario (UI/UX)

- [SI] **Visibilidad del Input DockerHub**: Acceder a la vista de edición de un servicio creado bajo el modo DockerHub (ej: nginx). Verificar que la tarjeta azul dice "Imagen de Dockerhub" y es un `<input>` editable, a diferencia del candado de antes.
- [SI] **Visibilidad del Switch de Persistencia**: Cerciorarse de que hay un switch prominente "Preservar Datos y Volúmenes (Recomendado)" activado por defecto.
- [SI] **Reactividad del Warning**: Apagar el switch de persistencia. La UI debería iluminar el div en color rojo suave, cambiar los bordes a peligro, y aparecer una alerta dramática señalando la purga inminente de la base de datos y archivos.
- [SI] **Sincronización Pre-Submit**: Al apagar la persistencia, guardar los cambios. Mirar los logs HTTP/Red asegurando que el body via`multipart/form-data` lleva consigocuidadosamente `keep_volumes=off` (o su homólogo falso).

### 2. Comportamiento en Servidor (API + Docker)

#### Test 2A: Mutación de Imagen Simple

- [SI] Cargar un contenedor DockerHub de `nginx:1.24`.
- [SI] Acceder, editar y transicionar a `nginx:latest`. Dejar `keep_volumes` encendido.
- [SI] Guardar.
- [SI] **Resultado esperado**: La barra transiciona a pantalla de logs automáticos. El contenedor anterior detiene, borra, y el nuevo `nginx:latest` se levanta en el mismo puesto o puerto de ser auto-asignado.

#### Test 2B: Retención Activa de Datos Reales (El Core del Feature)

- [SI] Desplegar una instancia o servicio de bases de datos desde DockerHub (ej: `mariadb:10`).
- [SI] Usar un conector y crear una tabla `TFG_TESTING_DATA` y un par de registros.
- [SI] Editar el servicio, dejar `keep_volumes` EN ON (modo persistente). Cambiar alguna variable de entorno o puerto. Guardar.
- [SI] Conectarse en la nueva iteración y correr el query.
- [SI] **Resultado esperado**: La tabla `TFG_TESTING_DATA` debe de pervivir. El sistema ha ejecutado un `volume_prune` / `--volumes=false` en background.

#### Test 2C: Purga Voluntaria (Destrucción Controlada)

- [SI] Ejecutar el paso anterior hasta tener una tabla poblada.
- [SI] Ir a editar el servicio, pero esta vez apagar el switch (Switch Off -> Warning Rojo). Cambiar variable o imagen y guardar.
- [SI] Intentar conectarse o leer.
- [SI] **Resultado esperado**: El sistema debe estar vacío de datos en el reinicio.

#### Test 2D: Comportamiento en Compose Multicontenedor

- [SI] Levantar un compose complejo con volúmenes declarados tipo `mysql_data:/var/lib/mysql`.
- [SI] Entrar en edición. Actualizar alguna capa mínima como el archivo `.zip` del frontend de React, dejando `keep_volumes` ON.
- [SI] **Resultado esperado**: El dockerd bajará la orquestación normal (`docker compose down`) PERO sin la bandera `--volumes`. Al subir, los datos de MySQL seguirán intactos para la aplicación web.

### Notas del Desarrollador para Aprobación

El backend transiciona la variable `_keep_volumes` y la emite directo al daemon. La API rest recibe silenciosamente tanto PATCH HTTP como serializadores form para soportar cualquier casuística de prueba de HTMX.
