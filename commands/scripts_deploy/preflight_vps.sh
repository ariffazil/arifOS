#!/bin/bash
# preflight_vps.sh — VPS health probe for arifOS production deployment
# Skill: vps_health_probe
# DITEMPA BUKAN DIBERI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_DIR="${SCRIPT_DIR}/.."
EVIDENCE_DIR="${ARIFOS_DIR}/evidence"
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
EVIDENCE_FILE="${EVIDENCE_DIR}/preflight_vps_${TIMESTAMP}.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

HOSTNAME=$(hostnamectl --static 2>/dev/null || hostname)
UPTIME_INFO=$(uptime)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | xargs)

# ── Gather metrics ────────────────────────────────────────────
MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
MEM_USED=$(free -m | awk '/^Mem:/{print $3}')
MEM_AVAIL=$(free -m | awk '/^Mem:/{print $7}')
SWAP_TOTAL=$(free -m | awk '/^Swap:/{print $2}')
SWAP_USED=$(free -m | awk '/^Swap:/{print $3}')

df -h / > "$TMP_DIR/df_root" 2>/dev/null || true
DISK_SIZE=$(awk 'NR==2 {print $2}' "$TMP_DIR/df_root")
DISK_USED=$(awk 'NR==2 {print $3}' "$TMP_DIR/df_root")
DISK_AVAIL=$(awk 'NR==2 {print $4}' "$TMP_DIR/df_root")
DISK_PCT=$(awk 'NR==2 {gsub(/%/,""); print $5}' "$TMP_DIR/df_root")

DOCKER_INFO="unavailable"
DOCKER_PS="unavailable"
DOCKER_DF="unavailable"
if command -v docker >/dev/null 2>&1; then
    DOCKER_INFO=$(docker info --format '{{json .}}' 2>/dev/null || echo "{\"error\":\"docker info failed\"}")
    docker ps -a --format '{{.Names}}\t{{.Status}}\t{{.Image}}' > "$TMP_DIR/docker_ps" 2>/dev/null || true
    docker system df > "$TMP_DIR/docker_df" 2>/dev/null || true
    DOCKER_PS=$(cat "$TMP_DIR/docker_ps" 2>/dev/null | wc -l)
    DOCKER_DF=$(cat "$TMP_DIR/docker_df" 2>/dev/null | head -5 | tr '\n' '; ')
fi

PORTS_INFO="unavailable"
ss -tulpn > "$TMP_DIR/ports" 2>/dev/null || true
PORTS_INFO=$(cat "$TMP_DIR/ports" 2>/dev/null | grep -E ':(80|443|8080|8081|8082|8083|5432|6379|6333|8100|11434|3000|3003|7474|7687)' | head -30 || true)

# ── Evaluate thresholds ───────────────────────────────────────
STATUS="PASS"
REASONS=()
RISK="LOW"

if [ "${DISK_PCT:-0}" -ge 95 ]; then
    STATUS="FAIL"
    REASONS+=("disk_usage_critical:${DISK_PCT}%")
    RISK="CRITICAL"
elif [ "${DISK_PCT:-0}" -ge 85 ]; then
    STATUS="HOLD"
    REASONS+=("disk_usage_high:${DISK_PCT}%")
    RISK="HIGH"
fi

# Memory pressure: if available < 10% of total
MEM_PCT_AVAIL=$(awk "BEGIN {printf \"%.0f\", (${MEM_AVAIL}/${MEM_TOTAL})*100}")
if [ "${MEM_PCT_AVAIL:-0}" -lt 5 ]; then
    STATUS="FAIL"
    REASONS+=("memory_pressure_critical:${MEM_AVAIL}MB available")
    RISK="CRITICAL"
elif [ "${MEM_PCT_AVAIL:-0}" -lt 10 ]; then
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("memory_pressure_high:${MEM_AVAIL}MB available")
    [ "$RISK" = "LOW" ] && RISK="HIGH"
fi

