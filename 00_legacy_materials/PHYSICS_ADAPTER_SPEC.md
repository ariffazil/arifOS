# PHYSICS ADAPTER INTERFACE SPECIFICATION
**Version 1.0 — 2026-04-14**
**Parent doc: GEOX_CONSTITUTIONAL_PHYSICS_STACK.md**
**Sovereign Authority: Muhammad Arif bin Fazil**
**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 0. Purpose

Physics adapters are **thin governed wrappers** around existing physics engines. They do not reimplement the physics — they standardize the interface so that:

1. Engine inputs are validated and typed before submission
2. Engine outputs are captured with explicit uncertainty (P10/P50/P90 or distributions)
3. All metadata required by the GEOX product schema is populated automatically
4. The transform ledger is auto-populated for F9 (anti-hantu) compliance
5. AC_Risk Term 1 (U_phys) is estimated from the engine's own uncertainty output

**Adapters are ~200–500 lines each. They are not simulations. They are governed pipes.**

This document specifies three highest-value adapters:
- `hazard_compute_pga` → OpenQuake Engine
- `hydro_simulate_flow` → MODFLOW 6
- `ccs_plume_simulate` → TOUGH2 / TOUGH+ (or equivalent open solver)

A fourth "skeleton" pattern is provided for extending to new adapters.

---

## 1. Common Adapter Contract

All adapters must conform to this interface contract.

### 1.1 Input Contract

Every adapter accepts an `AdapterRequest` with these mandatory fields:

```typescript
interface AdapterRequest {
  // Identity
  run_id: string;                  // Unique run identifier
  product_type: GEOXProductType;   // Must match the adapter's product type
  basin_context: string;           // Basin / field / region identifier
  crs: string;                     // EPSG code or WKT
  temporal_window: {
    data_from: string;             // ISO8601
    data_to: string;               // ISO8601
  };

  // L0 input sources (must already be QC-stamped)
  l0_sources: L0Source[];          // See GEOX_PRODUCT_VERSIONING.md §1

  // Engine configuration
  engine_config: Record<string, unknown>; // Engine-specific; validated by adapter
  engine_config_file_path: string; // Path to configuration file (for hashing)

  // UQ specification
  uq_method: "monte_carlo" | "logic_tree" | "ensemble" | "none";
  uq_n_samples?: number;           // Required if uq_method = monte_carlo
  uq_logic_tree?: LogicTreeNode[]; // Required if uq_method = logic_tree

  // Sovereign context
  issued_by: { agent: string; kernel: string; sovereign: string };
}
```

### 1.2 Output Contract

Every adapter returns an `AdapterResult` that is pre-formatted for the product schema:

```typescript
interface AdapterResult {
  // Status
  status: "success" | "failed" | "partial";
  error_message?: string;

  // Product schema fields (auto-populated by adapter)
  product_id: string;
  engine: {
    name: string;
    version: string;
    config_hash: string;  // SHA-256 of engine_config_file_path
    run_id: string;
  };
  inputs_hash: string;    // SHA-256 of all L0 source hashes

  // Primary output
  primary_output: {
    metric_name: string;           // e.g., "PGA_475yr", "drawdown_m", "CO2_plume_km2"
    unit: string;                  // SI units
    p10: number;
    p50: number;
    p90: number;
    distribution_file_path?: string; // Path to full distribution (optional)
  };

  // ToAC pre-computation
  u_phys_estimate: number;         // [0.0, 1.0] — adapter computes this from UQ spread
  transform_ledger: TransformStep[]; // Auto-populated by adapter

  // Additional outputs
  supplementary_outputs: Record<string, unknown>; // Engine-specific extras
  warnings: string[];              // Non-fatal issues detected during run
}
```

### 1.3 U_phys Estimation Rule (All Adapters)

Adapters estimate U_phys from the relative width of the uncertainty distribution:

```
coefficient_of_variation = σ(output) / μ(output)
  where σ = standard deviation across MC samples or logic tree
        μ = mean or P50

U_phys = clip(coefficient_of_variation / 2.0, 0.0, 1.0)
```

This is a heuristic. A CoV of 2.0 (200%) maps to U_phys = 1.0 (near-unconstrained). A CoV of 0.2 (20%) maps to U_phys = 0.1 (well-constrained). The TOAC_AC_RISK_SPEC.md §2.4 guide should be used to sanity-check the heuristic estimate.

