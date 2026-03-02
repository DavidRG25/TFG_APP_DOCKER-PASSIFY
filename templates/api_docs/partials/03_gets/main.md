# 🔍 3. Consultas (GETs)

La consulta de recursos es el punto de partida para cualquier automatización. Antes de crear o modificar un servicio, necesitas conocer los identificadores (`ID`) de tus proyectos y asignaturas.

---

### 📋 Patrones de Respuesta

Todos los endpoints de consulta de PaaSify siguen una estructura JSON predecible:

- **Listas**: Devuelven un `Array []` de objetos.
- **Detalle**: Devuelven un `Objeto {}` con los campos del recurso.

| Recurso        | Endpoint           | Información Clave que Obtienes                          |
| :------------- | :----------------- | :------------------------------------------------------ |
| **Directorio** | `/api/projects/`   | IDs de proyectos para tus futuros despliegues.          |
| **Académico**  | `/api/subjects/`   | Relación de asignaturas y años lectivos.                |
| **Inventario** | `/api/containers/` | Estado real (`running`, `stopped`) y puertos asignados. |

---

### ⚡ Filtrado Avanzado

Recuerda que puedes combinar parámetros en la URL para obtener solo lo que necesitas:

> `GET /api/containers/?project=5&subject=1`

Pulsando en los apartados de la izquierda podrás acceder a ejemplos de código CURL y esquemas de respuesta para cada recurso.
