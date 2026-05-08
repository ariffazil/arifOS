#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-/root/openclaw_data/workspace}"
SCRIPT="$WORKSPACE/memory_tools/memory_pipeline.py"
ENV_FILE="${OPENCLAW_ENV_FILE:-/root/XXX/.env.master}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

python3 "$SCRIPT" --workspace "$WORKSPACE" env-lint --env-file "$ENV_FILE"

# Daily consistency check (creates today's memory file/Retain section if missing).
python3 "$SCRIPT" --workspace "$WORKSPACE" retain-daily --min-count 3

python3 "$SCRIPT" --workspace "$WORKSPACE" index --rebuild
python3 "$SCRIPT" --workspace "$WORKSPACE" reflect

# Optional semantic sync if Qdrant is configured.
if [[ -n "${QDRANT_API_KEY:-}" ]]; then
  python3 "$SCRIPT" --workspace "$WORKSPACE" semantic-upsert
fi

echo "Memory cycle complete for $WORKSPACE"
