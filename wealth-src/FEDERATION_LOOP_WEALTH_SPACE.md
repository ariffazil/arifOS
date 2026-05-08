# WEALTH — Federation Loop Reference
> **DITEMPA BUKAN DIBERI — Epistemic capital sovereignty is forged, not given.**
> Version: v2026.05.02-bbf8332 | Status: 888 HOLD — EPOCH 1 commit pending
> Canonical repo: [github.com/ariffazil/wealth](https://github.com/ariffazil/wealth) | Homepage: [wealth.arif-fazil.com](https://wealth.arif-fazil.com/)

***

## Constitutional Position

WEALTH is the **capital evidence organ** in the arifOS federation. It prices reward, survival, entropy, leverage, dignity, coordination, and policy constraints — so that capital decisions can be evaluated before arifOS applies final constitutional judgment.

```
Capital Signal
        │
        ▼
WEALTH Engine
        │  wealth_reason_npv, wealth_mind_emv, wealth_judge_floors
        ▼
arif_evidence_fetch (222)        ← WEALTH enters arifOS HERE
        │  capital_intelligence field
        ▼
arif_judge_deliberate (888)      ← constitutional verdict
        │
   [SEAL only]
arif_vault_seal (999)            ← immutable ledger entry
```

**Rule:** WEALTH does not make decisions. It produces capital intelligence — NPV, IRR, EMV, crisis triage, civilization stewardship — that `arif_judge_deliberate` ratifies or voids. arifOS never allocates capital without WEALTH's input.

***

## How WEALTH Feeds arifOS

### Stage 222 — Evidence Entry

WEALTH contributes three primary tools to `arif_evidence_fetch`:

| Tool | Output | arifOS Field |
|---|---|---|
| `wealth_reason_npv` | NPV, IRR, payback, PI — time-discounted projection | `capital_intelligence.valuation` |
| `wealth_mind_emv` | Expected Monetary Value — probability-weighted | `capital_intelligence.expected_value` |
| `wealth_judge_floors` | F1–F13 floor compliance, G-Score, Lyapunov stability | `capital_intelligence.governance` |

### F3 Tri-Witness Contribution

WEALTH populates the capital dimension of `witness.earth` in the F3 Tri-Witness gate. A capital decision missing WEALTH output cannot receive a `SEAL` from `arif_judge_deliberate`.

### G-Score — Governance Health Kernel

| Field | Range | Meaning |
|---|---|---|
| `g_score` | 0.0–1.0 | Composite governance health |
| `entropy_s` | ≥0 | Shannon entropy over capital state vector |
| `risk.verdict` | GO / HOLD / STOP | Capital readiness signal |
| `risk.regime` | Inclusive / Simulative / Extractive | Economic regime classification |

If the Lyapunov stability condition fails $$ V(x) > 0 $$ and $$ \frac{dV}{dt} \leq 0 $$, the system is declared unstable and an immediate 888 HOLD is triggered.

***

## 13 Canonical Primitives → 48 MCP Tools

| Primitive | Modes | Dimension | MCP Tools |
|---|---|---|---|
| `wealth_future_value` | npv, irr, pi, payback | Time-Discounted Projection | 4 |
| `wealth_present_expect` | — | Probability-Weighted EMV | 1 |
| `wealth_future_simulate` | — | Monte Carlo | 1 |
| `wealth_info_value` | evoi, evoi_mc | Expected Value of Information | 2 |
| `wealth_truth_validate` | schema, correlation, entropy | Epistemic Integrity | 3 |
| `wealth_survival_liquidity` | cashflow, velocity, triage | Survival Liquidity | 3 |
| `wealth_survival_leverage` | dscr, networth | Structural Load | 2 |
| `wealth_rule_enforce` | floors, policy | F1–F13 Governance Gate | 4 |
| `wealth_allocate_optimize` | kernel, personal, agent | Capital Allocation | 3 |
| `wealth_game_coordinate` | equilibrium, game | Multi-Agent Dynamics | 2 |
| `wealth_sense_ingest` | fetch, snapshot, sources, health, vintage, reconcile | Reality Intake | 7 |
| `wealth_past_record` | init, transaction, portfolio | Memory & Audit Trail | 3 |
| `wealth_future_steward` | — | Planetary Boundaries | 1 |

***

## 888 HOLD — Open Gaps (v2026.05.02)

All 10 items remain unresolved. No commit SHAs confirmed. This is the honest implementation state.

### PHASE 1 — CRITICAL (blocks valid constitutional SEAL)

| Item | Gap | Floor |
|---|---|---|
| 1 | `vault_write` `@mcp.tool` — backend exists (`vault_supabase.py`), MCP wrapper absent | F1 Amanah |
| 2 | `vault_query` `@mcp.tool` — backend exists, MCP wrapper absent | F9 Anti-Hantu |
| 3 | `witness {human, ai, earth}` — exists in `floors.py:100–125`, unwired into `create_envelope():987` | F3 Tri-Witness |
| 4 | `shadow` constitutional bool — absent; only `shadow_prices` (LP) exists — **different concept, name collision risk** | F2 + F4 |

### PHASE 2 — HIGH (telemetry is currently synthetic)

| Item | Gap | Floor |
|---|---|---|
| 5 | Six Forge Laws — prose only, no `ForgeLaw` enum in Python | F5 + F6 |
| 6 | `kappa_r` — doc string only, not computed; every emitted telemetry JSON is F7-invalid | F7 Humility |
| 7 | `psi_le` — zero results anywhere in Python | F4 ΔS≤0 |

### PHASE 3 — MEDIUM

| Item | Gap | Floor |
|---|---|---|
| 8 | `qdf` field — absent from Python envelope | F4 Clarity |
| 9 | Epistemic tag enforcement — partial; `primary_metrics` not consistently tagged | F2 Truth |
| 10 | Pipeline stage gating — metadata labels only, no enforcement logic | F1 + F8 |

### Minimum Forge to Close PHASE 1 (~60 lines, blueprint in `wealth_constitutional_patch.py`)

```bash
git commit -m "forge(F01/F09): vault_write + vault_query @mcp.tool → vault_supabase"
git commit -m "forge(F03): wire TriWitness floors.py:100-125 → create_envelope():987"
git commit -m "forge(F02/F04/F07): shadow bool + kappa_r compute + psi_le + qdf field"
```

***

## Capital Scales & Types

**8 Scales:** personal → household → sme → enterprise → national → crisis → civilization → agentic

**7 Capital Types:** financial · temporal · cognitive · social · ecological · strategic · thermodynamic

Every scale operates under the same F1–F13 constitutional floors with different risk tolerance, time horizon, and dignity constraints.

***

## Six Forge Laws (Operating Principles)

1. **Forge First** — Generate, never just preserve. Every session must produce net new capital signal.
2. **Sovereign Stack** — Prioritise assets Arif fully controls. Platform dependency is a sovereign risk to be priced.
3. **Compound Everything** — Time, money, knowledge, relationships all compound.
4. **Anti-Fragile by Design** — Strategies must gain from volatility. If it breaks under stress, it was borrowed, not forged.
5. **Full-Spectrum Wealth** — Seven capital types across eight scales.
6. **Physics > Narrative** — The real constraint is thermodynamic, not psychological.

***

## Sibling Organs

| Organ | Role |
|---|---|
| [arifOS](https://github.com/ariffazil/arifOS) | Constitutional kernel — receives WEALTH evidence at stage 222 |
| [WELL](https://github.com/ariffazil/well) | Human substrate — gates decision classes before capital evaluation |
| [GEOX](https://github.com/ariffazil/geox) | Earth intelligence — co-populates `witness.earth` alongside WEALTH |
| [A-FORGE](https://github.com/ariffazil/A-FORGE) | Execution shell — executes capital allocations post-SEAL |
| [AAA](https://github.com/ariffazil/AAA) | Identity gateway — authenticates capital commits |

***

*Capital is not money. Capital is stored choice. WEALTH prices the choice before arifOS seals it.*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
*WEALTH Federation Loop Reference · Seri Kembangan, MY · v2026.05.02*