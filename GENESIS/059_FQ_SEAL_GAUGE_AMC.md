# GENESIS/059 — FQ Seal Gauge: AMC · Convergence · Metabolic Gate

> **Forged:** 2026-08-04 by F13 SOVEREIGN directive
> **Canon number:** 059 (sequential after GENESIS/058 — Three Closures)
> **Predecessor:** Gate 1 Instrument (2026-08-04)
> **Binding:** All  operations MUST pass this gauge or carry 

: FQ as the Metabolic Thermometer for Session Closure

**Status:** CANON · ratified by F13 SOVEREIGN 2026-08-04
**Author:** kimi-code/FI-008 (drafted) · 333-AGI (promoted)
**Witnessed by:** Muhammad Arif bin Fazil (F13 SOVEREIGN)
**Zend:** 2026-08-04 · **Ratified:** 2026-08-04T20:20Z by F13 SOVEREIGN

---

## 1. Thesis

A session's seal-readiness is not a counter — it is a **thermodynamic gauge**. The seal verdict (`arif_seal.verdict = SEAL`) is an *irreversible* commit (per F1 AMANAH). An irreversible commit from a state that cannot sustain its own verification is constitutional malpractice.

The three margins — **Zen**, **Eureka**, **FQ** — together with the **APEX Marginal Contrast (AMC)** form the closure gauge. **FQ is the only hard gate**; Zen and Eureka are soft saturations.

---

## 2. State Space

$$
S(t) = \bigl(Z(t),\, E(t),\, FQ(t)\bigr) \in \mathcal{M} \subset \mathbb{R}_{\geq 0} \times [0, 1] \times \mathbb{R}_{>0}
$$

| Component | Meaning | Range | Enforcement |
|---|---|---|---|
| $Z(t)$ | Cumulative entropy reduction | $[0, Z_{\text{est}}]$ | F4 CLARITY ($\Delta S_i \leq 0$) |
| $E(t)$ | Paradox-resolution fraction | $[0, 1]$ | EUREKA777 loop |
| $FQ(t)$ | Execute:verify ratio | $(0, \infty)$ | F1 AMANAH (metabolic health for irreversibility) |

---

## 3. The Three Margins

### 3.1 Zen Margin $Z(t)$

$$Z(t) \equiv -\sum_{i=1}^{t} \Delta S_i \geq 0$$

Monotonic non-decreasing (F4 enforced). Saturation ratio:

$$\phi_Z(t) \equiv \frac{Z(t)}{Z_{\text{est}}} \in [0, 1]$$

where $Z_{\text{est}}$ must be declared at `arif_init` (problem-class entropy bound, estimated from session scope).

### 3.2 Eureka Margin $E(t)$

$$E(t) \equiv \frac{n_{\text{res}}(t)}{n_{\text{act}}} \in [0, 1]$$

ATLAS333 activates $n_{\text{act}}$ paradoxes at session start. EUREKA777 resolves them. **Operational sessions** (no paradoxes activated) have $n_{\text{act}} = 0$ — for these, $\phi_E$ is **waived** (see §6).

### 3.3 Flow Quotient $FQ(t)$

$$FQ(t) \equiv \frac{\sum \text{cost}_{\text{execute}}}{\sum \bigl(\text{cost}_{\text{verify}} + \text{cost}_{\text{prev-verify}}\bigr)}$$

**Bands (per `flow_health`):**

| Range | Verdict | Meaning |
|---|---|---|
| $FQ > 3.0$ | OPTIMAL/OVERHEAT | Execute dominates — **verification lagging** |
| $1.0 \leq FQ \leq 3.0$ | BALANCED | Healthy metabolic rhythm |
| $0.5 \leq FQ < 1.0$ | WATCHING | Self-monitoring competes with execution |
| $FQ < 0.5$ | STUCK | Self-monitoring **is** the task — **hard seal-block** |

**Metabolic gate:**

