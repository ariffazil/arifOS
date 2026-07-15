---
atlas_class: 400
tier: core33
source_type: repo
authority: official
why_in_kernel: "Canonical SDKs (TypeScript, Python, Java, Go, Rust, Swift, Kotlin, C#, Ruby, PHP) and reference server implementations. arifOS uses the Python SDK via FastMCP."
freshness_policy: release-tracked
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# modelcontextprotocol — Official GitHub organization

**Citation:** modelcontextprotocol GitHub org. https://github.com/modelcontextprotocol

## Why in kernel

The official org hosts the protocol specification, the type definitions, the SDKs, and a curated set of reference servers. For ATLAS333, the Python SDK is the load-bearing piece: arifOS implements MCP via `fastmcp` (a higher-level Pythonic wrapper over the official SDK).

When a paradox between **specification drift and implementation lock-in** appears (Zone VI), this org is the upstream source of truth — follow it before trusting any third-party MCP library's claims about conformance.

## Key repos

| Repo | Role | ATLAS333 relevance |
|---|---|---|
| `modelcontextprotocol/python-sdk` | Official Python SDK | arifOS uses it indirectly via FastMCP |
| `modelcontextprotocol/typescript-sdk` | Official TypeScript SDK | OpenCode, AAA's `a2a-mcp-bridge.js` use it |
| `modelcontextprotocol/specification` | The spec source of truth | ATLAS333 resource module follows it for JSON-RPC framing |
| `modelcontextprotocol/servers` | Curated reference servers (filesystem, git, postgres, …) | Pattern reference for arifOS resource modules |
| `modelcontextprotocol/registry` | Community MCP server registry | Federation discovery (future: surface arifOS here) |
| `modelcontextprotocol/inspector` | Dev tool for testing MCP servers | Used by arifOS resource testing |

## ATLAS333 activation

- **Zone:** VI — SYSTEM
- **Floors:** F2 (specification rigor), F4 (clear separation), F8 (production-grade reference)
- **Quote sites:** J1–J5

## How to use

When evaluating "should we add another MCP surface?" — check the upstream org first. The pattern is usually already there. When the spec or SDK changes, this org is the canonical notification point.

When a paradox between **speed of adoption and spec stability** appears (Zone VI: order vs. progress), invoke the upstream versioning discipline.

## Pair with

- `01-mcp-spec.md` — protocol itself
- `04-json-rpc-2.md` — wire format the SDKs implement
- `400-protocols-standards/06-json-schema.md` — schemas the SDKs use for validation

## Cross-references

- `arifOS/arifosmcp/runtime/skills_contracts_resource.py` — uses FastMCP pattern, mirrors upstream examples
- `arifOS/arifosmcp/runtime/fastmcp_ext/` — local FastMCP extensions (resources.py, discovery.py)
- `AAA/a2a-server/a2a-mcp-bridge.js` — uses TypeScript SDK for A2A↔MCP translation

## Scar links

_None yet._

## Vault anchor

_None yet._