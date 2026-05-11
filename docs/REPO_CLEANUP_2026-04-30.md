# Repo De-Chaos Cleanup Report
**Date:** 2026-04-30 | **Auditor:** Kimi Code CLI | **Authority:** Arif Fazil

---

## Summary

Red-team audit revealed **naming drift across 4 generations** of tool names, competing canonical roots, and legacy code cohabiting with active runtime. This cleanup forges order from that entropy.

| Metric | Before | After |
|--------|--------|-------|
| Public tool naming generations | 4 (`arifos_*`, `init_anchor`, `arif_*`, `arifos_arifos_*`) | 1 (`arif_*`) |
| Competing `check_floors` implementations | 3 (NO-OP stubs, partial, canonical) | 2 with full enforcement |
| Stale registry files in root | 3 (`mcp.json`, `fastmcp.json`, `tool_registry_v2.json`) | 0 (all archived) |
| Docs instructing wrong names | 2 (`TOOL_NAMESPACING.md`, `manifest_v1.md`) | 0 (archived + canonical docs written) |
| Canonical governance docs | 0 | 4 (`CANONICAL_PATHS.md`, `PUBLIC_SURFACE_CANON.md`, `ADR_001_BOUNDARIES.md`, `REPO_CONSTITUTION.md`) |
| Validation script | 0 | 1 (`scripts/validate_canonical_surface.py`) |
| README consistency | Mixed 3 naming eras | Single `arif_*` contract |

---

## Files Created

| File | Purpose |
|------|---------|
| `CANONICAL_PATHS.md` | Registry of which files are allowed to define enforcement, signatures, and entrypoints |
| `PUBLIC_SURFACE_CANON.md` | Definitive public API contract — 13 tools, schemas, examples, legacy migration guide |
| `adr/ADR_001_BOUNDARIES.md` | Architecture decision record for monorepo boundary rules |
| `REPO_CONSTITUTION.md` | 10 binding rules preventing chaos from returning |
| `scripts/validate_canonical_surface.py` | CI guard that detects public surface drift |

---

## Files Quarantined to `arifosmcp/archive/legacy/`

| File | Reason |
|------|--------|
| `mcp.json` | Old `arifos_*` 11-tool surface, pre-KANON |
| `fastmcp.json` | Old `arifos_*` surface, FastMCP 2.x era |
| `tool_registry_v2.json` | Malformed doubled prefixes (`arifos_arifos_*`) |
| `TOOL_NAMESPACING.md` | Instructed `arifos_*` and `P_*` names, contradicted live surface |
| `docs/arifOS_13tool_manifest_v1.md` | Pre-canonical13 architecture with merged compute/oracle tools |

Tombstone files left in original locations redirect to archive.

---

## Files Modified

| File | Change |
|------|--------|
| `arifosmcp/README.md` | Complete rewrite of tool inventory, API examples, schema docs to use `arif_*` names exclusively |
| `arifosmcp/core/floors.py` | NO-OP stubs for F02–F08, F10 replaced with actual heuristic checks |
| `arifosmcp/runtime/tools.py` | `session_id` now passed to `check_floors` in `_arif_session_init` |
| `arifosmcp/tools/reality.py` | `_detect_injection()` now called before `_exec_shell()` |
| `arifosmcp/stdio_server.py` | Documented as deprecated (stdio removed in KANON) |
| `core/floors.py` | F6 violation now triggers VOID; F13 check added; `_check_f13_sovereign()` implemented |
| `core/organs/_2_asi.py` | Always-true `or "full"` bug fixed to `in ("logic", "full")` |
| `core/kernel/loop_controller.py` | Hardcoded `auth_token="IM ARIF"` → `os.environ.get("ARIFOS_AUTH_TOKEN", ...)` |
| `core/shared/crypto.py` | Dev fallback gated behind `ARIFOS_DEV_MODE`; fail-closed in production |
| `geox/.../mcp_server_hardened.py` | Traceback removed from client JSON responses |

---

## Validation Results

- ✅ `scripts/validate_canonical_surface.py` — passes (no drift)
- ✅ `tests/test_public_tool_registry.py` — passes
- ✅ `tests/test_000_init.py` — 38 passed
- ✅ `tests/test_floors_ci.py` + `tests/test_constitutional_guard.py` + `tests/runtime/test_tools_simple.py` + `tests/runtime/test_tools_advanced.py` — 12 passed
- ✅ `arifosmcp/tool_registry.json` — 13 canonical `arif_*` tools, all aligned with `PUBLIC_SURFACE_CANON.md`

---

## Remaining Work (Not in Scope)

1. **Session bootstrap chicken-egg** — `mcp-session-id` required for `arif_session_init` (P0)
2. **Unified floor evaluator** — consolidate `arifosmcp/core/floors.py`, `arifosmcp/runtime/floor.py`, `core/floors.py` (P0)
3. **3 pre-existing test failures** in `test_canonical.py` (F13 human-witness requirement)
4. **Ed25519 verification stubs** in `identities.py` and `governance_identity.py`
5. **WELL mirror** fails on `null` well_score
6. **Install `bandit` + `detect-secrets`** in pre-commit pipeline

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
