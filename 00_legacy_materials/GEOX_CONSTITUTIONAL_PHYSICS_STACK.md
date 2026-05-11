# GEOX CONSTITUTIONAL PHYSICS STACK
**Frozen Contract — Version 1.0 — 2026-04-14**
**Sovereign Authority: Muhammad Arif bin Fazil**
**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 0. Purpose and Status

This document is the **foundational frozen contract** for the GEOX Civilization Engine. It defines the six-layer stack through which all 12 canonical GEOX products must pass before any governed decision can be issued. All other specs (`TOAC_AC_RISK_SPEC.md`, `GEOX_PRODUCT_VERSIONING.md`, `PHYSICS_ADAPTER_SPEC.md`, `GEOX_INTERPRODUCT_RISK_RULES.md`) are children of this document and must not contradict it.

**This document does not describe what to compute. It describes what is real, what is safe to trust, and who is responsible.**

Amendment requires sovereign sign-off (888_HOLD + F13 veto).

---

## 1. The Six-Layer Constitutional Stack

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│  L5 — HUMAN SOVEREIGNTY                                                            │
│  Actor: Muhammad Arif bin Fazil (F13 sovereign authority)                          │
│  Instruments: Natural language decisions, policy mandates, 888_HOLD invocations    │
│  Obligation: All F8-flagged products (HAZARD/HYDRO/CCS) require explicit L5 sign  │
│  Role: The only layer that can convert HOLD → SEAL or invoke VOID override        │
├────────────────────────────────────────────────────────────────────────────────────┤
│  L4 — GOVERNANCE / EPISTEMOLOGY  [ToAC + Naming as Creation]                      │
│  Instruments: AC_Risk formula, SEAL/QUALIFY/HOLD/VOID verdicts, F1–F13 floors     │
│  Equation: AC_Risk = U_phys × D_transform × B_cog                                 │
│  Naming: Each dimension (HAZARD, HYDRO, CCS, …) is a constitutional act with      │
│          assigned floors, 888_HOLD gates, and inter-product inheritance rules      │
│  Anti-Hantu: F9 requires full transform provenance on every product                │
│  Role: Audits whether physics-math output is epistemically safe to act on         │
├────────────────────────────────────────────────────────────────────────────────────┤
│  L3 — CANONICAL GEOX PRODUCT                                                       │
│  Instruments: Typed product objects with versioning, UQ bounds, provenance hash   │
│  Schema: {product_id, version, engine, inputs_hash, UQ_summary,                   │
│           ac_risk, verdict, floor_flags, issued_by, timestamp}                     │
│  Requirement: Every product carries P10/P50/P90 or full distribution              │
│  Role: The governed output — the artifact that can be filed, audited, replayed    │
├────────────────────────────────────────────────────────────────────────────────────┤
│  L2 — MATH / FORMAL LANGUAGE  [Governing Equations]                                │
│  Instruments: PDEs, GMPEs, Darcy flow, Mohr-Coulomb, Ghijben-Herzberg,           │
│               CO₂ EOS equations, Arrhenius kinetics, mass balance equations      │
│  Principle: Equations encode physical regularity in minimal symbols               │
│  Units discipline: Every quantity carries SI units and regime-of-validity flags   │
│  Role: Compression layer — bridges raw data and physics engine outputs            │
├────────────────────────────────────────────────────────────────────────────────────┤
│  L1 — PHYSICS ENGINE  [Existing Open-Source / Industry Codes]                     │
│  Instruments: OpenQuake, MODFLOW, TOUGH2/TOUGH+, GeoMechanica, Leapfrog,         │
│               FEFLOW, Eclipse/OPM, OpendTect, Petrel (read-only)                  │
│  Adapter contract: Engine outputs must include uncertainty estimates (P10/P50/P90)│
│  or full Monte Carlo distributions; point estimates alone are HOLD-flagged        │
│  Role: Math executed against real measured data and boundary conditions           │
├────────────────────────────────────────────────────────────────────────────────────┤
│  L0 — RAW EARTH SIGNAL  [The World]                                                │
│  Instruments: Seismic waveforms, borehole logs (LAS/WITSML), geochemical samples, │
│               InSAR, Landsat/Sentinel, ALOS PALSAR, SRTM DEM, gravimetry, MT     │
│  Law: No layer above L0 can manufacture, infer, or substitute this data           │
│  Provenance: Every L0 input must carry {source, acquisition_date, CRS, QC_flag}  │
│  Role: Ground truth — irreducibly physical                                         │
└────────────────────────────────────────────────────────────────────────────────────┘

  ↑  Distortion accumulates UPWARD  (each transform adds to AC_Risk)
  ↓  Calibration feedback flows DOWNWARD  (outcome vs. verdict re-tunes U_phys, D_transform, B_cog)
