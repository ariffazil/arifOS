---
atlas_class: 400
tier: core33
source_type: spec
authority: official
why_in_kernel: "Wire format for MCP and A2A — every ATLAS333 resource read and every federated tool call uses JSON-RPC 2.0 framing. Stateless, lightweight, language-agnostic."
freshness_policy: static
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# JSON-RPC 2.0 Specification

**Citation:** JSON-RPC Working Group. *JSON-RPC 2.0 Specification*. https://www.jsonrpc.org/specification

## Why in kernel

JSON-RPC 2.0 is the **wire format** that MCP and A2A both build on. Every ATLAS333 resource read is a `POST /mcp` with a JSON-RPC envelope:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/read",
  "params": {"uri": "arifos://atlas333/thresholds"}
}
```

Every federated tool call is similar:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {"name": "arif_judge", "arguments": {"intent": "..."}}
}
```

The properties ATLAS333 relies on:

- **Stateless** — each request is independent; the server holds no session state in the request itself.
- **Lightweight** — single JSON object, ~200 bytes typical; cheap to log (F11).
- **Language-agnostic** — works from Python (arifOS, GEOX, WEALTH, WELL), TypeScript (AAA, A-FORGE), Go (sibling services).
- **Batch support** — `jsonrpc:[…]` array for fan-out; ATLAS333 could expose `paradox/{id}, quote/{id}` reads as batch when an agent needs many.

## ATLAS333 activation

- **Zone:** VI — SYSTEM
- **Floors:** F2 (deterministic envelope), F11 (every call auditable via the JSON envelope), F12 (sanitized inputs)
- **Quote sites:** J1–J5

## How to use

When calling any MCP or A2A endpoint, frame the request as JSON-RPC 2.0. When debugging, the JSON-RPC `error.code` + `error.message` fields are the canonical failure surface.

When a paradox between **stateless simplicity and stateful richness** appears (Zone VI: order vs. power), invoke JSON-RPC's discipline — every call is independent, every response is self-contained, no implicit session.

## Pair with

- `01-mcp-spec.md` — uses JSON-RPC 2.0 as wire format
- `03-a2a-spec.md` — uses JSON-RPC 2.0 for A2A messages
- `06-json-schema.md` — JSON-RPC `params` typically validate against a JSON Schema

## Cross-references

- `arifOS/arifosmcp/server.py:374` — `mcp.server.streamable_http.StreamableHTTPServerTransport` uses JSON-RPC framing
- `arifOS/arifosmcp/resources/atlas333.py` — every `@mcp.resource` handler returns JSON strings (JSON-RPC compatible)

## Scar links

_None yet._

## Vault anchor

_None yet._