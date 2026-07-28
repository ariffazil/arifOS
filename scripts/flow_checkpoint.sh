#!/bin/bash
# ── arifFLOW Session Checkpoint ──────────────────────────────────
# DITEMPA BUKAN DIBERI — Forged 2026-07-28
#
# Ingests a checkpoint receipt into arifFLOW :7073 via POST /ingest.
# The Rust daemon (not the Python server) is the runtime — schema is
# Rust struct IngestPayload with UUID receipt_id.
#
# Usage:
#   flow_checkpoint.sh start  "<session_id>" "<intent>"
#   flow_checkpoint.sh step   "<session_id>" "<action_summary>" "<verdict>"
#   flow_checkpoint.sh end    "<session_id>" "<summary>" "<verdict>"
#   flow_checkpoint.sh health
#
# Exit codes: 0 = ingested, 1 = arifFLOW down, 2 = bad args

set -euo pipefail
FLOW_URL="${ARIFLOW_URL:-http://127.0.0.1:7073}"
STEP_FILE="${ARIFLOW_STEP_FILE:-/tmp/ariflow_step_$$.counter}"

# ── Generate UUID v4 (no uuidgen dependency) ────────────────
_uuid() {
    python3 -c "import uuid; print(str(uuid.uuid4()))" 2>/dev/null || {
        cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "00000000-0000-0000-0000-$(date +%s%N | sha256sum | head -c 12)"
    }
}

# ── Step counter (per-session monotonic) ────────────────────
_step_num() {
    local sid="$1"
    local cf="/tmp/ariflow_step_${sid}.counter"
    local n=1
    if [[ -f "$cf" ]]; then
        n=$(($(cat "$cf") + 1))
    fi
    echo "$n" > "$cf"
    echo "$n"
}

# ── Args ────────────────────────────────────────────────────
stage="${1:-}"
session_id="${2:-}"
detail="${3:-}"
verdict="${4:-Pass}"

if [[ -z "$stage" ]]; then
    echo "USAGE: flow_checkpoint.sh <start|step|end|health> [session_id] [detail] [verdict]" >&2
    exit 2
fi

if [[ "$stage" == "health" ]]; then
    curl -sf "$FLOW_URL/health" 2>/dev/null || { echo '{"status":"arifFLOW unreachable"}'; exit 1; }
    exit 0
fi

if [[ -z "$session_id" ]]; then
    echo "ERROR: session_id required for stage '$stage'" >&2
    exit 2
fi

# ── Map stage → receipt fields ─────────────────────────────
now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
step_num=$(_step_num "$session_id")
receipt_id=$(_uuid)

case "$stage" in
    start)
        step_type="Barrier"
        epistemic="Observation"
        floor_verdict="Pass"
        payload="{\"intent\":\"$detail\"}"
        ;;
    step)
        step_type="Execute"
        epistemic="Derivation"
        floor_verdict="${verdict}"
        payload="{\"action\":\"$detail\",\"verdict\":\"$verdict\"}"
        ;;
    end)
        step_type="Seal"
        epistemic="Seal"
        floor_verdict="${verdict}"
        payload="{\"summary\":\"$detail\",\"verdict\":\"$verdict\"}"
        # Clean up step counter
        rm -f "/tmp/ariflow_step_${session_id}.counter"
        ;;
    *)
        echo "ERROR: unknown stage '$stage'. Use: start|step|end|health" >&2
        exit 2
        ;;
esac

# ── Ingest into arifFLOW Rust daemon ────────────────────────
resp=$(curl -sf "$FLOW_URL/ingest" \
    -H "Content-Type: application/json" \
    -d "{
        \"receipt_id\":\"$receipt_id\",
        \"actor_id\":\"copilot-cli\",
        \"session_id\":\"$session_id\",
        \"step_type\":\"$step_type\",
        \"epistemic_label\":\"$epistemic\",
        \"floor_verdict\":\"$floor_verdict\",
        \"cost_ns\":0,
        \"step_number\":$step_num,
        \"created_at\":\"$now_iso\",
        \"cooling_decision\":\"None\",
        \"lane_id\":1,
        \"topology_id\":\"copilot-cli\",
        \"previous_receipt_hash\":\"\",
        \"payload\":$payload
    }" 2>/dev/null) || {
    echo '{"error":"arifFLOW unreachable","stage":"'"$stage"'","session_id":"'"$session_id"'"}'
    exit 1
}

echo "$resp"
exit 0
