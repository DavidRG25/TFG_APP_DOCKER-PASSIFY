#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# start.sh - Inicializacion completa del proyecto PaaSify
# ============================================================================
# Uso: bash scripts/start.sh [opciones]
#
# Este script realiza la configuracion completa del entorno:
# - Crea entorno virtual (si no existe)
# - Instala dependencias
# - Ejecuta migraciones
# - Configura usuarios y datos de ejemplo
# - Arranca el servidor Daphne (ASGI)
#
# Para ejecucion rapida en desarrollo diario, usa scripts/run.sh
# ============================================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
HOST_DEFAULT="${HOST:-0.0.0.0}"
PORT_DEFAULT="${PORT:-8000}"
SKIP_INSTALL="false"
SKIP_MIGRATE="false"
SKIP_SETUP="false"
PORT_OVERRIDE=""
HOST_OVERRIDE=""

# Cargar variables de entorno desde .env si existe
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ROOT_DIR}/.env"
  set +a
fi

usage() {
  cat <<'EOF'
Uso: bash scripts/start.sh [opciones]

Inicializa el proyecto completo: crea venv, instala dependencias, ejecuta
migraciones, configura datos de ejemplo y arranca Daphne (servidor ASGI).

Opciones:
  --skip-install    No reinstala dependencias (usa las ya presentes en venv).
  --skip-migrate    No ejecuta makemigrations/migrate.
  --skip-setup      No ejecuta comandos de inicializacion (demo users, imagenes).
  --port <numero>   Puerto para Daphne (por defecto 8000).
  --host <ip>       Host para Daphne (por defecto 0.0.0.0).
  --help, -h        Muestra esta ayuda y termina.

Ejemplos:
  bash scripts/start.sh                              # Inicializacion completa
  bash scripts/start.sh --skip-install               # Reutiliza dependencias
  bash scripts/start.sh --port 8080 --host 127.0.0.1 # Puerto y host personalizados
  bash scripts/start.sh --skip-setup                 # Sin datos de ejemplo

Para desarrollo diario (ejecucion rapida), usa: bash scripts/run.sh
EOF
}

# Parsear argumentos
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-install)
      SKIP_INSTALL="true"
      shift
      ;;
    --skip-migrate)
      SKIP_MIGRATE="true"
      shift
      ;;
    --skip-setup)
      SKIP_SETUP="true"
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

HOST="${HOST_OVERRIDE:-${HOST_DEFAULT}}"
PORT="${PORT_OVERRIDE:-${PORT_DEFAULT}}"

cd "${ROOT_DIR}"

# Detectar interprete Python disponible
find_python() {
  local -a candidates=("python" "py -3" "py" "python3")
  local candidate parts

  for candidate in "${candidates[@]}"; do
    read -r -a parts <<< "${candidate}"
    if [[ -n "${parts[0]}" ]] && command -v "${parts[0]}" >/dev/null 2>&1; then
      PY_CMD=("${parts[@]}")
      return 0
    fi
  done

  echo "[!] No se encontro un interprete de Python (python/py/python3)." >&2
  echo "    Instala Python 3 o anade el comando correspondiente al PATH." >&2
  exit 1
}

# Crear entorno virtual si no existe
ensure_virtualenv() {
  if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[*] Creando entorno virtual en ${VENV_DIR}"
    "${PY_CMD[@]}" -m venv "${VENV_DIR}"
  else
    echo "[*] Entorno virtual existente detectado en ${VENV_DIR}"
  fi

  # Detectar ruta del Python del venv
  if [[ -x "${VENV_DIR}/Scripts/python" ]]; then
    VENV_PY="${VENV_DIR}/Scripts/python"
  elif [[ -x "${VENV_DIR}/bin/python" ]]; then
    VENV_PY="${VENV_DIR}/bin/python"
  else
    echo "[!] No se pudo localizar el interprete dentro del venv." >&2
    echo "    Se esperaba encontrar Scripts/python o bin/python." >&2
    exit 1
  fi
}

# Ejecutar comando en el entorno virtual
run_in_venv() {
  "${VENV_PY}" "$@"
}

echo "=========================================="
echo "  PaaSify - Inicializacion Completa"
echo "=========================================="
echo ""

# Paso 1: Detectar Python y crear venv
find_python
ensure_virtualenv

# Paso 2: Instalar dependencias
if [[ "${SKIP_INSTALL}" != "true" ]]; then
  echo "[*] Instalando dependencias desde requirements.txt"
  run_in_venv -m pip install --upgrade pip --quiet
  run_in_venv -m pip install -r requirements.txt --quiet
  echo "    âœ“ Dependencias instaladas"
else
  echo "[*] Omitiendo instalacion de dependencias (--skip-install)"
fi

# Paso 3: Ejecutar migraciones
if [[ "${SKIP_MIGRATE}" != "true" ]]; then
  echo "[*] Ejecutando migraciones de base de datos"
  run_in_venv manage.py makemigrations
  run_in_venv manage.py migrate --noinput
  echo "    âœ“ Migraciones completadas"
else
  echo "[*] Omitiendo migraciones (--skip-migrate)"
fi

# Paso 4: Configurar datos de ejemplo y usuarios
if [[ "${SKIP_SETUP}" != "true" ]]; then
  echo "[*] Configurando datos de ejemplo"
  run_in_venv manage.py create_demo_users 2>/dev/null || true
  run_in_venv manage.py populate_example_images --noinput 2>/dev/null || true
  echo "    âœ“ Usuarios y datos de ejemplo configurados"
else
  echo "[*] Omitiendo configuracion de datos de ejemplo (--skip-setup)"
fi

# Paso 5: Recolectar archivos estaticos
echo "[*] Recolectando archivos estaticos"
run_in_venv manage.py collectstatic --noinput --verbosity 0
echo "    âœ“ Archivos estaticos recolectados"

# Paso 6: Validar SECRET_KEY en produccion
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-app_passify.settings}"
export DJANGO_DEBUG="${DJANGO_DEBUG:-false}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-0.0.0.0,localhost,127.0.0.1}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-}"

if [[ -z "$DJANGO_SECRET_KEY" && "$DJANGO_DEBUG" != "true" ]]; then
  echo "[!] ERROR: DJANGO_SECRET_KEY debe estar configurada cuando DJANGO_DEBUG=false." >&2
  echo "    Define DJANGO_SECRET_KEY en el archivo .env o como variable de entorno." >&2
  exit 1
fi

# Paso 7: Arrancar servidor Daphne
echo ""
echo "=========================================="
echo "  Arrancando Daphne (ASGI)"
echo "=========================================="
echo "  Host: ${HOST}"
echo "  Port: ${PORT}"
echo "  Debug: ${DJANGO_DEBUG}"
echo "=========================================="
echo ""

exec "${VENV_PY}" -m daphne -b "${HOST}" -p "${PORT}" app_passify.asgi:application
