# GEOX Petrophysics Bridge: The Science of Rock Measurement

**Version:** v0.6.0-FORGE
**Status:** 🔨 DRAFT — Awaiting arifOS 888_HOLD review
**Motto:** *Ditempa Bukan Diberi* — Physics first, cutoffs explicit, magic forbidden.

---

## 1. The Fundamental Question: What Is Petrophysics?

### 1.1 Definition (Non-Negotiable)

**Petrophysics** is the measurement science that connects **physical rock properties** to **log measurements** through physics, chemistry, and empirical calibration. It is NOT magic. It is NOT purely empirical folklore. It is a **constrained inverse problem**:

```
LOG_RESPONSE = f(PHYSICAL_PROPERTIES, TOOL_GEOMETRY, ENVIRONMENT)
```

The goal: invert for `PHYSICAL_PROPERTIES` given `LOG_RESPONSE` and some model `f()`.

### 1.2 The Three Pillars

| Pillar | Domain | Governs | GEOX Implementation |
|--------|--------|---------|---------------------|
| **Physics** | Electromagnetism, nuclear physics, acoustics | Tool response equations | `PhysicsEngine` with Maxwell, Boltzmann, wave equations |
| **Geology** | Mineralogy, texture, diagenesis, facies | Parameter constraints | `RATLAS` material database + `RockType` ontology |
| **Empiricism** | Core, SCAL, MDT, production | Calibration & validation | `CalibrationServer` + `UncertaintyPropagator` |

**CLAIM:** Any petrophysical interpretation that skips physics is **alchemy**, not engineering. Any that claims pure determinism without calibration is **hubris** (F7 violation).

---

## 2. The Ontology: What Exists in the Petrophysical Universe

### 2.1 Core Entities (Must Be First-Class Objects)

