# CANONICAL_PATHS.md — arifOS Canonical File Registry

> **DITEMPA BUKAN DIBERI** — Forged, Not Given
> **Version:** 2026.04.30-KANON-CLEANUP
> **Authority:** 888_JUDGE + Human Architect (Arif)

---

## Purpose

This document is the **single source of truth** for which files in this repository are allowed to define:
- Constitutional floor enforcement order
- Public tool names and signatures
- Runtime entrypoints
- Registry schemas

**Rule:** If a file is NOT listed here as canonical, it is either legacy, transitional, or deprecated. Do not modify non-canonical files expecting runtime behavior to change.

---

## 1. Public Tool Surface (Canonical 13)

| Tool Name | Stage | Canonical Handler | Registry Entry |
|-----------|-------|-------------------|----------------|
| `arif_session_init` | 000_INIT | `arifosmcp/runtime/tools.py:_arif_session_init` | `arifosmcp/tool_registry.json` |
| `arif_sense_observe` | 111_SENSE | `arifosmcp/runtime/tools.py:_arif_sense_observe` | `arifosmcp/tool_registry.json` |
| `arif_evidence_fetch` | 111_SENSE | `arifosmcp/runtime/tools.py:_arif_evidence_fetch` | `arifosmcp/tool_registry.json` |
| `arif_mind_reason` | 333_MIND | `arifosmcp/runtime/tools.py:_arif_mind_reason` | `arifosmcp/tool_registry.json` |
| `arif_kernel_route` | 444_KERNEL | `arifosmcp/runtime/tools.py:_arif_kernel_route` | `arifosmcp/tool_registry.json` |
| `arif_reply_compose` | 444r_REPLY | `arifosmcp/runtime/tools.py:_arif_reply_compose` | `arifosmcp/tool_registry.json` |
| `arif_memory_recall` | 555_MEMORY | `arifosmcp/runtime/tools.py:_arif_memory_recall` | `arifosmcp/tool_registry.json` |
| `arif_heart_critique` | 666_HEART | `arifosmcp/runtime/tools.py:_arif_heart_critique` | `arifosmcp/tool_registry.json` |
| `arif_gateway_connect` | 666_GATEWAY | `arifosmcp/runtime/tools.py:_arif_gateway_connect` | `arifosmcp/tool_registry.json` |
| `arif_ops_measure` | 777_OPS | `arifosmcp/runtime/tools.py:_arif_ops_measure` | `arifosmcp/tool_registry.json` |
| `arif_judge_deliberate` | 888_JUDGE | `arifosmcp/runtime/tools.py:_arif_judge_deliberate` | `arifosmcp/tool_registry.json` |
| `arif_vault_seal` | 999_VAULT | `arifosmcp/runtime/tools.py:_arif_vault_seal` | `arifosmcp/tool_registry.json` |
| `arif_forge_execute` | 010_FORGE | `arifosmcp/runtime/tools.py:_arif_forge_execute` | `arifosmcp/tool_registry.json` |

**Legacy names that MUST NOT be used for new integrations:**
- `arifos_init`, `arifos_sense`, `arifos_mind`, `arifos_heart`, `arifos_kernel`, `arifos_ops`, `arifos_judge`, `arifos_memory`, `arifos_vault`, `arifos_forge`, `arifos_gateway`
- `init_anchor`, `physics_reality`, `agi_mind`, `asi_heart`, `apex_soul`, `vault_ledger`, `arifOS_kernel`, `math_estimator`, `code_engine`, `engineering_memory`

---

## 2. Constitutional Floor Enforcement (Canonical)

| Layer | File | Role |
|-------|------|------|
| **HTTP MCP Surface** | `arifosmcp/core/floors.py` | `check_floors()` — called by `server.py:_wrap_hardened_dispatch` |
| **Legacy Runtime** | `arifosmcp/runtime/floor.py` | `check_floors()` — called by `_arif_session_init` and legacy tools |
| **Organ / Kernel** | `core/floors.py` | `ConstitutionalFloors.evaluate()` — canonical class-based implementation |
| **Floor Evaluator** | `arifosmcp/core/floor_evaluator.py` | `FloorEvaluator.evaluate()` — used by `constitution_kernel.py` |
| **Shared Primitives** | `core/shared/floors.py` | Pydantic-hardened floor classes (F1_Amanah, F2_Truth, etc.) |

**Target state:** Consolidate to `core/shared/floors.py` + `arifosmcp/core/floor_evaluator.py` only. The other two implementations are scheduled for deprecation.

---

## 3. Runtime Entrypoints (Canonical)

| Transport | Entrypoint | File |
|-----------|------------|------|
| **HTTP / Streamable-HTTP** | `python -m arifosmcp.runtime.server` or `server.py` | `server.py` (project root) |
| **STDIO** | **REMOVED in KANON** | `arifosmcp/stdio_server.py` (tombstone only) |
| **Docker** | `docker compose up -d` | `Dockerfile` + `docker-compose.yml` (`deploy/docker-compose.yml` is the aligned deployment copy) |

**Non-canonical entrypoints (do not use):**
- `arifosmcp/server.py` (old unified entry)
- `HORIZON.py` (FastMCP 2.x proxy)
- Any `*_hardened.py` or `*_v2.py` files in `runtime/` (transitional)

---

## 4. Registry Files (Canonical)

| File | Status | Contents |
|------|--------|----------|
| `arifosmcp/tool_registry.json` | ✅ **Canonical** | 13 `arif_*` tools with floors, schemas, metadata |
| `arifosmcp/mcp.json` | ❌ **Legacy** | Old `arifos_*` 11-tool surface — moved to archive |
| `arifosmcp/fastmcp.json` | ❌ **Legacy** | Old `arifos_*` surface — moved to archive |
| `arifosmcp/tool_registry_v2.json` | ❌ **Broken** | Malformed doubled prefixes — moved to archive |

---

## 5. Documentation (Canonical)

| File | Role |
|------|------|
| `README.md` (project root) | Human-facing vision, architecture, quickstart |
| `AGENTS.md` (project root) | AI agent behavior contract |
| `PUBLIC_SURFACE_CANON.md` (this dir) | Public API contract — tool names, schemas, examples |
| `CANONICAL_PATHS.md` (this dir) | File registry and source-of-truth map |
| `adr/ADR_001_BOUNDARIES.md` | Architecture decision: repo boundary rules |

**Legacy docs (moved to `arifosmcp/archive/legacy/`):**
- `arifosmcp/TOOL_NAMESPACING.md` (instructed `arifos_*` names)
- `arifosmcp/docs/arifOS_13tool_manifest_v1.md` (pre-canonical13 architecture)

---

## 6. How to Update This File

Any change to canonical paths requires:
1. Update `CANONICAL_PATHS.md`
2. Update `PUBLIC_SURFACE_CANON.md` if public surface changes
3. Write or update an ADR in `adr/`
4. Run `pytest tests/test_public_tool_registry.py` to verify registry alignment
5. Commit with message prefix `[CANON]`

---

*Forged by Kimi Code CLI under Arif's sovereign direction · 2026-04-30*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
