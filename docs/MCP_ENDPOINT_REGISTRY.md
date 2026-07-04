# MCP Endpoint Registry — Source of Truth
# Updated: 2026-07-01
# Author: arifOS maintainers

## Purpose
Single source of truth for all MCP endpoints in the arifOS Federation.
All other references (openclaw.json, Caddyfile, docs) must match this registry.
Any divergence = immediate fix.

Companion SOT: `docs/MCP_SOURCE_OF_TRUTH.md`.

---

## Active Endpoints

### arifOS Kernel
| Property | Value |
|----------|-------|
| Name | arifOS Constitutional |
| Public URL | `https://mcp.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://127.0.0.1:8088/mcp` |
| Container port | 8080 (Docker default); live VPS uses 8088 |
| Caddy route | `mcp.arif-fazil.com/mcp*` → `127.0.0.1:8088` |
| Tools | 7 public canonical verbs (`arif_init/observe/think/route/judge/act/seal`); 17 internal canonical; 48 exposed via MCP |
| Auth | None (public) |
| Status | HEALTHY, verified by `/health` on 2026-07-01 |

### GEOX (Earth Intelligence)
| Property | Value |
|----------|-------|
| Name | GEOX Earth Coprocessor |
| Public URL | `https://geox.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://127.0.0.1:18081/mcp` AND `/mcp/stream` (both routes) |
| Container port | 8081 (Docker default); live VPS uses 18081 |
| Caddy route | `geox.arif-fazil.com/mcp/*` → `127.0.0.1:18081/mcp/stream` |
| Tools | 31 canonical tools per `/health` |
| Auth | None (public) |
| Status | HEALTHY, verified by `/health` on 2026-07-01 |
| Note | Enumeration requires MCP JSON-RPC session headers. Public `tools/list` without session may return 7 surface tools. |

### WEALTH (Capital Intelligence)
| Property | Value |
|----------|-------|
| Name | WEALTH Capital Coprocessor |
| Public URL | `https://wealth.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://127.0.0.1:18082/mcp` |
| Container port | 8082 (Docker default); live VPS uses 18082 |
| Caddy route | `wealth.arif-fazil.com/mcp` → `127.0.0.1:18082/mcp` |
| Tools | 32 live MCP tools (includes backward-compat aliases) |
| Auth | None (public) |
| Status | HEALTHY, verified by `/health` on 2026-07-01 |
| Note | Enumeration requires MCP JSON-RPC session headers. Includes legacy aliases such as `wealth_emv_compute`, `wealth_monte_carlo`, `wealth_evoi_compute`, `wealth_reason_agent`, `wealth_system_registry_status`. |

### WELL (Biological Substrate)
| Property | Value |
|----------|-------|
| Name | WELL Biological Monitor |
| Public URL | `https://well.arif-fazil.com/mcp` |
| Transport | `streamable-http` |
| Internal | `http://127.0.0.1:18083/mcp` |
| Container port | 8083 (Docker default); live VPS uses 18083 |
| Caddy route | `well.arif-fazil.com/mcp` → `127.0.0.1:18083` |
| Tools | 22 live MCP tools |
| Auth | None (public) |
| Status | **HEALTHY** — verified by `/health` on 2026-07-01 |
| Note | REFLECT_ONLY substrate monitor. `well_system_registry_status` is deprecated; use `well_registry_status`. |

---

## Endpoint Configuration Map

| Service | openclaw.json url | Caddyfile route | server.py transport |
|---------|------------------|-----------------|-------------------|
| arifOS | `http://localhost:8088/mcp` | `mcp.arif-fazil.com/mcp*` | `streamable-http` |
| GEOX | `https://geox.arif-fazil.com/mcp` | `geox.arif-fazil.com/mcp/*` | `streamable-http` |
| WEALTH | `http://localhost:18082/mcp` | `wealth.arif-fazil.com/mcp` | `streamable-http` |
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
curl -s --max-time 5 https://mcp.arif-fazil.com/health
curl -s --max-time 5 https://geox.arif-fazil.com/health
curl -s --max-time 5 https://wealth.arif-fazil.com/health
curl -s --max-time 5 https://well.arif-fazil.com/health

# MCP tool discovery (after initialize)
curl -s --max-time 5 -X POST https://mcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'

# Federation runtime probe used for current tool counts
curl -fsS --max-time 20 https://arifos.arif-fazil.com/api/federation-probe | python3 -m json.tool
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
