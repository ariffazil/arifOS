#!/bin/bash
# deploy_arifosmcp.sh — Safe deploy script for arifosmcp service
# Skill: release_captain + health_contract_engine + rollback_captain
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="${SCRIPT_DIR}/.."
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/deploy_arifosmcp_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

SERVICE="arifosmcp"
CONTAINER_NAME="arifosmcp"
COMPOSE_DIR="${COMPOSE_DIR:-/root/compose}"
COMPOSE_FILE="${COMPOSE_FILE:-$COMPOSE_DIR/docker-compose.yml}"
ARIFOS_DIR="${ARIFOS_DIR:-/root/arifOS}"
COMPOSE_CMD="docker compose -f $COMPOSE_FILE"

PUBLIC_HEALTH_URL="https://arifos.arif-fazil.com/health"
PUBLIC_TOOLS_URL="https://arifos.arif-fazil.com/tools"
PUBLIC_MCP_URL="https://mcp.arif-fazil.com/mcp"

STATUS="PASS"
REASONS=()
RISK="LOW"
DEPLOYED=false
ROLLED_BACK=false
PREVIOUS_IMAGE=""
NEW_IMAGE=""
NEW_DIGEST=""
GIT_COMMIT=""
BUILD_TIME=""
HEALTH_STATUS="unknown"
HEALTH_CODE="000"
TOOLS_CODE="000"
MCP_CODE="000"
ROUTE_PASS=true
COMPOSE_BACKUP=""

write_evidence_and_exit() {
    REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')
    cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "deploy_arifosmcp",
  "status": "$STATUS",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "service": "$SERVICE",
    "git_commit": "$GIT_COMMIT",
    "git_branch": "$GIT_BRANCH",
    "git_dirty": "$GIT_DIRTY",
    "previous_image": "$PREVIOUS_IMAGE",
    "new_image": "$NEW_IMAGE",
    "new_digest": "$NEW_DIGEST",
    "deployed": $DEPLOYED,
    "rolled_back": $ROLLED_BACK,
    "health_status": "$HEALTH_STATUS",
    "public_health_code": "$HEALTH_CODE",
    "public_tools_code": "$TOOLS_CODE",
    "public_mcp_code": "$MCP_CODE",
    "route_pass": $ROUTE_PASS,
    "compose_backup": "$COMPOSE_BACKUP"
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$STATUS" = "FAIL" ]; then echo '"investigate_and_manual_fix"'; elif [ "$ROLLED_BACK" = "true" ]; then echo '"review_logs_before_retry"'; else echo '"proceed_to_preseal_evidence"'; fi),
  "requires_arif": $(if [ "$STATUS" != "PASS" ] || [ "$ROLLED_BACK" = "true" ]; then echo 'true'; else echo 'false'; fi)
}
EOF
    echo ""
    echo "evidence:    $EVIDENCE_FILE"
    echo "=== END DEPLOY ==="
    if [ "$STATUS" = "FAIL" ]; then
        exit 1
    else
        exit 0
    fi
}

echo "=== DEPLOY arifosmcp ==="
echo "timestamp:   $TIMESTAMP"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "FAIL: compose file not found: $COMPOSE_FILE"
    STATUS="FAIL"
    REASONS+=("compose_file_missing")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

# ── 0. Capture rollback state ─────────────────────────────────
echo ""
echo "[0/7] Capturing rollback state..."
PREVIOUS_IMAGE=$($COMPOSE_CMD ps -q "$SERVICE" 2>/dev/null | xargs -I{} docker inspect --format='{{.Config.Image}}' {} 2>/dev/null || echo "")
if [ -z "$PREVIOUS_IMAGE" ]; then
    PREVIOUS_IMAGE=$(yq eval ".services.${SERVICE}.image" "$COMPOSE_FILE" 2>/dev/null || echo "")
fi
if [ -z "$PREVIOUS_IMAGE" ] && docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    PREVIOUS_IMAGE=$(docker inspect --format='{{.Config.Image}}' "$CONTAINER_NAME" 2>/dev/null || echo "")
fi

if [ -z "$PREVIOUS_IMAGE" ] || [ "$PREVIOUS_IMAGE" = "null" ]; then
    echo "FAIL: cannot determine previous image for rollback. HOLD."
    STATUS="FAIL"
    REASONS+=("rollback_path_missing:previous_image_unknown")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

echo "  previous_image: $PREVIOUS_IMAGE"

# ── 1. Git state ──────────────────────────────────────────────
echo ""
echo "[1/7] Git state..."
cd "$ARIFOS_DIR"
GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")
GIT_DIRTY=$(git diff --quiet && git diff --cached --quiet && echo "clean" || echo "dirty")

echo "  commit:    $GIT_COMMIT"
echo "  branch:    $GIT_BRANCH"
echo "  dirty:     $GIT_DIRTY"

