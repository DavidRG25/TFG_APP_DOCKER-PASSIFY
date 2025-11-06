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
export DJANGO_DEBUG="${DJANGO_DEBUG:-false}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-0.0.0.0,localhost,127.0.0.1}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-}"

if [[ -z "$DJANGO_SECRET_KEY" && "$DJANGO_DEBUG" != "true" ]]; then
  echo "ERROR: DJANGO_SECRET_KEY must be set when DJANGO_DEBUG=false." >&2
  exit 1
fi

HOST="${DJANGO_HOST:-0.0.0.0}"
PORT="${DJANGO_PORT:-8000}"
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

python -m daphne -b "$HOST" -p "$PORT" app_passify.asgi:application
