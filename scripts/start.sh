#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

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

python -m daphne -b "$HOST" -p "$PORT" app_passify.asgi:application
