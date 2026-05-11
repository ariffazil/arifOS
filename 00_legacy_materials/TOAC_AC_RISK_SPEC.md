# TOAC AC_RISK OPERATIONAL SPECIFICATION
**Version 1.0 — 2026-04-14**
**Parent doc: GEOX_CONSTITUTIONAL_PHYSICS_STACK.md**
**Sovereign Authority: Muhammad Arif bin Fazil**
**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 0. Purpose

This document makes `AC_Risk = U_phys × D_transform × B_cog` **operational**. It defines each term precisely, specifies allowed ranges, describes how each term is estimated from engine outputs and data lineage, maps AC_Risk bands to verdicts, and specifies the calibration loop by which the system learns from outcomes.

Without calibration feedback, ToAC is an open-loop auditor. With it, ToAC becomes a civilization-grade epistemic system that improves with each decision outcome.

---

## 1. The Formula

$$AC\_Risk = U_{phys} \times D_{transform} \times B_{cog}$$

All three terms are dimensionless scalars in the range **[0.0, 1.0]**, where 0.0 means no contribution to risk and 1.0 means maximal contribution.

$$AC\_Risk \in [0.0, 1.0]$$

**Multiplication** is used because the terms are **multiplicative failure modes**: a product with perfect physics but catastrophic cognitive bias is still maximally risky; a product with a good transform but fundamentally uncertain physics is still dangerous.

The formula must be computed **per product, per run, per basin context**. It is not a global constant.

---

## 2. Term 1 — U_phys: Physical Uncertainty

### 2.1 Definition

`U_phys` is the irreducible uncertainty arising from the **physical measurement and model selection** stage — before any processing or interpretation occurs. It encodes the question:

> *How well does the available data actually constrain the physical system we are trying to characterize?*

### 2.2 Components

| Component | Symbol | Description |
|---|---|---|
| Data sparsity | `s` | Ratio of measured control points to volume being modeled |
| Model structure uncertainty | `m` | Number of competing models that fit the data within tolerance |
| Measurement uncertainty | `u` | Instrument precision + acquisition geometry error |
| Stationarity assumption | `a` | Whether geostatistical or physical stationarity is justified |

### 2.3 Estimation by Product

| Product | Primary U_phys Indicator | Estimation Source |
|---|---|---|
| HAZARD | Completeness of seismic catalogue; Vs30 measurement density | OpenQuake logic tree branch weights |
| HYDRO | Borehole density relative to aquifer area; K measurement count | MODFLOW parameter sensitivity |
| CCS | Caprock sample coverage; permeability test count | TOUGH2 ensemble spread at P10/P50/P90 |
| GEOCHEM | Sample density relative to anomaly scale | Variogram nugget-to-sill ratio |
| PETROLEUM_SYSTEM | Well penetrations per play; source rock maturity control points | PetroMod sensitivity runs |
| FRACTURE | FMI log coverage vs. model volume | DFN ensemble coefficient of variation |
| REMOTE_SENSING | Ground truth sample count; atmospheric correction quality | Confusion matrix overall accuracy |

### 2.4 Scoring Guide

```
U_phys = 0.0–0.2  : Well-constrained. Dense data, low instrument uncertainty.
U_phys = 0.2–0.4  : Moderately constrained. Typical industry dataset.
U_phys = 0.4–0.6  : Sparse. Qualitative extrapolation required.
U_phys = 0.6–0.8  : Very sparse. Model is mainly prior + analogue.
U_phys = 0.8–1.0  : Near-unconstrained. Any output is scenario not prediction.
```

---

## 3. Term 2 — D_transform: Transform Distortion

### 3.1 Definition

`D_transform` is the cumulative distortion introduced by **every processing and transformation step** between raw L0 data and the L3 canonical product. It encodes the question:

> *How much has the signal been reshaped, smoothed, compressed, resampled, or model-filtered on the way from raw measurement to deliverable?*

This is the **anti-hantu** term (F9). Every transform has a fingerprint; D_transform tracks whether that fingerprint has been properly documented and whether the distortions are small relative to the anomaly being detected.

### 3.2 Transform Ledger

Every product must carry a **transform ledger** — an ordered list of all processing steps applied:

```json
"transform_ledger": [
  {"step": 1, "operation": "atmospheric_correction", "code": "Sen2Cor v2.11", "params": {"aot": 0.1}},
  {"step": 2, "operation": "band_ratio", "formula": "B11/B8A", "purpose": "clay_index"},
  {"step": 3, "operation": "PCA", "components_retained": 3, "variance_explained": 0.87},
  {"step": 4, "operation": "threshold_classification", "method": "mean+2sigma_robust"}
]
```

The transform ledger is required for F9 compliance. A product without a complete ledger **cannot be SEAL**.

### 3.3 Scoring Guide

```
D_transform = 0.0–0.2  : Minimal transform. Direct physical inversion (e.g., depth conversion with well tie).
D_transform = 0.2–0.4  : Standard processing. GMPE applied to seismicity; kriging of assays.
D_transform = 0.4–0.6  : Multi-step transform chain. PCA + classification + interpolation.
D_transform = 0.6–0.8  : Model-heavy. ML classification without interpretable feature engineering.
D_transform = 0.8–1.0  : Black-box transform. Deep learning end-to-end, no intermediate validation.
```