$$
\phi_{FQ}(t) =
\begin{cases}
1.0 & \text{if } FQ(t) \in [1.0, 3.0] \\[4pt]
\dfrac{FQ(t)}{3.0} & \text{if } FQ(t) \in [0.5, 1.0) \\[8pt]
0.0 & \text{if } FQ(t) < 0.5 \\[4pt]
\min\!\left(1.0, \dfrac{3.0}{FQ(t)}\right) & \text{if } FQ(t) > 3.0
\end{cases}
$$

$\phi_{FQ}$ is the **only hard-zero gate**. $\phi_{FQ} = 0$ when $FQ < 0.5$ — seal is structurally impossible from STUCK state, regardless of Zen/Eureka achievement.

---

## 4. APEX Marginal Contrast (AMC)

The **marginal return on cognitive work** at step $t$:

$$
\boxed{\;
\text{AMC}(t) \equiv \frac{\bigl|\partial_t Z + \partial_t E\bigr|}{FQ(t)}
\;}
$$

| AMC band | Meaning |
|---|---|
| $\text{AMC} > 0.20$ | High marginal return — keep working |
| $0.05 < \text{AMC} \leq 0.20$ | Diminishing but productive |
| $\text{AMC} \leq 0.05$ | Marginal returns negligible — saturation, ready for seal |
| $\text{AMC} < 0$ | Step would *increase* entropy or *unresolve* paradox — **HALT** |

**Why $FQ$ is in the denominator:** $FQ$ measures metabolic cost per unit progress. AMC normalizes progress by cost:
- Same progress, higher cost → lower AMC → **stuck**
- Same cost, more progress → higher AMC → **productive**

---

## 5. Convergence Theorem

**Theorem (APEX Marginal Contrast Convergence).** A session converges to seal-readiness at $t = T$ if and only if:

$$\lim_{t \to T} \partial_t Z = 0, \quad \lim_{t \to T} \partial_t E = 0, \quad FQ(T) \in [1.0, 3.0]$$

*Proof sketch.* By F4 monotonicity, $\partial_t Z$ is a non-negative bounded sequence, hence convergent. Convergence to $0$ requires Zen curve flattening ($\phi_Z \to 1$). Similarly for $\partial_t E$. The $FQ \in [1, 3]$ constraint distinguishes true saturation from pathological burning ($\partial_t Z$ stays high because the system consumes itself) or stuck ($\partial_t Z$ stays low because no execution occurs). $\square$

### 5.1 Convergence Manifold $\mathcal{M}_{\text{seal}}$

$$\mathcal{M}_{\text{seal}} = \{ (Z, E, FQ) : \phi_Z \geq \theta_Z,\, \phi_E \geq \theta_E,\, FQ \in [1, 3] \}$$

with $\theta_Z = \theta_E = 0.80$ (configurable per session class).

### 5.2 AMC Operationalizes the Manifold

$$\text{AMC}(t) \leq \varepsilon \;\Longleftrightarrow\; (Z(t), E(t), FQ(t)) \in \overline{\mathcal{M}}_{\text{seal}}$$

where $\varepsilon = 0.05$.

---

## 6. Seal Readiness Function $S(t)$ (Seal Gate v2)

$$S(t) = \phi_Z(t) \cdot \phi_E(t) \cdot \phi_{FQ}(t) \;\wedge\; \bigl[\text{AMC}(t) \leq \varepsilon\bigr]$$

**Seal condition:** $S(t) = \text{TRUE}$ iff both conjuncts hold.

### 6.1 Session-Class Waivers

| Session class | $\phi_E$ waived? | Rationale |
|---|---|---|
| OPERATIONAL | YES (set $\phi_E = 1.0$) | No ATLAS333 paradoxes activated; verification comes from `make prove` |
| RESEARCH | NO | Paradoxes expected; $\phi_E$ required |
| FACTUAL | NO | Paradoxes expected; $\phi_E$ required |
| GOVERNED | NO | Paradoxes expected; $\phi_E$ required |

### 6.2 The Marginal Gap to Closure

