#!/bin/bash
set -e

BACKUP_DIR="/opt/backups"
DEPLOY_DIR="/root/arifOS"

# Find the most recent backup
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}/arifos_backup_"*.tar.gz | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No backups found in ${BACKUP_DIR}."
    exit 1
fi

echo ">>> Found latest backup: ${LATEST_BACKUP}"
read -p "Are you sure you want to roll back to this version? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ && "$1" != "--force" ]]; then
    echo "Rollback cancelled."
    exit 1
fi

echo ">>> Stopping arifOS service..."
sudo systemctl stop arifos-router.service

echo ">>> Removing current deployment..."
rm -rf "${DEPLOY_DIR}"

echo ">>> Restoring from backup..."
tar -xzvf "$LATEST_BACKUP" -C "$(dirname ${DEPLOY_DIR})"

# Note: After extraction, the directory will be named arifOS, which is what we want.

echo ">>> Restarting arifOS service..."
# After restoring, the venv is gone. We need to recreate it and install deps.
# This assumes the backup contains the necessary pyproject.toml and other files.
cd "${DEPLOY_DIR}" || exit 1
echo ">>> Recreating virtual environment and installing dependencies..."
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -e ".[all]"
# Also install the deps that were missing from [all]
uv pip install "redis>=5.0.0" "pytest-benchmark"

echo ">>> Starting arifOS service..."
sudo systemctl start arifos-router.service

echo ">>> Rollback complete. Verifying status..."
sleep 5 # Give the service a moment to start
/root/arifOS/health-check.sh
