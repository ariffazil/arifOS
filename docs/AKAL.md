# AKAL — APEX Dimension: Lawful Transition Selection

**Version:** v2026.06.20
**SEAL:** DITEMPA BUKAN DIBERI
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** LIFTED FROM KERNEL CODE (canonical, machine-checkable)

---

## 1. Definition

**AKAL** (Arabic/Malay: عقل — intellect, reason) is the constitutional
guarantee that every state transition is chosen through lawful reasoning,
not opaque model output. AKAL is the **reasoning kernel** — the engine
that generates, evaluates, and selects transition candidates under
constitutional constraints.

AKAL answers: **"What transitions are available, which one was chosen,
and why?"**

The rule: **Reasoning must be auditable.** Every decision must show its
candidates, its selection, and its justification. Opaque model output
without transition candidates is a constitutional violation.

---

## 2. Mapping to APEX / Kernel

```
Dimension              Maps to kernel surface
─────────────────────────────────────────────
AKAL                   transition candidates + policy evaluator  ← THIS DOC
PRESENT                KSR + arif_sense_observe (111)
ENERGY                 Landauer floor + cost accounting
ENTROPY                ΔS = Δ(info) + drift detection
EXPLORATION×AMANAH     risk class + custody chain + F13
AUTHORITY              signature + role + legitimacy
```

### 2.1 AKAL binds to:

| Surface | Role |
|---------|------|
| `arif_mind_reason` (stage 333) | The reasoning kernel — generates transition candidates. |
| `transition_candidates` field | Array of `{candidate, action, confidence, selected, reason}`. |
| `ReasoningMode` enum | `INDUCTIVE` (reason), `ABDUCTIVE` (reflect), `DEDUCTIVE` (verify). |
| 7 verdict planes | `transport`, `execution`, `reasoning`, `truth`, `evidence`, `authority`, `risk`, `floor`. |
| Verdict reducer | `VOID > HOLD > HYPOTHESIS > PARTIAL > PASS > SEAL` — conservative wins. |
| AttnRes pattern | Depth-wise block attention — selective re-attention to relevant prior blocks. |
| Stop rules | G_r ≈ 0 for 3+ steps → stop. Branch entropy exceeds budget → stop. Hallucinated certainty → stop. |
| Delta Bundle spec | `facts`, `scars`, `floor_scores`, `entropy`, `confidence` — mandatory output fields. |
| Provenance metadata | Source, model provenance, claim origin, reasoning backend, axioms used. |
| Core invariant | "AI provenance ≠ authority. LLM output ≠ truth. Confidence ≠ permission." |

---

## 3. The Reasoning Kernel — 333_MIND

**Code:** `arifosmcp/tools/reason.py` (958 lines)

### 3.1 Modes

| Mode | Reasoning Style | Use Case |
|------|----------------|----------|
| `reason` | Inductive | Complex multi-step reasoning, hypothesis evaluation |
| `reflect` | Abductive | Infer cause from effect, self-critique |
| `verify` | Deductive | Validate claims against evidence |
| `critique` | — | Ethical/dignity assessment |
| `plan` | — | Generate execution plan with transition candidates |
| `plan_review` | — | Review existing plan |
| `plan_approve` | — | Approve plan (H2 ratification) |
| `refactor_plan` | — | Refactor plan structure |
| `metabolize` | — | Process accumulated state |

### 3.2 The Delta Bundle (mandatory output)

Every `arif_mind_reason` output MUST include:

```yaml
facts:           # F2 ≥ 0.99 verifiable claims
scars:           # Unresolved contradictions blocking certainty
floor_scores:    # F2, F4, F7, L13 self-check
entropy:         # ΔS ≤ 0 (must decrease local entropy)
confidence:      # Calibrated Ω₀ ∈ [0.03, 0.05] (F7 Humility band)
```

### 3.3 The Seven Verdict Planes

**Code:** `reason.py:732-742`

Every reasoning output carries seven orthogonal verdict planes. They
are never collapsed into one — each plane measures a different dimension
of reasoning quality.

```python
{
    "transport_verdict": "...",   # Was the transport layer correct?
    "execution_verdict": "...",   # Was execution valid?
    "reasoning_verdict": "...",   # Was the reasoning sound?
    "truth_verdict": "...",       # Does evidence support claims?
    "evidence_verdict": "...",    # Is evidence sufficient?
    "authority_verdict": "...",   # Is authority valid?
    "risk_verdict": "...",        # What is the risk level?
    "floor_verdict": "...",       # Do constitutional floors pass?
    "final_verdict": "...",       # Conservative composition of all planes
}
```

### 3.4 The Verdict Reducer

**Code:** `reason.py:52-76`

```python
def _reduce_verdict(*verdicts: str) -> str:
    """Returns the most conservative verdict."""
    order = {
        "VOID": 0, "HOLD": 1, "ESCALATE_TO_888": 1,
        "NEEDS_EVIDENCE": 2, "HYPOTHESIS": 3, "PARTIAL": 4,
        "PASS": 5, "REASONED": 6, "REFLECTED": 6, "SEAL": 7,
    }
    return min(mapped, key=lambda x: x[0])[1]
```