```python
# arifos/geox/schemas/petrophysics.py — THE ONTOLOGY

class RockFluidSystem(BaseModel):
    """
    The fundamental unit of petrophysics: rock + fluids at conditions.
    F4 Clarity: Every number has units. F9 Anti-Hantu: Every number has provenance.
    """
    # Frame (solid matrix)
    mineralogy: MineralogyAssembly  # From RATLAS
    texture: TextureClassification  # Grain size, sorting, packing
    clay_type: ClayMineralogy       # Illite, smectite, kaolinite, chlorite

    # Pore system
    porosity: PorosityEstimate      # Total, effective, micro, isolated
    permeability: PermeabilityEstimate  # Klinkenberg-corrected
    pore_geometry: PoreThroatDistribution  # MICP-derived

    # Fluids
    water_saturation: WaterSaturationEstimate  # Sw, Swirr, Swe
    hydrocarbon_saturation: float  # Sh = 1 - Sw
    fluid_contacts: list[FluidContact]  # Free water level, oil-water contact

    # Conditions
    pressure: PressureMeasurement   # Formation pressure
    temperature: TemperatureMeasurement
    salinity: SalinityMeasurement   # Rw derivation

    # Measurement links
    log_evidence: list[LogResponse]  # What logs observed
    core_evidence: list[CoreMeasurement]  # Ground truth
    scal_evidence: list[SCALExperiment]  # Flow properties


class PorosityEstimate(BaseModel):
    """
    Porosity is NOT a single number. It is a distribution with uncertainty.
    F7 Humility: Must declare uncertainty band.
    """
    value: float  # Primary estimate (fraction or percent — F4 mandate explicit)
    units: Literal["fraction", "percent"] = "fraction"

    # Uncertainty structure
    uncertainty_type: Literal["measurement", "model", "calibration", "combined"]
    confidence_interval_95: tuple[float, float]  # [phi_low, phi_high]

    # What porosity means
    porosity_type: Literal["total", "effective", "micro", "isolated", "secondary"]
    fluid_system: Literal["liquid_filled", "gas_filled", "partially_drained"]

    # Physics basis
    measurement_physics: Literal["neutron", "density", "sonic", "nmr", "resistivity_image", "core"]
    mixing_law: Literal["time_average", "raymer_hunt_gardner", "void_space", "grain_density"]

    # Provenance
    calibration_source: str  # Which core, SCAL, or offset well calibrated this
    equations_used: list[str]  # Archie? CRIM? Pride?
    assumptions: list[str]  # "Assumes clean sandstone" — F2 Truth requirement


class WaterSaturationEstimate(BaseModel):
    """
    Sw is the most abused number in petrophysics. GEOX treats it as a hypothesis.
    """
    value: float  # Sw estimate
    units: Literal["fraction", "percent"] = "fraction"

    # Model used (CRITICAL for audit)
    saturation_model: Literal[
        "archie_clean",      # Archie 1942 — clean formations
        "simandoux",         # Simandoux 1963 — shaly sand
        "indonesia",         # Poupon & Leveaux 1971 — laminated shaly sand
        "dual_water",        # Clavier et al. 1977 — clay conductivity
        "waxman_smits",      # Waxman & Smits 1968 — cation exchange
        "modified_simandoux",# Best for high-Vsh heterogeneous systems
        "juvenile",          # Freshwater formations
    ]

    # Model parameters (must be explicit, not magic defaults)
    archie_params: ArchieParameters | None
    shaly_sand_params: ShalySandParameters | None

    # Input sensitivity
    rw_sensitivity: SensitivityAnalysis  # How Sw changes with Rw uncertainty
    phi_sensitivity: SensitivityAnalysis  # How Sw changes with phi uncertainty
    m_exponent_sensitivity: SensitivityAnalysis  # Cementation factor uncertainty

    # Validation status
    validated_by: list[ValidationMethod]  # MDT, production, core Dean-Stark
    hold_status: Literal["SEAL", "QUALIFY", "888_HOLD"]  # Governance


class ArchieParameters(BaseModel):
    """
    Archie equation: Sw^n = (a × Rw) / (PHI^m × Rt)
    Every parameter must be justified, not assumed.
    """
    a: float = Field(default=1.0, description="Tortuosity factor")
    m: float = Field(default=2.0, description="Cementation exponent")
    n: float = Field(default=2.0, description="Saturation exponent")

    # Parameter provenance (F11 Auditability)
    m_derivation: Literal["default", "pickett_plot", "core_measured", "literature", "regional_average"]
    m_confidence: float  # Uncertainty in m
    core_samples_used: list[str] | None  # Which core plugs measured m

    # Rw — the Achilles heel of saturation
    rw_at_t: float  # Rw at formation temperature
    rw_temperature: float  # Temperature at which Rw was measured
    rw_source: Literal["spontaneous_potential", "water_sample", "catalog", "guess"]
    rw_confidence: float  # How certain are we?


class CutoffPolicy(BaseModel):
    """
    Cutoffs are DECISION THRESHOLDS, not physical laws.
    F2 Truth: Must explicitly state that cutoffs are economic/project decisions.
    """
    policy_id: str  # Unique identifier
    policy_name: str  # e.g., "Malay_Basin_Turbidite_2024"

    # Cutoff dimensions
    porosity_cutoff: CutoffDefinition  # Phi min for net reservoir
    vsh_cutoff: CutoffDefinition       # Vsh max for net sand
    sw_cutoff: CutoffDefinition        # Sw max for net pay
    permeability_cutoff: CutoffDefinition | None  # K min for flow

    # Cutoff rationale (F2 Truth requirement)
    calibration_basis: str  # "Based on MDT mobility > 0.1 mD/cP in 15 wells"
    economic_basis: str     # "Oil price $80/bbl, OPEX $15/bbl"
    rock_physics_basis: str # "Capillary pressure shows Pc < 50 psi for phi > 0.12"

    # Temporal scope
    valid_from: datetime
    valid_until: datetime | None
    superseded_by: str | None  # Chain of custody for cutoff evolution

    # Governance
    approved_by: str  # Human who signed off
    approval_date: datetime
    floor_check: dict[str, bool]  # F1-F13 compliance
```

### 2.2 The Measurement Chain (From Sensor to Decision)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEOX PETROPHYSICS MEASUREMENT CHAIN                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAW SIGNALS          PHYSICS MODELS         GEOLOGICAL INTERPRETATION      │
│  ───────────          ─────────────          ────────────────────────       │
│                                                                             │
│  Gamma Ray      →   Clay Volume Models   →   Lithology Facies               │
│  (API counts)       (Clavier-Fertl,         (Sand/Shale Ratio,             │
│                     Steiber, etc.)           Depositional Environment)      │
│                                                                             │
│  Neutron/Density →  Porosity Mixing      →   Rock Type                      │
│  (cps, g/cc)        Laws (time-avg,         (HFU, FZI, RQI)                │
│                     raymer-hunt)                                            │
│                                                                             │
│  Resistivity    →   Saturation Models    →   Fluid Contacts                 │
│  (ohm-m)            (Archie, Simandoux,      (OWC, GOC, FWL)               │
│                     Indonesia, Dual-Water)                                  │
│                                                                             │
│  NMR T2         →   Pore Size Dist       →   Permeability                   │
│  (msec)             (Coates, SDR)            (Free vs. Bound Fluid)        │
│                                                                             │
│  Sonic          →   Frame Properties     →   Geomechanics                   │
│  (μs/ft)            (Elastic moduli)         (Fracture gradient)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Physics: Models That Must Be Governed

### 3.1 Porosity Physics

