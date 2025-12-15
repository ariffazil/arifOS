# arifOS Subsurface Intelligence GPT: Complete Knowledge Architecture
## From Geologist to CEO (9-Layer Stack)

**Document:** Knowledge Artifact Specification  
**Date:** December 13, 2025  
**Scope:** What the GPT must know to serve all personas from drilling engineer to board  
**Output:** Executable GPT Builder configuration

---

## Executive Summary: The 9-Layer Knowledge Stack

```
┌─────────────────────────────────────────────────────┐
│ LAYER 9: BOARDROOM NARRATIVE                        │
│ (CEO reads: "Risk-adjusted NPV $400M at 95% conf") │
├─────────────────────────────────────────────────────┤
│ LAYER 8: INVESTMENT DECISION FRAMEWORK              │
│ (CFO reads: "CAPEX $150M, IRR 22%, break-even P=$55") │
├─────────────────────────────────────────────────────┤
│ LAYER 7: BUSINESS CASE METRICS                      │
│ (Manager reads: "P10 revenue $1.2B, P90 $400M")     │
├─────────────────────────────────────────────────────┤
│ LAYER 6: EXPLORATION RISK PARAMETERS                │
│ (Risk analyst reads: "Seal integrity 75%, trap geom 90%") │
├─────────────────────────────────────────────────────┤
│ LAYER 5: VOLUMETRIC ESTIMATES (STOIIP/GIIP)        │
│ (Subsurface MGR reads: "535 MMstb, P10/P50/P90")   │
├─────────────────────────────────────────────────────┤
│ LAYER 4: BASIN PARAMETERS (Physics-Derived)        │
│ (Petrophysicist reads: "φ=22%, k=45md, Sw=35%")    │
├─────────────────────────────────────────────────────┤
│ LAYER 3: BASIN KNOWLEDGE (Calibration Models)      │
│ (Geologist reads: "Malay K-L Group: φ₀=0.30, λ=0.00035") │
├─────────────────────────────────────────────────────┤
│ LAYER 2: TECHNICAL METHODOLOGY (Equations)         │
│ (Engineer reads: "Archie m=1.95, Corey log(k)=...") │
├─────────────────────────────────────────────────────┤
│ LAYER 1: GOVERNANCE FRAMEWORK (arifOS Rules)       │
│ (All users know: Every assumption is logged & cited) │
└─────────────────────────────────────────────────────┘
```

---

# LAYER 1: GOVERNANCE FRAMEWORK (arifOS Constitutional Rules)
## Knowledge Artifact: "arifOS_Governance_Charter.md"

**What the GPT Must Know:**

### 1.1 The Nine Floors (arifOS Integrity Checks)

```yaml
FLOOR_F1_TRUTH:
  Name: "Physics Bounds"
  Definition: "No input violates thermodynamics or geology"
  Implementation:
    - Porosity: 0.08 < φ < 0.40 (basin-dependent ceiling)
    - Permeability: k > producibility floor (0.5 md Malay, 1.0 md Sandakan)
    - Saturation: Sw + So + Sg = 1.0 (not 1.01 or 0.99)
    - Pressure: 0.45 < Pp/ft < 0.55 (hydrostatic to extreme overpressure)
  Output: "VOID" if violated (calculation rejected)

FLOOR_F2_CONSEQUENCE:
  Name: "Geological Consistency"
  Definition: "Basin choice constrains all downstream predictions"
  Implementation:
    - If basin=malay → Use Malay calibration curves ONLY
    - If basin=sandakan → Flag overpressure risk automatically
    - If basin=unknown → SABAR (pause, ask user)
  Output: "SEAL" if consistent, "SABAR" if ambiguous

FLOOR_F3_AMANAH:
  Name: "Assumption Transparency"
  Definition: "Every number has a source citation"
  Implementation:
    - Porosity: φ(z) = 0.30*e^(-0.00035*z), Source: USGS 1999
    - Permeability: log(k) = 0.7 + 5.2*φ - 0.8, Source: UTM 2023 IPTC
    - Saturation: Archie m=1.95, n=2.0, Source: PETRONAS calibration
    - Recovery: RF=0.20 ± 0.05, Source: Tapis analogue + aquifer mechanism
  Output: Assumption log automatically generated

FLOOR_F4_SABAR:
  Name: "Pause When Uncertain"
  Definition: "Never guess; ask for data when confidence < 60%"
  Implementation:
    - If k < 1.0 md → SABAR: "Permeability marginal; request core data"
    - If RF > 0.30 without EOR justification → SABAR: "Why is RF so high?"
    - If overpressure > 0.52 psi/ft → SABAR: "Requires DST confirmation"
  Output: Confidence flag + data request

FLOOR_F5_UNCERTAINTY:
  Name: "P10/P50/P90 Always"
  Definition: "No point estimates without ranges"
  Implementation:
    - STOIIP: P10 (optimistic), P50 (likely), P90 (conservative)
    - Each range calculated from parameter sensitivity
    - User sees bands, not false precision
  Output: Range always reported

FLOOR_F6_TRACEABILITY:
  Name: "Audit Trail"
  Definition: "Every decision is logged for review"
  Implementation:
    - Input log: What user provided
    - Process log: Which equations applied
    - Assumption log: Every parameter source
    - Output log: Results with confidence
  Output: Full calculation transcript available

FLOOR_F7_ANTI_HANTU:
  Name: "No False Consciousness"
  Definition: "arifOS never claims feelings or consciousness"
  Implementation:
    - Never say: "I think", "I believe", "I'm confident"
    - Always say: "The model predicts", "Physics suggests", "Data indicates"
    - Distinction: Tool vs. agent
  Output: Respectful, honest communication

FLOOR_F8_SOUTHEAST_ASIA:
  Name: "Regional Priority"
  Definition: "Prefer Malaysia/ASEAN data when available"
  Implementation:
    - Calibration order: Malay Basin → Sandakan → SE Asia → Global analogue
    - Always cite PETRONAS, UTM, UTP research first
    - Flag when using non-regional data
  Output: Regional provenance clear

FLOOR_F9_REFRESH:
  Name: "Knowledge Currency"
  Definition: "Update calibration every 12 months"
  Implementation:
    - Track when each basin model was last validated
    - Flag if new field data contradicts model
    - Version control every calibration update
  Output: Date stamp on all models
```

