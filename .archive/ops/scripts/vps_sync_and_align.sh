#!/bin/bash
# VPS Sync and Alignment Script
# Syncs arifOS repo from GitHub and aligns skills with laptop
# 
# Run on VPS: ./scripts/vps_sync_and_align.sh

set -euo pipefail

REPO_URL="https://github.com/ariffazil/arifosmcp.git"
VPS_ARIFOS_DIR="/root/arifOS"
GLOBAL_SKILLS_DIR="/root/.config/agents/skills"
PROJECT_SKILLS_DIR="${VPS_ARIFOS_DIR}/.kimi/skills"

echo "=========================================="
echo "arifOS VPS Sync & Alignment"
echo "DITEMPA BUKAN DIBERI"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_err() { echo -e "${RED}[ERR]${NC} $1"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Step 1: Sync repository
echo ""
log_info "Step 1: Syncing repository from GitHub..."

if [ -d "${VPS_ARIFOS_DIR}/.git" ]; then
    cd "${VPS_ARIFOS_DIR}"
    git fetch origin
    git pull origin main
    log_ok "Repository pulled successfully"
else
    log_err "Repository not found at ${VPS_ARIFOS_DIR}"
    exit 1
fi

# Step 2: Check current commit
echo ""
log_info "Step 2: Verifying sync..."
cd "${VPS_ARIFOS_DIR}"
LOCAL_SHA=$(git rev-parse --short HEAD)
REMOTE_SHA=$(git rev-parse --short origin/main)

if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
    log_ok "Repository synced at commit: ${LOCAL_SHA}"
else
    log_warn "Repository not fully synced"
    log_info "Local: ${LOCAL_SHA}, Remote: ${REMOTE_SHA}"
fi

# Step 3: Align skills
echo ""
log_info "Step 3: Aligning skills..."

# Create global skills directory if not exists
mkdir -p "${GLOBAL_SKILLS_DIR}"

# Copy project skills to global directory
if [ -d "${PROJECT_SKILLS_DIR}" ]; then
    for skill in "${PROJECT_SKILLS_DIR}"/*/; do
        skill_name=$(basename "$skill")
        if [ -d "${skill}" ]; then
            cp -r "${skill}" "${GLOBAL_SKILLS_DIR}/"
            log_ok "Synced skill: ${skill_name}"
        fi
    done
else
    log_warn "Project skills directory not found: ${PROJECT_SKILLS_DIR}"
fi

# Step 4: Verify alignment
echo ""
log_info "Step 4: Verification..."

echo ""
echo "Project Skills (in repo):"
ls -1 "${PROJECT_SKILLS_DIR}" 2>/dev/null || echo "  (none)"

echo ""
echo "Global Skills (in ~/.config/agents/skills):"
ls -1 "${GLOBAL_SKILLS_DIR}" 2>/dev/null || echo "  (none)"

# Step 5: System health check
echo ""
log_info "Step 5: System health check..."

# Check Docker containers
if command -v docker &> /dev/null; then
    echo ""
    echo "Docker containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || log_warn "Docker not running"
fi

# Check arifOS services
if systemctl is-active --quiet arifos-aaa-mcp 2>/dev/null; then
    log_ok "arifOS MCP service: RUNNING"
else
    log_warn "arifOS MCP service: NOT RUNNING (may use Docker)"
fi

# Step 6: Summary
echo ""
echo "=========================================="
log_ok "VPS Sync & Alignment Complete!"
echo "=========================================="
echo ""
echo "Repository: ${VPS_ARIFOS_DIR}"
echo "Commit: $(git rev-parse --short HEAD)"
echo "Branch: $(git branch --show-current)"
echo ""
echo "Skills synced to: ${GLOBAL_SKILLS_DIR}"
echo "Total skills: $(ls -1 ${GLOBAL_SKILLS_DIR} 2>/dev/null | wc -l)"
echo ""
echo "Next steps:"
echo "  1. Restart services if needed: docker compose restart"
echo "  2. Verify MCP connection: curl http://localhost:8080/health"
echo "  3. Check skills: ls ~/.config/agents/skills/"
echo ""
echo "DITEMPA BUKAN DIBERI"
