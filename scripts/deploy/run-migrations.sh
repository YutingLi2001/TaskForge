#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set."
  exit 1
fi

echo "Running Alembic migrations..."
cd "$(dirname "$0")/../../backend"
python run_migrations.py
echo "Migrations complete."
