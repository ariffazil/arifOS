#!/bin/bash
# federation-manager.sh — arifOS Federation Unified Dependency Manager
# Single command: install, update, test, health-check all 4 Python organs.
#
# Usage:
#   ./federation-manager.sh install    # Install all deps
#   ./federation-manager.sh update     # Update all deps to latest
#   ./federation-manager.sh test       # Run all test suites
#   ./federation-manager.sh health     # Health check all organs
#   ./federation-manager.sh status     # Show version/dependency status
#
# DITEMPA BUKAN DIBERI — Forged, Not Given

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FEDERATION_ROOT="/root"

# Color
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[FEDERATION]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }

# ─── System Dependencies (OS-level, globally available) ──────────────────
install_system_deps() {
    log "Installing system-level dependencies..."
    local pkgs=(
        gdal-bin libgdal-dev
        libgeos-dev proj-bin libproj-dev
        libspatialindex-dev
        build-essential python3-dev
        libpq-dev
        libblas-dev liblapack-dev
    )

    for pkg in "${pkgs[@]}"; do
        if dpkg -l "$pkg" &>/dev/null; then
            info "  $pkg — already installed"
        else
            info "  $pkg — installing..."
            apt install -y "$pkg" 2>&1 | tail -1
        fi
    done
    log "System dependencies complete."
}

# ─── Per-Organ Operations ────────────────────────────────────────────────

arifos_install() {
    log "arifOS: syncing dependencies..."
    cd /root/arifOS
    uv sync --frozen 2>&1 | tail -3
    log "arifOS: done."
}

arifos_update() {
    log "arifOS: upgrading to latest..."
    cd /root/arifOS
    uv sync --upgrade 2>&1 | tail -3
    log "arifOS: updated."
}

arifos_test() {
    log "arifOS: running tests..."
    cd /root/arifOS
    uv run pytest tests/ -q --tb=short -m "not e2e and not slow" 2>&1 | tail -5
}

geox_install() {
    log "GEOX: syncing dependencies..."
    cd /root/geox
    uv sync --frozen 2>&1 | tail -3
    log "GEOX: done."
}

geox_update() {
    log "GEOX: upgrading to latest..."
    cd /root/geox
    uv sync --upgrade 2>&1 | tail -3
    log "GEOX: updated."
}

geox_test() {
    log "GEOX: running tests..."
    cd /root/geox
    PYTHONPATH=src uv run pytest tests/ -q --tb=short 2>&1 | tail -5
}

wealth_install() {
    log "WEALTH: syncing dependencies..."
    cd /root/WEALTH
    uv sync --frozen 2>&1 | tail -3
    log "WEALTH: done."
}

wealth_update() {
    log "WEALTH: upgrading to latest..."
    cd /root/WEALTH
    uv sync --upgrade 2>&1 | tail -3
    log "WEALTH: updated."
}

wealth_test() {
    log "WEALTH: running tests..."
    cd /root/WEALTH
    uv run pytest tests/ -q --tb=short 2>&1 | tail -5
}

well_install() {
    log "WELL: syncing dependencies..."
    cd /root/WELL
    uv sync --frozen 2>&1 | tail -3
    log "WELL: done."
}

well_update() {
    log "WELL: upgrading to latest..."
    cd /root/WELL
    uv sync --upgrade 2>&1 | tail -3
    log "WELL: updated."
}

well_test() {
    log "WELL: running tests..."
    cd /root/WELL
    uv run pytest tests/ -q --tb=short 2>&1 | tail -5
}

# ─── Federation Health ───────────────────────────────────────────────────
federation_health() {
    log "Federation health probe..."
    echo ""

    # arifOS
    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8088/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}arifOS${NC}  :8088  ✓ ($status)"
    else
        echo -e "  ${RED}arifOS${NC}  :8088  ✗ ($status)"
    fi

    # A-FORGE
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7071/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}A-FORGE${NC} :7071  ✓ ($status)"
    else
        echo -e "  ${RED}A-FORGE${NC} :7071  ✗ ($status)"
    fi

    # GEOX
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}GEOX${NC}   :8081  ✓ ($status)"
    else
        echo -e "  ${RED}GEOX${NC}   :8081  ✗ ($status)"
    fi

    # WEALTH
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18082/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}WEALTH${NC} :18082 ✓ ($status)"
    else
        echo -e "  ${RED}WEALTH${NC} :18082 ✗ ($status)"
    fi

    # WELL
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:18083/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}WELL${NC}   :18083 ✓ ($status)"
    else
        echo -e "  ${RED}WELL${NC}   :18083 ✗ ($status)"
    fi

    # AAA
    status=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/health 2>/dev/null || echo "down")
    if [ "$status" = "200" ]; then
        echo -e "  ${GREEN}AAA${NC}    :3001  ✓ ($status)"
    else
        echo -e "  ${YELLOW}AAA${NC}    :3001  ~ ($status)"
    fi

    echo ""
    log "Health probe complete."
}

federation_status() {
    log "Federation dependency status..."
    echo ""
    for org in arifOS geox WEALTH WELL; do
        local name ver
        name=$(cd /root/$org && grep '^name = ' pyproject.toml 2>/dev/null | head -1 | cut -d'"' -f2)
        ver=$(cd /root/$org && grep '^version = ' pyproject.toml 2>/dev/null | head -1 | cut -d'"' -f2)
        local count
        count=$(cd /root/$org && grep -c '^\s*"' pyproject.toml 2>/dev/null || echo "?")
        echo -e "  ${CYAN}$org${NC}  →  $name v$ver  ($count deps)"
    done
    echo ""
    echo "  Unified requirements: /root/requirements-federation.txt"
    echo "  Manager: $(basename "$0")"
    echo "  System deps: gdal $(gdal-config --version 2>/dev/null || echo '?')"
}

# ─── Main ─────────────────────────────────────────────────────────────────
case "${1:-help}" in
    install)
        log "═══ Federation Install ═══"
        install_system_deps
        arifos_install
        geox_install
        wealth_install
        well_install
        federation_health
        log "═══ Install complete ═══"
        ;;
    update)
        log "═══ Federation Update ═══"
        install_system_deps
        arifos_update
        geox_update
        wealth_update
        well_update
        federation_health
        log "═══ Update complete ═══"
        ;;
    test)
        log "═══ Federation Test ═══"
        arifos_test
        geox_test
        wealth_test
        well_test
        log "═══ Tests complete ═══"
        ;;
    health)
        federation_health
        ;;
    status)
        federation_status
        ;;
    system-deps)
        install_system_deps
        ;;
    *)
        echo "arifOS Federation Manager"
        echo ""
        echo "Usage: $0 {install|update|test|health|status|system-deps}"
        echo ""
        echo "  install      Install all dependencies (system + Python)"
        echo "  update       Update all dependencies to latest"
        echo "  test         Run test suites for all organs"
        echo "  health       Health check all federation services"
        echo "  status       Show version and dependency status"
        echo "  system-deps  Install OS-level system dependencies only"
        echo ""
        echo "Single command for the entire federation."
        echo "DITEMPA BUKAN DIBERI — Forged, Not Given"
        ;;
esac
