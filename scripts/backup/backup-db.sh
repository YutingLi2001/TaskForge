#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set."
  exit 1
fi

backup_dir="${BACKUP_DIR:-./backups}"
mkdir -p "$backup_dir"

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_path="${backup_dir}/taskforge-${timestamp}.dump"

echo "Backing up database to ${backup_path}"
pg_dump "${DATABASE_URL}" --format=custom --file="${backup_path}"
echo "Backup complete."