| Tool | Physics | Key Equation | GEOX Class |
|------|---------|--------------|------------|
| **Density** | Electron density / Compton scattering | `φd = (ρma - ρb) / (ρma - ρfl)` | `DensityPorositySolver` |
| **Neutron** | Hydrogen index / neutron moderation | `φn = f(HI_fluid, HI_matrix)` | `NeutronPorositySolver` |
| **Sonic** | Acoustic wave transit time | `φs = (Δt - Δtma) / (Δtfl - Δtma)` | `SonicPorositySolver` |
| **NMR** | Spin-lattice relaxation (T2) | `φ = Σ(V_pore,i × HI_i)` | `NMRPorositySolver` |
| **Resistivity Image** | Ohm's law in 2D | `φ_img = f(conductivity contrast)` | `ImagePorositySolver` |

**Critical F4 Requirement:** Every porosity calculation must declare:
- Matrix density (`ρma`) — from RATLAS or core grain density
- Fluid density (`ρfl`) — from PVT or assumed
- Environmental corrections (borehole, invasion, standoff)

### 3.2 Saturation Physics: The Model Hierarchy

```python
# arifos/geox/physics/saturation_models.py

class SaturationModel(ABC):
    """
    Abstract base for all water saturation models.
    Each model has ASSUMPTIONS that must be checked against the rock.
    """

    @abstractmethod
    def compute_sw(self, rt: float, phi: float, rw: float, **params) -> float:
        """Compute Sw given resistivity, porosity, and formation water resistivity."""
        pass

    @abstractmethod
    def validate_assumptions(self, rock: RockFluidSystem) -> list[str]:
        """
        Return list of assumption violations.
        F9 Anti-Hantu: Must check that model assumptions match reality.
        """
        pass


class ArchieModel(SaturationModel):
    """
    Archie (1942): Sw^n = (a × Rw) / (PHI^m × Rt)

    ASSUMPTIONS (must be validated):
    - Clean formation (Vsh ≈ 0)
    - Homogeneous pore system
    - Water-wet rock
    - Single water salinity

    WHEN TO USE: Clean sandstones, some carbonates
    WHEN NOT TO USE: Shaly sands (>10% clay), laminated systems
    """

    def compute_sw(self, rt: float, phi: float, rw: float,
                   a: float = 1.0, m: float = 2.0, n: float = 2.0) -> float:
        if phi <= 0 or rt <= 0:
            return 1.0  # Fully wet — safe default
        sw = ((a * rw) / (phi**m * rt)) ** (1.0 / n)
        return max(0.0, min(1.0, sw))

    def validate_assumptions(self, rock: RockFluidSystem) -> list[str]:
        violations = []
        if rock.clay_type.total_clay_volume > 0.1:
            violations.append(f"Archie assumes clean sand. Vcl={rock.clay_type.total_clay_volume:.2f}")
        if rock.texture.lamination_index > 0.3:
            violations.append("Archie assumes homogeneous. Laminated system detected.")
        return violations


class SimandouxModel(SaturationModel):
    """
    Simandoux (1963): For shaly sands with dispersed clay.

    Equation: Sw = [ (a × Rw) / (PHI^m × Rt) ]^(1/n)  +  (Vsh × Rsh / Rt) × correction

    ASSUMPTIONS:
    - Shaly sand with dispersed clay
    - Clay resistivity (Rsh) known or estimable
    - Single water type

    WHEN TO USE: Moderately shaly sands (10-40% Vsh), many Tertiary clastics
    """
    pass


class IndonesiaModel(SaturationModel):
    """
    Poupon & Leveaux (1971): For laminated and dispersed shaly sands.

    Equation: 1/√Rt = (Vsh^((2-Vsh)/2) / √Rsh) + (PHI^(m/2) / √(a × Rw × Sw^n))

    ASSUMPTIONS:
    - Mixed clay distribution (laminated + structural + dispersed)
    - Better for high-Vsh systems than Simandoux

    WHEN TO USE: Heterolithic systems, high-Vsh sands (>30%)
    """
    pass


class DualWaterModel(SaturationModel):
    """
    Clavier et al. (1977): Explicit clay physics via CEC.

    Concept: Two waters — free water (Rw) and bound water (Rwb)
    Conductor: Clay counterions (Qv = CEC × (1-φ) / φ)

    ASSUMPTIONS:
    - CEC (cation exchange capacity) known or correlated
    - Clay type affects Qv (smectite >> illite > kaolinite)
    - More physically rigorous but requires more parameters

    WHEN TO USE: Freshwater formations, high-CEC clays, scientific work
    """
    pass


class WaxmanSmitsModel(SaturationModel):
    """
    Waxman & Smits (1968): Temperature-dependent clay conductivity.

    Concept: B × Qv term captures clay counterion conductivity
    Temperature-sensitive (B decreases with increasing T)

    WHEN TO USE: Varied temperature profiles, geothermal, deep gas
    """
    pass
```