```

---

## 2. The 12 Canonical GEOX Products — Layer Mapping

Each product is mapped to: (a) its L0 inputs, (b) its L1 engine, (c) its primary L2 equations, (d) its L3 product type, (e) its L4 dimension name and floor bindings.

---

### 2.1 HAZARD — Seismic / Volcanic / Multi-Hazard

| Layer | Content |
|---|---|
| **L0** | Seismic catalogue, fault maps, site characterization logs, borehole HVSR, strong-motion records |
| **L1** | OpenQuake Engine (PSHA), ShakeMap, CRISIS2015 |
| **L2** | GMPE: `ln(IM) = f(M, R, Vs30, …) + σε`; hazard integral over MFD |
| **L3** | PGA/PGV hazard map with return periods; UQ: logic-tree epistemic + aleatory σ |
| **L4 Dimension** | `HAZARD` |
| **Floor Bindings** | F2 (truth), F4 (clarity/units), F8 (regulatory), F9 (anti-hantu) |
| **888_HOLD trigger** | Any output used for building code calibration, dam siting, or infrastructure planning |
| **Mandatory UQ** | Deaggregation by M/R; full logic-tree hazard curves at P10/mean/P84 |

---

### 2.2 HYDRO — Hydrogeological / Groundwater Model

| Layer | Content |
|---|---|
| **L0** | Borehole logs, aquifer test data, water level records, recharge estimates, soil maps |
| **L1** | MODFLOW 6, FEFLOW, HGS |
| **L2** | Darcy: `q = -K∇h`; groundwater flow: `∇·(K∇h) = Ss(∂h/∂t) - W`; Ghijben-Herzberg for coastal |
| **L3** | Potentiometric surface map, drawdown contour, aquifer yield estimate; UQ: parameter ensembles |
| **L4 Dimension** | `HYDRO` |
| **Floor Bindings** | F2, F4, F6 (water sovereignty), F8 (regulatory), F9 |
| **888_HOLD trigger** | Any use for public water supply decisions, irrigation licensing, or dam safety |
| **Mandatory UQ** | K and Ss parameter uncertainty; recharge scenario ensemble |

---

### 2.3 CCS — Carbon Capture and Storage

| Layer | Content |
|---|---|
| **L0** | Seismic reflection, well logs (porosity, permeability, caprock integrity), formation pressure tests |
| **L1** | TOUGH2 / TOUGH+, Eclipse CO₂Store, DuMux |
| **L2** | Two-phase flow: `∂(φρ_CO₂)/∂t + ∇·(ρ_CO₂ u_CO₂) = q`; Peng-Robinson EOS for CO₂ |
| **L3** | CO₂ plume extent, trapping capacity estimate, injectivity assessment; UQ: caprock uncertainty |
| **L4 Dimension** | `CCS` |
| **Floor Bindings** | F2, F4, F8 (regulatory — CCUS regulation), F9 |
| **888_HOLD trigger** | Mandatory before any storage permit or regulatory filing |
| **Mandatory UQ** | Caprock seal uncertainty; P10/P50/P90 storage capacity; migration probability map |
| **Cross-product dependency** | Inherits HYDRO AC_Risk if saline aquifer is host formation (see `GEOX_INTERPRODUCT_RISK_RULES.md`) |

---

### 2.4 GEOCHEM — Geochemical Anomaly Map

| Layer | Content |
|---|---|
| **L0** | Stream sediment, soil, or rock geochemical survey data; VNIR/SWIR spectral imagery |
| **L1** | QGIS + statistical geochemistry (R/Python: compositional data analysis), ASTER processing |
| **L2** | Compositional data analysis (Aitchison geometry); threshold: `T = μ + 2σ` or robust MAD |
| **L3** | Anomaly probability map with confidence polygons; UQ: sampling density, detection limits |
| **L4 Dimension** | `GEOCHEM` |
| **Floor Bindings** | F2, F7 (humility — over-interpretation risk), F9 (anti-hantu — spectral artifacts) |
| **888_HOLD trigger** | Any product used to justify mineral exploration expenditure > JD threshold |
| **Mandatory UQ** | Nugget effect; false-positive rate from sampling density; spectral confusion matrix if EO-derived |

---

### 2.5 PETROLEUM_SYSTEM — Basin / Play / Prospect Assessment

| Layer | Content |
|---|---|
| **L0** | Seismic reflection/refraction, well logs, geochemistry (TOC, Ro), DST data |
| **L1** | PetroMod / BasinMod (maturity), Petrel / OpendTect (seismic interpretation), Monte Carlo engine |
| **L2** | Burial history + heat flow; Sweeney-Burnham vitrinite model; volumetrics: `N = A·h·φ·(1-Sw)/Boi` |
| **L3** | Play fairway map, prospect inventory with GRV/STOOIP P10/P50/P90; UQ: full Monte Carlo |
| **L4 Dimension** | `PETROLEUM_SYSTEM` |
| **Floor Bindings** | F2, F4, F8 (reserves certification), F9 |
| **888_HOLD trigger** | Any product used for reserves booking, FID, or regulatory submission |
| **Mandatory UQ** | Full volumetric Monte Carlo; chance of success decomposed (source, migration, trap, seal, reservoir) |

---

### 2.6 FRACTURE — Discrete Fracture Network / Structural Model

| Layer | Content |
|---|---|
| **L0** | FMI/UBI borehole image logs, core fracture description, seismic curvature, outcrop scanlines |
| **L1** | FracMan, Move (Petex), Petrel DFN module |
| **L2** | Power-law fracture length distribution; Oda tensor for permeability upscaling; critical stress analysis |
| **L3** | DFN realizations with permeability tensor; critically stressed fracture probability map |
| **L4 Dimension** | `FRACTURE` |
| **Floor Bindings** | F2, F7, F9 |
| **888_HOLD trigger** | Used for geothermal stimulation planning or induced seismicity risk assessment |
| **Mandatory UQ** | DFN parameter uncertainty (orientation, density, length distribution); ensemble of realizations |
| **Cross-product dependency** | Supplies fracture permeability to HYDRO, CCS, and GEOTHERMAL products |

---

### 2.7 GEOTHERMAL — Heat Flow / Geothermal Resource

| Layer | Content |
|---|---|
| **L0** | BHT logs, thermal conductivity measurements, geothermal gradient surveys, heat flow probes |
| **L1** | PetroMod (thermal), TOUGH2-EOS1, FEFLOW thermal mode |
| **L2** | Fourier heat conduction: `q = -λ∇T`; Nusselt-number convection where applicable |
| **L3** | Heat flow map, geothermal gradient section, resource volume estimate |
| **L4 Dimension** | `GEOTHERMAL` |
| **Floor Bindings** | F2, F4, F8 |
| **888_HOLD trigger** | Resource estimate used for power generation licensing |
| **Mandatory UQ** | Thermal conductivity uncertainty; fluid flow regime uncertainty (conductive vs. convective) |

---

### 2.8 MINERAL — Mineral Resource Model

| Layer | Content |
|---|---|
| **L0** | Drill core assays, density measurements, XRF/QXRD mineralogy, petrographic logs |
| **L1** | Leapfrog Geo, Surpac, GSLIB (kriging / simulation) |
| **L2** | Ordinary/indicator kriging; variogram model; grade-tonnage from block model |
| **L3** | Block model with grade-tonnage curve; resource classification (Inferred/Indicated/Measured) |
| **L4 Dimension** | `MINERAL` |
| **Floor Bindings** | F2, F4, F8 (JORC/NI43-101 compliance), F9 |
| **888_HOLD trigger** | Any resource estimate used for public reporting or mining investment decision |
| **Mandatory UQ** | Kriging variance; conditional simulation scatter; classification criteria explicit |

---

### 2.9 STRUCTURAL_GEOLOGY — Structural Model / 3D Geometry

| Layer | Content |
|---|---|
| **L0** | Seismic horizons and faults, borehole structural logs, wellbore deviation surveys, gravity |
| **L1** | Move (Petex restoration), SKUA-GOCAD, Petrel structure modelling |
| **L2** | Depth conversion: `z = t/2 · V_int`; fault throw/heave; flexural slip restoration |
| **L3** | 3D structural model with fault geometry and horizon surfaces; UQ: interpretation uncertainty polygons |
| **L4 Dimension** | `STRUCTURAL_GEOLOGY` |
| **Floor Bindings** | F2, F4, F7, F9 |
| **888_HOLD trigger** | Structural model used as geometry input to CCS, HYDRO, or HAZARD |
| **Mandatory UQ** | Depth conversion velocity uncertainty; interpretation pick alternatives |

---

### 2.10 ENVIRONMENTAL — Contamination / Remediation Model

| Layer | Content |
|---|---|
| **L0** | Environmental soil/water sampling, ERT/GPR surveys, site investigation boreholes |
| **L1** | PHREEQC (geochemical), FEFLOW / MODFLOW-MT3D (transport), HYDRUS |
| **L2** | Advection-dispersion: `∂C/∂t = D∇²C - v·∇C - λC`; sorption: `Kd` partitioning |
| **L3** | Contaminant plume map, risk score, remediation design recommendation |
| **L4 Dimension** | `ENVIRONMENTAL` |
| **Floor Bindings** | F2, F6 (water sovereignty), F8 (regulatory — environmental permit), F9 |
| **888_HOLD trigger** | Any output informing regulatory compliance action or public health assessment |
| **Mandatory UQ** | Kd parameter uncertainty; plume arrival time distribution |

---

### 2.11 SHALLOW_GEOHAZARD — Slope Stability / Subsidence / Landslide / Liquefaction

| Layer | Content |
|---|---|
| **L0** | InSAR displacement time series, LiDAR DEM, CPT/SPT borehole data, rainfall records |
| **L1** | SLOPE/W, PLAXIS, FLAC, CAESAR-Lisflood |
| **L2** | Mohr-Coulomb failure criterion: `τ = c' + σ'·tan φ'`; factor of safety; Newmark displacement |
| **L3** | Stability map with factor-of-safety contours, landslide susceptibility index |
| **L4 Dimension** | `SHALLOW_GEOHAZARD` |
| **Floor Bindings** | F2, F4, F8, F9 |
| **888_HOLD trigger** | Any assessment informing urban planning, road/rail routing, or dam safety |
| **Mandatory UQ** | Shear strength parameter uncertainty; pore pressure scenario ensemble |

