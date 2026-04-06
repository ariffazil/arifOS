#!/bin/bash
# Low-Entropy Server Management - Automated Maintenance
# Runs via cron - minimizes manual intervention

LOG_FILE="/var/log/arifos-maintenance.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function: Check and restart unhealthy containers
health_monitor() {
    log "🔍 Health monitoring..."
    
    local unhealthy=$(docker ps --filter "health=unhealthy" --format "{{.Names}}" 2>/dev/null)
    
    if [ -n "$unhealthy" ]; then
        log "⚠️  Unhealthy containers found: $unhealthy"
        
        for container in $unhealthy; do
            log "🔄 Restarting $container..."
            docker restart "$container" 2>&1 | tee -a "$LOG_FILE"
            sleep 10
            
            # Verify restart
            if docker ps --filter "name=$container" --filter "health=healthy" | grep -q "$container"; then
                log "✅ $container restored to healthy"
            else
                log "❌ $container still unhealthy after restart"
            fi
        done
    else
        log "✅ All containers healthy"
    fi
}

# Function: Clean up Docker system (conservative)
docker_cleanup() {
    log "🧹 Docker cleanup..."
    
    # Only remove unused images older than 7 days
    docker image prune -a --filter "until=168h" -f 2>&1 | tee -a "$LOG_FILE" || true
    
    # Clean build cache if > 10GB
    local cache_size=$(docker system df | grep "Build Cache" | awk '{print $4}')
    if [[ "$cache_size" == *"GB"* ]]; then
        local size_num=$(echo "$cache_size" | sed 's/GB//')
        if (( $(echo "$size_num > 10" | bc -l) )); then
            log "🧹 Build cache too large (${cache_size}), pruning..."
            docker builder prune -f 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
    
    log "✅ Docker cleanup complete"
}

# Function: Check disk space and alert
disk_monitor() {
    log "💾 Disk monitoring..."
    
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        log "🚨 CRITICAL: Disk usage ${usage}%"
        # Could trigger Slack/Telegram alert here
    elif [ "$usage" -gt 75 ]; then
        log "⚠️  WARNING: Disk usage ${usage}%"
    else
        log "✅ Disk usage ${usage}% OK"
    fi
}

# Function: Check memory
memory_monitor() {
    log "🧠 Memory monitoring..."
    
    local mem_info=$(free -h | grep Mem)
    local mem_percent=$(free | grep Mem | awk '{print ($3/$2) * 100}' | cut -d. -f1)
    
    if [ "$mem_percent" -gt 90 ]; then
        log "🚨 CRITICAL: Memory usage ${mem_percent}%"
    elif [ "$mem_percent" -gt 80 ]; then
        log "⚠️  WARNING: Memory usage ${mem_percent}%"
    else
        log "✅ Memory usage ${mem_percent}% OK"
    fi
}

# Function: Backup critical data
backup_data() {
    log "💾 Backup check..."
    
    # Check if backup needed (daily)
    local last_backup=$(stat -c %Y /opt/arifos/data/.last_backup 2>/dev/null || echo 0)
    local now=$(date +%s)
    local day_seconds=86400
    
    if [ $((now - last_backup)) -gt $day_seconds ]; then
        log "📦 Creating daily backup..."
        
        # Simple backup of critical configs
        tar czf "/opt/arifos/backups/config-$(date +%Y%m%d).tar.gz" \
            /opt/arifos/data/openclaw/openclaw.json \
            /root/arifosmcp/.env \
            /root/arifosmcp/.env.docker \
            2>/dev/null || true
        
        touch /opt/arifos/data/.last_backup
        log "✅ Backup complete"
    else
        log "⏭️  Backup not needed yet"
    fi
    
    # Clean old backups (keep 7 days)
    find /opt/arifos/backups -name "config-*.tar.gz" -mtime +7 -delete 2>/dev/null || true
}

# Function: Sync with GitHub (auto-deploy check)
git_sync() {
    log "🔄 Git sync check..."
    
    cd /root/arifosmcp
    
    git fetch origin main 2>&1 | tee -a "$LOG_FILE"
    
    local local_hash=$(git rev-parse HEAD)
    local remote_hash=$(git rev-parse origin/main)
    
    if [ "$local_hash" != "$remote_hash" ]; then
        log "📦 New commits available:"
        git log --oneline HEAD..origin/main | tee -a "$LOG_FILE"
        
        # Auto-deploy if configured
        if [ "${ARIFOS_AUTO_DEPLOY:-false}" = "true" ]; then
            log "🚀 Auto-deploy enabled, deploying..."
            /root/arifosmcp/scripts/auto-deploy.sh 2>&1 | tee -a "$LOG_FILE"
        else
            log "⏸️  Auto-deploy disabled, manual action required"
        fi
    else
        log "✅ Already up to date"
    fi
}

# Main execution
main() {
    log "═══════════════════════════════════════════════════"
    log "🔧 Low-Entropy Maintenance Started"
    
    case "${1:-all}" in
        health)
            health_monitor
            ;;
        docker)
            docker_cleanup
            ;;
        disk)
            disk_monitor
            ;;
        memory)
            memory_monitor
            ;;
        backup)
            backup_data
            ;;
        git)
            git_sync
            ;;
        all)
            health_monitor
            disk_monitor
            memory_monitor
            docker_cleanup
            backup_data
            git_sync
            ;;
    esac
    
    log "✅ Maintenance complete"
}

main "$@"
