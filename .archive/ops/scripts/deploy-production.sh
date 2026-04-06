#!/bin/bash
# arifOS Production Deployment Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_ROOT="${ARIFOS_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
SECRETS_DIR="${ARIFOS_SECRETS_DIR:-/opt/arifos/secrets}"
SERVICE_NAME="${ARIFOS_SERVICE_NAME:-arifos-mcp}"
PORT="${PORT:-8080}"
PYTHON_BIN="${ARIFOS_PYTHON_BIN:-$ARIFOS_ROOT/.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3)"
fi

echo "arifOS Production Deployment"
echo "==========================="
echo "Repo root: $ARIFOS_ROOT"
echo "Secrets : $SECRETS_DIR"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
  echo "ERROR: python runtime not found"
  exit 1
}
command -v curl >/dev/null 2>&1 || {
  echo "ERROR: curl required"
  exit 1
}

if [ ! -f "$SECRETS_DIR/governance.secret" ]; then
  echo "ERROR: governance secret missing at $SECRETS_DIR/governance.secret"
  exit 1
fi

echo "Verifying governance secret..."
ARIFOS_GOVERNANCE_SECRET_FILE="$SECRETS_DIR/governance.secret" \
  "$PYTHON_BIN" "$ARIFOS_ROOT/scripts/verify-secrets.py"

echo "Installing runtime dependencies..."
cd "$ARIFOS_ROOT"
"$PYTHON_BIN" -m pip install -e ".[dev]"

echo "Regenerating public specs and docs..."
"$PYTHON_BIN" "$ARIFOS_ROOT/scripts/generate_public_specs.py"
"$PYTHON_BIN" "$ARIFOS_ROOT/scripts/generate_public_contract_docs.py"

echo "Running targeted deploy validation..."
ARIFOS_GOVERNANCE_SECRET_FILE="$SECRETS_DIR/governance.secret" \
  "$PYTHON_BIN" -m pytest \
    tests/test_public_registry.py \
    tests/test_deploy_production.py \
    tests/test_runtime_prompts.py \
    tests/test_auth_continuity_file_secret.py \
    tests/test_runtime_capability_map.py \
    -q

echo "Restarting service..."
if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files | grep -q "^${SERVICE_NAME}\.service"; then
  systemctl restart "$SERVICE_NAME"
  systemctl --no-pager --full status "$SERVICE_NAME" || true
else
  pkill -f "python.*arifosmcp.runtime" || true
  ARIFOS_GOVERNANCE_SECRET_FILE="$SECRETS_DIR/governance.secret" \
    AAA_MCP_TRANSPORT=http \
    nohup "$PYTHON_BIN" -m arifosmcp.runtime http >/tmp/arifosmcp.log 2>&1 &
fi

echo "Health check..."
sleep 3
curl -fsS "http://127.0.0.1:${PORT}/health"

echo
echo "Deploy validation complete."
echo "Expected follow-up checks:"
echo "  curl -fsS http://127.0.0.1:${PORT}/health"
echo "  curl -fsS http://127.0.0.1:${PORT}/.well-known/mcp/server.json"