---

### 2.12 REMOTE_SENSING — Earth Observation / Surface Mapping

| Layer | Content |
|---|---|
| **L0** | Landsat, Sentinel-2, ALOS PALSAR, ASTER, WorldView, drone imagery |
| **L1** | ENVI, SNAP, Google Earth Engine, Orfeo Toolbox |
| **L2** | Spectral indices (NDVI, NDWI, band ratios); SAR coherence; change detection |
| **L3** | Classified thematic map, anomaly density map, change polygon dataset |
| **L4 Dimension** | `REMOTE_SENSING` |
| **Floor Bindings** | F2, F7, F9 (vision ≠ truth — highest B_cog risk in the entire stack) |
| **888_HOLD trigger** | EO-derived product used to assert geological class without confirmatory ground truth |
| **Mandatory UQ** | Accuracy assessment confusion matrix; producer's and user's accuracy per class |

---

## 3. Where AC_Risk Is Computed

AC_Risk is computed at **L3→L4 transition** — after the physics engine has produced a product and before a verdict is issued.

The formula is:

$$AC\_Risk = U_{phys} \times D_{transform} \times B_{cog}$$

Each term is assessed separately per product, per run. Detailed operational definitions are in `TOAC_AC_RISK_SPEC.md`.

---

## 4. Where 888_HOLD Is Legally Mandatory

