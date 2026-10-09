#!/bin/bash
# ── arifFLOW Session Resume ─────────────────────────────────────
# DITEMPA BUKAN DIBERI — Forged 2026-07-28
#
# Queries arifFLOW Rust daemon (/health) for metabolic state.
# Reads carry_forward.json for prior session continuity.
# Rust daemon currently exposes: GET /health, POST /ingest, POST /flow.
# Rich state management (Python server) is source-only, not deployed.
#
# Usage:
#   flow_resume.sh                 # print carry-forward + FQ
#
# Output: JSON to stdout
#
# WRITER BAN (2026-09-12, P0 carry_forward writer audit):
# --write flag REMOVED. flow_resume.sh is OBSERVE-ONLY.
# It must never mutate carry_forward.json — ownership belongs to
# carry_forward.py (flock-protected, v2-native, atomic writer).
# Writer authority > ownership = the disease we cured. — FI-003

set -euo pipefail
FLOW_URL="${ARIFLOW_URL:-http://127.0.0.1:7073}"
CARRY_FORWARD="${CARRY_FORWARD_PATH:-/root/.local/share/arifos/carry_forward.json}"

# ── Probe arifFLOW health ──────────────────────────────────
health=$(curl -sf "$FLOW_URL/health" 2>/dev/null) || {
    echo '{"error":"arifFLOW unreachable","source":"flow_resume.sh"}'
    exit 1
}

# ── Read existing carry_forward ────────────────────────────
carry="{}"
if [[ -f "$CARRY_FORWARD" ]]; then
    carry=$(cat "$CARRY_FORWARD" 2>/dev/null || echo "{}")
fi

# ── Merge into resume payload ──────────────────────────────
result=$(python3 -c "
import json, sys

health = json.loads('''$health''')
carry = json.loads('''$carry''')

resume = {
    'source': 'arifFLOW',
    'timestamp': '$(date -u +"%Y-%m-%dT%H:%M:%SZ")',
    'flow': {
        'receipts': health.get('receipts', 0),
        'fq_verdict': health.get('fq', {}).get('verdict', 'UNKNOWN'),
        'execute_count': health.get('fq', {}).get('execute_count', 0),
        'verify_count': health.get('fq', {}).get('verify_count', 0),
    },
    'prior_session': carry.get('prior_session_id'),
    'prior_verdict': carry.get('verdict'),
    'prior_sealed': carry.get('sealed'),
}
print(json.dumps(resume, indent=2))
" 2>/dev/null)

echo "$result"

# ── WRITE REMOVED (P0 audit 2026-09-12) ────────────────────
# --write flag deleted. This script is OBSERVE-ONLY.
# Ownership of carry_forward.json belongs to carry_forward.py.
# See: writer-audit 2026-09-12, P0 finding #1.

exit 0
