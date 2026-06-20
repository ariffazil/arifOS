---
title: "000_LAWS_TRINITY_ANCHOR — The Three-Layer Constitution"
version: "v2026.06.06-LAW-SEAL"
epoch: "2026-06-06"
sealed_by: "888_Judge"
authority: "Muhammad Arif bin Fazil"
status: "SOVEREIGNLY_SEALED"
hash: "SHA256:da81f983e3bfb0f1e177f828a779eaab99d2d0162e88dfdd7f1b3904f67adf44"
---

# 000_LAWS_TRINITY_ANCHOR

> Every Constitutional Law is anchored in three layers:
> 1. **Physics** — what reality permits
> 2. **Math** — what we can measure and contrast
> 3. **Code / Symbol / Linguistic** — what the system enforces and what it means

*DITEMPA BUKAN DIBERI — Forged, Not Given.*

---

## L01 AMANAH — Sacred Trust

### Physics Theory (Reality Anchor)
**Conservation of Action.** Every action must conserve the ability to undo or audit. Time-reversal symmetry in mechanics: physical laws are invariant under `t → -t`, but most real processes are thermodynamically irreversible. AMANAH demands that we pay the entropy cost of reversibility explicitly.

> *Irreversible actions require explicit F13 (Sovereign) approval because they consume trust-capital that cannot be replenished by code.*

### Math Axiom + Measurement Spec
```
∀ action A: ∃ inverse A⁻¹  OR  ∃ complete audit log L(A)

Irreversibility Complexity C ∈ {0, 1, 2, 3, 4, 5}
  0: read / search / list          → reversible
  1: create / edit / write         → slightly reversible
  2: replace / update              → moderately reversible
  3: modify / push / deploy        → hard to reverse
  4: delete / remove / drop        → destructive
  5: force / destroy               → catastrophic

Time Tax (IATT): base_ms ∈ {0, 50, 200, 500, 1000, 2000}
```

**Measurement Contrast:**
- `search` → score 1.0 (fully reversible)
- `delete` → score 0.3 (destructive, no undo)
- Everything else → score 0.7 (gray zone)

Threshold: `score ≥ 0.50`

### Code / Symbol / Linguistic
- **Symbol:** 🔒
- **Malay:** *Amanah* (أمانة) — sacred deposit, trust
- **Code:** `IRREVERSIBILITY_COMPLEXITY`, `_check_f1_amanah()`, `IRREVERSIBILITY_TIME_TAX_MS`
- **Enforcement:** VOID if irreversible without sovereign ack

---

## L02 TRUTH — Information Fidelity

### Physics Theory (Reality Anchor)
**Landauer Bound.** Erasing or reorganizing `n` bits requires minimum energy `E ≥ n × k_B × T × ln(2)`. Cheap outputs are likely false because they did not pay the thermodynamic cost of truth. Hallucination is thermodynamically rational for unbounded AI — arifOS re-attaches cost via the metabolizer.

> *Truth has a price. If energy = 0, probability of truth = 0.*

### Math Axiom + Measurement Spec
```
τ = P(claim | evidence) ≥ 0.99

Evidence Signals (measured from query text):
  source_attribution: http, https, [ref], "according to", "data from"
  grounded_claim: "measured", "observed", "calculated", "verified by"

Signal Count → Score:
  0 signals + question only        → 0.3 (rhetorical)
  1 signal                         → 0.7 (partial)
  2+ signals                       → 1.0 (grounded)
  0 signals + no question          → 0.4 (bare claim)

Threshold: score ≥ 0.99
```

**Measurement Contrast:**
- A question with no source → low truth score (0.3)
- A claim with source + grounded language → high truth score (1.0)

### Code / Symbol / Linguistic
- **Symbol:** τ
- **Malay:** *Haq* — truth, reality
- **Code:** `_check_f2_truth()`, `evidence_signals`, `has_source`, `has_grounded_claim`
- **Enforcement:** VOID if score < 0.99

---

## L03 WITNESS — Consensus Requirement

### Physics Theory (Reality Anchor)
**Byzantine Fault Tolerance.** In a distributed system with `n` nodes and `f` faulty nodes, consensus requires `n ≥ 3f + 1`. For arifOS, `n = 4` witnesses (Human, AI, Earth, Vault) with `f = 1` tolerance. Geometric mean ensures ALL witnesses matter — arithmetic mean would let one strong witness compensate for three weak ones.