---

## 2. Adapter 1 — `hazard_compute_pga` (OpenQuake Engine)

### 2.1 Purpose

Computes probabilistic seismic hazard (PSHA) — specifically Peak Ground Acceleration (PGA) at specified return periods — using the OpenQuake Engine. Produces a hazard map with P10/P50/P90 across the logic tree.

### 2.2 Input Fields (Adapter-Specific)

```typescript
interface HazardAdapterConfig extends AdapterRequest {
  product_type: "HAZARD";

  sites: {
    lat: number[];
    lon: number[];
    vs30: number[];         // Shear wave velocity (m/s); required per site
    vs30measured: boolean[];
  };

  seismic_source_model: {
    file_paths: string[];   // .xml source model files (OpenQuake format)
    description: string;
  };

  gmpe_logic_tree: {
    file_path: string;      // OpenQuake logic tree XML
    n_branches: number;     // Number of GMPE branches
  };

  return_periods: number[]; // e.g., [475, 975, 2475] years

  truncation_level: number; // Sigma truncation (typically 3.0)
  investigation_time: number; // Years (typically 50)
  intensity_measure_types: string[]; // e.g., ["PGA", "SA(0.3)", "SA(1.0)"]
}
```

### 2.3 Output Fields (Adapter-Specific)

```typescript
interface HazardAdapterResult extends AdapterResult {
  primary_output: {
    metric_name: "PGA_at_primary_return_period";
    unit: "g";
    p10: number;  // Logic-tree P10 of median hazard
    p50: number;  // Logic-tree median
    p90: number;  // Logic-tree P90
  };

  hazard_curves: {
    site_id: string;
    lat: number;
    lon: number;
    imt: string;
    hazard_values: number[];  // Hazard curve ordinates (annual exceedance probability)
    imls: number[];           // Intensity measure levels
  }[];

  deaggregation: {   // At P50, primary return period
    magnitude_bins: number[];
    distance_bins: number[];
    contribution: number[][];  // Contribution matrix M×R
  } | null;

  gmpe_contributions: {
    branch_id: string;
    weight: number;
    median_pga: number;
  }[];
}
```

### 2.4 Transform Ledger (Auto-populated)

```json
[
  {"step": 1, "operation": "seismic_source_model_load", "format": "OpenQuake XML", "validation": "schema_check"},
  {"step": 2, "operation": "magnitude_frequency_distribution_fit", "method": "Gutenberg-Richter or characteristic"},
  {"step": 3, "operation": "gmpe_evaluation", "n_branches": "<from config>", "sigma_truncation": "<from config>"},
  {"step": 4, "operation": "site_amplification", "vs30_source": "measured or proxy", "model": "Boore2016"},
  {"step": 5, "operation": "hazard_curve_integration", "integration_method": "numerical_poisson"},
  {"step": 6, "operation": "logic_tree_aggregation", "weighting": "branch_weights_from_xml"}
]
```

### 2.5 U_phys Estimation

```
sigma_epistemic = std(P50_per_gmpe_branch)
U_phys = clip(sigma_epistemic / mean_P50 / 2.0, 0.0, 1.0)
```

### 2.6 Mandatory 888_HOLD Triggers

- `return_periods` includes > 2475 years AND output will be used for nuclear / critical infrastructure
- `vs30` is proxy-derived for > 50% of sites (elevated D_transform flag)
- Logic tree has < 3 GMPE branches (flag: QUALIFY ceiling until expanded)

### 2.7 Validation Checks (Pre-run)

- All source model files parse without error against OpenQuake schema
- Vs30 values in valid range (100–3000 m/s)
- Return periods > 0 and ≤ 100,000 years
- At least one L0 source of type `seismic` with qc_flag = "passed"

---

## 3. Adapter 2 — `hydro_simulate_flow` (MODFLOW 6)

### 3.1 Purpose

Runs a governed groundwater flow simulation using MODFLOW 6. Produces aquifer head distributions and drawdown estimates with uncertainty from parameter ensembles (via PEST or Monte Carlo perturbation).

### 3.2 Input Fields (Adapter-Specific)

