#!/usr/bin/env bash
# /root/continue-arifos/service/cn-organ-preflight.sh
# Quick pre-flight check: verify cn binary and config exist.
# This script must EXIT quickly (used as ExecStartPre).

set -e

CN_CONFIG="${CN_CONFIG:-/root/.continue/config.yaml}"
CN_BINARY="${CN_BINARY:-/usr/bin/cn}"

if [ ! -x "$CN_BINARY" ]; then
  echo "FATAL: cn binary not found or not executable: $CN_BINARY" >&2
  exit 1
fi

if [ ! -f "$CN_CONFIG" ]; then
  echo "FATAL: cn config not found: $CN_CONFIG" >&2
  exit 1
fi

# Quick version check (cn --version is fast)
CN_VER=$("$CN_BINARY" --version 2>&1 | head -1)

# Log the preflight result
echo "cn-organ preflight OK: cn=${CN_VER} config=${CN_CONFIG}"
exit 0
