#!/bin/bash
# rollback_service.sh — Safe rollback for a Docker Compose service
# Skill: rollback_captain
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="${SCRIPT_DIR}/.."
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/rollback_service_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

COMPOSE_DIR="${COMPOSE_DIR:-/root/compose}"
COMPOSE_FILE="${COMPOSE_FILE:-$COMPOSE_DIR/docker-compose.yml}"
COMPOSE_CMD="docker compose -f $COMPOSE_FILE"

SERVICE="${1:-}"
PREVIOUS_DIGEST="${2:-}"

STATUS="PASS"
REASONS=()
RISK="LOW"
ROLLED_BACK=false
HEALTH_STATUS="unknown"
CURRENT_IMAGE=""
COMPOSE_BACKUP=""

write_evidence_and_exit() {
    REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')
    cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "rollback_service",
  "status": "$STATUS",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "service": "$SERVICE",
    "current_image": "$CURRENT_IMAGE",
    "restored_image": "$PREVIOUS_DIGEST",
    "rolled_back": $ROLLED_BACK,
    "health_status": "$HEALTH_STATUS",
    "compose_backup": "$COMPOSE_BACKUP"
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$STATUS" = "FAIL" ]; then echo '"manual_intervention_required"'; else echo '"monitor_and_validate_service"'; fi),
  "requires_arif": $(if [ "$STATUS" != "PASS" ]; then echo 'true'; else echo 'false'; fi)
}
EOF
    echo ""
    echo "evidence:    $EVIDENCE_FILE"
    echo "=== END ROLLBACK ==="
    if [ "$STATUS" = "FAIL" ]; then
        exit 1
    else
        exit 0
    fi
}

usage() {
    echo "Usage: $0 <service_name> <previous_image_or_digest>"
    echo "Example: $0 arifosmcp arifos@sha256:abc123..."
    exit 1
}

if [ -z "$SERVICE" ] || [ -z "$PREVIOUS_DIGEST" ]; then
    usage
fi

echo "=== ROLLBACK $SERVICE ==="
echo "timestamp:       $TIMESTAMP"
echo "service:         $SERVICE"
echo "target_image:    $PREVIOUS_DIGEST"

# ── Safety: refuse dangerous rollbacks ────────────────────────
DANGEROUS_SERVICES=("postgres" "vault999" "redis" "qdrant" "neo4j" "clickhouse" "minio")
for ds in "${DANGEROUS_SERVICES[@]}"; do
    if [ "$SERVICE" = "$ds" ]; then
        echo "FAIL: rollback of $SERVICE is DANGEROUS and blocked."
        echo "      Data migrations or stateful services require ARIF explicit confirmation."
        STATUS="FAIL"
        REASONS+=("rollback_blocked_dangerous_service:$SERVICE")
        RISK="CRITICAL"
        write_evidence_and_exit
    fi
done

# ── Verify compose file exists ────────────────────────────────
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "FAIL: compose file not found: $COMPOSE_FILE"
    STATUS="FAIL"
    REASONS+=("compose_file_missing")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

# ── Capture current state ─────────────────────────────────────
CURRENT_IMAGE=$($COMPOSE_CMD ps -q "$SERVICE" 2>/dev/null | xargs -I{} docker inspect --format='{{.Config.Image}}' {} 2>/dev/null || echo "")
if [ -z "$CURRENT_IMAGE" ]; then
    CURRENT_IMAGE=$(yq eval ".services.${SERVICE}.image" "$COMPOSE_FILE" 2>/dev/null || echo "unknown")
fi

echo "  current_image:   $CURRENT_IMAGE"

# ── Update compose and rollback ───────────────────────────────
COMPOSE_BACKUP="$COMPOSE_FILE.rollback_backup_${TIMESTAMP}"
cp "$COMPOSE_FILE" "$COMPOSE_BACKUP"

if command -v yq >/dev/null 2>&1; then
    yq eval ".services.${SERVICE}.image = \"${PREVIOUS_DIGEST}\"" -i "$COMPOSE_FILE"
else
    sed -i "s|image: .*|image: ${PREVIOUS_DIGEST}|" "$COMPOSE_FILE"
fi

if ! $COMPOSE_CMD config > /dev/null 2>"$TMP_DIR/compose_validate.err"; then
    echo "FAIL: compose invalid after rollback update. Restoring backup."
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    STATUS="FAIL"
    REASONS+=("compose_invalid_after_rollback")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

echo ""
echo "[ROLLBACK] Restarting $SERVICE with $PREVIOUS_DIGEST..."
if $COMPOSE_CMD up -d --no-deps "$SERVICE" > "$TMP_DIR/rollback.log" 2>&1; then
    echo "  ROLLBACK EXECUTED: $SERVICE restarted"
    ROLLED_BACK=true
else
    echo "  ROLLBACK FAIL"
    cat "$TMP_DIR/rollback.log"
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    STATUS="FAIL"
    REASONS+=("rollback_restart_failed")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

# ── Wait for health ───────────────────────────────────────────
echo ""
echo "[HEALTH] Waiting for $SERVICE to become healthy..."
for i in $(seq 1 30); do
    CONTAINER_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$SERVICE" 2>/dev/null || echo "none")
    if [ "$CONTAINER_HEALTH" = "healthy" ]; then
        HEALTH_STATUS="healthy"
        echo "  HEALTH PASS after ${i} attempts"
        break
    fi
    echo "  ... health=$CONTAINER_HEALTH (attempt $i/30)"
    sleep 2
done

if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "  HEALTH FAIL: $SERVICE not healthy after 60s"
    STATUS="FAIL"
    REASONS+=("rollback_health_failed")
    RISK="HIGH"
else
    echo "  ROLLBACK VERIFIED: $SERVICE is healthy"
fi

# ── Final report ──────────────────────────────────────────────
echo ""
echo "=== ROLLBACK VERDICT ==="
echo "status:      $STATUS"
echo "risk:        $RISK"
echo "rolled_back: $ROLLED_BACK"
echo "previous:    $CURRENT_IMAGE"
echo "restored:    $PREVIOUS_DIGEST"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

write_evidence_and_exit
