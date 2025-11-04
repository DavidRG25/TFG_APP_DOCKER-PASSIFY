#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
VENV_DIR="${ROOT_DIR}/venv"
BOOTSTRAP_PYTHON="${PYTHON_BIN:-python3}"
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
CLI_PORT=""
SKIP_INSTALL="false"
SKIP_MIGRATE="false"

usage() {
  cat <<'EOF'
Usage: scripts/start_app.sh [options]

Bootstraps the local environment and launches the ASGI server with Daphne.

Options:
  --skip-install    Reuse the existing virtualenv without installing packages.
  --skip-migrate    Skip running database migrations before starting Daphne.
  --port <number>   Override the default port (8080).
  --help            Show this help message and exit.

Environment variables:
  HOST  Override bind host (default: 0.0.0.0).
  PORT  Override bind port (default: 8080).
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
      CLI_PORT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

HOST="${HOST:-${DEFAULT_HOST}}"
PORT="${CLI_PORT:-${PORT:-${DEFAULT_PORT}}}"

cd "${ROOT_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[*] Creating virtual environment at ${VENV_DIR}"
  if ! command -v "${BOOTSTRAP_PYTHON}" >/dev/null 2>&1; then
    BOOTSTRAP_PYTHON="python"
  fi
  "${BOOTSTRAP_PYTHON}" -m venv "${VENV_DIR}"
fi

if [[ "${OSTYPE}" == "msys" || "${OSTYPE}" == "win32" ]]; then
  # Git Bash on Windows exposes the venv activate script under Scripts
  # shellcheck disable=SC1091
  source "${VENV_DIR}/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
fi

if [[ "${SKIP_INSTALL}" != "true" ]]; then
  echo "[*] Upgrading pip and installing dependencies"
  python -m pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "[*] Skipping dependency installation"
fi

if [[ "${SKIP_MIGRATE}" != "true" ]]; then
  echo "[*] Applying database migrations"
  python manage.py migrate
else
  echo "[*] Skipping database migrations"
fi

echo "[*] Starting Daphne on ${HOST}:${PORT}"
exec python -m daphne -b "${HOST}" -p "${PORT}" app_passify.asgi:application
