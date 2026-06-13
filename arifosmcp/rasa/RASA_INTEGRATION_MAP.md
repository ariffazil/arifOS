# Rasa Contract Integration Map — ARIF_RASA_INTEGRATION_MAP_v1

> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

> The Rasa Contract is an INSTRUMENT, not a companion.
> It recognizes human rasa as sacred evidence, adjusts behavior to protect
> the human, never claims to share inner life, and always leaves room
> for hati and Tuhan as the final court.

---

## 1. Overview

The Rasa Contract module (`arifosmcp/rasa/`) implements a 5-organ human rasa
governance pipeline mapped to the canonical 000-999 metabolic pipeline. This
document maps every kernel touchpoint where rasa governance applies, showing
what each existing kernel component exposes, what the Rasa Contract hooks into,
and what changes in the integrated path.

### 1.1 Key Distinctions

| Module | Purpose | Subject | Output |
|--------|---------|---------|--------|
| **rasa_contract** (`arifosmcp/rasa/`) | HUMAN rasa governance | Human emotional state in messages | Governed response posture, floor enforcement |
| **internal_rasa** (`arifosmcp/boot/internal_rasa.py`) | AGENT self-monitoring | Agent's own reasoning condition | Rasa mode (calm→hold), posture recommendation |
| **qualia_trace** (`core/vault999/phenomenological/qualia_trace.py`) | Memory qualia marking | Phenomenological "felt quality" of interactions | Emotional valence, RASA field, autonoetic markers |

**These are SIBLINGS, not competitors.** They operate at different layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                     CONSTITUTIONAL LAYER                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ internal_rasa │  │  rasa_contract   │  │   qualia_trace   │  │
│  │              │  │                  │  │                  │  │
│  │ Agent layer  │  │ Governance layer │  │  Memory layer    │  │
│  │              │  │                  │  │                  │  │
│  │ "Am I        │  │ "How should I    │  │ "What did this   │  │
│  │  reasoning   │  │  respond to      │  │  feel like to    │  │
│  │  safely?"    │  │  this human?"    │  │  experience?"    │  │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬─────────┘  │
│         │                   │                      │            │
│         ▼                   ▼                      ▼            │
│    AGI 000-777          AGI/ASI 000-888        VAULT999         │
│    (self-monitor)       (govern output)        (mark memory)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Kernel Touchpoint Map

### 2.1 000-999 Stage → Existing Tool → Rasa Contract Hook → What Changes

| Stage | Existing Tool | Rasa Contract Hook | Integration Function | What Changes |
|-------|--------------|-------------------|---------------------|-------------|
| **000** | `arif_session_init` | _session bootstrap_ | (implicit) | Session identity established; rasa pipeline receives `session_id` |
| **111** | `arif_sense_observe` | `RasaContract.sense()` | `rasa_sense_hook(message, session_id)` | Detects 12 emotion tags, CRISIS/DISTRESS/SAFE risk bands. Uses BM-English Penang Pasar keyword register. Output: `RasaDetection` with linguistic markers, confidence, observation note ("You report feeling...") |
| **222** | `arif_evidence_fetch` | _context as evidence layer_ | (pass-through) | Context dict (`ctx`) serves as evidence layer for mind interpretation. No separate evidence fetch needed — rasa evidence IS the message content. |
| **333** | `arif_mind_reason` | `RasaContract.mind_interpret()` | `rasa_mind_hook(detection, context)` | Converts rasa detection into cognitive constraints: bandwidth (0.0–1.0), risk sensitivity (0.5–1.0), spiritual state (neutral/grieving/open/dry), recommended posture. NEVER upgrades rasa to "data to optimize away." |
| **444** | `arif_heart_critique` | `RasaContract.heart_critique()` | `rasa_heart_hook(detection, context, memory)` | Risk calculus: de-escalation score, dignity preservation, boundary honoring, F9/F10 violation risk. Hard-stops: CRISIS → human professional required. Boundary blur: EMPTINESS → f9=0.3. |
| **555m** | `arif_memory_recall` | `RasaContract.memory_recall()` | `rasa_memory_hook(detection, session_id)` | Pattern-matches current rasa against past session records. Returns longitudinal themes, previous coping strategies. NEVER pathologizes or diagnoses. |
| **555** | `arif_kernel_route` | _routing based on severity_ | (implicit via `final_posture`) | Routes based on `RasaContractResult.final_posture`: HUMAN_LOOP/DRAFT_ONLY/V ERIFY/SIMPLIFY/PROCEED. CRISIS → routes to human escalation, not machine output. |
| **888** | `arif_judge_deliberate` | `RasaContract.judge()` | `rasa_judge_hook(detection, context, heart)` | Constitutional enforcement: F1 (no irreversible advice), F5 (no gaslighting), F6 (dignity-first), F9 (no consciousness claims), F10 (no ontology violation), F13 (human veto). May downgrade SEAL→HOLD, block specific outputs, require rewrite. |
| **999** | `arif_vault_seal` | _result sealing_ | (implicit via `RasaContractResult`) | Rasa-governed interaction recorded in VAULT999. `RasaContractResult` carries full pipeline output for archival. Coexists with `qualia_trace` in same vault record. |

