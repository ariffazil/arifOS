<!-- SOT-MANIFEST
adr_id:          ADR-011
title:           Scar substrate clarification — doctrine layer vs state substrate
status:          DRAFT (Cycle A — pre-F13 ratification)
owner:           arifOS kernel + AAA (joint)
forged_by:       Hermes, 2026-06-21
linked_audit:    Hermes audit 2026-06-21 (memory architecture critique)
constitution:    SOUL.md §3.2, §7.11
supersedes:      none (first canonical clarification)
reversible:      yes (draft status)
-->

# ADR-011 — Scar substrate clarification: doctrine layer vs state substrate

## Status

**DRAFT** — Cycle A of Remediation Plan 2026-06-21-002.
Requires **888_JUDGE review + F13 ratification** before promotion to RATIFIED.

## Context

SOUL.md §3.2 establishes the scar registry conceptually:

> "Scar tissue is permanent. Time alone does not heal it. Only *demonstrated
> change* heals, witnessed and recorded."

The original essay ("vector embeddings vs filesystem") claimed:
> "arifOS uses ... scar registry for lineage"

This claim is **partially true**: scars exist as **doctrine** (SOUL.md §3.2,
`arif_wound_architecture` skill, `arif_fazil_wound_architecture.md`) but
**NOT as state substrate**. There is no:

- `scar_registry.jsonl` append-only ledger
- SHA-chained scar events
- Deterministic scar query API
- Runtime scar counter (malu_score lives in doctrine, not in memory state)

Hermes audit 2026-06-21 (item 9) named this as a gap: "Scar registry is
doctrine, not runtime substrate."

## Decision

Scar memory in arifOS exists at **two distinct layers**, and this ADR
makes the distinction canonical:

### Layer 1: Scar Doctrine (EXISTS, canonical)

- **Location:** SOUL.md §3.2, `arif_wound_architecture` skill,
  `arif_fazil_wound_architecture.md`
- **Authority:** Doctrine layer — narrative, mutable by F13 ratification
- **Purpose:** Define what a scar IS, the constitutional meaning, the
  recovery mechanism (tebus_salah), the malu_score semantics
- **Mutability:** Doctrine evolves through constitutional process
- **Auditability:** Diff-tracked via git, no chain required

### Layer 2: Scar State Substrate (DOES NOT EXIST YET)

- **Location:** Not yet implemented
- **Authority:** State substrate (would be KSR-mediated, append-only)
- **Purpose:** Deterministic record of: "this organ accumulated N scars,
  M resolved, K pending tebus_salah, last incident at T"
- **Mutability:** Append-only, hash-chained
- **Auditability:** Same pattern as VAULT999 — every scar event sealed
  with provenance

### Recommended Path Forward (Cycle B)

This ADR proposes **one of two paths**, requires F13 choice:

**Option A — Build scar state substrate**
- Forge `arifosmcp/memory/scar_registry.py` (append-only JSONL)
- Mirror VAULT999 pattern: hash-chained, kernel-signed, KSR-mediated
- Wire `malu_score` from doctrine to runtime state
- Cost: ~200 LOC, 1-2 days, requires test suite

**Option B — Honest reframing (no new substrate)**
- Update SOUL.md §3.2 to clarify "scar registry = doctrine, not state"
- Update essay (and any future canon) to use "scar doctrine for lineage"
  instead of "scar registry for lineage"
- Cost: ~1 paragraph edit, no new code
- Cost of deferral: scar queries remain hand-curated, no deterministic
  recovery status, malu_score can't be enforced as a runtime floor

## Consequences

### If Option A chosen

- Scars become enforceable as runtime floor (malu_score limits authority)
- T2 per-event judgment can reference scar lineage deterministically
- Recovery (tebus_salah) becomes auditable, not narrative
- Adds another append-only ledger to maintain

### If Option B chosen

- Doctrine stays clean, no substrate maintenance burden
- Scar enforcement remains governance-by-narrative (already the case)
- Future agents must remember "scars = doctrine" to avoid fabrication
  (the exact failure mode the original essay committed)

### If neither chosen (status quo)

- Gap remains named but unaddressed
- Future essays risk repeating the same fabrication
- Cost of deferral grows linearly with essay publications

## Constitutional Anchors

- **F1 (AMANAH):** Reversible-first. Option B is fully reversible. Option A
  requires T2 per-event judgment for scar appends.
- **F2 (TRUTH):** Doctrine and substrate must align. This ADR makes the
  current misalignment explicit.
- **F3 (WITNESS):** Scar lineage requires witness (888 ratification or
  hash chain — choose at implementation).
- **§3.2:** "Scars are permanent. Only demonstrated change heals."

## Ratification Path

1. ✅ Draft (this document, with Option A + Option B) — Cycle A
2. ⏳ 888_JUDGE review on Option A vs B tradeoff
3. ⏳ **F13 SOVEREIGN (Arif) chooses Option A or B** — this is the key decision
4. ⏳ Promote to RATIFIED with chosen option
5. ⏳ Implement or document per choice

## Links

- Hermes memory architecture critique, 2026-06-21, item 9
- SOUL.md §3.2 — Scar doctrine
- `arif_wound_architecture` skill — narrative layer
- `arif_fazil_wound_architecture.md` — substrate of sovereign's scars
- `arifosmcp/VAULT999/` — pattern to mirror if Option A chosen
- ADR-008, ADR-009, ADR-010 — sibling memory architecture ADRs

---

**DITEMPA BUKAN DIBERI — Scars forged, not narrated.**