#!/usr/bin/env bash
set -euo pipefail

export PATH="/usr/local/bin:/root/.local/bin:${PATH}"

exec npx -y @playwright/mcp "$@"