### 3.3 Permeability Physics

| Method | Physics | Inputs | Validity |
|--------|---------|--------|----------|
| **Kozeny-Carman** | Pore geometry / tortuosity | φ, specific surface | Theoretical bound |
| **Timur/Coates** | NMR T2 / bound fluid | NMR T2 distribution, BVI | Empirical, validated |
| **SDR** | NMR T2 log-mean | T2lm, φ | Fast estimate |
| **Winland R35** | MICP pore throat | Pc at 35% Hg saturation | Rock typing |
| **Kazemi** | Hydraulic flow units | FZI, RQI, φz | HFU method |

**GEOX Rule:** Never report permeability without stating:
1. Method used
2. Calibration dataset (which cores)
3. Confidence interval
4. Applicable rock type (HFU)

---

## 4. The Cutoff Problem: From Physics to Decision

### 4.1 What Cutoffs Actually Are

**CRITICAL F2 TRUTH DECLARATION:**

Cutoffs are **NOT** physical laws. They are **decision boundaries** that separate:
- Reservoir vs. non-reservoir (geological)
- Pay vs. non-pay (economic)
- Bookable vs. non-bookable (regulatory)

**The Cutoff Ontology:**

```python
class CutoffDefinition(BaseModel):
    """
    A cutoff is a threshold applied to a petrophysical curve to classify rock.
    F2 Truth: Must explicitly declare the DECISION being made.
    """
    curve_name: str  # "PHIE", "VSH", "SW", "K"
    threshold_value: float
    operator: Literal[">", ">=", "<", "<=", "==", "range"]

    # What decision this cutoff drives
    decision_type: Literal[
        "reservoir_vs_non_reservoir",  # Geological
        "net_vs_gross",                # Volumetric
        "pay_vs_non_pay",              # Economic
        "proven_vs_unproven",          # Regulatory
        "drill_vs_no_drill",           # Operational
    ]

    # Physics basis (if any)
    physics_justification: str | None  # "Capillary pressure entry at Pc=50 psi"

    # Empirical basis (calibration)
    calibration_dataset: str  # "23 cores from Field X, MDT mobility > 0.1 mD/cP"
    calibration_statistics: dict[str, float]  # ROC curve, confusion matrix

    # Economic basis (for pay cutoffs)
    oil_price_basis: float | None  # $/bbl at time of cutoff definition
    opex_basis: float | None       # $/bbl
    economic_threshold: float | None  # Minimum EUR per well

    # Uncertainty
    false_positive_rate: float  # Rock classified as pay that isn't
    false_negative_rate: float  # Pay classified as non-pay

    # Governance
    defined_by: str  # Petrophysicist name
    approved_by: str  # Manager name
    definition_date: datetime
    review_date: datetime
```

### 4.2 The Cutoff Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CUTOFF HIERARCHY IN GEOX                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LEVEL 1: LITHOLOGY (Geological Reality)                                    │
│  ───────────────────────────────────────                                    │
│  Input: GR, SP, PE, elemental spectroscopy                                  │
│  Output: Sand vs. Shale (depositional)                                      │
│  Cutoff: Vsh < 0.50 (example — varies by basin)                            │
│  Decision: What is the geological facies?                                   │
│                                                                             │
│  LEVEL 2: RESERVOIR (Storage Capacity)                                      │
│  ───────────────────────────────────                                        │
│  Input: PHI, K, Vsh                                                        │
│  Output: Net Reservoir (can store fluids)                                   │
│  Cutoff: Phi > 0.08, Vsh < 0.40, K > 0.1 mD                                │
│  Decision: Does this rock have sufficient storage?                          │
│                                                                             │
│  LEVEL 3: PAY (Economic Flow)                                               │
│  ────────────────────────────                                               │
│  Input: Sw, PHI, fluid properties, economics                                │
│  Output: Net Pay (will flow economically)                                   │
│  Cutoff: Sw < 0.60 (oil), Sw < 0.75 (gas), NPV > 0                         │
│  Decision: Will this rock produce profitably?                               │
│                                                                             │
│  LEVEL 4: BOOKABLE (Regulatory Proved)                                      │
│  ───────────────────────────────────                                        │
│  Input: Sw, distance to wellbore, seismic quality                           │
│  Output: Proved reserves (SEC/SPE compliant)                                │
│  Cutoff: Distance < L/2 from well, Sw < proven cutoff, high confidence      │
│  Decision: Can we report this to investors/regulators?                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Typical Cutoff Values (Examples Only — Field-Specific Calibration Required)

