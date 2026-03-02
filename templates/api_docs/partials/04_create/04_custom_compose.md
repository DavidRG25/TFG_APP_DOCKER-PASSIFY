# 🐳 Modo Custom: Docker Compose

Ideal para proyectos que ya tienen un entorno Docker definido mediante un fichero `docker-compose.yml`.

#### Parámetros Base:

- **mode**: `custom` ✅
- **code**: Archivo `.zip` con el código. ✅
- **docker_compose**: Archivo `docker-compose.yml`. ✅

---

#### 📝 Ejemplo: Composición de Servicios

Para proyectos que incluyen bases de datos u otros servicios secundarios:

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

#### ✅ Ventajas:

- 🏗️ **Configurable**: Define varios servicios dentro de uno.
- 🔄 **Auto-config**: PaaSify detecta automáticamente los puertos de escucha de tu fichero `.yml`.