```typescript
interface HydroAdapterConfig extends AdapterRequest {
  product_type: "HYDRO";

  model_domain: {
    grid_type: "structured" | "unstructured";  // MODFLOW DIS or DISV
    nrow?: number; ncol?: number; nlay: number;
    cell_size_m: number;     // Representative cell size for metadata
    extent_wkt: string;      // WKT polygon of model domain
  };

  parameters: {
    hydraulic_conductivity: {
      zones: number;         // Number of K zones
      prior_min: number; prior_max: number; prior_units: "m/d";
    };
    specific_storage: {
      value_or_range: number | [number, number];
    };
    recharge: {
      method: "uniform" | "zonal" | "spatially_variable";
      rate_m_per_day: number | number[];
    };
  };

  stress_periods: {
    type: "steady_state" | "transient";
    n_periods: number;
    duration_days: number[];
  };

  // UQ via PEST ensemble smoother (preferred) or MC perturbation
  uq_config: {
    method: "PEST_IES" | "monte_carlo_perturbation" | "none";
    n_realizations: number;  // 100–500 recommended
    pest_control_file?: string;
  };

  observation_wells: {
    name: string;
    lat: number; lon: number;
    observed_head_m: number[];
    observation_dates: string[];
  }[];
}
```

### 3.3 Output Fields (Adapter-Specific)

```typescript
interface HydroAdapterResult extends AdapterResult {
  primary_output: {
    metric_name: "drawdown_at_pumping_well_m";
    unit: "m";
    p10: number;
    p50: number;
    p90: number;
  };

  head_distribution: {
    layer: number;
    stress_period: number;
    head_grid_file_path: string;   // NetCDF or ASCII grid
    uncertainty_grid_file_path?: string; // σ of head across realizations
  }[];

  water_budget: {
    stress_period: number;
    inflow_m3_per_day: number;
    outflow_m3_per_day: number;
    storage_change_m3: number;
  }[];

  calibration_summary: {
    rmse_m: number;              // Root mean square error vs. observed heads
    n_observation_wells: number;
    calibration_period: string;
  } | null;

  parameter_uncertainty: {
    parameter: string;
    p10: number; p50: number; p90: number; unit: string;
  }[];
}
```

### 3.4 Transform Ledger (Auto-populated)

```json
[
  {"step": 1, "operation": "grid_construction", "type": "<structured/unstructured>", "cell_size": "<m>"},
  {"step": 2, "operation": "parameter_zonation", "n_k_zones": "<n>", "interpolation": "pilot_points"},
  {"step": 3, "operation": "recharge_assignment", "method": "<uniform/zonal/spatial>"},
  {"step": 4, "operation": "boundary_condition_assignment", "types": ["CHD", "WEL", "DRN"]},
  {"step": 5, "operation": "steady_state_spin_up", "convergence_criterion": "1e-5"},
  {"step": 6, "operation": "transient_simulation", "n_stress_periods": "<n>"},
  {"step": 7, "operation": "uncertainty_ensemble", "method": "<PEST_IES/MC>", "n_realizations": "<n>"}
]
```

### 3.5 U_phys Estimation

```
K_range = p90_K / p10_K   (ratio of high to low hydraulic conductivity)
U_phys = clip(log10(K_range) / 4.0, 0.0, 1.0)
# K ratio of 10,000 → U_phys = 1.0 (very poorly constrained)
# K ratio of 10 → U_phys = 0.25 (moderately constrained)
```

### 3.6 Mandatory 888_HOLD Triggers

- Output used for municipal water supply or public health decision
- Recharge method = "uniform" for coastal aquifer (elevated U_phys automatically)
- RMSE > 0.5 m on calibration wells (product is HOLD until calibration improved)
- Observation well count < 3 for aquifer area > 100 km²

### 3.7 Validation Checks (Pre-run)

- Hydraulic conductivity prior_min > 0
- All observation wells have matching coordinates within model domain
- Stress period durations sum to temporal_window span
- At least one L0 source of type `borehole_log` or aquifer test data with qc_flag = "passed"

---

## 4. Adapter 3 — `ccs_plume_simulate` (TOUGH2 / equivalent)

### 4.1 Purpose

Simulates CO₂ injection and plume migration in a saline aquifer or depleted reservoir using two-phase flow. Produces plume extent, injectivity, and trapping capacity with uncertainty from ensemble of caprock and reservoir property realizations.