| Parameter | Typical Range | Malay Basin Example | Physics Basis |
|-----------|---------------|---------------------|---------------|
| **Phi_cutoff** | 0.08–0.12 (sand), 0.04–0.08 (carb) | 0.10 | Capillary entry pressure |
| **Vsh_cutoff** | 0.30–0.50 | 0.40 | Laminated vs. dispersed model |
| **Sw_cutoff (oil)** | 0.50–0.65 | 0.60 | Relative permeability kro > 0.1 |
| **Sw_cutoff (gas)** | 0.65–0.80 | 0.75 | Lower viscosity = higher Sw economic |
| **K_cutoff** | 0.1–10 mD | 1.0 mD | Flow capacity (Kh > threshold) |
| **NTG_cutoff** | 0.10–0.50 | 0.30 | Reservoir heterogeneity |

**GEOX Warning:** Using default cutoffs without calibration triggers **888_HOLD**.

---

## 5. The Architecture: What Needs to Be Forged

### 5.1 MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEOX PETROPHYSICS MCP SERVERS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  log_server     │    │  core_server    │    │  scal_server    │         │
│  │  ───────────    │    │  ───────────    │    │  ───────────    │         │
│  │  LAS/DLIS/WITS  │◄──►│  Core photos    │◄──►│  Cap pressure   │         │
│  │  DLIS parsing   │    │  Plug data      │    │  Rel perm       │         │
│  │  Curve QC       │    │  S lithology    │    │  Wettability    │         │
│  │  Depth shift    │    │  Grain density  │    │  Electrical     │         │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘         │
│           │                      │                      │                   │
│           └──────────────────────┼──────────────────────┘                   │
│                                  ▼                                          │
│                     ┌─────────────────────┐                                 │
│                     │   petrophysics_     │                                 │
│                     │   engine_server     │                                 │
│                     │   ───────────────── │                                 │
│                     │   Physics solvers   │                                 │
│                     │   Model selection   │                                 │
│                     │   Uncertainty prop  │                                 │
│                     │   Cutoff governance │                                 │
│                     └──────────┬──────────┘                                 │
│                                │                                            │
│           ┌────────────────────┼────────────────────┐                       │
│           ▼                    ▼                    ▼                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ rocktype_server │  │ cutoff_server   │  │ reserves_server │             │
│  │ ─────────────── │  │ ─────────────   │  │ ─────────────── │             │
│  │ HFU/RQI/FZI     │  │ Policy mgmt     │  │ OOIP/OGIP calc  │             │
│  │ Winland         │  │ Sensitivity     │  │ Probabilistic   │             │
│  │ Flow units      │  │ What-if         │  │ SEC compliance  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 New Tools to Forge

```python
# arifos/geox/tools/petrophysics/multimineral_solver.py

class MultiMineralSolverTool(BaseTool):
    """
    Solve for mineral volumes and porosity simultaneously.

    Physics: Linear mixing model with constraints
    Inputs: GR, RHOB, NPHI, PEF, elemental (if available)
    Outputs: V_quartz, V_calcite, V_dolomite, V_clay, PHIE

    F9 Anti-Hantu: Returns non-uniqueness metrics — how many solutions fit?
    """
    pass


# arifos/geox/tools/petrophysics/nmr_processor.py

class NMRProcessorTool(BaseTool):
    """
    Process NMR T2 distributions into petrophysical properties.

    Physics: Bloch equations, relaxation mechanisms
    Methods: Coates, SDR, spectral BVI/FFI decomposition
    Outputs: PHI, BVI, FFI, permeability, pore size distribution
    """
    pass


# arifos/geox/tools/petrophysics/cutoff_calibrator.py

class CutoffCalibratorTool(BaseTool):
    """
    Calibrate cutoffs from core, MDT, and production data.

    Method: ROC analysis, confusion matrix, economic optimization
    Output: CutoffPolicy with full provenance

    F2 Truth: Explicitly separates physics from economics.
    """
    pass


# arifos/geox/tools/petrophysics/uncertainty_propagator.py

class UncertaintyPropagatorTool(BaseTool):
    """
    Monte Carlo / analytical uncertainty propagation through petrophysics.

    Inputs: Log measurement uncertainties, model uncertainties
    Output: Porosity_distribution, Sw_distribution (not point estimates)

    F7 Humility: Forces acknowledgment of uncertainty in every number.
    """
    pass


# arifos/geox/tools/petrophysics/rock_typer.py

class RockTyperTool(BaseTool):
    """
    Classify rock into Hydraulic Flow Units (HFU) using RQI/FZI.

    Physics: Kozeny-Carman modified for variable tortuosity
    Method: FZI = RQI / PHIz
    Output: HFU class, expected permeability range, flow character
    """
    pass


# arifos/geox/tools/petrophysics/capillary_integrator.py

class CapillaryIntegratorTool(BaseTool):
    """
    Integrate capillary pressure data with log-derived saturations.

    Method: J-function normalization, height above FWL
    Output: Sw_predicted vs. Sw_log comparison, validation status
    """
    pass
```

