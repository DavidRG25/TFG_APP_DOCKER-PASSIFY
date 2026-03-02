#!/usr/bin/env bash
set -e

# ============================================================================
# build_and_push.sh - Construir, verificar y publicar imágenes de PaaSify
# ============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION_FILE="version.txt"
CREDS_FILE=".docker_credentials"
REPO="davidrg25/paasify"

echo "=========================================="
echo "    PaaSify - Docker Build & Push Tool    "
echo "=========================================="

# 1. Leer versión
if [ ! -f "$VERSION_FILE" ]; then
    echo "[!] Error: No se encontró el archivo $VERSION_FILE"
    echo "Por favor, crea el archivo con la versión, por ejemplo: echo 'v10.1.0' > version.txt"
    exit 1
fi
VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
echo "[*] Intentando desplegar la versión: $VERSION"

# 2. Verificar archivo de credenciales
if [ ! -f "$CREDS_FILE" ]; then
    echo "[!] Error: No se encontró el archivo $CREDS_FILE"
    echo "Crea un archivo en la raíz llamado .docker_credentials con:"
    echo "DOCKER_USER=tu_usuario"
    echo "DOCKER_PASS=tu_contraseña_o_token"
    exit 1
fi

# Cargar variables de forma segura
source "$CREDS_FILE"

# 3. Comprobar instalación de jq (necesaria para interactuar con la API)
if ! command -v jq &> /dev/null; then
    echo "[!] Error: 'jq' no está instalado. Instálalo para continuar (ej: choco install jq o apt-get install jq)."
    exit 1
fi

# 4. Comprobar si la versión ya existe en Docker Hub
echo "[*] Verificando en Docker Hub si la versión $VERSION ya existe..."
# Obtener token de la API de Docker Hub
TOKEN=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"username\": \"$DOCKER_USER\", \"password\": \"$DOCKER_PASS\"}" https://hub.docker.com/v2/users/login/ | grep -oP '"token":"\K[^"]+')

if [ -z "$TOKEN" ]; then
    # Por si usamos Mac/Linux puro sin PCRE
    TOKEN=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"username\": \"$DOCKER_USER\", \"password\": \"$DOCKER_PASS\"}" https://hub.docker.com/v2/users/login/ | jq -r .token)
fi

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "[!] Error: Credenciales de Docker Hub incorrectas en $CREDS_FILE o API inaccesible."
    exit 1
fi

# Consultar la etiqueta
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: JWT $TOKEN" "https://hub.docker.com/v2/repositories/${REPO}/tags/${VERSION}/")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "[!] ALERTA: La versión $VERSION ya existe en Docker Hub."
    echo "    Sube la versión editando el archivo $VERSION_FILE si quieres crear una nueva."
    exit 1
fi

echo "[✓] La versión $VERSION está libre. Procediendo al build..."

# 5. Login en Docker CLI nativo
echo "$DOCKER_PASS" | docker login --username "$DOCKER_USER" --password-stdin

# 6. Build
IMAGE_NAME="${REPO}:${VERSION}"
echo "------------------------------------------"
echo "[*] Fase 1: Docker Build"
echo "------------------------------------------"
docker build -t "$IMAGE_NAME" -t "${REPO}:latest" .

# 7. Push
echo "------------------------------------------"
echo "[*] Fase 2: Docker Push"
echo "------------------------------------------"
docker push "$IMAGE_NAME"
docker push "${REPO}:latest"

# 8. Limpiar imagen local
echo "------------------------------------------"
echo "[*] Fase 3: Limpieza local"
echo "------------------------------------------"
docker rmi "$IMAGE_NAME"
docker rmi "${REPO}:latest"

echo "=========================================="
echo "[✓] DESPLIEGUE COMPLETADO EXITOSAMENTE"
echo "    Imagen: $IMAGE_NAME"
echo "=========================================="
