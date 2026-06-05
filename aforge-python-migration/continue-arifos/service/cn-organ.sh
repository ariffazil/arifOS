#!/usr/bin/env bash
# /root/continue-arifos/service/cn-organ.sh
# Helper script for the cn-organ systemd service.
# Ensures config + binary exist before starting.

set -e

CN_CONFIG="${CN_CONFIG:-/root/.continue/config.yaml}"
CN_BINARY="${CN_BINARY:-/usr/bin/cn}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pre-flight checks
if [ ! -x "$CN_BINARY" ]; then
  echo "FATAL: cn binary not found or not executable: $CN_BINARY" >&2
  exit 1
fi

if [ ! -f "$CN_CONFIG" ]; then
  echo "FATAL: cn config not found: $CN_CONFIG" >&2
  exit 1
fi

echo "cn-organ preflight: cn=$(cn --version 2>/dev/null) config=$CN_CONFIG"

# Run the Python service
exec python3 "$SCRIPT_DIR/cn_organ.py"
