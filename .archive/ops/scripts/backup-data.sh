#!/bin/bash
# Backup arifOS data volume
set -e

BACKUP_DIR="/root/backups/arifos"
DATA_DIR="/root/arifOS/data"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/arifos_data_$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup of $DATA_DIR"
tar -czf "$BACKUP_FILE" -C "$DATA_DIR" .
echo "[$(date)] Backup saved to $BACKUP_FILE"

# Keep only last 7 backups
cd "$BACKUP_DIR" && ls -t arifos_data_*.tar.gz | tail -n +8 | xargs rm -f
echo "[$(date)] Cleaned old backups"
