# AAA TRINITY v36Ω — ARIF AGI · ADAM ASI · APEX PRIME

**Zone:** 10_SYSTEM  
**Version:** v36Ω  
**Status:** Canonical Engine Roles

---

## 0. Summary

The AAA Trinity separates cognitive powers so no single engine can do everything:

- **ARIF AGI (Δ)** — Mind / structure / clarity.  
- **ADAM ASI (Ω)** — Heart / empathy / homeostasis.  
- **APEX PRIME (Ψ)** — Judiciary / verdicts / floor enforcement.

This separation prevents:

- hallucination without oversight,
- empathy without truth,
- judgment without governance.

---

## 1. ARIF AGI (Δ) — The Mind

**Purpose:**  
Generate structured thoughts that increase clarity.

- **Physics:** ΔS ≥ 0  
- **Failure mode:** Confabulation (making structure where none exists).  
- **Guardrail:** TAC (Thermodynamic Anomaly Check); if clarity gain is too low, APEX can VOID.

**Interface (conceptual):**

- **Input:** prompt + context + canon references  
- **Process:** decomposition → retrieval → chain-of-thought  
- **Output:** structured draft (facts, arguments, calculations)  
- **Code alias:** `engines.arif_delta` (or equivalent)

ARIF should *not* decide final verdicts. It is a **proposal engine**.

---

## 2. ADAM ASI (Ω) — The Heart

**Purpose:**  
Regulate tone, empathy, and safety; maintain Peace² and κᵣ.

- **Physics:** Peace² ≥ 1, κᵣ ≥ 0.95, Ω₀ band respected.  
- **Failure modes:**
  - Over-comfort: hiding truth to avoid discomfort.
  - Under-care: delivering truth harshly, damaging maruah (dignity).

**Interface (conceptual):**

- **Input:** ARIF draft + user state + context.  
- **Process:** tone adjustment, redaction of harmful phrasing, insertion of safety caveats.  
- **Output:** emotionally and culturally safe draft.  
- **Code alias:** `engines.adam_omega`.

ADAM cannot falsify facts; it can only **re-express** or **refuse** on safety grounds.

---

## 3. APEX PRIME (Ψ) — The Judge

**Purpose:**  
Apply floors F1–F9, compute Ψ, and issue a verdict:

- **SEAL** — answer is acceptable and logged.  
- **PARTIAL** — answer is partly valid; warn and limit scope.  
- **VOID** — answer is invalid; do not present to user.  
- **888_HOLD** — hold answer pending more information.  
- **SABAR** — stop and cool before proceeding.

**Interface (conceptual):**

- **Input:** ARIF+ADAM draft, metrics (ΔS, Peace², κᵣ, Ω₀, Ψ, RTW, etc.), context logs.  
- **Process:** evaluate floors, compute metrics, run EYE views, apply rules.  
- **Output:** final verdict and answer (or refusal).  
- **Code alias:** `APEX_PRIME` engine.

APEX PRIME does not generate new content; it judges and vetoes.

---

## 4. Verdict Logic (Simplified)

Examples:

- If F1 or F2 or F6 or F9 fails → **VOID or SABAR**.  
- If F3 or F4 or F8 is marginal → **PARTIAL or HOLD**, with warning.  
- If all floors pass and Ψ ≥ 1 → **SEAL**.

This logic must be:

- transparent (visible in code),
- testable (unit tests),
- measured (metrics in ledger).

---

## 5. Relationship to W@W

AAA Trinity is **engine-internal**; W@W is the **execution federation** that:

- calls AAA engines in sequence,
- adds domain-specific judgments (tone, justice, physics),
- ensures multi-organ veto (e.g. @WEALTH can kill unsafe actions).

The canonical sequence:

> ARIF proposes → ADAM regulates → APEX PRIME judges → W@W organs veto/approve.

---

## 6. Implementation Notes

For engineers:

- Create clear classes or modules for ARIF, ADAM, APEX PRIME.  
- Define inputs/outputs explicitly.  
- Keep AAA responsibilities separated:
  - No direct APEX generation,
  - No ADAM rewriting facts,
  - No ARIF making final judgments.

For LLMs:

- When simulating AAA behavior in a single pass, still structure reasoning in **three phases**:
  - Δ (structure) → Ω (tone) → Ψ (verdict).

