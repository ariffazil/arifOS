# arifOS MCP Tool Namespacing

**Status:** SEALED — Option A. Confirmed by Arif 2026-04-17.
**Epoch:** 2026-04-17
**Author:** Claude Code (drafted for Arif's approval)

---

## Option A — Recommended Architecture

Two distinct caller surfaces. One public API. One internal substrate.

```
External callers (LLMs, agents, integrations)
        ↓
  arifos_* PUBLIC API LAYER
        ↓
  Dispatches to internal axis tools
        ↓
  P_/T_/V_/G_/E_/M_ SUBSTRATE LAYER
        ↓
  World
```

### Rule

> **LLM callers use `arifos_*` names only.**
> **Axis tools (`P_/T_/V_/G_/E_/M_`) are internal routing — never called directly by external agents.**

---

## Public API Layer (`arifos_*`)

These 11 names are the stable, sovereign-facing interface. They do not change when the internal architecture evolves.

| Public Tool | Constitutional Stage | Dispatches To |
|---|---|---|
| `arifos_init` | 000_INIT | `T00_01` arifos_arifos_init |
| `arifos_sense` | 111_SENSE | `T01_16` arifos_arifos_sense |
| `arifos_mind` | 333_MIND | `T07_90` arifos_arifos_mind |
| `arifos_heart` | 666_HEART | `T04_61` arifos_arifos_heart |
| `arifos_judge` | 888_JUDGE | `T00_08` arifos_arifos_judge |
| `arifos_vault` | 999_VAULT | `T00_04` arifos_arifos_vault |
| `arifos_forge` | 777_FORGE | `T05_71` arifos_arifos_forge |
| `arifos_kernel` | 444_KERNEL | `T00_06` arifos_arifos_kernel |
| `arifos_memory` | 000_INIT | `T00_03` arifos_arifos_memory |
| `arifos_ops` | 444_KERNEL | `T00_14` arifos_arifos_ops |
| `arifos_gateway` | 444_KERNEL | `T00_07` arifos_arifos_gateway |

---

## 8 Compound Tools — Live Session Mapping

These 8 tools are exposed in the live session without the `arifos_` prefix. Their canonical names and axis equivalents:

| Live name (current) | Correct public name | Axis equivalent | Registry tier | Status |
|---|---|---|---|---|
| `anchor_session` | `arifos_anchor_session` | `E09_session_anchor` | T00_02 | LIVE |
| `execute_judge` | `arifos_execute_judge` | `G06_execute_judge` | T00_09 | **HOLD** |
| `forge_execute` | `arifos_forge_execute` | `E03_forge_execute` | T05_72 | LIVE |
| `forge_judge_check` | `arifos_forge_judge_check` | `E02_forge_judge_check` | T00_10 | **HOLD** |
| `get_vault_data` | `arifos_get_vault_data` | `P11_vault_ledger_reader` | T00_05 | LIVE |
| `monitor_metabolism` | `arifos_monitor_metabolism` | `M11_metabolic_monitor` | T04_65 | LIVE |
| `perform_economic_audit` | `arifos_perform_economic_audit` | `T11_economic_audit_calculator` | T00_15 | **HOLD** |
| `verify_location` | `arifos_verify_location` | `P09_geospatial_verifier` | T00_13 | **HOLD** |

**Fix required in `agents_66.py`:** Add `arifos_` prefix to the 4 LIVE compound tools. The 4 HOLD tools should be tagged `{"hold", "internal"}` until formally promoted.

---

## Substrate Layer (`P_/T_/V_/G_/E_/M_`)

Internal axis architecture. 66 tools across 6 axes defined in `agents_66.py`. Not exposed to external callers directly.

| Axis | Role | Stage | Tool count |
|---|---|---|---|
| P — Perception | Evidence acquisition | 111_SENSE | ~11 |
| T — Transformation | Compute & synthesis | 333_MIND | ~11 |
| V — Valuation | Economic scoring | 333_MIND | ~9 |
| G — Governance | Constitutional routing | 888_JUDGE | ~8 |
| E — Execution | Forge & dispatch | 777_FORGE | ~9 |
| M — Meta | Self-correction | 333_MIND + 888_JUDGE | ~11 |

---

## What `arifos_route` Was

`arifos_route` was a routing alias for `arifos_kernel`. It was never wired in the live server. It has been removed from `tool_registry.json` as of 2026-04-17. `arifos_kernel` (T00_06) is the canonical routing conductor.

---

## 888-A Hold — Pending Decision

The Option A boundary above is **proposed but not sealed**. Two alternatives exist:

| Option | Description | Trade-off |
|---|---|---|
| **A (recommended)** | `arifos_*` = stable public API; axis tools = internal only | Cleanest separation. External callers never need to know axis names. |
| B | Rename all tools to axis naming, deprecate `arifos_*` | Breaks existing callers. High churn. Not recommended. |
| C | Flat mix — both naming surfaces exposed equally | Causes LLM confusion. Two paths to same verdict. Architecturally weak. |

**Arif resolves this.** When confirmed, remove the "PROPOSED" status from this file and seal with `git commit`.

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
