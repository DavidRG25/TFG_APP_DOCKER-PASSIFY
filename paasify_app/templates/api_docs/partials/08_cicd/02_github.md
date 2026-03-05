# 🐙 8.1 GitHub Actions

GitHub Actions permite automatizar el ciclo de vida de tu aplicación directamente desde tu repositorio. Para usar estos ejemplos, crea un archivo en `.github/workflows/deploy.yml`.

---

### 1️⃣ Despliegue Directo (Simple Patch)

Cada vez que haces un `push` a la rama `main`, GitHub construye tu imagen y le dice a PaaSify que la actualice.

**URL Dinámica de la API en este entorno:** `{{ PAASIFY_API_URL }}`

```yaml
name: Simple Deploy
on:
  push:
    branches: [main] # Se dispara solo al subir cambios a main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4 # Descarga tu código

      - name: 🐳 Build & Push
        run: |
          # Definimos el nombre de la imagen usando el SHA del commit
          IMAGE=${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}

          # Login en DockerHub (usando un Token de DockerHub recomendado)
          echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin

          # Construimos y subimos
          docker build -t $IMAGE .
          docker push $IMAGE

      - name: 🚀 Update PaaSify
        run: |
          # Llamada a la API de PaaSify para pedirle que use la nueva imagen
          # Sustituye ${{ secrets.CONTAINER_ID }} por el ID numérico de tu contenedor
          CURL -X PATCH "{{ PAASIFY_API_URL }}/containers/${{ secrets.CONTAINER_ID }}/" \
            -H "Authorization: Bearer ${{ secrets.PAASIFY_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d "{\"image\": \"${{ secrets.DOCKERHUB_USERNAME }}/mi-app:${{ github.sha }}\"}"
```

---

### 2️⃣ Estrategia Inteligente (Create or Patch)

¿No quieres crear el servicio a mano en el panel la primera vez? Este script lo hace por ti. Si el servicio ya existe (lo busca por nombre), lo actualiza. Si no, lo crea desde cero.

```yaml
deploy-smart:
  runs-on: ubuntu-latest
  steps:
    - name: Smart Strategy
      run: |
        # API URL de PaaSify: {{ PAASIFY_API_URL }}
        API_URL="{{ PAASIFY_API_URL }}"
        TOKEN="${{ secrets.PAASIFY_TOKEN }}"
        IMAGE="${{ secrets.DOCKERHUB_USERNAME }}/my-app:${{ github.sha }}"

        # 1. Consultamos a PaaSify qué servicios tenemos en este proyecto
        # Asegúrate de configurar PROJECT_ID en tus Secrets
        RESPONSE=$(CURL -s -H "Authorization: Bearer $TOKEN" "$API_URL/containers/?project=${{ secrets.PROJECT_ID }}")

        # 2. Buscamos si existe alguno que se llame "my-service-name" y extraemos su ID
        ID=$(echo "$RESPONSE" | jq -r ".[] | select(.name == \"my-service-name\") | .id")

        if [ -n "$ID" ] && [ "$ID" != "null" ]; then
          # Caso A: El servicio ya existe, hacemos PATCH (Actualizar)
          echo "Actualizando ID: $ID"
          CURL -X PATCH "$API_URL/containers/$ID/" -H "Authorization: Bearer $TOKEN" \
               -H "Content-Type: application/json" -d "{\"image\": \"$IMAGE\"}"
        else
          # Caso B: No existe, hacemos POST (Crear)
          echo "Creando nuevo servicio..."
          CURL -X POST "$API_URL/containers/" -H "Authorization: Bearer $TOKEN" \
               -H "Content-Type: application/json" \
               -d "{\"name\": \"my-service-name\", \"image\": \"$IMAGE\", \"project\": ${{ secrets.PROJECT_ID }}, \"subject\": ${{ secrets.SUBJECT_ID }}, \"mode\": \"dockerhub\", \"keep_volumes\": true}"
        fi
```

---

### 3️⃣ Verificación de Versión y Despliegue

Ideal para proyectos grandes. Lee un archivo llamado `VERSION` en tu repo y solo hace el despliegue si esa versión no existe ya en DockerHub.

```yaml
check-and-deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Check Registry
      id: check
      run: |
        # Leemos la versión del archivo
        V=$(cat VERSION | tr -d ' ')

        # Consultamos a la API de DockerHub si ya existe ese tag
        HTTP=$(CURL -s -o /dev/null -w "%{http_code}" "https://hub.docker.com/v2/repositories/${{ secrets.DOCKERHUB_USERNAME }}/my-app/tags/$V/")

        # Si devuelve 200, es que ya existe
        if [ "$HTTP" = "200" ]; then 
          echo "exists=true" >> $GITHUB_OUTPUT
        else 
          echo "exists=false" >> $GITHUB_OUTPUT
        fi
```
