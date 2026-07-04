# arifosmcp — Runtime Shell for arifOS

`arifosmcp/` is the **live MCP runtime package** inside this repository. It is the packaging and server layer for the arifOS constitutional kernel; it is **not** a separate public doctrine surface.

## Current truth

- Public MCP wire surface: **exactly 7 verbs**
  - `arif_init`
  - `arif_observe`
  - `arif_think`
  - `arif_route`
  - `arif_judge`
  - `arif_act`
  - `arif_seal`
- Canonical public endpoint: `https://mcp.arif-fazil.com/mcp`
- Canonical local runtime entrypoint: `uv run python -m arifosmcp.runtime.server`
- Packaged server authority: `arifosmcp.server`

## Source of truth order

When docs or manifests disagree, trust these first:

1. `arifosmcp/runtime/public_surface.py`
2. `arifosmcp/tool_registry.json`
3. `static/.well-known/mcp/server.json`
4. public lock tests such as `tests/test_public_registry.py` and `tests/test_public_tool_registry.py`

`arifosmcp/constitutional_map.py` is still the broader internal spec source, but the files above are the public-surface chain agents and operators should compare first.

## What lives here

- `server.py` and `runtime/server.py` — packaged and local runtime entrypoints
- `runtime/tools.py` — handler implementations and execution gates
- `runtime/public_registry.py` — machine-readable public discovery payloads
- `runtime/public_surface.py` — the 7-verb public facade
- `runtime/` bridges, leases, memory, and health/reporting infrastructure

## What this package does not mean

- Internal tools are **not** the same thing as the default public MCP surface.
- Legacy aliases may still route internally, but they are not part of `tools/list` in canonical mode.
- Older references to 13/15/16/21 public tools are historical unless they are explicitly marked as compatibility or archive material.

## Where to read next

- Root repo overview: [`../README.md`](../README.md)
- Agent/runtime operating constraints: [`../AGENTS.md`](../AGENTS.md)
- Public facade canon: [`PUBLIC_SURFACE_CANON.md`](PUBLIC_SURFACE_CANON.md)
- Live server card: [`../static/.well-known/mcp/server.json`](../static/.well-known/mcp/server.json)

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
