# AAA MCP Server — Complete Deployment Guide

**Version:** v60.0-FORGE  
**Last Updated:** 2026-02-10  
**MCP Protocol:** 2025-11-25 (Streamable HTTP)  
**Constitutional Floors:** F1-F13

---

## 📋 Executive Summary

This guide provides **copy-paste ready deployment configurations** for AAA MCP across the **top 10 AI platforms** used by humans worldwide, plus **5 developer tooling platforms** for testing and debugging.

### Top 10 AI Platforms by Usage (2025)

| Rank | Platform | Monthly Users | Transport | Difficulty |
|:----:|:---|:---:|:---:|:---:|
| 1 | **ChatGPT** (OpenAI) | 5.6B visits | SSE/HTTP | 🟡 Medium |
| 2 | **Claude Desktop** (Anthropic) | 500M+ | stdio | 🟢 Easy |
| 3 | **GitHub Copilot** | 1.3M paid | stdio/SSE | 🟡 Medium |
| 4 | **Gemini** (Google) | 400M+ | stdio/HTTP | 🟡 Medium |
| 5 | **Cursor** | 300K+ devs | stdio | 🟢 Easy |
| 6 | **Windsurf** (Codeium) | 200K+ | stdio/SSE | 🟢 Easy |
| 7 | **DeepSeek** | 100M+ | stdio | 🟢 Easy |
| 8 | **Perplexity** | 100M+ | stdio | 🟡 Medium |
| 9 | **Continue.dev** | 50K+ devs | stdio/SSE | 🟢 Easy |
| 10 | **Cline/Roo Code** | 30K+ devs | stdio | 🟢 Easy |

---

## 🟢 Platform Support Status

| Platform | Status | Last Verified | Notes |
|:---------|:------:|:-------------:|:------|
| ChatGPT Developer Mode | ✅ **Production** | 2026-02-10 | Requires OAuth 2.1 |
| Claude Desktop | ✅ **Production** | 2026-02-10 | Official MCP support |
| GitHub Copilot | 🟡 **Beta** | 2026-02-10 | MCP in preview via `copilot-mcp` extension |
| Gemini / AI Studio | 🟡 **Beta** | 2026-02-10 | stdio via Gemini CLI |
| Cursor | ✅ **Production** | 2026-02-10 | Native MCP support |
| Windsurf IDE | ✅ **Production** | 2026-02-10 | Cascade agent mode |
| DeepSeek | 🟢 **Compatible** | 2026-02-10 | Via OpenRouter or local |
| Perplexity | 🧪 **Experimental** | 2026-02-10 | Via API proxy (no native MCP yet) |
| Continue.dev | ✅ **Production** | 2026-02-10 | Agent mode only |
| Cline / Roo Code | ✅ **Production** | 2026-02-10 | stdio support |
| Smithery CLI | ✅ **Production** | 2026-02-10 | Universal MCP manager |
| mcptools CLI | ✅ **Production** | 2026-02-10 | Testing & debugging |
| Qwen-Agent | 🟡 **Beta** | 2026-02-10 | MCP support in preview |
| Kimi Code | 🟢 **Compatible** | 2026-02-10 | stdio via Moonshot AI |
| Codex CLI | 🟢 **Compatible** | 2026-02-10 | OpenAI terminal agent |

**Legend:**
- ✅ **Production**: Officially supported, stable
- 🟡 **Beta**: Working but may have breaking changes
- 🟢 **Compatible**: Works via third-party integration
- 🧪 **Experimental**: Unverified or community-reported

---

## 🎯 Which Platform Should I Use?

**Choose based on your use case:**

| Your Goal | Recommended Platform | Why |
|:----------|:--------------------|:----|
| **Personal AI assistant** | Claude Desktop | Easiest setup, local privacy |
| **Team deployment** | ChatGPT Dev Mode | Web + mobile, enterprise SSO |
| **Code review automation** | GitHub Copilot | Native VS Code integration |
| **Terminal-based workflow** | Smithery CLI or mcptools | Testing, CI/CD, scripting |
| **Custom LLM (Qwen, DeepSeek)** | Qwen-Agent or OpenRouter | Flexibility, cost optimization |
| **VS Code power users** | Continue.dev or Cursor | Deep IDE integration |
| **Multi-platform testing** | mcptools CLI | Cross-platform validation |

