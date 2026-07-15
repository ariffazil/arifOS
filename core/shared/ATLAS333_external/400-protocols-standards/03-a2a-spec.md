---
atlas_class: 400
tier: core33
source_type: spec
authority: official
why_in_kernel: "Defines how independent, opaque agents discover each other and collaborate on tasks. Orthogonal to MCP (which is agent↔tool); A2A is agent↔agent. arifOS participates via AAA's a2a-server bridge."
freshness_policy: release-tracked
paradox_zone: "III-AGENT"
scar_link: []
vault_anchor: null
---

# A2A — Agent2Agent Protocol Specification

**Citation:** Google + 50+ partners. *Agent2Agent Protocol* specification. https://github.com/a2a-protocol/a2a (Linux Foundation project since June 2025).

## Why in kernel

A2A is the **horizontal** protocol — agent ↔ agent. It is the complement to MCP's **vertical** protocol — agent ↔ tool/data. The two together form the substrate of multi-agent systems.

For ATLAS333:

1. **Discovery** — A2A defines an Agent Card (`agent-card.json`) schema that advertises capabilities, skills, modalities, and security requirements. arifOS could publish an Agent Card declaring "I serve ATLAS333 cognitive substrate" so A2A clients (Gemini Agent, future Google agents) can discover and call it.
2. **Task lifecycle** — A2A defines `message/send`, `tasks/get`, `tasks/cancel` for collaborating agents. arifOS organs already coordinate via NATS, but A2A is the cross-vendor surface.
3. **Modal negotiation** — A2A agents negotiate modality (text, file, structured data) per task. ATLAS333 resources are JSON, which is universally supported.

The arifOS federation currently bridges A2A via `/root/AAA/a2a-server/a2a-mcp-bridge.js` — this is the seam where A2A clients reach arifOS MCP resources.

## ATLAS333 activation

- **Zone:** III — AGENT (paradox axes 11–15)
- **Floors:** F3 (witness between agents), F5 (peace² across boundaries), F10 (ontology across vendors)
- **Quote sites:** R1–R11 (Mind organ)

## Key concepts

| Concept | Definition | ATLAS333 mapping |
|---|---|---|
| **Agent Card** | JSON manifest at `/.well-known/agent.json` | Future: arifOS Agent Card could declare ATLAS333 resources |
| **Skill** | Capability advertised in the card | Each ATLAS333 resource is a potential skill declaration |
| **Task** | Unit of work between agents | A `resources/read` call wrapped as an A2A task |
| **Message** | A2A protocol payload | Wraps MCP JSON-RPC |
| **Artifact** | Output produced by a task | A JSON resource payload |

## How to use

When designing a cross-organ task (e.g., "WEALTH computes NPV, GEOX validates prospect, WELL checks operator readiness"), think A2A first — each organ is an independent agent with its own MCP server; A2A is the bus.

When a paradox between **autonomy and coordination** appears (Zone III), invoke A2A — it gives agents a way to collaborate without losing independence.

## Pair with

- `01-mcp-spec.md` — vertical complement
- `02-mcp-github-org.md` — cross-vendor tooling
- `AAA/a2a-server/` — arifOS A2A bridge implementation

## Cross-references

- `/root/AAA/a2a-server/a2a-mcp-bridge.js` — A2A↔MCP translation
- `/root/AAA/a2a-server/agent-cards/` — federation Agent Cards
- `/root/AAA/a2a-server/a2a-part-types.js` — A2A message/artifact types

## Scar links

_None yet._

## Vault anchor

_None yet._