#!/bin/bash
# import_truth.sh — Python package resolution audit for arifOS
# Skill: import_truth_guard
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/import_truth_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

CONTAINER_NAME="${CONTAINER_NAME:-arifosmcp}"
ARIFOS_IMAGE="${ARIFOS_IMAGE:-}"

STATUS="PASS"
REASONS=()
RISK="LOW"
LOCAL_PASS=true
CONTAINER_PASS=true
IMAGE_PASS=true
RUNTIME_DRIFT=false

echo "=== IMPORT TRUTH ==="
echo "arifOS dir: ${ARIFOS_DIR}"
echo ""

# ── 1. Repo root shadow check ─────────────────────────────────
ROOT_INIT="${ARIFOS_DIR}/__init__.py"
if [ -f "$ROOT_INIT" ] && [ ! -L "$ROOT_INIT" ]; then
    STATUS="HOLD"
    REASONS+=("repo_root_init_shadow:${ROOT_INIT}")
    RISK="HIGH"
    echo "[WARN] Repo-root __init__.py exists — may shadow actual package"
    LOCAL_PASS=false
else
    echo "[OK] No repo-root __init__.py shadow"
fi

# ── 2. Local import check ─────────────────────────────────────
echo ""
echo "[LOCAL] Testing Python imports..."
LOCAL_OUT="$TMP_DIR/local.json"
python3 - "$LOCAL_OUT" <<PYEOF
import sys, json, os
out_path = sys.argv[1]
sys.path.insert(0, "${ARIFOS_DIR}")
result = {"ok": False, "errors": [], "paths": {}, "pythonpath": os.environ.get("PYTHONPATH", "")}
try:
    import arifosmcp
    import arifosmcp.runtime
    import arifosmcp.runtime.server
    result["paths"]["arifosmcp"] = arifosmcp.__file__
    result["paths"]["arifosmcp.runtime"] = arifosmcp.runtime.__file__
    result["paths"]["arifosmcp.runtime.server"] = arifosmcp.runtime.server.__file__
    result["ok"] = True
except Exception as e:
    result["errors"].append(str(e))
with open(out_path, "w") as f:
    json.dump(result, f)
PYEOF

LOCAL_RESULT=$(cat "$LOCAL_OUT")
LOCAL_OK=$(echo "$LOCAL_RESULT" | jq -r '.ok')
LOCAL_ARIFOSMCP=$(echo "$LOCAL_RESULT" | jq -r '.paths.arifosmcp // "MISSING"')
LOCAL_RUNTIME=$(echo "$LOCAL_RESULT" | jq -r '.paths["arifosmcp.runtime"] // "MISSING"')
LOCAL_PYTHONPATH=$(echo "$LOCAL_RESULT" | jq -r '.pythonpath // ""')

echo "  arifosmcp:        $LOCAL_ARIFOSMCP"
echo "  arifosmcp.runtime: $LOCAL_RUNTIME"
echo "  PYTHONPATH:       $LOCAL_PYTHONPATH"

if [ "$LOCAL_OK" != "true" ]; then
    LOCAL_PASS=false
    STATUS="FAIL"
    REASONS+=("local_import_failed")
    RISK="CRITICAL"
    echo "  [FAIL] local import failed"
elif [ "$LOCAL_ARIFOSMCP" != "MISSING" ]; then
    if [[ "$LOCAL_ARIFOSMCP" != *"/arifosmcp/__init__.py" ]]; then
        LOCAL_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("local_arifosmcp_not_from_package:$LOCAL_ARIFOSMCP")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
        echo "  [HOLD] arifosmcp not imported from package path"
    else
        echo "  [OK] local import path correct"
    fi
else
    LOCAL_PASS=false
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("local_arifosmcp_missing")
    [ "$RISK" = "LOW" ] && RISK="HIGH"
fi

# ── 3. Container import check ─────────────────────────────────
echo ""
echo "[CONTAINER] Testing imports inside $CONTAINER_NAME..."
if docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    CONTAINER_OUT="$TMP_DIR/container.json"
    docker exec "$CONTAINER_NAME" python3 - /dev/stdout <<'PYEOF' > /dev/null 2>&1
import sys, json, os
out_path = sys.argv[1]
result = {"ok": False, "errors": [], "paths": {}, "pythonpath": os.environ.get("PYTHONPATH", "")}
try:
    import arifosmcp
    import arifosmcp.runtime
    import arifosmcp.runtime.server
    result["paths"]["arifosmcp"] = arifosmcp.__file__
    result["paths"]["arifosmcp.runtime"] = arifosmcp.runtime.__file__
    result["paths"]["arifosmcp.runtime.server"] = arifosmcp.runtime.server.__file__
    result["ok"] = True
