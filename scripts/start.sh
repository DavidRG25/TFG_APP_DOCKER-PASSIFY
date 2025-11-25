#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/venv"
cd "$ROOT_DIR"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-app_passify.settings}"
export DJANGO_DEBUG="${DJANGO_DEBUG:-true}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-dev-secret-key-change-me}"

HOST="${DJANGO_RUNSERVER_HOST:-127.0.0.1}"
PORT="${DJANGO_RUNSERVER_PORT:-8000}"

# Crear venv si no existe
if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[*] Creando entorno virtual en ${VENV_DIR}"
  python -m venv "${VENV_DIR}"
fi

# Activar venv
if [[ -f "${VENV_DIR}/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
elif [[ -f "${VENV_DIR}/Scripts/activate" ]]; then
  # shellcheck disable=SC1091
  source "${VENV_DIR}/Scripts/activate"
else
  echo "[!] No se encontró el script de activación del venv en ${VENV_DIR}" >&2
  exit 1
fi

echo "[*] Instalando dependencias"
pip install --upgrade pip
pip install -r requirements.txt

echo "[*] Ejecutando migraciones"
python manage.py makemigrations
python manage.py migrate

echo "[*] Recolectando estáticos"
python manage.py collectstatic --noinput

echo "[*] Generando imágenes por defecto (si aplica)"
python manage.py generate_default_images || echo "WARNING: generación de imágenes falló, se continúa."
echo "[*] Poblando imágenes de ejemplo (si aplica)"
python manage.py populate_example_images --noinput 2>/dev/null || echo "WARNING: populate_example_images falló, se continúa."
echo "[*] Creando usuarios demo (opcional)"
python manage.py create_demo_users || echo "WARNING: create_demo_users falló, se continúa."

echo "[*] Arrancando servidor en ${HOST}:${PORT}"
python manage.py runserver "${HOST}:${PORT}"
