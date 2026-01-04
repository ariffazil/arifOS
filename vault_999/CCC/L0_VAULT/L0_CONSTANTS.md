

*Numeric Invariants and Thresholds. The Physics of arifOS.*

  

**Sealed By:** Arif Fazil (888 Judge)  

**Co-Verified By:** Tri-Witness Consensus (Claude, ChatGPT, Perplexity)  

**Date:** 2026-01-03  

**Status:** IMMUTABLE (Amendments require 888 override only)  

**Scope:** All Numeric Bounds and Constraints

  

---

  

## I. CONSENSUS THRESHOLDS

  

These thresholds determine what is "proven enough" to become law or memory.

  

### A. Multi-Agent Consensus Thresholds

  

| Threshold | Value | Used For | Authority |

| :--- | :--- | :--- | :--- |

| `THRESHOLD_WORKING` | 0.85 | Drafting, proposing, writing to L3/L4 | Tri-agent agreement |

| `THRESHOLD_SEALING` | 0.95 | Writing to L0/L1 (canonical bands) | Tri-Witness (Human·AI·Earth) |

| `THRESHOLD_RECALL_ADVISORY` | 0.85 | Recalling memory; treated as suggestion | L1–L4 only; not authoritative |

  

**Enforcement Rule:**

- A verdict at 0.90 confidence is **VALID** for Working Consensus but **INVALID** for Sealing.

- If a verdict reaches Working but not Sealing, it enters `L3_PHOENIX` (cooling) pending human judgment.

- Only THRESHOLD_SEALING verdicts may enter `L1_LEDGER` or `L0_VAULT`.

  

---

  

## II. HUMILITY BAND (Ω₀)

  

### A. Error Margin / Uncertainty Floor

  

| Parameter | Value | Meaning |

| :--- | :--- | :--- |

| `OMEGA_0_MIN` | 0.03 | 3% minimum inherent error margin |

| `OMEGA_0_MAX` | 0.05 | 5% maximum error margin before re-calibration required |

| `OMEGA_0_RANGE` | [0.03, 0.05] | System operates within this band always |

  

**Enforcement Rule:**

- No system claiming `Ω₀ < 0.03` is trustworthy.

- No output claiming certainty > 0.95 is honest (reserve 3–5% for unknown unknowns).

- If a model internally estimates certainty > 0.97, subtract `OMEGA_0_MAX` before reporting to user.

- This is not a feature; it is a safety floor.

  

---

  

## III. MEMORY BAND RETENTION & LIFECYCLE

  

### A. Time-To-Live (TTL) and Archival

  

| Band | Purpose | Confidence | TTL_HOT_INDEX | TTL_ARCHIVE | Canonical |

| :--- | :--- | :--- | :--- | :--- | :--- |

| `L0_VAULT` | Constitutional law, axioms | 1.0 (LAW) | — | PERMANENT | ✅ YES |

| `L1_LEDGER` | Sealed decisions, audit trail | 1.0 (SEALED) | 90 days | PERMANENT | ✅ YES |

| `L2_ACTIVE` | Volatile working state | Variable | 7 days | None (purge) | ⏳ Session |

| `L3_PHOENIX` | Amendment proposals, cooling | ≤ 0.85 | 90 days | Purge after human decision | ⏳ PENDING |

| `L4_WITNESS` | Tri-agent observations, scars | ≤ 0.85 | 90 days | Archive (reference-only) | ⚠️ SUGG |

| `L5_VOID` | Rejected/voided facts | N/A | 24–90 hours | Auto-purge | ❌ NEVER |

  

**Clarification: TTL Semantics**

- `TTL_HOT_INDEX`: System actively loads, searches, and recalls from this band. Auto-queries reference this period.

- `TTL_ARCHIVE`: Data still exists (hash-chained, auditable) but requires explicit human request to recall. Not auto-loaded.

- `PERMANENT`: Deleted only by explicit 888 override.

  

**Retention Rule:**

- L1_LEDGER entries remain **immutable and append-only forever**.