# Swap exhaustion
if [ "${SWAP_TOTAL:-0}" -gt 0 ] && [ "${SWAP_USED:-0}" -gt 0 ]; then
    SWAP_PCT=$(awk "BEGIN {printf \"%.0f\", (${SWAP_USED}/${SWAP_TOTAL})*100}")
    if [ "$SWAP_PCT" -ge 90 ]; then
        [ "$STATUS" = "PASS" ] && STATUS="HOLD"
        REASONS+=("swap_exhausted:${SWAP_PCT}%")
        [ "$RISK" = "LOW" ] && RISK="MEDIUM"
    fi
fi

# Load average vs CPU cores
CPU_CORES=$(nproc 2>/dev/null || echo 1)
LOAD_1MIN=$(echo "$LOAD_AVG" | awk -F',' '{gsub(/ /,""); print $1}')
LOAD_CMP=$(awk "BEGIN {print ($LOAD_1MIN > $CPU_CORES * 2) ? \"high\" : \"ok\"}")
if [ "$LOAD_CMP" = "high" ]; then
    [ "$STATUS" = "PASS" ] && STATUS="HOLD"
    REASONS+=("load_high:${LOAD_1MIN} vs ${CPU_CORES} cores")
    [ "$RISK" = "LOW" ] && RISK="MEDIUM"
fi

# Docker daemon check
if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
    STATUS="FAIL"
    REASONS+=("docker_unhealthy")
    RISK="CRITICAL"
fi

# ── Print report ──────────────────────────────────────────────
echo "=== VPS PREFLIGHT ==="
echo "host:        $HOSTNAME"
echo "uptime:      $UPTIME_INFO"
echo "load:        $LOAD_AVG"
echo "memory:      ${MEM_USED}MB / ${MEM_TOTAL}MB (avail: ${MEM_AVAIL}MB)"
echo "swap:        ${SWAP_USED}MB / ${SWAP_TOTAL}MB"
echo "disk (/):    ${DISK_USED} / ${DISK_SIZE} (avail: ${DISK_AVAIL}, ${DISK_PCT}%)"
echo "docker_ps:   ${DOCKER_PS} containers"
echo ""
echo "status:      $STATUS"
echo "risk:        $RISK"
if [ ${#REASONS[@]} -gt 0 ]; then
    echo "reasons:"
    for r in "${REASONS[@]}"; do echo "  - $r"; done
fi

# ── Write evidence JSON ───────────────────────────────────────
REASONS_JSON=$(printf '%s\n' "${REASONS[@]}" | jq -R . | jq -s . 2>/dev/null || echo '[]')

cat > "$EVIDENCE_FILE" << EOF
{
  "skill": "vps_health_probe",
  "status": "$STATUS",
  "host": "$HOSTNAME",
  "timestamp_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "evidence": {
    "uptime": "$UPTIME_INFO",
    "load_average": "$LOAD_AVG",
    "memory_mb": { "total": $MEM_TOTAL, "used": $MEM_USED, "available": $MEM_AVAIL },
    "swap_mb": { "total": ${SWAP_TOTAL:-0}, "used": ${SWAP_USED:-0} },
    "disk_root": { "size": "$DISK_SIZE", "used": "$DISK_USED", "available": "$DISK_AVAIL", "pct_used": ${DISK_PCT:-0} },
    "cpu_cores": $CPU_CORES,
    "docker_containers": ${DOCKER_PS:-0},
    "docker_system_df": "$DOCKER_DF",
    "ports": $(echo "$PORTS_INFO" | jq -R -s -c 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
  },
  "reasons": $REASONS_JSON,
  "risk": "$RISK",
  "next_safe_action": $(if [ "$STATUS" = "FAIL" ]; then echo '"stop_deploy_and_alert_arif"'; elif [ "$STATUS" = "HOLD" ]; then echo '"resolve_pressure_before_deploy"'; else echo '"proceed_to_compose_guardian"'; fi),
  "requires_arif": $(if [ "$STATUS" != "PASS" ]; then echo 'true'; else echo 'false'; fi)
}
EOF

echo ""
echo "evidence:    $EVIDENCE_FILE"
echo "=== END PREFLIGHT ==="

[ "$STATUS" != "FAIL" ]
