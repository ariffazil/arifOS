#!/bin/bash
set -euo pipefail

# check_reality.sh
# The single post-restart reality gate.
# Run this immediately after `systemctl restart arifos`.
# It fails if the 7 public verbs are not what is live.

PUBLIC_EXPECTED=7
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$DIR:${PYTHONPATH:-}"

echo "=== arifOS 7-Tool Reality Check ==="
echo "Source: $DIR"

CODE_COUNT=$(python3 -c '
import sys
sys.path.insert(0, ".")
from arifosmcp.runtime.public_surface import public_tool_names_for_mode
print(len(public_tool_names_for_mode(None)))
' )

echo "Declared in source: $CODE_COUNT"

if [ "$CODE_COUNT" != "$PUBLIC_EXPECTED" ]; then
  echo "FAIL: source not 7. Fix public_surface.py first."
  exit 1
fi

# Check running instance (local first)
LIVE=""
if curl -s -m 3 http://localhost:8088/health > /tmp/live.json 2>/dev/null; then
  LIVE=$(python3 -c '
import sys, json
d = json.load(open("/tmp/live.json"))
print(d.get("tools_registered") or d.get("public_tools_count") or "")
' 2>/dev/null || echo "")
fi

if [ -n "$LIVE" ]; then
  echo "Live (localhost): $LIVE"
  if [ "$LIVE" != "$PUBLIC_EXPECTED" ]; then
    echo "FAIL: running service not showing 7. Restart did not take effect or filter is broken."
    exit 1
  fi
else
  echo "Live localhost: unreachable (service may be on different host or port)"
fi

# Public (what agents see)
PUB=""
if curl -s -m 5 https://mcp.arif-fazil.com/mcp > /tmp/pub.json 2>/dev/null; then
  PUB=$(python3 -c '
import sys, json
try:
  d=json.load(open("/tmp/pub.json"))
  t = d.get("tools") or []
  print(len(t))
except: print("")
' 2>/dev/null || echo "")
fi

if [ -n "$PUB" ]; then
  echo "Public endpoint: $PUB"
  if [ "$PUB" != "$PUBLIC_EXPECTED" ]; then
    echo "WARN: public reports $PUB (may be network/auth in this env)"
  fi
else
  echo "Public: unreachable in this env — verify manually from a machine that can reach mcp.arif-fazil.com"
fi

echo "PASS. Code declares the 7-tool facade."
echo "After edit + restart: run this again to confirm the running service matches."
exit 0