if [ "$GIT_DIRTY" != "clean" ]; then
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("git_working_tree_dirty")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
    echo "  WARNING: working tree is dirty"
fi

# ── 2. Pre-deploy audit ───────────────────────────────────────
echo ""
echo "[2/7] Running pre-deploy audit..."
if [ -x "$SCRIPT_DIR/predeploy_audit.sh" ]; then
    if "$SCRIPT_DIR/predeploy_audit.sh" > "$TMP_DIR/predeploy.log" 2>&1; then
        AUDIT_STATUS=$(grep -E '^status:' "$TMP_DIR/predeploy.log" | awk '{print $2}' || echo "UNKNOWN")
        echo "  predeploy_audit: $AUDIT_STATUS"
        if [ "$AUDIT_STATUS" = "FAIL" ]; then
            echo "FAIL: predeploy audit failed. Deploy blocked."
            STATUS="FAIL"
            REASONS+=("predeploy_audit_fail")
            RISK="CRITICAL"
            write_evidence_and_exit
        fi
        if [ "$AUDIT_STATUS" = "HOLD" ]; then
            echo "HOLD: predeploy audit has warnings. Continue with caution."
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("predeploy_audit_hold")
        fi
    else
        echo "FAIL: predeploy audit script failed"
        STATUS="FAIL"
        REASONS+=("predeploy_audit_error")
        RISK="CRITICAL"
        write_evidence_and_exit
    fi
else
    echo "WARNING: predeploy_audit.sh not found — skipping"
fi

# ── 3. Build image ────────────────────────────────────────────
echo ""
echo "[3/7] Building image..."
BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
BUILD_TAG="arifos:${GIT_COMMIT:0:12}"
BUILD_LOG="$TMP_DIR/build.log"

if docker build \
    -t "$BUILD_TAG" \
    -f "$ARIFOS_DIR/Dockerfile" \
    --build-arg ARIFOS_BUILD_SHA="$GIT_COMMIT" \
    --build-arg ARIFOS_BUILD_BRANCH="$GIT_BRANCH" \
    --build-arg ARIFOS_BUILD_TIME="$BUILD_TIME" \
    "$ARIFOS_DIR" > "$BUILD_LOG" 2>&1; then
    echo "  BUILD PASS: $BUILD_TAG"
else
    echo "  BUILD FAIL"
    tail -50 "$BUILD_LOG"
    STATUS="FAIL"
    REASONS+=("docker_build_failed")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

NEW_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$BUILD_TAG" 2>/dev/null || echo "")
if [ -z "$NEW_DIGEST" ]; then
    NEW_DIGEST=$(docker inspect --format='{{.Id}}' "$BUILD_TAG" 2>/dev/null || echo "")
fi
NEW_IMAGE="$BUILD_TAG"
echo "  image_id/digest: $NEW_DIGEST"

# ── 4. Import truth in image ──────────────────────────────────
echo ""
echo "[4/7] Import truth check in new image..."
IMPORT_LOG="$TMP_DIR/import_truth_image.log"
if ARIFOS_IMAGE="$BUILD_TAG" "$SCRIPT_DIR/import_truth.sh" > "$IMPORT_LOG" 2>&1; then
    IMPORT_STATUS=$(grep -E '^status:' "$IMPORT_LOG" | awk '{print $2}' || echo "UNKNOWN")
    echo "  import_truth: $IMPORT_STATUS"
    if [ "$IMPORT_STATUS" != "PASS" ]; then
        echo "FAIL: import truth failed in new image. Deploy blocked."
        STATUS="FAIL"
        REASONS+=("import_truth_image_fail:$IMPORT_STATUS")
        RISK="CRITICAL"
        write_evidence_and_exit
    fi
else
    echo "FAIL: import truth check failed"
    STATUS="FAIL"
    REASONS+=("import_truth_image_error")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

# ── 5. Update compose and deploy ──────────────────────────────
echo ""
echo "[5/7] Deploying service..."
COMPOSE_BACKUP="$COMPOSE_FILE.deploy_backup_${TIMESTAMP}"
cp "$COMPOSE_FILE" "$COMPOSE_BACKUP"

if command -v yq >/dev/null 2>&1; then
    yq eval ".services.${SERVICE}.image = \"${BUILD_TAG}\"" -i "$COMPOSE_FILE"
    yq eval "del(.services.${SERVICE}.volumes)" -i "$COMPOSE_FILE" 2>/dev/null || true
else
    echo "WARNING: yq not available — using sed fallback"
    sed -i "s|image: .*arifos.*|image: ${BUILD_TAG}|" "$COMPOSE_FILE"
fi

if ! $COMPOSE_CMD config > /dev/null 2>"$TMP_DIR/compose_validate.err"; then
    echo "FAIL: compose invalid after image update. Restoring backup."
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    STATUS="FAIL"
    REASONS+=("compose_invalid_after_update")
    RISK="CRITICAL"
    write_evidence_and_exit
fi