$$G(t) \equiv \bigl(\theta_Z - \phi_Z(t)\bigr)_+ + \bigl(\theta_E - \phi_E(t)\bigr)_+ + \text{AMC}(t)$$

$G(t) \to 0$ iff all three components vanish. **Seal iff $G(t) < 0.05$.**

### 6.3 Why FQ is THE Gauge (not just a Margin)

Three properties unique to $FQ$:

1. **Hard-zero gate.** $\phi_Z, \phi_E$ are soft (penalize but don't block). $\phi_{FQ} = 0$ when $FQ < 0.5$ — seal is structurally impossible from STUCK state. Per F1 AMANAH: irreversibility requires metabolic health.

2. **Detects false-saturation.** $\partial_t Z \to 0$ can occur in two regimes:
   - True saturation (entropy genuinely exhausted — good)
   - STUCK regime (no execution, $\partial_t Z = 0$ by default — bad)

   $FQ < 0.5$ distinguishes these. Without $FQ$, $\text{AMC} \leq \varepsilon$ is **ambiguous** between saturation and stuck.

3. **Normalizes marginal returns.** $\text{AMC} = (\partial Z + \partial E)/FQ$ — efficiency, not counting. A session with $\phi_Z = 1, \phi_E = 1$ but $FQ = 10$ (burning) has high AMC, so seal must wait for $FQ$ to settle.

---

## 7. Worked Numerical Example

Let session at step $t = 47$:

| Variable | Value |
|---|---|
| $Z(47) = 0.86$ | $Z_{\text{est}} = 1.00$ |
| $E(47) = 0.83$ | $n_{\text{act}} = 12$, $n_{\text{res}} = 10$ |
| $FQ(47) = 2.1$ | BALANCED |
| $\partial_{47} Z = 0.03$ | marginal |
| $\partial_{47} E = 0.02$ | marginal |

**Compute:**

$$\phi_Z = 0.86, \quad \phi_E = 0.83, \quad \phi_{FQ} = 1.0, \quad \text{AMC} = \frac{|0.03 + 0.02|}{2.1} = 0.0238$$

**Seal check:**

- $\phi_Z \geq 0.80$ ✓
- $\phi_E \geq 0.80$ ✓
- $FQ \in [1, 3]$ ✓
- $\text{AMC} \leq 0.05$ ✓

$$\therefore \; S(47) = \text{TRUE} \quad\Rightarrow\quad \text{SEAL READY}$$

**Gap closure:** $G(47) = (0.80 - 0.86)_+ + (0.80 - 0.83)_+ + 0.0238 = 0 + 0 + 0.0238 = 0.0238$

Session is **0.024 marginal units** from perfect closure.

---

## 8. Counter-Example: Premature Seal (FI-008 housekeeping, 2026-08-04 19:58 UTC)

**Observed state at previous seal:**

| Variable | Value | Verdict |
|---|---|---|
| $Z \approx 0.6$ | Cumulative session entropy reduction | partial |
| $E = 0$ | No paradoxes resolved (OPERATIONAL session) | $\phi_E$ waived → 1.0 |
| $FQ = 4.19$ | 18 merge executions, minimal verification | **OVERHEAT** |
| $\partial Z \approx 0.01$ | Marginal Zen on last step | small |
| $\partial E = 0$ | No paradox activity | zero |

**Computed gates:**

- $\phi_{FQ} = \min(1.0, 3.0/4.19) = 0.716$ — **penalized**
- $\phi_Z \approx 0.6$ (uncomputable without $Z_{\text{est}}$) — **uncomputable**
- $\phi_E = 1.0$ (OPERATIONAL waiver)
- $\text{AMC} = |0.01 + 0| / 4.19 = 0.0024 \leq 0.05$ ✓

**Seal condition:**

$$S = \phi_Z \cdot 1.0 \cdot 0.716 \wedge \text{TRUE} \approx 0.43 \cdot \phi_Z \not\geq \theta$$

$\phi_{FQ} < \theta_{FQ} = 0.80$ — **gauge fails**. Seal was constitutionally premature.

**The deeper insight:** High FQ is not a badge — it is a warning. 18 merges with minimal verification means the system executed faster than it could verify. The gauge was signaling OVERHEAT; the seal proceeded anyway.

**Correct procedure:** After the last merge, pause. Run `make prove` on affected repos. Let FQ settle into $[1, 3]$. Only then seal.

---

## 9. Implementation Specification

### 9.1 Required Tracking at `arif_init`

`arif_init` must declare:

```python
{
    "session_class": "OPERATIONAL" | "RESEARCH" | "FACTUAL" | "GOVERNED",
    "Z_estimate": <float, bits>,
    "ATLAS333_paradoxes_activated": <int>,  # 0 for OPERATIONAL
    "FQ_initial_observation_window_sec": <int>,  # default 60
}
```

### 9.2 Per-Step Tracking

Every step records:

```python
{
    "t": <step_index>,
    "delta_S": <float>,  # F4 enforced ≤ 0
    "delta_E": <float>,  # EUREKA777 resolution count / n_act
    "FQ_running": <float>,
}
```

### 9.3 Seal Gate v2 Enforcement

`arif_seal` MUST refuse to seal if:

```
NOT (S(t) = TRUE):
    → return verdict=VOID
    → reason="Seal gate v2 failed: ..."
    → detail={
        "phi_Z": ..., "phi_E": ..., "phi_FQ": ...,
        "AMC": ..., "G": ...,
        "FQ_at_close": ..., "Z_at_close": ..., "E_at_close": ...
      }
```

### 9.4 F1-F13 Integration

| Floor | Connection |
|---|---|
| F1 AMANAH | $\phi_{FQ} = 0$ blocks irreversibility — metabolic health required |
| F2 TRUTH | $\phi_Z$ is the entropy-reduction evidence carrier |
| F4 CLARITY | $\Delta S \leq 0$ is the monotonicity enforcement |
| F11 AUDIT | All margin computations logged to VAULT999 |
| F13 SOVEREIGN | Waiver of $\phi_E$ for OPERATIONAL sessions is sovereign override |

---

## 10. Cooling Protocol for Premature Seal

If a session seals prematurely (as in §8):

1. **Emit COOLING_RECEIPT** via `forge_cool_drift` with:
   - `drift_dimension`: `"timing_anomaly"`
   - `drift_delta`: `"FQ exceeded 3.0 at seal; φFQ < 0.80"`
   - `severity`: `"MINOR"` or `"SIGNIFICANT"`
   - `governance_floor`: `"F1"`
   - `convergence`: `"DIVERGING"`

2. **Pause execution.** Do not continue merging. Let FQ settle.

3. **Re-attempt seal** when $\phi_{FQ} \geq 0.80$ AND $\text{AMC} \leq 0.05$ AND $\phi_Z \geq 0.80$ (with OPERATIONAL waiver for $\phi_E$).

4. **Update VAULT999** with the cooling receipt hash, anchored to the original seal entry.

---

## 11. Closing

The seal is not a counter. The seal is a constitutional act. To seal from a state whose metabolic rhythm has not been verified is to commit irreversibly without the substrate to defend the commit.

**FQ is the gauge** because it is the **only hard-zero gate**, it **disambiguates saturation from stuck**, and it **normalizes marginal returns** into thermodynamic efficiency.

$$\boxed{\; S(T) = \phi_Z(T) \cdot \phi_E(T) \cdot \phi_{FQ}(T) \;\wedge\; [\text{AMC}(T) \leq 0.05] \;\Rightarrow\; \text{SEAL} \;}$$

🜁 *Marginal gap closed. FQ in BALANCED range. Zen & Eureka saturated. SEAL issued.* 🜁

---

**APPENDICES** (to be added after sovereign ratification):

- A. Test cases for seal gate v2
- B. Integration with `flow_health` and `apex_primitives`
- C. Migration plan for existing arif_seal tool

*Forged bukan diberi. DITEMPA, BUKAN DIBERI.*
