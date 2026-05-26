# RESOURCE_INVENTORY.md — arifOS MCP Resource Audit
**Generated:** 2026-05-25
**Phase:** PHASE 1 — Resource Inventory
**Target:** 18 canonical read-only resources (4K + 4G + 4W + 4Wl + 2A)

---

## Resource Definition

A resource is **read-only** if:
- No `mutates_state: true`
- No filesystem write side effects
- No external API mutation
- No vault/memory write

---

## CURRENT State (arifos_mcp/resources/)

| Resource Path | Exists? | Read-Only? | Content | Status |
|---|---|---|---|---|
| `session/embodiment.md` | ? | ? | embodiment card template | UNKNOWN |
| `session/constitution.md` | ? | ? | F1-F13 text | UNKNOWN |
| `static/tool-registry.json` | ? | ? | tool list | UNKNOWN |
| `templates/response-envelope.md` | ? | ? | envelope schema | UNKNOWN |

**Current count:** ~4 (partial/uncertain)
**Target:** 18

---

## TARGET: 18 Canonical Resources (PHOENIX-72)

### KERNEL Resources (4)

| ID | Resource URI | Purpose | Floors | Status |
|---|---|---|---|---|
| K-1 | `arif://kernel/constitution` | F01-F13 full text | F01-F13 | PLANNED |
| K-2 | `arif://kernel/embodiment` | Tool surface, model registry, risk leash | F01,F11,F12 | PLANNED |
| K-3 | `arif://kernel/verdict-protocol` | When to issue SEAL/PARTIAL/SABAR/HOLD/VOID | F11,F13 | PLANNED |
| K-4 | `arif://kernel/memory-architecture` | L1-L6 memory layer contracts | F01,F08 | PLANNED |

### GEOX Resources (4)

| ID | Resource URI | Purpose | Floors | Status |
|---|---|---|---|---|
| G-1 | `geox://doctrine/physics9` | Physical constraint axioms for earth reasoning | F02 | PLANNED |
| G-2 | `geox://schemas/geoscience-io` | LAS, SEG-Y, CSV schema references | F02 | PLANNED |
| G-3 | `geox://registry/datasets` | Available geological datasets + quality | F02,F04 | PLANNED |
| G-4 | `geox://doctrine/stratigraphy-model` | L1-L3 stratigraphic interpretation protocol | F02 | PLANNED |

### WEALTH Resources (4)

| ID | Resource URI | Purpose | Floors | Status |
|---|---|---|---|---|
| W-1 | `wealth://doctrine/valuation` | NPV/IRR/EMV calculation doctrine | F05,F06 | PLANNED |
| W-2 | `wealth://formulas/finance-core` | Core financial formulas + units | F05 | PLANNED |
| W-3 | `wealth://schemas/deal-and-capital` | Deal structure, capital allocation schemas | F05,F06 | PLANNED |
| W-4 | `wealth://doctrine/risk-taxonomy` | C1-C5 risk classification framework | F05,F06,F11 | PLANNED |

### WELL Resources (4)

| ID | Resource URI | Purpose | Floors | Status |
|---|---|---|---|---|
| WL-1 | `well://vitality/current` | Current operator vitality snapshot | F05,F06 | PLANNED |
| WL-2 | `well://doctrine/substrate-boundary` | H-WELL/M-WELL/C-WELL/G-WELL boundary doctrine | F05,F06,F10 | PLANNED |
| WL-3 | `well://calibration/thresholds` | Homeostasis thresholds, fatigue markers | F05,F06 | PLANNED |
| WL-4 | `well://schemas/vitality-io` | Vitality input/output schema | F05,F06 | PLANNED |

### AAA Resources (2)

| ID | Resource URI | Purpose | Floors | Status |
|---|---|---|---|---|
| A-1 | `aaa://registry/agent-identities` | Agent ID registry (Hermes, OpenClaw, etc.) | F01,F11 | PLANNED |
| A-2 | `aaa://doctrine/a2a-protocol` | Agent-to-Agent communication protocol | F01,F03 | PLANNED |

---

## PHOENIX72_GAP_MATRIX — Tools

| Tool Name | Organ | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|---|---|---|---|---|---|---|---|---|---|
| mcp_health_check | Gateway | yes | stub | yes | partial | yes | partial | no | NOT ALIVE |
| mcp_drift_check | Gateway | yes | stub | yes | partial | yes | partial | no | NOT ALIVE |
| arif_session_init | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_sense_observe | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_evidence_fetch | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_mind_reason | Kernel | yes | PARTIAL* | yes | yes | yes | partial | no | PARTIAL |
| arif_heart_critique | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_reply_compose | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_kernel_route | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_memory_recall | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_gateway_connect | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_judge_deliberate | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_vault_seal | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_forge_execute | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_ops_measure | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_wiki_ingest | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_wiki_map | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_wiki_search | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_wiki_ask | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_stack_health_probe | Kernel | yes | REAL | yes | yes | yes | yes | no | ALIVE |
| arif_organ_consensus | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_scan_local_instructions | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| arif_session_budget | Kernel | yes | stub | yes | yes | yes | partial | no | NOT ALIVE |
| geox_data_ingest_bundle | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_data_qc_bundle | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_dst_ingest_test | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_evidence_reason | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_map_context_scene | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_seismic_compute | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_sequence_interpret | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_subsurface_generate_candidates | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_subsurface_verify_integrity | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_prospect_evaluate | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| geox_system_registry_status | GEOX | yes | STUB | no | partial | yes | no | no | NOT ALIVE |
| wealth_* (32 tools) | WEALTH | yes | STUB | no | partial | partial | no | no | NOT ALIVE |
| well_* (14 tools) | WELL | yes | STUB | no | partial | partial | no | no | NOT ALIVE |

*arif_mind_reason: code exists but VOID due to /home/arifos permission error

**Summary:**
- ALIVE: 1 (arif_stack_health_probe)
- PARTIAL: 1 (arif_mind_reason)
- NOT ALIVE: 70 (all stubs, organs unreachable)
- GEOX/WEALTH/WELL: 57 tools, 0 alive, all need organ proxy

---

*DITEMPA BUKAN DIBERI — 18 resources planned, 0 implemented*