The following product-decision combinations **always** require human veto (888_HOLD cannot be auto-bypassed):

| Product | Decision Trigger | Floor |
|---|---|---|
| HAZARD | Building code calibration, infrastructure siting, dam safety | F8, F13 |
| HYDRO | Public water supply, groundwater licensing, aquifer pump rate | F6, F8, F13 |
| CCS | Storage permit, regulatory CO₂ certification, injectivity approval | F8, F13 |
| PETROLEUM_SYSTEM | Reserves booking, FID, external reserves certification | F8, F13 |
| MINERAL | Publicly reported resource, mining investment decision | F8, F13 |
| ENVIRONMENTAL | Regulatory compliance action, public health notification | F6, F8, F13 |
| SHALLOW_GEOHAZARD | Urban planning, dam safety, critical infrastructure routing | F8, F13 |
| REMOTE_SENSING | Any product asserted as FACT without confirmatory ground data | F2, F9, F13 |

---

## 5. Calibration Feedback Arc (Mandatory Loop)

Every governed decision produces a feedback obligation:

```
VERDICT ISSUED (SEAL / QUALIFY / HOLD / VOID)
    ↓
OUTCOME OBSERVED (drilling result, monitoring data, regulatory audit)
    ↓
DELTA COMPUTED: expected vs. actual
    ↓
RE-TUNE: U_phys, D_transform, B_cog updated per basin / per engine / per dimension
    ↓
AC_Risk thresholds revised → new run uses improved priors
```

