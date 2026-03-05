# 🐳 Modo Custom: Docker Compose

Ideal para proyectos que ya tienen un entorno Docker definido mediante un fichero `docker-compose.yml`.

#### Parámetros Base:

- **mode**: `custom` ✅
- **code**: Archivo `.zip` con el código. (**Opcional**) ℹ️
- **docker_compose**: Archivo `docker-compose.yml`. ✅

---

#### 📝 Ejemplo 1: Stack con Código Local (ZIP + Compose)

Para proyectos donde el `docker-compose.yml` hace referencia a carpetas locales (ej: `build: .`) o monta volúmenes de código:

```bash
CURL -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-web-stack" \
  -F "mode=custom" \
  -F "code=@proyecto.zip" \
  -F "docker_compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

---

#### 📝 Ejemplo 2: Stack de Infraestructura (Solo Compose)

Para proyectos que solo orquestan imágenes oficiales (bases de datos, proxies, etc.) sin necesidad de código fuente propio:

```bash
CURL -X POST {{ PAASIFY_API_URL }}/containers/ \
  -H "Authorization: Bearer <TOKEN>" \
  -F "name=mi-infra-stack" \
  -F "mode=custom" \
  -F "docker_compose=@docker-compose.yml" \
  -F "project=1" \
  -F "subject=1"
```

> [!TIP]
> En este segundo caso, PaaSify no requerirá el archivo ZIP, ahorrando tiempo y ancho de banda en el despliegue.

---

#### ✅ Ventajas:

- 🏗️ **Configurable**: Define varios servicios dentro de uno.
- 🔄 **Auto-config**: PaaSify detecta automáticamente los puertos de escucha de tu fichero `.yml`.