except Exception as e:
    result["errors"].append(str(e))
with open(out_path, "w") as f:
    json.dump(result, f)
PYEOF
    docker cp "$CONTAINER_NAME:/dev/stdout" "$CONTAINER_OUT" 2>/dev/null || true
    # Actually, /dev/stdout won't work well across docker exec. Use a temp file inside container.
    # Let me redo this properly: write to a known temp path inside container and docker cp it out.
    :
fi

# Redo container check properly
if docker inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    CONTAINER_OUT="$TMP_DIR/container.json"
    TMP_IN_CONTAINER="/tmp/import_truth_$$.json"
    docker exec "$CONTAINER_NAME" python3 - "$TMP_IN_CONTAINER" <<'PYEOF'
import sys, json, os
out_path = sys.argv[1]
result = {"ok": False, "errors": [], "paths": {}, "pythonpath": os.environ.get("PYTHONPATH", "")}
try:
    import arifosmcp
    import arifosmcp.runtime
    import arifosmcp.runtime.server
    result["paths"]["arifosmcp"] = arifosmcp.__file__
    result["paths"]["arifosmcp.runtime"] = arifosmcp.runtime.__file__
    result["paths"]["arifosmcp.runtime.server"] = arifosmcp.runtime.server.__file__
    result["ok"] = True
except Exception as e:
    result["errors"].append(str(e))
with open(out_path, "w") as f:
    json.dump(result, f)
PYEOF
    docker cp "$CONTAINER_NAME:$TMP_IN_CONTAINER" "$CONTAINER_OUT" 2>/dev/null || true
    docker exec "$CONTAINER_NAME" rm -f "$TMP_IN_CONTAINER" 2>/dev/null || true

    CONTAINER_RESULT=$(cat "$CONTAINER_OUT" 2>/dev/null || echo '{"ok":false}')
    CONTAINER_OK=$(echo "$CONTAINER_RESULT" | jq -r '.ok')
    CONTAINER_ARIFOSMCP=$(echo "$CONTAINER_RESULT" | jq -r '.paths.arifosmcp // "MISSING"')
    CONTAINER_RUNTIME=$(echo "$CONTAINER_RESULT" | jq -r '.paths["arifosmcp.runtime"] // "MISSING"')
    CONTAINER_PYTHONPATH=$(echo "$CONTAINER_RESULT" | jq -r '.pythonpath // ""')

    echo "  arifosmcp:        $CONTAINER_ARIFOSMCP"
    echo "  arifosmcp.runtime: $CONTAINER_RUNTIME"
    echo "  PYTHONPATH:       $CONTAINER_PYTHONPATH"

    if [ "$CONTAINER_OK" != "true" ]; then
        CONTAINER_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("container_import_failed")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
        echo "  [FAIL] container import failed"
    elif [ "$CONTAINER_ARIFOSMCP" != "MISSING" ]; then
        if [[ "$CONTAINER_ARIFOSMCP" != "/app/arifosmcp/__init__.py" ]]; then
            CONTAINER_PASS=false
            [ "$STATUS" = "PASS" ] && STATUS="HOLD"
            REASONS+=("container_arifosmcp_wrong_path:$CONTAINER_ARIFOSMCP")
            [ "$RISK" = "LOW" ] && RISK="HIGH"
            echo "  [HOLD] container arifosmcp path wrong: $CONTAINER_ARIFOSMCP"
        else
            echo "  [OK] container import path correct"
        fi
    fi

    if [ "$CONTAINER_PYTHONPATH" != "/app" ]; then
        CONTAINER_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("container_pythonpath_not_app:$CONTAINER_PYTHONPATH")
        [ "$RISK" = "LOW" ] && RISK="MEDIUM"
        echo "  [HOLD] PYTHONPATH is not /app: $CONTAINER_PYTHONPATH"
    fi

    if docker exec "$CONTAINER_NAME" test -f /app/__init__.py 2>/dev/null; then
        CONTAINER_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("container_repo_root_init_py_present")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
        echo "  [WARN] /app/__init__.py exists in container"
    fi
else
    echo "  [SKIP] Container $CONTAINER_NAME not running"
    CONTAINER_PASS=false
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("container_not_running:$CONTAINER_NAME")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
fi

