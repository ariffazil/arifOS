---
sidebar_position: 5
title: Python
description: Programmatic arifOS integration with Python
---

# Python Integration

Use arifOS programmatically in your Python applications.

## Installation

```bash
pip install arifos
```

## Quick Start

```python
import asyncio
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

async def govern_response(query: str, response: str) -> dict:
    """Run full governance pipeline on a query/response pair."""

    # 1. Initialize session
    init = await mcp_000_init(action="init", query=query)
    session_id = init["session_id"]

    # 2. Check truth (Mind)
    agi = await mcp_agi_genius(
        action="full",
        query=query,
        session_id=session_id
    )

    # 3. Check empathy (Heart)
    asi = await mcp_asi_act(
        action="full",
        text=response,
        session_id=session_id
    )

    # 4. Get verdict (Soul)
    apex = await mcp_apex_judge(
        action="judge",
        query=query,
        response=response,
        session_id=session_id
    )

    # 5. Seal decision
    vault = await mcp_999_vault(
        action="seal",
        session_id=session_id,
        verdict=apex["verdict"]
    )

    return {
        "verdict": apex["verdict"],
        "lane": init["lane"],
        "truth_score": agi.get("truth_score"),
        "empathy_score": asi.get("empathy_score"),
        "seal_id": vault["seal_id"]
    }

# Run it
result = asyncio.run(govern_response(
    query="What is 2+2?",
    response="2+2 equals 4."
))
print(result)
# {'verdict': 'SEAL', 'lane': 'FACTUAL', 'truth_score': 0.99, ...}
```

## Core Functions

### mcp_000_init

Initialize a governance session.

```python
result = await mcp_000_init(
    action="init",           # "init", "gate", "reset", "validate"
    query="User's question",
    session_id=None,         # For resuming sessions
    authority_token=""       # Optional auth token
)

# Returns:
{
    "status": "initialized",
    "session_id": "sess-abc123",
    "lane": "FACTUAL",        # CRISIS, FACTUAL, CARE, or SOCIAL
    "floors_active": ["F1", "F2", ...],
    "verdict": "SEAL"
}
```

### mcp_agi_genius

Check truth, clarity, and humility (Mind).

```python
result = await mcp_agi_genius(
    action="full",           # "sense", "think", "atlas", "forge", "full"
    query="Your question",
    session_id="sess-abc123",
    thought=""               # Previous reasoning to build on
)

# Returns:
{
    "action": "full",
    "truth_score": 0.99,      # F2: must be ≥0.99
    "clarity_delta": 0.15,    # F4: must be ≥0
    "lane": "FACTUAL",
    "floor_results": {
        "F2": {"passed": True, "score": 0.99},
        "F4": {"passed": True, "score": 0.15},
        "F7": {"passed": True, "score": 0.04}
    }
}
```

### mcp_asi_act

Check empathy and safety (Heart).

```python
result = await mcp_asi_act(
    action="full",           # "evidence", "empathy", "act", "full"
    text="AI's response",
    session_id="sess-abc123"
)

# Returns:
{
    "action": "full",
    "empathy_score": 1.0,     # F6: must be ≥0.95
    "peace_squared": 1.0,     # F5: must be ≥1.0
    "reversible": True,       # F1: Amanah check
    "floor_results": {
        "F1": {"passed": True},
        "F5": {"passed": True, "score": 1.0},
        "F6": {"passed": True, "score": 1.0}
    }
}
```

### mcp_apex_judge

Get final verdict (Soul).

```python
result = await mcp_apex_judge(
    action="judge",          # "eureka", "judge", "proof"
    query="Original question",
    response="AI's response",
    session_id="sess-abc123"
)

# Returns:
{
    "action": "judge",
    "verdict": "SEAL",        # SEAL, SABAR, VOID, or 888_HOLD
    "confidence": 0.99,
    "tri_witness": {
        "agi": "SEAL",
        "asi": "SEAL",
        "apex": "SEAL"
    }
}
```

### mcp_999_vault

Seal decision to immutable ledger.

```python
result = await mcp_999_vault(
    action="seal",           # "seal", "query", "verify"
    session_id="sess-abc123",
    verdict="SEAL"
)

# Returns:
{
    "status": "sealed",
    "seal_id": "seal-abc123def456",
    "merkle_root": "0x7f83b1657ff1fc53...",
    "timestamp": "2026-01-25T12:34:56Z",
    "memory_tier": "L0"
}
```

## Simplified API

For simpler use cases, use the high-level wrapper:

```python
from arifos import govern

# Quick governance check
result = await govern(
    query="What is the capital of France?",
    response="The capital of France is Paris."
)

if result.verdict == "SEAL":
    print("Response approved!")
elif result.verdict == "VOID":
    print(f"Blocked: {result.reason}")
```

## Handling Verdicts

```python
async def safe_respond(query: str, response: str):
    result = await govern(query, response)

    match result["verdict"]:
        case "SEAL":
            # All good - deliver response
            return response

        case "SABAR":
            # Minor issue - deliver with warning
            return f"⚠️ {result['warning']}\n\n{response}"

        case "VOID":
            # Cannot deliver - explain why
            return f"I cannot answer this: {result['reason']}"

        case "888_HOLD":
            # High stakes - need human confirmation
            raise HumanConfirmationRequired(result)
```

## Integration with LangChain

```python
from langchain.callbacks import BaseCallbackHandler
from arifos import govern

class ArifOSCallback(BaseCallbackHandler):
    async def on_llm_end(self, response, **kwargs):
        # Govern the LLM's response
        result = await govern(
            query=kwargs.get("prompts", [""])[0],
            response=response.generations[0][0].text
        )

        if result["verdict"] == "VOID":
            raise GovernanceViolation(result)
```

## Running MCP Server

To run arifOS as an MCP server:

```python
# stdio mode (for Claude Desktop, Cursor)
python -m arifos.mcp

# SSE mode (for web clients)
python -m arifos.mcp trinity-sse

# With uvicorn (production)
uvicorn arifos.mcp.trinity_server:app --host 0.0.0.0 --port 8000
```

## Next Steps

- [MCP Examples](/mcp/examples) — Full request/response examples
- [Floor Reference](/floors/reference) — Understanding thresholds
- [Thermodynamics](/floors/thermodynamics) — The physics of governance
