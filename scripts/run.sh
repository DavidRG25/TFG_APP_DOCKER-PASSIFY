#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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
SSH_IMAGE="${SERVICE_SSH_IMAGE:-linuxserver/openssh-server}"

if command -v docker >/dev/null 2>&1; then
  echo "[*] Verificando imagen SSH requerida (${SSH_IMAGE})"
  if ! docker image inspect "$SSH_IMAGE" >/dev/null 2>&1; then
    echo "[*] Descargando imagen SSH ${SSH_IMAGE}"
    docker pull "$SSH_IMAGE"
  fi
else
  echo "[!] Docker no esta disponible; no se puede preparar la imagen SSH (${SSH_IMAGE})." >&2
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py runserver "${HOST}:${PORT}"
