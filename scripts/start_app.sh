#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
HOST_DEFAULT="${HOST:-0.0.0.0}"
PORT_DEFAULT="${PORT:-8080}"
SKIP_INSTALL="false"
SKIP_MIGRATE="false"
PORT_OVERRIDE=""

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ROOT_DIR}/.env"
  set +a
fi

usage() {
  cat <<'EOF'
Usage: scripts/start_app.sh [options]

Sets up the Python virtual environment (if needed), installs dependencies,
aplica migraciones y arranca Daphne siguiendo los pasos del README.

Options:
  --skip-install    No reinstala dependencias (usa las ya presentes en venv).
  --skip-migrate    No ejecuta makemigrations/migrate.
  --port <number>   Puerto para Daphne (por defecto 8080).
  --help            Muestra esta ayuda y termina.
EOF
}

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
    --port)
      PORT_OVERRIDE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Opción desconocida: $1" >&2
      usage
      exit 1
      ;;
  esac
done

HOST="${HOST_DEFAULT}"
PORT="${PORT_OVERRIDE:-${PORT_DEFAULT}}"

cd "${ROOT_DIR}"

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

  echo "[!] No se encontró un intérprete de Python (python/py)." >&2
  echo "    Instala Python 3 o añade el comando correspondiente al PATH." >&2
  exit 1
}

ensure_virtualenv() {
  if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[*] Creando entorno virtual en ${VENV_DIR}"
    "${PY_CMD[@]}" -m venv "${VENV_DIR}"
  fi

  if [[ -x "${VENV_DIR}/Scripts/python" ]]; then
    VENV_PY="${VENV_DIR}/Scripts/python"
  elif [[ -x "${VENV_DIR}/bin/python" ]]; then
    VENV_PY="${VENV_DIR}/bin/python"
  else
    echo "[!] No se pudo localizar el intérprete dentro del venv." >&2
    echo "    Se esperaba encontrar Scripts/python o bin/python." >&2
    exit 1
  fi
}

find_python
ensure_virtualenv

run_in_venv() {
  "${VENV_PY}" "$@"
}

if [[ "${SKIP_INSTALL}" != "true" ]]; then
  echo "[*] Instalando dependencias"
  run_in_venv -m pip install --upgrade pip
  run_in_venv -m pip install -r requirements.txt
else
  echo "[*] Omitiendo instalación de dependencias (--skip-install)"
fi

if [[ "${SKIP_MIGRATE}" != "true" ]]; then
  echo "[*] Ejecutando makemigrations y migrate"
  run_in_venv manage.py makemigrations
  run_in_venv manage.py migrate
else
  echo "[*] Omitiendo migraciones (--skip-migrate)"
fi

echo "[*] Arrancando Daphne en ${HOST}:${PORT}"
exec "${VENV_PY}" -m daphne -b "${HOST}" -p "${PORT}" app_passify.asgi:application
