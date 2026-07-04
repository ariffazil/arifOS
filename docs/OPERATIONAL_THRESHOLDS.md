# Operational Thresholds — arifOS Federation

> **Purpose:** Hard limits and response procedures for federation health.
> **Source:** MCP_ENDPOINT_REGISTRY.md — extracted for focused reference.
> **DITEMPA BUKAN DIBERI**

---

## Gateway Event Loop Thresholds

| P99 Delay | Status | Action |
|-----------|--------|--------|
| < 100ms | ✅ Healthy | None |
| 100–500ms | 🟡 Elevated | Monitor |
| 500–2000ms | 🔴 Warning | Investigate within 1 hour |
| > 2000ms | 🚨 Critical | Restart gateway immediately |
| > 10000ms | 💀 Choking | SIGUSR1 or kill + restart |

**Check:** `curl -s http://localhost:18789/health` — alert if P99 > 1000ms.

---

## Disk Health Thresholds

| Usage | Status | Action |
|-------|--------|--------|
| < 70% | ✅ Healthy | None |
| 70–80% | 🟡 Caution | Monitor weekly |
| 80–90% | 🔴 Warning | Investigate within 48h |
| > 90% | 🚨 Critical | Immediate cleanup — alert Arif |

**Check:** `df -h /` — monitor `/` partition.

---

## Chaos Prevention Rules (MCP Endpoints)

1. **Before changing any MCP endpoint**: Update the MCP_ENDPOINT_REGISTRY FIRST
2. **After changing openclaw.json**: Verify the URL matches the registry
3. **After changing Caddyfile routes**: Verify the proxy target matches the registry
4. **After changing server.py transport**: Update the transport column
5. **After deploying a new container**: Run the health check suite
6. **Gateway health check**: alert if P99 > 1000ms

---

## Maintenance Cron Schedule

| Frequency | Task |
|-----------|------|
| Every 15 min | Health check all public endpoints |
| Every 1 hour | Check gateway event loop P99 |
| Daily | Verify openclaw.json URLs match registry |
| After deployment | Run full health check suite |

---

## Health Check Commands

```bash
# All public endpoints
curl -s --max-time 5 https://mcp.arif-fazil.com/health
curl -s --max-time 5 https://geox.arif-fazil.com/health
curl -s --max-time 5 https://wealth.arif-fazil.com/health
curl -s --max-time 5 https://well.arif-fazil.com/health

# MCP tool discovery (after initialize)
curl -s --max-time 5 -X POST https://mcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

---

*Extracted from MCP_ENDPOINT_REGISTRY.md — maintained by ASI*
