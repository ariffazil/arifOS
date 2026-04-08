---
type: Concept
tags: [mcp, tools, substrate, execution]
sources: [tool_specs.py, server.py]
last_sync: 2026-04-08
confidence: 1.0
---

# MCP Tool Surface

Canonical tool surface for the arifOS MCP Server. These tools are the primary interface for agents interacting with the system.

## Tool Mapping (Metabolic Pipeline)

| Tool | Stage | Layer | Purpose |
| :--- | :--- | :--- | :--- |
| `arifos_init` | 000 | GOVERNANCE | Start governed session & bind identity. |
| `arifos_sense` | 111 | MACHINE | Constitutional reality sensing & grounding. |
| `arifos_vps_monitor` | 111 | MACHINE | Secure VPS telemetry (CPU, RAM, Disk). |
| `arifos_mind` | 333 | INTELLIGENCE | Structured reasoning & multi-source synthesis. |
| `arifos_route` | 444 | GOVERNANCE | Execution lane selection & metabolic routing. |
| `arifos_memory` | 555 | INTELLIGENCE | Governed memory recall from vector store. |
| `arifos_heart` | 666 | INTELLIGENCE | Safety, dignity, & adversarial critique. |
| `arifos_ops` | 777 | MACHINE | Cost, thermodynamic, & capacity estimation. |
| `arifos_judge` | 888 | GOVERNANCE | Final constitutional verdict engine. |
| `arifos_vault` | 999 | GOVERNANCE | Immutable verdict logging to VAULT999. |
| `arifos_forge` | 010 | EXECUTION | Delegated execution to AF-FORGE substrate. |

## Discovery

- **Well-known**: `/.well-known/mcp`
- **Health**: `/health`
- **Protocol**: MCP 2025-11-05

Citations:

- [[Concept_Metabolic_Loop]]
- `arifosmcp/runtime/tool_specs.py`