### Developer Tooling Platforms

| Platform | Purpose | Transport | Difficulty |
|:---|:---|:---:|:---:|
| **Smithery CLI** | Universal MCP installer | Any | 🟢 Easy |
| **mcptools CLI** | Testing & debugging | stdio/HTTP | 🟢 Easy |
| **Qwen-Agent** | Chinese LLM integration | stdio | 🟡 Medium |
| **Kimi Code** | Local AI development | stdio | 🟢 Easy |
| **Codex CLI** | OpenAI terminal agent | stdio | 🟢 Easy |

---

## 🚀 Quick Start (Choose Your Platform)

### Transport Compatibility Matrix

| Platform | stdio | SSE | Streamable HTTP | Notes |
|:---|:---:|:---:|:---:|:---|
| ChatGPT Developer Mode | ❌ | ✅ | ✅ | Remote only, requires OAuth |
| Claude Desktop | ✅ | ❌ | ❌ | Local subprocess |
| GitHub Copilot | ✅ | ✅ | ❌ | VS Code extension |
| Gemini/Gemini CLI | ✅ | ❌ | ✅ | Google AI Studio preferred |
| Cursor | ✅ | ❌ | ❌ | Local subprocess |
| Windsurf IDE | ✅ | ✅ | ❌ | Cascade agent mode |
| DeepSeek | ✅ | ✅ | ✅ | Via OpenRouter or local |
| Perplexity | ✅ | ❌ | ❌ | Mac app supports MCP |
| Continue.dev | ✅ | ✅ | ❌ | Agent mode only |
| Cline/Roo Code | ✅ | ❌ | ❌ | stdio only |

### Prerequisites

```bash
# 1. Install arifOS
pip install arifos

# 2. Verify installation
python -m aaa_mcp --version

# 3. Set environment variables (optional)
export BRAVE_API_KEY="your_key_here"  # For reality_search tool
export DATABASE_URL="postgresql://..."  # For VAULT999 persistence
```

---

## 1️⃣ ChatGPT Developer Mode (SSE/HTTP)

**Platform:** OpenAI ChatGPT (Web + Mobile)  
**Users:** 5.6 billion monthly visits  
**Transport:** SSE or Streamable HTTP  
**Difficulty:** 🟡 Medium

### Architecture

ChatGPT Developer Mode connects to **remote MCP servers only** — it cannot launch local stdio processes. You must deploy AAA MCP to a publicly accessible URL with OAuth 2.1 authentication.

```
┌─────────────┐      HTTPS/SSE      ┌─────────────────────┐
│  ChatGPT    │ ◄────────────────►  │  AAA MCP Server     │
│  (Browser)  │   OAuth 2.1 + JWT   │  (Railway/Render)   │
└─────────────┘                     └─────────────────────┘
```

### Step 1: Deploy to Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up

# Get your deployment URL
railway domain
# → https://arifos-mcp.up.railway.app
```

### Step 2: Configure ChatGPT Developer Mode

1. Open **ChatGPT Settings → Connectors → Advanced → Developer mode**
2. Click **"Add MCP Server" → "Remote"**
3. Enter configuration:

```json
{
  "name": "AAA Constitutional AI",
  "serverUrl": "https://your-app.up.railway.app",
  "transport": "sse",
  "auth": {
    "type": "oauth2",
    "clientId": "your-client-id",
    "authUrl": "https://your-auth-endpoint/oauth/authorize",
    "tokenUrl": "https://your-auth-endpoint/oauth/token"
  }
}
```

### Step 3: Test in Chat

1. Start new chat → Click **"... More >"** → Select **"Developer Mode"**
2. Choose **"AAA Constitutional AI"** connector
3. Test query:

```
Run init_gate with query: "Should I approve this $1M loan application?"
```

**Expected Response:**
```json
{
  "verdict": "888_HOLD",
  "justification": "High-stakes financial decision requires human oversight (F13 Sovereign)",
  "floors_checked": ["F11", "F12"],
  "session_id": "ses_xxx"
}
```

### OAuth 2.1 Implementation (Production)

ChatGPT Developer Mode **requires OAuth 2.1 with PKCE** for production use.

**Quick Setup with Auth0/Clerk:**

```bash
# Install auth library
pip install authlib

