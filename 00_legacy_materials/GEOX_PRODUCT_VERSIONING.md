# GEOX PRODUCT VERSIONING SCHEMA
**Version 1.0 — 2026-04-14**
**Parent doc: GEOX_CONSTITUTIONAL_PHYSICS_STACK.md**
**Sovereign Authority: Muhammad Arif bin Fazil**
**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 0. Purpose

Every GEOX canonical product is a **governed, versioned, replayable object**. This document defines the minimal schema all 12 canonical products must carry, the versioning rules, the binding to the arifOS vault (Merkle chain), and the audit replay contract.

A product without this schema **cannot be SEAL**. It may exist as a working artifact; it cannot be a governed output.

---

## 1. Core Product Schema

All 12 canonical GEOX products share this schema. Fields marked `REQUIRED` must be present for any verdict beyond VOID. Fields marked `CONDITIONAL` are required when the specified condition holds.

```json
{
  "product_id": "REQUIRED — globally unique identifier",
  "product_type": "REQUIRED — one of: HAZARD | HYDRO | CCS | GEOCHEM | PETROLEUM_SYSTEM | FRACTURE | GEOTHERMAL | MINERAL | STRUCTURAL_GEOLOGY | ENVIRONMENTAL | SHALLOW_GEOHAZARD | REMOTE_SENSING",
  "version": "REQUIRED — semver string: MAJOR.MINOR.PATCH (e.g., 1.3.0)",
  "version_reason": "REQUIRED — brief human-readable reason for this version (e.g., 'Added 3 new boreholes; K updated')",
  "parent_version": "CONDITIONAL — product_id of the version this supersedes (null if v1.0.0)",

  "dimension": "REQUIRED — named dimension from GEOX_CONSTITUTIONAL_PHYSICS_STACK.md §6",
  "basin_context": "REQUIRED — geographic / basin identifier (e.g., 'Malay Basin, Offshore Block PM3')",
  "crs": "REQUIRED — coordinate reference system (EPSG code or WKT string)",
  "temporal_window": {
    "data_from": "REQUIRED — ISO8601 date of oldest input data used",
    "data_to": "REQUIRED — ISO8601 date of newest input data used",
    "valid_until": "CONDITIONAL — expiry date if time-limited (e.g., aquifer licence period)"
  },

  "engine": {
    "name": "REQUIRED — physics engine name (e.g., 'OpenQuake 3.19', 'MODFLOW 6.4', 'TOUGH2 v2')",
    "version": "REQUIRED — engine version string",
    "config_hash": "REQUIRED — SHA-256 of engine configuration / input files",
    "run_id": "REQUIRED — engine run identifier for traceability"
  },

  "inputs": {
    "l0_sources": [
      {
        "source_id": "REQUIRED — identifier or URI for this L0 dataset",
        "type": "REQUIRED — one of: seismic | borehole_log | geochemical_sample | satellite_imagery | InSAR | gravity | MT | CPT | report",
        "acquisition_date": "REQUIRED — ISO8601",
        "provider": "REQUIRED — data provider institution / agency",
        "qc_flag": "REQUIRED — one of: passed | flagged | unverified",
        "hash": "REQUIRED — SHA-256 of the input file(s)"
      }
    ],
    "inputs_hash": "REQUIRED — SHA-256 of the concatenated hashes of all l0_sources"
  },

  "uq_summary": {
    "method": "REQUIRED — one of: monte_carlo | logic_tree | bootstrap | geostatistical_simulation | ensemble | expert_elicitation | not_computed",
    "p10": "CONDITIONAL — P10 value of primary output metric (required if method != not_computed)",
    "p50": "CONDITIONAL — P50 value of primary output metric",
    "p90": "CONDITIONAL — P90 value of primary output metric",
    "distribution_file": "CONDITIONAL — URI to full distribution output if available",
    "uq_note": "REQUIRED if method = not_computed — explicit justification for absence of UQ"
  },

  "toac": {
    "u_phys": "REQUIRED — float [0.0, 1.0]",
    "d_transform": "REQUIRED — float [0.0, 1.0]",
    "b_cog": "REQUIRED — float [0.0, 1.0]",
    "ac_risk": "REQUIRED — float [0.0, 1.0] = u_phys × d_transform × b_cog",
    "transform_ledger": "REQUIRED — ordered list of transform steps (see TOAC_AC_RISK_SPEC.md §3.2)",
    "anti_hantu_statement": "CONDITIONAL — required if d_transform > 0.6 (see TOAC_AC_RISK_SPEC.md §9)"
  },

  "verdict": "REQUIRED — one of: SEAL | QUALIFY | HOLD | VOID",
  "floor_flags": {
    "f2_truth": "REQUIRED — boolean: all material claims evidence-grounded",
    "f4_clarity": "REQUIRED — boolean: units, CRS, scale explicit",
    "f6_water": "CONDITIONAL — boolean: required for HYDRO and ENVIRONMENTAL",
    "f7_humility": "REQUIRED — boolean: uncertainty explicitly stated",
    "f8_regulatory": "CONDITIONAL — boolean: required if verdict used for regulatory filing",
    "f9_anti_hantu": "REQUIRED — boolean: transform ledger complete",
    "f13_sovereign": "REQUIRED — boolean: human veto live"
  },

  "hold_gate": {
    "triggered": "REQUIRED — boolean",
    "trigger_reason": "CONDITIONAL — required if triggered = true",
    "resolved_by": "CONDITIONAL — identity of human who resolved the hold gate",
    "resolution_timestamp": "CONDITIONAL — ISO8601",
    "resolution_decision": "CONDITIONAL — one of: approved | rejected | revised"
  },

  "issued_by": "REQUIRED — identity chain: {agent: 'GEOX', kernel: 'arifOS', sovereign: 'arif'}",
  "timestamp": "REQUIRED — ISO8601 datetime of product issuance",
  "vault_hash": "CONDITIONAL — Merkle hash issued by arifOS vault after SEAL (null until vaulted)",
  "superseded_by": "CONDITIONAL — product_id of the version that supersedes this one (null if current)"
}
```

