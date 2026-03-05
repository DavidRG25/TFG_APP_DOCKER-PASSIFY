# 🛠️ Configuración Editable

El endpoint `PATCH` es la herramienta preferida para realizar ajustes finos sin interrumpir el flujo de trabajo. Puedes actualizar casi cualquier campo dinámico del contenedor.

---

### Campos que puedes modificar:

| Campo              | Tipo   | Soporte      | Descripción                                                |
| :----------------- | :----- | :----------- | :--------------------------------------------------------- |
| **name**           | string | Todos        | Cambia el nombre visual y de red del servicio.             |
| **image**          | string | DockerHub    | Actualiza a una versión superior o cambia de imagen.       |
| **internal_port**  | int    | DockerHub/DF | Cambia el puerto donde escucha tu app.                     |
| **env_vars**       | JSON   | Todos        | Añade o quita variables de entorno sin borrar el servicio. |
| **container_type** | string | Todos        | Cambia la categoría (Web, API, DB).                        |
| **is_web**         | bool   | Todos        | Muestra u oculta el botón de acceso.                       |
| **keep_volumes**   | bool   | Todos        | Define si quieres persistencia tras reinicios.             |

---

### Campos Inmutables

Por seguridad y coherencia de datos, estos campos no pueden cambiarse:

- `owner`: El propietario del servicio es fijo.
- `mode`: No puedes pasar de un servicio de "Catálogo" a uno "Personalizado" ni viceversa.
- `subject` / `project`: Los servicios pertenecen a un contexto académico inamovible.

---

### 🔐 Seguridad en Modificaciones

PaaSify realiza un **doble chequeo** en cada `PATCH`:

1.  **Propiedad**: Verifica que el token pertenece al dueño del contenedor.
2.  **Estado**: Si el contenedor está en estado `error`, intentará una limpieza profunda antes de aplicar el nuevo despliegue.
3.  **Conflictos de Puerto**: Si cambias el nombre, se asegura de que el nuevo nombre no esté cogido en la red del proyecto.