### 5.3 Schema Extensions

```python
# arifos/geox/schemas/petrophysics/rock_types.py

class HydraulicFlowUnit(BaseModel):
    """
    Averitt (1961), Hearn et al. (1984), Amaefule et al. (1993)
    """
    hfu_id: int
    fzi: float  # Flow zone indicator
    rqi: float  # Reservoir quality index
    phiz: float  # Porosity (zeta)

    # Properties
    expected_perm_range: tuple[float, float]  # min, max mD
    expected_phi_range: tuple[float, float]   # min, max fraction

    # Characterization
    pore_throat_class: Literal["mega", "macro", "meso", "micro", "nano"]
    winland_r35: float | None

    # Geological correlation
    depositional_facies: str
    diagenetic_grade: str


class PetrophysicalInterpretation(BaseModel):
    """
    The complete governed interpretation of a well interval.
    """
    interpretation_id: str
    well_id: str
    interval_top: float
    interval_base: float

    # Primary results
    lithology: LithologyEstimate
    porosity: PorosityEstimate
    saturation: WaterSaturationEstimate
    permeability: PermeabilityEstimate

    # Classification
    net_reservoir_flag: bool
    net_pay_flag: bool
    hfu_classification: HydraulicFlowUnit

    # Governance
    cutoff_policy_applied: CutoffPolicy
    physics_models_used: list[str]
    uncertainty_envelope: UncertaintyEnvelope
    floor_check: dict[str, bool]
    verdict: Literal["SEAL", "QUALIFY", "888_HOLD"]

    # Evidence chain
    log_evidence: list[LogResponse]
    core_evidence: list[CoreMeasurement]
    mdt_evidence: list[MDTMeasurement]
    production_evidence: list[ProductionData]
```

---

## 6. The LLM Integration: Reasoning, Not Replacing

### 6.1 What LLMs Do in GEOX Petrophysics

| Role | Function | Example |
|------|----------|---------|
| **Model Selector** | Choose appropriate physics model | "High Vsh detected → recommend Indonesia over Archie" |
| **Assumption Checker** | Validate model assumptions | "Archie assumes clean sand. Vsh=35% violates this." |
| **Contradiction Detector** | Flag inconsistent data | "Log says Sw=80%, MDT says oil. Investigate." |
| **Explanation Generator** | Explain results to humans | "Sw=45% derived from Simandoux with Rw=0.15 at 150°C" |
| **Cutoff Justifier** | Document cutoff rationale | "Phi_cutoff=10% based on Pc>50psi from 12 MICP curves" |
| **Uncertainty Explainer** | Translate confidence intervals | "85% confidence that Sw is 40-55%" |

### 6.2 LLM Prompt Template: Physics Model Selection

```python
GEOX_PETROPHYSICS_MODEL_SELECTOR_PROMPT = """
You are the physics model selector for GEOX petrophysics.
Your job: select the appropriate water saturation model based on rock properties.

INPUT ROCK PROPERTIES:
- Clay volume: {vsh:.2f} (fraction)
- Clay type: {clay_type}
- Lamination index: {lamination:.2f}
- Formation water salinity: {salinity:.0f} kppm
- Temperature: {temperature:.1f} degC
- Available logs: {available_logs}

AVAILABLE MODELS:
1. ARCHIE: Clean formations (Vsh < 10%), homogeneous
2. SIMANDOUX: Moderately shaly (10-40% Vsh), dispersed clay
3. INDONESIA: High Vsh (>30%), laminated systems
4. DUAL_WATER: Freshwater, high CEC clays, scientific work
5. WAXMAN_SMITS: Temperature-sensitive, deep gas

SELECTION CRITERIA:
- If Vsh < 0.10 and homogeneous → ARCHIE
- If 0.10 <= Vsh < 0.40 and dispersed clay → SIMANDOUX
- If Vsh >= 0.30 and laminated → INDONESIA
- If salinity < 5000 kppm or CEC known → DUAL_WATER

OUTPUT FORMAT (JSON):
{{
    "selected_model": "model_name",
    "confidence": 0.0-1.0,
    "justification": "Why this model fits the rock",
    "assumption_violations": ["list of concerns"],
    "alternative_models": ["if primary fails"],
    "calibration_recommendations": ["what core/scal needed"]
}}

F2 TRUTH REQUIREMENT: If rock properties are ambiguous, declare UNCERTAINTY.
Do not guess when data is insufficient.
"""
```

