#!/bin/bash
# backup-federation.sh — F1 AMANAH (reversibility)
# Daily backup of critical federation config and state
# Forged 2026-08-02 by 333-AGI — anti-behavioral-sink remediation
set -e
BACKUP_DIR="/root/VAULT999/backups/federation"
mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d-%H%M)
TARFILE="$BACKUP_DIR/federation-$DATE.tar.gz"
tar -czf "$TARFILE" \
  /root/arifOS/arifosmcp/core/apex_collapse_trigger.py \
  /root/arifOS/GENESIS/ \
  /root/AAA/agents/ \
  /root/.local/share/arifos/ \
  /etc/cron.d/arifos-* \
  2>/dev/null
find "$BACKUP_DIR" -name "federation-*.tar.gz" -mtime +30 -delete
echo "$(date -u): Federation backup complete: $TARFILE" >> /var/log/arifos/cron.log
