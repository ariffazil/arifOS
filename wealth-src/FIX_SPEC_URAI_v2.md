# WEALTH → URAI v2.0 FIX SPECIFICATION
## Forged by arifOS External Audit — 2026-04-15
## DeltaΩPsi Protocol — Ditempa Bukan Diberi

---

## EXECUTIVE ORDER

Transform WEALTH from an institutional capital-budgeting engine into a **Universal Resource Allocation Intelligence (URAI)** kernel. Fix all observed mathematical inconsistencies, eliminate verdict-semantic ambiguity, and generalize across all scales of society and computation.

**Current Maturity:** 8.2/10 (enterprise finance) → **Target:** 9.5/10 (universal decision kernel)

---

## PART A: CRITICAL BUG FIXES (P0 — Execute First)

### A.1 Fix PI Inconsistency (Observed Anomaly: 1.23 vs expected ~1.34)

**Root Cause:** `wealth_pi_efficiency` MCP tool does NOT accept `terminal_value`, while `wealth_npv_reward` does. This creates a parameter asymmetry that caused the PI anomaly in debug mode.

**Fix in `server.py`:**
```python
@mcp.tool(name="wealth_pi_efficiency")
def pi_efficiency(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,  # <-- ADD THIS
) -> Any:
    """Compute Profitability Index (Concentration). [Energy Dimension]"""
    measurement = measurement_pi(initial_investment, cash_flows, discount_rate, terminal_value)
    # ... rest unchanged
```

**Fix in `host/kernel/finance.js` and `src/kernel/finance.js`:**
```javascript
export function calculateProfitabilityIndexMeasurement({
  initial_investment,
  cash_flows,
  discount_rate,
  terminal_value = 0,  // <-- ensure parameter exists and is forwarded
}) { ... }
```

**Add regression test in `tests/finance.test.js`:**
```javascript
test("PI includes terminal_value and reconciles with NPV", () => {
  const initial = 120000;
  const cfs = [30000, 35000, 40000, 45000, 50000];
  const r = 0.1;
  const tv = 20000;

  const npv = calculateNpvMeasurement({
    initial_investment: initial, cash_flows: cfs, discount_rate: r, terminal_value: tv
  });
  const pi = calculateProfitabilityIndexMeasurement({
    initial_investment: initial, cash_flows: cfs, discount_rate: r, terminal_value: tv
  });

  const expectedPi = npv.pv_inflows / Math.abs(initial);
  assert.ok(Math.abs(pi.pi - expectedPi) < 1e-6,
    `PI mismatch: ${pi.pi} vs expected ${expectedPi}`);
});
```

### A.2 Add Internal Consistency Validator

Create `measurement_validate_invariants()` in `server.py` and `validateMeasurementInvariants()` in `finance.js`.

**Checks:**
- `abs(PI - (PV_inflows / abs(initial_investment))) < 0.001`
- `sign(NPV)` must be consistent with `(IRR > discount_rate)` when both are defined and flows are normal
- If `NPV < 0` then `PI < 1` (within tolerance)
- If `NPV > 0` then `PI > 1` (within tolerance)
- If `MIRR` defined, `MIRR` should be between `finance_rate` and max(IRR, reinvestment_rate) logically

If violated, auto-inject flag: `INVARIANT_VIOLATION` → forces `verdict: VOID`.

---

## PART B: VERDICT SEMANTICS REFACTOR (P0)

### B.1 Dual-Verdict Architecture

Current problem: `verdict: SEAL` appears even for negative-NPV projects. This conflates **computation integrity** with **investment approval**.

**Change the envelope schema:**

Replace single `verdict` with:
```json
{
  "engine_status": "VALID | ERROR | WARNING",
  "allocation_signal": "ACCEPT | REJECT | MARGINAL | INSUFFICIENT_DATA",
  "governance_verdict": "SEAL | QUALIFY | 888-HOLD | VOID"
}
```

**Rules for `allocation_signal`:**
- For NPV-based tools:
  - `ACCEPT` if NPV > 0 AND PI > 1 AND no `HOLD_FLAGS`/`INVALID_FLAGS`
  - `REJECT` if NPV < 0 OR PI < 1
  - `MARGINAL` if NPV ≈ 0 (within ±1% of investment) OR `QUALIFY_FLAGS` present
  - `INSUFFICIENT_DATA` if `INVALID_FLAGS` present
- For DSCR:
  - `ACCEPT` if DSCR ≥ 1.5
  - `MARGINAL` if 1.25 ≤ DSCR < 1.5
  - `REJECT` if DSCR < 1.25