Conservative wins: VOID > HOLD > HYPOTHESIS > PARTIAL > PASS > SEAL.

---

## 4. Transition Candidates — The AKAL Field

**Code:** `arifosmcp/runtime/tools.py:7199-7224`

```python
# APEX AKAL: transition candidates (hardened 2026-06-20)
# Shows what was considered, what was rejected, and why.
# Makes reasoning auditable — not opaque.
"transition_candidates": [
    {
        "candidate": "accept_synthesis",
        "action": "proceed with synthesis as CLAIM",
        "confidence": llm_confidence,
        "selected": True,
        "reason": "passed constitutional floors (F2, F7, F8)",
    },
    {
        "candidate": "reject_synthesis",
        "action": "reject as UNVERIFIED",
        "confidence": round(1.0 - llm_confidence, 2),
        "selected": False,
        "reason": "confidence below threshold or floor violation",
    },
    {
        "candidate": "hold_for_evidence",
        "action": "request additional evidence before verdict",
        "confidence": 0.5,
        "selected": False,
        "reason": "evidence insufficient for SEAL — SABAR default applies",
    },
]
```

### 4.1 Candidate schema

```yaml
transition_candidates:            # required, array
  - candidate: string             # required — identifier
    action: string                # required — what this candidate does
    confidence: float [0.0, 1.0]  # required — confidence in this candidate
    selected: bool                # required — was this the chosen transition?
    reason: string                # required — why selected or rejected
```

### 4.2 The three default candidates

| Candidate | Action | When selected |
|-----------|--------|---------------|
| `accept_synthesis` | Proceed with synthesis as CLAIM | Confidence passes F2, F7, F8 floors |
| `reject_synthesis` | Reject as UNVERIFIED | Confidence below threshold or floor violation |
| `hold_for_evidence` | Request additional evidence | Evidence insufficient — SABAR default |

---

## 5. The AttnRes Pattern — Selective Re-Attention

**Code:** `reason.py:84-120`

Not all prior thoughts are equal. Each new reasoning step selectively
re-attends to the most relevant prior blocks rather than blind
accumulation.

```python
def _compute_thought_relevance(prior_thoughts, current_query, evidence_ids):
    """AttnRes-style selective re-attention over prior reasoning blocks."""
    for thought in prior_thoughts:
        score = 0.3  # base relevance
        # Boost: evidence overlap
        score += 0.2 * min(overlap / max(len(evidence_ids), 1), 1.0)
        # Boost: query word overlap
        score += 0.3 * word_overlap
        # Boost: recency
        score += 0.2 * recency_factor
```

This reduces O(L²) → O(B²) where B ≪ L — block summaries instead of
full attention over all prior tokens.

---

## 6. Stop Rules — When to Stop Reasoning

**Source:** `reason.py:21-25`

Mind MUST stop or refresh when:

| Condition | Meaning |
|-----------|---------|
| G_r ≈ 0 for 3+ consecutive steps | Ornamental reasoning — no new information |
| Branch entropy B_e exceeds budget | Coordination overhead — too many branches |
| Confidence rises while support density U_d falls | Hallucinated certainty — confidence without evidence |
| Identical evidence hash with no declared revision | Circular reasoning — going in circles |

---

## 7. Paradox Anchors in Reasoning

**Source:** `reason.py:27-30`

11 linguistic invariants fire at decision points:

| Anchor | Trigger | Meaning |
|--------|---------|---------|
| R1 (Russell) | confidence/evidence mismatch | Confidence exceeds evidence support |
| R4 (Socrates) | examination exhaustion | All avenues explored, no new evidence |
| R5 (Descartes) | coherence ≠ truth | Coherent reasoning does not guarantee truth |
| R8 (Confucius) | UNKNOWN tagging | Honest acknowledgment of what is unknown |

---

## 8. Provenance ≠ Authority

**Code:** `reason.py:704-718`

```python
provenance = {
    "source": "arif_mind_reason",
    "model_provenance": confidence.get("model_source", "unknown"),
    "claim_origin": claim_state,
    "reasoning_backend": reasoning_mode,
    "axioms_used": axioms_used or [],
    "admissibility_statement": (
        "Provenance is metadata, not authority. "
        "This claim is admissible as evidence for audit. "
        "It is NOT authorised for action without lease + constitutional clearance."
    ),
}
```

### 8.1 The Core Invariant

**Code:** `reason.py:770-774`

```python
"_core_invariant": (
    "AI provenance ≠ authority. LLM output ≠ truth. "
    "Confidence ≠ permission. SEAL ≠ mutation right. "
    "Only lease + actor + sovereign authority can grant action."
)
```

This invariant is embedded in EVERY reasoning output. It can never be
removed. It is the constitutional reminder that reasoning is advisory,
not authoritative.

