---
type: Tool
tier: 20_RUNTIME
strand: [tools]
audience: [engineers, operators]
difficulty: intermediate
prerequisites: [MCP_Tools, Concept_Deployment_Architecture]
tags: [telemetry, hardware, machine, vps, monitoring, ops]
sources: [tool_specs.py, vps_monitor.py, ROADMAP.md]
last_sync: 2026-04-10
confidence: 0.95
---

# Tool: arifos_vps_monitor

**arifos_vps_monitor** is the host telemetry surface for the AF-FORGE machine layer.

Its job is simple: show the machine as it is, in read-only form, so governance can reason about real thermodynamic limits before action.

## Purpose

To retrieve machine state such as:
- CPU load
- memory pressure
- swap usage
- disk usage
- storage pressure
- VPS health signals

This gives the constitutional stack a grounded view of whether the host can safely absorb more work.

## Why this tool exists

Without telemetry, planning drifts into fiction.
A model may propose more jobs, more agents, more containers, more indexing, more automation, while the host is already close to heat, memory, or storage limits.

`arifos_vps_monitor` exists to stop that kind of elegant nonsense.

## Specifications

- **Stage**: 111 (Sensing)
- **Layer**: MACHINE
- **Trinity**: Δ (Mind grounding against substrate reality)
- **Floors touched most directly**: F2, F4, F8, F12

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `action` | Enum | `get_telemetry`, `get_zram_status`, `get_disk_usage` |
| `dry_run` | Boolean | If `true`, plans the telemetry fetch instead of executing it |

## Boundary conditions

This tool should stay:
- read-only
- low-risk
- low-side-effect
- easy to audit

It is for observation, not remote administration.
If the system needs to change the machine, that should happen through the execution path, not by smuggling control into telemetry.

## Operational value

For AF-FORGE, this tool is especially useful when deciding whether to:
- start or stop heavy services
- add more agent concurrency
- run large embedding or indexing jobs
- deploy container changes
- escalate from CAUTION to HOLD because the host is near resource limits

## F12 hardening

`arifos_vps_monitor` should reject parameters that turn telemetry into shell escape, covert execution, or side-channel abuse.
The machine layer must remain glass-box enough for oversight, but not porous enough to become an execution bypass.

## Related

- [[MCP_Tools]]
- [[Concept_Architecture]]
- [[Concept_Deployment_Architecture]]
- [[arifos_forge]]