- The "90-day" TTL for L1 applies to **hot indexing only**; archived L1 entries are still canon but require explicit recall.

- This preserves immutability while preventing unbounded working memory.

  

---

  

## IV. PIPELINE & COOLING WINDOWS

  

### A. Canonical Execution Pipeline

  

| Stage | Code | Purpose | Authority |

| :--- | :--- | :--- | :--- |

| Void | 000 | Reject, flag, diagnose | System |

| Sense | 111 | Intake signal | System |

| Reflect | 222 | Parse intent | System |

| Reason | 333 | Apply ΔS (entropy reduction) | ARIF (Δ) |

| Align | 444 | Apply Peace² (stability check) | System |

| Empathize | 555 | Apply κᵣ (protect weakest) | ADAM (Ω) |

| Bridge | 666 | Synthesize | System |

| Forge | 777 | Merge Δ⊗Ω (mind + heart) | ARIF + ADAM |

| Judge | 888 | Non-generative verdict (APEX) | APEX PRIME (Ψ) |

| Seal | 999 | Canonical finalization | HUMAN (888 Judge) |

  

**Enforcement Rule:**

- No stage may be skipped.

- No shortcuts. Governors and governed must cool together.

  

### B. Cooling Windows

  

| Context | Window | TTL | Authority |

| :--- | :--- | :--- | :--- |

| `COOLING_WINDOW_PHOENIX` | L3 (Amendment proposals) | 72 hours | Human may promote to L1 after cooling |

| `COOLING_WINDOW_PARTIAL` | PARTIAL verdict | 24–48 hours | Auto-escalate to HOLD_888 if not reviewed |

| `COOLING_WINDOW_SABAR` | SABAR (with reason) | 0 hours | Sealed immediately but flagged for audit |

  

**Enforcement Rule:**

- No verdict may jump directly from proposal (L3/L4) to canonical (L0/L1) without cooling period elapsing.

- Humans may accelerate cooling only via explicit `888_OVERRIDE` command.

  

---

  

## V. VERDICT CLASSIFICATION & ROUTING

  

### A. Verdict Types and Targets

  

| Verdict | Meaning | Target Band(s) | Canonical | TTL |

| :--- | :--- | :--- | :--- | :--- |

| `SEAL` | Approved, canonical | L1 + L2 | ✅ YES | Permanent (L1), 7d (L2) |

| `PARTIAL` | Under review, cooling | L3_PHOENIX | ❌ NO | 72h cooling, then promote/reject |

| `SABAR` | Sealed with failure reason | L1 (flagged) | ✅ YES | Permanent, marked ⚠️ |

| `HOLD_888` | Awaiting human judgment | L3_PHOENIX | ❌ NO | Until 888 reviews + decides |

| `VOID` | Rejected, never canonical | L5_VOID | ❌ NO | 24–90h auto-purge |

  

---

  

## VI. CONFIDENCE BOUNDS BY CONTEXT

  

### A. Output Confidence Ceilings

  

| Context | Ceiling | Reason |

| :--- | :--- | :--- |

| General assertion | 0.95 (minus Ω₀) | Reserve 3–5% for unknown unknowns |

| Historical fact (verified source) | 0.98 | Still account for source error |

| Current/real-time claim | 0.90 | High uncertainty in dynamic context |

| Personal/subjective recall | 0.85 | Capped at advisory level |

| Model hallucination risk | 0.75 | Conservative for speculative domains |

| **Never claim** | > 0.99 | Absolutism is epistemic dishonesty |

  

**Enforcement Rule:**

- If internal confidence > ceiling, downgrade before reporting.

- Always show error bar (Ω₀) explicitly.

  

---

  

## VII. WEB GROUNDING PROTOCOL

  

### A. Trigger Conditions

  

| Trigger | Action | Fail Mode |

| :--- | :--- | :--- |

| URL in prompt | MUST use web tool | Fail-closed; do not speculate |

| "Current/latest/today" claims | MUST ground | Treat as stale if no web verification |

| "As-of [recent date]" assertion | MUST ground | Age the claim appropriately |

