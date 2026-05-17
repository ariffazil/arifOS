# MCP Endpoint Registry — Source of Truth
# Updated: 2026-05-16
# Author: ASI

## Purpose
Single source of truth for all MCP endpoints in the arifOS Federation.
All other references (openclaw.json, Caddyfile, docs) must match this registry.
Any divergence = immediate fix.

---

## Active Endpoints

### arifOS Kernel
| Property | Value |
|----------|-------|
| Name | arifOS Constitutional |
| Public URL | `https://arifos.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://arifosmcp:8080/mcp` |
| Container port | 8080 |
| Caddy route | `arifos.arif-fazil.com/mcp*` → `arifosmcp:8080` |
| Tools | 13 canonical (arif_session_init → arif_ops_measure) |
| Auth | None (public) |
| Status | ✅ HEALTHY |

### GEOX (Earth Intelligence)
| Property | Value |
|----------|-------|
| Name | GEOX Earth Coprocessor |
| Public URL | `https://geox.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://geox_eic:8081/mcp` AND `/mcp/stream` (both routes) |
| Container port | 8081 |
| Caddy route | `geox.arif-fazil.com/mcp/*` → `geox_eic:8081/mcp/stream` |
| Tools | 13 canonical geoscience tools |
| Auth | None (public) |
| Status | ✅ HEALTHY |
| Note | `/mcp` and `/mcp/stream` both work (same handler) |

### WEALTH (Capital Intelligence)
| Property | Value |
|----------|-------|
| Name | WEALTH Capital Coprocessor |
| Public URL | `https://wealth.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://wealth-organ:8082/mcp` |
| Container port | 8082 |
| Caddy route | `wealth.arif-fazil.com/mcp` → `wealth-organ:8082/mcp` |
| Tools | 79 (13 sovereign + 66 legacy aliases) |
| Auth | None (public) |
| Status | ✅ HEALTHY |

### WELL (Biological Substrate)
| Property | Value |
|----------|-------|
| Name | WELL Biological Monitor |
| Public URL | `https://well.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://well:8083/mcp` |
| Container port | 8083 |
| Caddy route | `well.arif-fazil.com/mcp` → `well:8083/mcp` |
| Tools | ~30 wellness/hardening tools |
| Auth | None (public) |
| Status | ✅ HEALTHY (compose stack re-added 2026-05-05) |

---

## Endpoint Configuration Map

| Service | openclaw.json url | Caddyfile route | server.py transport |
|---------|------------------|-----------------|-------------------|
| arifOS | `http://localhost:8080/mcp` | `arifos.arif-fazil.com/mcp*` | `streamable-http` |
| GEOX | `https://geox.arif-fazil.com/mcp` | `geox.arif-fazil.com/mcp/*` | `streamable-http` |
| WEALTH | `http://localhost:8082/mcp` | `wealth.arif-fazil.com/mcp` | `streamable-http` |
| WELL | `https://well.arif-fazil.com/mcp` | `well.arif-fazil.com/mcp` | `streamable-http` |

---

## Transport Reference

| Transport | Use Case | Client Support |
|-----------|----------|----------------|
| `streamable-http` | Public API, external clients, ChatGPT MCP | All modern MCP clients ✅ |
| `sse` | Legacy streamable-http v1 | Deprecated, avoid |
| `stdio` | Local CLI only | Local tools only ❌ |

**Rule: All public endpoints use `streamable-http`.**

---

## Health Check Commands

```bash
# All public endpoints
curl -s --max-time 5 https://arifos.arif-fazil.com/health
curl -s --max-time 5 https://geox.arif-fazil.com/health
curl -s --max-time 5 https://wealth.arif-fazil.com/health
curl -s --max-time 5 https://well.arif-fazil.com/health

# MCP tool discovery (after initialize)
curl -s --max-time 5 -X POST https://arifos.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

---

## Chaos Prevention Rules

1. **Before changing any MCP endpoint**: Update this registry FIRST
2. **After changing openclaw.json**: Verify the URL matches this registry
3. **After changing Caddyfile routes**: Verify the proxy target matches this registry
4. **After changing server.py transport**: Update the transport column
5. **After deploying a new container**: Run the health check commands above
6. **Gateway health check**: `curl -s http://localhost:18789/health` — alert if P99 > 1000ms

---

## Gateway Event Loop Thresholds

| P99 Delay | Status | Action |
|-----------|--------|--------|
| < 100ms | ✅ Healthy | None |
| 100-500ms | 🟡 Elevated | Monitor |
| 500-2000ms | 🔴 Warning | Investigate within 1 hour |
| > 2000ms | 🚨 Critical | Restart gateway immediately |
| > 10000ms | 💀 Choking | SIGUSR1 or kill + restart |

---

## Maintenance Cron

- Every 15 minutes: health check all public endpoints
- Every 1 hour: check gateway event loop P99
- Daily: verify openclaw.json URLs match registry
- After any deployment: run full health check suite

DITEMPA BUKAN DIBERI — Forged, not given.
