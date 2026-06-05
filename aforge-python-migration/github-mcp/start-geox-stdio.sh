#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/bin:/root/.local/bin:${PATH}"
export PYTHONPATH="/root${PYTHONPATH:+:${PYTHONPATH}}"

cd /root
exec python3 /root/geox_unified_mcp_server.py "$@"
