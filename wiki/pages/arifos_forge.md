---
type: Tool
tier: 20_RUNTIME
strand:
- tools
audience:
- engineers
difficulty: intermediate
prerequisites:
- MCP_Tools
tags:
- execution
- bridge
- forge
- shell
- manifest
- a-forge
sources:
- tool_specs.py
- capability_map.py
- ROADMAP.md
- CHANGELOG_snapshot_2026-04-07.md
last_sync: '2026-04-10'
confidence: 0.95
---

# Tool: arifos_forge

**arifos_forge** is the execution bridge between the constitutional kernel and the A-FORGE runtime substrate.

It exists to do one thing cleanly: convert a governed decision into machine action without letting execution logic become sovereign.

## What it is

`arifos_forge` dispatches approved work to external execution surfaces such as:
- shell commands
- API calls
- contracts / manifests
- containers
- VMs
- delegated compute

This is the point where reasoning stops being only symbolic and starts touching infrastructure.

## Why it matters

A-FORGE is not the constitution itself.
It is the **actuation layer**.

That distinction is the whole safety boundary:
- **judge** decides whether an action may proceed
- **forge** carries it out
- **vault** records what happened

If those collapse into one surface, arifOS loses separation of powers.

## Specifications

- **Stage**: 010 (Execution)
- **Layer**: EXECUTION
- **Trinity**: Δ (Mind acting on substrate)
- **Floors touched most directly**: F1, F2, F7, F11, F13

## Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `action` | Enum | `shell`, `api_call`, `contract`, `compute`, `container`, `vm` |
| `payload` | Object | Execution parameters for the requested action |
| `judge_verdict` | String | Required. Must be `SEAL` from `arifos_judge` |
| `judge_g_star` | Number | G★ score at verdict time |
| `dry_run` | Boolean | If `true`, generate the manifest only |

## Execution boundary

`arifos_forge` should be read as a **bridge**, not as a free-form agent.

That means:
- it should not self-authorize work
- it should not silently upgrade scope
- it should prefer manifests and explicit payloads over ad hoc improvisation
- it should remain auditable enough that a human can reconstruct what was intended

## The Sovereign Gate (F13)

`arifos_forge` must refuse dispatch without a valid `judge_verdict = "SEAL"`.

This is the anti-bypass rule that prevents prompt-to-execution jumps.
No matter how good a plan sounds, execution authority does not emerge from confidence alone.

## A-FORGE practical note

In deployment language, A-FORGE is the substrate where governed actions meet real services: containers, ingress, workers, automations, and remote compute.

That substrate may evolve, but the invariant should stay the same:
**execution remains downstream of verdict.**

## Related

- [[MCP_Tools]]
- [[Concept_Architecture]]
- [[Concept_Deployment_Architecture]]
- [[arifos_vps_monitor]]
- [[ToolSpec_arifos_judge]]
