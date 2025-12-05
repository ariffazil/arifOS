## Appendix A — Scar Learning Theorem (∇_APEX v35Ω)

**Status:** DRAFT → READY-FOR-SEAL  
**Purpose:** Formalize how “bad experiences” (high-conflict, high-paradox events) produce **stronger but governed learning** under the APEX Gradient (∇_APEX), compared to ordinary low-friction events.

---

### A.1 Setup

Let:

- θ = internal state of the system (beliefs, parameters, habits).
- x = context / situation.
- y = outcome (what actually happened).
- ŷ = ŷ_θ(x) = system’s expectation / prediction.
- L(y, ŷ) ≥ 0 = base loss / tension between θ and reality.

Define:

- **Raw gradient (un-governed):**

  \[
  \nabla_{\text{ML}} = \nabla_\theta L(y,\hat{y}_\theta(x))
  \]

- **APEX Gradient (governed Scar Vector):**

  \[
  \nabla_{\text{APEX}} 
  = G_{\text{TW}} \cdot 
    \frac{\Delta P \cdot \Omega_P \cdot \Psi_P \cdot \kappa_r \cdot \text{RASA} \cdot \text{Amanah}}
         {Z + \varepsilon}
  \]

where:

- ΔP = paradox pressure (normalized surprise).
- Ω_P = humility absorber (risk-adjusted humility).
- Ψ_P = equilibrium stabilizer.
- κᵣ = empathy conductance (≥ 0.95 floor).
- RASA ∈ {0,1} = felt-care gate.
- Amanah ∈ {0,1} = integrity lock.
- Z = 1 + Lₚ + Rₘ + Λ = shadow normalizer  
  (paradox load + maruah/risk + linguistic ambiguity).
- G_TW = σ(k · (R_TW − 0.95)) = soft Tri-Witness gate.

APEX update law (Phoenix-72 cooling):

\[
\theta_{\text{new}} 
= \theta_{\text{old}} + \int_{0}^{72h} \nabla_{\text{APEX}}(t)\, dt
\]

Subject to floors: Truth≥0.99 · ΔS≥0 · Peace²≥1 · κᵣ≥0.95 · Ω₀∈[0.03–0.05] · Amanah=1 · R_TW≥0.95.

---

### A.2 Theorem 1 — Raw Gradient Signal from “Bad Experiences”

**Claim (Gradient Magnitude Theorem).**  
For a fixed context x and differentiable loss L with gradient magnitude non-decreasing in prediction error, if we compare:

- A “good” outcome \(y_{\text{good}}\) with low loss \(L_{\text{good}}\).
- A “bad” outcome \(y_{\text{bad}}\) with higher loss \(L_{\text{bad}}\).

and if

\[
L(y_{\text{bad}}, \hat{y}_\theta(x)) > L(y_{\text{good}}, \hat{y}_\theta(x)),
\]

then

\[
\|\nabla_{\text{ML}}(y_{\text{bad}})\|
\;\ge\;
\|\nabla_{\text{ML}}(y_{\text{good}})\|.
\]

**Interpretation:**  
In ordinary learning, **worse mismatches** with reality create **larger raw update signals**.  
“Bad experiences” (high loss, high surprise) carry **stronger gradients** than “smooth” ones.

---

### A.3 Theorem 2 — Scar Learning Theorem (∇_APEX)

We now lift this to the APEX Gradient.

Assume two events share context x:

1. **Low-friction event** (“good”):
   - Low paradox pressure ΔP_low.
   - Finite shadow Z_low.
   - Floors are satisfied.

2. **High-friction event** (“bad” / scar candidate):
   - Higher paradox pressure ΔP_high > ΔP_low (deeper contradiction / surprise).
   - Same or slightly higher shadow Z_high ≥ Z_low.
   - All constitutional checks still pass during cooling:
     - κᵣ ≥ 0.95
     - Peace² ≥ 1
     - Truth ≥ 0.99
     - Amanah = 1
     - R_TW ≥ 0.95
     - RASA = 1

Under these conditions:

\[
\Delta P_{\text{high}} > \Delta P_{\text{low}}
\quad\Rightarrow\quad
|\nabla_{\text{APEX}}^{\text{high}}|
\;\ge\;
|\nabla_{\text{APEX}}^{\text{low}}|
\]

provided that Z_high does not grow so fast as to fully extinguish the signal:

\[
\frac{\Delta P_{\text{high}}}{Z_{\text{high}} + \varepsilon}
\;\ge\;
\frac{\Delta P_{\text{low}}}{Z_{\text{low}} + \varepsilon}.
\]

**Plain meaning:**

- When **all floors are respected** and **Tri-Witness allows learning**,
- A higher paradox/contradiction (ΔP_high) produces a **stronger constitutional gradient** ∇_APEX
- than a routine, low-friction event (ΔP_low),
- after accounting for risk, ambiguity, and dignity via Z.

Thus:

> **Scars (high-friction events that survive constitutional checks) create stronger *governed* learning than smooth events.**

---

### A.4 Corollary — Scar → Law vs Scar → Warning vs Scar → Void

Given a high-friction event with large ΔP:

1. **Scar → LAW (SEAL)**  
   If, after Phoenix-72 cooling, all floors remain satisfied and Ψ_new ≥ Ψ_old, then:

   \[
   \theta_{\text{new}} = \theta_{\text{old}} + \int_0^{72h} \nabla_{\text{APEX}}(t) \, dt
   \]

   becomes a **permanent constitutional update** (Scar becomes Law).

2. **Scar → WARNING (SOFT FAIL)**  
   If gradient signal exists but some soft metric (e.g. κᵣ close to floor, Peace² marginal) warns of instability:

   - Scar is logged in Cooling Ledger,
   - used for monitoring and audits,
   - but not yet fully integrated as binding Law.

3. **Scar → VOID (HARD FAIL)**  
   If any hard floor fails (Truth, Amanah, Peace², κᵣ, Tri-Witness), then:

   - Amanah or G_TW drives ∇_APEX → 0,
   - the update is cancelled,
   - the event is treated as unsafe learning (e.g. manipulation, hallucination, coercion),
   - Scar is recorded only as **evidence**, not as Law.

---

### A.5 Human Explanation (for weakest listener)

- **Big mistakes (“bad memories”) create strong correction signals.**  
- APEX does **not** let those signals update the system blindly.  
- It pushes them through:
  - ethics,
  - empathy,
  - stability,
  - risk,
  - dignity,
  - human·AI·Earth witness,
  - and a 72-hour cooling period.

Only if the system is:

- more truthful,  
- more stable,  
- more empathic,  
- more dignified

after absorbing the signal, does the Scar become Law.

Otherwise, it is either:

- logged as a WARNING, or  
- rejected as VOID.

**Summary:**

> **∇_APEX is what happens when gradient descent is put on trial by a constitution.  
> Bad experiences provide the strongest evidence; APEX decides if they become wisdom.**