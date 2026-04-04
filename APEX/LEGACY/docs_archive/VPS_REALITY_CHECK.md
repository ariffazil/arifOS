# VPS Reality Check Procedure

**Version:** 2026.03.03  
**Frequency:** Weekly (or before major changes)  
**Runtime:** ~2 minutes  

---

## Quick Health Script

Run this single command for a full health check:

```bash
curl -s https://raw.githubusercontent.com/ariffazil/arifOS/main/docs/vps_health.sh | bash
```

Or run manually with the checks below.

---

## Pass/Fail Checklist

| # | Check | Command | Expected | Pass? | On Fail |
|---|-------|---------|----------|-------|---------|
| 1 | Docker running | `docker ps --format '{{.Names}}' | wc -l` | `>= 10` | ☐ | `systemctl start docker` |
| 2 | OpenClaw healthy | `docker ps --filter name=openclaw --format '{{.Status}}'` | contains `healthy` | ☐ | `docker restart openclaw` |
| 3 | Qdrant reachable | `docker exec openclaw curl -s --max-time 3 http://10.0.4.4:6333 | head -c 5` | `{` or `{"ti` | ☐ | Check network, restart qdrant |
| 4 | Ollama reachable | `docker exec openclaw curl -s --max-time 3 http://10.0.4.2:11434/api/tags | head -c 5` | `{"mod` | ☐ | Check network, restart ollama |
| 5 | arifOS Router (8080) | `curl -s --max-time 3 http://localhost:8080/sse | head -c 20` | `event: endpoint` | ☐ | Check process, restart if needed |
| 6 | Embeddings (8001) | `curl -s --max-time 3 http://localhost:8001/health | head -c 5` | `{"det` or similar | ☐ | Check embeddings server |
| 7 | PostgreSQL | `pg_isready -h localhost` | `accepting connections` | ☐ | `systemctl start postgresql` |
| 8 | Redis | `redis-cli ping` | `PONG` | ☐ | `systemctl start redis` |
| 9 | Disk space | `df -h / | tail -1 | awk '{print $5}'` | `< 80%` | ☐ | Clean up docker/images |
| 10 | Memory | `free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}'` | `< 90%` | ☐ | Restart heavy containers |

---

## Network Verification

```bash
# Expected network topology
echo "=== NETWORK TOPOLOGY ==="
docker network inspect bridge ai-net trinity_network coolify 2>/dev/null | \
  grep -E '"Name"|"Subnet"|"IPAddress"' | paste - - - | \
  awk -F'\t' '{gsub(/"/, "", $1); gsub(/"/, "", $3); print $1, $3}'
```

**Expected Output:**
```
bridge      10.0.0.0/24
ai-net      10.0.4.0/24
trinity_network  10.0.2.0/24
coolify     10.0.1.0/24
```

---

## Container IP Verification

```bash
echo "=== CONTAINER IPs ==="
for c in openclaw qdrant ollama agent-zero coolify; do
  ip=$(docker inspect $c 2>/dev/null | grep -A30 '"Networks"' | grep '"IPAddress"' | head -1 | awk -F'"' '{print $4}')
  echo "$c: $ip"
done
```

**Expected Output:**
```
openclaw: 10.0.4.3
qdrant: 10.0.4.4
ollama: 10.0.4.2
agent-zero: 10.0.2.2
coolify: 10.0.1.4
```

---

## Native Process Verification

```bash
echo "=== NATIVE SERVICES ==="
ss -tlnp | grep -E ':(8080|8001|5432|6379|80|443)\s'
```

**Expected Ports:**
| Port | Service | Process |
|------|---------|---------|
| 8080 | arifOS Router | python (arifos_router.py) |
| 8001 | Embeddings | python (embed_server.py) |
| 5432 | PostgreSQL | postgres |
| 6379 | Redis | redis-server |
| 80/443 | Nginx | nginx |

---

## Connectivity Tests (From OpenClaw)

```bash
echo "=== OPENCLAW CONNECTIVITY ==="
docker exec openclaw bash -c '
echo -n "Ollama: "
curl -s --max-time 3 http://10.0.4.2:11434/api/tags | head -c 5 && echo "OK" || echo "FAIL"

echo -n "Qdrant: "
curl -s --max-time 3 http://10.0.4.4:6333 | head -c 5 && echo "OK" || echo "FAIL"

echo -n "Host arifOS: "
curl -s --max-time 3 http://host.docker.internal:8080/sse | head -c 20 && echo "OK" || echo "FAIL"
'
```

---

## MCP Functionality Test

```bash
echo "=== MCP TOOL CALL TEST ==="
cd /root/arifOS && PYTHONPATH=/root/arifOS timeout 10 /root/arifOS/.venv/bin/python -m aaa_mcp stdio 2>/dev/null << 'EOF' | head -c 200
{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"health-check","version":"1.0"}}}
EOF
echo ""
echo "If you see serverInfo above, MCP is working."
```

---

## Actions Requiring 888_HOLD

The following actions **MUST NOT** be performed without human approval:

| Action | Risk Level | Why |
|--------|------------|-----|
| `docker system prune -f` | CRITICAL | Destroys unused containers/images |
| `ufw allow/deny` changes | HIGH | May lock out access |
| `docker network disconnect` | HIGH | Breaks connectivity |
| `rm -rf /root/*` | CRITICAL | Data loss |
| `systemctl restart docker` | MODERATE | Downtime for all containers |
| Database schema changes | HIGH | Data integrity risk |
| Secret rotation | HIGH | May break services |

---

## Quick Recovery Commands

### If arifOS Router is down:
```bash
pkill -f arifos_router.py || true
cd /root/arifOS && nohup /root/arifOS/.venv/bin/python /root/arifOS/arifos_router.py --sse --host 0.0.0.0 --port 8080 > /var/log/arifos/router.log 2>&1 &
```

### If OpenClaw can't reach Ollama:
```bash
docker network connect ai-net ollama 2>/dev/null || true
docker network connect ai-net openclaw 2>/dev/null || true
docker restart openclaw
```

### If disk is full:
```bash
docker system df
docker image prune -f --filter "dangling=true"
docker builder prune -f --filter "until=24h"
```

---

## Report Template

After running checks, create a status report:

```markdown
## VPS Health Report - [DATE]

| Check | Status | Notes |
|-------|--------|-------|
| Docker | ✅/❌ | |
| OpenClaw | ✅/❌ | |
| Qdrant | ✅/❌ | |
| Ollama | ✅/❌ | |
| arifOS MCP | ✅/❌ | |
| PostgreSQL | ✅/❌ | |
| Redis | ✅/❌ | |
| Disk | XX% | |
| Memory | XX% | |

**Issues Found:** [List or "None"]
**Actions Taken:** [List or "None"]
**888_HOLD Required:** [List or "None"]
```

---

**Ditempa Bukan Diberi** 🔥