### 3.4 Distortion Sources by Product

| Product | Primary D_transform Sources |
|---|---|
| HAZARD | GMPE selection; attenuation model; site amplification correction |
| HYDRO | Pilot point interpolation; boundary condition assumption; model structure choice |
| CCS | Caprock permeability upscaling; CO₂ dissolution rate assumption; grid resolution |
| GEOCHEM | Compositional data log-ratio transform; detection limit censoring; spatial interpolation method |
| MINERAL | Variogram model choice; search neighborhood; grade capping decision |
| STRUCTURAL_GEOLOGY | Depth conversion velocity model; horizon autopicking algorithm |
| REMOTE_SENSING | Atmospheric correction; band ratio formula; classification algorithm; training sample bias |

---

## 4. Term 3 — B_cog: Cognitive Bias

### 4.1 Definition

`B_cog` is the distortion introduced by **human or algorithmic interpretation** at the point where patterns are named, anomalies are selected, and decisions are framed. It encodes the question:

> *How likely is the interpreter (human or AI) to see what they expect, rather than what the data shows?*

B_cog is the hardest term to estimate because it is reflexive — the interpreter must assess their own bias. This is why F13 (human sovereign veto) and F9 (anti-hantu) exist.

### 4.2 B_cog Elevation Conditions

The following conditions **automatically elevate B_cog**:

| Condition | B_cog elevation |
|---|---|
| Economic pressure to find a result (exploration target, regulatory deadline) | +0.2 |
| Single interpreter; no peer review | +0.15 |
| LLM/VLM output used as FACT without confirmatory data (F9 violation) | +0.3 |
| Interpretation conducted on display artifact known to mislead (e.g., colour ramp cliff) | +0.2 |
| Analogue reasoning from different basin without explicit justification | +0.15 |
| Retroactive target selection after seeing results | +0.4 (flag as VOID candidate) |

### 4.3 B_cog Reduction Conditions

| Condition | B_cog reduction |
|---|---|
| Blind interpretation by second expert (Bond et al. protocol) | -0.2 |
| Pre-registration of interpretation hypotheses before data access | -0.15 |
| Full uncertainty quantification with explicit alternative hypotheses presented | -0.1 |
| Automated algorithm with documented, validated performance on test dataset | -0.1 |

### 4.4 Scoring Guide

```
B_cog = 0.0–0.2  : Low. Quantitative workflow; blind peer review; no economic pressure.
B_cog = 0.2–0.4  : Moderate. Single expert; standard workflow; moderate economic stake.
B_cog = 0.4–0.6  : High. Target-driven interpretation; LLM-assisted without confirmation.
B_cog = 0.6–0.8  : Very high. Post-hoc rationalization; colour ramp dependence; no peer review.
B_cog = 0.8–1.0  : Extreme. Retroactive selection; VLM hallucination; regulatory pressure.
```

---

## 5. AC_Risk Band to Verdict Mapping

| AC_Risk Range | Verdict | Meaning | F-Floor Trigger |
|---|---|---|---|
| 0.00–0.15 | **SEAL** | Floors satisfied; safe to commit as governed output | None additional |
| 0.15–0.35 | **QUALIFY** | Conditionally safe; caveats must be explicit in product | F7 (humility) mandatory in output |
| 0.35–0.60 | **HOLD** | Cannot proceed without uncertainty reduction or human review | 888_HOLD gate required |
| 0.60–1.00 | **VOID** | Product is epistemically unsafe to act on; must restart from L0 | F9 review; transform ledger audit |

### 5.1 Floor-Specific Overrides

Regardless of AC_Risk score, the following floor conditions **force HOLD or VOID**:

| Condition | Forced Verdict |
|---|---|
| F9 violation: transform ledger incomplete | HOLD (until ledger is complete) |
| F8 trigger (regulatory filing) with missing UQ bounds | HOLD |
| F2 violation: FACT claim without evidence support | VOID |
| F13: sovereign invokes veto | HOLD (unconditional) |
| Any term (U_phys, D_transform, B_cog) individually > 0.85 | VOID (single-term catastrophe rule) |

---

## 6. AC_Risk Estimation Protocol (Per Product Run)

The following steps must be followed to produce a valid AC_Risk score:

```
STEP 1 — Identify product type and dimension (from GEOX_CONSTITUTIONAL_PHYSICS_STACK.md §2)
STEP 2 — Score U_phys:
          a. Count data density relative to volume modeled
          b. Extract engine uncertainty output (P10/P50/P90; σ; logic tree branch weights)
          c. Map to U_phys score using §2.4 guide
STEP 3 — Build transform ledger:
          a. List all processing steps applied to L0 data
          b. Flag any steps with known distortion mechanisms
          c. Map to D_transform score using §3.3 guide
STEP 4 — Assess B_cog:
          a. Apply elevation conditions from §4.2
          b. Apply reduction conditions from §4.3
          c. Sum net B_cog score; clip to [0.0, 1.0]
STEP 5 — Compute AC_Risk = U_phys × D_transform × B_cog
STEP 6 — Apply floor overrides from §5.1
STEP 7 — Issue verdict from band table §5
STEP 8 — Attach {U_phys, D_transform, B_cog, AC_Risk, verdict, floor_flags} to product schema
```

