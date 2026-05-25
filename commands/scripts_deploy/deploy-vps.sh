#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# arifOS Autonomous VPS Deploy — Constitutional kernel deployment
#
# Purpose: Build, push, and deploy arifOS image. The kernel must never drift.
#
# Flow:
#   1. Get current commit SHA
#   2. Check if ghcr.io/ariffazil/arifos:<sha> already exists
#   3. If missing → build locally → push to GHCR
#   4. Update /root/compose/docker-compose.yml image pin
#   5. Restart container
#   6. Verify health + constitutional readiness
#
# Usage:
#   ./scripts/deploy-vps.sh           # full deploy
#   ./scripts/deploy-vps.sh --check   # only check if image exists
#
# DITEMPA BUKAN DIBERI — Forged, Not Given
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

REPO_NAME="arifos"
IMAGE_BASE="ghcr.io/ariffazil/arifos"
COMPOSE_FILE="/root/compose/docker-compose.yml"
CONTAINER_NAME="arifosmcp"
COMPOSE_SERVICE="arifosmcp"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ── 1. Get current commit SHA ────────────────────────────────────────────────
SHORT_SHA=$(git rev-parse --short HEAD)
FULL_SHA=$(git rev-parse HEAD)
log_info "Deploying arifOS commit: $SHORT_SHA"

# ── 2. Check if image already exists on GHCR ─────────────────────────────────
log_info "Checking GHCR for image: $IMAGE_BASE:$SHORT_SHA"
if docker manifest inspect "$IMAGE_BASE:$SHORT_SHA" >/dev/null 2>&1; then
    log_info "Image already exists on GHCR — skipping build"
    NEED_BUILD=false
else
    log_warn "Image not found on GHCR — local build required"
    NEED_BUILD=true
fi

# ── --check mode: exit after check ───────────────────────────────────────────
if [[ "${1:-}" == "--check" ]]; then
    if $NEED_BUILD; then
        log_warn "Image missing — run without --check to build and deploy"
        exit 1
    else
        log_info "Image present — no action needed"
        exit 0
    fi
fi

# ── 3. Build and push if needed ──────────────────────────────────────────────
if $NEED_BUILD; then
    log_info "Building arifOS image locally..."
    docker build -t "$IMAGE_BASE:$SHORT_SHA" -t "$IMAGE_BASE:latest" .

    # Ensure GHCR login (uses gh CLI token if available)
    if command -v yq >/dev/null 2>&1 && [[ -f ~/.config/gh/hosts.yml ]]; then
        GH_TOKEN=$(yq '.["github.com"].oauth_token' ~/.config/gh/hosts.yml)
        echo "$GH_TOKEN" | docker login ghcr.io -u ariffazil --password-stdin
    elif [[ -n "${GITHUB_TOKEN:-}" ]]; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u ariffazil --password-stdin
    else
        log_error "No GHCR credentials found. Run: gh auth login"
        exit 1
    fi

    log_info "Pushing to GHCR..."
    docker push "$IMAGE_BASE:$SHORT_SHA"
    docker push "$IMAGE_BASE:latest"
    log_info "Push complete"
fi

# ── 4. Update compose pin ────────────────────────────────────────────────────
if [[ -f "$COMPOSE_FILE" ]]; then
    CURRENT_PIN=$(grep -E "^\s+image:\s+$IMAGE_BASE:" "$COMPOSE_FILE" | awk '{print $2}' || true)
    NEW_PIN="$IMAGE_BASE:$SHORT_SHA"

    if [[ "$CURRENT_PIN" != "$NEW_PIN" ]]; then
        log_info "Updating compose pin: $CURRENT_PIN → $NEW_PIN"
        sed -i "s|image: $IMAGE_BASE:[a-z0-9]*|image: $NEW_PIN|" "$COMPOSE_FILE"
    else
        log_info "Compose pin already correct"
    fi
else
    log_warn "Compose file not found at $COMPOSE_FILE"
fi

# ── 5. Restart container ─────────────────────────────────────────────────────
log_info "Restarting $CONTAINER_NAME container..."
cd /root/compose

# Stop and remove old container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
fi

docker compose up -d --no-deps "$COMPOSE_SERVICE"

# ── 6. Health check ──────────────────────────────────────────────────────────
# NOTE: localhost:8080 is the Docker Compose mapped port.
# The live VPS systemd service runs on port 8088.
log_info "Waiting for health check..."
for i in {1..30}; do
    if curl -sf http://localhost:8080/health \
        -H "Content-Type: application/json" >/dev/null 2>&1; then
        log_info "arifOS is healthy and responding on port 8080"
        break
    fi
    if [[ $i -eq 30 ]]; then
        log_error "arifOS failed health check after 30 seconds"
        exit 1
    fi
    sleep 1
done

# ── 7. Verify constitutional readiness ───────────────────────────────────────
log_info "Verifying constitutional readiness..."
TOOLS=$(curl -sf http://localhost:8080/mcp \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('result',{}).get('tools',[]))))")

if [[ "$TOOLS" -ge 13 ]]; then
    log_info "✅ Constitutional readiness confirmed — $TOOLS tools available"
else
    log_warn "⚠️  Only $TOOLS tools available (expected ≥13)"
fi

log_info "═══════════════════════════════════════════════════════════════════════════════"
log_info "arifOS deploy complete: $SHORT_SHA"
log_info "Image: $IMAGE_BASE:$SHORT_SHA"
log_info "═══════════════════════════════════════════════════════════════════════════════"