---

## 2. Product ID Convention

Product IDs must be globally unique and human-parseable:

```
{DIMENSION}-{BASIN_CODE}-{YEAR}-{MAJOR_VERSION}-{UUID4_SHORT}

Example:
  HAZARD-MALAY-2026-V1-a3f9c1
  HYDRO-SEPAT-2025-V2-88bc04
  CCS-BESAR-2026-V1-c7d221
```

- **DIMENSION**: uppercase dimension name from the registry
- **BASIN_CODE**: short code for basin or field (max 8 chars, alphanumeric)
- **YEAR**: 4-digit year of first issuance
- **MAJOR_VERSION**: V1, V2, ... (incremented on data or engine change)
- **UUID4_SHORT**: first 6 chars of a UUID4 (collision avoidance)

---

## 3. Versioning Rules

### 3.1 When to increment MAJOR version (e.g., 1.0.0 → 2.0.0)

- New L0 data added that changes the physical interpretation
- Engine upgraded to a new major version
- Basin geological model structurally revised
- Prior product was VOID or HOLD that has now been resolved

### 3.2 When to increment MINOR version (e.g., 1.0.0 → 1.1.0)

- Processing parameters tuned (grid resolution, search radius)
- Additional UQ scenarios added without new raw data
- ToAC scores revised after calibration event
- Floor flag status changed (e.g., F8 review now complete)

### 3.3 When to increment PATCH version (e.g., 1.0.0 → 1.0.1)

- Metadata correction (CRS string, date typo, provider name)
- Transform ledger annotation added
- Anti-hantu statement appended

### 3.4 Immutability rule

Once a product has been **SEAL**-vaulted (vault_hash present), its content is immutable. Only PATCH increments are permitted on vaulted products, and only for metadata. Any content change requires a new MINOR or MAJOR version.

---

## 4. Vault Binding (Merkle Chain)

Every product that achieves SEAL verdict must be committed to the arifOS vault:

```
PRODUCT_OBJECT → SHA-256 hash → submitted to arifOS vault tool
                                ↓
                        vault issues Merkle hash
                                ↓
                        vault_hash written back to product schema
                                ↓
                        product is now tamper-evident and replayable
```

The vault commitment chain means:
- Any modification of a vaulted product is **detectable** (hash mismatch)
- Any disputes about what was asserted at time of decision can be resolved by replaying the product
- Audit trails for regulatory submissions (F8) are permanently available

