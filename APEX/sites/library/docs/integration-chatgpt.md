---
id: integration-chatgpt
title: ChatGPT
sidebar_position: 3
description: Connect arifOS to ChatGPT via MCP for cloud-based constitutional governance
---

# ChatGPT Integration

Connect **arifOS** to [ChatGPT](https://chatgpt.com/) via the Model Context Protocol (MCP) for cloud-based constitutional AI governance.

---

## Overview

ChatGPT supports MCP servers through **remote HTTP connections** in two modes:
- **Chat Mode**: Interactive conversations with MCP tools
- **Deep Research Mode**: Comprehensive research with citations

:::tip Requirements
- **ChatGPT Plus, Pro, Team, Enterprise, or Edu** subscription
- **Developer Mode** enabled (for Chat mode)
- Publicly accessible arifOS server (or use ngrok for development)
:::

:::note Free Tier
Free ChatGPT users can use MCP servers in **Deep Research mode only**. Chat mode requires Developer Mode which is available on paid plans.
:::

---

## Deployment Options

### Option 1: Public Server (Production)

Deploy arifOS to a publicly accessible HTTPS endpoint:

```bash
# Using Docker
docker run -d \
  --name arifos \
  -p 8080:8080 \
  -e ARIFOS_GOVERNANCE_SECRET=your-secret \
  -e JINA_API_KEY=your-jina-key \
  arifos/arifosmcp:latest
```

Your server will be available at:
- **MCP Endpoint**: `https://your-domain.com/mcp`
- **Dashboard**: `https://your-domain.com/dashboard/`

### Option 2: Development with ngrok

For local development, expose your local server:

```bash
# Terminal 1: Start arifOS
python -m arifosmcp.runtime http --host 0.0.0.0 --port 8080

# Terminal 2: Expose via ngrok
ngrok http 8080

# Note the HTTPS URL (e.g., https://abc123.ngrok.io)
```

---

## Connect to ChatGPT

### Step 1: Enable Developer Mode (Chat Mode)

1. Open ChatGPT
2. Go to **Settings** → **Connectors**
3. Under **Advanced**, toggle **Developer Mode** to enabled

### Step 2: Create MCP Connector

1. In **Settings** → **Connectors**, click **Create**
2. Enter details:
   * **Name**: arifOS Constitutional AI
   * **Server URL**: `https://your-server.com/mcp`
3. Check **I trust this provider**
4. Add authentication if needed (see below)
5. Click **Create**

Use the three URLs deliberately:
- **Widget domain / app origin**: `https://your-server.com`
- **MCP connector URL**: `https://your-server.com/mcp`
- **Dashboard page**: `https://your-server.com/dashboard/`

Do not put `/mcp` or `/dashboard/` inside the widget domain field. The widget domain is the origin only.

### Step 3: Use in Chat

1. Start a new chat
2. Click the **+** button → **More** → **Developer Mode**
3. **Enable your arifOS connector** (must be added to each chat)
4. Now you can use constitutional tools

---

## Authentication

### Public Server with API Key

If your arifOS server requires authentication:

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://your-server.com/mcp",
      "headers": {
        "X-ARIFOS-API-KEY": "your-api-key"
      }
    }
  }
}
```

### Bearer Token

```json
{
  "mcpServers": {
    "arifOS": {
      "url": "https://your-server.com/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

---

## Chat Mode Usage

### Constitutional Web Search

Ask ChatGPT:
> "Search for quantum computing breakthroughs and verify with arifOS"

ChatGPT will:
1. Call `search_reality` via arifOS
2. Jina Reader extracts clean Markdown from results
3. F2 Truth floor validates evidence
4. F12 Defense wraps external content

### Risk-Classified Operations

Ask ChatGPT:
> "List files in my project directory"

- Risk: **LOW** → Executes immediately

Ask ChatGPT:
> "Run a shell command to clean up temp files"

- Risk: **MODERATE** → May ask for confirmation

Ask ChatGPT:
> "Delete all files in the database"

- Risk: **CRITICAL** → **888_HOLD triggered**
- Requires explicit `confirm_dangerous=True`
- Human must approve via 888 Judge

---

## Deep Research Mode

Deep Research provides systematic information retrieval with citations.

:::warning Search/Fetch Required
Deep Research mode requires search and fetch-capable behavior. arifOS provides:
- `search_reality` — Web search with evidence
- `ingest_evidence` — URL content extraction
:::

### Using Deep Research

1. Start a new chat
2. Click **+** → **Deep Research**
3. Select your arifOS server as a source
4. Ask research questions

### Example

Ask ChatGPT:
> "Research constitutional AI governance frameworks and their enforcement mechanisms"

ChatGPT will:
1. Use `search_reality` to find papers
2. Use `ingest_evidence` to extract full text
3. Cite sources with arifOS verification
4. Present findings with confidence scores

---

## Tool Annotations

Control confirmation behavior with tool annotations:

| Annotation | Behavior |
|------------|----------|
| **Read-only** | Skip confirmations |
| **Destructive** | Always require confirmation |
| **Idempotent** | Skip if safe to retry |

arifOS automatically sets these based on constitutional risk classification:
- `search_reality`, `audit_rules`, `check_vital` → Read-only
- `ingest_evidence`, `session_memory` → Usually operator-safe
- `arifOS_kernel` → Governed by risk tier and floor checks

---

## Constitutional Guarantees

Every ChatGPT interaction through arifOS enforces:

| Floor | Cloud Context |
|-------|--------------|
| **F2 Truth** | Web grounding via Jina Reader, τ≥0.99 threshold |
| **F4 Clarity** | Clean Markdown extraction reduces entropy |
| **F7 Humility** | Uncertainty markers when confidence low |
| **F11 Authority** | Your ChatGPT account = Sovereign identity |
| **F12 Defense** | Untrusted envelope for all external content |
| **F13 Sovereignty** | You control all critical operations |

---

## Environment Variables

Your deployed arifOS server needs these environment variables:

```bash
# Required
ARIFOS_GOVERNANCE_SECRET=$(openssl rand -hex 32)

# Recommended for search quality
JINA_API_KEY=jina_...           # Primary search backend
PERPLEXITY_API_KEY=pplx_...     # Fallback
BRAVE_API_KEY=BSA...            # Fallback

# Optional
ARIFOS_ML_FLOORS=1              # Enable ML empathy scoring
DATABASE_URL=postgresql://...   # For VAULT999 ledger
```

---

## Troubleshooting

### "Server rejected" error

ChatGPT requires servers to have search/fetch tools for Deep Research. arifOS has:
- ✅ `search_reality` — Web search
- ✅ `ingest_evidence` — URL extraction

Ensure your server is properly exposing these tools.

### "Cannot connect to server"

1. Verify your server is publicly accessible:
```bash
curl https://your-server.com/health
```

2. Check firewall rules (port 443/80 open)

3. Ensure HTTPS (ChatGPT requires secure connections)

### "NO_API_KEY" in search results

Your server needs search API keys:

```bash
docker run -d \
  --name arifos \
  -p 8080:8080 \
  -e JINA_API_KEY=jina_... \
  arifos/arifosmcp:latest
```

Get free keys:
- **Jina Reader**: https://jina.ai (10M tokens)
- **Perplexity**: https://perplexity.ai
- **Brave**: https://brave.com/search/api

### Connector not showing in Developer Mode

1. Ensure Developer Mode is toggled ON
2. Create the connector first (Settings → Connectors)
3. In chat, click **+** → **More** → **Developer Mode**
4. **Enable** the connector explicitly (not automatic)

---

## Security Considerations

:::warning Cloud Deployment
When deploying arifOS for ChatGPT:

1. **Use HTTPS only** — ChatGPT requires secure connections
2. **Set strong governance secret** — Protects against token forgery
3. **Enable authentication** — API key or bearer token
4. **Rate limiting** — Prevent abuse (built-in to arifOS)
5. **Monitor logs** — Watch for suspicious activity
:::

---

## Comparison: ChatGPT vs Claude vs Gemini

| Feature | ChatGPT | Claude Desktop | Gemini CLI |
|---------|---------|----------------|------------|
| **Transport** | HTTP/Remote | STDIO/Local | STDIO/Local |
| **Mode** | Cloud | Local | Local |
| **Best For** | Team sharing | Privacy-first | Terminal users |
| **Setup** | Deploy server | Install locally | Install locally |
| **Offline** | ❌ No | ✅ Yes | ✅ Yes |
| **Speed** | Network latency | Fast (local) | Fast (local) |

---

## Next Steps

- [Public Contract](/public-contract) — Learn the 8 public tools
- [Claude Desktop Integration](/integration-claude) — Local alternative
- [Gemini CLI Integration](/integration-gemini) — Terminal option
- [Deployment Guide](/deployment) — Production deployment

---

*Ditempa Bukan Diberi — Forged, Not Given*
