#!/usr/bin/env bash
set -euo pipefail

# arifOS MCP stdio server launcher
# Runs from the repo root so both arifosmcp and sibling core modules resolve
# without creating a fresh uv environment on every launch.

export PATH="/usr/local/bin:/root/.local/bin:${PATH}"
export ARIFOS_MINIMAL_STDIO=1
ARIFOS_REPO="${ARIFOS_REPO:-/opt/arifos/src/arifOS}"
export PYTHONPATH="${ARIFOS_REPO}${PYTHONPATH:+:${PYTHONPATH}}"

cd "${ARIFOS_REPO}"
exec python3 -m arifosmcp.runtime.__main__ stdio
