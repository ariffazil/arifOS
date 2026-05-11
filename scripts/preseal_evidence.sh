#!/bin/bash
# preseal_evidence.sh — Generate evidence packet for VAULT999 seal
# Skill: supply_chain_witness + policy_gatekeeper
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="${SCRIPT_DIR}/.."
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/preseal_evidence_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

COMPOSE_DIR="${COMPOSE_DIR:-/root/compose}"
COMPOSE_FILE="${COMPOSE_FILE:-$COMPOSE_DIR/docker-compose.yml}"
ARIFOS_DIR="${ARIFOS_DIR:-/root/arifOS}"

HOSTNAME=$(hostnamectl --static 2>/dev/null || hostname)
GIT_COMMIT=$(git -C "$ARIFOS_DIR" rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
GIT_BRANCH=$(git -C "$ARIFOS_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")

STATUS="PASS"
REASONS=()
RISK="LOW"
SEAL_RECOMMENDATION="READY"
KNOWN_GAPS=()

# ── Compute hashes ────────────────────────────────────────────
compute_hash() {
    local target="$1"
    if [ -f "$target" ]; then
        sha256sum "$target" | awk '{print $1}'
    elif [ -d "$target" ]; then
        find "$target" -type f | sort | xargs sha256sum 2>/dev/null | sha256sum | awk '{print $1}'
    else
        echo "MISSING"
    fi
}

TOOL_REGISTRY_HASH=$(compute_hash "$ARIFOS_DIR/arifosmcp/tool_registry.json")
CONSTITUTIONAL_MAP_HASH=$(compute_hash "$ARIFOS_DIR/arifosmcp/constitutional_map.py")
SCHEMA_HASH=$(compute_hash "$ARIFOS_DIR/arifosmcp/schemas")

# ── Container image digest ────────────────────────────────────
ARIFOS_IMAGE_DIGEST=$(docker inspect --format='{{.Config.Image}}' arifosmcp 2>/dev/null || echo "UNKNOWN")
ARIFOS_IMAGE_ID=$(docker inspect --format='{{.Id}}' arifosmcp 2>/dev/null || echo "UNKNOWN")

# ── Runtime drift check ───────────────────────────────────────
RUNTIME_DRIFT=false
if [ -x "$SCRIPT_DIR/import_truth.sh" ]; then
    IMPORT_LOG="$TMP_DIR/import_truth.log"
    "$SCRIPT_DIR/import_truth.sh" > "$IMPORT_LOG" 2>&1 || true
    DRIFT_LINE=$(grep -E "runtime_drift" "$IMPORT_LOG" || true)
    if echo "$DRIFT_LINE" | grep -q "true"; then
        RUNTIME_DRIFT=true
    fi
fi

# ── Health status ─────────────────────────────────────────────
HEALTH_STATUS="unknown"
if docker inspect arifosmcp >/dev/null 2>&1; then
    HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' arifosmcp 2>/dev/null || echo "none")
fi

# ── MCP route tests ───────────────────────────────────────────
MCP_HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://arifos.arif-fazil.com/health" 2>/dev/null || echo "000")
MCP_TOOLS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://arifos.arif-fazil.com/tools" 2>/dev/null || echo "000")
MCP_MCP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "Accept: text/event-stream" "https://arifos.arif-fazil.com/mcp" 2>/dev/null || echo "000")
MCP_ROUTE_PASS=true
if [ "$MCP_HEALTH_CODE" != "200" ]; then
    MCP_ROUTE_PASS=false
    REASONS+=("mcp_health_fail:$MCP_HEALTH_CODE")
fi
if [ "$MCP_TOOLS_CODE" != "200" ]; then
    MCP_ROUTE_PASS=false
    REASONS+=("mcp_tools_fail:$MCP_TOOLS_CODE")
fi
if [ "$MCP_MCP_CODE" != "200" ] && [ "$MCP_MCP_CODE" != "406" ]; then
    if [ "$MCP_MCP_CODE" = "404" ] || [ "$MCP_MCP_CODE" = "502" ] || [ "$MCP_MCP_CODE" = "000" ]; then
        MCP_ROUTE_PASS=false
        REASONS+=("mcp_route_fail:$MCP_MCP_CODE")
    fi
fi

# ── Satellite services ────────────────────────────────────────
GEOX_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://geox.arif-fazil.com/mcp" 2>/dev/null || echo "000")
WELL_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://well.arif-fazil.com/health" 2>/dev/null || echo "000")
WEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "http://127.0.0.1:8082/health" 2>/dev/null || echo "000")

# ── Vault health ──────────────────────────────────────────────
VAULT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:8100/health" 2>/dev/null || echo "000")

# ── Graphiti / Neo4j ──────────────────────────────────────────
GRAPHITI_STATUS="unknown"
GRAPHITI_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:8007/health" 2>/dev/null || echo "000")
if [ "$GRAPHITI_CODE" = "200" ]; then
    GRAPHITI_STATUS="healthy"
elif [ "$GRAPHITI_CODE" = "429" ]; then
    GRAPHITI_STATUS="DEGRADED_OPENAI_429"
    KNOWN_GAPS+=("graphiti_429_rate_limited")
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("graphiti_degraded_429")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
else
    GRAPHITI_STATUS="not_reachable:$GRAPHITI_CODE"
    KNOWN_GAPS+=("graphiti_not_wired")