### 4.2 Input Fields (Adapter-Specific)

```typescript
interface CCSAdapterConfig extends AdapterRequest {
  product_type: "CCS";

  reservoir: {
    top_depth_m: number;
    thickness_m: { p10: number; p50: number; p90: number };
    porosity: { p10: number; p50: number; p90: number };
    permeability_mD: { horizontal: { p10: number; p50: number; p90: number }; vertical_ratio: number };
    temperature_C: number;
    pressure_MPa: number;
    salinity_ppm: number;
  };

  caprock: {
    thickness_m: { p10: number; p50: number; p90: number };
    permeability_mD: { p10: number; p50: number; p90: number }; // Must be << reservoir
    integrity_assessment: "intact" | "minor_faults_possible" | "faults_present";
  };

  injection: {
    rate_Mt_per_year: number;
    duration_years: number;
    well_count: number;
  };

  simulation: {
    domain_km: [number, number]; // [x, y] extent in km
    grid_resolution_m: number;
    simulation_years: number;   // Total simulation time (injection + post-injection)
    co2_eos: "ECO2N" | "ECO2M" | "custom"; // TOUGH2 equation of state module
  };

  uq_config: {
    n_realizations: number;     // Ensemble of property draws; 50–200 recommended
    sampling_method: "latin_hypercube" | "monte_carlo";
  };
}
```

### 4.3 Output Fields (Adapter-Specific)

```typescript
interface CCSAdapterResult extends AdapterResult {
  primary_output: {
    metric_name: "CO2_plume_area_km2_at_end_of_injection";
    unit: "km2";
    p10: number;
    p50: number;
    p90: number;
  };

  storage_capacity: {
    theoretical_Mt: { p10: number; p50: number; p90: number };
    effective_Mt: { p10: number; p50: number; p90: number }; // After efficiency correction
    efficiency_factor: { p10: number; p50: number; p90: number };
  };

  injectivity: {
    injectivity_index_kg_per_s_per_MPa: { p10: number; p50: number; p90: number };
    bottomhole_pressure_MPa: { max_p50: number };
    fracture_gradient_MPa: number;
    pressure_margin_MPa: number; // fracture_gradient - max_P50 BHP
  };

  trapping_breakdown: {
    time_years: number;
    structural_pct: number;
    residual_pct: number;
    dissolution_pct: number;
    mineral_pct: number;
  }[];

  plume_footprint_files: {
    realization: number;
    time_years: number;
    file_path: string;    // GeoTIFF or shapefile of plume boundary
  }[];

  caprock_integrity: {
    max_overpressure_MPa: { p50: number; p90: number };
    breach_probability_pct: number; // P(overpressure > fracture gradient)
  };
}
```

### 4.4 Transform Ledger (Auto-populated)

```json
[
  {"step": 1, "operation": "reservoir_property_sampling", "method": "<latin_hypercube/mc>", "n": "<n>"},
  {"step": 2, "operation": "co2_eos_parameterization", "module": "<ECO2N/ECO2M>", "T_C": "<T>", "P_MPa": "<P>"},
  {"step": 3, "operation": "grid_construction", "type": "radial_or_cartesian", "resolution_m": "<r>"},
  {"step": 4, "operation": "relative_permeability_curve", "model": "van_Genuchten_or_Brooks_Corey"},
  {"step": 5, "operation": "capillary_pressure_curve", "model": "van_Genuchten"},
  {"step": 6, "operation": "injection_simulation", "duration_yr": "<n>"},
  {"step": 7, "operation": "post_injection_monitoring_simulation", "duration_yr": "<n>"},
  {"step": 8, "operation": "ensemble_aggregation", "n_realizations": "<n>"}
]
```

### 4.5 U_phys Estimation

```
storage_cap_range = p90_storage / p10_storage
U_phys = clip(log10(storage_cap_range) / 3.0, 0.0, 1.0)
# Range of 1000× → U_phys = 1.0
# Range of 10× → U_phys = 0.33
```

### 4.6 Mandatory 888_HOLD Triggers

