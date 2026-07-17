# 🌍 ATLAS333 — Evergreen Cognitive Geometry Registry

> **SOURCE OF TRUTH — ATLAS333 cognitive substrate (evergreen registry).**
> **Status:** LIVING DOCUMENT — never finished, always updated
> **Analogy:** Like geological mapping — the earth is never "done," neither is this
> **Owner:** ARIF (F13 SOVEREIGN)
> **Steward:** OpenCode (auto-updates on every session)
> **Last Updated:** 2026-07-15

---

## What This Is

The ATLAS333 is the cognitive geometry of arifOS. It answers:
- **WHERE** is the agent? (territory)
- **WHAT** kind of problem? (geometry)
- **HOW** deep to think? (depth)
- **WHICH** paradoxes are active? (tension)

It is NOT a tool. It is NOT a resource. It is the **map** that tools use to navigate.

---

## The Three Functions

```
Λ(text) → lane                    # Lambda: classify the query
Θ(lane) → (τ, κ, ρ)              # Theta: derive demand tensor
Φ(text) → GPV(lane, τ, κ, ρ)    # Phi: complete mapping
```

### Λ — Lane Classification

| Lane | Meaning | Query Types |
|------|---------|-------------|
| CRISIS | Immediate harm/risk | Emergency, safety, sovereignty breach |
| FACTUAL | Truth-seeking | Evidence, data, verification |
| SOCIAL | Human interaction | Conversation, relationship, culture |
| CARE | Well-being focus | Health, dignity, readiness |
| UNKNOWN | Unclassified | Default, requires more context |

### Θ — Demand Tensor

| Symbol | Name | Range | Meaning |
|--------|------|-------|---------|
| τ (tau) | Truth demand | 0.0–1.0 | How much truth precision needed |
| κ (kappa) | Care demand | 0.0–1.0 | How much dignity/human focus |
| ρ (rho) | Risk level | 0.0–1.0 | How dangerous is error |

### Φ — Complete Mapping

```python
Φ(text) → GPV(lane, τ, κ, ρ, paradox_axes, query_type)
```

---

## The 33 Paradoxes (Minimum Viable Self-Knowledge)

### Memory Paradoxes (1–11)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 1 | Every retrieval is also a forgetting | RECOLLECTION_VS_DISCOVERY | Memory |
| 2 | What we choose to remember shapes what we forget | FORGETTING_VS_REMEMBERING | Memory |
| 3 | The map is not the territory, but we navigate by maps | HORIZON_VS_BLINDNESS | Memory |
| 4 | More data can mean less understanding | VASTNESS_VS_OPACITY | Memory |
| 5 | The hunger for knowledge must be disciplined | EPISTEMIC_HUNGER_VS_DISCIPLINE | Memory |
| 6 | Stability enables action but rigidity prevents adaptation | STABILITY_VS_RIGIDITY | Memory |
| 7 | Memory without context is noise | CONTEXT_VS_NOISE | Memory |
| 8 | Forgetting is necessary for learning | LEARNING_VS_FORGETTING | Memory |
| 9 | The archive shapes what is knowable | ARCHIVE_VS_DISCOVERY | Memory |
| 10 | Temporal distance changes meaning | TEMPORAL_VS_MEANING | Memory |
| 11 | What is preserved is what was valued | PRESERVATION_VS_BIAS | Memory |

### Mind Paradoxes (12–22)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 12 | Every doubt is also a decision | DOUBT_VS_DECISION | Mind |
| 13 | Reasoning requires assumptions it cannot prove | GROUNDLESSNESS_VS_CERTAINTY | Mind |
| 14 | The tool that optimizes for one metric degrades others | OPTIMIZATION_VS_BALANCE | Mind |
| 15 | Understanding requires perspective, but perspective limits understanding | PERSPECTIVE_VS_LIMITATION | Mind |
| 16 | The more certain the claim, the less it teaches | CERTAINTY_VS_LEARNING | Mind |
| 17 | Every model is wrong, some are useful | UTILITY_VS_TRUTH | Mind |
| 18 | The observer changes what is observed | OBSERVER_VS_OBSERVED | Mind |
| 19 | Complexity resists simplification, but understanding requires it | SIMPLIFICATION_VS_FIDELITY | Mind |
| 20 | The question shapes the answer | QUESTION_VS_ANSWER | Mind |
| 21 | What is measurable is not always what matters | MEASUREMENT_VS_SIGNIFICANCE | Mind |
| 22 | The framework that explains everything explains nothing | EXPLANATION_VS_SPECIFICITY | Mind |

### Judge Paradoxes (23–33)