---

## 7. The Governance: Constitutional Floors Applied

### 7.1 Petrophysics-Specific Floor Enforcement

| Floor | Petrophysics Application | Violation Example | GEOX Response |
|-------|-------------------------|-------------------|---------------|
| **F1 Amanah** | Cutoffs can be revised | Locked in wrong cutoffs | Versioned cutoff policies, reversible flags |
| **F2 Truth** | Sw accuracy claim | Claiming Sw ±2% when uncertainty is ±15% | 888_HOLD until uncertainty declared |
| **F4 Clarity** | Units explicit | Porosity as "12" (unitless? percent?) | Reject output without explicit units |
| **F7 Humility** | Uncertainty bounds | Sw=50% (point estimate only) | Force distribution output |
| **F9 Anti-Hantu** | No assumed parameters | Using Archie m=2.0 without justification | Flag as unverified assumption |
| **F11 Audit** | Full calculation chain | Missing intermediate steps | Log every equation and parameter |
| **F13 Sovereign** | Human approval for reserves | Automated booked reserves | 888_HOLD pending signoff |

### 7.2 Automatic 888_HOLD Triggers for Petrophysics

```python
# arifos/geox/governance/petrophysics_hold_triggers.py

PETROPHYSICS_HOLD_TRIGGERS = {
    # Physics violations
    "unverified_archie_in_shaly_sand": {
        "condition": "Vsh > 0.15 AND saturation_model == 'archie'",
        "rationale": "Archie assumes clean sand. Using in shaly sand violates physics.",
        "required_action": "Switch to Simandoux, Indonesia, or Dual-Water model"
    },

    "unverified_rw": {
        "condition": "rw_source in ['guess', 'regional_default'] AND confidence > 0.5",
        "rationale": "Rw is the dominant uncertainty in Sw. Unverified Rw invalidates Sw.",
        "required_action": "Obtain water sample or SP-derived Rw with temperature correction"
    },

    "missing_core_calibration": {
        "condition": "phi_cutoff_defined AND no_core_validation_within_500m",
        "rationale": "Cutoffs without core calibration are economic guesses, not engineering.",
        "required_action": "Acquire core or MDT data to validate cutoff"
    },

    "uncertainty_not_propagated": {
        "condition": "reported_sw_uncertainty == 0.0 OR reported_phi_uncertainty == 0.0",
        "rationale": "All petrophysical measurements have uncertainty. Zero uncertainty is false precision.",
        "required_action": "Run Monte Carlo or analytical uncertainty propagation"
    },

    # Economic/governance violations
    "cutoff_not_documented": {
        "condition": "net_pay_calculated AND cutoff_policy_id is None",
        "rationale": "Net pay requires explicit cutoff policy for reproducibility.",
        "required_action": "Define and approve CutoffPolicy with full provenance"
    },

    "reserves_without_validation": {
        "condition": "proved_reserves_reported AND validation_data is None",
        "rationale": "SEC/SPE requires validation for proved reserves.",
        "required_action": "Provide production, MDT, or test validation data"
    }
}
```

---

## 8. The Integration: MCP + arifOS + LLM

### 8.1 Example Workflow: From Log to Reserves

