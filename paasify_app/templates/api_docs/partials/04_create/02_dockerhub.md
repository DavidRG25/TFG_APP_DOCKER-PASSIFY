# 🐳 Modo DockerHub

El modo `dockerhub` te permite desplegar **cualquier imagen pública** desde DockerHub sin limitaciones.

#### Parámetros Específicos:

| Campo             | Valor            | Descripción                           |
| :---------------- | :--------------- | :------------------------------------ |
| **mode**          | `dockerhub`      | ✅ **Requerido**.                     |
| **image**         | ej: `python:3.9` | Imagen pública (usuario/imagen:tag).  |
| **internal_port** | entero           | Puerto interno de escucha (ej: 3000). |
| **env_vars**      | objeto           | Variables de entorno (opcional).      |

#### 📝 Ejemplo CURL:

```bash
CURL -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-api-python",
    "mode": "dockerhub",
    "image": "python:3.9-slim",
    "internal_port": 5000,
    "env_vars": {
      "DEBUG": "True",
      "SECRET_KEY": "xyz"
    },
    "project": 1,
    "subject": 1,
    "container_type": "api"
  }'
```

#### ✅ Ventajas:

- 🌍 **Libertad**: Acceso a millones de imágenes públicas.
- 🎨 **Configuración**: Tú defines los puertos y variables.
