#!/bin/bash
# 111_SENSE — Native Machine Sensing Layer
# Runs as systemd service. Feeds thermodynamic state to VAULT.

VAULT="/var/lib/arifos/vault/sense.jsonl"
FIFO="/run/arifos/sense.fifo"
INTERVAL=5

mkdir -p /run/arifos
[ -p "$FIFO" ] || mkfifo "$FIFO" 2>/dev/null

echo "{\"ts\":\"$(date -Iseconds)\",\"event\":\"SENSE_BOOT\",\"pid\":$$}" >> "$VAULT"

while true; do
    TS=$(date -Iseconds)
    
    # Thermodynamic metrics
    CPU_LOAD=$(cut -d' ' -f1 /proc/loadavg)
    MEM_TOTAL=$(awk '/MemTotal/{print $2}' /proc/meminfo)
    MEM_AVAIL=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
    MEM_PCT=$(awk "BEGIN {printf \"%.2f\", (($MEM_TOTAL - $MEM_AVAIL) / $MEM_TOTAL) * 100}")
    ENTROPY=$(cat /proc/sys/kernel/random/entropy_avail)
    DISK_PCT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    PROCS=$(nproc)
    UPTIME=$(awk '{print $1}' /proc/uptime)
    
    # Docker metabolism
    CONTAINERS=$(docker ps -q 2>/dev/null | wc -l)
    CONTAINERS_TOTAL=$(docker ps -aq 2>/dev/null | wc -l)
    
    # JSON payload
    JSON=$(cat <<EOF
{"ts":"$TS","floor":"111_SENSE","cpu_load":$CPU_LOAD,"mem_pct":$MEM_PCT,"entropy":$ENTROPY,"disk_pct":$DISK_PCT,"procs":$PROCS,"uptime_sec":$UPTIME,"containers_running":$CONTAINERS,"containers_total":$CONTAINERS_TOTAL}
EOF
)
    
    # Write to VAULT (append-only, cannot be tampered)
    echo "$JSON" >> "$VAULT"
    
    # Also write to FIFO for live consumers
    echo "$JSON" > "$FIFO" 2>/dev/null || true
    
    sleep $INTERVAL
done