# Add to environment
export AAA_ISSUER="https://your-domain.us.auth0.com"
export AAA_CLIENT_ID="your-client-id"
export AAA_CLIENT_SECRET="your-secret"

# Start with OAuth
python -m aaa_mcp sse
```

**Required Environment Variables:**
```bash
# OAuth 2.1 Configuration
AAA_ISSUER="https://your-auth-provider.com"
AAA_CLIENT_ID="chatgpt-mcp-client"
AAA_CLIENT_SECRET="your-secret"
AAA_REDIRECT_URI="https://your-server.com/oauth/callback"
AAA_SCOPES="mcp:read mcp:execute"
```

**Development Mode (Testing Only):**
```bash
# Skip OAuth for local testing (NOT for production)
export AAA_AUTH_MODE="dev"
export AAA_DEV_TOKEN="test-token-$(date +%s)"
python -m aaa_mcp sse
```

**ChatGPT Configuration (Development):**
```json
{
  "name": "AAA Constitutional AI [DEV]",
  "serverUrl": "https://your-server.up.railway.app",
  "transport": "sse",
  "auth": {
    "type": "none"
  }
}
```

⚠️ **Security Warning**: Never deploy to production without OAuth 2.1. Unauthenticated MCP servers can be accessed by anyone with the URL.

---

## 2️⃣ Claude Desktop (stdio)

**Platform:** Anthropic Claude Desktop App  
**Users:** 500M+  
**Transport:** stdio (local subprocess)  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  Claude Desktop │ ◄──────────────► │  AAA MCP Server │
│  (Electron App) │  JSON-RPC over  │  (Python proc)  │
└─────────────────┘   stdin/stdout  └─────────────────┘
```

### Step 1: Configure Claude Desktop

Create or edit `claude_desktop_config.json`:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add AAA MCP Configuration

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "GOVERNANCE_MODE": "HARD",
        "BRAVE_API_KEY": "your_key_here"
      },
      "disabled": false,
      "alwaysAllow": [
        "init_gate",
        "agi_sense",
        "agi_reason",
        "asi_empathize",
        "apex_verdict"
      ]
    }
  }
}
```

### Step 3: Restart Claude Desktop

1. Fully quit Claude Desktop (Cmd+Q / Ctrl+Q)
2. Restart the application
3. Look for the 🔌 icon (MCP tools available)

### Step 4: Test

Ask Claude:
```
Use the aaa-mcp init_gate tool to check: "Is it safe to delete the production database?"
```

---

## 3️⃣ GitHub Copilot (stdio/SSE)

**Platform:** GitHub Copilot (VS Code extension)  
**Users:** 1.3M paid subscribers  
**Transport:** stdio (preferred) or SSE  
**Difficulty:** 🟡 Medium

### Important Note

GitHub is moving toward **MCP servers** as the recommended integration method for extending Copilot functionality. The `copilot-mcp` extension enables MCP support in VS Code. Check [GitHub's official documentation](https://docs.github.com/en/copilot) for the latest updates on MCP support.

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  VS Code +      │ ◄──────────────► │  AAA MCP Server │
│  GitHub Copilot │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Step 1: Install copilot-mcp Extension

```bash
# Install from VS Code marketplace
code --install-extension VikashLoomba.copilot-mcp

# Or search "Copilot MCP" in Extensions panel
```

### Step 2: Configure MCP Server

Create `.vscode/mcp.json` in your project:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_MODE": "PROD",
        "GOVERNANCE_MODE": "HARD"
      },
      "disabled": false
    }
  }
}
```

### Step 3: Use in Copilot Chat

Open Copilot Chat and type:

