#!/bin/bash
# Autonomous Deployment System for arifOS MCP
# F5 Witness + F11 Auth + F13 Seal
# Triggers rebuild only when necessary

set -e

LOG_FILE="/var/log/arifos-auto-deploy.log"
LOCK_FILE="/tmp/arifos-auto-deploy.lock"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
TELEGRAM_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT="${TELEGRAM_CHAT_ID:-}"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Send notification
notify() {
    local message="$1"
    local priority="${2:-info}"
    
    # Telegram
    if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT}" \
            -d "text=${message}" \
            -d "parse_mode=Markdown" > /dev/null 2>&1 || true
    fi
    
    log "NOTIFY [$priority]: $message"
}

# Health check before deploy
pre_deploy_health_check() {
    log "Running pre-deploy health check..."
    
    # Check current container health
    if ! curl -fsS http://localhost:8080/health > /dev/null 2>&1; then
        log "⚠️  WARNING: Current container not healthy"
        notify "⚠️ Pre-deploy check: Container unhealthy" "warning"
        return 1
    fi
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 85 ]; then
        log "❌ ERROR: Disk usage ${disk_usage}% > 85%"
        notify "❌ Auto-deploy BLOCKED: Disk usage ${disk_usage}%" "error"
        return 1
    fi
    
    # Check memory
    local mem_available=$(free | grep Mem | awk '{print $7}')
    if [ "$mem_available" -lt 500000 ]; then
        log "⚠️  WARNING: Low memory (${mem_available}KB available)"
        notify "⚠️ Low memory warning: ${mem_available}KB available" "warning"
    fi
    
    log "✅ Pre-deploy health check passed"
    return 0
}

# Determine if rebuild is needed
needs_rebuild() {
    cd /root/arifosmcp
    
    # Pull latest
    git fetch origin main
    
    local local_hash=$(git rev-parse HEAD)
    local remote_hash=$(git rev-parse origin/main)
    
    if [ "$local_hash" = "$remote_hash" ]; then
        log "✅ Already at latest commit ($local_hash)"
        return 1
    fi
    
    log "📦 New commits available:"
    git log --oneline HEAD..origin/main | tee -a "$LOG_FILE"
    
    # Check what changed
    local changed_files=$(git diff --name-only HEAD origin/main)
    
    # Full reforge triggers
    if echo "$changed_files" | grep -qE "Dockerfile|requirements\.txt|pyproject\.toml"; then
        log "🔥 Full reforge needed (dependencies changed)"
        echo "reforge"
        return 0
    fi
    
    # Fast rebuild triggers
    if echo "$changed_files" | grep -qE "^core/|^arifosmcp/"; then
        log "⚡ Fast rebuild needed (code changed)"
        echo "fast"
        return 0
    fi
    
    # Config only
    if echo "$changed_files" | grep -qE "\.env|config|yaml|yml|json"; then
        log "🔄 Config reload needed"
        echo "reload"
        return 0
    fi
    
    # Default: hot restart
    log "🔄 Hot restart sufficient"
    echo "restart"
    return 0
}

# Deploy with rollback capability
deploy() {
    local strategy="$1"
    local start_time=$(date +%s)
    
    log "🚀 Starting deployment (strategy: $strategy)..."
    notify "🚀 Auto-deploy starting (strategy: $strategy)"
    
    # Backup current state
    local current_image=$(docker inspect arifos/arifosmcp:latest --format '{{.Id}}' 2>/dev/null || echo "none")
    log "📦 Current image: ${current_image:0:12}"
    
    # Execute deployment
    case $strategy in
        reforge)
            make reforge 2>&1 | tee -a "$LOG_FILE"
            ;;
        fast)
            make fast-deploy 2>&1 | tee -a "$LOG_FILE"
            ;;
        reload)
            make reload-config 2>&1 | tee -a "$LOG_FILE" || make restart 2>&1 | tee -a "$LOG_FILE"
            ;;
        restart)
            make restart 2>&1 | tee -a "$LOG_FILE"
            ;;
    esac
    
    # Post-deploy health check
    log "⏳ Waiting for container to stabilize..."
    sleep 15
    
    local attempts=0
    local max_attempts=12
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -fsS http://localhost:8080/health > /dev/null 2>&1; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            log "✅ Deployment successful (${duration}s)"
            notify "✅ Auto-deploy successful (${duration}s)"
            return 0
        fi
        attempts=$((attempts + 1))
        log "  Health check attempt $attempts/$max_attempts..."
        sleep 5
    done
    
    # Rollback on failure
    log "❌ Deployment failed - initiating rollback..."
    notify "❌ Deploy failed - rolling back" "error"
    
    docker stop arifosmcp 2>/dev/null || true
    docker rm arifosmcp 2>/dev/null || true
    docker run -d --name arifosmcp_old "$current_image" 2>/dev/null || true
    
    notify "🔄 Rollback complete" "warning"
    return 1
}

# Main auto-deploy loop
main() {
    # Check lock
    if [ -f "$LOCK_FILE" ]; then
        local lock_age=$(($(date +%s) - $(stat -c %Y "$LOCK_FILE")))
        if [ $lock_age -lt 300 ]; then
            log "⏭️  Auto-deploy already running (lock age: ${lock_age}s)"
            exit 0
        fi
        rm -f "$LOCK_FILE"
    fi
    
    touch "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
    
    log "═══════════════════════════════════════════════════"
    log "🤖 Auto-deploy check started"
    
    # Pre-deploy checks
    if ! pre_deploy_health_check; then
        log "⛔ Pre-deploy checks failed - aborting"
        exit 1
    fi
    
    # Check if rebuild needed
    local strategy=$(needs_rebuild)
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        log "✅ No deployment needed"
        exit 0
    fi
    
    # Execute deployment
    if deploy "$strategy"; then
        log "✅ Auto-deploy complete"
        exit 0
    else
        log "❌ Auto-deploy failed"
        exit 1
    fi
}

# Run main
main "$@"
