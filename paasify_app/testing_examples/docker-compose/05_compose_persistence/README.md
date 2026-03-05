# Ejemplo de Persistencia con Docker Compose

Este directorio contiene un ejemplo básico para comprobar el funcionamiento de la persistencia de bases de datos utilizando la opción "Preservar Datos y Volúmenes" de PaaSify en servicios de tipo Docker Compose (Stack).

## ¿Qué contiene?

- **`docker-compose.yml`**: Configuración de un entorno con un contenedor MySQL y una red interna básica. Incluye la definición de un volumen mapeado (`/var/lib/mysql`) para garantizar que la base de datos se almacene.
- **Volúmenes Nombrados**: Por defecto, se utiliza el volumen que el sistema Docker Compose auto-cree u orqueste.

## ¿Qué debes probar?

1. Crea un nuevo servicio seleccionando la opción **Docker Compose** y sube el archivo `.yml`.
2. Una vez desplegado, accede de alguna forma a la base de datos (por ejemplo, a través de consola remota, phpmyadmin u otra conexión vinculada a su red) y crea algunos registros falsos.
3. En la interfaz web de PaaSify, entra a editar el servicio, cerciórate de que el botón de **"Preservar Datos" (ON)** esté activo y dale a _Guardar_.
4. Cuando el contenedor vuelva a levantar, verás que tus tablas y datos creados siguen estando ahí.
5. Vuelve a editar el servicio, pero esta vez desactiva el interruptor **(Preservar Datos = OFF)**. Al reiniciar, PaaSify destruirá todo el volumen de MySQL y la base de datos volverá a sus configuraciones de fábrica completamente vacías.