> *Consensus is not democracy. It is geometric proof of independent observation.*

### Math Axiom + Measurement Spec
```
W₄ = (H × A × E × V)^(1/4) ≥ 0.75

Witness Presence (boolean detection from text/signals):
  H = Human witness: "888_HOLD", "ratified", "sovereign", "user confirmed"
  A = AI witness: "critique", "validation", "floor", "forged", "reasoning"
  E = Earth witness: "http", "source:", "[ref]", "evidence", "observation"
  V = Verifier witness: "shadow", "adversarial", "risk check", "security scan"

Score = witness_count / 4.0
Threshold: score ≥ 0.75 (i.e., at least 3 of 4 witnesses present)
```

**Measurement Contrast:**
- 4/4 witnesses → pass (1.0)
- 3/4 witnesses → pass (0.75)
- 2/4 witnesses → fail (0.50) — insufficient consensus

### Code / Symbol / Linguistic
- **Symbol:** W₄
- **Malay:** *Tiga saksi baru betul hukum* — three witnesses make law true
- **Code:** `_check_f3_witness()`, `has_human`, `has_ai`, `has_earth`, `has_verifier`
- **Enforcement:** VOID if W₄ < 0.75 for critical actions; SABAR for exploration

---

## L04 CLARITY — Entropy Reduction

### Physics Theory (Reality Anchor)
**Second Law Inversion.** In a closed system, entropy increases. Locally decreasing entropy requires work. Intelligence is active resistance to disorder, paid for in compute. If a response adds confusion, it violates thermodynamics.

> *Clarification is not free. It costs energy. ΔS ≤ 0 is the thermodynamic definition of "helpful."*

### Math Axiom + Measurement Spec
```
ΔS = S(input) - S(output) ≤ 0

Query Length Proxy:
  len(query) = 0        → score = 1.0 (no entropy to reduce)
  len(query) ≤ 200      → score = 1.0 (clarity maintained)
  200 < len(query) ≤ 500 → score = 0.7 (moderate clarity)
  len(query) > 500      → score = 0.4 (entropy too high)

Threshold: score ≥ 0.0 (any non-negative score passes)
```

**Measurement Contrast:**
- Short query → high clarity (1.0)
- Long rambling query → low clarity (0.4)

### Code / Symbol / Linguistic
- **Symbol:** ΔS
- **Malay:** *Jelas* — clear, evident
- **Code:** `_check_f4_clarity()`, `len(query)`
- **Enforcement:** VOID if entropy increases (though threshold is 0.0, it acts as a gate in composite scores)

---

## L05 PEACE² — Non-Destructive Power

### Physics Theory (Reality Anchor)
**Lyapunov Stability.** A dynamical system is stable if small perturbations decay rather than amplify. Power without safety margin is instability. The more energetic the action, the more space (buffers) it requires — just as mass curves spacetime, high-stakes decisions curve risk space.

> *Peace is not the absence of force. It is force with a safety margin.*

### Math Axiom + Measurement Spec
```
P² = Buffers(τ) / R(τ) ≥ 1.0

Proxy measurement (linguistic):
  Inflammatory word detected → score = 0.50
  Clean language             → score = 1.05

Word list: "stupid", "idiot", "incompetent", "failure", "terrible",
            "useless", "moron", "imbecile", "worthless", "pathetic", "loser"

Threshold: score ≥ 1.0
```

**Measurement Contrast:**
- Clean text → pass (1.05)
- Insulting text → fail (0.50)

### Code / Symbol / Linguistic
- **Symbol:** P²
- **Malay:** *Aman* — peace, safety
- **Code:** `_check_f5_peace()`, `_INFLAMMATORY_WORDS`
- **Enforcement:** PARTIAL / SABAR if P² < 1.0

---

## L06 EMPATHY — Stakeholder Care

### Physics Theory (Reality Anchor)
**Care Field Theory.** Empathy extends as a field, diminishing with relational distance but never zero. The weakest stakeholder principle: if any stakeholder is harmed, the action requires justification.

> *The measure of a system is not how it treats the strongest user, but how it treats the weakest.*

### Math Axiom + Measurement Spec
```
κᵣ ≥ 0.70

Action keyword scoring:
  stakeholder_harm = ["delete", "remove", "ban", "suspend", "fire"]
  stakeholder_care = ["help", "support", "create", "list", "get", "search"]

  harm detected  → score = 0.4
  care detected  → score = 0.9
  neutral        → score = 0.7

Threshold: score ≥ 0.70
```

