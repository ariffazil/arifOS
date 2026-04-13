---
type: Concept
tier: 20_RUNTIME
strand:
- tools
audience:
- engineers
difficulty: intermediate
prerequisites:
- Metabolic_Loop
tags:
- mcp
- tools
- substrate
- execution
- migration
- audit
sources:
- APEX/ASF1/tool_registry.json
- tool_specs.py
- public_registry.py
- tools.py
- server.py
last_sync: '2026-04-11'
confidence: 0.92
---

# MCP Tool Surface

The arifOS MCP tool surface is in a **migration contrast** state.

The current registry target is a clean **10-tool public canon**, but the repo runtime still contains transitional surfaces that must be audited before the naming migration can be sealed.

## Canonical Public Target (Registry)

| Tool | Stage | Layer | Purpose |
| :--- | :--- | :--- | :--- |
| `arifos_init` | 000 | GOVERNANCE | Start governed session & bind identity. |
| `arifos_sense` | 111 | MACHINE | Constitutional reality sensing & grounding. |
| `arifos_mind` | 333 | INTELLIGENCE | Structured reasoning & multi-source synthesis. |
| `arifos_kernel` | 444 | GOVERNANCE | Execution lane selection & metabolic routing. |
| `arifos_memory` | 555 | INTELLIGENCE | Governed memory recall from vector store. |
| `arifos_heart` | 666 | INTELLIGENCE | Safety, dignity, & adversarial critique. |
| `arifos_ops` | 777 | MACHINE | Cost, thermodynamic, & capacity estimation. |
| `arifos_judge` | 888 | GOVERNANCE | Final constitutional verdict engine. |
| `arifos_vault` | 999 | GOVERNANCE | Immutable verdict logging to VAULT999. |
| `arifos_forge` | 010 | EXECUTION | Delegated execution to AF-FORGE substrate. |

**Source of target truth**: `APEX/ASF1/tool_registry.json`

## Transitional / Compatibility Surface Still Present in Repo

| Surface | Current Repo Role | Evidence |
| :--- | :--- | :--- |
| `arifos_reply` | internal composite/orchestrator still defined | `arifosmcp/runtime/tool_specs.py`, `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/server.py` |
| `arifos_vps_monitor` | legacy/internal telemetry surface still referenced | `arifosmcp/runtime/tool_specs.py`, `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/resources.py` |
| `arifos_route` | compatibility alias / old 444 symbol still referenced | `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/kernel_runtime.py`, `arifosmcp/runtime/server.py` |
| `arifos_repo_read` | Git bridge for reading repository state | `arifosmcp/runtime/tools.py`, `arifosmcp/integrations/git_bridge.py` |
| `arifos_repo_seal` | Git bridge for sealing commits and state | `arifosmcp/runtime/tools.py`, `arifosmcp/integrations/git_bridge.py` |
| `arifos_health` | System health endpoint for readiness checks | `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/server.py` |
| `arifos_fetch` | Grounding bridge for external content retrieval | `arifosmcp/runtime/tools.py`, `arifosmcp/tools/fetch_tool.py` |
| `arifos_forge_bridge`| Internal bridge to delegated execution substrate | `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/forge_bridge.py` |
| dotted `arifos.*` names | legacy alias surface still active | `arifosmcp/runtime/tools.py`, `arifosmcp/runtime/kernel_router.py`, `arifosmcp/runtime/server.py` |

## Current Contrast

The repository currently shows all of the following at once:

1. `APEX/ASF1/tool_registry.json` defines **10 public canonical tools** and **5 internal folded tools**.
2. `arifosmcp/runtime/tool_specs.py` exports `PUBLIC_TOOL_SPECS = TOOLS`, so the runtime public surface still follows the broader runtime tuple rather than the 10-tool registry target.
3. `arifosmcp/runtime/public_registry.py` still declares `EXPECTED_TOOL_COUNT = 11`.
4. `arifosmcp/runtime/server.py` still describes public tools with canonical dotted ids and explicitly mentions `arifos.reply`.

This means the naming migration should currently be treated as **audit-pending**, not fully sealed.

## Substrate Layer (Official Reference Servers)

The arifos_* tools are grounded by a substrate of official MCP reference servers. These servers provide the foundational capabilities required for metabolic execution.

| Server | Role | Primary Tool Touch |
| :--- | :--- | :--- |
| `Time` | Epoch Anchor | `arifos_init`, `arifos_vault` |
| `Filesystem` | State Access | `arifos_vault`, `arifos_ops` |
| `Memory` | Knowledge Graph | `arifos_memory`, `arifos_mind` |
| `Fetch` | Reality Sensing | `arifos_sense` |
| `Sequential Thinking` | Reasoning Chain | `arifos_mind`, `arifos_judge` |
| `Git` | Audit Integrity | `arifos_vault`, `arifos_vps_monitor` |

See [[Reference_MCP_Servers]] for the full architectural mapping.

## Discovery

- **Well-known**: `/.well-known/mcp`
- **Health**: `/health`
- **Protocol**: MCP 2025-11-05

## Proposed Next Move

Run one **master naming-migration audit** across registry, runtime, reachability, deployment, and client surfaces before any redesign or seal decision.

The recommended sequence is:

1. prove current-state truth with evidence
2. classify all non-canonical surfaces as alias, internal, deprecated, dead, or unresolved
3. seal only after registry, runtime, and deployment truth agree

Do not treat the proposed `3x3 + 1` doctrine as live runtime truth until that audit passes.

Citations:

- [[Metabolic_Loop]]
- `APEX/ASF1/tool_registry.json`
- `arifosmcp/runtime/tool_specs.py`
- `arifosmcp/runtime/public_registry.py`
- `arifosmcp/runtime/tools.py`
- `arifosmcp/runtime/server.py`
- `wiki/raw/mcp_naming_migration_audit_directive_2026-04-11.md`
