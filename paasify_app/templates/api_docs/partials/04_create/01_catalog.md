# 📚 Modo Catálogo (Default)

Despliega una imagen pre-aprobada del catálogo oficial de la facultad. Para usar el catálogo usa el modo `default`.

#### Parámetros Específicos:

| Campo     | Tipo   | Valor          | Descripción                          |
| :-------- | :----- | :------------- | :----------------------------------- |
| **mode**  | string | `default`      | (Opcional, es el valor por defecto). |
| **image** | string | (ver catálogo) | Ejemplo: `wordpress:latest`.         |

#### 📝 Ejemplo CURL:

```bash
CURL -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mi-blog",
    "image": "wordpress:latest",
    "project": 1,
    "subject": 1,
    "container_type": "web"
  }'
```

#### ✅ Ventajas:

- ⚡ **Velocidad**: Las imágenes ya están descargadas en los nodos.
- 🔒 **Seguridad**: Imágenes optimizadas por la universidad.
