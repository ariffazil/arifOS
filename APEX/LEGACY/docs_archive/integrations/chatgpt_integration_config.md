# arifOS ChatGPT Integration Configuration

## Current Server Status
- **Live Production Server**: https://aaamcp.arif-fazil.com
- **Health Check**: https://aaamcp.arif-fazil.com/health
- **Current Version**: v55.4-SEAL
- **Tools Available**: 9 canonical tools (init_gate, agi_sense, agi_think, agi_reason, asi_empathize, asi_align, apex_verdict, reality_search, vault_seal)

## ChatGPT Integration Options

### Option 1: Direct Integration (Recommended)
Use the live production server with ChatGPT Actions:

**Endpoint**: https://aaamcp.arif-fazil.com

**Configuration for Custom GPT**:
1. Create a Custom GPT at chatgpt.com
2. In the "Add Action" section, use:
   - **URL**: https://aaamcp.arif-fazil.com
   - **OpenAPI Schema**: Available at https://aaamcp.arif-fazil.com/openapi.json (when implemented)

### Option 2: OpenAI API Integration
For developers using the OpenAI API directly:

```python
import openai
from arifos import ConstitutionalAgent

# Configure the agent
agent = ConstitutionalAgent(
    mcp_server="https://aaamcp.arif-fazil.com",
    floors="all"  # Enforce all 9 constitutional floors
)

# Use in your application
response = agent.process("Your query here")
print(response.verdict)  # SEAL, VOID, SABAR, or 888_HOLD
```

### Option 3: MCP Protocol Integration
For Claude, Cursor, or other MCP-compatible editors:

**Add to your .mcp.json or editor configuration**:
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://aaamcp.arif-fazil.com/sse"
    }
  }
}
```

## Available Tools (9 Canonical Tools)

1. **init_gate** - Session initialization and injection defense (F11, F12)
2. **agi_sense** - Input parsing and intent detection (F2, F4) 
3. **agi_think** - Hypothesis generation (F2, F4, F7)
4. **agi_reason** - Deep logical reasoning (F2, F4, F7)
5. **asi_empathize** - Stakeholder impact assessment (F5, F6)
6. **asi_align** - Constitutional alignment check (F5, F6, F9)
7. **apex_verdict** - Final constitutional judgment (F3, F8)
8. **reality_search** - External fact-checking (F2, F7)
9. **vault_seal** - Immutable audit logging (F1, F3)

## OpenAPI Schema Structure
The server will provide an OpenAPI 3.1.0 specification at `/openapi.json` with all 9 tools defined with their parameters, return types, and constitutional floor enforcement details.

## Testing Your Integration
```bash
# Health check
curl https://aaamcp.arif-fazil.com/health

# Test individual tool (example)
curl -X POST https://aaamcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "init_gate",
    "params": {
      "query": "Test query",
      "session_id": "test-session"
    }
  }'
```

## Production Endpoints
- **Health**: https://aaamcp.arif-fazil.com/health
- **MCP**: https://aaamcp.arif-fazil.com/mcp
- **SSE**: https://aaamcp.arif-fazil.com/sse
- **Dashboard**: https://aaamcp.arif-fazil.com/dashboard
- **Docs**: https://aaamcp.arif-fazil.com/docs

## Constitutional Enforcement
Every tool enforces specific constitutional floors:
- **F1 Amanah**: Reversibility and audit trails
- **F2 Truth**: Verifiable claims only
- **F3 Tri-Witness**: Consensus requirements
- **F5 Peace²**: Stability requirements
- **F7 Ω₀**: Humility (3-5% uncertainty)
- **F9 Anti-Hantu**: No consciousness claims

The server returns verdicts: SEAL (approved), VOID (blocked), SABAR (caution), or 888_HOLD (human review).