if $COMPOSE_CMD up -d --no-deps "$SERVICE" > "$TMP_DIR/deploy.log" 2>&1; then
    echo "  DEPLOY PASS: $SERVICE restarted"
    DEPLOYED=true
else
    echo "  DEPLOY FAIL"
    cat "$TMP_DIR/deploy.log"
    echo "  Attempting automatic rollback..."
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    if $COMPOSE_CMD up -d --no-deps "$SERVICE" > "$TMP_DIR/rollback_auto.log" 2>&1; then
        echo "  ROLLBACK PASS: restored $PREVIOUS_IMAGE"
        ROLLED_BACK=true
        STATUS="FAIL"
        REASONS+=("deploy_failed_rollback_success")
        RISK="HIGH"
    else
        echo "  ROLLBACK FAIL: manual intervention required"
        STATUS="FAIL"
        REASONS+=("deploy_failed_rollback_failed")
        RISK="CRITICAL"
    fi
    write_evidence_and_exit
fi

# ── 6. Health wait ────────────────────────────────────────────
echo ""
echo "[6/7] Waiting for health..."
for i in $(seq 1 30); do
    CONTAINER_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "none")
    if [ "$CONTAINER_HEALTH" = "healthy" ]; then
        HEALTH_STATUS="healthy"
        echo "  HEALTH PASS after ${i} attempts"
        break
    fi
    echo "  ... health=$CONTAINER_HEALTH (attempt $i/30)"
    sleep 2
done

if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "  HEALTH FAIL: container not healthy after 60s"
    echo "  Attempting automatic rollback..."
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    if $COMPOSE_CMD up -d --no-deps "$SERVICE" > "$TMP_DIR/rollback_health.log" 2>&1; then
        echo "  ROLLBACK PASS: restored $PREVIOUS_IMAGE"
        ROLLED_BACK=true
        STATUS="FAIL"
        REASONS+=("health_failed_rollback_success")
        RISK="HIGH"
    else
        echo "  ROLLBACK FAIL"
        STATUS="FAIL"
        REASONS+=("health_failed_rollback_failed")
        RISK="CRITICAL"
    fi
    write_evidence_and_exit
fi

# ── 7. Public route tests ─────────────────────────────────────
echo ""
echo "[7/7] Public route tests..."
HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$PUBLIC_HEALTH_URL" 2>/dev/null || echo "000")
TOOLS_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$PUBLIC_TOOLS_URL" 2>/dev/null || echo "000")
MCP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "Accept: text/event-stream" "$PUBLIC_MCP_URL" 2>/dev/null || echo "000")

echo "  /health => $HEALTH_CODE"
echo "  /tools  => $TOOLS_CODE"
echo "  /mcp    => $MCP_CODE (with SSE Accept)"

if [ "$HEALTH_CODE" != "200" ]; then
    ROUTE_PASS=false
    REASONS+=("public_health_not_200:$HEALTH_CODE")
fi
if [ "$TOOLS_CODE" != "200" ]; then
    ROUTE_PASS=false
    REASONS+=("public_tools_not_200:$TOOLS_CODE")
fi
if [ "$MCP_CODE" != "200" ] && [ "$MCP_CODE" != "406" ]; then
    if [ "$MCP_CODE" = "404" ] || [ "$MCP_CODE" = "502" ] || [ "$MCP_CODE" = "000" ]; then
        ROUTE_PASS=false
        REASONS+=("public_mcp_fail:$MCP_CODE")
    fi
fi

if [ "$ROUTE_PASS" != "true" ]; then
    echo "  ROUTE FAIL — attempting rollback..."
    cp "$COMPOSE_BACKUP" "$COMPOSE_FILE"
    if $COMPOSE_CMD up -d --no-deps "$SERVICE" > "$TMP_DIR/rollback_route.log" 2>&1; then
        echo "  ROLLBACK PASS: restored $PREVIOUS_IMAGE"
        ROLLED_BACK=true
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("route_test_failed_rollback_success")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
    else
        echo "  ROLLBACK FAIL"
        STATUS="FAIL"
        REASONS+=("route_test_failed_rollback_failed")
        RISK="CRITICAL"
        write_evidence_and_exit
    fi
else
    echo "  ROUTE PASS"
fi

if [ "$STATUS" = "PASS" ] && [ "$ROLLED_BACK" != "true" ]; then
    rm -f "$COMPOSE_BACKUP"
    echo ""
    echo "  Deploy sealed — backup removed."
fi

# ── Final report ──────────────────────────────────────────────
echo ""
echo "=== DEPLOY VERDICT ==="
echo "status:      $STATUS"
echo "risk:        $RISK"
echo "deployed:    $DEPLOYED"
echo "rolled_back: $ROLLED_BACK"
echo "previous:    $PREVIOUS_IMAGE"
echo "new:         $NEW_IMAGE"
echo "new_digest:  $NEW_DIGEST"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

write_evidence_and_exit