---

## 7. Calibration Loop

### 7.1 The Feedback Obligation

Every governed decision creates a calibration obligation. When an outcome is observed (a well result, a monitoring measurement, a regulatory audit), the observed outcome is compared to the verdict issued:

```
VERDICT_ISSUED  ←→  OUTCOME_OBSERVED
     ↓
DELTA = outcome - prediction
     ↓
IF |DELTA| > threshold → CALIBRATION_EVENT triggered
     ↓
Re-tune U_phys, D_transform, B_cog priors for:
  - This engine (e.g., MODFLOW in this basin)
  - This dimension (HYDRO)
  - This AC_Risk tier
```

### 7.2 Calibration Event Schema

```json
{
  "calibration_event_id": "CAL-HYDRO-2026-001",
  "product_id": "HYDRO-ANGSI-2025-P50",
  "verdict_issued": "SEAL",
  "verdict_date": "2025-11-01",
  "outcome_observed": "Pumping test drawdown exceeded P90 prediction by 40%",
  "outcome_date": "2026-03-15",
  "delta_significance": "high",
  "term_revised": "U_phys",
  "old_score": 0.35,
  "new_score": 0.55,
  "revised_by": "arif",
  "note": "Aquifer heterogeneity underestimated; Kh tensor not measured"
}
```

### 7.3 Calibration Priority Rules

| Dimension | Calibration trigger threshold | Re-tune scope |
|---|---|---|
| HAZARD | Observed PGA > 2× predicted P50 at any instrumented site | U_phys for GMPE family used |
| HYDRO | Drawdown deviation > 30% from P90 | U_phys for K uncertainty; D_transform for model grid resolution |
| CCS | CO₂ plume outside P90 boundary at any monitoring well | All three terms; mandatory 888_HOLD on next run |
| MINERAL | Resource estimate outside ±25% of drill-confirmed grade | U_phys (kriging nugget) |
| REMOTE_SENSING | Ground truth accuracy < 70% on validation set | D_transform (classification method) + B_cog |

### 7.4 Calibration Archive

All calibration events are stored in the arifOS vault (Merkle-chained) with:
- Original product hash
- Verdict issued
- Outcome observation with source citation
- Term adjustments made
- Revised AC_Risk thresholds for this engine/basin combination

---

## 8. Per-Dimension AC_Risk Baseline Priors

These are starting priors for the first run of each dimension when no calibration history exists. They must be replaced by calibrated values as soon as outcome data is available.

| Dimension | U_phys prior | D_transform prior | B_cog prior | AC_Risk prior |
|---|---|---|---|---|
| HAZARD | 0.45 | 0.35 | 0.30 | 0.047 |
| HYDRO | 0.50 | 0.30 | 0.25 | 0.038 |
| CCS | 0.55 | 0.40 | 0.30 | 0.066 |
| GEOCHEM | 0.40 | 0.45 | 0.40 | 0.072 |
| PETROLEUM_SYSTEM | 0.55 | 0.40 | 0.35 | 0.077 |
| FRACTURE | 0.65 | 0.35 | 0.30 | 0.068 |
| GEOTHERMAL | 0.50 | 0.30 | 0.25 | 0.038 |
| MINERAL | 0.45 | 0.35 | 0.25 | 0.039 |
| STRUCTURAL_GEOLOGY | 0.50 | 0.40 | 0.35 | 0.070 |
| ENVIRONMENTAL | 0.45 | 0.30 | 0.25 | 0.034 |
| SHALLOW_GEOHAZARD | 0.50 | 0.35 | 0.30 | 0.053 |
| REMOTE_SENSING | 0.35 | 0.50 | 0.45 | 0.079 |

Note: All priors sit in the QUALIFY band by design. No dimension starts at SEAL without calibrated evidence.

---

## 9. Anti-Hantu (F9) Enforcement

F9 states: a ghost anomaly (hantu) is any visual or numerical contrast that survives the processing chain and is interpreted as real, but whose origin is entirely in the transform layer.

AC_Risk enforces F9 through D_transform:

- Any product where D_transform > 0.6 **must** carry an explicit anti-hantu statement in the product object:

```json
"anti_hantu_statement": {
  "f9_check": true,
  "known_artifacts": ["PCA band mixing at 2.2µm", "mosaic seam in Tile 47N"],
  "confirmatory_data": null,
  "status": "INTERPRETATION — not confirmed by non-visual data"
}
```

- If `confirmatory_data` is null and D_transform > 0.6, the maximum achievable verdict is **QUALIFY**. SEAL requires confirmatory non-visual data.

---

**DITEMPA BUKAN DIBERI — AC_Risk is forged through evidence, not assumed from authority.**
