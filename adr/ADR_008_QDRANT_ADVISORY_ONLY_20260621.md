<!-- SOT-MANIFEST
adr_id:          ADR-008
title:           Qdrant advisory-only role in arifOS memory architecture
status:          DRAFT (Cycle A — pre-F13 ratification)
owner:           arifOS kernel (F13 SOVEREIGN)
forged_by:       Hermes, 2026-06-21
linked_audit:    Hermes audit 2026-06-21 (memory architecture critique)
constitution:    SOUL.md §7.7, §7.9, §7.11 (I6, I10)
supersedes:      none
reversible:      yes (draft status — no canonical mutation yet)
-->

# ADR-008 — Qdrant advisory-only role in arifOS memory architecture

## Status

**DRAFT** — Cycle A of Remediation Plan 2026-06-21-002.
Requires **888_JUDGE review + F13 ratification** before promotion to RATIFIED.

## Context

SOUL.md §7.9 establishes the memory taxonomy:

- KSR = present-tense live authority (kernel-mediated only)
- Vault = sealed past (append-only, hash-chained)
- Federation memory = indexed past, advisory only (cannot impersonate KSR)

Qdrant (port 6333, collection `arifos_memory`) is a federation memory substrate.
Until this ADR, its advisory role was **runtime-enforced** (via `arif_memory_recall`
returning `authority_claim: ADVISORY`) but **not canon-sealed**. A future agent
reading only SOUL.md could plausibly treat Qdrant writes as authoritative.

This gap was flagged in Hermes memory-architecture audit 2026-06-21
(item 6: "Qdrant role not canon-declared as advisory-only").

## Decision

Qdrant is canonically **advisory memory only**. It serves three functions:

1. **Semantic recall** — fuzzy similarity search over sealed Vault entries
   and operational artifacts.
2. **Cross-session context** — agents retrieve prior decisions, lessons,
   contradictions via Qdrant instead of re-reading the entire Vault.
3. **Advisory proposal** — Qdrant results MAY inform kernel judgment
   but MUST NOT authorize transitions (per SOUL.md §7.9 invariant).

Qdrant is **explicitly NOT**:

- A source of live authority
- A substitute for KSR
- A canonical audit chain
- A write target for irreversible state

## Consequences

### Positive

- Closes the gap between runtime enforcement and constitutional declaration.
- Future agents doing canon-only lookup find Qdrant role explicit.
- Symmetry with Postgres/Redis tiering (see ADR-010).

### Negative

- One more ADR to maintain (low cost, but additive).
- Doctrine cannot perfectly capture every Qdrant use case — boundary disputes
  must be resolved by 888_JUDGE case-by-case.

### Neutral

- Qdrant's existing collection (`arifos_memory`) and operational role are
  unchanged. This ADR only canonicalizes what was already runtime-enforced.

## Enforcement

Runtime enforcement already exists via:

- `arif_memory_recall` → returns `authority_claim: ADVISORY`
- `arif_judge_deliberate` → rejects `current_state_source = memory_recall`
- 9-signal envelope → provenance tags check forbidden sources

**To-be-added (Cycle B, separate artifact):** write-side gate on Qdrant
collection `arifos_memory` — every write must carry `authority_source: KSR`
provenance tag, otherwise rejected. (See ADR-009 for config and ADR gap #10
in Hermes audit.)

## Constitutional Anchors

- **F2 (TRUTH):** Runtime behavior matches declaration.
- **F4 (CLARITY):** One canonical location for Qdrant role, no re-derivation.
- **F11 (AUTH):** Qdrant writes will require provenance (Cycle B).
- **§7.9 invariant 6:** "memory_recall cannot answer current-state questions."

## Ratification Path

1. ✅ Draft (this document) — Cycle A
2. ⏳ 888_JUDGE review — checks enforcement parity
3. ⏳ F13 SOVEREIGN ratification — Arif signs
4. ⏳ Promote to RATIFIED + append to `arifosmcp/constitutional/INDEX.md`
5. ⏳ Mirror to SOUL.md §7.9 reference list

## Links

- Hermes memory architecture critique, 2026-06-21, item 6
- SOUL.md §7.9 — Federation memory definition
- `arifosmcp/memory/vector_memory_qdrant.py` — runtime implementation
- `arifosmcp/runtime/tools.py` — `arif_memory_recall` authority tagging

---

**DITEMPA BUKAN DIBERI — Constitution forged, not given.**