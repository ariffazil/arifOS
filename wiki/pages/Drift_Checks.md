---
type: Synthesis
tags: [audit, checker, ci, drift, tooling, governance]
sources: [check_tool_surface_drift.py, tool_specs.py, MCP_Tools.md, Tool_Surface_Architecture.md]
last_sync: 2026-04-08
confidence: 0.95
---

# Drift Checks

## Checker

- Script: `scripts/check_tool_surface_drift.py`
- Purpose: detect divergence between canonical tool contract and outward surfaces
- Exit behavior: non-zero on drift

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
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`

## Usage

```bash
python scripts/check_tool_surface_drift.py

```

## Current Expected Failures

As of this audit:

- `tool_registry.json` is still 10-tool dotted surface
- `public_registry.py` still expects 10
- `tools_hardened_dispatch.py` still omits `arifos_vps_monitor` from `list_canonical_tools()`
- dotted-name leakage exists outside compatibility files

## CI Recommendation

Run the checker in pull requests before any merge that touches:

- `arifosmcp/runtime/`
- `arifosmcp/tool_registry.json`
- `wiki/pages/MCP_Tools.md`
- `wiki/pages/Tool_Surface_Architecture.md`

## 888_HOLD

The checker is intentionally audit-first. It should fail loudly before any destructive cleanup or alias removal is attempted.
