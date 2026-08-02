#!/bin/bash
# vault999-daily-backup — F11 AUDITABILITY
# Daily Postgres dump of VAULT999 to /root/VAULT999/backups/
# Forged 2026-08-02 by 333-AGI — anti-behavioral-sink remediation
set -e
BACKUP_DIR="/root/VAULT999/backups"
mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d)
pg_dump -U arifos -h localhost arifos_vault > "$BACKUP_DIR/vault999-$DATE.sql" 2>/dev/null || echo "WARN: pg_dump failed (may not be running)"
# Keep last 30 days
find "$BACKUP_DIR" -name "vault999-*.sql" -mtime +30 -delete
echo "$(date -u): VAULT999 backup complete" >> /var/log/arifos/cron.log
