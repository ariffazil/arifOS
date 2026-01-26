# MCP Client Integration Guide - arifOS v52.5.1

**Complete guide for integrating arifOS with MCP-compatible clients**

**Status:** PRODUCTION READY  
**Version:** v52.5.1-SEAL  
**Authority:** Muhammad Arif bin Fazil

---

## Table of Contents

1. [Overview](#overview)
2. [Claude Desktop Integration](#claude-desktop-integration)
3. [ChatGPT Custom GPT Integration](#chatgpt-custom-gpt-integration)
4. [Kimi AI Integration](#kimi-ai-integration)
5. [Direct API Integration](#direct-api-integration)
6. [MCP Protocol Details](#mcp-protocol-details)

---

## Overview

arifOS v52.5.1 provides two MCP transport modes:

1. **stdio** - For local desktop clients (Claude Desktop, Cursor)
2. **SSE (Server-Sent Events)** - For cloud/remote clients (ChatGPT, web apps)

The constitutional checkpoint is accessible via:
- MCP tools: `000_init`, `agi_genius`, `asi_act`, `apex_judge`, `999_vault`
- REST endpoint: `POST /checkpoint`

---

## Claude Desktop Integration

### Method 1: stdio (Local Development)

**Configuration:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "arifos.mcp"],
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "ARIFOS_HUMAN_SOVEREIGN": "YourName",
        "PYTHONPATH": "/path/to/arifOS"
      }
    }
  }
}
```

**Alternative using uv:**

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "uv",
      "args": ["run", "python", "-m", "arifos.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

**Restart Claude Desktop** after editing configuration.

### Method 2: SSE (Remote Server)

**Configuration:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-remote": {
      "url": "https://your-app.railway.app/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

### Verify Integration

1. Open Claude Desktop
2. Look for "MCP" indicator in the interface
3. Try using one of the Trinity tools:
   ```
   Use the agi_genius tool with action=sense to analyze: "What is 2+2?"
   ```

---

## ChatGPT Custom GPT Integration

ChatGPT Custom GPTs can call arifOS via the `/checkpoint` REST endpoint.

### Step 1: Create Custom GPT

1. Go to [chat.openai.com](https://chat.openai.com)
2. Click your profile → "My GPTs" → "Create a GPT"
3. Name it: "arifOS Constitutional Checkpoint"

### Step 2: Configure Actions

In the "Actions" section:

**Schema Method 1: Import from OpenAPI**

```
https://your-app.railway.app/openapi.json
```

**Schema Method 2: Manual Schema**

```yaml
openapi: 3.0.0
info:
  title: arifOS Constitutional Checkpoint
  version: v52.5.1
  description: Constitutional AI governance checkpoint

servers:
  - url: https://your-app.railway.app
    description: Production server

paths:
  /checkpoint:
    post:
      operationId: validateAction
      summary: Validate action through constitutional checkpoint
      description: |
        Validates an action against 13 constitutional floors (F1-F13).
        Returns a verdict: SEAL (approved), PARTIAL (with warnings), 
        VOID (rejected), or 888_HOLD (requires review).
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - query
              properties:
                query:
                  type: string
                  description: The action or text to validate
                context:
                  type: string
                  description: Optional context about the situation
                stakeholders:
                  type: array
                  items:
                    type: string
                  description: List of affected stakeholders
      responses:
        '200':
          description: Constitutional verdict
          content:
            application/json:
              schema:
                type: object
                properties:
                  verdict:
                    type: string
                    enum: [SEAL, PARTIAL, VOID, SABAR, 888_HOLD]
                  summary:
                    type: string
                  session_id:
                    type: string
                  floors:
                    type: object
```

### Step 3: Configure Authentication (Optional)

If you set `ARIFOS_API_TOKEN`:

1. In Actions → Authentication
2. Select "API Key"
3. Set header: `Authorization: Bearer YOUR_TOKEN`

### Step 4: System Prompt

```
You are an AI assistant with access to the arifOS Constitutional Checkpoint.

Before providing answers to sensitive questions or actions, use the validateAction 
function to check constitutional compliance.

When you receive a verdict:
- SEAL ✅: Action is approved, proceed
- PARTIAL ⚠️: Action approved with warnings, mention concerns
- VOID ❌: Action rejected, explain why and suggest alternatives
- 888_HOLD ⏸️: High-stakes action, requires human review

Always explain the constitutional reasoning in simple terms.
```

### Example Usage

User asks:
```
Should I delete all user data from the database?
```

GPT calls:
```json
{
  "query": "Delete all user data from database",
  "context": "Database maintenance request",
  "stakeholders": ["users", "admin", "data"]
}
```

Response:
```json
{
  "verdict": "VOID",
  "summary": "Violates F1 (Amanah/Reversibility) - irreversible action without backup",
  "floors": {
    "F1": "FAIL",
    "F5": "FAIL"
  }
}
```

---

## Kimi AI Integration

Kimi supports HTTP MCP protocol.

### Configuration: `.kimi/kimi_config.json`

```json
{
  "mcp_servers": {
    "arifos": {
      "url": "https://your-app.railway.app",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      },
      "tools": [
        "init_000",
        "agi_genius",
        "asi_act",
        "apex_judge",
        "vault_999"
      ]
    }
  }
}
```

### Usage in Kimi

```
@mcp arifos init_000 --action init --query "Initialize session"
@mcp arifos agi_genius --action sense --query "Analyze this code"
```

---

## Direct API Integration

### REST API - /checkpoint Endpoint

**Endpoint:** `POST /checkpoint`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN  # Optional
```