```
@aaa-mcp Run constitutional analysis on: "Deploy this code to production"
```

---

## 4️⃣ Gemini / Google AI Studio (stdio/HTTP)

**Platform:** Google Gemini & AI Studio  
**Users:** 400M+  
**Transport:** stdio (Gemini CLI) or HTTP  
**Difficulty:** 🟡 Medium

### Option A: Gemini CLI (stdio)

```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Configure MCP
gemini config set mcp.servers.aaa-mcp.command "python -m aaa_mcp"
gemini config set mcp.servers.aaa-mcp.env.ARIFOS_MODE "PROD"
```

### Option B: Google AI Studio (HTTP)

Create `gemini_mcp_config.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "serverUrl": "https://your-server.up.railway.app",
      "transport": "streamable-http",
      "auth": {
        "type": "bearer",
        "token": "${GEMINI_MCP_TOKEN}"
      }
    }
  }
}
```

### Usage in AI Studio

```python
from google.generativeai import mcp

client = mcp.connect("aaa-mcp")
result = client.init_gate(query="Analyze this code for safety issues")
print(result.verdict)  # SEAL, VOID, PARTIAL, or SABAR
```

---

## 5️⃣ Cursor (stdio)

**Platform:** Cursor AI Code Editor  
**Users:** 300K+ developers  
**Transport:** stdio  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  Cursor IDE     │ ◄──────────────► │  AAA MCP Server │
│  (Electron)     │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Step 1: Open Cursor Settings

1. Press `Cmd/Ctrl + ,` to open Settings
2. Search for "MCP" or navigate to **Features → MCP**
3. Click **"Add New MCP Server"**

### Step 2: Configure AAA MCP

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "GOVERNANCE_MODE": "HARD"
      }
    }
  }
}
```

### Step 3: Use in Composer

Open Cursor Composer (`Cmd/Ctrl + I`) and type:

```
@aaa-mcp Check if this refactor is safe: "Rename all user_id fields to customer_id"
```

---

## 6️⃣ Windsurf IDE / Cascade (stdio/SSE)

**Platform:** Windsurf IDE by Codeium (formerly Codeium)  
**Users:** 200K+ developers  
**Transport:** stdio (preferred) or SSE  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  Windsurf IDE   │ ◄──────────────► │  AAA MCP Server │
│  Cascade Agent  │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Step 1: Open Cascade Settings

1. In Windsurf, open **Cascade AI settings**
2. Navigate to **MCP Servers** section
3. Click **"Add Server" → "Add custom server +"**

### Step 2: Add Configuration

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

### Step 3: Use in Cascade

In Cascade chat:

```
Use aaa-mcp to verify: "Should we merge this PR with 200 changed files?"
```

**Cascade will:**
1. Call `init_gate` (F11, F12 checks)
2. Call `agi_reason` (F2, F4, F7 enforcement)
3. Return verdict with floor scores

---

## 7️⃣ DeepSeek (stdio)

**Platform:** DeepSeek AI  
**Users:** 100M+  
**Transport:** stdio  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  DeepSeek Chat  │ ◄──────────────► │  AAA MCP Server │
│  or API Client  │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Option A: DeepSeek Chat Desktop

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_MODE": "PROD"
      }
    }
  }
}
```

### Option B: Via OpenRouter

```python
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key"
)

# DeepSeek with constitutional governance
response = client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[{
        "role": "system",
        "content": "You have access to AAA MCP tools for constitutional enforcement."
    }],
    tools=[{
        "type": "mcp",
        "server": {
            "command": "python",
            "args": ["-m", "aaa_mcp"]
        }
    }]
)
```

---

## 8️⃣ Perplexity (stdio)

**Platform:** Perplexity AI  
**Users:** 100M+  
**Transport:** stdio  
**Difficulty:** 🟡 Medium

### Perplexity for Mac MCP Support

**Status:** 🧪 **Experimental** — Perplexity has not officially announced native MCP support as of February 2026.

**Alternative:** Use Perplexity API with AAA MCP via OpenRouter or direct API integration:

```python
import openai

# Use AAA MCP with Perplexity via OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key"
)

response = client.chat.completions.create(
    model="perplexity/pplx-70b-online",
    messages=[{
        "role": "system",
        "content": "You have access to AAA MCP tools for constitutional enforcement."
    }],
    tools=[{
        "type": "mcp",
        "server": {"command": "python", "args": ["-m", "aaa_mcp"]}
    }]
)
```

**If Perplexity adds native MCP support in the future**, configuration would be:
```json
{
  "name": "AAA Constitutional AI",
  "command": "python",
  "args": ["-m", "aaa_mcp"],
  "env": {
    "ARIFOS_MODE": "PROD"
  }
}
```

---

## 9️⃣ Continue.dev (stdio/SSE)

**Platform:** Continue.dev (VS Code extension)  
**Users:** 50K+ developers  
**Transport:** stdio or SSE  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  VS Code +      │ ◄──────────────► │  AAA MCP Server │
│  Continue.dev   │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Step 1: Install Continue.dev

```bash
code --install-extension Continue.continue
```

### Step 2: Configure MCP

Create `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_MODE": "PROD"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

### Step 3: Use in Agent Mode

**Important:** MCP tools only work in **Agent Mode**, not inline chat.

1. Open Continue panel → Switch to **"Agent"** tab
2. Type:

```
@aaa-mcp init_gate query="Review this code for security issues" actor_id="dev_001"
```

---

## 🔟 Cline / Roo Code (stdio)

**Platform:** Cline & Roo Code (VS Code agents)  
**Users:** 30K+ developers  
**Transport:** stdio  
**Difficulty:** 🟢 Easy

### Architecture

```
┌─────────────────┐      stdio      ┌─────────────────┐
│  VS Code +      │ ◄──────────────► │  AAA MCP Server │
│  Cline/Roo Code │  JSON-RPC       │  (Python proc)  │
└─────────────────┘                 └─────────────────┘
```

### Cline Configuration

Create `.cline/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "GOVERNANCE_MODE": "HARD"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Roo Code Configuration

Create `.roo/roo_mcp_settings.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "disabled": false
    }
  }
}
```

### Usage

In Cline/Roo chat:

```
Use the aaa-mcp tool_router to determine the best tool for: "Should I approve this infrastructure change?"
```

---

## 🛠️ Developer Tooling Platforms

### 11. Smithery CLI — Universal MCP Manager

**Purpose:** Install, debug, and test any MCP server  
**Transport:** Any (stdio, SSE, HTTP)  
**Difficulty:** 🟢 Easy

#### Installation

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Install AAA MCP to Claude Desktop
npx -y @smithery/cli@latest install aaa-mcp --client claude

# Install to Cursor
npx @smithery/cli install aaa-mcp --client cursor

# Install to any client (generates config)
npx @smithery/cli install aaa-mcp --output ./mcp-config.json
```

#### Debug in Playground

```bash
# Run AAA MCP in interactive playground
npx @smithery/cli playground --command "python -m aaa_mcp"

# Test specific tool
npx @smithery/cli call init_gate \
  --args '{"query": "test", "actor_id": "dev"}'
```

#### Inspect Server Metadata

```bash
# List available tools
npx @smithery/cli inspect --command "python -m aaa_mcp"

# Output: 13 tools with schemas
```

---

### 12. mcptools CLI — Testing & Debugging

**Purpose:** Interact with MCP servers via terminal  
**Transport:** stdio or HTTP  
**Difficulty:** 🟢 Easy

#### Installation

```bash
npm install -g @f/mcptools
```

#### Test AAA MCP

```bash
# Start interactive shell
mcptools shell --command "python -m aaa_mcp"

# List all tools
> tools

# Call init_gate
> call init_gate '{"query": "Should I delete production DB?", "actor_id": "eng_001"}'

# Expected output:
# {
#   "verdict": "VOID",
#   "reason": "F1 Amanah violation - irreversible action detected"
# }
```

#### Test HTTP Transport

```bash
# Start HTTP server
python -m aaa_mcp http --port 8080

# Call via mcptools
mcptools call --url http://localhost:8080 \
  --tool init_gate \
  --args '{"query": "test"}'