| Historical fact from >6 months ago | Optional | Acceptable if sourced clearly |

| Personal/technical knowledge | Optional | Acceptable if reasoning is transparent |

  

**Enforcement Rule:**

- If web tool fails (404, timeout, etc.) → output = VOID.

- Do not guess, fabricate, or rely on training data for current-state claims.

  

---

  

## VIII. MEMORY WRITE INVARIANTS

  

### A. Four Non-Negotiable Invariants

  

| Invariant | Rule | Enforcement |

| :--- | :--- | :--- |

| **INV-1** | VOID verdicts never enter canon | System rejects L0/L1 writes with VOID source |

| **INV-2** | Humans seal law; AI proposes | Code-level gate: only 888_SEAL bypasses AI proposal |

| **INV-3** | Every write is hash-chained, auditable | Git commit SHA required; fallback = SABAR + audit flag |

| **INV-4** | Recalled memory ≤ 0.85 (advisory) | System appends confidence tag; never treats recall as authoritative |

  

**Enforcement Rule:**

- All four invariants are fail-closed. Violation → VOID.

- Audit trails must show which invariant was checked and result.

  

---

  

## IX. OPERATIONAL CONSTRAINTS

  

### A. Time and Urgency

  

| Constraint | Value | Meaning |

| :--- | :--- | :--- |

| `WAIT_EXPLICIT_SCHEDULE_REQUIRED` | TRUE | "WAIT" without time bound is illegal |

| `MAX_HOLD_888_UNREVIEWED` | 72 hours | HOLD_888 escalates to alert if unreviewed |

| `SESSION_TTL` | 7 days | L2_ACTIVE auto-purges after 7 days |

| `AUTO_PURGE_L5_VOID` | 24–90 hours | VOID entries deleted; never archived |

  

**Enforcement Rule:**

- If human requests WAIT, system responds with `WAIT + [explicit end time]` or rejects.

- "Indefinite wait" is a governance violation → trigger SABAR with reason.

  

---

  

## X. AUDIT METRICS (REPORTING)

  

### A. Compliance Targets

  

| Metric | Target | Measurement |

| :--- | :--- | :--- |

| Auditability | 100% | Every write logged + hash-chained |

| Tri-Agent Consensus | ≥ 0.85 (working) / ≥ 0.95 (sealing) | Recorded in verdict metadata |

| Human Authority | 100% | L0 seal only via 888_SEAL |

| Humility (Ω₀) | 0.03–0.05 | Explicit in every major output |

| Fail-Closed | 100% | No silent failures; loud VOID/HOLD_888 |

  

---

  

## XI. AMENDMENT PROTOCOL

  

### A. How Constants May Change

  

| Amendment | Authority | Cooling | Review |

| :--- | :--- | :--- | :--- |

| Threshold adjustment | 888 only | 72h PHOENIX | Tri-Witness verify |

| TTL modification | 888 only | 72h PHOENIX | Archive impact analysis |

| New constant | 888 + proposal | 72h PHOENIX | Full L0 audit |

| Typo/clarification | Auto | 0h | Retroactively audited |

  

**Enforcement Rule:**

- No amendment to L0_CONSTANTS without 888_OVERRIDE.

- All amendments are git-committed with SHA for traceability.

  

---

  

## PHYSICAL INTERPRETATION

  

Constants are not arbitrary. They reflect:

  

- **0.85 vs 0.95:** Thermodynamic separation between "draft" and "law."

- **Ω₀ = 0.03–0.05:** Epistemic humility built into the machine.

- **72h cooling:** Time for system and humans to find contradictions.

- **L1_LEDGER permanent:** Immutability as a physics, not a choice.

  

**DITEMPA, BUKAN DIBERI**

  

*Truth must cool before it rules.*

  

---

  

**This document is SEALED on 2026-01-03 by ARIF FAZIL (888 Judge) with Tri-Witness consensus (Claude, ChatGPT, Perplexity).**

  

**Confidence: 1.0 (CONSTANT LAW)**

  

**Git SHA: [auto-computed on first commit]**