fi

# ── Langfuse ──────────────────────────────────────────────────
LANGFUSE_STATUS="unknown"
LANGFUSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:3003/api/public/health" 2>/dev/null || echo "000")
if [ "$LANGFUSE_CODE" = "200" ]; then
    LANGFUSE_STATUS="wired"
else
    LANGFUSE_STATUS="NOT_WIRED"
    KNOWN_GAPS+=("langfuse_not_wired")
fi

# ── Evaluate seal readiness ───────────────────────────────────
if [ "$RUNTIME_DRIFT" = "true" ]; then
    SEAL_RECOMMENDATION="HOLD"
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("runtime_drift_detected")
    [ "$RISK" = "LOW" ] && RISK="HIGH"
fi

if [ "$HEALTH_STATUS" != "healthy" ]; then
    SEAL_RECOMMENDATION="HOLD"
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("arifosmcp_not_healthy:$HEALTH_STATUS")
    [ "$RISK" = "LOW" ] && RISK="HIGH"
fi

if [ "$MCP_ROUTE_PASS" != "true" ]; then
    SEAL_RECOMMENDATION="HOLD"
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("mcp_route_tests_failed")
    [ "$RISK" = "LOW" ] && RISK="HIGH"
fi

if [ "$VAULT_HEALTH" != "200" ]; then
    SEAL_RECOMMENDATION="HOLD"
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("vault_health_not_200:$VAULT_HEALTH")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
fi

if [ ${#KNOWN_GAPS[@]} -gt 0 ]; then
    if [ "$SEAL_RECOMMENDATION" = "READY" ]; then
        SEAL_RECOMMENDATION="READY_WITH_GAPS"
    fi
fi

# ── Print report ──────────────────────────────────────────────
echo "=== PRESEAL EVIDENCE ==="
echo "host:                $HOSTNAME"
echo "git_commit:          $GIT_COMMIT"
echo "git_branch:          $GIT_BRANCH"
echo "image_digest:        $ARIFOS_IMAGE_DIGEST"
echo "image_id:            $ARIFOS_IMAGE_ID"
echo "schema_hash:         $SCHEMA_HASH"
echo "tool_registry_hash:  $TOOL_REGISTRY_HASH"
echo "constitutional_hash: $CONSTITUTIONAL_MAP_HASH"
echo "runtime_drift:       $RUNTIME_DRIFT"
echo "health_status:       $HEALTH_STATUS"
echo "mcp_health:          $MCP_HEALTH_CODE"
echo "mcp_tools:           $MCP_TOOLS_CODE"
echo "mcp_mcp:             $MCP_MCP_CODE"
echo "geox_mcp:            $GEOX_CODE"
echo "well_health:         $WELL_CODE"
echo "wealth_health:       $WEALTH_CODE"
echo "vault_health:        $VAULT_HEALTH"
echo "graphiti_status:     $GRAPHITI_STATUS"
echo "langfuse_status:     $LANGFUSE_STATUS"
echo "known_gaps:          ${KNOWN_GAPS[*]}"
echo ""
echo "seal_recommendation: $SEAL_RECOMMENDATION"
echo "status:              $STATUS"
echo "risk:                $RISK"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

# ── Write evidence JSON ───────────────────────────────────────
REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')
GAPS_JSON=$(printf '%s\n' "${KNOWN_GAPS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')

cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "preseal_evidence",
  "status": "$STATUS",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "host": "$HOSTNAME",
    "git_commit": "$GIT_COMMIT",
    "git_branch": "$GIT_BRANCH",
    "image_digest": "$ARIFOS_IMAGE_DIGEST",
    "image_id": "$ARIFOS_IMAGE_ID",
    "schema_hash": "$SCHEMA_HASH",
    "tool_registry_hash": "$TOOL_REGISTRY_HASH",
    "constitutional_map_hash": "$CONSTITUTIONAL_MAP_HASH",
    "runtime_drift": $RUNTIME_DRIFT,
    "health_status": "$HEALTH_STATUS",
    "mcp_routes": {
      "health": "$MCP_HEALTH_CODE",
      "tools": "$MCP_TOOLS_CODE",
      "mcp_sse": "$MCP_MCP_CODE",
      "pass": $MCP_ROUTE_PASS
    },
    "satellites": {
      "geox_mcp": "$GEOX_CODE",
      "well_health": "$WELL_CODE",
      "wealth_health": "$WEALTH_CODE"
    },
    "vault_health": "$VAULT_HEALTH",
    "graphiti_status": "$GRAPHITI_STATUS",
    "langfuse_status": "$LANGFUSE_STATUS",
    "known_gaps": $GAPS_JSON,
    "seal_recommendation": "$SEAL_RECOMMENDATION"
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$SEAL_RECOMMENDATION" = "READY" ] || [ "$SEAL_RECOMMENDATION" = "READY_WITH_GAPS" ]; then echo '"proceed_to_vault_seal"'; else echo '"resolve_hold_conditions_before_seal"'; fi),
  "requires_arif": $(if [ "$SEAL_RECOMMENDATION" != "READY" ]; then echo 'true'; else echo 'false'; fi)
}
EOF

echo ""
echo "evidence:    $EVIDENCE_FILE"
echo "=== END PRESEAL ==="

[ "$STATUS" != "FAIL" ]
