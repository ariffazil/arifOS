# arifOS MCP Tool Namespacing

**Status:** SEALED — 20-tool surface confirmed. Arif 2026-04-17.
**Epoch:** 2026-04-17

---

## Architecture — 20 Tool Surface

arifOS MCP serves exactly **20 tools** across two layers:

### Layer 1 — Constitutional Core (11 tools)
Each tool owns one stage of the 000-999 pipeline. No aliases. No duplicates.

| Public Tool | Stage | Role |
|---|---|---|
| `arifos_init` | 000_INIT | Session anchor + epoch |
| `arifos_sense` | 111_SENSE | Reality grounding (+ `location` mode) |
| `arifos_mind` | 333_MIND | Constitutional reasoning |
| `arifos_kernel` | 444_ROUT | Metabolic lane routing |
| `arifos_heart` | 666_HEART | Adversarial ethics critique |
| `arifos_ops` | 777_OPS | Cost + thermodynamics (+ `economic_audit`, `metabolism`) |
| `arifos_judge` | 888_JUDGE | Constitutional verdict |
| `arifos_memory` | 555_MEM | Vector store + context |
| `arifos_vault` | 999_SEAL | Immutable ledger (+ `read` mode) |
| `arifos_forge` | EXECUTION | Delegated execution bridge |
| `arifos_gateway` | ORTHO | Ω_ortho ≥ 0.95 enforcement |

### Layer 2 — Perception Oracles (9 P_* tools)
Domain interfaces. No equivalent in constitutional core. Legitimate organ boundaries.

| Oracle | Domain |
|---|---|
| `P_well_state_read` | Biological telemetry |
| `P_well_readiness_check` | Biological readiness verdict |
| `P_well_floor_scan` | W-Floor status |
| `P_geox_scene_load` | Seismic/well/volume |
| `P_geox_skills_query` | GEOX skill registry |
| `P_wealth_snapshot_fetch` | Macro/energy/carbon snapshot |
| `P_wealth_series_fetch` | Live series (FRED/ALFRED) |
| `P_wealth_vintage_fetch` | Vintage series |
| `P_vault_ledger_read` | VAULT999 ledger read |

---

## Naming Rules

> **LLM callers use `arifos_*` (Layer 1) or `P_*` (Layer 2) names only.**
> **T_/V_/G_/E_/M_ tools are internal substrate — never called directly.**

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
