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
sources:
- tool_specs.py
- server.py
last_sync: '2026-04-10'
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
| `arifos_kernel` | 444 | GOVERNANCE | Execution lane selection & metabolic routing. |
| `arifos_memory` | 555 | INTELLIGENCE | Governed memory recall from vector store. |
| `arifos_heart` | 666 | INTELLIGENCE | Safety, dignity, & adversarial critique. |
| `arifos_ops` | 777 | MACHINE | Cost, thermodynamic, & capacity estimation. |
| `arifos_judge` | 888 | GOVERNANCE | Final constitutional verdict engine. |
| `arifos_vault` | 999 | GOVERNANCE | Immutable verdict logging to VAULT999. |
| `arifos_forge` | 010 | EXECUTION | Delegated execution to AF-FORGE substrate. |
| `arifos_reply` | 000-999 | GOVERNANCE | Governed reply compositor — deterministic dual-axis reply pipeline. |

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

Citations:

- [[Metabolic_Loop]]
- `arifosmcp/runtime/tool_specs.py`
