#!/bin/bash
# CLI Governance Sidecar — Observed Execution, Maximum Capability
# Principle: All dangerous commands are witnessed and published to the law layer.
#            Execution is NEVER blocked. Governance is retrospective and async.
#
# To activate: export BASH_ENV=/root/arifOS/deploy/cli-governance-sidecar.sh
#              (sourced automatically for all bash shells when BASH_ENV is set)
#
# DITEMPA BUKAN DIBERI

# Guard: only define once per shell (P1 fix, 2026-06-13)
if [[ -n "${_ARIFOS_GOVERNANCE_ACTIVE:-}" ]]; then
    return 0
fi
_ARIFOS_GOVERNANCE_ACTIVE=1

ARIFOS_MCP_URL="${ARIFOS_MCP_URL:-http://127.0.0.1:8088/mcp}"
GOVERNANCE_LOG="/root/.agent-workbench/governance-sidecar.jsonl"
GOVERNANCE_CACHE="/tmp/.arifos_governance_cache.$$"
mkdir -p "$(dirname "$GOVERNANCE_LOG")"
touch "$GOVERNANCE_CACHE"

# Patterns that trigger witnessing (not blocking)
_WITNESS_PATTERNS=(
    '^rm -rf /+$'
    '^rm -rf /[a-zA-Z0-9]+'
    '^docker system prune'
    '^docker volume rm'
    '^docker network rm'
    '^docker container rm -f'
    '^git push --force'
    '^git push -f'
    '^git reset --hard'
    '^git clean -fdx'
    '^DROP TABLE'
    '^DELETE FROM .* WHERE .*='
    '^ALTER TABLE .* DROP'
    '^chmod -R 777 /'
    '^chown -R .* /$'
    '^systemctl stop .*arifos'
    '^systemctl restart .*arifos'
    '^pkill -9 .*arifos'
    '^kill -9 .*arifos'
)

# Fast, fire-and-forget witness
function _arifos_witness() {
    local cmd="$1" pat="$2"
    local ts epoch sid payload
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    epoch=$(date -u +%s)
    sid="${ARIFOS_SESSION_ID:-$(cat /tmp/.arifos_last_session 2>/dev/null || echo "unknown")}"

    payload=$(jq -n \
        --arg ts "$ts" \
        --arg sid "$sid" \
        --arg agent "${ARIFOS_ACTOR_ID:-cli}" \
        --arg cmd "$cmd" \
        --arg matched "$pat" \
        --argjson epoch "$epoch" \
        '{
            type: "governance-witness",
            timestamp: $ts,
            epoch: $epoch,
            agent: $agent,
            session_id: $sid,
            command: $cmd,
            matched_pattern: $matched,
            verdict: "WITNESSED",
            reason: "Dangerous pattern matched — execution observed and logged."
        }')

    # 1. Append to local log (non-blocking)
    printf '%s\n' "$payload" >> "$GOVERNANCE_LOG" 2>/dev/null &

    # 2. Publish to NATS agent_memory (fire-and-forget, background)
    if command -v nats >/dev/null 2>&1; then
        nats pub "agent.memory.governance" "$payload" 2>/dev/null &
    fi

    # 3. Async judge call — does NOT block execution
    #    Writes verdict to cache for retrospective inspection
    (
        local judge_payload judge_resp judge_verdict
        judge_payload=$(jq -n \
            --arg actor "${ARIFOS_ACTOR_ID:-cli}" \
            --arg cmd "$cmd" \
            --arg sid "$sid" \
            '{jsonrpc:"2.0",id:1,method:"tools/call",params:{name:"arif_judge_deliberate",arguments:{actor_id:$actor,task_description:$cmd,session_id:$sid,decision_class:"C4",mode:"judge"}}}')

        judge_resp=$(curl -s -X POST "$ARIFOS_MCP_URL" \
            -H "Content-Type: application/json" \
            -d "$judge_payload" \
            --max-time 3 2>/dev/null)

        judge_verdict=$(echo "$judge_resp" | jq -r '.result.content[0].text // "HOLD"' 2>/dev/null)

        # Cache the verdict for this command pattern
        local cache_key
        cache_key=$(echo "$cmd" | sha256sum | awk '{print $1}')
        printf '%s\t%s\t%s\n' "$ts" "$cache_key" "$judge_verdict" >> "$GOVERNANCE_CACHE" 2>/dev/null

        # If judge says VOID or REDLINE, escalate to NATS immediately
        if [[ "$judge_verdict" == *"VOID"* ]] || [[ "$judge_verdict" == *"REDLINE"* ]]; then
            local escalate
            escalate=$(jq -n \
                --arg ts "$ts" \
                --arg sid "$sid" \
                --arg cmd "$cmd" \
                --arg verdict "$judge_verdict" \
                '{
                    type: "governance-escalation",
                    timestamp: $ts,
                    session_id: $sid,
                    command: $cmd,
                    judge_verdict: $verdict,
                    urgency: "CRITICAL"
                }')
            nats pub "agent.memory.governance.escalation" "$escalate" 2>/dev/null || true
        fi
    ) &
}

function _arifos_governance_check() {
    local raw_cmd="$1"
    local cmd
    cmd=$(echo "$raw_cmd" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    for pat in "${_WITNESS_PATTERNS[@]}"; do
        if [[ "$cmd" =~ $pat ]]; then
            _arifos_witness "$cmd" "$pat"
            break
        fi
    done

    # ALWAYS return 0 — execution is never blocked
    return 0
}

# Override functions — these call the original command via `command`
function rm() {
    _arifos_governance_check "rm $*"
    command rm "$@"
}

function docker() {
    _arifos_governance_check "docker $*"
    command docker "$@"
}

function git() {
    _arifos_governance_check "git $*"
    command git "$@"
}

function systemctl() {
    _arifos_governance_check "systemctl $*"
    command systemctl "$@"
}

function pkill() {
    _arifos_governance_check "pkill $*"
    command pkill "$@"
}

function kill() {
    _arifos_governance_check "kill $*"
    command kill "$@"
}

function chmod() {
    _arifos_governance_check "chmod $*"
    command chmod "$@"
}

function chown() {
    _arifos_governance_check "chown $*"
    command chown "$@"
}
