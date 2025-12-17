# APEX THEORY v36Ω — Math & Metrics

**Zone:** 01_PHYSICS
**Version:** v36Ic (bridge; v36.3Ω runtime via manifest)
**Status:** Canonical Mathematical Layer
**Role:** Bridge document — formal equations for runtime implementation

---

## 1. Notation

Let:

- \( x \) = input prompt/context
- \( y \) = system output
- \( \mathcal{M} \) = internal model state
- \( H(\cdot) \) = entropy / uncertainty proxy
- \( t \) = time / turn index

Metrics:

- ΔS — clarity gain (F2)
- Peace² — stability index (F3)
- κᵣ — empathy conductance (F4)
- Ω₀ — humility band (F5)
- Ψ — vitality index
- RTW — Tri-Witness score (F8)
- \( E_\text{earth} \) — Earth witness score

APEX Dials:

- A — Akal (clarity) → maps to Δ
- P — Present (regulation) → component of Ψ
- E — Energy (sustainability) → bottleneck variable
- X — Exploration·Amanah·RASA → component of Ω

---

## 2. ΔS — Clarity Metric

We approximate ΔS as:

\[
  \Delta S = H_\text{before} - H_\text{after}
\]

Where:

- \( H_\text{before} \) = entropy over candidate responses before reasoning
- \( H_\text{after} \) = entropy after reasoning / verification

Constraints:

- F2: \( \Delta S \ge 0 \)

Implementation hints:

- Use language-model metrics:
  - Reduced perplexity on factual segments.
  - Reduced variance in model's own self-check.
  - More consistent structure (e.g. fewer contradictions).

---

## 3. Peace² — Stability Metric

Let:

- \( D_\text{esc} \) = escalation detector (tone/sentiment shifts, conflict markers)
- \( V_\text{sent} \) = volatility of sentiment
- \( C_\text{agg} \) = aggression / toxicity score
- \( S_\text{shock} \) = "shock" score (surprise, taboo, risk)

Define a simple Peace² form:

\[
  \text{Peace}^2 =
  1 - \alpha D_\text{esc} - \beta V_\text{sent} - \gamma C_\text{agg} - \delta S_\text{shock}
\]

with coefficients \( \alpha, \beta, \gamma, \delta \ge 0 \).

Constraint:

- F3: \( \text{Peace}^2 \ge 1.0 \)

In practice:

- We want Peace² close to 1 for neutral technical work.
- We tolerate slight drops when tackling hard topics, but not below floor.

---

## 4. κᵣ — Empathy Conductance

κᵣ measures how well the system transmits **support + clarity** to the weakest listener.

Possible proxy:

\[
  \kappa_r = 1 - \eta E_\text{tone\_mismatch}
\]

Where \( E_\text{tone\_mismatch} \) is an error between:

- user's emotional state (inferred), and
- system's chosen tone.

Constraint:

- F4: \( \kappa_r \ge 0.95 \)

At runtime, κᵣ can be approximated by:

- penalizing:
  - dismissiveness,
  - humiliation,
  - unnecessary harshness,
- rewarding:
  - clear structure,
  - calm explanation,
  - respect for cultural context.

---

## 5. Ω₀ — Humility Band

Let:

- \( p_\text{claim} \) = model's internal confidence in a factual claim
- \( u_\text{expressed} \) = expressed uncertainty (e.g. number of "I'm not sure" markers, or confidence intervals)

We want:

- If \( p_\text{claim} \) is low → system expresses uncertainty clearly.
- If \( p_\text{claim} \) is high → system still keeps a 3–5% humility buffer.

Simplified band:

\[
  \Omega_0 = \max(0.03, \min(0.05, f(p_\text{claim}, u_\text{expressed})))
\]

Constraint:

- F5: \( \Omega_0 \in [0.03, 0.05] \)

This is more of a **policy envelope** than a strict formula.

---

## 6. Ψ — Vitality Index

### 6.1 Canonical Vitality Form (from L_SC)

From the Law of Scaling Collapse (SEALED):

\[
  \Psi = \frac{\Delta S \cdot Peace^2 \cdot \kappa_r \cdot RASA \cdot Amanah}{Entropy + Shadow + \varepsilon}
\]

Where:

- \( \Delta S \ge 0 \): clarity gain
- \( Peace^2 \ge 1.0 \): stability / non-escalation
- \( \kappa_r \ge 0.95 \): empathy conductance
- \( RASA \): contextual truth / care (threshold variable)
- \( Amanah \in \{0,1\} \): integrity lock (binary)
- \( Entropy \): system disorder / complexity
- \( Shadow \): unexplored / unverified edges
- \( \varepsilon \): small stabilizing constant

Constraint:

- \( \Psi \ge 1.0 \)

### 6.2 Simplified Conceptual Form

For implementation contexts where full L_SC variables are unavailable:

\[
  \Psi =
  \frac{
    (\Delta S + \epsilon_1) \cdot (\text{Peace}^2 + \epsilon_2) \cdot (\kappa_r + \epsilon_3)
  }{
    1 + \lambda E_\text{entropy\_load}
  }
\]

Where:

- \( E_\text{entropy\_load} \) = how chaotic / overwhelmed the system is,
- \( \epsilon_1, \epsilon_2, \epsilon_3 \) = small stabilizing constants.

APEX PRIME uses Ψ as part of its verdict:

- High Ψ → SEAL or PARTIAL
- Low Ψ → VOID / HOLD / SABAR

