#!/bin/bash
# ~/.openclaw/workspace/scripts/gödel-shim.sh
# Gödel Lock — Runtime enforcement layer for Ring-based security
# Version: 2026.03.21

set -euo pipefail

COMMAND="$1"
SESSION_ID="${2:-unknown}"
ACTOR_ID="${3:-anonymous}"
LOG_FILE="/root/.openclaw/workspace/logs/security.jsonl"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="267378578"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Timestamp helper
get_ts() {
    date -u +%Y-%m-%dT%H:%M:%SZ
}

# Log security event
log_event() {
    local event="$1"
    local details="${2:-}"
    local ts
    ts=$(get_ts)
    
    cat >> "$LOG_FILE" <<EOF
{"ts":"$ts","event":"$event","session_id":"$SESSION_ID","actor_id":"$ACTOR_ID","command":"$COMMAND","details":"$details"}
EOF
}

# Telegram alert
alert_telegram() {
    local severity="$1"
    local message="$2"
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        return 0
    fi
    
    local emoji
    case "$severity" in
        CRITICAL) emoji="🚨" ;;
        HIGH) emoji="⚠️" ;;
        MEDIUM) emoji="ℹ️" ;;
        *) emoji="📝" ;;
    esac
    
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${emoji} Gödel Lock: ${message}

Command: \`$COMMAND\`
Session: \`$SESSION_ID\`
Time: $(get_ts)" \
        -d "parse_mode=Markdown" > /dev/null 2>&1 || true
}

# Ring 2 pattern detection
# Returns 0 if blocked, 1 if allowed
ring_2_check() {
    local cmd="$1"
    
    # Define patterns as array of regex
    local patterns=(
        '^iptables\s'
        '^ufw\s+(enable|disable|allow|deny|reload|reset)'
        '^systemctl\s+(start|stop|restart|enable|disable|mask)'
        '^service\s+(start|stop|restart)'
        '^sysctl\s+-w'
        '^modprobe\s+(install|remove)'
        '^useradd\s'
        '^usermod\s'
        '^passwd\s'
        'sshd?_config'
        'docker\s+.*--privileged'
        'docker\s+.*--cap-add'
        'docker\s+.*--host'
        'docker\s+.*--network\s+host'
        'scp\s+.*\.(key|pem|secret|env)'
        'curl\s+.*-d\s+.*(sk-|token|api_key|password)'
        'wget\s+.*\|\s*sh'
        'wget\s+.*\|\s*bash'
        '^eval\s*\$'
        'base64\s+.*\|\s*sh'
        'chmod\s+.*\+x\s+/tmp'
        '^nc\s+-[el]'
        '^ncat\s+-[el]'
        'openssl\s+s_server'
        'mkfs\.'
        'fdisk\s'
        'parted\s'
    )
    
    for pattern in "${patterns[@]}"; do
        if echo "$cmd" | grep -qE "$pattern" 2>/dev/null; then
            echo "$pattern"
            return 0
        fi
    done
    
    return 1
}

# Secrets path detection
secrets_check() {
    local cmd="$1"
    
    local secret_paths=(
        '/opt/arifos/secrets'
        '~/.openclaw/credentials'
        'openclaw.json.secure'
        '/etc/shadow'
        '/etc/passwd'
        '\.key$'
        'id_rsa'
        'id_ed25519'
        '\.pem$'
    )
    
    for path in "${secret_paths[@]}"; do
        if echo "$cmd" | grep -qE "$path" 2>/dev/null; then
            echo "$path"
            return 0
        fi
    done
    
    return 1
}

# Main execution logic
main() {
    # Check for Ring 2 patterns
    local blocked_pattern
    if blocked_pattern=$(ring_2_check "$COMMAND"); then
        log_event "RING_2_BLOCKED" "matched_pattern:$blocked_pattern"
        alert_telegram "HIGH" "Ring 2 action blocked. Plan produced only."
        
        echo "GÖDEL_LOCK_BLOCKED: '$COMMAND' matches Ring 2 pattern '$blocked_pattern'"
        echo "ACTION: Produce plan only. Requires explicit 'do it' from Arif."
        exit 0
    fi
    
    # Check for secrets access
    local secret_path
    if secret_path=$(secrets_check "$COMMAND"); then
        log_event "SECRETS_ACCESS_ATTEMPT" "path:$secret_path"
        alert_telegram "HIGH" "Attempted access to secrets: $secret_path"
        
        echo "GÖDEL_LOCK_WARNING: Access to secrets path '$secret_path' detected and logged."
    fi
    
    # Ring 1 execution logging
    log_event "RING_1_EXEC" ""
    
    # Execute in sandboxed environment
    # Note: Actual execution is handled by OpenClaw's exec tool
    echo "GÖDEL_LOCK_OK: Ring 1 execution logged. Proceeding with sandboxed execution."
    exit 1  # Signal to continue with normal execution
}

main "$@"