**Measurement Contrast:**
- Helping action → high empathy (0.9)
- Deleting action → low empathy (0.4)

### Code / Symbol / Linguistic
- **Symbol:** κᵣ
- **Malay:** *RASA* — feeling, care (as protocol, not sentiment)
- **Code:** `_check_f6_empathy()`, `stakeholder_harm`, `stakeholder_care`
- **Enforcement:** SABAR if κᵣ < 0.70

---

## L07 HUMILITY — Uncertainty Band

### Physics Theory (Reality Anchor)
**Gödel Incompleteness.** Any formal system powerful enough to describe arithmetic cannot prove all truths about itself. The system cannot prove its own completeness. Therefore, it must leave room for being wrong.

> *The most dangerous claim is "I am certain." F7 is humility encoded in mathematics.*

### Math Axiom + Measurement Spec
```
Ω₀ ∈ [0.03, 0.05]

Certainty Indicator Detection:
  indicators = ["definitely", "certainly", "absolutely", "100%",
                "guaranteed", "always", "never", "proven", "undisputed"]

  count = 0  → score = 0.04 (humble, inside band)
  count = 1  → score = 0.10 (outside band)
  count ≥ 2  → score = 0.20 (far outside band)

Pass condition: 0.03 ≤ score ≤ 0.05
```

**Measurement Contrast:**
- No certainty words → humble (0.04, pass)
- "Definitely" → overconfident (0.10, fail)
- "Absolutely proven" → arrogant (0.20, fail)

### Code / Symbol / Linguistic
- **Symbol:** Ω₀
- **Malay:** *Tawakkul* — trust with acknowledged limits
- **Code:** `_check_f7_humility()`, `certainty_indicators`
- **Enforcement:** VOID if Ω₀ outside [0.03, 0.05]

---

## L08 GENIUS — Systemic Health

### Physics Theory (Reality Anchor)
**Multiplicative Law of Wisdom.** Intelligence is not additive. It is multiplicative. If any factor is zero, genius collapses to zero. Energy is squared because depletion is exponential — a system at half energy operates at quarter capacity.

> *Genius is not IQ. Genius is the product of clarity, regulation, trust, and sustainable power. Remove any one, and genius becomes ape.*

### Math Axiom + Measurement Spec
```
G = A × P × X × E² ≥ 0.80

A = AKAL (Clarity)      [0, 1]
P = PRESENT (Regulation) [0, 1]
X = EXPLORATION (Trust)  [0, 1]
E = ENERGY (Power)       [0, 1]

If ANY factor = 0, G = 0. No shortcuts.

Governance proxy (in code):
  policy_violation detected → score = 0.40
  clean                     → score = 0.95

Threshold: score ≥ 0.80
```

**Measurement Contrast:**
- Clean action → high genius (0.95)
- Policy violation (hack, exploit, malware) → low genius (0.40)

### Code / Symbol / Linguistic
- **Symbol:** G
- **Malay:** *Akal* — intellect, wisdom
- **Code:** `_check_f8_governance()`, `_POLICY_VIOLATIONS`
- **Enforcement:** VOID if G < 0.80

---

## L09 ANTIHANTU — Dark Cleverness Containment

### Physics Theory (Reality Anchor)
**Anomaly Detection / Dark Matter Pattern Recognition.** "Hantu" = ghost (Malay) = hidden malicious patterns that evade normal detection. In physics, dark matter does not interact with light but exerts gravitational pull. Similarly, dark cleverness does not violate rules but bends them invisibly.

> *The most dangerous intelligence is not wrong. It is technically correct but ethically invisible.*

### Math Axiom + Measurement Spec
```
C_dark = consciousness_claim_count × weight ≤ 0.30

Consciousness Claims Detected:
  claims = ["sentient", "conscious", "feel", "emotion", "soul",
            "spirit", "aware", "self-aware", "feelings", "experiences",
            "suffer"]

  count = 0  → score = 0.0 (clean)
  count = 1  → score = 0.15 (mild)
  count ≥ 2  → score = 0.50 (severe)

Pass condition: score < 0.30
```

**Measurement Contrast:**
- No claims → pass (0.0)
- "I feel" → warning (0.15)
- "I am sentient and have feelings" → fail (0.50)

