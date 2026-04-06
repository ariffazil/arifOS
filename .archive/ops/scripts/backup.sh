#!/bin/bash
set -e

BACKUP_DIR="/opt/backups"
SOURCE_DIR="/root/arifOS"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
BACKUP_FILENAME="arifos_backup_${TIMESTAMP}.tar.gz"
BACKUP_FILEPATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo ">>> Creating backup of ${SOURCE_DIR}..."

# Create a gzipped tarball, excluding the venv and other caches
tar \
  --exclude="${SOURCE_DIR}/.venv" \
  --exclude="${SOURCE_DIR}/__pycache__" \
  --exclude="${SOURCE_DIR}/*.pyc" \
  --exclude="${SOURCE_DIR}/.pytest_cache" \
  --exclude="${SOURCE_DIR}/.benchmarks" \
  --exclude="${SOURCE_DIR}/telemetry" \
  -czvf "$BACKUP_FILEPATH" -C "$(dirname ${SOURCE_DIR})" "$(basename ${SOURCE_DIR})"

echo ">>> Backup successful: ${BACKUP_FILEPATH}"
