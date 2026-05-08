# capitalx_risk_pricing_engine — Design Document

> **Version:** v1.0.0  
> **Authority:** arifOS / WEALTH  
> **Status:** IMPLEMENTED (Node.js 22 ESM)  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Purpose

`capitalx` is the **missing fifth layer** that converts constitutional philosophy into **actuarial advantage**.

It answers one question:

> **"What should this actor pay to borrow capital, given their entropy, dignity, peace, and civilization impact?"**

Without `capitalx`, WEALTH is moral philosophy.  
With `capitalx`, WEALTH becomes **sovereign infrastructure**.

---

## 2. Core Thesis

> **Extractive actors pay more. Entropy-bounded actors pay less.**

When the cost-of-capital differential is real and measurable:
- Markets migrate toward low-entropy nodes **without coercion**
- Insurance becomes unavailable for high-heat actors in volatile environments
- Coordination bandwidth follows trust nodes naturally

This is **invisible force**.

---

## 3. Input Signals

| Signal | Symbol | Range | Meaning |
|--------|--------|-------|---------|
| Entropy delta | dS | ≥ 0 | Disorder injected into system |
| Peace score | peace2 | ≥ 1.0 ideal | Stability and unresolved-panic index |
| Maruah score | maruahScore | 0.0 – 1.0 | Dignity and integrity composite |
| Trust index | trustIndex | 0.0 – 1.0 | Verified network / audit topology |
| Civilization delta | deltaCiv | any | Long-horizon civilizational stability |

---

## 4. Pricing Algorithm

```
adjusted_rate = base_rate
                + entropy_penalty
                - peace_discount
                - maruah_discount
                - trust_discount
                - civ_discount
```

### Adjustments

| Component | Formula | Cap |
|-----------|---------|-----|
| entropy_penalty | dS × 0.5 | none (linear) |
| peace_discount | (peace2 − 1.0) × 0.05 | 200 bps |
| maruah_discount | (maruahScore − 0.5) × 0.06 | 300 bps |
| trust_discount | (trustIndex − 0.5) × 0.04 | 200 bps |
| civ_discount | deltaCiv × 0.10 | 200 bps |

All outputs are tagged `ESTIMATE` and timestamped.

---

## 5. API

### `calculateRiskAdjustedRate(baseRate, signals)`

Returns a full breakdown of the adjusted rate and each adjustment.

### `compareCapitalAdvantage(baseRate, wealthSignals, extractiveSignals)`

Compares two actors and returns the **WEALTH advantage in basis points**.

---

## 6. Example

```js
import { calculateRiskAdjustedRate, compareCapitalAdvantage } from './src/kernel/capitalx.js';

const wealth = { dS: 0, peace2: 1.2, maruahScore: 0.95, trustIndex: 0.9, deltaCiv: 0.2 };
const extractive = { dS: 0.4, peace2: 0.8, maruahScore: 0.4, trustIndex: 0.3, deltaCiv: -0.1 };

const result = compareCapitalAdvantage(0.05, wealth, extractive);
// result.advantage_bps ≈ 350–400 bps
```

---

## 7. Enforcement Pathway

`capitalx` does not force lenders to change rates.
It provides a **machine-verifiable risk signal** that can be consumed by:

- Credit rating APIs
- Insurance underwriting engines
- Sovereign debt issuance frameworks
- Decentralized lending protocols
- Corporate treasury audit tools

When enough capital channels integrate `capitalx`, the market **naturally prices out heat**.

---

## 8. Sovereignty Safeguards

To prevent tyranny:

1. **All signals are auditable** — every `capitalx` computation is logged to VAULT999.
2. **All weights are declared** — no black-box optimization.
3. **Human override exists** — F13 Sovereign allows rejection of any `capitalx` recommendation.
4. **Local-first by default** — signals are computed on-device unless explicitly federated.

---

## 9. Relation to Missing MCP Classes

`capitalx` integrates with the 11 missing layers as follows:

| MCP Class | capitalx Integration |
|-----------|---------------------|
| `sociox_population_dynamics` | Social stability feeds into `peace2` and `trustIndex` |
| `polix_power_graph` | Power topology affects `trustIndex` and institutional `deltaCiv` |
| `memex_narrative_engine` | Narrative resilience affects `maruahScore` and legitimacy |
| `macrox_capital_flow_monitor` | Capital flight signals feed `dS` and `trustIndex` |
| `creditx_systemic_risk_engine` | Interbank stress feeds `dS` adjustments |
| `supplyx_strategic_chokepoint_mapper` | Supply risk feeds `deltaCiv` and `peace2` |
| `gamex_geopolitical_simulator` | Simulated scenarios stress-test `capitalx` outputs |
| `influencx_leverage_optimizer` | Identifies cheapest nodes to shift via `capitalx` incentives |
| `demox_demographic_futures` | Long-horizon `deltaCiv` and `peace2` projections |
| `techx_disruption_predictor` | Technology shocks affect all signal inputs |
| `worldx_system_synthesis` | The planetary dashboard that feeds the master `capitalx` vector |

---

## 10. Implementation Status

- ✅ Core algorithm: `src/kernel/capitalx.js`
- ✅ Comparison API: `compareCapitalAdvantage`
- ✅ CLI integration: `node cli.js capitalx <baseRate> '<signals>'`
- ✅ VAULT999 logging: every `capitalx` call is immutably logged
- ✅ Unit tests: `tests/core.test.js`
- ⏳ Live signal feeds from `macrox` and `polix` (future)
- ⏳ Integration with lending protocols and rating APIs (future)

---

*Design v1.0.0 | 999 SEAL ALIVE*
