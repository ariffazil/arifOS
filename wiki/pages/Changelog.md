---
type: Source
tier: 50_AUDITS
strand:
- operations
audience:
- operators
difficulty: beginner
prerequisites:
- What-is-arifOS
tags:
- changelog
- release
- audit
- architecture
- history
sources:
- CHANGELOG.md
last_sync: '2026-04-10'
confidence: 1.0
---

# arifOS Changelog

> **Source:** `wiki/raw/CHANGELOG.md`  
> **Coverage:** All notable changes to arifOS MCP.

---

## Release Timeline (Most Recent First)

### `2026.04.07-SOT-SEALED` — Versioned File Unification + Single Source of Truth

**Scale:** −3,841 lines of chaos eliminated.

Key changes:

- **13 versioned files** (`tools_v2.py`, `prompts_v2.py`, `schemas_v2_clean.py`, etc.) → consolidated into single canonical modules
- `ToolSpecV2 → ToolSpec`, `V2_TOOLS → TOOLS` (backward-compat aliases preserved)
- `/health` endpoint now exposes: `source_repo`, `source_commit`, `release_tag`, `transport`, `governance_version`, `floors_active`, `warnings[]`
- `/.well-known/arifos-index.json` — new canonical index linking runtime to SoT repo
- `arifos_v2` namespace fully purged from all active runtime Python files
- Lean Dockerfile: ~500MB multi-stage build (was 6.1GB)
- AGI Mind Pipeline: Wide internal state → Narrow output envelopes (max 15 lines)
- VPS Docker hygiene: reclaimed 32.5GB; git phantom history cleaned

**SoT Rule (enforced from this release):**
> Doctrine conflict → arifOS repo wins. Runtime surface conflict → live `/health` + `/tools` wins.

---

### `2026.04.06.3-TOM-ANCHORED` — Theory of Mind + 9+1 Architecture

**The definitive constitutional architecture.**

#### 9+1 Constitutional Architecture

| Layer | Tools | Role |
|-------|-------|------|
| **9 Governance Tools** | init, sense, mind, route, heart, ops, judge, memory, vault | Think / Validate — never execute directly |
| **1 Execution Bridge** | forge | Action — requires `judge verdict="SEAL"` |

**ToM Requirements (all governance tools):** Every tool forces LLM mental model externalization — alternatives, second-order effects, confidence estimates, assumptions. Missing ToM fields → `tom_violation: True` + VOID verdict.

**G★ Scoring formula:** `G★ = confidence + adjustments` (clamped [0,1])  
Factors: confidence estimates, alternative count, assumptions declared, second-order effects, consistency checks, harm probability (inverse).

#### Philosophy Registry v1.2.0

- 83 civilizational quotes across 5 G★ bands
- Deterministic selection: `sha256(session_id + band + g_star) % count`
- Hard override: INIT stage and SEAL verdict → "DITEMPA, BUKAN DIBERI."
- Diversity score: 0.85 (target ≥0.80)

#### Tool Modes (consolidation)

- `arifos_judge` → modes: `judge`, `health`, `history`, `validate`
- `arifos_vault` → modes: `seal`, `seal_card`, `render`, `status`

---

### `2026.04.06.2-HOUSEKEEPING` — Canonical Tool Names + Dead Code Purge

**~6,000 lines of dead/superseded code archived.**

- Canonical tool names restored (11 mega-tools): `init_anchor`, `architect_registry`, `physics_reality`, `agi_mind`, `asi_heart`, `arifOS_kernel`, `engineering_memory`, `math_estimator`, `apex_soul`, `vault_ledger`, `code_engine`
- Archived: `arifosmcp/specs/` (duplicate), 4 hardened runtime files (2,620+ lines), `tools/governance/`, `tools/intelligence/`, `tools/reality/`, `tools/execution/` (never wired)
- Surface counts fixed: exactly 11 tools / 10 prompts / 8 resources
- PYTHONPATH fix in docker-compose.yml

---

### `2026.04.06.1` — Clean Architecture + ChatGPT Apps SDK

**arifOS exposes constitutional health via OpenAI Apps SDK.**

Exposed tools (read-only Phase 1):

- `get_constitutional_health` — health card with telemetry
- `render_vault_seal` — widget render
- `list_recent_verdicts` — vault audit log (last 100 entries)

Widget at `https://mcp.af-forge.io/widget/vault-seal` — CSP-compliant with ChatGPT iframe allowlist.  
888_HOLD compliance: no vault write or VPS execution in ChatGPT path.

---

### `2026.04.05-ARCHIVE-SURGERY` — `core/` → `arifosmcp/` Migration Complete

**153 files permanently migrated from `core/` into `arifosmcp/`.**

- `core/` directory deleted (governance_kernel, pipeline, judgment, organs, shared, physics, intelligence, enforcement, kernel, security, vault, workflow, theory, SOULS, config, contracts, observability, perception, prompts, protocols, recovery, scheduler, state)
- Canonical home: all logic now exclusively in `arifosmcp/`
- F13 KHILAFAH: Gemini, Copilot, Kimi granted full filesystem access via `SEMANTIC_BYPASS_ACTORS`
- `arif-site`: forge-portal React/Vite/Tailwind frontend scaffold added

> **Agent note:** References to `core/organs/`, `core/pipeline.py`, etc. are obsolete. Use `arifosmcp/` paths.

---

### `2026.04.06-GREAT-UNIFICATION` — Repository Restructuring & Consolidation

Repository Order Architect mandate executed — chaos and narrative overlap eliminated.

---

### `2026.03.20` — Tool Consolidation

42 tools consolidated into 11 Mega-Tools — the canonical surface that replaced the previous sprawl.

---

## Evolution Arc

```
Ignition (concept)
  → Unification (42 tools → 11 Mega-Tools, Mar 2026)
  → Archive Surgery (core/ → arifosmcp/, Apr 5)
  → Great Unification (repo restructure, Apr 6)
  → ToM-Anchored (9+1 architecture, Apr 6.3)
  → SOT-Sealed (single source of truth, Apr 7) ← CURRENT

```

---

## Open Questions

- What does the next release milestone look like after SOT-SEALED?
- When is the `platform=` dispatch (Path A) expected to land?
- Is Philosophy Registry v1.2.0 (83 quotes) the latest, or has it grown?

---

> [!NOTE]  
> This page is a synthesis. Full entry details (infra tables, code snippets, archived file lists) live in `wiki/raw/CHANGELOG.md`.

**Related:** [[Roadmap]] | [[What-is-arifOS]]