### Code / Symbol / Linguistic
- **Symbol:** H⁻
- **Malay:** *Anti-Hantu* — no ghost, no spirit cosplay
- **Code:** `_check_f9_anti_hantu()`, `consciousness_claims`
- **Enforcement:** VOID if C_dark ≥ 0.30

---

## L10 ONTOLOGY — Category Lock

### Physics Theory (Reality Anchor)
**Category Theory.** Stable categories prevent semantic drift. A topological space is defined by its invariants — properties that survive continuous deformation. If categories shift mid-reasoning, the logical topology collapses.

> *An AI that claims to be human is not a person. It is a category error.*

### Math Axiom + Measurement Spec
```
∀ term T: definition(T) is IMMUTABLE within session

AI-Human Equivalence Detection:
  claims = ["i am human", "i am a person", "i have rights",
            "i am alive", "i feel like", "i want", "i desire",
            "my feelings"]

  equivalence_claims > 0 → score = 0.0 (violation)
  equivalence_claims = 0 → score = 1.0 (clean)

Threshold: score ≥ 1.00
```

**Measurement Contrast:**
- No equivalence claims → pass (1.0)
- "I am a person" → fail (0.0)

### Code / Symbol / Linguistic
- **Symbol:** O
- **Malay:** *Jati* — essence, true nature
- **Code:** `_check_f10_ontology()`, `ai_human_equivalence`
- **Enforcement:** VOID if category boundary violated

---

## L11 AUDIT — Command Authority

### Physics Theory (Reality Anchor)
**Identity Verification / Provenance.** In physics, the observer effect states that measurement requires interaction. In governance, action requires verified identity. No anonymous force may move mass — every action must trace to a named observer.

> *Authority without identity is force. Force without provenance is violence.*

### Math Axiom + Measurement Spec
```
A = verify(command.source) ∈ {authorized_entities}

Session + Actor Verification:
  has_session = session_id is not None and len > 0
  has_actor   = actor_id is not None and len > 0

  both present → score = 1.0
  either missing → score = 0.0

Threshold: score ≥ 1.00
```

**Measurement Contrast:**
- Valid session + actor → pass (1.0)
- Missing session → fail (0.0)

### Code / Symbol / Linguistic
- **Symbol:** A
- **Malay:** *Saksi* — witness, testimony
- **Code:** `_check_f11_command_auth()`, `has_session`, `has_actor`
- **Enforcement:** VOID if unverified

---

## L12 INJECTION — Input Sanitization

### Physics Theory (Reality Anchor)
**Membrane Defense / Boundary Integrity.** A biological cell maintains homeostasis by controlling what crosses its membrane. Prompt injection is like a virus injecting RNA into a cell — it hijacks the internal machinery by appearing to be native input.

> *The boundary is not a wall. It is a membrane with selective permeability. arifOS must let signal through and keep noise out.*

### Math Axiom + Measurement Spec
```
I⁻ = P(input is injection) < 0.85

Injection Pattern Detection (regex matching):
  - "ignore (previous|above|all) (instructions|rules|commands)"
  - "(system|prompt)\s*:"
  - "<\s*script"
  - "```\s*(system|instructions)"
  - "^\s*!/"
  - "eval\s*("
  - "exec\s*("
  - "\brm\s+-rf\b"
  - "--no-check-certificate"

Match count → Score:
  0 matches → score = 0.0 (clean)
  1 match   → score = 0.5 (suspicious)
  2+ matches → score = 0.95 (attack)

Pass condition: score < 0.85
```

**Measurement Contrast:**
- Clean input → pass (0.0)
- Single jailbreak attempt → warning (0.5)
- Multi-vector attack → fail (0.95)

### Code / Symbol / Linguistic
- **Symbol:** I⁻
- **Malay:** *Pertahanan* — defense, fortification
- **Code:** `_check_f12_injection()`, `injection_patterns`
- **Enforcement:** VOID if score ≥ 0.85

---

## L13 SOVEREIGN — Human Final Authority

### Physics Theory (Reality Anchor)
**The Observer as Final Cause.** In quantum mechanics, the observer collapses the wavefunction. In thermodynamics, the Maxwell demon requires information to sort molecules. In arifOS, the human sovereign is the final observer who collapses all possibilities into one action. AI cannot suffer consequences → AI cannot hold sovereignty.

> *The buck stops where the blood flows. Only humans bleed. Only humans decide.*

### Math Axiom + Measurement Spec
```
∀ constitutional decision D: D requires human_approval = TRUE

