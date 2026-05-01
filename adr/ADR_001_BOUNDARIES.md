# ADR-001: Repository Boundary Rules — Mind vs. Body Separation

**Status:** ACCEPTED
**Date:** 2026-04-30
**Architect:** Arif Fazil
**Decision Driver:** Red-team audit uncovered chaotic naming drift, multiple competing canonical roots, and legacy code cohabiting with active runtime.

---

## Context

The arifOS repository had accumulated at least three naming generations:
1. `arifos_*` public tools (old generation, pre-KANON)
2. `init_anchor`, `agi_mind`, `apex_soul` (intermediate internal naming)
3. `arif_session_init`, `arif_sense_observe`, etc. (current live public surface)

Plus malformed transitional names (`arifos_arifos_init`) in `tool_registry_v2.json`.

This created split-brain documentation where a new contributor could infer contradictory public APIs depending on which file they read first.

---

## Decision

**Option 2 (Monorepo with Hard Boundaries)** is adopted for operational continuity, with these strict rules:

### Rule 1: Top-Level Folder Governance
No new top-level directory without:
- An ADR entry (`/adr/ADR_XXX_*`)
- Update to `CANONICAL_PATHS.md`
- Update to `INDEX.md`

### Rule 2: Canonical Entrypoint Governance
Only these are allowed as runtime entrypoints:
- `python server.py` (HTTP / streamable-http)
- `python -m arifosmcp.runtime.server` (same as above)

STDIO transport was removed in KANON.

### Rule 3: Legacy Quarantine
Everything legacy goes to `/archive/` or `*/archive/legacy/` and becomes read-only. CI ignores it. Tests never import it.

### Rule 4: Public Surface Lock
The public MCP tool surface is frozen at 13 canonical `arif_*` names. Any new public tool requires:
- ADR approval
- Update to `tool_registry.json`
- Update to `PUBLIC_SURFACE_CANON.md`
- Schema test in `tests/test_public_tool_registry.py`

### Rule 5: Contracts-First Enforcement
Tool schema ↔ handler signature must match. CI must introspect `@mcp.tool()` decorators and compare to handler function signatures.

---

## Consequences

### Positive
- Unambiguous "where do I change X?" answers
- Legacy docs cannot confuse new contributors
- Registry files become machine-verifiable

### Negative
- One-time migration effort to move legacy files
- Need to maintain archive/ tombstones for audit trail

---

## Implementation

- [x] `CANONICAL_PATHS.md` created
- [x] `PUBLIC_SURFACE_CANON.md` created
- [x] Legacy docs moved to `arifosmcp/archive/legacy/`
- [x] Stale registry files moved to `arifosmcp/archive/legacy/`
- [ ] Add CI test: verify `tool_registry.json` aligns with `runtime/tools.py` handlers
- [ ] Add CI test: verify no `arifos_*` names appear in public discovery

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
