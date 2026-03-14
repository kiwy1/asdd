#!/usr/bin/env bash
# OpenHAB7 Stack - Restore Script
# Restores from a backup directory created by backup.sh
# Usage: ./restore.sh <backup_dir>
# Example: ./restore.sh backups/20250114_120000
# Stop the stack before restore: cd docker && docker compose down

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup_dir>"
  echo "Example: $0 backups/20250114_120000"
  exit 1
fi

BACKUP_DIR="$(cd "$1" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[$(date -Iseconds)] Restoring from $BACKUP_DIR"
echo "Ensure stack is stopped: cd docker && docker compose down"

# --- OpenHAB conf ---
if [[ -d "$BACKUP_DIR/openhab_conf" ]]; then
  echo "  Restoring openhab/conf..."
  rm -rf "$PROJECT_ROOT/openhab/conf"
  cp -a "$BACKUP_DIR/openhab_conf" "$PROJECT_ROOT/openhab/conf"
fi

# --- Docker volumes (restore into existing volumes) ---
if ! command -v docker &>/dev/null; then
  echo "  Docker not found; only openhab/conf was restored."
  exit 0
fi

cd "$PROJECT_ROOT/docker"

for name in openhab_userdata influxdb_data grafana_data mosquitto_data; do
  archive="$BACKUP_DIR/${name}.tar.gz"
  volume_name="openhab7_${name}"
  if [[ -f "$archive" ]] && docker volume inspect "$volume_name" &>/dev/null; then
    echo "  Restoring volume $volume_name..."
    docker run --rm -v "$volume_name:/data" -v "$BACKUP_DIR:/backup" alpine sh -c "rm -rf /data/* /data/..?* 2>/dev/null; tar xzf /backup/${name}.tar.gz -C /data"
  fi
done

echo "[$(date -Iseconds)] Restore completed. Start stack: cd docker && docker compose up -d"
