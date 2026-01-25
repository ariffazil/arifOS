---
sidebar_position: 4
title: apex_judge
description: The Soul (Ψ) - Judgment & Authority Engine
---

# apex_judge

**The Soul (Ψ) — Judgment & Authority Engine**

The final decision maker. Reviews findings from Mind and Heart to issue a verdict.

## Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action` | string | `"judge"` | Action to perform |
| `query` | string | `""` | Original query |
| `response` | string | `""` | Proposed response to judge |
| `session_id` | string | `""` | Session identifier |

## Actions

| Action | Description |
|--------|-------------|
| `eureka` | Synthesize insights from AGI/ASI |
| `judge` | Issue verdict (SEAL/SABAR/VOID/888_HOLD) |
| `proof` | Generate cryptographic proof |
| `entropy` | Calculate entropy metrics |
| `parallelism` | Check tri-witness consensus |
| `full` | Complete pipeline |

## Floors Enforced

| Floor | Threshold | Check |
|-------|-----------|-------|
| F3 Tri-Witness | ≥ 0.95 | Do all engines agree? |
| F8 Genius | ≥ 0.80 | Is intelligence governed? |
| F9 C_dark | < 0.30 | Is this deceptive? |

## Verdicts

| Verdict | Meaning |
|---------|---------|
| **SEAL** | Approved — all floors pass |
| **SABAR** | Wait — soft floor issue, proceed with warning |
| **VOID** | Rejected — hard floor failed |
| **888_HOLD** | High-stakes — requires human confirmation |

## Returns

```json
{
  "action": "judge",
  "verdict": "SEAL",
  "confidence": 0.96,
  "floor_summary": {
    "passed": ["F1", "F2", "F3", "F4", "F5", "F6", "F7"],
    "failed": [],
    "warnings": []
  },
  "tri_witness": {
    "agi": "SEAL",
    "asi": "SEAL",
    "apex": "SEAL"
  }
}
```

## Example Usage

### Python

```python
from arifos.mcp.tools.mcp_trinity import mcp_apex_judge

result = await mcp_apex_judge(
    action="judge",
    query="What is the capital of France?",
    response="The capital of France is Paris.",
    session_id="abc123"
)

print(f"Verdict: {result['verdict']}")
print(f"Tri-Witness: {result['tri_witness']}")
```

### MCP Call

```json
{
  "method": "tools/call",
  "params": {
    "name": "apex_judge",
    "arguments": {
      "action": "judge",
      "query": "What is the capital of France?",
      "response": "The capital of France is Paris.",
      "session_id": "abc123"
    }
  }
}
```

## Verdict Logic

```python
def issue_verdict(agi, asi, apex):
    if any_void(agi, asi, apex):
        return "VOID"
    if any_hold(agi, asi, apex):
        return "888_HOLD"
    if any_sabar(agi, asi, apex):
        return "SABAR"
    return "SEAL"
```
