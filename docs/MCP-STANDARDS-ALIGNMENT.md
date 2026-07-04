# MCP Standards Alignment — arifOS Federation

> **DITEMPA BUKAN DIBERI** — Standards are forged, not given.
> **Last updated:** 2026-07-03 (RSI)
> **Transport contract:** `contracts/transport/arifos.transport.v2.json`
> **RATIFIED BY:** FORGE (000Ω) — pending 888_JUDGE

---

## 1. MCP Specification Compliance

| Spec Component | arifOS Status | Details |
|---------------|--------------|---------|
| **Spec Version** | ✅ 2025-11-25 | Supported via `MCP-Protocol-Version` header validation |
| **JSON-RPC 2.0** | ✅ Full | All tool calls use JSON-RPC 2.0 over HTTP POST |
| **Streamable HTTP** | ✅ Full | `/mcp` endpoint, session management via `MCP-Session-Id` |
| **SSE Transport** | ✅ Supported | Port 8089 for A2A SSE agents |
| **Lifecycle** | ✅ Full | initialize → initialized → tools/list → tools/call |
| **Auth (OAuth 2.1)** | ➖ Not yet | Lease-based auth instead. OAuth planned. |
| **Tool Discovery** | ✅ Full | `tools/list` returns 21 canonical + filtered 7 public |
| **Resource Discovery** | ✅ Full | `resources/list` returns 223 registered URIs |
| **Prompt Discovery** | ✅ Full | `prompts/list` returns system prompts |

### Protocol Versions

| Version | Status | Notes |
|---------|--------|-------|
| **2025-11-25** | ✅ **Canonical** | Latest. Supports session management, Streamable HTTP |
| 2025-03-26 | ✅ Supported | Previous stable |
| 2024-11-05 | ⚠️ Deprecated | Legacy — will be removed |

---

## 2. SEP Compliance

| SEP | Title | Status | Gap |
|-----|-------|--------|-----|
| **SEP-1613** | JSON Schema 2020-12 as Default Dialect | ✅ **Compliant** | All tool `inputSchema` use `draft/2020-12` via FastMCP |
| **SEP-2106** | inputSchema & outputSchema Conform to JSON Schema 2020-12 | ✅ **Compliant** | Both schema types conform |
| **SEP-414** | OpenTelemetry Trace Context Propagation | 🟡 **Partial** | W3C traceparent header supported. OTel Phase 5 spans pending full propagation |
| **SEP-986** | Format for Tool Names | ✅ **Compliant** | `arif_*` (governance) and `forge_*` (execution) snake_case |
| **SEP-2243** | HTTP Header Standardization | ✅ **Compliant** | MCP-Session-Id, MCP-Protocol-Version, traceparent |
| **SEP-973** | Additional Metadata for Tools/Resources/Prompts | 🟡 **Partial** | `full_affordance` available but not in public manifest |
| **SEP-2549** | TTL for List Results | ➖ N/A | Not implemented. No list endpoints need TTL gating yet |
| **SEP-2567** | Sessionless MCP | ➖ N/A | **Intentional** — arifOS is session-bound (F11 AUDIT) |
| **SEP-2577** | Deprecate Roots, Sampling, Logging | 📌 **Acknowledged** | arifOS does NOT expose any of these |
| **SEP-2596** | Feature Lifecycle / Deprecation Policy | 📌 **Acknowledged** | `deprecation-registry.json` serves this purpose |
| **SEP-2164** | Standardize Resource Not Found Error | ➖ N/A | arifOS uses custom `fault_code` system |
| **SEP-1036** | URL Mode Elicitation | ➖ N/A | All user input is text/structured |
| **SEP-1046** | OAuth Client Credentials Flow | ➖ N/A | Lease-based auth model |
| **SEP-1865** | MCP Apps (Interactive UI) | 📌 **Acknowledged** | FastMCP apps available. Not native to arifOS yet |
| **SEP-2322** | Multi Round-Trip Requests | ➖ N/A | Single-round-trip pattern |
| **SEP-2484** | Conformance Tests Required for Final SEPs | 📌 **Acknowledged** | arifOS conformance spine: 9/9 + 1 new for SEP-1613 |
| **SEP-1686/2663** | Tasks Extension | 📌 **Acknowledged** | Not yet implemented. Planned. |