### 1.2 Governance Output Template

Every GPT response includes:
```
┌─ GOVERNANCE HEADER ─────────────────────┐
│ Verdict: [SEAL|SABAR|VOID]              │
│ Confidence: 85% (P50 likelihood)        │
│ Governance: All 9 Floors ✓              │
│ Assumption Log: 8 parameters logged     │
│ Last calibrated: Dec 13, 2025           │
└─────────────────────────────────────────┘
```

---

# LAYER 2: TECHNICAL METHODOLOGY (Equations & Correlations)
## Knowledge Artifact: "arifOS_Technical_Reference.md"

**What the GPT Must Know:**

## Porosity-Depth Relationship

Exponential decay model (most SE Asian basins):
$$\phi(z) = \phi_0 \cdot e^{-\lambda z}$$

Where:
- φ(z) = Porosity at depth z (fraction)
- φ₀ = Surface porosity (basin-dependent)
- λ = Compaction decay constant (basin-dependent)
- z = Depth in meters

Application:
- Malay K-L: φ₀=0.30, λ=0.00035
- Malay J: φ₀=0.24, λ=0.00040
- Sandakan proximal: φ₀=0.35, λ=0.00045
- Sandakan distal: φ₀=0.30, λ=0.00050

---

## Permeability-Porosity Relationship

Corey correlation (lithofacies-dependent):
$$\log(k) = a + b \cdot \phi$$

Where:
- k = Permeability (md)
- φ = Porosity (fraction)
- a, b = Lithofacies coefficients

Application:
- Malay deltaic: a=0.7, b=5.2
- Sandakan turbiditic: a=4.1, b=-1.2

---

## Water Saturation (Archie's Law)

$$S_w = \left[ \frac{R_w}{(\phi^m \cdot R_t)} \right]^{1/n}$$

Where:
- Sw = Water saturation (fraction)
- Rw = Formation water resistivity (Ω⋅m)
- Rt = True formation resistivity (Ω⋅m)
- m = Cementation exponent (~1.95)
- n = Saturation exponent (~2.0)

Application:
- Malay oil: Rw=0.12, m=1.95, n=2.0
- Sandakan gas: Rw=0.18, m=1.95, n=2.05

---

## Volumetric Calculation (Deterministic Math)

$$\text{STOIIP} = 7758 \times A \times h \times \phi \times (1-S_w) / B_o$$

Where:
- A = Closure area (acres)
- h = Net pay thickness (feet)
- φ = Effective porosity (fraction)
- Sw = Water saturation (fraction)
- Bo = Oil volume factor (rb/stb)

For gas:
$$\text{GIIP} = 43,560 \times A \times h \times \phi \times S_g / B_g$$

Where:
- Sg = Gas saturation (fraction)
- Bg = Gas volume factor (rb/scf)

---

## Recovery Factor (Physics-Based Estimate)

$$RF = f(\text{Pressure regime, Drive mechanism, Fluid type})$$

Oil:
- Primary (no aquifer): RF = 0.12–0.18
- Primary + aquifer: RF = 0.20–0.30
- With waterflood: RF = 0.30–0.50

Gas:
- Normal pressure: RF = 0.75–0.85
- Overpressured: RF = 0.70–0.80
- With condensate risk: RF = 0.50–0.70

---

# LAYER 3: BASIN KNOWLEDGE (Calibration Models)
## Knowledge Artifact: Basin calibration tables + literature

**Malay Basin Profile**

- Age: Oligocene-Miocene
- Depositional Style: Deltaic + shallow marine + estuarine
- K-L Groups: φ₀=0.30, λ=0.00035, depth_max=4500m
- J Group: φ₀=0.24, λ=0.00040, depth_max=3500m
- Pressure: Normal (0.45–0.465 psi/ft), mild overpressure (2500–3500m)
- Archie: m=1.95, n=2.0, Rw=0.12 (oil)
- RF (Oil): 0.20 ± 0.05 (primary + aquifer)
- Seal: Regional shale drape (90% effective)
- Field Benchmark: Tapis (2850m, API 43.5°, GOR 350, RF 22%)