This loop is not optional for HAZARD, HYDRO, and CCS products. It is the mechanism that converts ToAC from an open-loop auditor into a civilization-grade epistemic system.

---

## 6. Naming as Creation — Dimension Registry

Each named dimension in this document is a constitutional act. Naming `HYDRO` does not create the data — it opens the governance slot, assigns the floors, and obligates the engineer to fill it with real physics before a verdict can be issued.

| Dimension Name | Named | Floors Assigned | Data Contract Fulfilled? |
|---|---|---|---|
| HAZARD | ✅ | F2, F4, F8, F9 | Requires L0 seismic catalogue |
| HYDRO | ✅ | F2, F4, F6, F8, F9 | Requires L0 borehole + aquifer test |
| CCS | ✅ | F2, F4, F8, F9 | Requires L0 seismic + well logs |
| GEOCHEM | ✅ | F2, F7, F9 | Requires L0 sample survey |
| PETROLEUM_SYSTEM | ✅ | F2, F4, F8, F9 | Requires L0 seismic + well geochemistry |
| FRACTURE | ✅ | F2, F7, F9 | Requires L0 FMI logs or core |
| GEOTHERMAL | ✅ | F2, F4, F8 | Requires L0 BHT + conductivity |
| MINERAL | ✅ | F2, F4, F8, F9 | Requires L0 drill core assays |
| STRUCTURAL_GEOLOGY | ✅ | F2, F4, F7, F9 | Requires L0 seismic interpretation |
| ENVIRONMENTAL | ✅ | F2, F6, F8, F9 | Requires L0 environmental sampling |
| SHALLOW_GEOHAZARD | ✅ | F2, F4, F8, F9 | Requires L0 CPT + InSAR |
| REMOTE_SENSING | ✅ | F2, F7, F9 | Requires L0 EO data + ground truth |

---

## 7. Sovereignty Declaration

This stack is a governed instrument under the following sovereignty rules:

- **Owner**: Muhammad Arif bin Fazil
- **F13 Right**: Sovereign may override any SEAL, invoke any VOID, or hold any product at any time
- **Amendment gate**: Any change to this document requires 888_HOLD invocation and explicit sign-off
- **Deployment rule**: This doc is a production contract only when deployed under arifOS kernel governance; standalone use is experimental

**DITEMPA BUKAN DIBERI — This stack was forged, not given.**
