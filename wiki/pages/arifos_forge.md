---
type: Tool
tags: [execution, bridge, forge, shell, manifest]
sources: [tool_specs.py, capability_map.py]
last_sync: 2026-04-08
confidence: 1.0
---

# Tool: arifos_forge

**arifos_forge** is the **Delegated Execution Bridge** of arifOS. It is the primary tool for materializing intelligence into machine action (AF-FORGE substrate).

## Purpose

To issue signed execution manifests to external compute substrates (containers, VMs, Cloud) while maintaining strict **Separation of Powers** from the Constitutional Kernel.

## Specifications

- **Stage**: 010 (Execution)
- **Layer**: EXECUTION
- **Trinity**: Δ (Mind)
- **Floors**: F1, F2, F7, F13

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `action` | Enum | `shell`, `api_call`, `contract`, `compute`, `container`, `vm` |
| `payload` | Object | Parameters for the action |
| `judge_verdict`| String | **Required**: Must be `"SEAL"` from `arifos_judge` |
| `judge_g_star` | Number | G★ score at time of verdict |
| `dry_run` | Boolean| If `true`, only generates the manifest (default: `true`) |

---

## The Sovereign Gate (F13)

`arifos_forge` will refuse to dispatch any payload unless provided with a valid `judge_verdict = "SEAL"`. This prevents "Prompt Injection to Execution" bypasses by forcing a governed decision before any machine work commences.

## Related

- [[Concept_Architecture]]
- [[arifos_judge]]
- [[Horizon_3_Universal_Body]]
