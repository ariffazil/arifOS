#!/usr/bin/env bash
# backup-state.sh — Phase 5A: Postgres + Qdrant backup
# Run: cron on host, 03:00 UTC daily (11:00 MYT)

set -euo pipefail

BACKUP_DIR="/srv/backups/arifos"
TS=$(date -u +%Y%m%d_%H%M%S)
DATE=$(date -u +%Y%m%d)
LOG="/srv/backups/arifos/backup.log"

mkdir -p "${BACKUP_DIR}/postgres" "${BACKUP_DIR}/qdrant"

log() { echo "[${TS}] $*" | tee -a "${LOG}"; }

log "=== arifOS backup starting ==="

# --- Postgres ---
docker exec arifos-postgres pg_dumpall -U postgres 2>/dev/null | \
  gzip > "${BACKUP_DIR}/postgres/pg_${DATE}.sql.gz" && \
  log "Postgres OK: $(du -sh ${BACKUP_DIR}/postgres/pg_${DATE}.sql.gz | cut -f1)" || \
  log "ERROR: Postgres backup failed"
find "${BACKUP_DIR}/postgres" -name "pg_*.sql.gz" -mtime +30 -delete

# --- Qdrant snapshot ---
SNAPSHOT=$(curl -sf -X POST http://localhost:6333/snapshots 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('name',''))" 2>/dev/null || echo "")
if [ -n "${SNAPSHOT}" ]; then
  curl -sf "http://localhost:6333/snapshots/${SNAPSHOT}" \
    -o "${BACKUP_DIR}/qdrant/qdrant_${DATE}.snapshot" 2>/dev/null && \
    log "Qdrant OK: $(du -sh ${BACKUP_DIR}/qdrant/qdrant_${DATE}.snapshot | cut -f1)" || \
    log "WARNING: Qdrant download failed"
  find "${BACKUP_DIR}/qdrant" -name "*.snapshot" -mtime +30 -delete
else
  log "WARNING: Qdrant snapshot failed (empty DB?)"
fi

# --- Disk check ---
DISK_PCT=$(df / | awk 'NR==2{print $5}' | tr -d '%')
log "Disk: ${DISK_PCT}%"
[ "${DISK_PCT}" -gt 80 ] && log "WARNING: Disk >80% — docker builder prune -f"

log "=== Done ==="
