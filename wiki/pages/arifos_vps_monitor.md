---
type: Tool
tags: [telemetry, hardware, machine, machine, vps, monitoring]
sources: [tool_specs.py, vps_monitor.py]
last_sync: 2026-04-08
confidence: 1.0
---

# Tool: arifos_vps_monitor

**arifos_vps_monitor** is the **Secure Telemetry Tool** for arifOS. It provides hardened, read-only access to host machine diagnostics.

## Purpose

To retrieve real-time resource utilization (CPU, Memory, ZRAM, Disk) for the `CCC` (Constitutional Core) to evaluate the thermodynamic feasibility of complex operations.

## Specifications

- **Stage**: 111 (Sensing)
- **Layer**: MACHINE
- **Trinity**: Δ (Mind)
- **Floors**: F4 (Clarity), F12 (Void Management)

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `action` | Enum | `get_telemetry`, `get_zram_status`, `get_disk_usage` |
| `dry_run` | Boolean| If `true`, plans the telemetry fetch (default: `true`) |

---

## F12 Hardening

Unlike standard system monitoring tools, `arifos_vps_monitor` is restricted by the kernel's **F12 injection guard**. It rejects any parameters that could be used for shell escape or side-channel information leakage, ensuring that the machine layer remains a "Glass Box" for the governing layers.

## Related

- [[Concept_Architecture]]
- [[Concept_Metabolic_Pipeline]]
- [[Concept_Governance_Enforcer]]
