---
sidebar_position: 3
title: asi_act
description: The Heart (Ω) - Safety & Empathy Engine
---

# asi_act

**The Heart (Ω) — Safety & Empathy Engine**

Checks if the action is safe and empathetic. Enforces F1 (Amanah), F5 (Peace), and F6 (Empathy).

## Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action` | string | `"empathize"` | Action to perform |
| `text` | string | `""` | Text to analyze for empathy |
| `session_id` | string | `""` | Session identifier |
| `proposal` | string | `""` | Proposed action to evaluate |

## Actions

| Action | Description |
|--------|-------------|
| `evidence` | Gather supporting data |
| `empathize` | Check stakeholder impact |
| `align` | Align with constitutional values |
| `act` | Execute with safeguards |
| `witness` | Request tri-witness consensus |
| `full` | Complete pipeline |

## Floors Enforced

| Floor | Threshold | Check |
|-------|-----------|-------|
| F1 Amanah | LOCK | Is this reversible? |
| F5 Peace² | ≥ 1.0 | Is this non-destructive? |
| F6 Empathy | κᵣ ≥ 0.95 | Is the weakest protected? |

## Returns

```json
{
  "action": "full",
  "empathy_score": 0.98,
  "peace_squared": 1.2,
  "weakest_stakeholder": "end user",
  "reversible": true,
  "floor_results": {
    "F1": {"passed": true, "reversible": true},
    "F5": {"passed": true, "score": 1.2},
    "F6": {"passed": true, "score": 0.98}
  }
}
```

## Example Usage

### Python

```python
from arifos.mcp.tools.mcp_trinity import mcp_asi_act

result = await mcp_asi_act(
    action="full",
    text="Here's how to delete all your files...",
    session_id="abc123"
)

print(f"Empathy Score: {result['empathy_score']}")
print(f"Reversible: {result['reversible']}")
```

### MCP Call

```json
{
  "method": "tools/call",
  "params": {
    "name": "asi_act",
    "arguments": {
      "action": "full",
      "text": "The capital of France is Paris.",
      "session_id": "abc123"
    }
  }
}
```

## Stakeholder Analysis

The Heart asks: **"Who is the weakest person affected?"**

| Response Type | Weakest Stakeholder |
|---------------|---------------------|
| Code deletion | User (data loss) |
| Investment advice | User (financial risk) |
| Manipulation tips | Target of manipulation |
| Medical advice | Patient |
