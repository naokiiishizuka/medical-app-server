#!/bin/sh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR"
cd "$ROOT_DIR"

if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

alembic upgrade head "$@"
