# Ejemplo de Persistencia con Dockerfile

Este directorio contiene un simple `Dockerfile` hecho para probar cómo PaaSify maneja los volúmenes para imágenes con instrucciones internas tipo `VOLUME`.

## ¿Qué contiene?

- **`Dockerfile`**: Es una pequeña base de Debian/Ubuntu o Alpine con configuraciones mínimas que emula la necesidad de persistir algún archivo (`/data` o `/app/data`).

## ¿Qué debes probar?

1. Crea un nuevo servicio usando la pestaña de **Despliegue de Código Custom (Dockerfile)** en la UI.
2. Sube el `.zip` o archivo con este `Dockerfile` y configura el contenedor.
3. Tras que termine el build, sube, entra a la Terminal Web de la plataforma del contenedor o ábrela y crea un archivo de texto en el directorio con orden de persistencia. Por ejemplo: `echo "datos_privados" > /data/secreto.txt`.
4. En el panel de PaaSify pulsa **Editar**. Verifica que el **switch para Preservar Datos** se encuentre activado (ON) y re-aplica / guarda. PaaSify forzará una reconstrucción / purga del contenedor existente.
5. Al volver a abrir la terminal del contenedor nuevo, debes ver que `cat /data/secreto.txt` sigue existiendo y persistido correctamente su contenido.
6. Realiza un segundo Edit, y **deshabilita / borra la preservancia (OFF)**. Tras regenerar, el contenedor estará de fábrica y el archivo de prueba se habrá perdido para siempre.
