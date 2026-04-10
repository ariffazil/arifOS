---
type: Synthesis
tier: 20_RUNTIME
strand:
- integration
audience:
- engineers
difficulty: intermediate
prerequisites:
- Tool_Surface_Architecture
tags:
- mcp
- substrate
- arifos
sources:
- mcp_reference_servers_mapping.md
last_sync: '2026-04-11'
confidence: 0.95
---

# Reference MCP Servers (Substrate Layer)

This page documents the 7 official MCP reference servers and their mapping to the arifOS functional layers. These servers provide the "Reality Grounding" (Substrate) upon which the arifosmcp metabolic tools operate.

## Layer Mapping

| MCP Server | arifOS Role | Stage / Floor | Purpose |
| :--- | :--- | :--- | :--- |
| **Everything** | Integration Harness | F2 / 000 | Validates the full server stack (prompts, resources, tools). |
| **Fetch** | Intelligence Ingestion | F9 / 111 | Pulls live web content into agent context without browser overhead. |
| **Filesystem** | Sovereign Vault Access | F1 / F8 / 888 | Controlled read/write to arifOS state files and config. |
| **Git** | Version Integrity | F2 / F11 | Audit trails, diffs, and 999 SEAL telemetry. |
| **Memory** | Knowledge Graph | F3 / 333 | Persistent entity relationships across sessions. |
| **Sequential Thinking** | Pipeline Engine Mirror | 111 → 777 → 888 | Implements reflective thought sequences matching arifOS loop. |
| **Time** | Epoch Anchor | 000 / 999 | Locks telemetry to real UTC (critical for MY+08 logging). |

## Architectural Stack View

The reference servers form a four-layer stack within the arifOS environment:

1. **Foundation (Infrastructure)**: `Filesystem` + `Git` → Sovereign state storage + immutable audit trail.
2. **Cognition (Runtime)**: `Memory` + `Sequential Thinking` → Persistent context + structured reasoning pipeline.
3. **Environment (I/O)**: `Fetch` + `Time` → Live world data + temporal grounding.
4. **Validation (Test)**: `Everything` → Integration smoke test harness.

## Priority Integration Order

For VPS Docker deployment, the following sequence is enforced to maintain constitutional integrity:

1. **Time**: Anchor epochs first.
2. **Filesystem**: Mount configuration and state volumes.
3. **Git**: Connect for commit-level telemetry.
4. **Memory**: Spin up the knowledge graph.
5. **Fetch**: Enable external grounding.
6. **Sequential Thinking**: Activate reasoning loops once memory is warm.
7. **Everything**: Final full-stack smoke test.

---

> [!TIP]
> **Metabolic Alignment**: `Memory` + `Sequential Thinking` together are the closest substrate analog to the arifOS internal pipeline (000→999).

Citations:
- [[Tool_Surface_Architecture]]
- [[Metabolic_Loop]]
- [[mcp_reference_servers_mapping.md]]
