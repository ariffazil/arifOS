# REPO_CONSTITUTION.md — arifOS Codebase Governance Rules

> **DITEMPA BUKAN DIBERI** — Forged, Not Given
> **Authority:** Human Architect (Arif) + 888_JUDGE
> **Version:** 2026.04.30-KANON-CLEANUP
> **Enforcement:** CI gates + pre-commit hooks

---

## Preamble

This repository hosts the arifOS Constitutional Federation. To prevent the entropy that accumulates when multiple naming generations, competing canonical roots, and legacy code cohabit, these rules are binding on all commits.

---

## Rule 1: Top-Level Folder Governance (F10 Ontology)

**No new top-level directory without:**
1. An ADR entry (`/adr/ADR_XXX_*`)
2. Update to `CANONICAL_PATHS.md`
3. Update to `INDEX.md` (or creation thereof)

**Rationale:** Unbounded top-level creation is the first symptom of architectural decay.

---

## Rule 2: Canonical Entrypoint Governance (F11 Auth)

**Only these are allowed as runtime entrypoints:**
- `python server.py` (HTTP / streamable-http)
- `python -m arifosmcp.runtime.server` (same as above)

**STDIO transport was removed in KANON.** Any resurrection requires ADR approval.

---

## Rule 3: Public Surface Lock (F13 Sovereign)

The public MCP tool surface is frozen at **13 canonical `arif_*` names**.

Any new public tool requires:
1. ADR approval
2. Update to `arifosmcp/tool_registry.json`
3. Update to `PUBLIC_SURFACE_CANON.md`
4. Schema test in `tests/test_public_tool_registry.py`
5. Handler implementation in `arifosmcp/runtime/tools.py`

**Forbidden on the public surface:**
- `arifos_*` names (internal engines only)
- Legacy codenames (`init_anchor`, `agi_mind`, `apex_soul`, etc.)
- Doubled prefixes (`arifos_arifos_*`)

---

## Rule 4: Legacy Quarantine (F1 Amanah)

**Everything legacy goes to `/archive/` or `*/archive/legacy/` and becomes read-only.**

- CI ignores archived paths
- Tests never import from archive
- Archive files get tombstone headers, not updates

---

## Rule 5: Contracts-First Enforcement (F2 Truth)

**Tool schema ↔ handler signature must match.**

CI must verify:
- `@mcp.tool()` decorator names match handler function names
- Pydantic input schemas match handler type annotations
- No `or "literal"` always-true bugs in conditionals

---

## Rule 6: Single Source of Truth (F3 Witness)

When documentation disagrees with live runtime:
1. **Live runtime wins** on behavior
2. **`PUBLIC_SURFACE_CANON.md` wins** on intent
3. **`CANONICAL_PATHS.md` wins** on file authority

Any contradiction must be resolved in favor of the higher-numbered source.

---

## Rule 7: No Hardcoded Secrets (F12 Injection)

- `detect-secrets` baseline scan on every commit
- `bandit` security scan on every PR
- No `auth_token="IM ARIF"` or equivalent dev fallbacks in production paths
- Dev-mode bypasses must be gated behind explicit `ARIFOS_DEV_MODE` env flag

---

## Rule 8: Floor Enforcement Consistency (F4 Clarity)

There must be **one canonical floor evaluator** per layer.

Current canonical paths:
- HTTP surface: `arifosmcp/core/floors.py`
- Organ layer: `core/shared/floors.py`
- Target: Consolidate to `core/shared/floors.py` only

Adding a new `check_floors` implementation requires ADR approval.

---

## Rule 9: Naming Hygiene (F9 Anti-Hantu)

Pre-commit must reject commits that:
- Introduce new `arifos_*` public tool names
- Add doubled prefixes (`arifos_arifos_*`)
- Use consciousness/emotion claims in code comments (F9 Anti-Hantu)

---

## Rule 10: Thermodynamic Budget (F8 Genius)

No commit that:
- Adds >500 lines without ADR
- Introduces a new dependency without security audit
- Duplicates existing functionality (check `CANONICAL_PATHS.md` first)

---

## Amendment Process

These rules may be amended only by:
1. ADR proposing the change
2. `arif_judge_deliberate(mode="plan_approve")` — deterministic sovereign ratification
3. Update to `REPO_CONSTITUTION.md` with amendment timestamp

---

*Forged by Kimi Code CLI under Arif's sovereign direction · 2026-04-30*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
