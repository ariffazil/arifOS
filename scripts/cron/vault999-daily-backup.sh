#!/bin/bash
# vault999-daily-backup — F11 AUDITABILITY
# Daily tar.gz snapshot of the REAL VAULT999 (JSONL ledgers) to /root/VAULT999/backups/
# Forged 2026-08-02 by 333-AGI — anti-behavioral-sink remediation
# REPAIRED 2026-09-16 by 333-AGI — predecessor dumped a Postgres DB (role 'arifos',
#   db 'arifos_vault') that never existed on this host → 46 days of silent 0-byte
#   backups + "backup complete" log lines = integrity theater (F11 shadow failure).
#   Real vault = JSONL: /root/.local/share/arifos/vault999/ + /root/VAULT999/*.jsonl
set -uo pipefail
BACKUP_DIR="/root/VAULT999/backups"
LOG="/var/log/arifos/cron.log"
mkdir -p "$BACKUP_DIR" /var/log/arifos
DATE=$(date +%Y%m%d)
TARGET="$BACKUP_DIR/vault999-$DATE.tar.gz"

# Snapshot the real ledgers. Exclude backups dir to avoid self-inclusion.
# tar rc 0 = clean; rc 1 = "file changed as we read it" (ledger active — acceptable);
# rc >= 2 = fatal.
tar -czf "$TARGET" \
	--exclude='backups' \
	--exclude='*.lock' \
	-C /root/.local/share/arifos vault999 \
	-C /root VAULT999 \
	2>>"$LOG"
RC=$?
if [ $RC -ge 2 ]; then
	rm -f "$TARGET"
	echo "$(date -u): VAULT999 backup FAILED (tar rc=$RC) — no file left behind" >>"$LOG"
	exit 1
fi

# Integrity floor: a valid ledger snapshot cannot be trivially small.
SIZE=$(stat -c%s "$TARGET" 2>/dev/null || echo 0)
if [ "$SIZE" -lt 10240 ]; then
	rm -f "$TARGET"
	echo "$(date -u): VAULT999 backup FAILED (size=${SIZE}B < 10KB floor) — removed" >>"$LOG"
	exit 1
fi

# Retention: 30 days of real backups; purge legacy 0-byte .sql theater.
find "$BACKUP_DIR" -name "vault999-*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "vault999-*.sql" -size 0 -delete

echo "$(date -u): VAULT999 backup complete (${SIZE} bytes -> $TARGET) [rc=$RC]" >>"$LOG"