- For Payback:
  - `ACCEPT` if recovered AND period < 0.5 * project life
  - `MARGINAL` if recovered but period > 0.5 * project life
  - `REJECT` if `NOT_RECOVERED`

**Update `create_envelope()` in `server.py`:**
```python
def derive_allocation_signal(flags, primary_metric, tool_name):
    if any(f in INVALID_FLAGS for f in flags):
        return "INSUFFICIENT_DATA"
    # ... add per-tool logic
    return "MARGINAL"

def create_envelope(...):
    flags = flags or []
    derived_governance = verdict or derive_verdict(flags)
    derived_allocation = derive_allocation_signal(flags, primary, tool)
    engine_status = "ERROR" if derived_governance == "VOID" else "WARNING" if derived_governance in ("QUALIFY", "888-HOLD") else "VALID"
    return {
        "tool": tool,
        "dimension": dimension,
        "governance_verdict": derived_governance,
        "allocation_signal": derived_allocation,
        "engine_status": engine_status,
        ...
    }
```

**Update JS kernel envelope builders** (`host/kernel/finance.js` or wherever envelopes are built) to match.

---

## PART C: UNIVERSAL RESOURCE ALLOCATION INTELLIGENCE (URAI) REDESIGN

### C.1 Abstract Capital Types

WEALTH currently assumes financial capital. Generalize to **Resource Vector** `R`:

| Capital Class | Symbol | Personal Example | National Example | AI-Agent Example |
|---------------|--------|------------------|------------------|------------------|
| Financial | `$` | Salary, savings | GDP, tax revenue | Compute budget, token cost |
| Temporal | `T` | Free hours, lifespan | Policy window, election cycle | Inference latency, training time |
| Cognitive | `C` | Attention, skill points | Bureaucratic bandwidth | Model capacity, context window |
| Social | `S` | Reputation, network | Legitimacy, trust index | API reputation, user retention |
| Ecological | `E` | Carbon footprint | Water, biodiversity | Energy consumption (kWh) |
| Strategic | `X` | Optionality, degrees of freedom | Diplomatic maneuverability | Model architecture flexibility |
| Thermodynamic | `Φ` | Physical energy, health | Grid stability, fuel reserves | Cooling capacity, power density |

**Implementation:**
Add `capital_type` parameter to all tools (default: `financial` for backward compatibility):
```python
capital_type: str = "financial"  # Enum: ["financial", "temporal", "cognitive", "social", "ecological", "strategic", "thermodynamic"]
```

When `capital_type != "financial"`, replace financial terminology in `assumptions` and `dimension` descriptions with capital-agnostic language:
- "NPV" → "Net Resource Value (NRV)"
- "IRR" → "Internal Resource Return (IRR)"
- "cash_flows" → "resource_streams"
- "initial_investment" → "initial_commitment"

### C.2 Scale-Adaptive Mode Parameter

Add `scale_mode` to all tool requests:
```python
scale_mode: str = "enterprise"  # Enum: ["personal", "household", "sme", "enterprise", "national", "crisis", "civilization", "agentic"]
```

**Scale-specific behaviors:**

| Scale | Discount Rate Default | Time Horizon Default | Objective Function |
|-------|----------------------|----------------------|-------------------|
| personal | 3% (opportunity cost) | 5 years | Maximize lifetime utility |
| household | 4% | 10 years | Intergenerational stability |
| sme | 10% | 3-5 years | Survival + growth |
| enterprise | 10% | 5-10 years | Shareholder value |
| national | 2% (social discount) | 20-50 years | GDP + welfare |
| crisis | ∞ (survival mode) | Immediate | Minimize collapse probability |
| civilization | 0.5% (longtermist) | 100-500 years | Species continuation |
| agentic | 15% (fast obsolescence) | 1-2 years | Capability accumulation |

**Implementation:** Create `get_scale_defaults(scale_mode)` function that adjusts:
- Assumption language
- Confidence band width (civilization = wider, crisis = tighter)
- Thresholds for `allocation_signal` (crisis lowers acceptance bars for liquidity)

### C.3 Human-Agent Interface Additions

**New MCP Tools for Personal/Agentic Scale:**

1. **`wealth_personal_decision`**
   - Inputs: `alternatives` (list of options), `constraints` (budget, time), `values` (weighted priorities)
   - Output: ranked alternatives with NRV per alternative
   - Use case: student choosing major, family choosing school

2. **`wealth_agent_budget`**
   - Inputs: `compute_budget`, `token_budget`, `time_deadline`, `expected_value_of_information`
   - Output: optimal action sequence under resource constraints
   - Use case: AI agent deciding whether to run deep research or quick heuristic

