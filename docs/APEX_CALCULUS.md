# APEX Theory T-000: Computed Governance Calculus Specification
**Version:** `v2026.07.APEX`  
**Equation:** $G_{\text{APEX}} = A \cdot P \cdot E \cdot X$  
**Authority:** `888_JUDGE` | `F13 SOVEREIGN`

---

## 1. The Grand Equation

$$\text{Intelligence} = \text{Governed Constraint Satisfaction}$$

$$G = A \cdot P \cdot E \cdot X$$

Where $A, P, E, X \in [0.00, 1.00]$ are Nash Geometric Means across normalized floor sub-scores:

- **A (AKAL):** Reasoning lawfulness, truth labeling, humility cap, ontology integrity.
  $$A = \text{GM}(F2_{\text{Truth}}, F4_{\text{Clarity}}, F7_{\text{Humility}}, F10_{\text{Ontology}})$$
- **P (PRESENT_AUTHORITY):** State truth, reversibility, auditability, sovereign authorization.
  $$P = \text{GM}(F1_{\text{Amanah}}, F5_{\text{Peace}}, F11_{\text{Auditability}}, F13_{\text{Sovereign}})$$
- **E (ENTROPY_ENERGY):** Uncertainty integrity, clarity gain, resilience, mutation thermodynamic cost.
  $$E = \text{GM}(F3_{\text{Tri-Witness}}, F4_{\text{Clarity}}, F12_{\text{Resilience}}, \text{Energy}_{\text{Score}}, \text{Energy}_{\text{Score}})$$
- **X (EXPLORATION_AMANAH):** Useful novelty under custody, empathy, anti-hantu, genius efficiency.
  $$X = \text{GM}(F6_{\text{Empathy}}, F8_{\text{Genius}}, F9_{\text{Anti-Hantu}}, \text{Risk}_{\text{Score}})$$

$$G = \text{GM}(A, P, E, X) = \sqrt[4]{A \cdot P \cdot E \cdot X}$$

---

## 2. Verdict Thresholds & Hard Floor Overrides

### Verdict Thresholds
- **$G \ge 0.80$:** `SEAL` candidate (Eligible for execution ratification)
- **$0.70 \le G < 0.80$:** `SABAR` (Caution/delay pending score improvement)
- **$G < 0.70$:** `VOID` (Severe degradation, immediate rejection)

### Priority Evaluation Logic
1. **Priority 1 (Hard Floor Rejection):**
   If $F13 < 1.00$, $F9 < 1.00$, $F10 < 1.00$, or $F12 < 1.00$, return `VOID` immediately.
2. **Priority 2 (Reversibility Gate):**
   If action is irreversible ($F1 < 1.00$) and lacks explicit operator approval, force verdict to `HOLD_888`.
3. **Priority 3 (Calculus Score Evaluation):**
   Evaluate $G = \text{GM}(A, P, E, X)$ against thresholds `SEAL`, `SABAR`, `VOID`.
