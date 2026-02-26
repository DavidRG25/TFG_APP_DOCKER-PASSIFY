# 🚀 4. Crear Servicio

Endpoint principal para desplegar servicios en PaaSify. Soporta tres modos principales de despliegue según tus necesidades.

**Endpoint Principal:** `POST /api/containers/`

---

### 📋 Parámetros Comunes

Campos disponibles en **todos** los modos de despliegue:

| Campo              | Tipo   | Obligatorio | Descripción                                                      |
| :----------------- | :----- | :---------- | :--------------------------------------------------------------- |
| **name**           | string | ✅ **Sí**   | Nombre del servicio. (ej: `mi-app`).                             |
| **project**        | int    | ✅ **Sí**   | ID del proyecto (obtener desde `GET /api/projects/`).            |
| **subject**        | int    | ✅ **Sí**   | ID de la asignatura (obtener desde `GET /api/subjects/`).        |
| **container_type** | string | ⭕ No       | Clasificación: `web` (default), `api`, `database`, `misc`.       |
| **is_web**         | bool   | ⭕ No       | `true` (default) o `false`. Si es `true`, aparece el acceso web. |
| **keep_volumes**   | bool   | ⭕ No       | `true` (default) o `false`. Conserva los datos tras reinicios.   |

> 💡 **Tip Educativo**: El nombre del servicio es **auto-normalizado**. Si envías `Mi APP Web`, PaaSify lo convertirá internamente a `mi-app-web` para cumplir con los estándares de red de Docker.
