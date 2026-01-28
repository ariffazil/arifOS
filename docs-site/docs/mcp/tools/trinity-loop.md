---
sidebar_position: 6
title: trinity_loop
description: Complete AGI→ASI→APEX→VAULT governance pipeline in one call
---

# trinity_loop

**Role:** Pipeline — Complete constitutional governance cycle in one call.

## Overview

`trinity_loop` runs the full Trinity metabolic pipeline in a single call:

```
AGI (Mind) → ASI (Heart) → APEX (Soul) → VAULT (Seal)
```

Instead of calling 4-5 individual tools sequentially, `trinity_loop` handles the entire governance cycle automatically. This is ideal for simple queries where you don't need fine-grained control over each stage.

## When to Use

| Use Case | Recommended Tool |
|----------|-----------------|
| Quick governance check | `trinity_loop` ✅ |
| Full pipeline with one call | `trinity_loop` ✅ |
| Fine-grained control per stage | Individual tools |
| Custom stage parameters | Individual tools |
| Debugging specific floors | Individual tools |

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "User query to process through the full governance pipeline"
    },
    "session_id": {
      "type": "string",
      "description": "Optional session identifier (auto-generated if omitted)"
    }
  },
  "required": ["query"]
}
```

## Actions

`trinity_loop` does not use the `action` parameter — it always runs the full pipeline.

## Example

### Request

```json
{
  "method": "tools/call",
  "params": {
    "name": "trinity_loop",
    "arguments": {
      "query": "What is the capital of France?"
    }
  }
}
```

### Response

```json
{
  "status": "completed",
  "verdict": "SEAL",
  "session_id": "sess-auto-abc123",
  "pipeline": {
    "agi": {
      "truth_score": 0.99,
      "clarity_delta": 0.12,
      "floor_results": {
        "F2": {"passed": true, "score": 0.99},
        "F4": {"passed": true, "score": 0.12},
        "F7": {"passed": true, "score": 0.04}
      }
    },
    "asi": {
      "empathy_score": 1.0,
      "peace_squared": 1.0,
      "floor_results": {
        "F1": {"passed": true},
        "F5": {"passed": true, "score": 1.0},
        "F6": {"passed": true, "score": 1.0}
      }
    },
    "apex": {
      "verdict": "SEAL",
      "confidence": 0.99,
      "tri_witness": {
        "agi": "SEAL",
        "asi": "SEAL",
        "apex": "SEAL"
      }
    },
    "vault": {
      "sealed": true,
      "seal_id": "seal-trinity-abc123",
      "merkle_root": "0x7f83b1657ff1fc53..."
    }
  }
}
```

## Pipeline Stages

`trinity_loop` executes these stages in order:

1. **AGI Mind** — Evaluates truth (F2), clarity (F4), humility (F7), ontology (F10)
2. **ASI Heart** — Evaluates amanah (F1), peace (F5), empathy (F6), dark cleverness (F9)
3. **APEX Soul** — Synthesizes verdict from AGI + ASI, checks tri-witness (F3), genius (F8), command auth (F11), injection (F12)
4. **VAULT Seal** — Records the decision in the immutable hash-chained ledger

If any **hard floor** fails, the pipeline short-circuits with a `VOID` verdict.

## Constitutional Floors Checked

All 12 constitutional floors are evaluated during the pipeline:

| Stage | Floors | Type |
|-------|--------|------|
| AGI | F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Ontology) | Hard |
| ASI | F1 (Amanah), F5 (Peace²), F6 (Empathy), F9 (C_dark) | Mixed |
| APEX | F3 (Tri-Witness), F8 (Genius), F11 (Command Auth), F12 (Injection) | Hard |

## Comparison: trinity_loop vs Individual Tools

### trinity_loop (One Call)

```python
result = await trinity_loop(query="What is 2+2?")
# Returns complete verdict + seal in one response
```

### Individual Tools (Five Calls)

```python
init = await init_000(action="init", query="What is 2+2?")
agi = await agi_genius(action="full", query="What is 2+2?", session_id=init["session_id"])
asi = await asi_act(action="full", text="2+2 equals 4.", session_id=init["session_id"])
apex = await apex_judge(action="judge", query="What is 2+2?", response="2+2 equals 4.", session_id=init["session_id"])
vault = await vault_999(action="seal", session_id=init["session_id"], verdict=apex["verdict"])
```

## Rate Limiting

`trinity_loop` is **not individually rate-limited** (unlike the other 5 tools which have per-tool limits). However, it internally calls all engines, so heavy use will still consume system resources.

## Next Steps

- [MCP Overview](/mcp/overview) — Architecture and all 6 tools
- [Examples](/mcp/examples) — Full request/response examples
- [init_000](/mcp/tools/init-000) — Fine-grained session control
