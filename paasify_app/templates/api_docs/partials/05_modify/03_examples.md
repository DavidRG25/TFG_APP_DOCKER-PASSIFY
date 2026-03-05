# 📝 Ejemplos de Modificación

A continuación se presentan casos de uso reales para actualizar tus servicios mediante peticiones `PATCH`. Estos ejemplos cubren las situaciones más comunes que encontrarás durante el desarrollo y mantenimiento.

---

### 1️⃣ Actualización de Imagen (CD Directo)

El caso más común: has subido una nueva versión a DockerHub y quieres que PaaSify la despliegue sin cambiar puertos ni variables.

```bash
# Cambiamos la imagen del contenedor 123 a la versión v2
CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"image": "mi-usuario/mi-app:v2"}'
```

---

### 2️⃣ Cambio de Variables de Entorno

Ideal para activar modos de depuración (`DEBUG`) o rotar credenciales de bases de datos externas.

```bash
# Activamos el modo DEBUG y cambiamos una API KEY
CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "env_vars": {
        "DEBUG": "True",
        "API_KEY": "nueva_clave_de_seguridad"
    }
  }'
```

---

### 3️⃣ Cambio de Nombre y Puerto Interno

Si decides reestructurar tu aplicación o cambiar el puerto en el que escucha tu servidor (ej: de 3000 a 8080).

```bash
# Renombramos el servicio y actualizamos el puerto interno
CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nueva-web-produccion",
    "internal_port": 8080
  }'
```

---

### 4️⃣ Modificación masiva (Full Patch)

Puedes combinar todos los campos en una única petición para realizar un cambio estructural completo.

```bash
CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/123/" \
  -H "Authorization: Bearer <TU_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "microservicio-auth",
    "image": "docker.io/library/nginx:alpine",
    "container_type": "api",
    "is_web": true,
    "env_vars": {
        "REPLICA_ID": "node-1"
    }
  }'
```

---

### ✅ Verificación del Cambio

Tras realizar un `PATCH`, PaaSify responde con el objeto del contenedor actualizado. Es recomendable guardar el `id` y verificar el `status` para asegurar que el re-arranque ha sido exitoso.