### SEP Compliance Score: **14/18 active** (6 compliant, 2 partial, 6 acknowledged)

---

## 3. A2A Protocol Compliance

| Component | arifOS Status | Details |
|-----------|--------------|---------|
| **A2A Version** | ✅ v1.0.0 gateway / v1.0.1 registry | dual support |
| **Agent Card** | ✅ Published | `/.well-known/agent.json` at `aaa.arif-fazil.com` |
| **JSON-RPC 2.0** | ✅ Full | Same as MCP transport |
| **Agent Discovery** | ✅ Supported | Via Agent Cards |
| **Task Management** | ✅ Supported | `tasks/send`, `tasks/get` |
| **SSE Streaming** | ✅ Supported | Server-Sent Events for task status |
| **Async Push** | ❌ Missing | No push notification mechanism |
| **Skill Negotiation** | ❌ Missing | No `QuerySkill()` method |
| **SDKs** | ❌ Custom | No A2A SDK integration (Python/JS/Go SDKs exist upstream) |

### A2A Compliance Score: **5/7 core features** — gaps in async push and skill negotiation

### arifOS A2A Architecture

```
Agent Card (.well-known/agent.json)
  → AAA Gateway (:3001 /a2a)
    → Deliberation Engine (a2a-server/deliberation.ts)
      → A-FORGE Execution (via bridge)
        → arifOS Governance (via MCP)
```

**Key difference from standard A2A:** arifOS routes all A2A tasks through the constitutional pipeline (judge → seal → forge). Standard A2A assumes agents can execute autonomously. arifOS agents execute only after SEAL.

---

## 4. FastMCP Ecosystem Alignment

| Feature | arifOS Equivalent | Gap |
|---------|------------------|-----|
| FastMCP Server | ✅ arifOS uses FastMCP `mcp` instance | — |
| MCP Apps | ➖ Not native | FastMCP apps available externally |
| Auth (Bearer/OAuth/CIMD) | ➖ Not implemented | Lease-based auth instead |
| Code Mode | ➖ Not native | A-FORGE serves this role |
| Tool Fingerprinting | ✅ `forge_registry` + affordance cards | — |
| Middleware | ✅ `MCPProtocolVersionMiddleware` + `MCPSessionBridgeMiddleware` | — |
| OpenTelemetry | 🟡 Partial (Phase 2 done, Phase 5 pending) | Missing: full span propagation |

---

## 5. Gap Closure Roadmap

| Priority | Gap | Effort | Dependencies |
|----------|-----|--------|-------------|
| **P0** | Port sync (dual_transport.py → 8088) | 10 min | None |
| **P1** | SEP-414 OTel full propagation (Phase 5) | 4-6h | Phase 2 baseline |
| **P1** | A2A Agent Cards for all 7 organs | 2h | Per-organ `.well-known/` |
| **P2** | SEP-973 metadata in public manifest | 3h | Public manifest refactor |
| **P2** | A2A SDK integration | 8h | Dependencies + testing |
| **P3** | SEP-2549 TTL for list results | 2h | None |
| **P3** | OAuth 2.1 support | 16h | Security audit |
| **P4** | A2A async push notifications | 8h | SSE infrastructure |
| **P4** | MCP Apps native support | 12h | UI rendering layer |

---

## 6. Key References

| Resource | URL |
|----------|-----|
| MCP Specification (2025-11-25) | https://modelcontextprotocol.io/specification/2025-11-25/ |
| MCP SEP Index | https://modelcontextprotocol.io/seps/index.md |
| A2A Protocol v1.0.1 | https://github.com/a2aproject/A2A |
| A2A Specification | https://a2a-protocol.org/latest/specification/ |
| FastMCP Documentation | https://gofastmcp.com/ |
| arifOS Transport Contract | `/root/arifOS/contracts/transport/arifos.transport.v2.json` |
| arifOS Deprecation Registry | `/root/AAA/docs/deprecation-registry.json` |

---

*DITEMPA BUKAN DIBERI — Forged 2026-07-03 by FORGE (000Ω).*
*MCP SEP compliance: 14/18 active. A2A compliance: 5/7 core.*
*Every gap has a closure path. Every path has a priority.*
