# HISTORICAL NOTICE — arifOS Tool Naming Eras

> **Created:** 2026-09-10 by FI-008 (kimi-code) — fixes broken reference from
> `docs/architecture/ARIFOS_TOOL_AUDIT_REPORT.md` (banner linked here; file was missing).

## Why this notice exists

Documents written before the **33/13 ZEN surface refactor (2026-08-08, commit 0174ec8af)**
reference long-form tool names (`arif_session_init`, `arif_sense_observe`, `arif_judge_deliberate`,
`arif_vault_seal`, `arif_reply_compose`, …). Those names were correct at time of writing.
They are **historical**, not current.

## Current truth (as of 2026-09-10)

- **Live MCP wire surface: 8 canonical verbs** — `arif_init, arif_observe, arif_think, arif_route, arif_memory, arif_judge, arif_forge, arif_seal` (verified by `scripts/mcp_surface_truth_test.py`, wire layer).
- **Full registry: `arifosmcp/constitutional_map.py`** — 25 canonical specs + 40 diagnostic specs. Declared ≠ served; truth test verdict **FAIL** on this gap (known, queued for reconciliation).
- **Legacy-name tolerance: `TOOL_ALIAS_MAP`** in `scripts/arifosd.py` maps most long-form names to canonical verbs. Known gap: `arif_session_init` is not aliased yet.
- **Governed SOT for the served surface: `tools_sot.yaml`** (8 = 8, drift-free per `forge_surface_audit`).

## Rule for readers

If a document names an `arif_*` tool that is not one of the 8 canonical verbs, treat the name as
historical vocabulary unless it appears in `constitutional_map.py` AND on the live wire surface.
When in doubt: `python3 scripts/mcp_surface_truth_test.py`.

DITEMPA BUKAN DIBERI ⚒️
