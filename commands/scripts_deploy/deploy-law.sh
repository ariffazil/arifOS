#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# deploy-law.sh — arifOS Federation Deploy Constitution Enforcer
# F1–F13 governed. Must be sourced, not executed directly.
#
# Usage:
#   source /root/scripts/deploy-law.sh
#   deploy_enforce "arifOS" "/root/arifOS" "arifosmcp" 8080
#
# DITEMPA BUKAN DIBERI — Forged, Not Given
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

DEPLOY_LAW_VERSION="2026.05.12"

deploy_enforce() {
    local ORG_NAME="$1"       # e.g. "arifOS"
    local REPO_PATH="$2"      # e.g. "/root/arifOS"
    local COMPOSE_SERVICE="$3" # e.g. "arifosmcp"
    local HEALTH_PORT="${4:-8080}"

    echo "═══ DEPLOY LAW ENFORCEMENT [${ORG_NAME}] ═══"

    # ── Step 1: Git sanity ────────────────────────────────────────────
    cd "$REPO_PATH"

    local LOCAL_HASH
    LOCAL_HASH=$(git rev-parse --short=7 HEAD 2>/dev/null)
    echo "  local HEAD:  ${LOCAL_HASH}"

    git fetch origin main 2>/dev/null || true

    local REMOTE_HASH
    REMOTE_HASH=$(git rev-parse --short=7 origin/main 2>/dev/null)
    echo "  origin/main: ${REMOTE_HASH}"

    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        echo "  ❌ F1 AMANAH BREACH: local HEAD ≠ origin/main"
        echo "     Push or rebase before deploying."
        echo "     git push origin main"
        return 1
    fi
    echo "  ✅ F1: local matches origin/main"

    # ── Step 2: Check that image tag matches commit ───────────────────
    local COMPOSE_TAG
    COMPOSE_TAG=$(grep -A1 "image: ghcr.io/ariffazil/${ORG_NAME,,}" /root/compose/docker-compose.yml 2>/dev/null | grep -oP ':\K[a-f0-9]{7}' | head -1)
    if [ -n "$COMPOSE_TAG" ] && [ "$COMPOSE_TAG" != "$LOCAL_HASH" ]; then
        echo "  ⚠️  Compose tag (${COMPOSE_TAG}) ≠ commit (${LOCAL_HASH})"
        echo "     The running compose references a different commit."
        echo "     Run: make deploy-local  (from repo root)"
        echo "     This will rebuild with the correct SHA."
    fi

    # ── Step 3: Health check ──────────────────────────────────────────
    local HEALTH_SHA
    HEALTH_SHA=$(curl -fsS "http://localhost:${HEALTH_PORT}/health" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('git_commit',''))" 2>/dev/null || echo "")
    if [ -n "$HEALTH_SHA" ]; then
        if [ "${HEALTH_SHA:0:7}" != "$LOCAL_HASH" ]; then
            echo "  ❌ F3 WITNESS BREACH: running container SHA ≠ local HEAD"
            echo "     Container: ${HEALTH_SHA}"
            echo "     Expected:  ${LOCAL_HASH}"
            return 1
        fi
        echo "  ✅ F3: container SHA matches"
    else
        echo "  ⚠️  Health endpoint unreachable on port ${HEALTH_PORT}"
    fi

    echo "═══ DEPLOY LAW: PASS [${ORG_NAME}] ═══"
    return 0
}

deploy_reconcile() {
    local ORG_NAME="$1"
    local REPO_PATH="$2"

    echo "═══ RECONCILING [${ORG_NAME}] deploy manifest ═══"
    cd "$REPO_PATH"

    local LOCAL_HASH
    LOCAL_HASH=$(git rev-parse --short=7 HEAD)

    # Update the canonical deploy compose with the current commit tag
    if [ -f "deploy/docker-compose.yml" ]; then
        sed -i "s|image: ghcr.io/ariffazil/${ORG_NAME,,}:[a-f0-9]*|image: ghcr.io/ariffazil/${ORG_NAME,,}:${LOCAL_HASH}|g" deploy/docker-compose.yml
        echo "  Updated deploy/docker-compose.yml → ${LOCAL_HASH}"
        git add deploy/docker-compose.yml
        git commit -m "chore: reconcile deploy tag to ${LOCAL_HASH}" || true
        git push origin main
        echo "  ✅ Pushed to origin/main"
    else
        echo "  ⚠️  No deploy/docker-compose.yml found"
    fi

    # Update the runtime compose
    if [ -f "/root/compose/docker-compose.yml" ]; then
        sed -i "s|image: ghcr.io/ariffazil/${ORG_NAME,,}:[a-f0-9]*|image: ghcr.io/ariffazil/${ORG_NAME,,}:${LOCAL_HASH}|g" /root/compose/docker-compose.yml
        echo "  Updated /root/compose/docker-compose.yml → ${LOCAL_HASH}"
    fi

    echo "═══ RECONCILE DONE [${ORG_NAME}] ═══"
}

deploy_audit_all() {
    echo "═══════════════════════════════════════════════════════"
    echo "  FEDERATION DEPLOY AUDIT — $(date -u)"
    echo "═══════════════════════════════════════════════════════"

    deploy_enforce "arifOS" "/root/arifOS" "arifosmcp" 8080 || echo "  ⚠️  arifOS needs attention"
    deploy_enforce "geox" "/root/geox" "geox" 8081 || echo "  ⚠️  geox needs attention"
    deploy_enforce "wealth" "/root/WEALTH" "wealth-organ" 8082 || echo "  ⚠️  wealth needs attention"
    deploy_enforce "well" "/root/WELL" "well" 8083 || echo "  ⚠️  well needs attention"

    echo "═══════════════════════════════════════════════════════"
    echo "  AUDIT COMPLETE"
    echo "═══════════════════════════════════════════════════════"
}

# If sourced, just define functions. If executed, run audit.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "═══ DEPLOY LAW v${DEPLOY_LAW_VERSION} ═══"
    echo "Usage: source deploy-law.sh && deploy_enforce <name> <path> <service> [port]"
    echo "       source deploy-law.sh && deploy_audit_all"
    echo ""
    deploy_audit_all
fi
