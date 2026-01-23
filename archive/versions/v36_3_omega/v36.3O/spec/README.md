# v36.3O Spec Layer

**Epoch:** v36.3Omega (v36.3O)
**Status:** SEALED
**Last Updated:** 2025-12-12

## Purpose

This directory contains the **Spec Layer** (Track B) of arifOS v36.3Omega:
- Machine-readable specifications (JSON, YAML)
- Derived from canon bridges, consumed by runtime code

**Pipeline:** Canon (Law) -> Spec (Contract) -> Code (Implementation)

Specs implement canon without changing it. They are mutable for tuning, but canon is frozen.

## Core Specs (8)

| Spec File | Implements | Purpose |
|-----------|------------|---------|
| `measurement_floors_v36.3O.json` | MEASUREMENT_APEX_STANDARDS | F1-F9 floor definitions, thresholds, types |
| `measurement_aggregates_v36.3O.json` | MEASUREMENT_APEX_STANDARDS | Delta/Omega/Psi aggregates, derived metrics |
| `apex_prime_telemetry_v36.3O.json` | JUDICIARY_APEX_PRIME | Telemetry entry schema, CCE audits |
| `trinity_aaa_spec_v36.3O.yaml` | TRINITY_AAA_ENGINES | Engine roles, packets, floor ownership |
| `waw_federation_spec_v36.3O.yaml` | OVERSIGHT_WAW_FEDERATION | 5 organs, veto hierarchy, signals |
| `paradox_777_schema_v36.3O.json` | PARADOX_777_CUBE | Cube geometry, layers, Crown Equation |
| `vault999_ledger_schema_v36.3O.json` | CCC_ARCHITECTURE | L0-L4 layer schemas, integrity |
| `dreamforge_otask_spec_v36.3O.yaml` | DREAMFORGE_ARCHITECTURE | O-TASK cadence, OreType, safety |

## Additional Specs (7)

| Spec File | Implements | Purpose |
|-----------|------------|---------|
| `vault999_final_seal_spec_v36.3O.json` | 062_CCC_FINAL_SEAL_PROTOCOL | Final Seal requirements, workflow |
| `llm_governance_spec_v36.3O.yaml` | 050/051_METABOLIZER_LOOP | LLM roles, packets, constraints |
| `memory_context_spec_v36.3O.json` | ARIFOS_MEMORY_STACK | Six-band MemoryContext schema |
| `cooling_ledger_entry_spec_v36.3O.json` | COOLING_LEDGER_INTEGRITY | L1 entry schema (JSONL) |
| `phoenix72_amendment_spec_v36.3O.json` | VAULT_999_AMENDMENTS | Amendment record schema |
| `scar_record_spec_v36.3O.json` | SCARS_PHOENIX_HEALING | Scar/witness record schema |
| `eureka_receipt_spec_v36.3O.json` | CCC_ARCHITECTURE (L4) | zkPC receipt schema |

## Spec Details

### measurement_floors_v36.3O.json
- **F1-F9 definitions** with thresholds, types (hard/soft), domains
- **Hard floors (7):** F1, F2, F5, F6, F7, F8, F9 -> VOID on fail
- **Soft floors (2):** F3, F4 -> PARTIAL on fail

### measurement_aggregates_v36.3O.json
- **Delta_metric:** Clarity aggregate (Truth + DeltaS)
- **Omega_metric:** Stability aggregate (Peace^2 + kappa_r + Omega_0 + RASA)
- **Psi_metric:** Vitality aggregate (Amanah + Tri-Witness + Anti-Hantu)
- **Derived metrics:** G, C_dark, Psi_APEX
- **Verdict codes:** SEAL, PARTIAL, HOLD_888, SABAR, VOID

### trinity_aaa_spec_v36.3O.yaml
- **ARIF (Delta):** F1, F2 ownership; cold logic engine
- **ADAM (Omega):** F3, F4, F5, F7 ownership; warm logic engine
- **APEX (Psi):** F6, F8, F9 ownership; judiciary engine
- **Routing:** CLASS_A (fast), CLASS_B (full)

### vault999_final_seal_spec_v36.3O.json
- **Requirements:** verdict, floors, Tri-Witness, hash chain
- **Workflow:** 888_JUDGE -> 999_SEAL -> L1 -> Merkle -> zkPC
- **Invariants:** I1-I6 (chain integrity, signatures, forbidden content)

## HOTSPOTS (Known Drift)

| ID | Issue | Spec Location |
|----|-------|---------------|
| HS-005 | G threshold drift | `measurement_aggregates_v36.3O.json` - canonical 0.70 vs runtime 0.80 |
| HS-006 | F5 ownership | `trinity_aaa_spec_v36.3O.yaml` - moved from ARIF to ADAM |

See `v36.3O/canon/CANON_MAP_v36.3O.md` PARADOX_HOTSPOTS for full list.

## Usage

```python
import json
import yaml

# Load floor definitions
with open('v36.3O/spec/measurement_floors_v36.3O.json') as f:
    floors = json.load(f)

# Load AAA spec
with open('v36.3O/spec/trinity_aaa_spec_v36.3O.yaml') as f:
    aaa = yaml.safe_load(f)

# Check floor threshold
truth_threshold = floors['floors']['F1']['threshold']  # 0.99
```

## Related Directories

- `v36.3O/canon/` - Law layer (authoritative source)
- `arifos_core/` - Runtime implementation
- `tests/` - Test coverage

## Versioning

Each spec file contains a `meta` block:
```json
{
  "meta": {
    "spec_id": "<name>_v36.3O",
    "epoch": "v36.3Omega",
    "implements": "<bridge_file>",
    "law_source": "<physics_bridge>",
    "law_commit": "<commit_hash>"
  }
}
```

This enables traceability from spec -> bridge -> canon source.

---

**Spec implements law. Code implements spec. Law is frozen.**

