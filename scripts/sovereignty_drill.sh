#!/bin/bash
# sovereignty_drill.sh — Monthly Test of Tier 3 Sovereignty Floor
#
# Constitutional anchor: /root/arifOS/COMPUTE_TIERING.md §5
# Floors enforced: F13 SOVEREIGN
#
# PURPOSE:
# Verify that Tier 3 (Ollama local) actually works when Tier 1+2 disabled.
# Prevents "sovereignty theater" (untested fallback that fails during real outage).
#
# SCHEDULE:
# Runs 1st Sunday of each month, 02:00 MYT (low-traffic window)
#
# WHAT IT DOES:
# 1. Disable Tier 1 (MiniMax) + Tier 2 (ILMU) via environment override
# 2. Restart arifOS to pick up change
# 3. Verify Tier 3 (Ollama) serving traffic via /health endpoint
# 4. Run for 10 minutes (verify stability under Tier 3 load)
# 5. Re-enable Tier 1+2, restart arifOS
#
# EXIT CODES:
# 0 = Success (Tier 3 functional)
# 1 = Failure (Tier 3 did not serve traffic — F13 violation discovered)
#
# FAILURE HANDLING:
# If drill fails, DO NOT re-enable Tier 1+2 until Tier 3 fixed.
# This is pre-failure discovery (good outcome).
# Document in /root/arifOS/incidents/SOVEREIGNTY_DRILL_FAILURE_$(date -I).md

set -euo pipefail

# ═════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════

DRILL_DURATION=600  # 10 minutes
WARMUP_TIME=30      # Seconds to wait for arifOS restart
HEALTH_ENDPOINT="http://localhost:8088/health"
LOG_FILE="/var/log/arifos/sovereignty_drill.log"
INCIDENT_DIR="/root/arifOS/incidents"

# Systemd drop-in override directory
DROPIN_DIR="/etc/systemd/system/arifos.service.d"
DROPIN_FILE="${DROPIN_DIR}/sovereignty-drill-override.conf"

# ═════════════════════════════════════════════════════════════════════════
# LOGGING HELPER
# ═════════════════════════════════════════════════════════════════════════

