#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# run.sh - Ejecucion rapida del proyecto PaaSify
# ============================================================================
# Uso: bash scripts/run.sh [opciones]
#
# Este script ejecuta el servidor rapidamente asumiendo que el entorno
# ya esta configurado (venv creado, dependencias instaladas).
#
# Por defecto usa runserver (desarrollo). Usa --production para Daphne.
#
# Para inicializacion completa (primera vez), usa scripts/start.sh
# ============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
USE_PRODUCTION="false"
PORT_OVERRIDE=""
HOST_OVERRIDE=""

# Cargar variables de entorno desde .env si existe
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

usage() {
  cat <<'EOF'
Uso: bash scripts/run.sh [opciones]

Ejecuta el servidor rapidamente. Asume que el entorno ya esta configurado.
Por defecto usa runserver (desarrollo). Usa --production para Daphne (ASGI).

Opciones:
  --production      Usa Daphne (ASGI) en lugar de runserver.
  --port <numero>   Puerto personalizado (default: 8000).
  --host <ip>       Host personalizado (default: 127.0.0.1 en dev, 0.0.0.0 en prod).
  --help, -h        Muestra esta ayuda y termina.

Ejemplos:
  bash scripts/run.sh                    # Desarrollo (runserver)
  bash scripts/run.sh --production       # Produccion (Daphne)
  bash scripts/run.sh --port 9000        # Puerto personalizado
  bash scripts/run.sh --production --host 0.0.0.0 --port 8080

Para inicializacion completa (primera vez), usa: bash scripts/start.sh
EOF
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
  case "$1" in
    --production)
      USE_PRODUCTION="true"
      shift
      ;;
    --port)
      PORT_OVERRIDE="$2"
      shift 2
      ;;
    --host)
      HOST_OVERRIDE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Opcion desconocida: $1" >&2
      usage
      exit 1
      ;;
  esac
done

cd "${ROOT_DIR}"

# Configurar variables de entorno Django
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-app_passify.settings}"

if [[ "${USE_PRODUCTION}" == "true" ]]; then
  export DJANGO_DEBUG="${DJANGO_DEBUG:-false}"
  export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-0.0.0.0,localhost,127.0.0.1}"
  export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-}"
  HOST="${HOST_OVERRIDE:-${DJANGO_HOST:-0.0.0.0}}"
  PORT="${PORT_OVERRIDE:-${DJANGO_PORT:-8000}}"
  
  # Validar SECRET_KEY en produccion
  if [[ -z "$DJANGO_SECRET_KEY" && "$DJANGO_DEBUG" != "true" ]]; then
    echo "[!] ERROR: DJANGO_SECRET_KEY debe estar configurada cuando DJANGO_DEBUG=false." >&2
    echo "    Define DJANGO_SECRET_KEY en el archivo .env o como variable de entorno." >&2
    exit 1
  fi
else
  export DJANGO_DEBUG="${DJANGO_DEBUG:-true}"
  export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"
  export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-dev-secret-key-change-me}"
  HOST="${HOST_OVERRIDE:-${DJANGO_RUNSERVER_HOST:-127.0.0.1}}"
  PORT="${PORT_OVERRIDE:-${DJANGO_RUNSERVER_PORT:-8000}}"
fi

# Detectar Python (venv o sistema)
if [[ -x "${VENV_DIR}/Scripts/python" ]]; then
  PYTHON="${VENV_DIR}/Scripts/python"
elif [[ -x "${VENV_DIR}/bin/python" ]]; then
  PYTHON="${VENV_DIR}/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "[!] No se encontro Python. Ejecuta 'bash scripts/start.sh' primero." >&2
  exit 1
fi

echo "=========================================="
if [[ "${USE_PRODUCTION}" == "true" ]]; then
  echo "  PaaSify - Modo Produccion (Daphne)"
else
  echo "  PaaSify - Modo Desarrollo (runserver)"
fi
echo "=========================================="
echo ""

# Ejecutar migraciones (rapido si no hay cambios)
echo "[*] Ejecutando migraciones"
"${PYTHON}" manage.py migrate --noinput
echo "    âœ“ Migraciones completadas"

# Recolectar archivos estaticos
echo "[*] Recolectando archivos estaticos"
"${PYTHON}" manage.py collectstatic --noinput --verbosity 0
echo "    âœ“ Archivos estaticos recolectados"

# Arrancar servidor
echo ""
echo "=========================================="
if [[ "${USE_PRODUCTION}" == "true" ]]; then
  echo "  Arrancando Daphne (ASGI)"
else
  echo "  Arrancando runserver (desarrollo)"
fi
echo "=========================================="
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  Debug: ${DJANGO_DEBUG}"
echo "=========================================="
echo ""

if [[ "${USE_PRODUCTION}" == "true" ]]; then
  exec "${PYTHON}" -m daphne -b "${HOST}" -p "${PORT}" app_passify.asgi:application
else
  exec "${PYTHON}" manage.py runserver "${HOST}:${PORT}"
fi
