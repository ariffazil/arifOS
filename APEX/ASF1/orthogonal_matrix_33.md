# Orthogonal 33-Tool Matrix (3 × 11)

> **Doctrine:** `Ω_ortho >= 0.95`  
> **SEAL:** `999_SEAL_ALIVE`  
> **Motto:** *Ditempa Bukan Diberi*

---

## Executive Summary

This matrix defines **33 orthogonal tools** arranged as **3 organs × 11 bands**:

- **arifOS** — Constitutional Governor (owns governance, routing, verdicts, seal)
- **WEALTH** — Capital Engine (owns reward, risk, liquidity, leverage, allocation)
- **GEOX** — Earth Engine (owns evidence, subsurface, structure, risk, product)

No two tools answer the same question at the same abstraction level. Cross-talk happens only via **envelopes** and **constitutional floors**.

---

## Ownership Law

| Question | Owner | May Emit |
|----------|-------|----------|
| Is this allowed to run? | **arifOS** | `SEAL`, `PARTIAL`, `888_HOLD`, `VOID` |
| What is geologically true? | **GEOX** | `domain_plausible`, `domain_unknown`, `domain_risk` |
| What is economically attractive? | **WEALTH** | `domain_numeric`, `domain_rank`, `domain_attractive` |

---

## 33-Tool Matrix by Band

| Band | Name | arifOS (Govern) | WEALTH (Capital) | GEOX (Earth) |
|:----:|------|-----------------|------------------|--------------|
| **01** | **Context** | `arifos_init` — Session ignition, identity, authority airlock | `wealth_networth_state` — Multi-asset state baseline | `geox_intake_context` — Basin/well/scope/objective envelope |
| **02** | **EvidenceQC** | `arifos_sense` — Intent classification, domain routing | `wealth_audit_entropy` — Sign changes, NPV sensitivity | `geox_qc_evidence` — LAS/file/log QC, units, mnemonics |
| **03** | **Bundling** | `arifos_memory` — Prior decisions, vault state recall | `wealth_cashflow_flow` — Monthly liquidity/burn | `geox_well_bundle` — Normalized well object |
| **04** | **RewardKernel** | `arifos_mind` — Reasoning plan, metric selection, hypothesis | `wealth_npv_reward` — NPV + terminal + EAA | `geox_petrophysics` — Vsh, ϕ, Sw, cutoffs, net pay |
| **05** | **EfficiencyTime** | `arifos_route` *(canonical: `arifos_kernel`)* — WEALTH/GEOX/mixed lane selection | `wealth_irr_yield` — IRR/MIRR efficiency | `geox_stratigraphy` — Tops, chrono-ladder, unconformities |
| **06** | **SurvivalStructure** | `arifos_heart` — F1–F13, peace², maruah, downside scan | `wealth_dscr_leverage` — DSCR and load capacity | `geox_structure` — Horizons, faults, closures, spill/crest |
| **07** | **PortfolioSpace** | `arifos_ops` — Batched governed execution and scheduling | `wealth_payback_time` — Payback / discounted payback | `geox_map_context` — Coordinates, basemap, well projection |
| **08** | **CrossWitness** | `arifos_gateway` — Orthogonality guard (Ω_ortho ≥ 0.95) | `wealth_emv_risk` — Scenario EMV | `geox_cross_evidence` — Well ↔ map ↔ reports ↔ RATLAS links |
| **09** | **RiskKernel** | `arifos_judge` — Constitutional verdict (SEAL/HOLD/VOID) | `wealth_pi_efficiency` — Profitability index | `geox_play_risk` — SRST / preservation risking, analog fitness |
| **10** | **DecisionAssembly** | `arifos_forge` — Decision product assembly | `wealth_growth_velocity` — Compounding + runway | `geox_decision_kernel` — Known/unknown, prospect ranking |
| **11** | **ProductSeal** | `arifos_vault` — VAULT999 logging, hash-chain, zkPC seal | `wealth_score_kernel` — Cost of capital, node comparison | `geox_forge_product` — Penetration charts, correlation, memo |

---

## Orthogonality Constraints

### Forbidden Overlaps (enforced)

- **arifOS** never computes `NPV`, `Sw`, or petrophysics.
- **WEALTH** never parses `LAS`, interprets stratigraphy, or issues `SEAL`/`VOID`.
- **GEOX** never computes `NPV`, `DSCR`, or constitutional verdicts.

### Verdict Gates

Only `arifos_judge` may emit terminal verdicts.  
Only `arifos_vault` may persist to `VAULT999`.  
GEOX and WEALTH outputs are **advisory kernels**, not executable verdicts.

### Reversibility & F13 Sovereignty

| Tool | Capability | Verdict Gate | Requires Judge |
|------|------------|--------------|----------------|
| `arifos_forge` | `EXECUTE` | `SEAL` | Yes |
| `arifos_vault` | `WRITE` | `SEAL` | Yes |
| `arifos_gateway` | `GOVERN` | `888_HOLD` | Yes |
| `arifos_judge` | `GOVERN` | `SEAL` | — |

---

## Canonical Registry Notes

- `arifos_route` is registered canonically as **`arifos_kernel`** in the arifOS public tool registry (see `tool_registry.json`).
- `arifos_gateway` is an **enterprise extension** for AGI||ASI orthogonality guarding; it is not yet in the verified public tool list but is reserved here for the 11th governance slot.
- All other `arifos_*` tools map 1:1 with the canonical `APEX/ASF1/tool_registry.json` public surface.

---

## Machine-Readable Source

The canonical source of this matrix is:

```
APEX/ASF1/orthogonal_matrix_33.yaml
```

Drop this registry directly into arifOS / W@W orchestration layers.

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