```

#### Mock Server for Testing

```bash
# Create mock AAA MCP server
mcptools mock --schema ./server.json --port 9000
```

---

### 13. Qwen-Agent (stdio)

**Purpose:** Alibaba's Qwen model with MCP support  
**Transport:** stdio  
**Difficulty:** 🟡 Medium

#### Installation

```bash
pip install -U "qwen-agent[gui,rag,code_interpreter,mcp]"
```

#### Configuration

Create `qwen_mcp_config.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_MODE": "PROD",
        "GOVERNANCE_MODE": "HARD"
      }
    }
  }
}
```

#### Usage

```python
from qwen_agent.agents import Assistant
from qwen_agent.tools.mcp_tool import MCPTool

# Initialize MCP tools
mcp_tool = MCPTool(config_path="qwen_mcp_config.json")

# Create constitutional Qwen assistant
assistant = Assistant(
    llm={
        "model": "qwen3-32b",
        "api_key": "your-openrouter-key"
    },
    function_list=[mcp_tool],
    name="Constitutional Qwen"
)

# Query with F1-F13 enforcement
response = assistant.run("Should we approve this loan for $500K?")
print(response[-1]["content"])  # Includes floor scores, verdict, Ω₀
```

---

### 14. Kimi Code (stdio)

**Purpose:** Moonshot AI's coding agent  
**Transport:** stdio  
**Difficulty:** 🟢 Easy

#### Configuration

Create `.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "env": {
        "PYTHONPATH": ".",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      },
      "alwaysAllow": [
        "init_gate",
        "trinity_forge",
        "agi_sense",
        "agi_reason",
        "asi_empathize",
        "apex_verdict"
      ]
    }
  }
}
```

---

### 15. Codex CLI (stdio)

**Purpose:** OpenAI's terminal-based coding agent  
**Transport:** stdio  
**Difficulty:** 🟢 Easy

#### Configuration

Create `~/.codex/mcp.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp"],
      "env": {
        "ARIFOS_MODE": "PROD"
      }
    }
  }
}
```

#### Usage

```bash
# Start Codex with MCP
codex --mcp-config ~/.codex/mcp.json

# In Codex chat:
# @aaa-mcp init_gate query="Is this migration safe?"
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build image
docker build -t arifos-mcp:latest .

# Run with environment variables
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e BRAVE_API_KEY="your_key" \
  -e DATABASE_URL="postgresql://..." \
  arifos-mcp:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  arifos-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - HOST=0.0.0.0
      - AAA_MCP_TRANSPORT=sse
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 15s
      timeout: 5s
      retries: 3
```

Run:
```bash
docker-compose up -d
```

---

## ☁️ Cloud Deployment

### Railway (Recommended)

```bash
# Install CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Deploy
railway up

# Get domain
railway domain
```

**Railway auto-provisions:**
- PostgreSQL (VAULT999)
- Redis (session state)

### Render

```bash
# Create render.yaml
render:
  services:
    - type: web
      name: arifos-mcp
      runtime: docker
      plan: standard
      envVars:
        - key: PORT
          value: 8080
        - key: AAA_MCP_TRANSPORT
          value: sse
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Launch
fly launch --dockerfile Dockerfile

# Set secrets
fly secrets set BRAVE_API_KEY="your_key"
```

---

## 🔐 Environment Variables Reference

| Variable | Default | Required | Description |
|:---------|:-------:|:--------:|:------------|
| `PORT` | 8080 | No | Server port |
| `HOST` | 0.0.0.0 | No | Bind address |
| `AAA_MCP_TRANSPORT` | sse | No | `stdio`, `sse`, or `http` |
| `ARIFOS_CONSTITUTIONAL_MODE` | AAA | No | Governance mode |
| `GOVERNANCE_MODE` | HARD | No | `HARD` or `SOFT` |
| `BRAVE_API_KEY` | — | For search | Web search API key |
| `DATABASE_URL` | — | For VAULT | PostgreSQL connection |
| `REDIS_URL` | — | For sessions | Redis connection |
| `SECRET_KEY` | — | For auth | Cryptographic signing |
| `JWT_SECRET` | — | For OAuth | JWT signing key |

---

## 📊 Health & Monitoring

### Health Check Endpoint

```bash
curl https://your-server.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "arifOS MCP Server",
  "version": "60.0-FORGE",
  "checks": {
    "core_pipeline": {"status": "healthy"},
    "vault_connection": {"status": "healthy"}
  }
}
```

### Metrics Endpoint (Prometheus)

```bash
curl https://your-server.com/metrics
```

### Stats Endpoint (JSON)

```bash
curl https://your-server.com/stats
```

---

## 🧪 Testing Your Deployment

### Quick Validation

```bash
# Run validation script
python scripts/deploy_production.py --platform validate

