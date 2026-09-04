#!/usr/bin/env bash
# wire-snapshot.sh — Daily read-only wire snapshot + diff
# OBSERVE-ONLY. No mutations. No credentials in output.
set -euo pipefail

SNAPSHOT_DIR="/root/audit/snapshots"
TODAY=$(date +%Y%m%d)
YESTERDAY=$(date -d "yesterday" +%Y%m%d 2>/dev/null || date -v-1d +%Y%m%d)
OUTFILE="${SNAPSHOT_DIR}/wire-snapshot-${TODAY}.json"
PREVFILE="${SNAPSHOT_DIR}/wire-snapshot-${YESTERDAY}.json"
DIFFFILE="${SNAPSHOT_DIR}/wire-diff-${TODAY}.txt"

mkdir -p "$SNAPSHOT_DIR"

# Host info
HOSTNAME_S=$(hostname)
UPTIME_S=$(uptime -p 2>/dev/null || uptime)
LOAD_S=$(cat /proc/loadavg | awk '{print $1, $2, $3}')
MEM_PCT=$(free | awk '/Mem:/ {printf "%.1f", $3/$2*100}')
DISK_PCT=$(df / | awk 'NR==2 {gsub(/%/,""); print $5}')
TIMESTAMP=$(date -Iseconds)

# Services
SERVICES=$(systemctl list-units --type=service --state=running --no-pager --no-legend 2>/dev/null | awk '{print "\"" $1 "\""}' | paste -sd, -)

# Containers
CONTAINERS=$(docker ps --format '"{{.Names}}:{{.Image}}"' 2>/dev/null | paste -sd, - || echo "")

# Ports
PORTS=$(ss -tlnp 2>/dev/null | tail -n +2 | awk '{print $4}' | sort -u | sed 's/.*://' | sort -n | uniq | awk '{printf "\"%s\",", $1}' | sed 's/,$//' || echo "")

# Organ health
declare -A HEALTH
for port in 8088 7071 7072 7073 3001 8081 18082 18083 18901; do
  status=$(curl -sf --connect-timeout 2 "http://127.0.0.1:${port}/health" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "DOWN")
  HEALTH[$port]="$status"
done

# Config hashes
CFG_HASHES=""
for f in /root/AGENTS.md /root/AAA/instructions/constitution.md /root/AAA/instructions/autonomy.md; do
  if [ -f "$f" ]; then
    hash=$(sha256sum "$f" 2>/dev/null | awk '{print $1}' | head -c 16)
    CFG_HASHES="${CFG_HASHES}\"$(basename "$f")\":\"${hash}\","
  fi
done
CFG_HASHES="${CFG_HASHES%,}"

# Inventory
TOOLS=$(curl -sf --connect-timeout 2 "http://127.0.0.1:7071/health" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tools_loaded',0))" 2>/dev/null || echo "0")
SKILLS=$(find /root/AAA/skills -name "SKILL.md" -type f 2>/dev/null | wc -l || echo "0")

# Cron — SEC P0 (2026-09-04 Path A fix, FI-003): per-line json.dumps so any
# inner double quotes (e.g. "$SHA" in the observatory cron entry) are
# properly escaped as \" instead of leaking into the JSON string and
# breaking json.load(). Previous awk-only wrapping left inner " literal,
# producing "Expecting ',' delimiter" at parse time. Also handles backslashes.
CRON=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | python3 -c '
import sys, json
print(",".join(json.dumps(line.rstrip("\n")) for line in sys.stdin))
' || echo "")

# Build JSON
cat > "$OUTFILE" << JSONEOF
{
  "host": {"hostname":"${HOSTNAME_S}","uptime":"${UPTIME_S}","load":"${LOAD_S}","mem_pct":${MEM_PCT},"disk_pct":${DISK_PCT},"timestamp":"${TIMESTAMP}"},
  "services": [${SERVICES}],
  "containers": [${CONTAINERS}],
  "listening_ports": [${PORTS}],
  "organ_health": {":8088":"${HEALTH[8088]}","7071":"${HEALTH[7071]}","7072":"${HEALTH[7072]}","7073":"${HEALTH[7073]}","3001":"${HEALTH[3001]}","8081":"${HEALTH[8081]}","18082":"${HEALTH[18082]}","18083":"${HEALTH[18083]}","18901":"${HEALTH[18901]}"},
  "config_hashes": {${CFG_HASHES}},
  "inventory": {"tools_registered":${TOOLS},"skills_on_disk":${SKILLS}},
  "cron_jobs": [${CRON}]
}
JSONEOF

# Diff
if [ -f "$PREVFILE" ]; then
  python3 - "$PREVFILE" "$OUTFILE" "$DIFFFILE" << 'PYEOF'
import json, sys
prev_f, curr_f, diff_f = sys.argv[1], sys.argv[2], sys.argv[3]
with open(prev_f) as f: prev = json.load(f)
with open(curr_f) as f: curr = json.load(f)
changes = []
ps = set(prev.get("services",[])); cs = set(curr.get("services",[]))
for s in cs-ps: changes.append(f"NEW_SERVICE: {s}")
for s in ps-cs: changes.append(f"LOST_SERVICE: {s}")
pc = set(prev.get("containers",[])); cc = set(curr.get("containers",[]))
for c in cc-pc: changes.append(f"NEW_CONTAINER: {c}")
for c in pc-cc: changes.append(f"LOST_CONTAINER: {c}")
pp = set(prev.get("listening_ports",[])); cp = set(curr.get("listening_ports",[]))
for p in cp-pp: changes.append(f"NEW_PORT: {p}")
for p in pp-cp: changes.append(f"LOST_PORT: {p}")
ph = prev.get("config_hashes",{}); ch = curr.get("config_hashes",{})
for k in set(list(ph.keys())+list(ch.keys())):
    if ph.get(k) != ch.get(k): changes.append(f"CONFIG_CHANGED: {k}")
pi = prev.get("inventory",{}); ci = curr.get("inventory",{})
if pi.get("tools_registered") != ci.get("tools_registered"):
    changes.append(f"TOOL_COUNT: {pi.get('tools_registered')} -> {ci.get('tools_registered')}")
if pi.get("skills_on_disk") != ci.get("skills_on_disk"):
    changes.append(f"SKILL_COUNT: {pi.get('skills_on_disk')} -> {ci.get('skills_on_disk')}")
with open(diff_f,'w') as f:
    if not changes:
        f.write("NO_CHANGES\n"); print("WIRE SNAPSHOT: NO_CHANGES")
    else:
        for c in changes: f.write(c+"\n"); print(f"WIRE SNAPSHOT: {c}")
PYEOF
else
  echo "FIRST_SNAPSHOT" > "$DIFFFILE"
  echo "WIRE SNAPSHOT: FIRST_SNAPSHOT (baseline)"
fi

echo "Snapshot: ${OUTFILE}"
echo "Diff: ${DIFFFILE}"
