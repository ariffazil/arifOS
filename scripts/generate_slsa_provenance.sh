#!/usr/bin/env bash
# SLSA v1.0 provenance generation for CI pipelines
# Forged 2026-07-19
set -euo pipefail

REPO="${1:-unknown}"
COMMIT_SHA="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo 'local')}"
WORKFLOW="${GITHUB_WORKFLOW:-local}"
RUN_ID="${GITHUB_RUN_ID:-local}"
TIMESTAMP="$(date -Iseconds)"

python3 -c "
from arifosmcp.core.protocols.slsa import ci_provenance
import json, os

provenance = ci_provenance(
    repo='$REPO',
    commit_sha='$COMMIT_SHA',
    workflow='$WORKFLOW',
    run_id='$RUN_ID',
    timestamp='$TIMESTAMP',
)
# Write to artifact directory
os.makedirs('/tmp/slsa-provenance', exist_ok=True)
path = f'/tmp/slsa-provenance/{provenance[\"predicate\"][\"buildDefinition\"][\"externalParameters\"][\"repository\"]}-${RUN_ID}.json'
with open(path, 'w') as f:
    json.dump(provenance, f, indent=2)
print(f'SLSA provenance: {path}')
" 2>/dev/null || echo "SLSA module not available — skipping provenance generation"
