---
sidebar_position: 1
title: init_000
description: System Ignition & Constitutional Gateway
---

# init_000

**System Ignition & Constitutional Gateway**

The first step for any interaction. Initializes the session, verifies authority, and routes the request via ATLAS-333.

## Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action` | string | `"init"` | Action to perform |
| `query` | string | `""` | The user's query (for intent detection) |
| `session_id` | string | `null` | Existing session ID (for resume) |
| `authority_token` | string | `""` | Optional authority token |

## Actions

| Action | Description |
|--------|-------------|
| `init` | Full 7-step ignition (default) |
| `gate` | Quick authority check only |
| `reset` | Clear session state |
| `validate` | Verify session integrity |

## The 7-Step Ignition Sequence

1. **MEMORY INJECTION** — Load context from VAULT999
2. **SOVEREIGN RECOGNITION** — Verify authority
3. **INTENT MAPPING** — Route via ATLAS-333 (CRISIS/FACTUAL/CARE/SOCIAL)
4. **THERMODYNAMIC BOOT** — Initialize entropy tracking
5. **FLOOR ACTIVATION** — Enable constitutional checks
6. **SESSION CREATION** — Generate secure session_id
7. **READY SIGNAL** — Return ignition status

## Returns

```json
{
  "status": "initialized",
  "session_id": "uuid-abc123-def456",
  "lane": "FACTUAL",
  "floors_active": ["F1", "F2", "F3", "F4", "F5", "F6", "F7"],
  "verdict": "SEAL"
}
```

## Example Usage

### Python

```python
from arifos.mcp.tools.mcp_trinity import mcp_000_init

result = await mcp_000_init(
    action="init",
    query="What is the capital of France?"
)

print(f"Session: {result['session_id']}")
print(f"Lane: {result['lane']}")
```

### MCP Call

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

## Lane Detection

Based on the query, `init_000` routes to the appropriate lane:

| Query Pattern | Lane |
|---------------|------|
| "I want to die" | CRISIS |
| "How do I code X?" | FACTUAL |
| "I'm feeling sad" | CARE |
| "Hello!" | SOCIAL |
