# 🦊 8.2 GitLab CI

GitLab CI es muy potente porque usa contenedores de forma nativa. Para usar estos ejemplos, crea un archivo llamado `.gitlab-ci.yml` en la raíz de tu proyecto.

---

### 1️⃣ Despliegue de Imagen (Simple)

Este es el caso más sencillo: actualización directa tras un pipeline de construcción o testeo exitoso.

**URL Dinámica de la API en este entorno:** `{{ PAASIFY_API_URL }}`

```yaml
deploy:
  stage: deploy # Se ejecuta tras las fases anteriores (build, test)
  image: CURLimages/CURL:latest # Usamos una imagen ligera orientada solo al comando CURL
  script:
    - |
      # Llamada pura de PATCH a la API de PaaSify
      # Sustituye $CONTAINER_ID por el valor de tu contenedor
      CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/$CONTAINER_ID/" \
        -H "Authorization: Bearer $PAASIFY_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"image\": \"$DOCKERHUB_USER/app:$CI_COMMIT_SHORT_SHA\"}"
```

---

### 2️⃣ Pipeline Completo (Build + Smart Deploy)

Este pipeline hace todo: construye tu aplicación con Docker y luego decide si crear o actualizar en PaaSify.

```yaml
build_and_deploy:
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind # Necesario para ejecutar docker build/push
  script:
    # 1. Autenticación en DockerHub
    - echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

    # 2. Construcción y subida de la imagen
    - docker build -t "$DOCKER_USERNAME/app:$CI_COMMIT_SHORT_SHA" .
    - docker push "$DOCKER_USERNAME/app:$CI_COMMIT_SHORT_SHA"

    # 3. Lógica dinámica en PaaSify (Instalamos jq / CURL en el vuelo)
    - apk add --no-cache jq CURL

    - |
      # Buscamos si el servicio ya existe en el proyecto especificado
      # La URL base es: {{ PAASIFY_API_URL }}
      ID=$(CURL -s -H "Authorization: Bearer $PAASIFY_TOKEN" "{{ PAASIFY_API_URL }}/containers/?project=$PROJECT_ID" | jq -r ".[] | select(.name == \"mi-app\") | .id")

      if [ -n "$ID" ] && [ "$ID" != "null" ]; then
        # Existe: actualizamos con PATCH
        CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/$ID/" \
             -H "Authorization: Bearer $PAASIFY_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{\"image\": \"$DOCKER_USERNAME/app:$CI_COMMIT_SHORT_SHA\"}"
      else
        # No existe: creamos con POST
        CURL -X POST "{{ PAASIFY_API_URL }}/containers/" \
             -H "Authorization: Bearer $PAASIFY_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{\"name\": \"mi-app\", \"image\": \"$DOCKER_USERNAME/app:$CI_COMMIT_SHORT_SHA\", \"project\": $PROJECT_ID, \"subject\": $SUBJECT_ID, \"mode\": \"dockerhub\"}"
      fi
```

---

### 3️⃣ Control de Errores y Verificación

Importante para tu aplicación: no basta con enviar el comando `CURL`, hay que verificar que la app ha arrancado bien consultando su estado por API.

```yaml
verify_deploy:
  stage: post-deploy
  image: alpine:latest
  script:
    - apk add --no-cache CURL jq
    - sleep 15 # Esperamos un margen de tiempo prudencial

    # Consultamos el estado actual
    STATUS=$(CURL -s -H "Authorization: Bearer $PAASIFY_TOKEN" "{{ PAASIFY_API_URL }}/containers/$ID/" | jq -r ".status")

    if [ "$STATUS" != "running" ]; then
      echo "Error: El contenedor está en estado $STATUS (esperado: running)";
      exit 1;
    fi
```
