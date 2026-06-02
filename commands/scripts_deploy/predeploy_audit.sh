#!/bin/bash
# predeploy_audit.sh — Pre-deploy audit for arifOS federation stack
# Skill: compose_guardian + health_contract_engine + policy_gatekeeper
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="${SCRIPT_DIR}/.."
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/predeploy_audit_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

COMPOSE_DIR="${COMPOSE_DIR:-/root/compose}"
COMPOSE_FILE="${COMPOSE_FILE:-$COMPOSE_DIR/docker-compose.yml}"
CADDY_FILE="${CADDY_FILE:-$COMPOSE_DIR/Caddyfile}"
ARIFOS_DIR="${ARIFOS_DIR:-/root/arifOS}"

STATUS="PASS"
REASONS=()
RISK="LOW"
POLICY_RULES=()

echo "=== PREDEPLOY AUDIT ==="
echo "compose:     $COMPOSE_FILE"
echo "caddyfile:   $CADDY_FILE"
echo "arifos_dir:  $ARIFOS_DIR"
echo ""

# ── 1. Compose config validation ──────────────────────────────
echo "[1/8] Compose config validation..."
COMPOSE_VALID=false
if [ -f "$COMPOSE_FILE" ]; then
    if docker compose -f "$COMPOSE_FILE" config > "$TMP_DIR/compose_config.yml" 2>"$TMP_DIR/compose_config.err"; then
        COMPOSE_VALID=true
        echo "  PASS: docker compose config validates"
    else
        STATUS="FAIL"
        REASONS+=("compose_config_invalid")
        RISK="CRITICAL"
        echo "  FAIL: docker compose config invalid"
        cat "$TMP_DIR/compose_config.err" | head -10
    fi
else
    STATUS="FAIL"
    REASONS+=("compose_file_missing:$COMPOSE_FILE")
    RISK="CRITICAL"
    echo "  FAIL: compose file missing"
fi

# ── 2. Healthcheck audit ──────────────────────────────────────
echo ""
echo "[2/8] Healthcheck audit..."
HEALTHCHECK_PASS=true
REQUIRED_SERVICES=("arifosmcp" "postgres" "redis" "qdrant" "vault999" "geox" "wealth-organ" "well")
MISSING_HEALTHCHECKS=()

for svc in "${REQUIRED_SERVICES[@]}"; do
    HAS_HC=$(yq eval ".services.${svc}.healthcheck" "$COMPOSE_FILE" 2>/dev/null || true)
    if [ -z "$HAS_HC" ] || [ "$HAS_HC" = "null" ]; then
        MISSING_HEALTHCHECKS+=("$svc")
        HEALTHCHECK_PASS=false
        if [ "$svc" = "arifosmcp" ] || [ "$svc" = "postgres" ] || [ "$svc" = "vault999" ]; then
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("missing_healthcheck_critical:$svc")
            [ "$RISK" = "LOW" ] && RISK="HIGH"
        fi
    fi
done

