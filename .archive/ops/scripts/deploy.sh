#!/bin/bash
set -e

# Run the backup script before doing anything else
/root/arifOS/backup.sh

# Navigate to the deployment directory
cd /root/arifOS || { echo "Deployment directory /root/arifOS not found."; exit 1; }

# Deactivate virtual environment if active, to ensure a clean start
if command -v deactivate &> /dev/null; then
    deactivate
fi

# Pull the latest changes from the main branch
echo ">>> Pulling latest changes from main..."
git fetch origin main
git reset --hard origin/main

# Set up the Python virtual environment
echo ">>> Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install/update dependencies
echo ">>> Installing dependencies..."
pip install uv
uv pip install -e ".[all]"
# Install potentially missing packages (discovered in Task 1)
uv pip install "redis>=5.0.0" "pytest-benchmark"

# Run tests as a CI check
echo ">>> Running tests..."
/root/arifOS/.venv/bin/pytest

# Restart the arifOS server (assumes a systemd service is defined)
echo ">>> Restarting arifOS server..."
sudo systemctl restart arifos-mcp.service

echo ">>> Deployment successful."