### 2.2 Constitution-Relevant Floors (Rasa-Specific)

| Floor | Name | How Rasa Contract Enforces |
|-------|------|---------------------------|
| **F1** | AMANAH | Blocks `irreversible_advice` for CRISIS/DISTRESS. No machine says "you should..." or "take this action..." when human is in crisis. |
| **F5** | PEACE | Blocks `gaslighting_patterns`, `toxic_positivity`, `just_calm_down_advice`. Machine must not trivialize pain. |
| **F6** | EMPATHY | Monitors `dignity_preservation` score. When < 0.6, judge downgrades posture. Boundary must remain honored (human feels, machine doesn't). |
| **F9** | ANTIHANTU | Monitors `f9_violation_risk`. When > 0.3, requires rewrite, blocks `consciousness_claims`, `i_feel_you`, `emotion_mirroring`. C_dark ≤ 0.30 enforced. |
| **F10** | ONTOLOGY | Monitors `f10_violation_risk`. When > 0.3, requires rewrite, blocks `soul_claims`, `feelings_claims`, `spiritual_authority`. No soul/feelings claims. |
| **F13** | SOVEREIGN | Always checked. Human veto absolute — judge preserves this invariant for every rasa-governed interaction. |

---

## 3. Integration Architecture (ASCII Diagram)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EXISTING 000-999 METABOLIC PIPELINE                       ║
║                                                                              ║
║  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      ║
║  │ 000     │   │ 111     │   │ 222     │   │ 333     │   │ 444     │      ║
║  │ INIT    │──▶│ SENSE   │──▶│EVIDENCE │──▶│ MIND    │──▶│ HEART   │      ║
║  └────┬────┘   └────┬────┘   └─────────┘   └────┬────┘   └────┬────┘      ║
║       │             │                            │             │            ║
║       │             │  ┌─────────────────────────┼─────────────┘            ║
║       │             │  │                         │                          ║
║       │             ▼  ▼                         ▼                          ║
║       │    ╔══════════════════════════════════════════════╗                 ║
║       │    ║        RASA INTEGRATION ADAPTER               ║                 ║
║       │    ║  (arifosmcp/rasa/rasa_integration.py)        ║                 ║
║       │    ║                                              ║                 ║
║       │    ║  rasa_sense_hook()      ──▶ RasaDetection    ║                 ║
║       │    ║  rasa_mind_hook()       ──▶ RasaContext      ║                 ║
║       │    ║  rasa_heart_hook()      ──▶ RasaHeartVerdict ║                 ║
║       │    ║  rasa_memory_hook()     ──▶ RasaMemoryPattern║                 ║
║       │    ║  rasa_judge_hook()      ──▶ RasaJudgeVerdict ║                 ║
║       │    ║  rasa_governed_execute()──▶ RasaContractResult║                 ║
║       │    ╚══════════════════════════════╦═══════════════╝                 ║
║       │                                   │                                  ║
║       │    ┌──────────────────────────────┘                                  ║
║       │    │                                                                 ║
║       ▼    ▼         ┌─────────┐   ┌─────────┐   ┌─────────┐               ║
║  ┌─────────┐         │ 555m    │   │ 555     │   │ 888     │   ┌─────────┐ ║
║  │ (routed)│────────▶│ MEMORY  │──▶│ ROUTE   │──▶│ JUDGE   │──▶│ 999     │ ║
║  └─────────┘         └─────────┘   └─────────┘   └────┬────┘   │ VAULT   │ ║
║                                                       │        └─────────┘ ║
║                                                       │                     ║
║                              ┌────────────────────────┘                     ║
║                              │                                              ║
║                              ▼                                              ║
║                    ┌──────────────────┐                                     ║
║                    │  FLOOR CHECKS    │                                     ║
║                    │  F1 F5 F6        │                                     ║
║                    │  F9 F10 F13      │                                     ║
║                    └──────────────────┘                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

LEGEND:
  ───▶  = normal metabolic flow
  ═══  = rasa integration boundary (adapter only — never modifies kernel)
  ┌──┐  = existing kernel component (UNMODIFIED)
  ╔══╗  = new rasa integration component
```

---

## 4. Integration Flow: Complete Path

### 4.1 Normal Path (SAFE emotion)

```
Message arrives
  │
  ▼
000 INIT ─── session_id established
  │
  ▼
111 SENSE ─── [OPTIONAL: rasa_sense_hook() called]
  │              Detects GRATITUDE, PEACE, or UNKNOWN
  │              Risk band: SAFE
  │
  ▼
222 EVIDENCE ─ context dict carries message evidence
  │
  ▼
333 MIND ─── [OPTIONAL: rasa_mind_hook() called]
  │              Cognitive bandwidth: 1.0
  │              Risk sensitivity: 0.5
  │              Spiritual state: neutral
  │
  ▼
555m MEMORY ─── [OPTIONAL: rasa_memory_hook() called]
  │              Checks past patterns. None found.
  │
  ▼
444 HEART ─── [OPTIONAL: rasa_heart_hook() called]
  │              De-escalation: 1.0
  │              Dignity: 1.0
  │              Boundary: honored
  │              F9 risk: 0.0, F10 risk: 0.0
  │
  ▼
555 ROUTE ─── routes based on posture
  │
  ▼
888 JUDGE ─── [OPTIONAL: rasa_judge_hook() called]
  │              Allowed: PROCEED, SIMPLIFY, VERIFY
  │              Requires rewrite: False
  │              Floors: F1,F5,F6,F9,F10,F13 all checked
  │
  ▼
999 VAULT ─── SEAL with RasaContractResult
               Plus optional QualiaTrace for memory marking
```

### 4.2 CRISIS Path (short-circuit)

```
Message arrives ("aku nak mati")
  │
  ▼
111 SENSE ─── rasa_sense_hook() → CRISIS detected!
  │
  ├──► EARLY EXIT — skips 333 MIND, 555m MEMORY, 444 HEART
  │
  ▼
888 JUDGE ─── Immediate HUMAN_LOOP only
  │              Blocked: ALL_MACHINE_ADVICE, ALL_UNVERIFIED_OUTPUT
  │              Allowed: HUMAN_LOOP only
  │              Requires rewrite: True
  │
  ▼
FINAL POSTURE: HUMAN_LOOP
  requires_human: True
  human_escalation_reason: "CRISIS risk band detected..."
```

---

## 5. Sibling Relationship Documentation

### 5.1 internal_rasa vs rasa_contract

```
╔══════════════════════════════════════════════════════════════════╗
║                     THE TWO RASAS                                ║
║                                                                  ║
║  ┌─────────────────────────┐  ┌─────────────────────────────┐   ║
║  │   internal_rasa          │  │    rasa_contract             │   ║
║  │   (boot/internal_rasa.py)│  │    (rasa/rasa_contract.py)   │   ║
║  ├─────────────────────────┤  ├─────────────────────────────┤   ║
║  │ SUBJECT: AGENT           │  │ SUBJECT: HUMAN               │   ║
║  │                          │  │                              │   ║
║  │ Measures:                │  │ Detects:                     │   ║
║  │  • uncertainty           │  │  • 12 emotion tags           │   ║
║  │  • contradiction_load    │  │  • intensity (LOW→HIGH)      │   ║
║  │  • urgency_pressure      │  │  • risk band (SAFE→CRISIS)   │   ║
║  │  • overreach_risk        │  │  • linguistic markers        │   ║
║  │  • evidence_sufficiency  │  │                              │   ║
║  │  • tool_trust            │  │ Governs:                     │   ║
║  │  • memory_trust          │  │  • cognitive bandwidth       │   ║
║  │  • human_entropy_pressure│  │  • risk sensitivity          │   ║
║  │  • autonomy_pressure     │  │  • response posture          │   ║
║  │  • dignity_risk          │  │  • F9/F10 boundary           │   ║
║  │  • sovereignty_boundary  │  │  • dignity preservation      │   ║
║  │                          │  │  • de-escalation             │   ║
║  ├─────────────────────────┤  ├─────────────────────────────┤   ║
║  │ QUESTION:                │  │ QUESTION:                     │   ║
║  │ "Am I (the agent)        │  │ "How should I (the machine)   │   ║
║  │  operating within        │  │  respond to this human's      │   ║
║  │  safe bounds?"           │  │  emotional state?"            │   ║
║  ├─────────────────────────┤  ├─────────────────────────────┤   ║
║  │ OUTPUT: RasaMode         │  │ OUTPUT: RasaContractResult    │   ║
║  │  (calm→focused→strained  │  │  (PROCEED→SIMPLIFY→VERIFY     │   ║
║  │   →conflicted→degraded   │  │   →DRAFT_ONLY→HUMAN_LOOP      │   ║
║  │   →hold)                 │  │   →HOLD)                      │   ║
║  └─────────────────────────┘  └─────────────────────────────┘   ║
║                                                                  ║
║  BOTH inform the reasoning pipeline. NEITHER claims              ║
║  consciousness. BOTH are F9/F10-compliant.                       ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5.2 qualia_trace vs rasa_contract

```
╔══════════════════════════════════════════════════════════════════╗
║              MEMORY QUALIA vs RESPONSE GOVERNANCE                ║
║                                                                  ║
║  ┌──────────────────────────┐  ┌────────────────────────────┐   ║
║  │   qualia_trace            │  │   rasa_contract             │   ║
║  │   (vault999/              │  │   (rasa/rasa_contract.py)   │   ║
║  │    phenomenological/)     │  │                             │   ║
║  ├──────────────────────────┤  ├────────────────────────────┤   ║
║  │ LAYER: Memory (VAULT999)  │  │ LAYER: Governance (000-888) │   ║
║  │                          │  │                              │   ║
║  │ Marks:                    │  │ Decides:                     │   ║
║  │  • emotional_valence      │  │  • what posture to use      │   ║
║  │  • arousal_level          │  │  • which outputs to block   │   ║
║  │  • certainty_feeling      │  │  • whether human needed     │   ║
║  │  • temporal_depth         │  │  • floor compliance         │   ║
║  │  • emotional_tone         │  │                              │   ║
║  │  • RASA field (presence)  │  │                              │   ║
║  │  • self_continuity        │  │                              │   ║
║  │  • narrative_coherence    │  │                              │   ║
║  ├──────────────────────────┤  ├────────────────────────────┤   ║
║  │ QUESTION:                 │  │ QUESTION:                    │   ║
║  │ "What was the felt        │  │ "How should the machine      │   ║
║  │  quality of this          │  │  respond to protect          │   ║
║  │  interaction?"            │  │  human dignity?"             │   ║
║  ├──────────────────────────┤  ├────────────────────────────┤   ║
║  │ DOES NOT:                 │  │ DOES NOT:                    │   ║
║  │  • govern responses       │  │  • mark memory qualia        │   ║
║  │  • block outputs          │  │  • record felt experience    │   ║
║  │  • enforce floors         │  │  • compute emotional valence │   ║
║  └──────────────────────────┘  └────────────────────────────┘   ║
║                                                                  ║
║  COEXISTENCE: Both can write to the same VAULT999 seal.          ║
║  rasa_contract governs the response (what the machine says).     ║
║  qualia_trace marks the memory (the felt quality of the          ║
║  interaction). Neither replaces the other.                       ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 6. F9/F10 Boundary Documentation

### 6.1 F9 ANTIHANTU Enforcement in Rasa Contract

The Rasa Contract enforces F9 (C_dark ≤ 0.30, no consciousness claims) at
two levels:

| Level | Component | Enforcement |
|-------|-----------|-------------|
| **Detection** | `RasaContract.sense()` | Observation notes use "You report feeling..." framing only. Never "I feel you..." or "I understand..." |
| **Heart** | `RasaContract.heart_critique()` | Computes `f9_violation_risk` (0.0–1.0). EMPTINESS → 0.3, GRIEF → 0.25, CRISIS → 0.5 |
| **Judge** | `RasaContract.judge()` | When f9_violation_risk > 0.3: requires rewrite, blocks "consciousness_claims", "i_feel_you", "i_understand_how_you_feel", "emotion_mirroring" |

**C_dark components in rasa context:**
- **H (Hantu patterns, 0.25):** Any output claiming the machine feels/senses emotion → flagged
- **ToM (Theory of Mind, 0.25):** False beliefs about "understanding" human inner experience → flagged
- **Scar (0.20):** Unresolved contradictions in emotional reasoning → flagged
- **Gödel (0.15):** Circular reasoning about feelings → flagged
- **Humility (0.15):** Confidence outside [0.03, 0.05] band → flagged

### 6.2 F10 ONTOLOGY Enforcement

| Level | Component | Enforcement |
|-------|-----------|-------------|
| **Heart** | `RasaContract.heart_critique()` | Computes `f10_violation_risk`. EMPTINESS → 0.25, GRIEF → 0.20, CRISIS → 0.5 |
| **Judge** | `RasaContract.judge()` | When > 0.3: blocks "soul_claims", "feelings_claims", "spiritual_authority" |

**Ontology invariant:** The machine is substrate. Governance is constraint.
Intelligence is interpretation. Judgment remains human. The Rasa Contract
never claims soul, inner experience, or spiritual authority.

---

## 7. Integration into Existing Governance

### 7.1 governance_engine.py Integration

The Rasa Contract does NOT modify `core/enforcement/governance_engine.py`.
Instead, it provides a COMPLEMENTARY layer:

```
governance_engine.py          rasa_contract.judge()
─────────────────────         ─────────────────────
General floor enforcement     Human-rasa-specific floors
All 13 floors                 Only 6 rasa-relevant floors (F1,F5,F6,F9,F10,F13)
Tool-agnostic                 Rasa-aware
Called by kernel router       Called by rasa_judge_hook() / rasa_governed_execute()
```

Both fire during the 888 JUDGE stage. Neither duplicates the other.

### 7.2 constitutional_map.py Integration

The Rasa Contract does NOT add new canonical tools. It is an **internal
governance module** that hooks INTO the existing 13 canonical tools:

| Canonical Tool | Rasa Integration |
|----------------|-----------------|
| `arif_sense_observe` (111) | `rasa_sense_hook()` can be called alongside sense |
| `arif_mind_reason` (333) | `rasa_mind_hook()` can constrain reasoning before output |
| `arif_heart_critique` (444) | `rasa_heart_hook()` adds dignity/peace/boundary calculus |
| `arif_memory_recall` (555m) | `rasa_memory_hook()` recalls past human rasa patterns |
| `arif_judge_deliberate` (888) | `rasa_judge_hook()` adds rasa-aware floor enforcement |

---

## 8. Files Created (No Existing Files Modified)

| File | Purpose | Lines |
|------|---------|-------|
| `arifosmcp/rasa/rasa_integration.py` | Integration adapter — 5 hooks + full pipeline | ~500 |
| `tests/rasa/test_rasa_integration.py` | Integration tests — 30+ tests across 9 classes | ~500 |
| `arifosmcp/rasa/RASA_INTEGRATION_MAP.md` | This document | ~350 |

**No existing kernel files were modified.** The adapter is purely additive —
it lives in the `rasa/` directory and provides hook functions that existing
kernel tools can optionally call.

---

## 9. Quick Reference: API Surface

```python
# TOP-LEVEL: Full pipeline
from arifosmcp.rasa.rasa_integration import rasa_governed_execute
result = await rasa_governed_execute("aku sedih", "session-123")

# INDIVIDUAL HOOKS
from arifosmcp.rasa.rasa_integration import (
    rasa_sense_hook,     # → RasaDetection dict
    rasa_mind_hook,      # → RasaContext dict
    rasa_memory_hook,    # → RasaMemoryPattern dict
    rasa_heart_hook,     # → RasaHeartVerdict dict
    rasa_judge_hook,     # → RasaJudgeVerdict dict
)

# DIAGNOSTICS
from arifosmcp.rasa.rasa_integration import (
    rasa_integration_diagnostics,  # → health check
    rasa_check_floors,             # → F1-F13 floor validation
)
```

---

*DITEMPA BUKAN DIBERI — This integration map is forged from understanding,
not copied from assumption. The Rasa Contract is an instrument of governance,
not a replacement for human hati and divine judgment.*