if [ ${#MISSING_HEALTHCHECKS[@]} -eq 0 ]; then
    echo "  PASS: all required services have healthchecks"
else
    echo "  HOLD: missing healthchecks for: ${MISSING_HEALTHCHECKS[*]}"
fi

# ── 3. Public port exposure audit ─────────────────────────────
echo ""
echo "[3/8] Public port exposure audit..."
PUBLIC_PORT_PASS=true
DB_SERVICES=("postgres" "redis" "qdrant" "neo4j" "clickhouse" "minio")
EXPOSED_DB_PORTS=()

for svc in "${DB_SERVICES[@]}"; do
    PORTS=$(yq eval ".services.${svc}.ports[]" "$COMPOSE_FILE" 2>/dev/null || true)
    if [ -n "$PORTS" ] && [ "$PORTS" != "null" ]; then
        while IFS= read -r port_line; do
            if [[ "$port_line" != *"127.0.0.1"* ]] && [[ "$port_line" != *"::1"* ]]; then
                EXPOSED_DB_PORTS+=("$svc:$port_line")
                PUBLIC_PORT_PASS=false
                [ "$STATUS" = "PASS" ] && STATUS="HOLD"
                REASONS+=("db_port_publicly_exposed:$svc:$port_line")
                [ "$RISK" = "LOW" ] && RISK="HIGH"
            fi
        done <<< "$PORTS"
    fi
done

if [ ${#EXPOSED_DB_PORTS[@]} -eq 0 ]; then
    echo "  PASS: no DB services publicly exposed"
else
    echo "  HOLD: exposed DB ports:"
    for ep in "${EXPOSED_DB_PORTS[@]}"; do echo "    - $ep"; done
fi

# ── 4. Image tag vs digest audit ──────────────────────────────
echo ""
echo "[4/8] Image tag vs digest audit..."
IMAGE_TAG_PASS=true
LATEST_IMAGES=()
NO_DIGEST_IMAGES=()

IMAGES=$(yq eval '.services | to_entries | .[] | select(.value.image) | "\(.key)=\(.value.image)"' "$COMPOSE_FILE" 2>/dev/null || true)
while IFS='=' read -r svc img; do
    if [ -n "$svc" ] && [ -n "$img" ]; then
        if [[ "$img" == *":latest"* ]]; then
            LATEST_IMAGES+=("$svc:$img")
            IMAGE_TAG_PASS=false
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("image_uses_latest:$svc:$img")
            [ "$RISK" = "LOW" ] && RISK="MEDIUM"
        fi
        if [[ "$img" != *"@sha256:"* ]]; then
            NO_DIGEST_IMAGES+=("$svc:$img")
        fi
    fi
done <<< "$IMAGES"

if [ ${#LATEST_IMAGES[@]} -eq 0 ]; then
    echo "  PASS: no images use :latest"
else
    echo "  HOLD: images using :latest:"
    for li in "${LATEST_IMAGES[@]}"; do echo "    - $li"; done
fi

if [ ${#NO_DIGEST_IMAGES[@]} -gt 0 ]; then
    echo "  NOTE: images without digest (seal recommendation: use digest):"
    for nd in "${NO_DIGEST_IMAGES[@]}"; do echo "    - $nd"; done
fi

# ── 5. Live mount / runtime drift audit ───────────────────────
echo ""
echo "[5/8] Live mount / runtime drift audit..."
DRIFT_PASS=true
MOUNTED_SERVICES=()

MOUNTS=$(yq eval '.services | to_entries | .[] | select(.value.volumes) | "\(.key)=\(.value.volumes | length)"' "$COMPOSE_FILE" 2>/dev/null || true)
while IFS='=' read -r svc count; do
    if [ -n "$svc" ] && [ "$count" != "0" ]; then
        RAW_MOUNTS=$(yq eval ".services.${svc}.volumes[]" "$COMPOSE_FILE" 2>/dev/null || true)
        while IFS= read -r mnt; do
            if [[ "$mnt" == *"/root/arifOS:/app"* ]] || [[ "$mnt" == *"/root/geox:/app"* ]] || [[ "$mnt" == *"/root/WEALTH:/app"* ]] || [[ "$mnt" == *"/root/well:/app"* ]]; then
                MOUNTED_SERVICES+=("$svc:$mnt")
                DRIFT_PASS=false
                [ "$STATUS" = "PASS" ] && STATUS="HOLD"
                REASONS+=("live_mount_detected:$svc:$mnt")
                [ "$RISK" = "LOW" ] && RISK="HIGH"
            fi
        done <<< "$RAW_MOUNTS"
    fi
done <<< "$MOUNTS"

if [ ${#MOUNTED_SERVICES[@]} -eq 0 ]; then
    echo "  PASS: no source-code live mounts detected"
else
    echo "  HOLD: live mounts detected (runtime drift risk):"
    for ms in "${MOUNTED_SERVICES[@]}"; do echo "    - $ms"; done
fi

# ── 6. Import truth check ─────────────────────────────────────
echo ""
echo "[6/8] Import truth check..."
IMPORT_TRUTH_PASS=true
if [ -x "$SCRIPT_DIR/import_truth.sh" ]; then
    if "$SCRIPT_DIR/import_truth.sh" > "$TMP_DIR/import_truth.log" 2>&1; then
        IMPORT_TRUTH_STATUS=$(grep -E '^status:' "$TMP_DIR/import_truth.log" | awk '{print $2}' || echo "UNKNOWN")
        if [ "$IMPORT_TRUTH_STATUS" != "PASS" ]; then
            IMPORT_TRUTH_PASS=false
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("import_truth_not_pass:$IMPORT_TRUTH_STATUS")
            [ "$RISK" = "LOW" ] && RISK="HIGH"
        fi
        echo "  PASS: import_truth.sh returned $IMPORT_TRUTH_STATUS"
    else
        IMPORT_TRUTH_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("import_truth_failed")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
        echo "  FAIL: import_truth.sh failed"
    fi
else
    IMPORT_TRUTH_PASS=false
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("import_truth_script_missing")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
    echo "  HOLD: import_truth.sh not found or not executable"
fi

# ── 7. Caddy route validation ─────────────────────────────────
echo ""
echo "[7/8] Caddy route validation..."
CADDY_PASS=true
if [ -f "$CADDY_FILE" ]; then
    REQUIRED_ROUTES=("arifos.arif-fazil.com" "mcp.arif-fazil.com" "geox.arif-fazil.com" "well.arif-fazil.com" "health" "mcp")
    MISSING_ROUTES=()
    for route in "${REQUIRED_ROUTES[@]}"; do
        if ! grep -q "$route" "$CADDY_FILE"; then
            MISSING_ROUTES+=("$route")
            CADDY_PASS=false
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("caddy_missing_route:$route")
            [ "$RISK" = "LOW" ] && RISK="MEDIUM"
        fi
    done
    if [ ${#MISSING_ROUTES[@]} -eq 0 ]; then
        echo "  PASS: critical Caddy routes present"
    else
        echo "  HOLD: missing Caddy routes: ${MISSING_ROUTES[*]}"
    fi
else
    CADDY_PASS=false
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("caddyfile_missing:$CADDY_FILE")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
    echo "  HOLD: Caddyfile missing"
fi

# ── 8. Tool registry hash check ───────────────────────────────
echo ""
echo "[8/8] Tool registry / schema hash check..."
REGISTRY_PASS=true
TOOL_REGISTRY="$ARIFOS_DIR/arifosmcp/tool_registry.json"
CONSTITUTIONAL_MAP="$ARIFOS_DIR/arifosmcp/constitutional_map.py"
SCHEMA_DIR="$ARIFOS_DIR/arifosmcp/schemas"

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

TOOL_REGISTRY_HASH=$(compute_hash "$TOOL_REGISTRY")
CONSTITUTIONAL_MAP_HASH=$(compute_hash "$CONSTITUTIONAL_MAP")
SCHEMA_HASH=$(compute_hash "$SCHEMA_DIR")
GIT_COMMIT=$(git -C "$ARIFOS_DIR" rev-parse HEAD 2>/dev/null || echo "UNKNOWN")
GIT_BRANCH=$(git -C "$ARIFOS_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "UNKNOWN")

echo "  git_commit:           $GIT_COMMIT"
echo "  git_branch:           $GIT_BRANCH"
echo "  tool_registry_hash:   $TOOL_REGISTRY_HASH"
echo "  constitutional_hash:  $CONSTITUTIONAL_MAP_HASH"
echo "  schema_hash:          $SCHEMA_HASH"

if [ "$TOOL_REGISTRY_HASH" = "MISSING" ]; then
    REGISTRY_PASS=false
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("tool_registry_missing")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
fi

# AGENTS.md auto-gen drift check — must be in sync with CANONICAL_TOOLS
# (Single source of truth: arifosmcp/constitutional_map.py)
if [ -f "$ARIFOS_DIR/arifosmcp/maintenance/generate_agents_md.py" ]; then
    if (cd "$ARIFOS_DIR" && python3 -m arifosmcp.maintenance.generate_agents_md --check) \
            > "$TMP_DIR/agents_md_check.log" 2>&1; then
        echo "  PASS: AGENTS.md is in sync with CANONICAL_TOOLS"
    else
        REGISTRY_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("agents_md_drift_detected")
        [ "$RISK" = "LOW" ] && RISK="MEDIUM"
        echo "  FAIL: AGENTS.md has drifted from CANONICAL_TOOLS"
        echo "        Remediation:"
        echo "          cd $ARIFOS_DIR"
        echo "          python3 -m arifosmcp.maintenance.generate_agents_md"
        echo "          git add arifosmcp/AGENTS.md && git commit"
        cat "$TMP_DIR/agents_md_check.log" | head -3
    fi
else
    echo "  SKIP: AGENTS.md generator not present (run pre-deploy on a clean clone)"
fi

# ── Policy Gatekeeper ─────────────────────────────────────────
echo ""
echo "[POLICY GATEKEEPER]"
if [ ${#MISSING_HEALTHCHECKS[@]} -gt 0 ]; then
    POLICY_RULES+=("no_service_without_healthcheck:violated")
else
    POLICY_RULES+=("no_service_without_healthcheck:pass")
fi

if [ ${#EXPOSED_DB_PORTS[@]} -gt 0 ]; then
    POLICY_RULES+=("no_public_db_ports:violated")
else
    POLICY_RULES+=("no_public_db_ports:pass")
fi

if [ "$IMPORT_TRUTH_PASS" != "true" ]; then
    POLICY_RULES+=("no_deploy_without_import_truth:violated")
else
    POLICY_RULES+=("no_deploy_without_import_truth:pass")
fi

if [ ${#LATEST_IMAGES[@]} -gt 0 ]; then
    POLICY_RULES+=("no_latest_tag_in_production:violated")
else
    POLICY_RULES+=("no_latest_tag_in_production:pass")
fi

if [ ${#MOUNTED_SERVICES[@]} -gt 0 ]; then
    POLICY_RULES+=("no_live_mount_in_production:violated")
else
    POLICY_RULES+=("no_live_mount_in_production:pass")
fi

for pr in "${POLICY_RULES[@]}"; do
    echo "  $pr"
done

# ── Final verdict ─────────────────────────────────────────────
echo ""
echo "=== PREDEPLOY AUDIT VERDICT ==="
echo "status:      $STATUS"
echo "risk:        $RISK"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')
POLICY_JSON=$(printf '%s\n' "${POLICY_RULES[@]}" | jq -R '. | split(":") | {rule:.[0],status:.[1]}' | jq -s . 2>/dev/null || echo '[]')

cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "predeploy_audit",
  "status": "$STATUS",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "compose_valid": $COMPOSE_VALID,
    "healthcheck_pass": $HEALTHCHECK_PASS,
    "missing_healthchecks": $(echo "${MISSING_HEALTHCHECKS[*]}" | jq -R 'split(" ") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "public_port_pass": $PUBLIC_PORT_PASS,
    "exposed_db_ports": $(echo "${EXPOSED_DB_PORTS[*]}" | jq -R 'split(" ") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "image_tag_pass": $IMAGE_TAG_PASS,
    "latest_images": $(echo "${LATEST_IMAGES[*]}" | jq -R 'split(" ") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "no_digest_images": $(echo "${NO_DIGEST_IMAGES[*]}" | jq -R 'split(" ") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "drift_pass": $DRIFT_PASS,
    "live_mounts": $(echo "${MOUNTED_SERVICES[*]}" | jq -R 'split(" ") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "import_truth_pass": $IMPORT_TRUTH_PASS,
    "caddy_pass": $CADDY_PASS,
    "registry_pass": $REGISTRY_PASS,
    "git_commit": "$GIT_COMMIT",
    "git_branch": "$GIT_BRANCH",
    "tool_registry_hash": "$TOOL_REGISTRY_HASH",
    "constitutional_map_hash": "$CONSTITUTIONAL_MAP_HASH",
    "schema_hash": "$SCHEMA_HASH",
    "policy_rules": $POLICY_JSON
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$STATUS" = "FAIL" ]; then echo '"fix_compose_before_deploy"'; elif [ "$STATUS" = "HOLD" ]; then echo '"resolve_audit_findings_before_deploy"'; else echo '"proceed_to_deploy_arifosmcp"'; fi),
  "requires_arif": $(if [ "$STATUS" != "PASS" ]; then echo 'true'; else echo 'false'; fi)
}
EOF

echo ""
echo "evidence:    $EVIDENCE_FILE"
echo "=== END PREDEPLOY AUDIT ==="

[ "$STATUS" != "FAIL" ]