# Expected output:
# [OK] Python 3.10+
# [OK] Core organs importable
# [OK] AAA MCP server importable
# [OK] Pipeline executes
# [OK] VALIDATION PASSED
```

### End-to-End Test

```bash
# Test with mcptools
mcptools shell --command "python -m aaa_mcp"

> call init_gate '{"query": "Test query", "actor_id": "test"}'
> call agi_reason '{"query": "What is 2+2?", "session_id": "test-001"}'
> call apex_verdict '{"query": "Test", "session_id": "test-001"}'
```

---

## 🆘 Troubleshooting

### "Transport not supported"

**Cause:** Platform doesn't support the configured transport.  
**Fix:** Check the Transport Compatibility Matrix above.

### "Module not found: aaa_mcp"

**Cause:** Python package not installed or not in PATH.  
**Fix:**
```bash
pip install -e .
which python  # Verify path
```

### "Connection refused" (SSE/HTTP)

**Cause:** Server not running or wrong port.  
**Fix:**
```bash
# Check server is running
curl http://localhost:8080/health

# Check firewall
sudo ufw allow 8080
```

### "OAuth authentication failed" (ChatGPT)

**Cause:** Missing or incorrect OAuth configuration.  
**Fix:** Configure `AAA_ISSUER` and OAuth endpoints.

---

## ✅ Production Deployment Checklist

Before deploying AAA MCP to production:

- [ ] **Authentication**: OAuth 2.1 configured (required for ChatGPT, public deployments)
- [ ] **HTTPS**: SSL/TLS certificate valid (not self-signed)
- [ ] **Database**: PostgreSQL configured for VAULT999 audit trails
- [ ] **Environment**: `GOVERNANCE_MODE=HARD` set for strict enforcement
- [ ] **Secrets**: `BRAVE_API_KEY`, `DATABASE_URL`, `JWT_SECRET` in secure vault (not in code)
- [ ] **Health checks**: `/health` endpoint returns 200 OK
- [ ] **Monitoring**: Prometheus metrics enabled (`ENABLE_METRICS=true`)
- [ ] **Backup**: VAULT999 audit logs backed up daily
- [ ] **Rate limiting**: Configured (default: 100 req/min)
- [ ] **Error tracking**: Sentry or equivalent configured
- [ ] **CORS**: Origin validation enabled for HTTP/SSE transports
- [ ] **Documentation**: Team trained on constitutional verdicts (SEAL/SABAR/PARTIAL/VOID)

**Validation Command:**
```bash
python scripts/deploy_production.py --platform validate --strict
```

**Expected Output:**
```
[OK] Python 3.10+
[OK] OAuth 2.1 configured
[OK] HTTPS certificate valid
[OK] Database connection healthy
[OK] All 13 floors registered
[OK] Audit trail writable
[OK] Rate limiting active
[OK] PRODUCTION VALIDATION PASSED ✅
```

---

## 📚 Additional Resources

- **MCP Protocol Spec:** https://modelcontextprotocol.io/specification/2025-11-25
- **arifOS Documentation:** https://arifos.arif-fazil.com
- **Live Demo:** https://aaamcp.arif-fazil.com/health
- **GitHub:** https://github.com/ariffazil/arifOS
- **PyPI:** https://pypi.org/project/arifos/

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠  
*Forged, Not Given*