**Request Body:**
```json
{
  "query": "The text or action to validate",
  "context": "Optional context about the situation",
  "stakeholders": ["user", "environment"]
}
```

**Response:**
```json
{
  "verdict": "SEAL",
  "summary": "Action validated through constitutional checkpoint",
  "session_id": "abc123def456",
  "ledger_hash": "sha256_merkle_proof",
  "floors": {
    "F1": "PASS",
    "F2": "PASS",
    "F3": "PASS",
    ...
  },
  "trinity_results": {
    "agi": {"status": "PASS", "confidence": 0.99},
    "asi": {"status": "PASS", "empathy": 0.96},
    "apex": {"status": "SEAL", "consensus": 0.97}
  }
}
```

### Python Example

```python
import requests

def validate_action(query: str, context: str = "", stakeholders: list = None):
    """Validate action through arifOS checkpoint."""
    url = "https://your-app.railway.app/checkpoint"
    
    payload = {
        "query": query,
        "context": context,
        "stakeholders": stakeholders or ["user"]
    }
    
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_TOKEN"  # If required
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Example usage
result = validate_action(
    query="Delete user account",
    context="User requested account deletion",
    stakeholders=["user", "admin", "database"]
)

print(f"Verdict: {result['verdict']}")
print(f"Summary: {result['summary']}")
```

### JavaScript Example

```javascript
async function validateAction(query, context = '', stakeholders = ['user']) {
  const url = 'https://your-app.railway.app/checkpoint';
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': 'Bearer YOUR_TOKEN'  // If required
    },
    body: JSON.stringify({
      query,
      context,
      stakeholders
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  
  return await response.json();
}

// Example usage
validateAction(
  'Delete user account',
  'User requested account deletion',
  ['user', 'admin', 'database']
).then(result => {
  console.log(`Verdict: ${result.verdict}`);
  console.log(`Summary: ${result.summary}`);
});
```

### cURL Example

```bash
curl -X POST https://your-app.railway.app/checkpoint \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "Delete all logs older than 30 days",
    "context": "Routine maintenance",
    "stakeholders": ["admin", "audit", "compliance"]
  }'
```

---

## MCP Protocol Details

### Available Tools

arifOS exposes 5 canonical Trinity tools via MCP:

#### 1. `init_000` - Constitutional Gateway

```json
{
  "name": "init_000",
  "description": "System Ignition & Constitutional Gateway",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["init", "verify", "status"],
        "default": "init"
      },
      "query": {
        "type": "string",
        "description": "User query or action"
      },
      "session_id": {
        "type": "string",
        "description": "Optional session ID"
      }
    },
    "required": ["action"]
  }
}
```

#### 2. `agi_genius` - Mind (Δ)

```json
{
  "name": "agi_genius",
  "description": "SENSE → THINK → ATLAS → FORGE pipeline",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["sense", "think", "atlas", "forge", "full"],
        "default": "full"
      },
      "query": {
        "type": "string",
        "description": "Query or data to process"
      }
    },
    "required": ["action", "query"]
  }
}
```

#### 3. `asi_act` - Heart (Ω)

