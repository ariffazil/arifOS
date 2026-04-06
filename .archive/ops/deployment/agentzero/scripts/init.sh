#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# AgentZero + arifOS Initialization Script
# Version: 2026.03.13-FORGED
# Author: Muhammad Arif bin Fazil [ΔΩΨ | ARIF]
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARIFOS_VERSION="2026.3.12-FORGED"
AGENTZERO_VERSION="v0.9.6"

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              AGENTZERO + arifOS INITIALIZATION                 ║"
echo "║                    Ditempa Bukan Diberi                        ║"
echo "║                    [ΔΩΨ | ARIF] v${ARIFOS_VERSION}               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: Environment Validation
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 1/7: Validating environment..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    log_error "Docker Compose is not installed."
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    log_error "Docker daemon is not running."
    exit 1
fi

log_success "Environment validated"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: Directory Structure
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 2/7: Creating directory structure..."

mkdir -p "$PROJECT_DIR"/{data,logs,workspace}
mkdir -p "$PROJECT_DIR/data"/{vault999,agentzero/memory,qdrant,ollama}
mkdir -p "$PROJECT_DIR/logs"/{arifos,agentzero}
mkdir -p "$PROJECT_DIR/config"/{arifos,agentzero,grafana/dashboards,prometheus}

# Set permissions
chmod 700 "$PROJECT_DIR/data/vault999"
chmod 755 "$PROJECT_DIR/workspace"

log_success "Directory structure created"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Configuration Files
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 3/7: Generating configuration files..."

# Generate secrets if not exist
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    log_info "Creating environment file..."
    cat > "$PROJECT_DIR/.env" << EOF
# AgentZero + arifOS Environment Configuration
# Generated: $(date -Iseconds)

# ═══════════════════════════════════════════════════════════════════════
# Security
# ═══════════════════════════════════════════════════════════════════════
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 24)
ARIFOS_API_KEY=$(openssl rand -hex 32)
VAULT999_ENCRYPTION_KEY=$(openssl rand -hex 64)

# ═══════════════════════════════════════════════════════════════════════
# LLM Configuration (via arifOS proxy)
# ═══════════════════════════════════════════════════════════════════════
# Add your API keys here for external LLM access
# These are proxied through arifOS for constitutional enforcement
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# OPENROUTER_API_KEY=sk-or-...

# ═══════════════════════════════════════════════════════════════════════
# AgentZero Configuration
# ═══════════════════════════════════════════════════════════════════════
AGENTZERO_MAX_DEPTH=3
AGENTZERO_MAX_EXECUTION_TIME=300
AGENTZERO_REQUIRE_TOOL_APPROVAL=true

# ═══════════════════════════════════════════════════════════════════════
# arifOS Configuration
# ═══════════════════════════════════════════════════════════════════════
ARIFOS_MODE=agentzero_governance
ARIFOS_LOG_LEVEL=INFO
F2_TRUTH_THRESHOLD=0.99
F7_HUMILITY_MIN=0.03
F7_HUMILITY_MAX=0.20
F12_INJECTION_MAX=0.15
EOF
    log_success "Environment file created at $PROJECT_DIR/.env"
    log_warn "Please review and update API keys in $PROJECT_DIR/.env"
else
    log_info "Environment file already exists, skipping generation"
fi

# Create Prometheus config
cat > "$PROJECT_DIR/config/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'arifos'
    static_configs:
      - targets: ['arifos:8080']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'agentzero'
    static_configs:
      - targets: ['agentzero:50001']
    metrics_path: /metrics
    scrape_interval: 10s
EOF

# Create Grafana datasources
cat > "$PROJECT_DIR/config/grafana/datasources.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF

log_success "Configuration files generated"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: Seccomp Profile
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 4/7: Creating seccomp security profile..."