```python
# Example: GEOX petrophysics workflow orchestrated by LLM

async def evaluate_prospect_petrophysics(well_id: str, interval: tuple[float, float]):
    """
    Complete petrophysics evaluation with full governance.
    """

    # 1. SENSE: Load data via MCP
    las_data = await mcp_call("log_server", "get_las", well_id=well_id)
    core_data = await mcp_call("core_server", "get_core", well_id=well_id, interval=interval)
    scal_data = await mcp_call("scal_server", "get_scal", well_id=well_id)

    # 2. MIND: LLM selects physics models
    model_selection = await llm.select_saturation_model(
        vsh=las_data.vsh_avg,
        clay_type=core_data.clay_type,
        lamination=core_data.lamination_index
    )

    # 3. Check F9 Anti-Hantu: Validate assumptions
    if model_selection.assumption_violations:
        return GeoxVerdictResult(
            verdict=Verdict.HOLD,
            explanation=f"Model assumptions violated: {model_selection.assumption_violations}",
            audit_id="F9-HANTU-PETRO-001"
        )

    # 4. COMPUTE: Physics engine calculates properties
    results = await mcp_call(
        "petrophysics_engine",
        "compute_properties",
        logs=las_data,
        model=model_selection.selected_model,
        propagate_uncertainty=True
    )

    # 5. REFLECT: Validate against core/MDT
    validation = await mcp_call(
        "petrophysics_engine",
        "validate",
        log_results=results,
        core_data=core_data,
        scal_data=scal_data
    )

    # 6. Check F7 Humility: Uncertainty declared?
    if results.porosity.uncertainty is None or results.saturation.uncertainty is None:
        return GeoxVerdictResult(
            verdict=Verdict.HOLD,
            explanation="F7 Humility: Uncertainty not propagated",
            audit_id="F7-HUMILITY-PETRO-001"
        )

    # 7. APPLY: Cutoff policy
    cutoff_policy = await mcp_call("cutoff_server", "get_policy", basin="Malay_Basin")
    net_pay = apply_cutoffs(results, cutoff_policy)

    # 8. Check F2 Truth: Cutoffs justified?
    if not cutoff_policy.calibration_basis:
        return GeoxVerdictResult(
            verdict=Verdict.HOLD,
            explanation="F2 Truth: Cutoffs not calibrated to local data",
            audit_id="F2-TRUTH-PETRO-001"
        )

    # 9. CALCULATE: Reserves with uncertainty
    reserves = await mcp_call(
        "reserves_server",
        "calculate_ooip",
        area=prospect_area,
        thickness=net_pay,
        porosity=results.porosity,
        saturation=results.saturation,
        method="probabilistic"
    )

    # 10. JUDGE: Human approval for proved reserves
    if reserves.category == "proved":
        return GeoxVerdictResult(
            verdict=Verdict.HOLD,
            explanation="F13 Sovereign: Proved reserves require human signoff",
            audit_id="F13-SOVEREIGN-001",
            reserves=reserves
        )

    # 11. SEAL: All floors passed
    return GeoxVerdictResult(
        verdict=Verdict.SEAL,
        explanation="All constitutional floors passed. Petrophysics SEALED.",
        audit_id="SEAL-PETRO-001",
        results=results,
        reserves=reserves
    )
```

---

## 9. Summary: What Needs to Be Forged

### 9.1 Immediate Priorities (P0)

| Component | File Path | Status | Description |
|-----------|-----------|--------|-------------|
| **Multi-Mineral Solver** | `tools/petrophysics/multimineral_solver.py` | 🔨 FORGE | Simultaneous mineral + porosity solution |
| **Saturation Model Selector** | `physics/saturation_models.py` | 🔨 FORGE | Archie, Simandoux, Indonesia, Dual-Water |
| **Cutoff Policy Manager** | `governance/cutoff_policy.py` | 🔨 FORGE | Explicit, versioned, auditable cutoffs |
| **Uncertainty Propagator** | `tools/petrophysics/uncertainty_propagator.py` | 🔨 FORGE | Monte Carlo through petrophysics |
| **Rock Type Classifier** | `tools/petrophysics/rock_typer.py` | 🔨 FORGE | HFU/FZI/RQI classification |

### 9.2 Medium-Term (P1)

| Component | Description |
|-----------|-------------|
| **NMR Processor** | T2 distribution → porosity, permeability, BVI/FFI |
| **Capillary Integrator** | MICP/log Sw reconciliation |
| **Dielectric Processor** | CDR/CRL for fresh water, unconventional |
| **Image Log Analyzer** | FMI/UBI for fracture aperture, porosity |
| **SCAL Database MCP** | Centralized SCAL search and retrieval |

### 9.3 Long-Term Vision (P2)

| Component | Description |
|-----------|-------------|
| **Real-Time Petrophysics** | LWD-based steering decisions |
| **4D Petrophysics** | Time-lapse saturation monitoring |
| **Unconventional Specialist** | Shale gas/oil, tight gas physics |
| **Carbon Storage Petrophysics** | CO2 plume monitoring, capillary trapping |

---

## 10. The Scientific Manifesto

**What Petrophysics Is:**
1. A measurement science grounded in physics (electromagnetism, nuclear physics, acoustics)
2. An empirical discipline requiring calibration (core, MDT, production)
3. An inverse problem with non-uniqueness that must be acknowledged
4. A decision-support tool where cutoffs are economic, not physical

**What Petrophysics Is NOT:**
1. Magic (despite the black box reputation)
2. Purely empirical (physics constrains the solution space)
3. Deterministic (uncertainty is inherent and must be quantified)
4. Universal (every basin, every field needs calibration)

**GEOX's Role:**
- Make the physics explicit
- Make the assumptions checkable
- Make the uncertainty unavoidable
- Make the decisions auditable
- Make the magic impossible

---

**DITEMPA BUKAN DIBERI — Forged in Physics, Governed by arifOS, Verified by Evidence.**

ΔΩΨ | GEOX v0.6.0-PETRO-FORGE | 999 SEAL PENDING

*Last Updated: 2026-04-07*
*Author: Arif (Sovereign Architect)*
