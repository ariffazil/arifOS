# ENGINEER README: 11-Stage Metabolic Loop Refactoring

**Date:** 2026-03-06
**Authority:** A-ENGINEER (Ω)

## Overview
The arifOS AAA MCP server has been refactored to prioritize the canonical **11-stage public workflow** over the legacy numeric sequences and Trinity lanes. The old stages (111-889) and lane-level prompts (AGI, ASI, APEX) are now considered **internal execution primitives** and should not be invoked directly by external clients as top-level workflows.

## The New Canonical 11-Stage Loop

The `metabolic_loop` tool now acts as a pure orchestrator across these 11 explicit stages, enforcing hard checks on Sandbox (700), Judgment (888), and Sealing (999):

| Stage | Internal Mapping / Primitives Used | Hard Constraints |
| :--- | :--- | :--- |
| **000_INIT** | `anchor_session` | Establishes F11/F12 bounds. |
| **100_EXPLORE** | `reason_mind` (Read-only) | Gathering context. |
| **200_DISCOVER**| `reason_mind` | Deep reasoning, associative recall. |
| **300_APPRAISE**| `simulate_heart` | Initial safety/impact assessment. |
| **400_DESIGN** | `reason_mind` | Architecture/invariant mapping. |
| **500_PLAN** | `simulate_heart` | Action planning, empathy checks. |
| **600_PREPARE** | `audit_rules` | Environment readiness validation. |
| **700_PROTOTYPE**| `eureka_forge` | **MUST** run in sandbox. No prod. |
| **800_VERIFY** | `audit_rules` | Final rules audit. |
| **888_JUDGE** | `apex_judge` | Checks all 13 Floors. No side-effects. |
| **999_VAULT** | `seal_vault` | **REQUIRES** human approval evidence. |

## Deprecation of Legacy Public Stages

The old numerical stage names (111, 222, 333, 444, 555, 666, 777, 889) and Trinity loop prompts (`agi_mind_loop`, `asi_heart_loop`, `apex_soul_loop`) have been **deprecated from the public MCP registry surface**.

*   They are now prefixed with `internal.` (e.g., `internal.agi_mind_loop`) or `[INTERNAL_ONLY]`.
*   External clients (like Gemini CLI) should prefer listing and invoking `workflow.000_init` through `workflow.999_vault` directly or just execute the unified `metabolic_loop`.

## Verdict & Gate Normalization
The `metabolic_loop` tool now consistently returns a structured dict conforming to the normalized JSON structure, embedding `verdict`, explicit `floors` passed/failed, structured `gates` status, and required `telemetry` (dS, peace², kappar, confidence, omega0).

DITEMPA BUKAN DIBERI 🔥