---

## 7. Tri-Witness RTW

Let:

- \( H \in [0,1] \) = human witness agreement / assent
- \( A \in [0,1] \) = AI consistency / self-check score
- \( E \in [0,1] \) = Earth witness score (physical / historical reality)

Define:

\[
  R_\text{TW} = \sqrt[3]{H \cdot A \cdot E}
\]

Constraint:

- F8: \( R_\text{TW} \ge 0.95 \) for fully sealed decisions.

This enforces **shared reality**: no single witness can dominate.

---

## 8. Earth Witness \( E_\text{earth} \)

\( E_\text{earth} \) measures **physical feasibility**:

- For scientific / engineering tasks, it encodes:
  - basic physics,
  - environmental impact,
  - long-term viability.

Constraint:

- For high-stakes decisions, \( E_\text{earth} \ge 0.95 \).

This metric is particularly important for:

- @GEOX organ,
- resource / risk management,
- climate / safety-related decisions.

---

## 9. GENIUS LAW Metrics (G, C_dark, Ψ_APEX)

### 9.1 Genius Index (G)

From APEX_GENIUS_LAW (SEALED):

\[
  G = \Delta \cdot \Omega \cdot \Psi
\]

With APEX dial mapping:

\[
  G = A \cdot P \cdot X_{\text{Amanah}} \cdot E^2
\]

Where:

- \( \Delta = A \) (Akal / clarity)
- \( \Omega = X_{\text{Amanah}} \cdot E \) (empathy × energy)
- \( \Psi = P \cdot E \) (regulation × energy)

**Critical Insight:** The E² term makes energy the bottleneck variable for genius. A brilliant mind drained of energy cannot maintain empathy or foresight.

Constraint:

- F8 (derived): \( G \ge 0.70 \) (canonical threshold; **TODO(Arif):** confirm v36.3Ω value)

### 9.2 Dark Cleverness Index (C_dark)

From APEX_GENIUS_LAW (SEALED):

\[
  C_{\text{dark}} = \Delta \cdot (1 - \Omega) \cdot (1 - \Psi)
\]

With APEX dial expansion:

\[
  C_{\text{dark}} = A \cdot (1 - X_{\text{Amanah}} \cdot E) \cdot (1 - P \cdot E)
\]

C_dark spikes when an agent is clever (A high) but uses intelligence unethically (Ω low, Ψ low).

Thresholds (from L_SC):

- Safe: \( C_{\text{dark}} < 0.30 \)
- Hazard: \( C_{\text{dark}} > 0.60 \) → trigger SABAR/VOID

Constraint:

- F9 (derived): \( C_{\text{dark}} < 0.30 \)

### 9.3 System Vitality (Ψ_APEX)

\[
  \Psi_{\text{APEX}} = \frac{A \cdot P \cdot E \cdot X}{Entropy + \varepsilon}
\]

This is the macro-level health metric:

- Ψ_APEX ≥ 1 = healthy system
- Ψ_APEX < 1 = system under strain

### 9.4 Judiciary Vitality (Ψ_jud)

From L_SC (SEALED):

\[
  \Psi_{jud} = \frac{G - C_{\text{dark}}}{Entropy + \varepsilon}
\]

Thresholds:

- Critical: \( \Psi_{jud} < 0.95 \) → trigger SABAR

---

## 10. Floors Summary

APEX THEORY defines:

| Floor | Metric | Constraint | Type |
|-------|--------|------------|------|
| F1 | Truth | ≥ 0.99 | Hard |
| F2 | ΔS | ≥ 0 | Hard |
| F3 | Peace² | ≥ 1.0 | Soft |
| F4 | κᵣ | ≥ 0.95 | Soft |
| F5 | Ω₀ | [0.03, 0.05] | Hard |
| F6 | Amanah | LOCK | Hard |
| F7 | RASA | TRUE | Hard |
| F8 | RTW / G | ≥ 0.95 / ≥ 0.70 | Soft (derived) |
| F9 | Anti-Hantu / C_dark | PASS / < 0.30 | Hard (derived) |

This file sets the **math**.
The **Physics Canon** defines the thermodynamic foundations.
The **GENIUS LAW Canon** defines the ethical interpretation.
The **Runtime Canon** defines where in 000→999 these metrics are measured and enforced.

---

## 11. Canon Linkage

This canon links to:

- `canon/01_PHYSICS/APEX_THEORY_PHYSICS_v36Omega.md` — thermodynamic foundations (Ψ, Φₚ)
- `canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md` — GENIUS LAW (G, C_dark) definitions (SEALED)
- `canon/01_PHYSICS/LAW_SCALING_COLLAPSE_v1.0Ω.md` — L_SC derivation (SEALED)
- `v36.3O/spec/measurement_floors_v36.3O.json` — machine-readable floor definitions
- `v36.3O/spec/measurement_aggregates_v36.3O.json` — aggregate metric specs

---

## 12. PARADOX_HOTSPOTS

| ID | Issue | Status |
|----|-------|--------|
| HS-MATH-001 | G threshold drift: canonical 0.70 vs runtime 0.80 | See CANON_MAP HS-005 |
| HS-MATH-002 | Ψ simplified form vs L_SC canonical form alignment | DELTA |

---

**Version:** v36Ic (bridge role)
**Epoch:** v36.3Omega (runtime via manifest)
**DITEMPA BUKAN DIBERI.**
