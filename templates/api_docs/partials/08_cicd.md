# 🤖 Integración CI/CD

PaaSify está diseñado para integrarse fácilmente con flujos de trabajo de Integración y Despliegue Continuo (CI/CD). Esta guía te permitirá automatizar el despliegue de tus aplicaciones directamente desde GitHub o GitLab.

---

## 🚀 Flujo Recomendado

Para una integración profesional, el flujo de trabajo estándar es:

1.  **Código**: Subes cambios a tu repositorio (GitHub/GitLab).
2.  **Build**: Tu pipeline de CI construye una imagen de Docker.
3.  **Registry**: La imagen se sube a DockerHub.
4.  **Deploy**: Tu pipeline llama a la API de PaaSify para actualizar el servicio con la nueva imagen.

> 💡 **Tip de Oro**: No uses el tag `latest` para automatizaciones. Usa el **Commit SHA** como tag de la imagen. Esto permite trazabilidad total y facilita volver a una versión anterior si algo falla.

---

## 🐙 Ejemplo: GitHub Actions

Crea el archivo `.github/workflows/deploy.yml` en tu repositorio. Este workflow se ejecutará automáticamente en cada `push` a la rama `main`.

```yaml
name: Build & Deploy to PaaSify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout código
        uses: actions/checkout@v4

      - name: 🐳 Login en DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: 🛠️ Build y Push de la imagen
        run: |
          # Usamos el SHA corto del commit como tag
          TAG=$(echo ${{ github.sha }} | cut -c1-7)
          IMAGE_NAME=${{ secrets.DOCKERHUB_USERNAME }}/mi-app:$TAG

          docker build -t $IMAGE_NAME .
          docker push $IMAGE_NAME
          echo "IMAGE=$IMAGE_NAME" >> $GITHUB_ENV

      - name: 🚀 Despliegue en PaaSify (PATCH)
        run: |
          curl -X PATCH "${{ secrets.PAASIFY_API_URL }}/containers/${{ secrets.CONTAINER_ID }}/" \
            -H "Authorization: Bearer ${{ secrets.PAASIFY_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d "{\"image\": \"${{ env.IMAGE }}\"}"
```

---

## 🦊 Ejemplo: GitLab CI/CD

Añade esto a tu archivo `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - deploy

build_image:
  stage: build
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  script:
    - docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_TOKEN
    - docker build -t $DOCKERHUB_USERNAME/mi-app:$CI_COMMIT_SHORT_SHA .
    - docker push $DOCKERHUB_USERNAME/mi-app:$CI_COMMIT_SHORT_SHA

deploy_paasify:
  stage: deploy
  image: curlimages/curl:latest
  script:
    - |
      curl -X PATCH "$PAASIFY_API_URL/containers/$CONTAINER_ID/" \
        -H "Authorization: Bearer $PAASIFY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"image\": \"$DOCKERHUB_USERNAME/mi-app:$CI_COMMIT_SHORT_SHA\"}"
```

---

## 🧠 Estrategia: "Create or Patch"

Si quieres que tu script sea capaz de crear el servicio si no existe, o actualizarlo si ya existe, puedes usar este script de Bash en tu pipeline:

```bash
# 1. Buscar si el servicio ya existe por nombre dentro del proyecto
EXISTING_ID=$(curl -s -X GET "$PAASIFY_API_URL/containers/?project=$PROJECT_ID" \
  -H "Authorization: Bearer $PAASIFY_TOKEN" | \
  jq -r ".[] | select(.name == \"mi-app-nombre\") | .id")

if [ -z "$EXISTING_ID" ]; then
  echo "🚀 Creando nuevo servicio..."
  curl -X POST "$PAASIFY_API_URL/containers/" \
    -H "Authorization: Bearer $PAASIFY_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"mi-app-nombre\", \"image\": \"$IMAGE\", \"project\": $PROJECT_ID, \"subject\": $SUBJECT_ID, \"mode\": \"dockerhub\"}"
else
  echo "🔄 Actualizando servicio existente (ID: $EXISTING_ID)..."
  curl -X PATCH "$PAASIFY_API_URL/containers/$EXISTING_ID/" \
    -H "Authorization: Bearer $PAASIFY_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"image\": \"$IMAGE\"}"
fi
```

---

## 🛠️ Configuración de Secretos

Para que esto funcione de forma segura, **NUNCA** pongas tus tokens directamente en el código del YAML.

1.  **En GitHub**: Ve a `Settings` > `Secrets and variables` > `Actions` > `New repository secret`.
2.  **En GitLab**: Ve a `Settings` > `CI/CD` > `Variables`.

**Variables necesarias:**

- `PAASIFY_TOKEN`: Tu token de desarrollo (obtenido en tu Perfil).
- `PAASIFY_API_URL`: La URL base de la API (ej: `http://paasify.tu-uni.es/api`).
- `CONTAINER_ID`: El ID del contenedor que quieres actualizar.
- `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`.

---

## ✅ Buenas Prácticas de CI/CD

- 🚫 **No uses `latest`**: Siempre usa tags específicos (SHA del commit o versión semántica).
- 💾 **Persistencia**: Asegúrate de que el servicio tenga `keep_volumes: true` si necesitas que la DB no se borre en cada despliegue.
- 🔍 **Verificación**: Puedes añadir un paso final de `curl` al endpoint `GET /api/containers/{id}/` para verificar que el estado pase a `running` tras el despliegue.
- 📋 **Logs**: Si el despliegue falla, consulta los logs mediante `/api/containers/{id}/logs/`.
- 🔗 **Trailing Slash**: Recuerda terminar siempre las URLs de la API con `/` (ej: `/containers/123/`).

---
