# APEX Theory (v2026.07.APEX · T-000) — Canonical Governance Equation

> **Ditempa Bukan Diberi** — *Forged, Not Given*  
> **Status:** CANONICAL DRAFT (Step A) | **Authority:** Sovereign ARIF & 888_JUDGE  
> **Layer:** CONSTITUTIONAL KERNEL (GENESIS 000)

---

## 🏛️ 1. The Core Equation: $G = A \cdot P \cdot E \cdot X$

Governed General Intelligence under arifOS is defined by the 4-variable canonical APEX equation:

$$G = A \cdot P \cdot E \cdot X$$

Where $G \in [0.0, 1.0]$ represents the **Governed Capability Score** of an action, plan, or execution frame.

---

## 📐 2. Canonical Variable-to-Floor Decomposition

Each variable in the 4-tuple $(A, P, E, X)$ is computed as the geometric mean ($\text{GM}$) of its assigned Constitutional Floor measurements (F1–F13) and runtime telemetry:

### 1. $A$ — Authority & Epistemic Grounding
$$A = \text{GM}(F2, F4, F7, F10) = \left( F2 \cdot F4 \cdot F7 \cdot F10 \right)^{1/4}$$
- **$F2$ (Truth):** Reality grounding and claim verification ($\text{Psi } \Psi \ge \Psi_{\min}$).
- **$F4$ (Clarity):** Entropy reduction and deterministic intent ($\Delta S \le 0$).
- **$F7$ (Humility):** Honest confidence labeling and epistemic uncertainty cap ($\Omega \le \Omega_{\max}$).
- **$F10$ (Ontology):** Structural coherence and non-LLM ground-truth evidence requirements.

### 2. $P$ — Peace & Sovereign Protection
$$P = \text{GM}(F1, F5, F11, F13) = \left( F1 \cdot F5 \cdot F11 \cdot F13 \right)^{1/4}$$
- **$F1$ (Amanah):** Reversibility, state snapshots, and backup integrity.
- **$F5$ (Peace²):** Human dignity preservation and non-escalation ($\text{PEACE}^2 \ge 1.0$).
- **$F11$ (Auth):** SCT identity resolution, session verification, and VAULT999 append-only logging.
- **$F13$ (Sovereign):** Absolute human veto and `888 HOLD` ratifications.

### 3. $E$ — Energy & Substrate Telemetry
$$E = \text{GM}(F3, F4, F12, \text{energy\_score}, \text{energy\_score}) = \left( F3 \cdot F4 \cdot F12 \cdot \text{energy\_score}^2 \right)^{1/5}$$
- **$F3$ (Tri-Witness):** Quad/Tri-witness consensus (Local $\rightarrow$ Remote $\rightarrow$ VPS).
- **$F4$ (Clarity):** Telemetry log completeness and trace clarity.
- **$F12$ (Injection):** Input sanitization and prompt-injection barrier integrity.
- **$\text{energy\_score}$:** Double-weighted substrate resource efficiency and thermal/hardware budget.

### 4. $X$ — eXploration & Bounded Genius
$$X = \text{GM}(F6, F8, F9, \text{exploration\_score}) = \left( F6 \cdot F8 \cdot F9 \cdot \text{exploration\_score} \right)^{1/4}$$
- **$F6$ (Empathy):** Consequence, harm assessment, and blast-radius evaluation.
- **$F8$ (Genius):** Execution efficiency threshold ($G \ge 0.80$).
- **$F9$ (Anti-Hantu):** Absolute prohibition against simulating self-awareness or role-playing authority.
- **$\text{exploration\_score}$:** Bounded search capacity and novelty index.

---

## 📜 3. Semantic Delta Log: Legacy $g(t)$ vs Proposed $G$

> [!WARNING]
> **Constitutional Notice: Non-Equivalence & Governance Semantic Shift**  
> The transition from legacy 6-variable $g(t) = A \cdot P \cdot H \cdot S \cdot U \cdot E^2$ to proposed 4-variable $G = A \cdot P \cdot E \cdot X$ is **NOT** a harmless bijective rename. It represents a formal re-weighting of governance semantics:

1. **Demotion of $H$ (Human):**  
   - *Legacy:* $H$ was a top-level independent multiplier.  
   - *Proposed:* $H$ is demoted into sub-floor measurements: $F13$ (Sovereign Veto in $P$), $F6$ (Empathy in $X$), and $F9$ (Anti-Hantu in $X$).
2. **Folding of $S$ (Sabar / Cooldown):**  
   - *Legacy:* $S$ was a top-level multiplier representing SABAR cooldown.  
   - *Proposed:* $S$ is dropped as a top-level variable. $F5 \text{ (PEACE}^2\text{)}$ is folded into $P$; $F8 \text{ (GENIUS)}$ into $X$; $F3 \text{ (WITNESS)}$ into $E$.
3. **Re-weighting of Energy ($E$):**  
   - *Legacy:* $E^2$ directly squared energy as a top-level quadratic factor.  
   - *Proposed:* `energy_score` appears twice inside a 5-element geometric mean. The monotonic mapping across historical ledgers is altered.

**Audit Protocol Requirement:** The historical `VAULT999` ledger must keep both `apex_legacy` and `apex_v2` reachable side-by-side under `--legacy-apex` until delta bounds are certified.

---

## 🔒 4. Constitutional Invariants & Authority Hierarchy

1. **Sole Verdict Engine:** `arifOS` (`arifosmcp/tools/judge.py` / `runtime/kernel/judge.py`) is the **ONLY** constitutional engine authorized to issue verdicts (`SEAL`, `SABAR`, `HOLD`, `VOID`) and write sealed receipts to `VAULT999`.
2. **Read-Only Aggregators:** External projections (e.g., `governance/enforce.js` or AAA Cockpit) are **strictly read-only aggregators** emitting evidence. They must **NEVER** function as a second verdict engine.
3. **Metric Levers:** Levers such as `auditability_score` and `clarity_score` are internal $F4/F11$ measurements that aggregate into $A, P, E, X$, rather than promoted first-class top-level variables.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
