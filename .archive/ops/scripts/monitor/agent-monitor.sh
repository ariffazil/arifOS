#!/bin/bash
# Agent Activity Monitor - CLI Tool
# Usage: ./agent-monitor.sh [today|recent|errors|stats]

VAULT_FILE="/root/arifOS/VAULT999/vault999.jsonl"
LOG_FILE="/var/log/agent-activity.log"

show_help() {
    echo "Agent Activity Monitor"
    echo ""
    echo "Usage: agent-monitor [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  today       Show all agent activity from today"
    echo "  recent      Show last 20 agent actions"
    echo "  errors      Show failed/VOID verdicts"
    echo "  stats       Show activity statistics"
    echo "  live        Watch real-time activity"
    echo "  help        Show this help"
    echo ""
}

show_today() {
    echo "🔍 Agent Activity - Today ($(date +%Y-%m-%d))"
    echo "================================================"
    TODAY=$(date +%Y-%m-%d)
    grep "\"timestamp\":\"$TODAY" "$VAULT_FILE" 2>/dev/null | \
        jq -r '[.timestamp, .session_id[:8], .verdict, .query[:50]] | @tsv' | \
        tail -20 | \
        column -t -s $'\t'
    
    COUNT=$(grep "\"timestamp\":\"$TODAY" "$VAULT_FILE" 2>/dev/null | wc -l)
    echo ""
    echo "Total actions today: $COUNT"
}

show_recent() {
    echo "🔍 Recent Agent Activity (Last 20)"
    echo "================================================"
    tail -20 "$VAULT_FILE" | \
        jq -r '[.timestamp[:19], .session_id[:8], .verdict, .query[:40]] | @tsv' | \
        column -t -s $'\t'
}

show_errors() {
    echo "⚠️  Failed Agent Actions (VOID/ERROR)"
    echo "================================================"
    grep '"verdict":"VOID"' "$VAULT_FILE" 2>/dev/null | \
        jq -r '[.timestamp[:19], .session_id[:8], .verdict, .query[:40]] | @tsv' | \
        tail -10 | \
        column -t -s $'\t'
    
    ERROR_COUNT=$(grep '"verdict":"VOID"' "$VAULT_FILE" 2>/dev/null | wc -l)
    echo ""
    echo "Total failures: $ERROR_COUNT"
}

show_stats() {
    echo "📊 Agent Activity Statistics"
    echo "================================================"
    
    TOTAL=$(wc -l < "$VAULT_FILE")
    TODAY=$(date +%Y-%m-%d)
    TODAY_COUNT=$(grep "\"timestamp\":\"$TODAY" "$VAULT_FILE" 2>/dev/null | wc -l)
    SEAL_COUNT=$(grep '"verdict":"SEAL"' "$VAULT_FILE" 2>/dev/null | wc -l)
    VOID_COUNT=$(grep '"verdict":"VOID"' "$VAULT_FILE" 2>/dev/null | wc -l)
    
    echo "Total logged actions:     $TOTAL"
    echo "Actions today:            $TODAY_COUNT"
    echo "Successful (SEAL):        $SEAL_COUNT"
    echo "Failed (VOID):            $VOID_COUNT"
    TOTAL_VERDICTS=$((SEAL_COUNT + VOID_COUNT))
    if [ $TOTAL_VERDICTS -gt 0 ]; then
        echo "Success rate:             $(( SEAL_COUNT * 100 / TOTAL_VERDICTS ))%"
    else
        echo "Success rate:             N/A (no verdicts logged)"
    fi
    echo ""
    echo "Last 5 sessions:"
    tail -5 "$VAULT_FILE" | jq -r '[.timestamp[:19], .session_id[:8], .verdict] | @tsv' | column -t -s $'\t'
}

watch_live() {
    echo "👁️  Watching agent activity in real-time..."
    echo "Press Ctrl+C to stop"
    echo "================================================"
    tail -f "$VAULT_FILE" | jq -r '[.timestamp[:19], .session_id[:8], .verdict, .query[:40]] | @tsv'
}

# Main
case "${1:-help}" in
    today)
        show_today
        ;;
    recent)
        show_recent
        ;;
    errors)
        show_errors
        ;;
    stats)
        show_stats
        ;;
    live)
        watch_live
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