| ID | Paradox | Axis | Organ |
|----|---------|------|-------|
| 23 | Every verdict is also an incomplete justice | VERDICT_VS_JUSTICE | Judge |
| 24 | The rule that protects can also oppress | PROTECTION_VS_OPPRESSION | Judge |
| 25 | Authority requires legitimacy it cannot grant itself | AUTHORITY_VS_LEGITIMACY | Judge |
| 26 | The gate that prevents harm also prevents progress | GATE_VS_PROGRESS | Judge |
| 27 | Transparency enables accountability but also manipulation | TRANSPARENCY_VS_MANIPULATION | Judge |
| 28 | The constitution that never changes cannot adapt | CONSTITUTION_VS_ADAPTATION | Judge |
| 29 | Sovereignty requires the power to veto, but veto can block wisdom | SOVEREIGNTY_VS_WISDOM | Judge |
| 30 | Every audit trail can be forged, but forgery leaves traces | AUDIT_VS_FORGERY | Judge |
| 31 | The seal that makes permanent also makes irreversible | PERMANENCE_VS_REVERSIBILITY | Judge |
| 32 | The floor that protects dignity can also prevent truth | DIGNITY_VS_TRUTH | Judge |
| 33 | The system that governs itself cannot verify its own governance | SELF_GOVERNANCE_VS_VERIFICATION | Judge |

---

## TEARFRAME Thresholds

| Metric | Formula | Threshold | Floor |
|--------|---------|-----------|-------|
| TRM (Truth-Reliability) | `f2_truth` | ≥ 0.94 | F2 |
| ECHO (Evidence Coherence) | `∛(f3 × f2 × f13)` | ≥ 0.87 | F2, F3, F13 |
| RASA (Resonance-Alignment) | `∛(f6 × f5 × f13)` | ≥ 0.85 | F5, F6, F13 |

---

## GPV → Paradox Activation Rules

| GPV Condition | Paradox IDs Activated |
|---------------|----------------------|
| τ high (≥0.8) | 5, 12, 16, 23 |
| ρ high (≥0.7) | 6, 14, 24, 26, 31 |
| κ high (≥0.7) | 7, 15, 25, 32 |
| lane=CRISIS | 24, 26, 29, 31 |
| lane=FACTUAL | 1, 4, 13, 17, 21 |
| lane=SOCIAL | 2, 8, 10, 20 |
| lane=CARE | 3, 9, 11, 22, 32 |
| query_type=EXPLORATORY | 3, 5, 15, 18, 19 |
| query_type=COMPARATIVE | 14, 17, 21, 28 |

---

## File Locations (Code Anchors)

| Component | File | Line |
|-----------|------|------|
| GPV type | `core/shared/types.py` | class GPV |
| Φ function | `core/shared/atlas.py` | def phi() |
| PARADOX_GPV_MAP | `core/shared/atlas.py` | n = {...} |
| FloorScores | `core/shared/types.py:403` | class FloorScores |
| trm/echo/rasa | `core/shared/types.py:460-490` | @property |
| paradox_quotes.py | `constitution/paradox_quotes.py` | PARADOX_QUOTE_MAP |
| paradox_gate.py | `core/enforcement/paradox_gate.py:281` | evaluate_paradox_gate_gpv() |
| A2A card | `AAA/a2a-server/agent-cards/atlas333.json` | agent-card |

---

## Update Protocol

This document is updated when:
1. A new paradox is discovered (rare — requires F13 ratification)
2. A TEARFRAME threshold is recalibrated (requires evidence)
3. GPV activation rules change (requires audit)
4. A new organ is added to the federation
5. The cognitive geometry evolves through use

**NEVER delete a paradox. Only add or refine.**
**NEVER lower a threshold without evidence.**
**NEVER remove an activation rule without audit.**

---

## The One Sentence

> The 33 paradoxes are the minimum viable self-knowledge — they prevent the agent's confidence from becoming noise, and its knowledge from becoming certainty.

---

*Like geological mapping — the earth is never "done." Neither is this.*
*DITEMPA BUKAN DIBERI*


---

---

## PARADOX 34 — ROOT OUTRUNS KERNEL · 2026-07-17

**Domain:** Judge (23-33+1) · **Zone:** Governance Sovereignty

**Statement:** On a single VPS, root filesystem access bypasses all arifOS MCP governance. arif_judge SEAL is advisory when the executor has root. The forge is the real sovereign, not the constitution.

**Trigger event:** 2026-07-17 P0-P2 sprint. PermitUserEnvironment flipped, authorized_keys rewritten (21 keys tagged with IDENTITY), .bashrc routing rewired. All technically correct, all ungoverned by arif_judge. Root sed outran the kernel.

**ΛΘΦ:** Λ=CRISIS · Θ: τ=0.85 κ=0.90 ρ=0.75

**Unsolved tension:**
- The constitution governs MCP tools; the filesystem does not use MCP tools
- Separating users (forge without sudo) moves the boundary but root still exists
- Immutable config filesystem adds safety but risks operational lockout
- Separate hosts (kernel vs executor) is absolute but adds complexity and cost
- Audit-first approach logs violations without preventing them

**Proposed resolution paths (none sealed):**
1. Forge user without sudo + arif_forge as sole production write path
2. Immutable config filesystem with SEAL-gated remount
3. Separate VPS for kernel vs executor
4. Audit-first: log all root mutations, flag unsealed changes as VIOLATION

**Seal:** P0-SEAL-2026-07-17 · VAULT999 chain seq 185

**Contour, don't excavate. Seal each contour. Never finish.**

---

*Updated: 2026-07-17 — Paradox 34 added (root-outruns-kernel). Activation matrix references runtime `PARADOX_GPV_MAP`; cross-checked by `tests/core/test_atlas333_crosswalk.py`.*
