---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
audience:
- engineers
difficulty: intermediate
prerequisites:
- MCP_Tools
tags:
- architecture
- tools
- contracts
- generation
- compatibility
- drift
sources:
- APEX/ASF1/tool_registry.json
- tool_specs.py
- tools.py
- tools_hardened_dispatch.py
- __main__.py
- server.py
- rest_routes.py
- resources.py
- public_registry.py
- wiki/raw/mcp_naming_migration_audit_directive_2026-04-11.md
last_sync: '2026-04-11'
confidence: 0.95
---

# Tool Surface Architecture

The arifOS tool surface currently has **two competing truths**:

1. the **registry target** in `APEX/ASF1/tool_registry.json`
2. the **runtime-exported surface** still assembled from `arifosmcp/runtime/tool_specs.py`, `tools.py`, `public_registry.py`, and `server.py`

That makes this page a **contrast architecture** page, not a seal page.

## Registry Target (Current Canon Candidate)

| Tool | Stage | Layer | Notes |
| :--- | :--- | :--- | :--- |
| `arifos_init` | 000 | GOVERNANCE | Session anchoring |
| `arifos_sense` | 111 | MACHINE | Reality grounding |
| `arifos_mind` | 333 | INTELLIGENCE | Structured reasoning |
| `arifos_kernel` | 444 | GOVERNANCE | Primary conductor |
| `arifos_memory` | 555 | INTELLIGENCE | Vector memory recall |
| `arifos_heart` | 666 | INTELLIGENCE | Safety & empathy critique |
| `arifos_ops` | 777 | MACHINE | Thermodynamic estimation |
| `arifos_judge` | 888 | GOVERNANCE | Final constitutional verdict |
| `arifos_vault` | 999 | GOVERNANCE | Immutable audit ledger |
| `arifos_forge` | 010 | EXECUTION | A-FORGE execution bridge |

Everything outside this 10-tool public set should be classified explicitly as:

- alias
- internal-only
- deprecated
- dead code
- substrate mode
- unresolved ambiguity

## Current Surface Layers

### 1. Canonical Contract

- `APEX/ASF1/tool_registry.json`
- `arifosmcp/runtime/tool_specs.py`
- The registry defines the desired public/internal split.
- The runtime spec still defines the callable/exported tuple.

### 2. Runtime Execution Surface

- `arifosmcp/runtime/tools.py`
- `arifosmcp/runtime/__main__.py`
- `arifosmcp/runtime/kernel_router.py`
- These files still preserve older symbols such as `arifos_route`, `arifos_reply`, and `arifos_vps_monitor`.

### 3. Compatibility Surface

- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `arifosmcp/runtime/megaTools/__init__.py`
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`
- These files preserve older names or route legacy flows into the canonical runtime.

### 4. Transport / Registry Surface

- `arifosmcp/runtime/server.py`
- `arifosmcp/runtime/rest_routes.py`
- `arifosmcp/runtime/resources.py`
- `arifosmcp/runtime/public_registry.py`
- These files expose tool names to REST, MCP, discovery manifests, or resource documents.

### 5. Wiki / Narrative Surface

- `wiki/pages/MCP_Tools.md`
- `wiki/index.md`
- audit and concept pages that describe the tool surface

## Contrast Evidence (2026-04-11)

| Layer | Evidence | Meaning |
| :--- | :--- | :--- |
| Registry | `APEX/ASF1/tool_registry.json` defines 10 public tools + 5 internal folded tools | Canon target is reduced public surface |
| Runtime spec | `arifosmcp/runtime/tool_specs.py` exports `PUBLIC_TOOL_SPECS = TOOLS` | Public runtime still follows broad tuple, not the registry split |
| Discovery registry | `arifosmcp/runtime/public_registry.py` sets `EXPECTED_TOOL_COUNT = 11` | Discovery still expects pre-migration count |
| Server narrative | `arifosmcp/runtime/server.py` says public tools use canonical dotted ids and mentions `arifos_reply` | Transport docs still leak older naming/surface assumptions |
| Runtime handlers | `arifosmcp/runtime/tools.py` keeps handlers and aliases for `arifos_reply`, `arifos_vps_monitor`, `arifos_route`, and dotted names | Compatibility still exists inside live code path candidates |

## Structural Law

The stable target architecture remains:

`registry canon` → `runtime handlers / compatibility adapter` → `transport discovery surfaces` → `wiki inventory`

The migration is not seal-ready until these layers agree on the same public surface.

## Proposed Doctrine (Target, Not Proven Runtime)

The most coherent long-term model is **Machine Governance Intelligence 3x3 + 1**:

| Stage / Lane | Reality | Intelligence | Governance |
|--------------|---------|--------------|------------|
| Ingest | `arifos_init` | `arifos_memory` | `arifos_sense` |
| Deliberate | `arifos_ops` | `arifos_mind` | `arifos_heart` |
| Act | `arifos_forge` | `arifos_kernel` | `arifos_judge` |

Plus one sovereign boundary:

- `arifos_vault`

This is a useful organizing doctrine, but it should remain **proposed architecture** until the audit proves current-state truth and the runtime actually matches it.

## Proposed Next Action

Before any redesign:

1. run one master audit across registry, runtime, reachability, deployment, and client discovery
2. classify every non-canonical surface
3. only then decide whether to fold or remove legacy paths

## 888_HOLD

The following are governance-sensitive and should not be deleted in this pass:

- legacy mega-tool namespace
- dotted-name compatibility paths
- old registry manifests consumed by unknown clients

They should first be isolated, audited, and covered by rollback + equivalence evidence.
