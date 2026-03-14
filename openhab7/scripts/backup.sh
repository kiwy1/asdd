#!/usr/bin/env bash
# OpenHAB7 Stack - Backup Script
# Backs up: OpenHAB conf & userdata, InfluxDB, Grafana, Mosquitto data
# Usage: ./backup.sh [backup_dir]
# Backup rotation: keep last BACKUP_RETENTION_DAYS (default 7)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_ROOT="${1:-${BACKUP_DIR:-$PROJECT_ROOT/backups}}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"
cd "$PROJECT_ROOT"

echo "[$(date -Iseconds)] Starting backup to $BACKUP_DIR"

# --- OpenHAB configuration (bind-mounted dir) ---
if [[ -d "openhab/conf" ]]; then
  echo "  Backing up openhab/conf..."
  cp -a openhab/conf "$BACKUP_DIR/openhab_conf"
fi

# --- Docker volumes (require docker) ---
if command -v docker &>/dev/null; then
  # OpenHAB userdata volume
  if docker volume inspect openhab7_openhab_userdata &>/dev/null; then
    echo "  Backing up volume openhab7_openhab_userdata..."
    docker run --rm -v openhab7_openhab_userdata:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/openhab_userdata.tar.gz -C /data .
  fi

  # InfluxDB data volume
  if docker volume inspect openhab7_influxdb_data &>/dev/null; then
    echo "  Backing up volume openhab7_influxdb_data..."
    docker run --rm -v openhab7_influxdb_data:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/influxdb_data.tar.gz -C /data .
  fi

  # Grafana data volume
  if docker volume inspect openhab7_grafana_data &>/dev/null; then
    echo "  Backing up volume openhab7_grafana_data..."
    docker run --rm -v openhab7_grafana_data:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/grafana_data.tar.gz -C /data .
  fi

  # Mosquitto data volume
  if docker volume inspect openhab7_mosquitto_data &>/dev/null; then
    echo "  Backing up volume openhab7_mosquitto_data..."
    docker run --rm -v openhab7_mosquitto_data:/data -v "$BACKUP_DIR:/backup" alpine tar czf /backup/mosquitto_data.tar.gz -C /data .
  fi
fi

echo "[$(date -Iseconds)] Backup completed: $BACKUP_DIR"

# --- Rotation: remove backups older than BACKUP_RETENTION_DAYS ---
if [[ -d "$BACKUP_ROOT" ]]; then
  find "$BACKUP_ROOT" -maxdepth 1 -type d -name "20*" -mtime +$((BACKUP_RETENTION_DAYS)) -exec rm -rf {} \; 2>/dev/null || true
  echo "  Rotation: kept last $BACKUP_RETENTION_DAYS days"
fi