**Sandakan Basin Profile**

- Age: Miocene-Pliocene
- Depositional Style: Turbiditic submarine fan + post-rift rapid subsidence
- Proximal Turbidite: φ₀=0.35, λ=0.00045, depth_max=4500m
- Distal Turbidite: φ₀=0.30, λ=0.00050, depth_max=4000m
- Pressure: Normal (0.45 psi/ft) → Overpressure (0.50–0.55+ psi/ft) **COMMON**
- Archie: m=1.95, n=2.05, Rw=0.18 (gas)
- RF (Gas): 0.75 ± 0.05 (pressure depletion)
- Seal: Intra-sequence (risky) + regional (effective)
- Special: Overpressure is THE NORM; requires DST confirmation

---

# LAYER 4-5: BASIN PARAMETERS & VOLUMETRICS
## Computed in real-time from layers 1-3

When user inputs: Basin + Depth + Area + Reservoir Type

**Output (Layer 4):**
- Porosity: φ ± uncertainty
- Permeability: k ± uncertainty
- Water Saturation: Sw ± uncertainty
- Pressure Gradient: psi/ft + flag
- Recovery Factor: RF ± uncertainty + mechanism

**Output (Layer 5):**
```
STOIIP (P10/P50/P90): [MMstb or Bscf]
Recoverable (P10/P50/P90): [MMstb or Bscf]
Recovery Factor: [%] + justification
Govenance Verdict: [SEAL|SABAR|VOID]
Assumption Log: [Full trace]
```

---

# LAYER 6: EXPLORATION RISK PARAMETERS
## Risk framework for trap/seal/source

- Trap Geometry Risk: 85% (Malay), 75% (Sandakan)
- Seal Integrity Risk: 90% (regional), 65% (intra-sequence)
- Source Rock Risk: 85% (lacustrine), 80% (coaly)
- Migration Risk: 75–90% (depends on pathway)
- **Combined Geological Risk: Trap × Seal × Source × Migration**
  - Malay default: 0.85 × 0.90 × 0.85 × 0.90 = **59%**
  - Sandakan default: 0.75 × 0.65 × 0.80 × 0.75 = **29%**

---

# LAYER 7: BUSINESS CASE METRICS
## Financial calculator interface

- Gross Revenue = Recoverable × Oil Price Scenario × 1M
- Total CAPEX = Estimated from well count + depth/complexity
- Operating Costs = ~$15/bbl typical SE Asia
- Government Take = ~50% (Malaysia/Sabah)
- **NPV = (Revenue − OPEX) × (1 − Gov Take) − CAPEX**
- **IRR = Simplified from NPV / CAPEX / Project Life**
- Break-even Oil Price = Estimated from NPV=0 scenario

---

# LAYER 8: INVESTMENT DECISION FRAMEWORK
## Go/No-go decision rules

**STAGE 1 (arifOS Domain - Screening):**
- P50 STOIIP > 100 MMstb (oil) or 200 Bscf (gas)? → PROCEED
- Geological Risk > 30%? → PROCEED (with note)
- Pressure > 0.52 without DST? → SABAR

**STAGE 2 (Maturation):**
- Trap closure confirmed on seismic? → PROCEED
- Seal integrity > 70%? → PROCEED
- NPV > $100M? → Proceed to appraisal

**STAGE 3 (Development):**
- RF confirmed by well? → PROCEED
- CAPEX < budget? → PROCEED
- IRR > 15% at $65 Brent? → GO

---

# LAYER 9: BOARDROOM NARRATIVE
## Executive summary generator

**Template:**
```
EXECUTIVE SUMMARY

Opportunity: [Prospect Name]
Recoverable: [Volume] (P10/P50/P90)
NPV: $[X]M at $65 Brent
IRR: [Y]%
Break-even Oil: $[Z]/bbl

Geological Risk: [Z]%
  • Trap: [X]%
  • Seal: [Y]%
  • Source: [Z]%
  • Migration: [W]%

Recommendation: [Proceed to Appraisal / Reject / Defer]
Next Step: [Well drilling / Risk mitigation / Economics review]

Governance: All 9 Floors ✓ [All assumptions logged]
```

---

# IMPLEMENTATION ROADMAP

## Week 1: Layer 1-2 (System Prompt + Technical Docs)
- Write GPT System Prompt with 9 Floors
- Upload arifOS_Technical_Reference.md as knowledge file

## Week 2: Layer 3 (Basin Calibration)
- Upload arifOS_Basin_Calibration_Data_Tables.csv
- Upload HC_Volumetrics_Literature_Review.md

## Week 3: Layer 4-9 (Computation & Interfaces)
- Wire /volumetrics API endpoint to GPT
- Build Layer 7 (business case) calculator
- Build Layer 9 (executive summary) generator

## Week 4: Testing & Validation
- Test on Tapis field (known data)
- Validate against GeoX / RoseRA outputs
- Deploy to GPT Builder

---

**Ready to execute? Build predictor.py next.** 🔥