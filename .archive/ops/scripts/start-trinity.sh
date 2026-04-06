#!/bin/bash
set -e

# Ensure writable directories exist
mkdir -p /usr/src/app/telemetry /usr/src/app/data /usr/src/app/VAULT999 /usr/src/app/memory

echo "[TRINITY] Starting SSE server on port 8080..."
python -m arifosmcp.runtime sse &
SSE_PID=$!

REST_FALLBACK="${ENABLE_REST_FALLBACK:-0}"
REST_PID=""

if [ "$REST_FALLBACK" = "1" ]; then
  REST_PORT="${REST_PORT:-8089}"
  echo "[TRINITY] Starting HTTP MCP fallback on port ${REST_PORT}..."
  PORT="${REST_PORT}" python -m arifosmcp.runtime http &
  REST_PID=$!
fi

if [ -n "$REST_PID" ]; then
  echo "[TRINITY] Servers running (SSE=$SSE_PID, REST fallback=$REST_PID)"
  wait -n "$SSE_PID" "$REST_PID"
  echo "[TRINITY] A process exited. Shutting down..."
  kill "$SSE_PID" "$REST_PID" 2>/dev/null
  wait
else
  echo "[TRINITY] SSE server running (REST fallback disabled)"
  wait "$SSE_PID"
fi