- `breach_probability_pct` > 5% (caprock integrity concern)
- `pressure_margin_MPa` < 2 MPa (near fracture gradient)
- `caprock.integrity_assessment` = "faults_present"
- Any regulatory filing (F8) — unconditional HOLD requirement
- CCS product depends on HYDRO product that is HOLD or VOID (cross-product rule, see `GEOX_INTERPRODUCT_RISK_RULES.md`)

### 4.7 Validation Checks (Pre-run)

- Caprock permeability < 0.01 mD (else flag warning: caprock may not be sealing)
- Injection pressure < fracture gradient at all realizations
- Simulation domain ≥ 5× expected plume radius at P90
- At least one L0 source of type `borehole_log` with formation pressure test; qc_flag = "passed"

---

## 5. Extension Pattern — New Adapter Skeleton

Use this skeleton to add new adapters without breaking the common contract:

```typescript
// FILE: adapter_{dimension}_{engine}.ts

import { AdapterRequest, AdapterResult } from "./adapter_contract";

interface {Dimension}AdapterConfig extends AdapterRequest {
  product_type: "{DIMENSION}";
  // ... dimension-specific fields ...
}

interface {Dimension}AdapterResult extends AdapterResult {
  primary_output: {
    metric_name: string;
    unit: string;
    p10: number; p50: number; p90: number;
  };
  // ... dimension-specific outputs ...
}

async function {dimension}_simulate_{engine}(
  request: {Dimension}AdapterConfig
): Promise<{Dimension}AdapterResult> {

  // STEP 1: Validate inputs
  validate_l0_sources(request.l0_sources);
  validate_engine_config(request.engine_config);

  // STEP 2: Hash engine config
  const config_hash = sha256(read_file(request.engine_config_file_path));

  // STEP 3: Run engine
  const raw_output = await run_engine(request.engine_config);

  // STEP 4: Extract UQ
  const { p10, p50, p90, cov } = extract_uq(raw_output, request.uq_method);

  // STEP 5: Estimate U_phys
  const u_phys_estimate = clip(cov / 2.0, 0.0, 1.0);

  // STEP 6: Build transform ledger
  const transform_ledger = build_transform_ledger(request);

  // STEP 7: Check hold triggers
  const warnings = check_hold_triggers(raw_output, request);

  // STEP 8: Return AdapterResult
  return {
    status: warnings.some(w => w.startsWith("HOLD")) ? "partial" : "success",
    product_id: generate_product_id("{DIMENSION}", request.basin_context),
    engine: { name: "{ENGINE}", version: get_engine_version(), config_hash, run_id: request.run_id },
    inputs_hash: compute_inputs_hash(request.l0_sources),
    primary_output: { metric_name: "...", unit: "...", p10, p50, p90 },
    u_phys_estimate,
    transform_ledger,
    supplementary_outputs: {},
    warnings
  };
}
```

---

## 6. Adapter Registry

| Adapter Function | Engine | Dimension | Status |
|---|---|---|---|
| `hazard_compute_pga` | OpenQuake 3.x | HAZARD | SPECIFIED ← this doc |
| `hydro_simulate_flow` | MODFLOW 6 | HYDRO | SPECIFIED ← this doc |
| `ccs_plume_simulate` | TOUGH2/TOUGH+ | CCS | SPECIFIED ← this doc |
| `geochem_compute_anomaly` | R/Python (isometric log-ratio) | GEOCHEM | TODO |
| `petroleum_system_mature` | PetroMod (wrapped) | PETROLEUM_SYSTEM | TODO |
| `fracture_build_dfn` | FracMan (wrapped) | FRACTURE | TODO |
| `geothermal_simulate_heat` | TOUGH2-EOS1 | GEOTHERMAL | TODO |
| `mineral_estimate_resource` | GSLIB / Leapfrog export | MINERAL | TODO |
| `structural_build_model` | Move / SKUA export | STRUCTURAL_GEOLOGY | TODO |
| `environmental_simulate_transport` | MODFLOW-MT3D | ENVIRONMENTAL | TODO |
| `shallow_geohazard_slope_stability` | SLOPE/W (wrapped) | SHALLOW_GEOHAZARD | TODO |
| `remote_sensing_classify` | SNAP / ENVI (wrapped) | REMOTE_SENSING | TODO |

---

**DITEMPA BUKAN DIBERI — Adapters are pipes, not oracles. The physics engine is the oracle; governance is what makes it trustworthy.**
