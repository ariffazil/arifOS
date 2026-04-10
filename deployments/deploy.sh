#!/bin/bash
# arifOS Deployment Script
# Deploys to VPS or Horizon with MCP Inspector validation
#
# Usage:
#   ./deployments/deploy.sh vps
#   ./deployments/deploy.sh horizon
#   ./deployments/deploy.sh test  # Run MCP Inspector tests only

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Function: Run MCP Inspector tests
run_mcp_inspector_tests() {
    log_info "Running MCP Inspector tests..."
    
    # Check if Python is available
    if ! command -v python &> /dev/null; then
        log_error "Python not found"
        return 1
    fi
    
    # Run MCP Inspector tests
    if python arifosmcp/evals/mcp_inspector_test.py --all --output deployments/mcp_inspector_report.json; then
        log_success "MCP Inspector tests PASSED"
        return 0
    else
        log_error "MCP Inspector tests FAILED"
        return 1
    fi
}

# Function: Run deployment gate tests
run_deployment_gates() {
    log_info "Running deployment gate tests..."
    
    if python arifosmcp/evals/deploy_gate.py --output deployments/deploy_gate_report.json; then
        log_success "Deployment gates PASSED"
        return 0
    else
        log_error "Deployment gates FAILED"
        return 1
    fi
}

# Function: Build and push Docker image
build_and_push() {
    local tag=${1:-latest}
    
    log_info "Building Docker image..."
    docker build -t arifos/arifosmcp:$tag .
    
    log_info "Pushing Docker image..."
    docker push arifos/arifosmcp:$tag
    
    log_success "Docker image built and pushed: arifos/arifosmcp:$tag"
}

# Function: Deploy to VPS
deploy_vps() {
    log_info "Deploying to VPS..."
    
    # Run tests first
    if ! run_mcp_inspector_tests; then
        log_error "MCP Inspector tests failed. Deployment aborted."
        exit 1
    fi
    
    if ! run_deployment_gates; then
        log_warn "Some deployment gates failed. Review before continuing."
        read -p "Continue deployment? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled."
            exit 0
        fi
    fi
    
    # Build and push
    build_and_push "vps-$(date +%Y%m%d-%H%M%S)"
    build_and_push "latest"
    
    # Deploy via SSH
    log_info "Deploying to VPS via SSH..."
    ssh root@arif-fazil.com << 'EOF'
        cd /root/arifOS
        git pull origin main
        docker-compose -f docker-compose.yml -f deployments/vps-deploy.yml pull
        docker-compose -f docker-compose.yml -f deployments/vps-deploy.yml up -d
        docker-compose ps
EOF
    
    log_success "VPS deployment complete!"
}

# Function: Deploy to Horizon
deploy_horizon() {
    log_info "Deploying to Horizon..."
    
    # Run tests first
    if ! run_mcp_inspector_tests; then
        log_error "MCP Inspector tests failed. Deployment aborted."
        exit 1
    fi
    
    # Build and push
    build_and_push "horizon-$(date +%Y%m%d-%H%M%S)"
    
    # Deploy to horizon server
    log_info "Deploying to Horizon via SSH..."
    ssh root@horizon.arif-fazil.com << 'EOF'
        cd /root/arifOS
        git pull origin main
        docker-compose -f docker-compose.yml -f deployments/horizon-deploy.yml pull
        docker-compose -f docker-compose.yml -f deployments/horizon-deploy.yml up -d
        docker-compose ps
EOF
    
    log_success "Horizon deployment complete!"
}

# Function: Test only
test_only() {
    log_info "Running tests only..."
    
    log_info "=== MCP Inspector Tests ==="
    run_mcp_inspector_tests
    
    log_info "=== Deployment Gate Tests ==="
    run_deployment_gates
    
    log_info "=== Substrate Smoke Tests ==="
    python arifosmcp/evals/substrate_smoke_runner.py --output deployments/substrate_smoke.json || true
    
    log_success "All tests complete. Reports saved to deployments/"
}

# Main
main() {
    local target="${1:-test}"
    
    echo "========================================"
    echo "  arifOS Deployment Script"
    echo "  Target: $target"
    echo "========================================"
    echo
    
    case "$target" in
        vps)
            deploy_vps
            ;;
        horizon)
            deploy_horizon
            ;;
        test)
            test_only
            ;;
        *)
            echo "Usage: $0 {vps|horizon|test}"
            echo
            echo "Commands:"
            echo "  vps     - Deploy to VPS (with full testing)"
            echo "  horizon - Deploy to Horizon (with testing)"
            echo "  test    - Run all tests only (no deployment)"
            exit 1
            ;;
    esac
}

main "$@"
