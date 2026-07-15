---
atlas_class: 400
tier: core33
source_type: spec
authority: standard
why_in_kernel: "Schema spine for structured outputs and contract validation. ATLAS333 resource payloads validate against JSON Schemas; paradox_quotes.py Pydantic models and arifOS FloorScores are JSON Schema-compatible."
freshness_policy: release-tracked
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# JSON Schema

**Citation:** OpenJS Foundation + community. *JSON Schema* specification. https://json-schema.org

**Current:** Draft 2020-12 (the version OpenAPI 3.1 adopts). Older drafts 04, 06, 07 still in use.

## Why in kernel

JSON Schema is the **schema spine** for the federation. Every structured payload — ATLAS333 resource responses, MCP tool arguments, A2A Agent Cards, paradox_quotes.py Pydantic models — can be validated against a JSON Schema.

For ATLAS333 specifically:

- The 14 `arifos://atlas333/*` resources return JSON; clients can validate against a published schema.
- `paradox_quotes.py` `ParadoxQuote` dataclass maps cleanly to a JSON Schema (Pydantic v2 emits JSON Schema automatically).
- `core/shared/types.py` `FloorScores`, `GPV`, `Verdict` Pydantic models are JSON Schema-compatible.

The discipline: **every ATLAS333 resource should have a JSON Schema declaration.** Without it, the data is prose; with it, the data is a contract.

## ATLAS333 activation

- **Zone:** VI — SYSTEM
- **Floors:** F2 (deterministic), F4 (clarity), F8 (production-grade contracts)
- **Quote sites:** J1–J5

## How to use

When designing a new ATLAS333 resource, generate the JSON Schema from the Python type (Pydantic v2 `.model_json_schema()`) and publish it alongside the URI. When validating an incoming MCP payload, use the same schema to reject malformed calls.

When a paradox between **strict typing and flexible parsing** appears (Zone VI), invoke JSON Schema — schemas can be additive (additionalProperties allowed) or strict (no extras), matching the discipline level needed.

## Pair with

- `05-openapi.md` — OpenAPI 3.1 embeds JSON Schema 2020-12
- `01-mcp-spec.md` — MCP tool `inputSchema` is JSON Schema
- `paradox_quotes.py` — Pydantic dataclass → JSON Schema

## Cross-references

- `arifOS/arifosmcp/constitution/paradox_quotes.py` — Pydantic dataclasses, JSON Schema compatible
- `arifOS/core/shared/types.py` — `FloorScores`, `GPV`, `Verdict` are Pydantic models
- `arifOS/arifosmcp/resources/atlas333.py` — every resource returns JSON; could publish schemas

## Scar links

_None yet._

## Vault anchor

_None yet._