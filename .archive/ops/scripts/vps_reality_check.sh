#!/bin/bash
# VPS Reality Check - Weekly Ritual
# Version: 2026.03.03
# Usage: bash /root/arifOS/scripts/vps_reality_check.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

check_pass() { echo "${GREEN}✅ PASS${NC} $1"; ((PASS++)); }
check_fail() { echo "${RED}❌ FAIL${NC} $1"; ((FAIL++)); }
check_warn() { echo "${YELLOW}⚠️  WARN${NC} $1"; ((WARN++)); }

echo "=========================================="
echo "   VPS REALITY CHECK - $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="
echo ""

# 1. Docker Running
echo "## 1. Docker Status"
if docker ps --format "{{.Names}}" | grep -q .; then
    check_pass "Docker is running ($(docker ps -q | wc -l) containers)"
else
    check_fail "Docker not running or no containers"
fi
echo ""

# 2. Container Health
echo "## 2. Critical Containers"
for c in openclaw qdrant ollama agent-zero; do
    status=$(docker ps --filter "name=$c" --format "{{.Status}}" 2>/dev/null)
    if echo "$status" | grep -qi "healthy\|up"; then
        check_pass "$c: $status"
    else
        check_fail "$c: $status"
    fi
done
echo ""

# 3. Network Topology
echo "## 3. Network Topology"
expected_ai_net="openclaw:10.0.4.3 ollama:10.0.4.2 qdrant:10.0.4.4"
actual_ai_net=$(docker network inspect ai-net --format '{{range .Containers}}{{.Name}}:{{.IPv4Address}} {{end}}' 2>/dev/null)

if echo "$actual_ai_net" | grep -q "openclaw.*10.0.4.3"; then
    check_pass "ai-net topology matches expected"
else
    check_warn "ai-net topology may have drifted: $actual_ai_net"
fi
echo ""

# 4. Data Plane Connectivity
echo "## 4. Data Plane (OpenClaw -> Ollama/Qdrant)"
if docker exec openclaw curl -s --max-time 3 http://10.0.4.2:11434/api/tags 2>&1 | grep -q "models"; then
    check_pass "OpenClaw -> Ollama: Connected"
else
    check_fail "OpenClaw -> Ollama: Cannot connect"
fi

if docker exec openclaw curl -s --max-time 3 http://10.0.4.4:6333 2>&1 | grep -q "title\|result"; then
    check_pass "OpenClaw -> Qdrant: Connected"
else
    check_fail "OpenClaw -> Qdrant: Cannot connect"
fi
echo ""

# 5. Governance Plane
echo "## 5. Governance Plane (arifOS MCP)"
if timeout 3 curl -s http://localhost:8080/sse 2>&1 | grep -q "event: endpoint"; then
    check_pass "arifOS Router: SSE endpoint responding"
else
    check_fail "arifOS Router: Not responding"
fi

if docker exec openclaw curl -s --max-time 3 http://host.docker.internal:8080/sse 2>&1 | grep -q "event: endpoint"; then
    check_pass "OpenClaw -> arifOS: Connected via host.docker.internal"
else
    check_warn "OpenClaw -> arifOS: Cannot reach (UFW may block)"
fi
echo ""

# 6. Native Services
echo "## 6. Native Services"
for port service in 8080 "arifOS Router" 8001 "Embeddings" 5432 "PostgreSQL" 6379 "Redis"; do
    if ss -tlnp | grep -q ":$port "; then
        check_pass "$service listening on port $port"
    else
        check_fail "$service NOT listening on port $port"
    fi
done
echo ""

# 7. MCP stdio Test
echo "## 7. MCP stdio Mode"
result=$(cd /root/arifOS && PYTHONPATH=/root/arifOS timeout 5 /root/arifOS/.venv/bin/python -m arifosmcp.transport stdio 2>/dev/null << 'EOF'
{"jsonrpc":"2.0","method":"initialize","id":1,"params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"health-check","version":"1.0"}}}
EOF
)
if echo "$result" | grep -q "serverInfo\|protocolVersion"; then
    check_pass "MCP stdio mode working"
else
    check_fail "MCP stdio mode not responding"
fi
echo ""

# 8. Security Posture
echo "## 8. Security Checks"
if ufw status | grep -q "Status: active"; then
    check_pass "UFW firewall is active"
else
    check_warn "UFW firewall is not active"
fi

# Check for docker-mcp in Kimi config
if grep -q '"docker-mcp"' ~/.kimi/mcp.json 2>/dev/null; then
    check_warn "docker-mcp is ENABLED - RCE risk (see GODEL_BOUNDARY.md)"
else
    check_pass "docker-mcp is disabled"
fi

# Check published ports (UFW bypass risk)
published=$(docker ps --format "{{.Ports}}" | grep "0.0.0.0" | wc -l)
if [ "$published" -gt 0 ]; then
    check_warn "$published containers publish to 0.0.0.0 (bypasses UFW)"
fi
echo ""

# 9. Resource Usage
echo "## 9. Resource Usage"
disk_usage=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$disk_usage" -lt 80 ]; then
    check_pass "Disk usage: ${disk_usage}%"
elif [ "$disk_usage" -lt 90 ]; then
    check_warn "Disk usage: ${disk_usage}% (cleanup recommended)"
else
    check_fail "Disk usage: ${disk_usage}% (CRITICAL)"
fi

mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "${mem_usage%.*}" -lt 80 ]; then
    check_pass "Memory usage: ${mem_usage}%"
elif [ "${mem_usage%.*}" -lt 90 ]; then
    check_warn "Memory usage: ${mem_usage}% (consider restart)"
else
    check_fail "Memory usage: ${mem_usage}% (CRITICAL)"
fi
echo ""

# Summary
echo "=========================================="
echo "   SUMMARY"
echo "=========================================="
echo "${GREEN}PASSES: $PASS${NC}"
echo "${RED}FAILS: $FAIL${NC}"
echo "${YELLOW}WARNINGS: $WARN${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "${RED}STATUS: DRIFTING - RESEAL REQUIRED${NC}"
    echo "Run: /root/arifOS/scripts/vps_reseal.sh"
    exit 1
elif [ $WARN -gt 2 ]; then
    echo "${YELLOW}STATUS: CAUTION - Review warnings${NC}"
    exit 0
else
    echo "${GREEN}STATUS: REALITY_OK - TRINITY SEALED${NC}"
    exit 0
fi
