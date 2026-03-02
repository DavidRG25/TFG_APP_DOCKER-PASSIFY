# 🔄 Re-desplegar Imagen

Función específica para el **Modo DockerHub**. Permite forzar la descarga de una imagen con el mismo `tag` (ej: `latest`) para actualizar el código sin cambiar la configuración del contenedor.

**Endpoint:** `PATCH /api/containers/{id}/`

---

#### 📝 Parámetros:

| Campo     | Tipo   | Valor                    | Descripción                                    |
| :-------- | :----- | :----------------------- | :--------------------------------------------- |
| **image** | string | ej: `mi-repo/web:latest` | El nombre de la imagen que quieres actualizar. |

#### 📝 Ejemplo CURL de Actualización:

```bash
# Actualizamos el contenedor 123 con la última imagen de DockerHub
CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"image": "mi-usuario/mi-app:latest"}'
```

#### ✅ Ventajas:

- 🚀 **Velocidad**: Solo recrea el contenedor sobre la misma infraestructura de red.
- 🔄 **Persistencia**: Si tienes `keep_volumes: true`, los datos de tu base de datos o carpetas persistentes no se perderán tras la actualización.
