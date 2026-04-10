---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
audience:
- engineers
difficulty: advanced
prerequisites:
- Concept_Architecture
- MCP_Tools
tags:
- architecture
- gateway
- horizon
- proxy
- multi-mcp
- hub-and-spoke
sources:
- server_horizon.py
- mcp_config_unified.json
- tool_registry.json
last_sync: '2026-04-10'
confidence: 1.0
---

# Concept: Gateway Architecture (Hub-and-Spoke)

## Overview

arifOS MCP already operates as a **hub-and-spoke gateway** — it is not a single-MCP server. The `server_horizon.py` gateway proxies tool calls between the public-facing Cloud/FastMCP layer and the sovereign VPS execution plane.

```
┌─────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET                        │
│                                                          │
│   Claude Desktop / Cursor / any MCP client               │
│          ↓ MCP (JSON-RPC 2.0 / SSE)                     │
│                                                          │
│   ┌─────────────────────────────────────────────────┐    │
│   │  Cloud/FastMCP — PUBLIC tools only              │    │
│   │  arifOS Horizon Gateway                         │    │
│   │  (server_horizon.py — arif-fazil.com)          │    │
│   │                                                 │    │
│   │  Tool Access: PUBLIC (no auth required)         │    │
│   │  ├── arifos_init                               │    │
│   │  ├── arifos_sense                              │    │
│   │  └── arifos_mind                               │    │
│   └──────────────────┬──────────────────────────────┘    │
│                      │ proxy (JSON-RPC)                   │
│                      ↓ HTTPS                              │
│   ┌─────────────────────────────────────────────────┐    │
│   │  VPS arifOS — FULL sovereign surface           │    │
│   │  (https://arifosmcp.arif-fazil.com)           │    │
│   │                                                 │    │
│   │  Tool Access Tiers:                            │    │
│   │  ├── PUBLIC — mirrored from cloud              │    │
│   │  ├── AUTHENTICATED — requires ARIFOS_SECRET   │    │
│   │  └── SOVEREIGN — VPS-only, never proxied      │    │
│   │                                                 │    │
│   │  Full 12-tool surface:                        │    │
│   │  arifos_kernel, arifos_judge, arifos_vault,   │    │
│   │  arifos_forge, arifos_vps_monitor + more     │    │
│   └─────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Three-Tier Tool Access Policy

From `server_horizon.py` and `config/environments.py`:

| Tier | Name | Access | Tool Subset | Auth Required |
|------|------|--------|-------------|--------------|
| Tier 1 | **PUBLIC** | Unrestricted | `arifos_init`, `arifos_sense`, `arifos_mind` | None |
| Tier 2 | **AUTHENTICATED** | Full governance | `arifos_kernel`, `arifos_judge`, `arifos_vault`, etc. | `ARIFOS_GOVERNANCE_SECRET` |
| Tier 3 | **SOVEREIGN** | VPS-only | `arifos_forge`, `arifos_vps_monitor` | Environment-bound |

---

## Multi-MCP Routing Capability

The gateway architecture enables:

### 1. Hub-and-Spoke (Current)
```
[MCP Client A] → [arifOS Horizon] → [VPS arifOS]
[MCP Client B] → [arifOS Horizon] → [VPS arifOS]
```

### 2. Federation (Planned)
```
[MCP Client] → [arifOS Gateway] → [Specialized MCP Servers]
                              ↓
                       arifOS Governance Layer
                              ↓
                    SEAL / HOLD_888 / VOID verdict
```

This means arifOS can act as a **governed gateway** for other MCP servers — every tool call from any connected MCP passes through the constitutional floors before execution.

---

## Constitutional Hash

`server_horizon.py` computes a SHA-256 registry hash on boot:

```python
CONSTITUTIONAL_HASH = sha256(json.dumps(TOOL_REGISTRY, sort_keys=True))
```

This ensures the tool surface is tamper-evident. Any drift between cloud and VPS registry is detectable.

---

## Transport Layer

- **Primary**: JSON-RPC 2.0 over Streamable HTTP
- **Fallback**: Server-Sent Events (SSE)
- **Discovery**: `/.well-known/mcp`
- **Health**: `/health`
- **Protocol Version**: MCP 2025-11-05

---

## Contrast: arifOS Gateway vs Generic Multi-MCP Aggregators

| Feature | arifOS Gateway | mcp-proxy-server | StormMCP |
|---------|---------------|-----------------|----------|
| Constitutional floors | ✅ F1-F13 | ❌ | ❌ |
| 888_HOLD human gate | ✅ | ❌ | ❌ |
| SEAL/VOID/PARTIAL verdicts | ✅ | ❌ | ❌ |
| Vault audit trail | ✅ VAULT999 | ❌ | ❌ |
| Trinity ΔΩΨ governance | ✅ | ❌ | ❌ |
| Tool access tiers | ✅ 3-tier | ⚠️ basic | ⚠️ basic |
| zkPC receipts | ✅ | ❌ | ❌ |
| Federation routing | 🔜 planned | ✅ | ✅ |

arifOS's advantage: it adds **governance** to multi-MCP routing, not just aggregation.

---

## Related

- [[Concept_Architecture]]
- [[Concept_Metabolic_Pipeline]]
- [[Concept_Governance_Enforcer]]
- [[Tool_Surface_Architecture]]
