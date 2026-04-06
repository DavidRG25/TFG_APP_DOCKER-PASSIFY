# 🤖 8. Integración CI/CD

La integración continua y el despliegue continuo (CI/CD) permiten que tu aplicación en PaaSify se actualice automáticamente cada vez que realizas un cambio en tu repositorio de código.

La **forma recomendada** es usar la GitHub Action oficial de PaaSify, que reduce todo el proceso a una sola línea en tu workflow. Si prefieres hacerlo a mano, también tienes disponibles guías detalladas para [🐙 8.1 GitHub Actions](../github) y [🦊 8.2 GitLab CI](../gitlab) en el menú lateral.

---

## 🤖 GitHub Action Oficial de PaaSify

PaaSify dispone de su propia **GitHub Action oficial** que simplifica el despliegue a una sola línea. En lugar de escribir decenas de líneas de `curl` y `jq`, basta con añadir un bloque `uses:` en tu workflow.

**Repositorio de la Action:** [DavidRG25/paasify-deploy-action](https://github.com/DavidRG25/paasify-deploy-action)

**URL Dinámica de la API en este entorno:** `{{ PAASIFY_API_URL }}`

---

### ¿Qué hace la Action?

- ✅ Valida los parámetros según el modo elegido
- ✅ Busca si el servicio ya existe en PaaSify (por nombre)
- ✅ Si existe → actualiza (`PATCH`)
- ✅ Si no existe → crea (`POST`)
- ✅ Devuelve el `container_id` como output reutilizable

### ¿Qué NO hace la Action?

- ❌ No construye imágenes Docker (eso lo hace tu workflow antes)
- ❌ No hace push a DockerHub
- ❌ No se autentica en registries externos

---

### 🔑 Secrets que debes configurar en GitHub (Comunes)

Ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions** y añade esta configuración fundamental antes de empezar:

| Secret              | Descripción                                                   | Requerido siempre |
|---------------------|---------------------------------------------------------------|:-----------------:|
| `PAASIFY_API_URL`   | URL base de la API de PaaSify (sin `/` final)                 | ✅                |
| `PAASIFY_TOKEN`     | Tu token de API de PaaSify (obtenido en tu Perfil)           | ✅                |
| `PROJECT_ID`        | ID numérico de tu proyecto en PaaSify                        | ✅                |
| `SUBJECT_ID`        | ID numérico de tu asignatura en PaaSify                      | ✅                |
| `DOCKERHUB_USERNAME`| Tu usuario de DockerHub                                       | Solo modo `dockerhub` |
| `DOCKERHUB_TOKEN`   | Token de acceso de DockerHub (no tu contraseña)              | Solo modo `dockerhub` |

---

### 📋 Referencia de Parámetros de la Action

| Parámetro            | Descripción                                        | Modos que lo usan                        |
|----------------------|----------------------------------------------------|------------------------------------------|
| `mode`               | Modo de desplegue (`dockerhub`, `custom_dockerfile`, `custom_compose`) | Todos (obligatorio) |
| `paasify_api_url`    | URL base de la API                                 | Todos (obligatorio)                      |
| `paasify_token`      | Token de autenticación                             | Todos (obligatorio)                      |
| `name`               | Nombre único del servicio en PaaSify               | Todos (obligatorio)                      |
| `project_id`         | ID del proyecto                                    | Todos (obligatorio)                      |
| `subject_id`         | ID de la asignatura                                | Todos (obligatorio)                      |
| `image`              | Imagen Docker (ej: `usuario/app:latest`)           | Solo `dockerhub`                         |
| `internal_port`      | Puerto interno de la aplicación                    | `dockerhub` y `custom_dockerfile`        |
| `code_path`          | Ruta al directorio del código fuente               | `custom_dockerfile` y `custom_compose`   |
| `dockerfile_path`    | Ruta al Dockerfile                                 | Solo `custom_dockerfile`                 |
| `docker_compose_path`| Ruta al archivo docker-compose.yml                 | Solo `custom_compose`                    |

---

### 1️⃣ Modo `dockerhub` — Imagen pública

<div class="p-3 mb-3 rounded-3 shadow-sm border border-primary" style="background-color: #f8faff; border-left-width: 5px !important;">
    El caso más habitual y sencillo. Tu pipeline construye y sube la imagen a DockerHub (o GHCR), y la Action oficial simplemente le indica a PaaSify qué imagen remota debe usar.
    <hr class="my-2 text-primary">
    <strong>⚠️ Importante:</strong> PaaSify solo soporta imágenes <strong>públicas</strong> por ahora en modo <code>dockerhub</code>.
</div>

```yaml
name: Deploy to PaaSify

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: 🐳 Build & Push to DockerHub
        run: |
          echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin
          docker build -t ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }} .
          docker push ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: 🚀 Deploy to PaaSify
        uses: DavidRG25/paasify-deploy-action@v1
        with:
          mode: dockerhub
          paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
          paasify_token: ${{ secrets.PAASIFY_TOKEN }}
          name: mi-app
          image: ${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}
          internal_port: 8000
          project_id: ${{ secrets.PROJECT_ID }}
          subject_id: ${{ secrets.SUBJECT_ID }}
```

---

### 2️⃣ Modo `custom_dockerfile` — Código fuente + Dockerfile

<div class="p-3 mb-3 rounded-3 shadow-sm border border-success" style="background-color: #f3fcf6; border-left-width: 5px !important;">
    PaaSify compila la imagen localmente a partir de tu código comprimido dinámicamente. Muy útil si no quieres tener que publicar tu artefacto intermedio en DockerHub o si es un proyecto interno (código privado).
</div>

```yaml
name: Deploy Custom Dockerfile to PaaSify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: 🚀 Deploy to PaaSify
        uses: DavidRG25/paasify-deploy-action@v1
        with:
          mode: custom_dockerfile
          paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
          paasify_token: ${{ secrets.PAASIFY_TOKEN }}
          name: mi-app-dockerfile
          code_path: .
          dockerfile_path: ./Dockerfile
          internal_port: 8000
          project_id: ${{ secrets.PROJECT_ID }}
          subject_id: ${{ secrets.SUBJECT_ID }}
```

---

### 3️⃣ Modo `custom_compose` — Docker Compose

<div class="p-3 mb-3 rounded-3 shadow-sm border border-danger" style="background-color: #fff5f5; border-left-width: 5px !important;">
    Para infraestructuras complejas y multi-contenedor (por ejemplo, Web + Backend + Redis + Database). PaaSify orquesta automáticamente toda la pila levantándola como un proyecto completo y manejando el enrutamiento.
</div>

```yaml
name: Deploy Custom Compose to PaaSify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: 🚀 Deploy to PaaSify
        uses: DavidRG25/paasify-deploy-action@v1
        with:
          mode: custom_compose
          paasify_api_url: ${{ secrets.PAASIFY_API_URL }}
          paasify_token: ${{ secrets.PAASIFY_TOKEN }}
          name: mi-app-compose
          code_path: .
          docker_compose_path: ./docker-compose.yml
          project_id: ${{ secrets.PROJECT_ID }}
          subject_id: ${{ secrets.SUBJECT_ID }}
```

---

### Errores comunes

| Error                                    | Causa probable                                    | Solución                                                     |
|------------------------------------------|---------------------------------------------------|--------------------------------------------------------------|
| `401 Unauthorized`                       | Token inválido o expirado                         | Regenera tu token en el panel de PaaSify y actualiza el secret |
| `403 Forbidden`                          | El `project_id` o `subject_id` no te pertenece   | Verifica los IDs en tu panel de PaaSify                       |
| `Dockerfile not found`                   | La ruta `dockerfile_path` no existe en el repo    | Comprueba que el fichero existe y la ruta es correcta         |
| `docker-compose.yml not found`           | La ruta `docker_compose_path` no existe           | Comprueba la ruta del archivo compose                         |
| La imagen no arranca en modo `dockerhub` | La imagen es privada en DockerHub                 | Cambia la imagen a pública o usa modo `custom_dockerfile`     |
