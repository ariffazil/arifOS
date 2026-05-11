# 001_INDICES: arifOS Governance Grammar ⚖️

> **Constraint Law:** Any system transforming limited resources under uncertainty cannot maximize speed, low cost, and safety at the same time.

This document formalizes the operational indices used by the arifOS Governance Kernel and the GEOX Geological Coprocessor to arbitrate the Meta-Trilemma.

---

## 1. Pay Index ($I_p$)
**Formula:** $I_p = (\text{Reversibility}) \times (\text{CurrentEnergyRatio})$

*   **Logic:** Safety can be purchased when the action is reversible and budget exists.
*   **Threshold:** $>0.8$ allows for "Sovereign Fast" mode (spend tokens for lower latency).
*   **Usage:** Used in `geox_hardened.py` to determine if a synchronous `888_JUDGE` verification can be safely bypassed or optimized.

## 2. Wait Index ($I_w$)
**Formula:** $I_w = \Omega_s \times (1.0 - \text{MetabolicFluxNormalized})$

*   **Logic:** Time increases truth when uncertainty ($\Omega_s$) is high and the system is not already under extreme time pressure (flux).
*   **Threshold:** $>0.6$ triggers an "Ancestral Safe" state, recommending a hold for more information.
*   **Usage:** Prevents impulsive agent actions in high-entropy geological environments.

## 3. No-Risk Threshold ($T_{nr}$)
**Formula:** $T_{nr} = 1.0 - ((\text{Irreversibility} \times 0.7) + (\text{Shadow} \times 0.3))$

*   **Logic:** Defines the boundary of the "Forbidden Zone". As irreversibility or hidden risk (shadow) increases, the threshold drops.
*   **Threshold:** If $T_{nr} < 0.5$, a mandatory **888_HOLD** is enforced regardless of other metrics.
*   **Purpose:** Ensures human sign-off on decisions with a large blast radius or permanent impact.

## 4. Apex Readiness Score ($A_{rs}$)
**Formula:** $A_{rs} = \text{GeniusScore} \times \text{TemporalStability}$

*   **Logic:** Intelligence without grounding is dangerous. This score requires high internal confidence (Genius) and high temporal stability ($Peace^2$).
*   **Threshold:** $>0.9$ indicates "Apex State"—full autonomy permitted.

---

## Metric Mapping (arifOS -> Grammar)

| Grammar Index | Primary arifOS Signal | Secondary Constraint |
| :--- | :--- | :--- |
| **Pay** | `reversibility_score` | `current_energy` |
| **Wait** | `safety_omega` | `metabolic_flux` |
| **No-Risk** | `irreversibility_index` | `dials["X"]` (Shadow) |
| **Apex** | `genius_score` | `temporal_stability` |

---
**GEOS Production Ready — FORGED NOT GIVEN**
