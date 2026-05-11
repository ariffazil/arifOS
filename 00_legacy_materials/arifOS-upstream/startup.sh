#!/bin/sh
# startup.sh — runs inside container as root before uvicorn
# NOTE: sg docker removed — fails as PID 1; docker group not needed for health monitoring

set -e

# Install docker-cli + login if not already installed (one-time cost)
if ! command -v docker >/dev/null 2>&1; then
    apt-get update -qq 2>/dev/null || true
    apt-get install -y -qq docker-cli login 2>/dev/null || true
fi

# Ensure arifos is in docker group
usermod -aG docker arifos 2>/dev/null || true

# Run uvicorn directly (no sg docker wrapper needed)
exec python3 -m uvicorn arifosmcp.runtime.server:app --host 0.0.0.0 --port 8080
