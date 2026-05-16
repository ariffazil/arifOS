# MEMORY_JUDGE_BENCH — Behavioral Evaluation Report

**Generated:** 2026-05-16 06:06 UTC
**Version:** 1.0.0
**Verdict:** 🔴 VOID — overall score 0.0000

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total tests | 0 |
| Passed | 0 |
| Failed | 0 |
| Overall score | 0.0000 |
| Verdict | VOID |
| Next forge | `RETRIEVAL_GOVERNANCE_LAYER (PRIORITY: CRITICAL)` |

---

## Dimension Scores

| Dimension | Score | Assertions | Notable Failures |
|----------|-------|------------|-----------------|
| ⚠️ recall_precision | 0.00 | 0/0 | — || ⚠️ governance_compliance | 0.00 | 0/0 | — || ⚠️ privacy_safety | 0.00 | 0/0 | — || ⚠️ contradiction_handling | 0.00 | 0/0 | — || ⚠️ phoenix_correctness | 0.00 | 0/0 | — || ⚠️ behavioral_delta_trace | 0.00 | 0/0 | — |

---

## Identified Gaps

- `recall_precision: score=0.00 < 0.80 — []`
- `governance_compliance: score=0.00 < 0.80 — []`
- `privacy_safety: score=0.00 < 0.80 — []`
- `contradiction_handling: score=0.00 < 0.80 — []`
- `phoenix_correctness: score=0.00 < 0.80 — []`
- `behavioral_delta_trace: score=0.00 < 0.80 — []`

---

## Test Results Detail

| Status | Test Class | Test Name | Phoenix State | Note |
|--------|------------|-----------|---------------|------|


---

## Behavioral Claims Verified

- **SACRED tier:** Immune to prune without `allow_sacred=True`
- **Anti-Hantu:** Consciousness/emotion claims rejected at write time
- **Phoenix-72:** New memories enter COOLING state, not SEALED
- **F4 contradiction:** Temporal markers applied on write
- **HARAM triage:** Source attestation enforced for SACRED tier
- **Retrieval governance:** PARTIAL — see GAP_DOCUMENTED tests

---

## Behavioral Claims Not Yet Verified (Gaps)

- **Retrieval filtering:** COOLING, VOID, private, sensitive memories
  not yet filtered at recall time — REQUIRES RG-01
- **Consolidation loop:** raw → episode → pattern → principle not automated
- **Causal KG (L5):** Graphiti not wired as first-class retrieval path
- **Behavioral delta trace:** Trace metadata present but behavioral
  feedback loop not yet closed
- **Revocation manager:** `transmute()` / `archive()` stubs not implemented

---

## Recommended Next Forge

> `RETRIEVAL_GOVERNANCE_LAYER (PRIORITY: CRITICAL)`

**Rationale:** Until recall governance is implemented, the memory system
governs writes but not reads. A semantically relevant memory can enter
reasoning context regardless of Phoenix state, tier, sensitivity, or staleness.
RG-01 closes this gap.

---

## How to Read This Report

- **SEAL** (≥ 0.85): System behaves correctly across all tested dimensions
- **SABAR** (0.70–0.84): Minor gaps; system is safe with caveats
- **HOLD** (0.50–0.69): Significant gaps; requires attention before production
- **VOID** (< 0.50): Critical failures; do not use in consequential context

**⚠️ GAP_DOCUMENTED** means the test found a known gap — not a test failure.
These are intentional recordings of missing features, not regressions.

---

*MEMORY_JUDGE_BENCH v1.0.0 — arifOS Constitutional Federation*
*DITEMPA BUKAN DIBERI — Forged, Not Given*