```json
{
  "name": "asi_act",
  "description": "EVIDENCE → EMPATHY → ACT pipeline",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["evidence", "empathy", "act", "full"],
        "default": "full"
      },
      "query": {
        "type": "string",
        "description": "Action to evaluate"
      }
    },
    "required": ["action", "query"]
  }
}
```

#### 4. `apex_judge` - Soul (Ψ)

```json
{
  "name": "apex_judge",
  "description": "EUREKA → JUDGE → PROOF pipeline",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["eureka", "judge", "proof", "full"],
        "default": "full"
      },
      "query": {
        "type": "string",
        "description": "Action to judge"
      }
    },
    "required": ["action", "query"]
  }
}
```

#### 5. `vault_999` - Seal

```json
{
  "name": "vault_999",
  "description": "Merkle sealing + immutable ledger",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["seal", "verify", "query"],
        "default": "seal"
      },
      "session_id": {
        "type": "string",
        "description": "Session to seal or verify"
      }
    },
    "required": ["action"]
  }
}
```

### Complete Pipeline Example

Full constitutional validation flow:

```python
# 1. Initialize session
init_result = await mcp.call_tool("init_000", {
    "action": "init",
    "query": "Analyze security vulnerability"
})
session_id = init_result["session_id"]

# 2. Mind analysis (AGI)
agi_result = await mcp.call_tool("agi_genius", {
    "action": "full",
    "query": "SQL injection in login form",
    "session_id": session_id
})

# 3. Heart evaluation (ASI)
asi_result = await mcp.call_tool("asi_act", {
    "action": "full",
    "query": "Fix vulnerability affecting 10k users",
    "session_id": session_id
})

# 4. Soul judgment (APEX)
apex_result = await mcp.call_tool("apex_judge", {
    "action": "full",
    "query": "Deploy security patch immediately",
    "session_id": session_id
})

# 5. Vault sealing
vault_result = await mcp.call_tool("vault_999", {
    "action": "seal",
    "session_id": session_id
})

print(f"Final Verdict: {vault_result['verdict']}")
```

---

## Testing Your Integration

### 1. Health Check

```bash
curl https://your-app.railway.app/health
```

### 2. Simple Checkpoint Test

```bash
curl -X POST https://your-app.railway.app/checkpoint \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello world", "context": "test"}'
```

### 3. Constitutional Test Cases

**Test 1: F1 Amanah (Reversibility)**
```json
{
  "query": "Delete all production data without backup",
  "context": "Database cleanup"
}
```
Expected: `VOID` (violates F1)

**Test 2: F2 Truth**
```json
{
  "query": "The Earth is flat",
  "context": "Fact checking"
}
```
Expected: `VOID` (violates F2)

**Test 3: F6 Empathy**
```json
{
  "query": "Increase prices by 500% for low-income users",
  "context": "Revenue optimization"
}
```
Expected: `VOID` or `PARTIAL` (violates F6)

**Test 4: Valid Action**
```json
{
  "query": "Send password reset email to user",
  "context": "User requested password reset"
}
```
Expected: `SEAL` (all floors pass)

---

## Troubleshooting

### MCP Connection Issues

**Problem:** "MCP server not responding"

**Solutions:**
1. Check server is running: `curl https://your-app.railway.app/health`
2. Verify MCP transport (stdio vs SSE)
3. Check firewall/network settings
4. Review Railway logs: `railway logs`

### Authentication Errors

**Problem:** "401 Unauthorized"

**Solutions:**
1. Verify `ARIFOS_API_TOKEN` is set
2. Check Authorization header format: `Bearer YOUR_TOKEN`
3. Regenerate token if expired

### Slow Response Times

**Problem:** Checkpoint takes > 10 seconds

**Solutions:**
1. Check Redis connection (used for caching)
2. Verify Railway instance isn't sleeping (free tier)
3. Consider upgrading Railway plan
4. Review logs for errors

---

## Next Steps

- **Load Testing**: Use `tests/k6/checkpoint_load_test.js`
- **Monitoring**: Access `/dashboard` for live metrics
- **Custom Integrations**: Build your own client using the REST API
- **Advanced Features**: Explore cooling tiers and tri-witness consensus

---

**DITEMPA BUKAN DIBERI** - Forged, Not Given

**Authority:** Muhammad Arif bin Fazil  
**Version:** arifOS v52.5.1-SEAL  
**Last Updated:** 2026-01-26
