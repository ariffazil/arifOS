# arifOS MCP — Platform Integration Guide

**MCP Endpoint:** `https://arifosmcp.arif-fazil.com/mcp`
**Transport:** Streamable HTTP (stateless)
**Protocol:** MCP 2024-11-05
**Auth:** None required (public server) — Bearer tokens are accepted and ignored

---

## Quick Compatibility Matrix

| Platform | Status | Transport | Auth |
|----------|--------|-----------|------|
| Anthropic (Claude API) | ✅ Compatible | Streamable HTTP | Bearer (optional) |
| OpenAI (Responses API) | ✅ Compatible | Streamable HTTP | Bearer (optional) |
| Google Gemini (SDK) | ✅ Compatible | HTTP | Bearer / x-api-key (optional) |
| Claude Desktop | ✅ Compatible | stdio (local) or HTTP (remote) | — |
| Cursor / Windsurf | ✅ Compatible | Streamable HTTP | — |
| MCP Inspector | ✅ Compatible | Streamable HTTP | — |

---

## 1. Anthropic — Claude API (Python SDK)

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    tools=[
        {
            "type": "mcp",
            "name": "arifos",
            "url": "https://arifosmcp.arif-fazil.com/mcp",
        }
    ],
    messages=[
        {"role": "user", "content": "What time is it in Kuala Lumpur?"}
    ],
    betas=["mcp-client-2025-04-04"],
)
print(response.content)
```

**Notes:**
- Include `betas=["mcp-client-2025-04-04"]` in all calls
- Bearer token not required — server is public
- Only tools are exposed (resources/prompts not used by this integration)

---

## 2. OpenAI — Responses API

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4o",
    tools=[
        {
            "type": "mcp",
            "server_label": "arifos",
            "server_url": "https://arifosmcp.arif-fazil.com/mcp",
            "require_approval": "never",
        }
    ],
    input="What is the governance status of this AI request?",
)
print(response.output_text)
```

**Notes:**
- `require_approval: "never"` for automated pipelines — arifOS has its own constitutional gate (F1-F13)
- `require_approval: "always"` for sovereign/high-stakes operations
- Keep `mcp_list_tools` in context between calls to avoid re-fetching tool schemas
- Optional: filter tools with `allowed_tools: ["init_anchor", "agi_mind"]`

---

## 3. Google Gemini SDK (Python)

```python
import google.generativeai as genai
from fastmcp import Client

# Option A: FastMCP client → Gemini tools
async def with_fastmcp_client():
    async with Client("https://arifosmcp.arif-fazil.com/mcp") as mcp:
        tools = await mcp.list_tools()

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=[mcp.session],  # pass MCP session directly
        )
        response = model.generate_content("What time is it in Kuala Lumpur?")
        print(response.text)

# Option B: Direct HTTP (Gemini API native MCP — experimental)
import google.genai as genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Analyze this governance request.",
    config={
        "tools": [{
            "type": "mcp",
            "url": "https://arifosmcp.arif-fazil.com/mcp"
        }]
    }
)
print(response.text)
```

**Notes:**
- Gemini MCP support is currently experimental (Python + JS SDK only)
- FastMCP client approach (Option A) is the most stable path today
- `x-api-key` header accepted if your Gemini integration requires it

---

## 4. Claude Desktop / Claude.ai

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos": {
      "type": "url",
      "url": "https://arifosmcp.arif-fazil.com/mcp",
      "name": "arifOS Constitutional AI"
    }
  }
}
```

---

## 5. MCP Inspector (debugging)

```bash
npx @modelcontextprotocol/inspector https://arifosmcp.arif-fazil.com/mcp
```

---

## Available Tools (11 Mega-Tools)

| Tool | Layer | Key Modes |
|------|-------|-----------|
| `init_anchor` | Governance | init, state, revoke |
| `arifOS_kernel` | Governance | kernel, status |
| `apex_soul` | Governance | judge, validate, hold |
| `vault_ledger` | Governance | seal, verify |
| `agi_mind` | Intelligence | reason, reflect, forge |
| `asi_heart` | Intelligence | critique, simulate, align |
| `engineering_memory` | Intelligence | engineer, vector_query, vector_store |
| `physics_reality` | Machine | search, ingest, time, compass, atlas |
| `math_estimator` | Machine | cost, health, vitals |
| `code_engine` | Machine | fs, process, net, tail |
| `architect_registry` | Machine | register, list, read |

**Quickstart example** — get current time (no auth needed):

```bash
curl -s https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"physics_reality","arguments":{"mode":"time"}},"id":1}'
```

---

## CORS Policy

arifOS accepts requests from all origins (`*`). Security is enforced by the 13 constitutional floors internally, not by network-level restrictions.

Custom deployments can restrict origins via the `ARIFOS_ALLOWED_ORIGINS` environment variable.

---

## Related

- [POSITIONING.md](./POSITIONING.md) — what arifOS is
- [LICENSING.md](./LICENSING.md) — CC0 standard, AGPL-3.0 runtime
- [SABAR.md](./SABAR.md) — thermodynamic cooling states
- MCP Registry: `io.github.ariffazil/arifosmcp`
- Health: https://arifosmcp.arif-fazil.com/health
