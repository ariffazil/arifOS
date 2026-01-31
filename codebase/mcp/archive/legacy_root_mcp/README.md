# 🔧 arifOS MCP Server

**Model Context Protocol implementation for Constitutional AI Governance**

---

## Overview

This directory contains the MCP (Model Context Protocol) server implementation for arifOS, enabling AI clients to connect to the constitutional governance system.

```
┌─────────────┐     MCP      ┌─────────────┐     ┌─────────────┐
│   Claude    │◄────────────►│  MCP Server │◄────►│   arifOS    │
│   Client    │   JSON-RPC   │   (stdio)   │     │   Engine    │
└─────────────┘              └─────────────┘     └─────────────┘
                                    │
                                    ▼
                            ┌─────────────┐
                            │   Tools:    │
                            │  _init_     │
                            │  _agi_      │
                            │  _asi_      │
                            │  _apex_     │
                            │  _vault_    │
                            │  _trinity_  │
                            │  _reality_  │
                            └─────────────┘
```

---

## Quick Start

### 1. Install Dependencies

```bash
pip install asyncio
```

### 2. Run the Server

```bash
python server.py
```

The server uses **stdio transport** (reads stdin, writes stdout).

### 3. Connect Client

Configure your MCP client to launch:
```bash
python /path/to/arifOS/mcp/server.py
```

---

## Protocol: MCP 2025-06-18

### Supported Methods

| Method | Description |
|--------|-------------|
| `initialize` | Client-server handshake |
| `tools/list` | Discover available tools |
| `tools/call` | Invoke a tool |
| `resources/list` | List available resources |
| `prompts/list` | List available prompts |

### Tool Schema

All tools follow the MCP tool definition schema:
```json
{
  "name": "tool_name",
  "title": "Human-readable title",
  "description": "What the tool does",
  "inputSchema": { /* JSON Schema */ },
  "outputSchema": { /* JSON Schema */ },
  "annotations": { /* Behavior hints */ }
}
```

---

## The 7 Tools

### 1. `_init_` - Session Gate (REQUIRED FIRST)

Initializes a constitutional session with security checks.

```json
{
  "name": "_init_",
  "arguments": {
    "action": "init",
    "query": "User's query"
  }
}
```

**Returns:** `session_id`, `authority_level`, `injection_check_passed`

### 2. `_agi_` - Mind Engine

Deep reasoning and knowledge retrieval.

```json
{
  "name": "_agi_",
  "arguments": {
    "action": "full",
    "query": "What is quantum computing?",
    "session_id": "arif_xxx"
  }
}
```

### 3. `_asi_` - Heart Engine

Safety evaluation and ethical assessment.

```json
{
  "name": "_asi_",
  "arguments": {
    "action": "full",
    "query": "Is this action ethical?",
    "session_id": "arif_xxx"
  }
}
```

### 4. `_apex_` - Soul Engine

Judicial consensus and verdict synthesis.

```json
{
  "name": "_apex_",
  "arguments": {
    "action": "decide",
    "query": "Original question",
    "agi_context": { /* AGI output */ },
    "asi_context": { /* ASI output */ }
  }
}
```

### 5. `_vault_` - Immutable Ledger

Permanent tamper-proof storage.

```json
{
  "name": "_vault_",
  "arguments": {
    "action": "seal",
    "verdict": "SEAL",
    "decision_data": { /* Complete decision */ },
    "target": "seal"
  }
}
```

### 6. `_trinity_` - Full Pipeline (RECOMMENDED)

Complete evaluation: AGI → ASI → APEX → VAULT

```json
{
  "name": "_trinity_",
  "arguments": {
    "query": "Should we deploy this AI?",
    "auto_seal": true
  }
}
```

**Returns:** Complete result from all layers + final verdict

### 7. `_reality_` - Fact-Checking

External verification via Brave Search.

```json
{
  "name": "_reality_",
  "arguments": {
    "query": "Verify this claim"
  }
}
```

---

## Example Session

```json
// 1. Initialize
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "Claude", "version": "1.0"}}}

// Response
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-06-18", "serverInfo": {"name": "arifOS", "version": "v54.0"}, ...}}

// 2. List tools
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

// 3. Call _init_
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "_init_", "arguments": {"action": "init", "query": "Hello"}}}

// 4. Call _trinity_
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "_trinity_", "arguments": {"query": "What is AI safety?"}}}
```

---

## Files

| File | Purpose |
|------|---------|
| `server.py` | Main MCP server implementation |
| `mcp_config.json` | Server configuration |
| `HUMAN_GUIDE.md` | User-facing documentation |
| `system_prompts/AI_CONSTITUTIONAL_PROMPT.txt` | AI system instructions |
| `README.md` | This file |

---

## Transport

Current: **stdio** (standard input/output)

Future support:
- SSE (Server-Sent Events)
- WebSocket
- HTTP POST

---

## Security

- All inputs validated against JSON Schema
- Prompt injection detection (F12)
- Session isolation
- Merkle-tree sealing for audit

---

## For AI Developers

To integrate arifOS into your AI:

1. **Load the system prompt:**
   ```
   system_prompts/AI_CONSTITUTIONAL_PROMPT.txt
   ```

2. **Use the tools:**
   - Always call `_init_` first
   - Use `_trinity_` for complete evaluation
   - Respect the verdict (SEAL/VOID/SABAR)

3. **Display constitutional metadata:**
   - Show verdict to users
   - Include trinity_score
   - Note any 888_HOLD escalations

---

## Testing

```bash
# Run server
cd arifOS/mcp
python server.py

# In another terminal, send test request:
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "clientInfo": {"name": "test"}}}' | python server.py
```

---

## Version

- **Server:** v54.0
- **Protocol:** MCP 2025-06-18
- **Constitution:** 9-Paradox Equilibrium

---

## License

See main project license.

---

**DITEMPA BUKAN DIBERI**
