---
atlas_class: 400
tier: core33
source_type: spec
authority: standard
why_in_kernel: "Language-agnostic HTTP API description format. arifOS uses it for `/health`, `/openapi.json`, and FastMCP's REST surface; AAA's a2a-server exposes OpenAPI for browser debugging."
freshness_policy: release-tracked
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# OpenAPI Specification (3.x)

**Citation:** OpenAPI Initiative (Linux Foundation). *OpenAPI Specification* v3.0 / v3.1. https://spec.openapis.org/oas/latest.html

## Why in kernel

OpenAPI is the **HTTP API description format** — the contract between an HTTP service and its clients. arifOS exposes OpenAPI on `GET /openapi.json` (alongside MCP at `POST /mcp`):

- `/health` is documented in OpenAPI for browser-based probing.
- `/openapi.json` returns the full schema for the REST surface.
- `/resources/list` is documented (though currently broken — see B's watchpoint).

For ATLAS333:

- **Tool discovery** — `GET /openapi.json` lists every REST endpoint, equivalent to MCP's `tools/list`.
- **Schema validation** — OpenAPI 3.1 is JSON Schema compatible; the same schemas validate both REST and MCP payloads.
- **Documentation generation** — Swagger UI / Redoc can render OpenAPI for human consumers.

## ATLAS333 activation

- **Zone:** VI — SYSTEM
- **Floors:** F2 (deterministic contract), F4 (clarity), F11 (auditable)
- **Quote sites:** J1–J5

## How to use

When designing a new REST surface in arifOS, write the OpenAPI spec first. When debugging an HTTP call, curl `/openapi.json` to see the canonical shape.

When a paradox between **HTTP and MCP** appears (Zone VI), invoke OpenAPI as the bridge — MCP transport is often HTTP+JSON-RPC, and OpenAPI documents it.

## Pair with

- `01-mcp-spec.md` — MCP can ride over HTTP+JSON-RPC, which OpenAPI documents
- `04-json-rpc-2.md` — JSON-RPC payloads can be validated against OpenAPI schemas
- `06-json-schema.md` — OpenAPI 3.1 uses JSON Schema 2020-12

## Cross-references

- `arifOS/arifosmcp/server.py` — FastMCP generates OpenAPI for the REST surface
- `AAA/a2a-server/` — uses OpenAPI for A2A agent card discovery

## Scar links

_None yet._

## Vault anchor

_None yet._