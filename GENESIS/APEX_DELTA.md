# APEX Theory Delta Log & Floor Re-weighting Record (v2026.07 · Step B)

> **Ditempa Bukan Diberi** — *Forged, Not Given*  
> **Status:** CANONICAL DELTA LOG (Step B) | **Authority:** Sovereign ARIF & 888_JUDGE  
> **Layer:** CONSTITUTIONAL KERNEL (GENESIS 000)

---

## 📊 1. Per-Floor Re-weighting Matrix: Legacy $g(t)$ vs Proposed $G$

The table below details how each Constitutional Floor (F1–F13) maps from the legacy 6-variable formulation ($A, P, H, S, U, E^2$) into the proposed 4-variable formulation ($A, P, E, X$):

| Floor | Name | Legacy Location & Weight | Proposed Location & Formula | Shift Rationale & Governance Impact |
|---|---|---|---|---|
| **F1** | Amanah | Top-level $P$ | $P = \text{GM}(F1, F5, F11, F13)$ | Retained in $P$. Weight shifted from 1/6 linear product to 1/4 geometric mean exponent. |
| **F2** | Truth | Top-level $A$ | $A = \text{GM}(F2, F4, F7, F10)$ | Retained in $A$. Evaluated alongside $F4, F7, F10$. |
| **F3** | Witness | Top-level $S$ (Witness sub-component) | $E = \text{GM}(F3, F4, F12, \text{energy}^2)$ | Moved from $S$ into $E$. Tri-witness consensus now gates Energy telemetry integrity. |
| **F4** | Clarity | Top-level $A$ & $U$ | $A = \text{GM}(F2, F4, F7, F10)$ & $E = \dots$ | Dual-mapped into $A$ (intent) and $E$ (logging trace). Direct input to `clarity_score`. |
| **F5** | Peace² | Top-level $S$ | $P = \text{GM}(F1, F5, F11, F13)$ | Moved from $S$ into $P$. Human dignity & non-escalation directly scale Peace ($P$). |
| **F6** | Empathy | Top-level $H$ (Human) | $X = \text{GM}(F6, F8, F9, \text{exploration})$ | Demoted from top-level $H$ into $X$. Harm assessment gates exploration capacity. |
| **F7** | Humility | Top-level $U$ (Uncertainty) | $A = \text{GM}(F2, F4, F7, F10)$ | Moved from $U$ into $A$. Epistemic uncertainty ($\Omega$) bounds Authority directly. |
| **F8** | Genius | Top-level $S$ | $X = \text{GM}(F6, F8, F9, \text{exploration})$ | Moved from $S$ into $X$. Efficiency threshold ($G \ge 0.80$) bounds exploration efficiency. |
| **F9** | Anti-Hantu | Top-level $H$ (Human) | $X = \text{GM}(F6, F8, F9, \text{exploration})$ | Demoted from top-level $H$ into $X$. Non-simulation rule gates search novelty. |
| **F10** | Ontology | Top-level $A$ | $A = \text{GM}(F2, F4, F7, F10)$ | Retained in $A$. Guarantees non-LLM ground-truth evidence in Authority calculation. |
| **F11** | Auth | Top-level $P$ | $P = \text{GM}(F1, F5, F11, F13)$ | Retained in $P$. SCT token resolution & VAULT999 logging. Input to `auditability_score`. |
| **F12** | Injection | Top-level $E$ | $E = \text{GM}(F3, F4, F12, \text{energy}^2)$ | Retained in $E$. Prompt-injection barrier integrity gates substrate Energy. |
| **F13** | Sovereign | Top-level $P$ & $H$ | $P = \text{GM}(F1, F5, F11, F13)$ | Absolute human veto & `888 HOLD` ratifications anchored in $P$. |

---

## 🧮 2. Derivation of Internal Metric Levers

To maintain the 4-variable top-level identity $G = A \cdot P \cdot E \cdot X$, candidate metric levers are derived strictly as **sub-floor measurement aggregators**:

### 1. `auditability_score` ($F4 / F11$ Lever)
$$\text{auditability\_score} = \min(F4_{\text{trace}}, F11_{\text{receipt}}) \in [0.0, 1.0]$$
- **Function:** Measures whether an action leaves a complete, unambiguous, append-only log in `VAULT999`.
- **Routing:** Operates as a constituent input inside $A$ ($F4$) and $P$ ($F11$). Does **not** add a 5th top-level variable.

### 2. `clarity_score` ($F4 / F2$ Lever)
$$\text{clarity\_score} = 1.0 - \max(0.0, \Delta S) \cdot \Psi \in [0.0, 1.0]$$
- **Function:** Measures entropy reduction ($\Delta S \le 0$) combined with reality-grounding ($\Psi$).
- **Routing:** Operates as a constituent input inside $A$ ($F4, F2$) and $E$ ($F4$). Does **not** add a 5th top-level variable.

---

## 🔬 3. Quarantine & Replay Specification (Step C)

Before any code path switches to $G = A \cdot P \cdot E \cdot X$:

1. **Quarantine Flag:** The legacy calculation ($A \cdot P \cdot H \cdot S \cdot U \cdot E^2$) remains accessible via `--legacy-apex`.
2. **Side-by-Side Replay Script:** `scripts/replay_apex_comparison.py` will read historical receipts from `VAULT999`, compute both `apex_legacy` and `apex_v2`, and output a side-by-side delta matrix.
3. **Acceptance Threshold:**  
   - Mean Delta $|G_{v2} - g_t| \le 0.05$  
   - Max Delta $|G_{v2} - g_t| \le 0.10$  
   - Verdict Flips $== 0$

---

## 🚨 4. Empirical 50-Receipt Audit Result (2026-07-26)

> [!CAUTION]
> **VERDICT: 888_HOLD — REPLAY ACCEPTANCE BAND BREACH DETECTED**  
> Execution of `scripts/replay_apex_comparison.py` against 50 recent `VAULT999/SEALED_EVENTS.jsonl` receipts yielded:
> - **Mean Delta $|G_{v2} - g_t|$:** `0.4027` (Breached $\le 0.05$)
> - **Max Delta $|G_{v2} - g_t|$:** `0.4027` (Breached $\le 0.10$)
> - **Verdict Flips:** `50 / 50` (`SABAR` $\rightarrow$ `SEAL`) (Breached $== 0$)
> 
> **Root Cause:** Legacy $g(t)$ multiplies 6 raw fractional terms, compounding suppression ($0.5052$), whereas $G = \text{GM}(A, P, E, X)$ computes Nash geometric means ($0.9079$).  
> **Constitutional Impact:** `APEX_T000.md` remains under **`888 REVISION HOLD`**. The kernel math is **UNCHANGED**.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
