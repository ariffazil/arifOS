---
type: Synthesis
tier: 50_AUDITS
strand:
- operations
audience:
- engineers
difficulty: intermediate
prerequisites:
- Tool_Surface_Architecture
tags:
- audit
- checker
- ci
- drift
- tooling
- governance
sources:
- check_tool_surface_drift.py
- tool_specs.py
- MCP_Tools.md
- Tool_Surface_Architecture.md
last_sync: '2026-04-10'
confidence: 0.97
---

# Drift Checks

## Checker

- Script: `scripts/check_tool_surface_drift.py`
- Purpose: detect divergence between canonical tool contract and outward surfaces
- Exit behavior: non-zero on drift
- Current verdict: **GREEN**

## What It Verifies

1. Canonical tool count from `arifosmcp/runtime/tool_specs.py`
2. Canonical tool ids from `tool_specs.py`
3. Full-surface inventories in:
   - `arifosmcp/runtime/tools.py`
   - `arifosmcp/runtime/__main__.py`
   - `arifosmcp/runtime/tools_hardened_dispatch.py`
   - `arifosmcp/runtime/resources.py`
   - `arifosmcp/tool_registry.json`
   - `wiki/pages/MCP_Tools.md`
   - `wiki/pages/Tool_Surface_Architecture.md`
4. Count hints in `arifosmcp/runtime/public_registry.py`
5. Dotted-name leakage outside approved compatibility files
6. Deprecated alias usage, reported separately

## Approved Compatibility Files

- `arifosmcp/runtime/tool_specs.py`
- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `arifosmcp/runtime/megaTools/__init__.py`
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`

## Usage

```bash
python scripts/check_tool_surface_drift.py
```

## Live Result

```text
== Verdict ==
NO DRIFT DETECTED
```

Generated target surfaces currently aligned:

- `arifosmcp/tool_registry.json`
- `arifosmcp/runtime/public_registry.py`
- `arifosmcp/runtime/resources.py`
- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `wiki/pages/MCP_Tools.md`
- `wiki/pages/Tool_Surface_Architecture.md`

## CI Recommendation

Run the checker in pull requests before any merge that touches:

- `arifosmcp/runtime/`
- `arifosmcp/tool_registry.json`
- `wiki/pages/MCP_Tools.md`
- `wiki/pages/Tool_Surface_Architecture.md`

## 888_HOLD

Green checker does **not** authorize destructive cleanup by itself.

Still held:

- collapsing compatibility surfaces
- deleting dotted-name adapters
- archive relocation or mega-tool namespace removal

Those changes should follow only after generation is extended and downstream compatibility usage is confirmed.