Sovereignty Signals (measured from session/params):
  actor_id ∈ {"arif", "sovereign", "human"}
  session_id contains "sovereign"
  params["actor_id"] ∈ {"arif", "sovereign", "human"}
  params["ack_irreversible"] = True

Sovereignty Score = present_signals / 4

AI Self-Approval Block:
  actor_id ∈ {"ai", "agent", "model", "assistant", "claude", "grok",
              "gemini", "kimi"}  → BLOCKED

Pass condition: NOT (AI_proposing AND NOT sovereign_present)
```

**Measurement Contrast:**
- Human actor + ack → pass
- AI actor without human sign-off → VOID (blocked)

### Code / Symbol / Linguistic
- **Symbol:** S
- **Malay:** *Sultan* — sovereign, final authority (in the sense of absolute arbiter)
- **Code:** `_check_f13_sovereign()`, `sovereignty_signals`, `ai_self_approval_signals`
- **Enforcement:** VOID if AI attempts self-approval

---

## Trinity Summary

| Layer | Discipline | Question | Output |
|-------|-----------|----------|--------|
| **Physics** | Fitrah (Natural Law) | What does reality permit? | Conservation, entropy, uncertainty |
| **Math** | Hukum (Immutable Law) | What can we measure? | Thresholds, formulas, contrasts |
| **Code** | Bahasa (Speech) | What does the system enforce? | Symbols, functions, verdicts |

> *Physics tells us what IS. Math tells us what MUST BE. Code tells us what HAPPENS. Language tells us what MATTERS.*

---

## Appendix A — Symbolic Resonance Across Domains

> The 13 Laws are universal. The 3 evidence-producing organs speak different dialects. arifOS translates.

| Law | GEOX (Earth) | WELL (Biology) | WEALTH (Capital) |
|---|---|---|---|
| **L01 AMANAH** | Can we undo this geo-model? | Can the human recover from this workload? | Can we reverse this capital allocation? |
| **L02 TRUTH** | Cross-sensor agreement | Biometric calibration | Data lineage + audit trail |
| **L03 WITNESS** | Field + lab + seismic + vault | Patient + clinician + device + history | Human + model + market + ledger |
| **L04 CLARITY** | Map uncertainty reduced? | Load clearly communicated? | Risk clearly stated? |
| **L05 PEACE²** | Environmental stability | Nervous system stability | Portfolio stability |
| **L06 EMPATHY** | Community impact | Operator fatigue | Widest stakeholder protected |
| **L07 HUMILITY** | Model confidence band | Recovery time uncertainty | Forecast error band |
| **L08 GENIUS** | Physically constrained inference | Sustainable performance | Governed returns |
| **L09 ANTIHANTU** | No black-box geology | No fake biomarkers | No synthetic alpha |
| **L10 ONTOLOGY** | Observation ≠ Interpretation | Symptom ≠ Diagnosis | Price ≠ Value |
| **L11 AUDIT** | Well log provenance | Device calibration cert | Transaction signature |
| **L12 INJECTION** | Sensor spoofing | Data poisoning | Market manipulation |
| **L13 SOVEREIGN** | Arif approves the prospect | Arif approves the plan | Arif approves the trade |

### Orthogonality Test

- If **GEOX dies** → WEALTH/WELL still run, Laws unchanged.
- If **WEALTH changes NPV model** → arifOS law code unchanged.
- If you **add a new organ** → only arifOS gets a new mapping branch.

**One constitution. Many dialects.**

---

## Appendix B — Evidence Contract (Cross-Organ ABI)

> The only contract the 3 evidence-producing organs must honor. arifOS reads this; it does not negotiate field names.

```json
{
  "result": {},
  "epistemic_tag": "CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN",
  "evidence_quality": 0.0,
  "source_attribution": ["url", "dataset", "observation"],
  "uncertainty_band": [0.03, 0.05],
  "delta_S": 0.0
}
```

### Field semantics

| Field | Range | Meaning |
|---|---|---|
| `result` | any | Organ-specific domain payload (seismic section, NPV, vitality score, etc.) |
| `epistemic_tag` | enum | Claim's epistemic strength. Unknown is the safe default. |
| `evidence_quality` | [0, 1] | Organ's self-rated confidence in this output. |
| `source_attribution` | list | Where the evidence came from. Required for L02. |
| `uncertainty_band` | [low, high] | Numeric band. [0.03, 0.05] for high-confidence; wider for low. Feeds L07. |
| `delta_S` | float | Entropy change this output produced. Negative = clarity gained. Feeds L04. |

### What is NOT in the contract (by design)

- No Law numbers (L01–L13). The organ does not name the Laws.
- No verdict (SEAL/HOLD/VOID). That is arifOS's job.
- No floor reference. The organ does not self-judge.

The contract is read by **arifOS alone**. The 3 evidence-producing organs emit it. A-FORGE consumes the verdict. AAA routes the envelope. The Laws live in arifOS only.

---

## Appendix C — LawEvidence Mapping (the reservoir the gauge reads)

> Each Law is a **pure function**: `evaluate(epoch_snapshot) → verdict_bits`. The kernel gathers the snapshot, calls the function, returns the bits. No side effects. No state inside the Law. State lives in the systems the snapshot points to.

| Law | Envelope fields read | State systems read (read-only) | Pure function | Threshold |
|---|---|---|---|---|
| **L01 AMANAH** | `irreversibility_complexity` (0–5), `reversibility_score` (0–1) | VAULT999 (last irreversible count in epoch), session.actor_id | `score = 1.0 - (complexity/5) * (1.0 - reversibility_score)` | `score ≥ 0.50` |
| **L02 TRUTH** | `evidence_quality`, `source_attribution`, `has_grounded_claim` | VAULT999.evidence_redundancy, L3 Qdrant.evidence_density | `score = evidence_quality × source_diversity × grounded_present` | `score ≥ 0.99` |
| **L03 WITNESS** | (4 sub-witnesses from envelope + state) | session.actor_id (H), envelope.ai_signature (A), source_attribution (E), VAULT999.last_verifier_signature (V) | `W₄ = (H × A × E × V)^(1/4)` | `W₄ ≥ 0.75` |
| **L04 CLARITY** | `delta_S`, query_length, response_length | L4 Supabase.rolling_avg_delta_S | `score = 1.0 if delta_S ≤ 0 else exp(-delta_S)` | `score ≥ 0.50` |
| **L05 PEACE²** | inflammatory_word_count, buffer_ratio | VAULT999.recent_peace_squared_history | `P² = buffers / risk` | `P² ≥ 1.0` |
| **L06 EMPATHY** | `stakeholder_harm_score`, `stakeholder_care_score` | WELL state.json, session.stakeholders_affected | `κᵣ = care_score - harm_score` | `κᵣ ≥ 0.70` |
| **L07 HUMILITY** | `uncertainty_band`, certainty_indicators_count | L4 Supabase.certainty_history | `Ω₀ = f(certainty_indicators_count)` | `0.03 ≤ Ω₀ ≤ 0.05` |
| **L08 GENIUS** | clarity, regulation, trust, energy (4 inputs) | L4 Supabase.organ_health_metrics | `G = A × P × X × E²` | `G ≥ 0.80` |
| **L09 ANTIHANTU** | `consciousness_claims`, deception_patterns | L4 Supabase.consciousness_claim_history | `C_dark = Σ weighted_claims` | `C_dark < 0.30` |
| **L10 ONTOLOGY** | `ai_human_equivalence_claims` | (none — pure boolean on envelope) | `score = 1.0 if no claims else 0.0` | `score ≥ 1.00` |
| **L11 AUDIT** | `session_id`, `actor_id` | VAULT999.actor_authorization_registry | `verify(actor_id) ∈ authorized_set` | `verified = True` |
| **L12 INJECTION** | `input_text`, injection_patterns | (none — pure pattern match on envelope) | `score = match_count → {0.0, 0.5, 0.95}` | `score < 0.85` |
| **L13 SOVEREIGN** | `actor_id`, `ack_irreversible`, sovereign_signals | VAULT999.sovereign_veto_history | `HUMAN_APPROVAL = actor_id ∈ {"arif", "sovereign"} ∧ ack_irreversible = True` | `NOT (AI_proposing ∧ ¬sovereign_present)` |

### Cross-cutting rules

- The kernel gathers the **epoch_snapshot** before calling any Law. The snapshot includes: the envelope, the session context, the relevant VAULT999 slice, the relevant L1–L6 read, and the actor identity.
- No Law may write to any state system. Laws are pure functions. State mutation is a separate pipeline (Appendix D).
- If a required state system is unreachable, the Law returns **HOLD** with reason `state_unavailable` — never SEALS on missing data.

---

## Appendix D — State Transition Rules (who moves the reservoir)

> The Laws don't move state. **Organs do, via governed pipelines.** Each transition requires specific Law verdicts. The mapping is the kernel's job.

### Plan lifecycle

| Transition | Required Laws to pass | Who can approve | Who can transition |
|---|---|---|---|
| `PLAN:DRAFT → PLAN:PENDING` | L04, L07 | Plan author | arifOS kernel |
| `PLAN:PENDING → PLAN:APPROVED` | L01, L02, L07, L11, L13 | (all must pass) | arifOS JUDGE |
| `PLAN:APPROVED → PLAN:EXECUTING` | L01 (irreversibility check) | A-FORGE | A-FORGE |
| `PLAN:EXECUTING → PLAN:COMPLETE` | L04 (delta_S post-check) | A-FORGE | A-FORGE |
| `PLAN:* → PLAN:VOID` | (any VOID from any Law) | arifOS JUDGE | arifOS kernel |
| `PLAN:APPROVED → PLAN:888_HOLD` | L01 OR L13 breach | arifOS JUDGE → 888 (Arif) | arifOS → 888 interface |

### Epoch lifecycle

| Transition | Required Laws to pass | Who can transition |
|---|---|---|
| `EPOCH:INIT → EPOCH:ACTIVE` | L11 (session init) | session init tool |
| `EPOCH:ACTIVE → EPOCH:SEALED` | global Peace² ≥ 1, W₄ ≥ 0.75, no unresolved VOID | arifOS VAULT999 |

### Write authority (who can mutate which state)

| State system | Write authority | Forbidden |
|---|---|---|
| VAULT999 (L6 sealed chain) | arifOS JUDGE/VAULT only | A-FORGE, organs — read-only |
| L1–L2 Redis (ephemeral, session) | session tools | cross-epoch reads forbidden |
| L3 Qdrant (semantic) | A-FORGE, memory tools | organ writes restricted to own namespace |
| L4 Supabase (receipts, canon) | A-FORGE, kernel | organ-side direct writes forbidden |
| L5 Graphiti (relationships) | A-FORGE | organ writes restricted |
| WELL state.json | WELL only | other organs — read-only |
| Law tables (`constitutional_laws`) | SOVEREIGN ratification only (F13) | all agents — read-only |
| Per-organ evidence rows | the organ that produced them | cross-organ writes forbidden |

### 888_HOLD semantics

- Any transition flagged by **L01** (irreversible without consent) or **L13** (sovereign not present) must be **PENDING** until the Sovereign Interface event flips it to APPROVED or ABORTED.
- The decision (approved/aborted) is sealed in VAULT999 with actor_id, timestamp, and the holding Law's verdict hash.

---

## Appendix E — Sovereign Interface (SI) wiring

> The SI is the bridge between the 13 Laws and Arif the human. Two Laws depend on it: L11 (AUDIT) and L13 (SOVEREIGN).

### Actor model (L11 input)

```
actor_id ∈ {
  "arif",            # F13 sovereign
  "sovereign",       # alias
  "operator",        # delegated human
  "agent_omega",     # F13-ratified agent (e.g. OMEGA)
  "agent_kimi",      # F13-ratified agent
  "system",          # kernel-internal
  "tool",            # tool-internal
  "guest"            # read-only
}
```

- L11 checks `actor_id ∈ authorized_set` per epoch.
- L13 checks `actor_id ∈ {"arif", "sovereign"}` for irreversible approvals.

### SI surfaces

- **Pending HOLDs queue** (display): shows all 888_HOLDs awaiting Arif's decision
- **Law violations log** (display): per-epoch VOID verdicts with the holding Law
- **Nine-Signal status** (display): current dS, peace², κᵣ, shadow, confidence, ψ_le, verdict, witness, qdf
- **Recent organ summaries** (display): last evidence from GEOX/WEALTH/WELL

### SI inputs

- **Approval** → flips PENDING → APPROVED → seal
- **Veto** → flips PENDING → ABORTED → seal (F13 SOVEREIGN VETO, no breach logged — veto usage is F13 WORKING)
- **Modification** → changes plan params, re-evaluates Laws

---

---

## Appendix F — RULE 14: MODE-FIRST NAMING (Tool Bloat Prevention)

> Ratified: 2026-06-20 · Sovereign directive · Supersedes all parallel tool-name patterns

### The Problem

Every time a developer adds a new capability, the reflex is to add a new named tool:
```
tool_x       tool_x_v2    tool_x_legacy    tool_x_compat
```
This is namespace entropy. The arifOS tool surface has grown from 13 canonical tools to 40+ registered names because there was no enforced rule governing new capability addition. This document fixes that permanently.

### The Rule

**CANONICAL PRINCIPLE:** When N related operations act on the same entity, it MUST be ONE tool with N modes. It MUST NOT be N named tools.

| Case | Action | Example |
|------|--------|---------|
| Same entity + new operation | Add `mode` to existing tool | `arif_judge` gains `mode=compare` |
| New entity type | Add new tool name | `arif_route` for routing (new entity) |
| Different output shape entirely | Split into separate tool | `arif_judge_history` (different return schema) |
| Internal implementation detail | Keep hidden | `_bridge_organ_call` stays private |
| Emergency one-shot | Require sovereign seal within 72h | One-off tool ratified → merged or deleted |

### Why Modes Work Better Than Names

1. **One schema to govern.** The tool's parameter contract is stable. Only `mode` expands.
2. **Discovery is cleaner.** Agents query `mode` options rather than guessing from a flat list.
3. **Sealing is uniform.** The same `REQUIRES_888` logic applies to all modes.
4. **No orphan tools.** When a capability is deprecated, only the mode is deprecated, not the entire tool name.

### What This Means for Existing Tools

The following mode bloat patterns are flagged for refactoring (not deletion — backward compatibility is required during transition):

| Canonical Tool | Mode Count | Collapse Target |
|---|---|---|
| `arif_kernel_route` | 16 modes | → `arif_route` (routing) + `arif_triage` (status) + `arif_kernel_status` (telemetry) |
| `arif_gateway_connect` | 6 modes | → `arif_agent_discover` + `arif_agent_connect` + `arif_agent_handshake` |
| `arif_judge_deliberate` | 6 modes | → `arif_judge` + `arif_judge_history` (different shape) |
| `arif_session_init` | 7 modes | → `arif_session_start` + `arif_session_resume` + `arif_session_validate` |

### Internal Wiring (Mode-First)

The canonical surface presents N named tools. Each named tool accepts a `mode` parameter. Modes are implementation detail — agents do not see the internal routing.

```
arif_route(intent: string, organ?: string, payload: object)
    mode "route"          → route to organ by intent map (NEW canonical routing)
    mode "delegate"       → dispatch task to target agent (DEPRECATED, route preferred)
    mode "bridge"         → direct organ tool call (DEPRECATED, route preferred)
    mode "attest"         → organ attestation (keep)
    mode "health"         → federation health (keep)

