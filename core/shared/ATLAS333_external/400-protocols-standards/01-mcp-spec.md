---
atlas_class: 400
tier: core33
source_type: spec
authority: official
why_in_kernel: "Defines the JSON-RPC substrate that lets agents reach tools, data, and prompts through a uniform interface. arifOS implements FastMCP 3.x; arifOS resources (including the 14 ATLAS333 entries) live on this protocol."
freshness_policy: release-tracked
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# MCP — Model Context Protocol Specification

**Citation:** Anthropic + community. *Model Context Protocol* specification. https://modelcontextprotocol.io

**Versions:** 2024-11-05, 2025-03-26, 2025-11-25 (arifOS runs 2025-11-25 per `/health`).

## Why in kernel

MCP is the substrate that every tool, resource, and prompt in arifOS rides on. Without it, there is no federation-wide contract for what an agent can call. The atlas333.py resource module that just went live (14 resources on `arifos://atlas333/...`) is itself an MCP server exposing read-only Resources — the exact pattern MCP was designed to enable.

For ATLAS333 the protocol matters in four places:

1. **Tools** — model-controlled calls (e.g., `arif_judge`, `paradox_gate`). MCP's tool/resource/prompt triad is the surface model.
2. **Resources** — application-controlled reads (e.g., `arifos://atlas333/thresholds`). Read-only by design (F8: no resource/tool confusion).
3. **Prompts** — user-controlled templates. (Not yet wired in arifOS; reserved.)
4. **JSON-RPC 2.0** — the wire format. ATLAS333 resources are read via `POST /mcp` with `method: "resources/read"` payloads.

## ATLAS333 activation

- **Zone:** VI — SYSTEM (paradox axes 26–30)
- **Floors:** F2 (deterministic), F4 (structured), F11 (every call auditable)
- **Quote sites:** J1–J5 (Judge organ)

## Key concepts

| Concept | Definition | ATLAS333 mapping |
|---|---|---|
| **Host** | LLM application that consumes MCP | arifOS kernel, Claude Code, Cursor, custom agents |
| **Client** | 1:1 connector inside the host | arifOS MCP client (per-organ client) |
| **Server** | Exposes tools/resources/prompts | arifOS MCP server (`server.py:5` FastMCP 3.2.0) |
| **Tool** | Model-controlled, has side effects | `arif_judge`, `forge_execute`, `paradox_gate_evaluate` |
| **Resource** | App-controlled, read-only, addressed by URI | `arifos://atlas333/*`, `arifos://doctrine`, `arifos://trinity`, … |
| **Prompt** | User-controlled template | (reserved — not wired in arifOS yet) |

## How to use

When an agent wants to know "what's available?", it calls `resources/list`. When it wants a specific datum, it calls `resources/read` with a URI. When it wants to invoke an action, it calls `tools/call`. The triad is the surface model; do not collapse it.

When a paradox between **observability and execution** appears (Zone VI), invoke MCP — it explicitly separates Resources (observability) from Tools (execution) to prevent the collapse.

## Pair with

- `04-json-rpc-2.md` — wire format
- `02-mcp-github-org.md` — official SDKs and reference servers
- `03-a2a-spec.md` — orthogonal horizontal protocol (agent ↔ agent, not agent ↔ tool)

## Cross-references

- `arifOS/arifosmcp/server.py:5` — FastMCP 3.2.0 + MCP Apps + Streamable HTTP
- `arifOS/arifosmcp/resources/__init__.py` — 49 MCP resources registered
- `arifOS/arifosmcp/resources/atlas333.py` — 14 ATLAS333 resources (just refactored + deployed)
- `paradox_gate.py:281` — `evaluate_paradox_gate_gpv()` exposes an MCP tool surface

## Scar links

_None yet._

## Vault anchor

_None yet._