log() {
    echo "[$(date -Iseconds)] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date -Iseconds)] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

# ═════════════════════════════════════════════════════════════════════════
# PRE-FLIGHT CHECKS
# ═════════════════════════════════════════════════════════════════════════

log "════════════════════════════════════════════════════════════════"
log "Starting Sovereignty Drill (Tier 3 Isolation Test)"
log "════════════════════════════════════════════════════════════════"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$INCIDENT_DIR"

# Check if arifOS service exists
if ! systemctl list-unit-files | grep -q "^arifos.service"; then
    log_error "arifOS service not found. Cannot run drill."
    exit 1
fi

# Check if Ollama is running (Tier 3 dependency)
if ! systemctl is-active --quiet ollama 2>/dev/null && ! pgrep -f ollama >/dev/null; then
    log_error "Ollama (Tier 3) is not running. Start it before drill: systemctl start ollama"
    exit 1
fi

log "Pre-flight checks passed."

# ═════════════════════════════════════════════════════════════════════════
# STEP 1: Disable Tier 1+2 (Create Systemd Drop-In Override)
# ═════════════════════════════════════════════════════════════════════════

log "Step 1: Disabling Tier 1 (MiniMax) + Tier 2 (ILMU) via systemd override"

mkdir -p "$DROPIN_DIR"

cat > "$DROPIN_FILE" <<'EOF'
# Temporary override for sovereignty drill
# Created by: /root/arifOS/scripts/sovereignty_drill.sh
# Purpose: Disable Tier 1+2 to test Tier 3 sovereignty floor

[Service]
Environment="MINIMAX_ENABLED=false"
Environment="ILMU_ENABLED=false"
EOF

log "Created systemd drop-in: $DROPIN_FILE"

# Reload systemd to pick up override
systemctl daemon-reload
log "Systemd reloaded."

# ═════════════════════════════════════════════════════════════════════════
# STEP 2: Restart arifOS
# ═════════════════════════════════════════════════════════════════════════

log "Step 2: Restarting arifOS to apply Tier 1+2 disable"

systemctl restart arifos

log "Waiting ${WARMUP_TIME}s for arifOS warm-up..."
sleep "$WARMUP_TIME"

# ═════════════════════════════════════════════════════════════════════════
# STEP 3: Verify Tier 3 Serving Traffic
# ═════════════════════════════════════════════════════════════════════════

log "Step 3: Verifying Tier 3 (Ollama) is serving traffic"

# Query health endpoint (expect llm_tier=ollama)
HEALTH_RESPONSE=$(curl -s "$HEALTH_ENDPOINT" || echo "{}")
LLM_TIER=$(echo "$HEALTH_RESPONSE" | jq -r '.llm_tier // "unknown"')

log "Health endpoint response: llm_tier=$LLM_TIER"

if [ "$LLM_TIER" != "ollama" ]; then
    log_error "DRILL FAILED: Expected llm_tier='ollama', got '$LLM_TIER'"
    log_error "Tier 3 did not activate when Tier 1+2 disabled."
    log_error "This is a HIDDEN SOVEREIGNTY VULNERABILITY (F13)."
    
    # Create incident report
    INCIDENT_FILE="${INCIDENT_DIR}/SOVEREIGNTY_DRILL_FAILURE_$(date -I).md"
    cat > "$INCIDENT_FILE" <<EOF_INCIDENT
# Sovereignty Drill Failure — $(date -Iseconds)

## What Happened

Monthly sovereignty drill detected that Tier 3 (Ollama) **did not serve traffic**
when Tier 1 (MiniMax) and Tier 2 (ILMU) were disabled.

## Health Endpoint Response

\`\`\`json
$HEALTH_RESPONSE
\`\`\`

Expected: \`llm_tier: "ollama"\`
Actual: \`llm_tier: "$LLM_TIER"\`

## Constitutional Impact

**This is F13 SOVEREIGN violation (hidden).** If a real Tier 1+2 outage occurred,
system would hard-fail instead of degrading gracefully to Tier 3.

## Next Steps

1. **DO NOT re-enable Tier 1+2 until Tier 3 fixed.**
2. Investigate why Tier 3 failed:
   - Check Ollama status: \`systemctl status ollama\`
   - Check models: \`ollama list\`
   - Check port: \`ss -tuln | grep 11434\`
   - Check disk: \`df -h\`
   - Check logs: \`journalctl -u ollama -n 100\`
3. Fix root cause.
4. Re-run drill manually: \`/root/arifOS/scripts/sovereignty_drill.sh\`
5. Verify success (\`llm_tier: "ollama"\`) before restoring Tier 1+2.

## Timeline

- **$(date -Iseconds):** Drill started
- **$(date -Iseconds):** Tier 1+2 disabled via systemd override
- **$(date -Iseconds):** arifOS restarted
- **$(date -Iseconds):** Health check failed (llm_tier != "ollama")
- **$(date -Iseconds):** Drill aborted, Tier 1+2 NOT restored

## Recovery

\`\`\`bash
# After fixing Tier 3:
/root/arifOS/scripts/sovereignty_drill.sh

# If success, manually restore Tier 1+2:
rm /etc/systemd/system/arifos.service.d/sovereignty-drill-override.conf
systemctl daemon-reload
systemctl restart arifos
\`\`\`

**Status:** Tier 1+2 remain disabled. System in manual-recovery mode.
EOF_INCIDENT
    
    log_error "Incident report created: $INCIDENT_FILE"
    log_error "Tier 1+2 remain DISABLED until manual recovery."
    log_error "Read incident report for recovery steps."
    
    # Set Prometheus metric (if prometheus_client available)
    echo "arifos_sovereignty_drill_status 0" | curl --data-binary @- http://localhost:9091/metrics/job/sovereignty_drill || true
    
    exit 1
fi

log "✓ Tier 3 verified serving traffic (llm_tier=ollama)"

# ═════════════════════════════════════════════════════════════════════════
# STEP 4: Run for 10 Minutes (Stability Test)
# ═════════════════════════════════════════════════════════════════════════

log "Step 4: Running for ${DRILL_DURATION}s to verify Tier 3 stability under load"

# Poll health endpoint every 30s, verify llm_tier stays "ollama"
POLL_INTERVAL=30
ELAPSED=0

while [ $ELAPSED -lt $DRILL_DURATION ]; do
    sleep $POLL_INTERVAL
    ELAPSED=$((ELAPSED + POLL_INTERVAL))
    
    HEALTH_RESPONSE=$(curl -s "$HEALTH_ENDPOINT" || echo "{}")
    LLM_TIER=$(echo "$HEALTH_RESPONSE" | jq -r '.llm_tier // "unknown"')
    
    if [ "$LLM_TIER" != "ollama" ]; then
        log_error "DRILL FAILED at ${ELAPSED}s: Tier 3 switched away from ollama (now: $LLM_TIER)"
        log_error "Tier 3 is unstable under load."
        exit 1
    fi
    
    log "Health check @ ${ELAPSED}s: llm_tier=$LLM_TIER (OK)"
done

log "✓ Tier 3 stable for ${DRILL_DURATION}s"

# ═════════════════════════════════════════════════════════════════════════
# STEP 5: Re-Enable Tier 1+2
# ═════════════════════════════════════════════════════════════════════════

log "Step 5: Re-enabling Tier 1 + Tier 2"

# Remove systemd override
rm -f "$DROPIN_FILE"
systemctl daemon-reload
log "Systemd override removed."

# Restart arifOS to restore normal tiering
systemctl restart arifos
log "arifOS restarted with Tier 1+2 enabled."

sleep "$WARMUP_TIME"

# Verify Tier 1 (MiniMax) or Tier 2 (ILMU) now serving
HEALTH_RESPONSE=$(curl -s "$HEALTH_ENDPOINT" || echo "{}")
LLM_TIER=$(echo "$HEALTH_RESPONSE" | jq -r '.llm_tier // "unknown"')

if [ "$LLM_TIER" == "ollama" ]; then
    log "WARNING: After re-enabling Tier 1+2, still using Tier 3 (llm_tier=ollama)"
    log "This may indicate Tier 1+2 are down. Check provider status."
else
    log "✓ Tier 1+2 restored (llm_tier=$LLM_TIER)"
fi

# ═════════════════════════════════════════════════════════════════════════
# SUCCESS
# ═════════════════════════════════════════════════════════════════════════

log "════════════════════════════════════════════════════════════════"
log "Sovereignty Drill PASSED"
log "════════════════════════════════════════════════════════════════"
log "Tier 3 (Ollama) successfully served traffic for ${DRILL_DURATION}s"
log "when Tier 1+2 were disabled."
log "F13 SOVEREIGN floor verified functional."

# Set Prometheus metric
echo "arifos_sovereignty_drill_status 1" | curl --data-binary @- http://localhost:9091/metrics/job/sovereignty_drill || true

exit 0
