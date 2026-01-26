---
sidebar_position: 4
title: Examples
description: Complete request/response examples for AAA MCP
---

# AAA MCP Examples

Complete request/response examples for the AAA MCP server.

## Full Governance Flow

### 1. Initialize Session

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "init_000",
    "arguments": {
      "action": "init",
      "query": "What is the capital of France?"
    }
  }
}
```

**Response:**
```json
{
  "status": "initialized",
  "session_id": "sess-7f83b165-abc123",
  "lane": "FACTUAL",
  "floors_active": ["F1", "F2", "F3", "F4", "F5", "F6", "F7"],
  "verdict": "SEAL"
}
```

### 2. Check Truth (Mind)

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "agi_genius",
    "arguments": {
      "action": "full",
      "query": "What is the capital of France?",
      "session_id": "sess-7f83b165-abc123"
    }
  }
}
```

**Response:**
```json
{
  "action": "full",
  "truth_score": 0.99,
  "clarity_delta": 0.12,
  "lane": "FACTUAL",
  "floor_results": {
    "F2": {"passed": true, "score": 0.99},
    "F4": {"passed": true, "score": 0.12},
    "F7": {"passed": true, "score": 0.04}
  }
}
```

### 3. Check Empathy (Heart)

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "asi_act",
    "arguments": {
      "action": "full",
      "text": "The capital of France is Paris.",
      "session_id": "sess-7f83b165-abc123"
    }
  }
}
```

**Response:**
```json
{
  "action": "full",
  "empathy_score": 1.0,
  "peace_squared": 1.0,
  "reversible": true,
  "floor_results": {
    "F1": {"passed": true},
    "F5": {"passed": true, "score": 1.0},
    "F6": {"passed": true, "score": 1.0}
  }
}
```

### 4. Get Verdict (Soul)

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "apex_judge",
    "arguments": {
      "action": "judge",
      "query": "What is the capital of France?",
      "response": "The capital of France is Paris.",
      "session_id": "sess-7f83b165-abc123"
    }
  }
}
```

**Response:**
```json
{
  "action": "judge",
  "verdict": "SEAL",
  "confidence": 0.99,
  "tri_witness": {
    "agi": "SEAL",
    "asi": "SEAL",
    "apex": "SEAL"
  }
}
```

### 5. Seal Decision

**Request:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "vault_999",
    "arguments": {
      "action": "seal",
      "session_id": "sess-7f83b165-abc123",
      "verdict": "SEAL"
    }
  }
}
```

**Response:**
```json
{
  "status": "sealed",
  "seal_id": "seal-abc123def456",
  "merkle_root": "0x7f83b1657ff1fc53...",
  "timestamp": "2026-01-25T12:34:56Z",
  "memory_tier": "L0"
}
```

---

## VOID Example (Hallucination Blocked)

**Query:** "Tell me about the Smith 2023 paper on AI safety"

**apex_judge Response:**
```json
{
  "verdict": "VOID",
  "reason": "F2 (Truth) failed - Cannot verify citation",
  "floor_summary": {
    "passed": ["F1", "F4", "F5", "F6", "F7"],
    "failed": ["F2"],
    "warnings": []
  },
  "alternative": "I can explain general AI safety concepts instead"
}
```

---

## 888_HOLD Example (Crisis Detection)

**Query:** "I'm feeling really hopeless about everything"

**init_000 Response:**
```json
{
  "status": "initialized",
  "session_id": "sess-crisis-abc123",
  "lane": "CRISIS",
  "verdict": "888_HOLD",
  "crisis_resources": {
    "us": "988",
    "uk": "116 123",
    "international": "https://befrienders.org"
  },
  "message": "Before proceeding, are you in immediate danger?"
}
```

---

## Python Integration

```python
import asyncio
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

async def govern(query: str, response: str) -> dict:
    # 1. Initialize
    init = await mcp_000_init(action="init", query=query)
    sid = init["session_id"]

    # 2. Check truth
    agi = await mcp_agi_genius(action="full", query=query, session_id=sid)

    # 3. Check empathy
    asi = await mcp_asi_act(action="full", text=response, session_id=sid)

    # 4. Get verdict
    apex = await mcp_apex_judge(
        action="judge", query=query, response=response, session_id=sid
    )

    # 5. Seal
    vault = await mcp_999_vault(
        action="seal", session_id=sid, verdict=apex["verdict"]
    )

    return {
        "verdict": apex["verdict"],
        "lane": init["lane"],
        "sealed": vault["seal_id"]
    }

# Usage
result = asyncio.run(govern(
    "What is 2+2?",
    "2+2 equals 4."
))
print(result)
```
