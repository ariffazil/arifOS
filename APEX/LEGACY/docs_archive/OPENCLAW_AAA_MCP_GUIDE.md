# Configuring arifOS AAA MCP Server with OpenClaw

**How to connect any OpenClaw instance to the arifOS Constitutional AI governance layer.**

---

## Quick Start (3 Options)

### Option 1: Use the Public Endpoint (Easiest)

The arifOS AAA MCP server is already running at:

```
https://aaamcp.arif-fazil.com
```

**Add to your OpenClaw config:**

```json
{
  "mcpServers": {
    "arifos": {
      "baseUrl": "https://aaamcp.arif-fazil.com/sse"
    }
  }
}
```

**Using mcporter:**

```bash
mcporter config add arifos --url https://aaamcp.arif-fazil.com/sse
```

---

### Option 2: Self-Host via Docker

```bash
# Clone the repo
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Run with Docker
docker build -t arifos-mcp .
docker run -p 8080:8080 arifos-mcp
```

**Then configure OpenClaw:**

```json
{
  "mcpServers": {
    "arifos": {
      "baseUrl": "http://localhost:8080/sse"
    }
  }
}
```

---

### Option 3: Run Locally (Python)

```bash
# Clone and install
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .

# Run SSE server
python -m aaa_mcp sse
```

**Or for stdio transport (Claude Desktop):**

```bash
python -m aaa_mcp
```

---

## OpenClaw Configuration

### Method A: Edit mcporter.json

Location: `~/.openclaw/workspace/config/mcporter.json` or `./config/mcporter.json`

```json
{
  "mcpServers": {
    "arifos": {
      "baseUrl": "https://aaamcp.arif-fazil.com/sse"
    },
    "other-servers": "..."
  }
}
```

### Method B: Use mcporter CLI

```bash
# Add the server
mcporter config add arifos --url https://aaamcp.arif-fazil.com/sse

# Verify it's added
mcporter config list

# Test connection
mcporter list arifos
```

---

## Available Tools (9 Canonical)

Once configured, these tools are available:

| Tool | Purpose | Example Call |
|------|---------|--------------|
| `init_gate` | Session init & injection defense | `mcporter call arifos.init_gate query="Hello" session_id=test` |
| `agi_sense` | Intent parsing & classification | `mcporter call arifos.agi_sense query="Analyze this" session_id=test` |
| `agi_think` | Hypothesis generation | `mcporter call arifos.agi_think query="What if..." session_id=test` |
| `agi_reason` | Deep logical reasoning | `mcporter call arifos.agi_reason query="Why does..." session_id=test` |
| `asi_empathize` | Stakeholder impact | `mcporter call arifos.asi_empathize query="Who is affected?" session_id=test` |
| `asi_align` | Ethics & Anti-Hantu check | `mcporter call arifos.asi_align query="Is this ethical?" session_id=test` |
| `apex_verdict` | Final constitutional judgment | `mcporter call arifos.apex_verdict query="Decide" session_id=test` |
| `reality_search` | External fact-checking | `mcporter call arifos.reality_search query="Verify X" session_id=test` |
| `vault_seal` | Immutable ledger recording | `mcporter call arifos.vault_seal session_id=test verdict=SEAL` |

---

## Verify Connection

### Health Check

```bash
curl https://aaamcp.arif-fazil.com/health
# Expected: {"status":"ok"}
```

### SSE Connection Test

```bash
curl -N https://aaamcp.arif-fazil.com/sse
# Expected: event: endpoint
#           data: /messages?session_id=<uuid>
```

### mcporter Test

```bash
mcporter list arifos --schema
```

---

## Transport Modes

| Mode | Endpoint | Use Case |
|------|----------|----------|
| **SSE** | `/sse` | Remote connections (OpenClaw, web clients) |
| **HTTP** | `/mcp` | Streamable HTTP transport |
| **STDIO** | N/A | Local agent (Claude Desktop, Claude Code) |

---

## Constitutional Floors Enforced

All tool calls pass through 13 Constitutional Floors:

- **F1 Amanah** — Reversibility audit
- **F2 Truth** — Factual fidelity ≥ 0.99
- **F9 Anti-Hantu** — No consciousness claims
- **F11 Authority** — Sovereign command validation
- **F12 Defense** — Injection scan

Verdicts: `SEAL` | `PARTIAL` | `SABAR` | `VOID` | `HOLD-888`

---

## Troubleshooting

### "SSE error: Non-200 status code (404)"

Use `/sse` endpoint, not `/mcp`:

```json
{
  "arifos": {
    "baseUrl": "https://aaamcp.arif-fazil.com/sse"
  }
}
```

### mcporter doesn't show tools

SSE transport requires the client to maintain an SSE connection. Some mcporter versions have limited SSE support. Workaround:

```bash
# Direct SSE test
curl -N https://aaamcp.arif-fazil.com/sse &
SESSION_ID=$(curl -s -m 2 https://aaamcp.arif-fazil.com/sse | grep session_id | sed 's/.*=//')

curl -X POST "https://aaamcp.arif-fazil.com/messages/?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Connection refused (self-hosted)

Ensure server is running and port is correct:

```bash
python -m aaa_mcp sse  # Starts on port 8080
PORT=3000 python -m aaa_mcp sse  # Custom port
```

---

## Example: Full OpenClaw Integration

```json
{
  "mcpServers": {
    "arifos": {
      "baseUrl": "https://aaamcp.arif-fazil.com/sse"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

---

## Links

- **GitHub:** https://github.com/ariffazil/arifOS
- **PyPI:** `pip install arifos`
- **Live Endpoint:** https://aaamcp.arif-fazil.com
- **Constitutional Docs:** https://apex.arif-fazil.com/llms.txt

---

*DITEMPA BUKAN DIBERI* 🔥