# ── 4. Image import check (if ARIFOS_IMAGE set) ───────────────
if [ -n "$ARIFOS_IMAGE" ]; then
    echo ""
    echo "[IMAGE] Testing imports in $ARIFOS_IMAGE..."
    IMAGE_OUT="$TMP_DIR/image.json"
    docker run --rm -v "$TMP_DIR:/hosttmp" --entrypoint python3 "$ARIFOS_IMAGE" - /hosttmp/image.json <<'PYEOF'
import sys, json, os
out_path = sys.argv[1]
result = {"ok": False, "errors": [], "paths": {}, "pythonpath": os.environ.get("PYTHONPATH", "")}
try:
    import arifosmcp
    import arifosmcp.runtime
    import arifosmcp.runtime.server
    result["paths"]["arifosmcp"] = arifosmcp.__file__
    result["paths"]["arifosmcp.runtime"] = arifosmcp.runtime.__file__
    result["paths"]["arifosmcp.runtime.server"] = arifosmcp.runtime.server.__file__
    result["ok"] = True
except Exception as e:
    result["errors"].append(str(e))
with open(out_path, "w") as f:
    json.dump(result, f)
PYEOF

    IMAGE_RESULT=$(cat "$IMAGE_OUT" 2>/dev/null || echo '{"ok":false}')
    IMAGE_OK=$(echo "$IMAGE_RESULT" | jq -r '.ok')
    IMAGE_ARIFOSMCP=$(echo "$IMAGE_RESULT" | jq -r '.paths.arifosmcp // "MISSING"')
    IMAGE_PYTHONPATH=$(echo "$IMAGE_RESULT" | jq -r '.pythonpath // ""')

    echo "  arifosmcp:  $IMAGE_ARIFOSMCP"
    echo "  PYTHONPATH: $IMAGE_PYTHONPATH"

    if [ "$IMAGE_OK" != "true" ]; then
        IMAGE_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("image_import_failed:$ARIFOS_IMAGE")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
    elif [ "$IMAGE_ARIFOSMCP" != "/app/arifosmcp/__init__.py" ]; then
        IMAGE_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("image_arifosmcp_wrong_path:$IMAGE_ARIFOSMCP")
        [ "$RISK" = "LOW" ] && RISK="HIGH"
    fi

    if [ "$IMAGE_PYTHONPATH" != "/app" ]; then
        IMAGE_PASS=false
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("image_pythonpath_not_app:$IMAGE_PYTHONPATH")
        [ "$RISK" = "LOW" ] && RISK="MEDIUM"
    fi
else
    echo ""
    echo "[IMAGE] ARIFOS_IMAGE not set — skipping"
fi

# ── 5. Runtime drift detection ────────────────────────────────
if [ "$LOCAL_PASS" = "true" ] && [ "$CONTAINER_PASS" = "true" ]; then
    if [ "$LOCAL_ARIFOSMCP" != "$CONTAINER_ARIFOSMCP" ]; then
        RUNTIME_DRIFT=true
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("runtime_drift_detected:local!=container")
        [ "$RISK" = "LOW" ] && RISK="MEDIUM"
        echo ""
        echo "[DRIFT] Local and container paths differ"
    fi
fi

# ── Report ────────────────────────────────────────────────────
echo ""
echo "=== IMPORT TRUTH VERDICT ==="
echo "status:      $STATUS"
echo "risk:        $RISK"
echo "local:       $LOCAL_PASS"
echo "container:   $CONTAINER_PASS"
echo "image:       $IMAGE_PASS"
echo "drift:       $RUNTIME_DRIFT"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')

cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "import_truth_guard",
  "status": "$STATUS",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "local": $(cat "$TMP_DIR/local.json" 2>/dev/null || echo '{"ok":false}'),
    "container": $(cat "$TMP_DIR/container.json" 2>/dev/null || echo '{"ok":false,"note":"skipped"}'),
    "image": $(cat "$TMP_DIR/image.json" 2>/dev/null || echo '{"ok":false,"note":"skipped"}'),
    "runtime_drift": $RUNTIME_DRIFT,
    "repo_root_init_py_present": $(if [ -f "$ARIFOS_DIR/__init__.py" ]; then echo 'true'; else echo 'false'; fi)
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$STATUS" = "FAIL" ]; then echo '"fix_import_paths_before_any_deploy"'; elif [ "$STATUS" = "HOLD" ]; then echo '"resolve_drift_and_shadowing_before_deploy"'; else echo '"proceed_to_predeploy_audit"'; fi),
  "requires_arif": $(if [ "$STATUS" != "PASS" ]; then echo 'true'; else echo 'false'; fi)
}
EOF

echo ""
echo "evidence:    $EVIDENCE_FILE"
echo "=== END IMPORT TRUTH ==="

[ "$STATUS" != "FAIL" ]