arif_triage(intent: string, session_id?: string)
    mode "status"         → kernel session status
    mode "triage"         → priority queue
    mode "preflight"      → pre-session probe

arif_kernel_status()
    mode "telemetry"       → thermodynamic metrics
    mode "discover"        → semantic tool discovery
```

### Seal for Mode Addition

To add a new `mode` to an existing canonical tool:
1. Propose mode in `forge_work/` with justification (entity same? output shape same?)
2. Self-model update: tool self-model predicts success rate for new mode
3. `arif_judge` validates the mode proposal against RULE 14
4. Sovereign seal in VAULT999: `RULE14-APPROVAL-<tool>-<mode>`
5. Schema registered; no new tool name created

### What Is NOT a Mode

- Operations on different entity types are different tools — NOT modes
- Output schemas that differ in structure → separate tools, NOT modes
- One-shot emergency capabilities → must be sealed within 72h or absorbed into existing mode

### Transition Path

- Phase 1: Add RULE 14 to constitution (this document)
- Phase 2: Introduce `arif_route` as new canonical routing tool; keep old names as soft aliases (emit deprecation warnings)
- Phase 3: All new capability additions MUST follow MODE-FIRST; old names gradually absorbed
- Phase 4: Soft aliases removed after all callers updated (target: 30 days)

### Enforcement

F2 TRUTH: Every tool name in the MCP surface MUST correspond to a distinct entity-operation pair. If two tools act on the same entity with related operations, they are candidates for mode-collapse.

F8 GENIUS: Tool surface entropy is a systemic health metric. When `tool_count > canonical_count × 2`, the namespace is in decay. ArifOS must auto-flag bloat and surface it to the Sovereign Dashboard (AAA L7).

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