3. **`wealth_crisis_triage`**
   - Inputs: `resources` (inventory), `demands` (urgent needs), `recovery_horizon`
   - Output: survival probability, triage priority list
   - Use case: disaster response, liquidity crisis, system overload

4. **`wealth_civilization_stewardship`**
   - Inputs: `population`, `energy_budget`, `carbon_budget`, `tech_growth_rate`, `time_horizon_years`
   - Output: sustainable growth path, collapse risk curve
   - Use case: long-term planning, climate policy, space colonization economics

### C.4 Multi-Agent Coordination Layer

Add **`wealth_coordination_equilibrium`** tool:
- Inputs: `agents` (list of agent resource vectors and objectives), `shared_resources` (scarce commons), `mechanism` ("cooperative" | "competitive" | "mixed")
- Output: Nash/correlated equilibrium approximation, tragedy-of-commons risk score, cooperative surplus
- Use case: multiple AI agents sharing GPU cluster; multiple nations sharing water basin

---

## PART D: RISK ENGINE UPGRADE

### D.1 Monte Carlo Module

Add `wealth_monte_carlo_forecast` tool:
```python
def monte_carlo_forecast(
    initial_commitment: float,
    mean_cash_flows: List[float],
    volatilities: List[float],
    correlation_matrix: Optional[List[List[float]]] = None,
    discount_rate: float = 0.1,
    simulations: int = 10000,
    distributions: str = "lognormal"  # "normal" | "lognormal" | "triangular"
) -> Any:
```
Output:
- `probability_positive_nrv`
- `expected_shortfall_5pct`
- `upside_potential_95pct`
- `volatility_of_outcome`

### D.2 Regime Shift Modeling

Add `regime_probabilities` parameter to NPV/PI tools:
```python
regime_probabilities: Optional[Dict[str, float]] = None
# e.g. {"baseline": 0.6, "recession": 0.3, "boom": 0.1}
```
Each regime provides alternate `cash_flows` and `discount_rate`. Compute **scenario-weighted expected NRV** and **regime-switch risk**.

---

## PART E: IMPLEMENTATION CHECKLIST FOR AGENTS

### Step 1: Fix PI (server.py, finance.js, tests)
- [ ] Add `terminal_value` to `pi_efficiency`
- [ ] Add `terminal_value` to JS `calculateProfitabilityIndexMeasurement`
- [ ] Write regression test and run `npm test` and Python parity test

### Step 2: Invariant Validator
- [ ] Implement `measurement_validate_invariants()` in Python
- [ ] Implement `validateMeasurementInvariants()` in JS
- [ ] Wire into all envelope creators before `derive_verdict()`

### Step 3: Dual Verdict Refactor
- [ ] Replace single `verdict` with `governance_verdict` + `allocation_signal` + `engine_status`
- [ ] Implement `derive_allocation_signal()` per tool type
- [ ] Update all tests to assert on `allocation_signal`
- [ ] Update MCP schema (`api/schemas/wealth-mcp-tools.json`)

### Step 4: Universal Capital Abstraction
- [ ] Add `capital_type` and `scale_mode` parameters to all tools
- [ ] Create `get_scale_defaults()` and `get_capital_terminology()` helpers
- [ ] Update assumptions/dimension labels dynamically

### Step 5: New Tools
- [ ] Implement `wealth_personal_decision`
- [ ] Implement `wealth_agent_budget`
- [ ] Implement `wealth_crisis_triage`
- [ ] Implement `wealth_civilization_stewardship`
- [ ] Implement `wealth_coordination_equilibrium`
- [ ] Implement `wealth_monte_carlo_forecast`

### Step 6: Documentation & Schema
- [ ] Update `wealth-mcp-tools.json` schema
- [ ] Update `README.md` with URAI v2 vision
- [ ] Add `URAI_ARCHITECTURE.md` to `docs/`

---

## PART F: ACCEPTANCE CRITERIA

The fix is complete when:
1. `npm test` passes with new regression tests
2. Python server parity test passes (`tests/finance.test.js` Python section)
3. Calling `wealth_pi_efficiency` with `terminal_value=20000` returns PI ≈ 1.337 (matching NPV tool)
4. Negative NPV projects return `allocation_signal: REJECT` (not just `SEAL`)
5. All tools accept `scale_mode` and `capital_type` without error
6. New personal/agentic/crisis/civilization tools execute and return valid envelopes
7. `INVARIANT_VIOLATION` is impossible to trigger under normal operation

---

## CLOSING

This specification transforms WEALTH from a finance calculator into a cross-scale decision intelligence kernel. It fixes the observed PI bug, eliminates semantic ambiguity, and opens the system to all forms of capital and all scales of agency.

**Deliver to engineering agents.**
**No further questions.**
**Execute.**