---

## 5. Replayability Contract

A product with vault_hash MUST be fully replayable. This means:

1. All L0 input files are archived (or URIs are durable and access-controlled)
2. Engine configuration (config_hash) is stored alongside the product
3. The transform ledger fully documents every processing step
4. The UQ method and parameters are sufficient to re-run the uncertainty analysis
5. The ToAC scores are justifiable from the evidence in the product schema without external memory

GEOX does not guarantee physical reproducibility (engines may behave non-deterministically), but guarantees **audit reproducibility**: a reviewer with the schema can reconstruct the reasoning chain used to issue the verdict.

---

## 6. Product Lifecycle

```
DRAFT
  ↓ (L0 data loaded, engine run, UQ computed)
CANDIDATE
  ↓ (ToAC scored; AC_Risk computed; floor flags checked)
  ├── if VOID → archived with VOID status; no further steps
  ├── if HOLD → 888_HOLD gate opened; awaits human resolution
  │     ↓ (human resolves: approved / rejected / revised)
  │     └── if revised → back to CANDIDATE
  └── if SEAL or QUALIFY
        ↓ (vault committed; vault_hash issued)
SEALED
  ↓ (new data arrives or calibration event triggers)
SUPERSEDED (superseded_by = new product_id)
```

Dead states: VOID and SUPERSEDED products are retained for audit but must not be used for new decisions without explicit sovereign override.

---

## 7. Minimal Product Object — Example (HYDRO)

```json
{
  "product_id": "HYDRO-ANGSI-2025-V1-88bc04",
  "product_type": "HYDRO",
  "version": "1.0.0",
  "version_reason": "Initial governed product from 2025 aquifer study",
  "parent_version": null,
  "dimension": "HYDRO",
  "basin_context": "Angsi Field aquifer, Malay Basin, Malaysia",
  "crs": "EPSG:32647",
  "temporal_window": {
    "data_from": "2018-01-01",
    "data_to": "2025-06-30",
    "valid_until": "2030-12-31"
  },
  "engine": {
    "name": "MODFLOW 6",
    "version": "6.4.2",
    "config_hash": "d8f3a1c7...sha256...",
    "run_id": "MF6-ANGSI-20250701-001"
  },
  "inputs": {
    "l0_sources": [
      {
        "source_id": "BH-ANGSI-001-LAS",
        "type": "borehole_log",
        "acquisition_date": "2020-03-15",
        "provider": "COMPANY Geoscience Division",
        "qc_flag": "passed",
        "hash": "a1b2c3...sha256..."
      }
    ],
    "inputs_hash": "f9e8d7...sha256..."
  },
  "uq_summary": {
    "method": "monte_carlo",
    "p10": 1200,
    "p50": 2100,
    "p90": 3800,
    "distribution_file": "vault://HYDRO-ANGSI-2025/mc_drawdown_dist.nc",
    "uq_note": null
  },
  "toac": {
    "u_phys": 0.48,
    "d_transform": 0.28,
    "b_cog": 0.22,
    "ac_risk": 0.030,
    "transform_ledger": [
      {"step": 1, "operation": "pilot_point_interpolation", "code": "PEST 17.5", "params": {"n_pilots": 45}},
      {"step": 2, "operation": "boundary_condition_assignment", "type": "constant_head", "source": "regional_model"}
    ],
    "anti_hantu_statement": null
  },
  "verdict": "QUALIFY",
  "floor_flags": {
    "f2_truth": true,
    "f4_clarity": true,
    "f6_water": true,
    "f7_humility": true,
    "f8_regulatory": false,
    "f9_anti_hantu": true,
    "f13_sovereign": true
  },
  "hold_gate": {
    "triggered": false,
    "trigger_reason": null,
    "resolved_by": null,
    "resolution_timestamp": null,
    "resolution_decision": null
  },
  "issued_by": {"agent": "GEOX", "kernel": "arifOS", "sovereign": "arif"},
  "timestamp": "2025-07-01T09:30:00Z",
  "vault_hash": null,
  "superseded_by": null
}
```

---

**DITEMPA BUKAN DIBERI — Every product is a governed object, not a file.**