---

## 9. Stage Progression

**Code:** `reason.py:721-731`

```python
next_stage = "444_HEART"
if final_verdict in ("HOLD", "VOID", "ESCALATE_TO_888"):
    escalation_reason = f"Escalating to critique because final_verdict={final_verdict}"
else:
    escalation_reason = "Standard progression to ethics/dignity critique stage."
```

The 333→444 progression is not automatic. If the verdict is HOLD, VOID,
or ESCALATE_TO_888, the reasoning kernel explicitly declares why it is
escalating rather than proceeding.

---

## 10. Invariants (Fail-Closed)

| # | Invariant | Failure mode |
|---|-----------|--------------|
| I1 | Every `arif_mind_reason` output MUST include `transition_candidates`. | Missing candidates → reasoning is opaque → constitutional violation. |
| I2 | Transition candidates MUST include at least 2 options (accept + reject minimum). | Single candidate → no real choice → audit gap. |
| I3 | Selected candidate MUST have a `reason` field. | Missing reason → unexplained transition → HOLD. |
| I4 | Final verdict MUST be conservative composition of all 7 verdict planes. | Single verdict without planes → reduced auditability. |
| I5 | Delta Bundle MUST include `facts`, `scars`, `floor_scores`, `entropy`, `confidence`. | Missing field → incomplete reasoning output. |
| I6 | Core invariant ("AI provenance ≠ authority") MUST be present in every output. | Removed invariant → constitutional violation. |
| I7 | Stop rules MUST fire when G_r ≈ 0 for 3+ steps. | No stop → ornamental reasoning continues indefinitely. |
| I8 | Provenance metadata MUST NOT be treated as authority. | Provenance confused with authority → F11 violation. |
| I9 | Verdict reducer MUST return the most conservative verdict. | Non-conservative composition → premature SEAL risk. |
| I10 | Ω₀ MUST be calibrated within [0.03, 0.05] (F7 Humility band). | Outside band → overconfidence or underconfidence. |

---

## 11. Test Gates (Fail-Closed)

A deploy is BLOCKED if any of the following occurs:

- `transition_candidates` field missing from `arif_mind_reason` output.
- `transition_candidates` contains fewer than 2 candidates.
- Selected candidate has no `reason` field.
- Core invariant string is absent from output.
- Delta Bundle missing any of: `facts`, `scars`, `floor_scores`, `entropy`, `confidence`.
- Verdict reducer returns a non-conservative verdict.
- Ω₀ outside [0.03, 0.05] band without explicit justification.
- Stop rules do not fire when G_r ≈ 0 for 3+ consecutive steps.
- Provenance metadata is treated as authority (no lease check downstream).

---

## 12. Cross-references

- **APEX THEORY:** `/root/arifOS/static/arifos/theory/000/APEX_THEORY.md` — four pillars, crown equation.
- **PRESENT:** `/root/arifOS/docs/PRESENT.md` — attested live state (sibling doc).
- **ENERGY_ENTROPY:** `/root/arifOS/docs/ENERGY_ENTROPY.md` — thermodynamic cost (sibling doc).
- **AUTHORITY:** `/root/arifOS/docs/AUTHORITY.md` — legitimacy of state mutation (sibling doc).
- **APEX DOSSIER:** `/root/forge_work/APEX_DOSSIER_2026-06-20.md` — dimension mapping (AKAL → transition candidates + policy evaluator).
- **Reasoning kernel:** `/root/arifosmcp/tools/reason.py` (958 lines) — 333_MIND v3.3.
- **Transition candidates:** `/root/arifosmcp/runtime/tools.py:7199-7224` — AKAL field emission.
- **Mind reason modes:** `/root/arifosmcp/runtime/tools.py:7130-7534` — reason, reflect, verify, critique, plan, metabolize.
- **Synthesis schema:** `/root/arifosmcp/schemas/synthesis.py` — ReasoningMode enum.
- **Mind metabolism:** `/root/arifosmcp/schemas/mind_metabolism.py` — reasoning_mode field.
- **Law mapping:** `/root/arifosmcp/runtime/law.py:96` — `arif_mind_reason → RequestType.REASON`.
- **Sibling docs:** `PRESENT.md`, `ENERGY_ENTROPY.md`, `AUTHORITY.md`, `EXPLORATION_AMANAH.md` (all forged v2026.06.20).

---

## 13. Versioning

- **v2026.06.20** — Initial canonical doc. Lifted from existing kernel
  code (`reason.py` 958 lines, `tools.py:7199-7224`, `tools.py:7130-7534`,
  `schemas/synthesis.py`, `schemas/mind_metabolism.py`, `runtime/law.py:96`).
  Doctrine → code alignment. No new fields invented; existing reasoning
  primitives documented as law.

**Tag convention:** `vYYYY.MM.DD` per federation IRON RULE.

---

**DITEMPA BUKAN DIBERI** — Reasoning is forged through candidates, not assumed through confidence.