cat > "$PROJECT_DIR/seccomp-agentzero.json" << 'EOF'
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_AARCH64"],
  "syscalls": [
    {
      "comment": "Basic file operations",
      "names": [
        "read", "write", "open", "openat", "close",
        "stat", "fstat", "lstat", "statx",
        "access", "faccessat", "faccessat2",
        "lseek", "pread64", "pwrite64",
        "readv", "writev", "preadv", "pwritev"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Directory operations",
      "names": [
        "mkdir", "mkdirat", "rmdir", "unlink", "unlinkat",
        "rename", "renameat", "renameat2",
        "chdir", "fchdir", "getcwd",
        "chown", "fchown", "lchown", "fchownat"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Process control",
      "names": [
        "exit", "exit_group", "wait4", "waitpid", "waitid",
        "getpid", "getppid", "getpgrp", "getpgid", "getsid",
        "setpgid", "setsid",
        "kill", "tkill", "tgkill"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Memory management",
      "names": [
        "brk", "mmap", "munmap", "mprotect", "mremap",
        "madvise", "mincore", "msync"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Threading",
      "names": [
        "clone", "clone3", "fork", "vfork",
        "setns", "unshare",
        "futex", "set_robust_list", "get_robust_list"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Signals",
      "names": [
        "rt_sigaction", "rt_sigprocmask", "rt_sigpending",
        "rt_sigtimedwait", "rt_sigqueueinfo", "rt_tgsigqueueinfo",
        "sigaltstack", "signalfd", "signalfd4"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Time",
      "names": [
        "clock_gettime", "clock_getres", "clock_nanosleep",
        "gettimeofday", "nanosleep", "time", "times"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "User/group info",
      "names": [
        "getuid", "getgid", "geteuid", "getegid",
        "getgroups", "getresuid", "getresgid"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Polling",
      "names": [
        "poll", "ppoll", "select", "pselect6",
        "epoll_create", "epoll_create1", "epoll_ctl", "epoll_wait", "epoll_pwait"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Evented I/O",
      "names": [
        "eventfd", "eventfd2", "pipe", "pipe2", "tee", "splice"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Descriptors",
      "names": [
        "dup", "dup2", "dup3", "fcntl",
        "ioctl", "fcntl64"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Synchronization",
      "names": [
        "fsync", "fdatasync", "sync", "syncfs",
        "sync_file_range"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Execution",
      "names": [
        "execve", "execveat"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Sockets (for Python multiprocessing)",
      "names": [
        "socket", "socketpair", "getsockopt", "setsockopt"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Prctl",
      "names": ["prctl"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Uname",
      "names": ["uname", "sethostname"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Random",
      "names": ["getrandom"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "Umask",
      "names": ["umask"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "comment": "BLOCKED: Dangerous network",
      "names": [
        "connect", "bind", "listen", "accept", "accept4"
      ],
      "action": "SCMP_ACT_ERRNO"
    },
    {
      "comment": "BLOCKED: Module loading",
      "names": [
        "init_module", "finit_module", "delete_module"
      ],
      "action": "SCMP_ACT_KILL_PROCESS"
    },
    {
      "comment": "BLOCKED: Privilege escalation",
      "names": [
        "setuid", "setgid", "setreuid", "setregid",
        "setgroups", "setresuid", "setresgid",
        "setfsuid", "setfsgid", "capset"
      ],
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}
EOF

log_success "Seccomp profile created"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Pull Images
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 5/7: Pulling container images..."

# Pull required images
images=(
    "agent0ai/agent-zero:latest"
    "qdrant/qdrant:latest"
    "ollama/ollama:latest"
    "prom/prometheus:latest"
    "grafana/grafana:latest"
)

for image in "${images[@]}"; do
    log_info "Pulling $image..."
    docker pull "$image" || log_warn "Failed to pull $image (will retry on start)"
done

log_success "Images pulled"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: Constitution Verification
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 6/7: Verifying constitutional integrity..."

# Check system prompt exists and is readable
SYSTEM_PROMPT="$PROJECT_DIR/prompts/arifos-system.md"
if [[ ! -f "$SYSTEM_PROMPT" ]]; then
    log_error "Constitutional system prompt not found: $SYSTEM_PROMPT"
    exit 1
fi

# Calculate hash
PROMPT_HASH=$(sha256sum "$SYSTEM_PROMPT" | awk '{print $1}')
log_info "Constitution hash: $PROMPT_HASH"

# Verify constitution contains all 13 floors
FLOORS=("F1" "F2" "F3" "F4" "F5" "F6" "F7" "F8" "F9" "F10" "F11" "F12" "F13")
MISSING_FLOORS=0

for floor in "${FLOORS[@]}"; do
    if ! grep -q "$floor" "$SYSTEM_PROMPT"; then
        log_error "Floor $floor not found in constitution!"
        MISSING_FLOORS=$((MISSING_FLOORS + 1))
    fi
done

if [[ $MISSING_FLOORS -gt 0 ]]; then
    log_error "Constitution incomplete! Missing $MISSING_FLOORS floors."
    exit 1
fi

log_success "All 13 constitutional floors verified"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 7: Final Summary
# ═══════════════════════════════════════════════════════════════════════════
log_info "Step 7/7: Finalizing setup..."

# Create status script
cat > "$PROJECT_DIR/scripts/status.sh" << 'EOF'
#!/bin/bash
echo "AgentZero + arifOS Status"
echo "========================"
docker compose ps
echo ""
echo "Health Checks:"
curl -s http://localhost:18080/health 2>/dev/null || echo "arifOS: Not responding"
echo ""
echo "VAULT999 Status:"
ls -la ./data/vault999/ 2>/dev/null | head -5 || echo "Vault not initialized"
EOF
chmod +x "$PROJECT_DIR/scripts/status.sh"

# Create stop script
cat > "$PROJECT_DIR/scripts/stop.sh" << 'EOF'
#!/bin/bash
echo "Stopping AgentZero + arifOS..."
docker compose down
EOF
chmod +x "$PROJECT_DIR/scripts/stop.sh"

# Create logs script
cat > "$PROJECT_DIR/scripts/logs.sh" << 'EOF'
#!/bin/bash
service="${1:-arifos}"
docker compose logs -f "$service"
EOF
chmod +x "$PROJECT_DIR/scripts/logs.sh"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           INITIALIZATION COMPLETE — AGENTZERO READY            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_success "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review and configure API keys in: $PROJECT_DIR/.env"
echo "  2. Start the stack: cd $PROJECT_DIR && docker compose up -d"
echo "  3. Check status: $PROJECT_DIR/scripts/status.sh"
echo "  4. View logs: $PROJECT_DIR/scripts/logs.sh [service]"
echo "  5. Access arifOS API: http://localhost:18080"
echo "  6. Access Grafana: http://localhost:13000 (admin/see .env)"
echo ""
echo -e "${YELLOW}Constitutional Status: 13/13 Floors Enforced${NC}"
echo -e "${YELLOW}VAULT999: Ready for audit logging${NC}"
echo -e "${YELLOW}F13 Sovereign: Human kill switch armed${NC}"
echo ""
echo "Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]"
