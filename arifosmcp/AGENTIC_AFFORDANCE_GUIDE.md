# arifOS MCP — Constitutional Affordance & Metacognitive Tool Design

> **NOTE (2026-06-23)**: Examples may reference pre-freeze tool names (e.g. arif_forge). Current public surface is the 7 verbs only. See CORE_SEVEN in constitutional_map.py.

**Goal**: Turn every MCP tool from "I can do X" into "I can do X under these conditions, with this authority, producing this evidence shape, with these limits, and this is the next safe action."

This implements the 2026-06 feedback for metacognitive agents (less "function calling", more cognitive clarity).

## Core Principles (the 4 questions every agent must answer)

1. **What is this tool really for?** → `purpose` + `use_when`
2. **When should I not use it?** → `do_not_use_when` + `do_not_conclude`
3. **What changed after I used it?** → `facts` / `inferences` / `result`
4. **How confident am I, and what evidence supports that?** → `confidence`, `metacognition`, `unknowns`, `evidence`

## Standard Output Envelope (always present)

```json
{
  "status": "OK",
  "tool": "arif_xxx",
  "mode": "observe | analyze | recommend | prepare | execute",
  "authority": "advisory_only | requires_human_confirmation",
  "facts": ["..."],
  "inferences": [{"claim": "...", "confidence": 0.72, "basis": "..."}],
  "recommendations": [{"action": "...", "priority": "high"}],
  "unknowns": ["..."],
  "do_not_conclude": ["Do not treat as engineering certification"],
  "confidence": 0.72,
  "risk": {
    "blast_radius": "low | medium | high",
    "reversibility": "reversible | irreversible",
    "human_confirmation_required": true
  },
  "metacognition": {
    "confidence": 0.72,
    "confidence_band": "ADVISORY_ONLY",
    "uncertainty_reason": "...",
    "why_this_tool": "...",
    "failure_modes": [...],
    "next_safe_action": "..."
  },
  "constitutional_check": {
    "floor_passed": true,
    "hold_required": false,
    "hold_reason": null,
    "agency_level": "L2_RECOMMEND"
  },
  "next_safe_action": { "action": "...", "tool": "arif_yyy", "reason": "..." },
  "verdict": "SEAL | HOLD | ADVISORY",
  "affordance_contract": { ... },
  "full_affordance": { ... }
}
```

## Agency Level Taxonomy (L0–L5)

| Level | Type                    | Agent alone? | Human ack? | Example                  |
|-------|-------------------------|--------------|------------|--------------------------|
| L0    | Observe                 | Yes          | No         | arif_observe, arif_ping  |
| L1    | Analyze                 | Yes          | No         | arif_think               |
| L2    | Recommend               | Yes (caveat) | No         | arif_critique, arif_judge|
| L3    | Prepare                 | Yes          | No         | arif_forge (dry)         |
| L4    | Execute (reversible)    | Usually      | No         | memory remember, label   |
| L5    | Execute (irreversible)  | **NO**       | **YES**    | arif_seal, arif_forge_execute |

**L5 rule**: Always `888_HOLD` + explicit `ack_irreversible` + human confirmation, regardless of confidence score.

## Decision Thresholds (standardized)

```
< 0.50 → HOLD
0.50–0.70 → ADVISORY ONLY (caveats required)
0.70–0.85 → ACTIONABLE WITH CAVEAT
> 0.85 → STRONG RECOMMENDATION
Irreversible (L5) → 888 HOLD + human confirmation (overrides score)
```

## Pre-call Reasoning (agent must produce)

```json
{
  "candidate_tool": "arif_critique",
  "why_this_tool": "User wants risk assessment before irreversible action.",
  "why_not_other_tools": ["WEALTH premature", "direct execute violates L5"],
  "expected_output": "critique_report with confidence + next_safe",
  "risk_of_calling": "low"
}
```

## Post-call Reflection

The response always contains `next_safe_action`. Agent loop:
Intent → (get_full_affordance or arif://tools/affordance) → call → inspect metacognition + next_safe → decide (stop / another tool / ask human).

## How to Author New Tools

1. Declare in `TOOL_PURPOSE_CONTRACTS` (runtime/tools.py) — purpose, use_when, do_not..., agency_level, blast_radius.
2. Return via `_ok(...)` (auto-enriched) **or** `build_standard_mcp_result(...)` for rich facts/inferences.
3. The wrapper `_coerce_public_envelope` + `ensure_standard_mcp_output` guarantees the grammar for all calls.
4. Expose affordance via `arif_get_affordance(name)` or the `arif://tools/affordance` resource.

## Resources for Agents

- `arif://tools/discovery` — use_when + examples
- `arif://tools/affordance` — full contracts + L0-L5 + thresholds
- `arif_get_affordance(name)` — programmatic pre-call lookup
- `arif_resolve_tool(name)` — alias → canonical

## Federation Note

Other organs (GEOX, WEALTH, WELL, A-FORGE) should adopt the same envelope keys and affordance shape. arifOS is the canonical governor; organ tools remain evidence-only unless explicitly escalated through 888 path.

**DITEMPA BUKAN DIBERI** — Forged, not given. Clarity is engineered.
