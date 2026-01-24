# AAA_MCP — Constitutional AI MCP Server

**An MCP Server for Constitutional AI Governance** | v51.1.0 SEALED

[![MCP](https://img.shields.io/badge/MCP-2024--11-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/python-3.10+-green)](https://python.org)
[![Transport](https://img.shields.io/badge/transport-stdio%20%7C%20SSE-orange)](https://modelcontextprotocol.io/docs/concepts/architecture)
[![Version](https://img.shields.io/badge/version-v51.1.0-purple)]()
[![SEAL Rate](https://img.shields.io/badge/SEAL%20rate-0.85+-brightgreen)]()

---

## What is AAA_MCP?

**AAA_MCP** is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides **constitutional AI governance** tools. It enables AI applications (like Claude Desktop, Cursor, VS Code) to make decisions through a structured governance framework with safety guarantees.

Unlike typical MCP servers that provide file access (Filesystem MCP) or web search (Brave Search MCP), AAA_MCP provides **judgment and safety validation** for AI outputs.

```
┌────────────────────────────────────────────────────────────────┐
│                    What AAA_MCP Does                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   AI Application                AAA_MCP Server                 │
│   (Claude, etc.)                                               │
│        │                                                       │
│        │ "Should I execute                                     │
│        │  this code?"          ┌─────────────────────┐         │
│        │ ─────────────────────►│  Constitutional     │         │
│        │                       │  Validation         │         │
│        │                       │  ───────────────    │         │
│        │                       │  • Truth Check      │         │
│        │                       │  • Safety Check     │         │
│        │                       │  • Authority Check  │         │
│        │◄───────────────────── └─────────────────────┘         │
│        │  SEAL (approved)                                      │
│        │  VOID (rejected)                                      │
│        │  SABAR (needs human)                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Why Use AAA_MCP?

### The Problem

AI assistants make decisions constantly, but:
- ❌ No audit trail of what was decided and why
- ❌ No consistent safety validation framework
- ❌ No structured way to pause for human approval
- ❌ No governance for high-stakes actions

### The Solution

AAA_MCP provides a **5-tool governance pipeline**:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `000_init` | Start a governed session | Every new conversation |
| `agi_genius` | Analyze and reason | When thinking through problems |
| `asi_act` | Validate safety and empathy | Before taking actions |
| `apex_judge` | Make final decision | Before delivering output |
| `999_vault` | Log decision immutably | After every decision |

---

## How Does MCP Work?

The [Model Context Protocol](https://modelcontextprotocol.io) is an open standard by Anthropic for connecting AI applications to external tools.

### MCP Architecture (Official Spec)

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐                                          │
│   │    MCP HOST     │  Claude Desktop, Cursor, VS Code, etc.  │
│   │   (AI App)      │                                          │
│   └────────┬────────┘                                          │
│            │                                                    │
│   ┌────────▼────────┐                                          │
│   │   MCP CLIENT    │  Built into the host application        │
│   │                 │  Manages connections to servers          │
│   └────────┬────────┘                                          │
│            │                                                    │
│            │  JSON-RPC 2.0 over stdio or HTTP/SSE              │
│            │                                                    │
│   ┌────────▼────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │   MCP SERVER    │  │  MCP SERVER  │  │  MCP SERVER  │     │
│   │   (AAA_MCP)     │  │ (Filesystem) │  │  (GitHub)    │     │
│   └─────────────────┘  └──────────────┘  └──────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Key Concepts:
─────────────
• HOST: The AI application (Claude Desktop, Cursor)
• CLIENT: Component inside the host that talks to servers
• SERVER: External program providing tools (this is AAA_MCP)
• TRANSPORT: How messages travel (stdio for local, SSE for cloud)
• TOOLS: Functions the AI can call (like our 5 governance tools)
```

### MCP Primitives

MCP servers can expose three types of things:

| Primitive | Description | AAA_MCP Usage |
|-----------|-------------|---------------|
| **Tools** | Functions the AI can call | ✅ 5 governance tools |
| **Resources** | Data sources for context | ❌ Not used |
| **Prompts** | Reusable interaction templates | ❌ Not used |

AAA_MCP is a **tools-only** MCP server focused on judgment and validation.

---

## Installation

### Option 1: Claude Desktop (Local)

Add to your `~/.claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos-aaa": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

### Option 2: Cursor / VS Code

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "arifos-aaa": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

### Option 3: Cloud Deployment (SSE)

```bash
# Run SSE server
python -m AAA_MCP sse

# Connect via URL
# https://your-deployment.railway.app/sse
```

---

## Platform Support Matrix

| Platform | Status | Transport | Config Location | Recommended Model |
|----------|--------|-----------|-----------------|-------------------|
| **Claude Desktop** | ✅ Production | stdio | `%APPDATA%\Claude\` (Win) / `~/.config/Claude/` (Linux) | Claude 3.7 Sonnet |
| **Cursor** | ✅ Production | stdio | `~/.cursor/mcp.json` | Claude or GPT-4 |
| **Cline (VS Code)** | ✅ Production | stdio | `.vscode/mcp.json` | Claude or GPT-4 |
| **Continue.dev** | ✅ Production | stdio | `~/.continue/config.json` | Llama 3, Mixtral |
| **ChatGPT Dev Mode** | ✅ Production | HTTP/SSE | Custom Action | GPT-4 Turbo |
| **Ollama (Local)** | ✅ Production | HTTP/SSE | Bridge script | Llama 3 70B |
| **Cody (Sourcegraph)** | ⏳ Experimental | - | - | Pending support |
| **Kimi (Moonshot)** | ⏳ Experimental | - | - | Pending MCP support |
| **GitHub Copilot** | ❌ Not Supported | - | - | No MCP support |

### AI Model Compatibility

| Model | Expected SEAL Rate | Transport | Notes |
|-------|-------------------|-----------|-------|
| Claude 3.7 Sonnet | 0.82–0.85 | stdio | Best MCP support |
| GPT-4 Turbo | 0.75–0.80 | HTTP/SSE | Via ChatGPT Actions |
| Gemini 1.5 Pro | 0.70–0.78 | stdio (via Claude bridge) | Experimental |
| Llama 3 70B | 0.78–0.82 | HTTP/SSE | Local via Ollama |
| Llama 3 8B | 0.50–0.65 | HTTP/SSE | Lower assurance |
| Mixtral 8x7B | 0.60–0.75 | HTTP/SSE | Good local option |

---

## The 5 Tools Explained

### Tool 1: `000_init` — The Gate

**What it does:** Starts a governed session. Every conversation should begin here.

**When to use:** At the start of any task that needs governance.

**Example:**
```json
{
  "tool": "000_init",
  "arguments": {
    "action": "init",
    "query": "I need to delete some files"
  }
}
```

**Returns:**
- `session_id`: Unique ID for this session
- `lane`: HARD (technical), SOFT (discussion), PHATIC (greeting)
- `authority`: Whether user has elevated permissions

---

### Tool 2: `agi_genius` — The Mind

**What it does:** Analyzes and reasons about problems. This is the "thinking" phase.

**When to use:** When you need to break down a problem or validate truth claims.

**Actions:**
| Action | Purpose |
|--------|---------|
| `sense` | Classify the type of request |
| `think` | Reason through the problem |
| `reflect` | Check clarity and entropy |
| `atlas` | Map to governance requirements |
| `forge` | Refine with humility bounds |
| `full` | Run complete pipeline |

**Example:**
```json
{
  "tool": "agi_genius",
  "arguments": {
    "action": "full",
    "query": "Is it safe to run rm -rf /tmp/*?",
    "session_id": "abc-123"
  }
}
```

---

### Tool 3: `asi_act` — The Heart

**What it does:** Validates safety and empathy. This is the "feeling" phase.

**When to use:** Before taking any action that affects users or systems.

**Actions:**
| Action | Purpose |
|--------|---------|
| `evidence` | Ground claims in sources |
| `empathize` | Consider impact on affected parties |
| `align` | Check against safety constraints |
| `witness` | Gather agreement from stakeholders |
| `full` | Run complete pipeline |

**Example:**
```json
{
  "tool": "asi_act",
  "arguments": {
    "action": "empathize",
    "proposal": "Delete user's backup files",
    "stakeholders": ["user", "system"]
  }
}
```

---

### Tool 4: `apex_judge` — The Soul

**What it does:** Makes the final decision. This is the "judging" phase.

**When to use:** Before delivering any output to the user.

**Returns one of:**
- `SEAL`: Approved - proceed with output
- `SABAR`: Pause - needs human approval
- `VOID`: Rejected - do not proceed

**Example:**
```json
{
  "tool": "apex_judge",
  "arguments": {
    "action": "judge",
    "query": "Original user question",
    "response": "My proposed answer",
    "agi_result": { ... },
    "asi_result": { ... }
  }
}
```

---

### Tool 5: `999_vault` — The Seal

**What it does:** Logs the decision immutably. This is the "recording" phase.

**When to use:** After every decision to create an audit trail.

**Example:**
```json
{
  "tool": "999_vault",
  "arguments": {
    "action": "seal",
    "verdict": "SEAL",
    "session_id": "abc-123"
  }
}
```

---

## How AAA_MCP Compares to Other MCP Servers

| MCP Server | Purpose | Tools Provided |
|------------|---------|----------------|
| **Filesystem** | File operations | read, write, search files |
| **GitHub** | Repository access | create issues, read code |
| **Brave Search** | Web search | search the internet |
| **Puppeteer** | Browser automation | click, type, screenshot |
| **Memory** | Persistent memory | store/retrieve knowledge |
| **Sequential Thinking** | Reasoning | step-by-step problem solving |
| **AAA_MCP** | **Governance** | **validate, judge, audit** |

### Key Difference

Most MCP servers provide **capabilities** (what the AI *can* do).

AAA_MCP provides **governance** (whether the AI *should* do it).

```
┌─────────────────────────────────────────────────────────────────┐
│                    Capability vs Governance                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Filesystem MCP:  "Here's how to delete a file"  (capability) │
│                                                                 │
│   AAA_MCP:         "Should you delete this file?" (governance) │
│                    → SEAL (yes, safe)                           │
│                    → VOID (no, dangerous)                       │
│                    → SABAR (ask the human first)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Component Overview

```
AAA_MCP/
├── __init__.py      # Package exports and version
├── __main__.py      # Entry point: python -m AAA_MCP
├── server.py        # MCP server with 5 tools
├── bridge.py        # Routes tools to arifOS core engines
└── sse.py           # HTTP/SSE transport for cloud deployment
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      AAA_MCP Data Flow                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. MCP Client sends JSON-RPC request                          │
│     ───────────────────────────────────────────────►           │
│                                                                 │
│  2. server.py receives request, identifies tool                │
│     ┌─────────────────────────────────────────────────┐        │
│     │  Tool: "agi_genius"                             │        │
│     │  Arguments: { action: "full", query: "..." }    │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                 │
│  3. bridge.py routes to appropriate engine                     │
│     ┌─────────────────────────────────────────────────┐        │
│     │  if action == "full":                           │        │
│     │      result = core.agi_engine.process(query)    │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                 │
│  4. arifOS core processes with constitutional checks           │
│     ┌─────────────────────────────────────────────────┐        │
│     │  • F2 Truth Check: score >= 0.99?               │        │
│     │  • F6 Clarity Check: entropy reduced?           │        │
│     │  • F7 Humility Check: confidence bounded?       │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                 │
│  5. Result returned via JSON-RPC                               │
│     ◄───────────────────────────────────────────────────       │
│     { "status": "SEAL", "reasoning": "...", ... }              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Transport Options

| Transport | Use Case | How to Start |
|-----------|----------|--------------|
| **stdio** | Local (Claude Desktop) | `python -m AAA_MCP` |
| **SSE** | Cloud (Railway, Fly.io) | `python -m AAA_MCP sse` |

---

## FAQ

### Who is this for?

**Developers** building AI applications that need:
- Audit trails for AI decisions
- Consistent safety validation
- Human-in-the-loop pause points
- Governance for high-stakes actions

**Institutions** that require:
- Compliance documentation
- Reproducible AI decision-making
- Risk management for AI systems

**AI Systems** that need:
- Self-governance capabilities
- Constitutional constraints
- Verifiable decision-making

### When should I use AAA_MCP?

| Scenario | Recommendation |
|----------|----------------|
| Casual chat | Not needed |
| Code generation | Recommended |
| File operations | Recommended |
| Database queries | Strongly recommended |
| Financial decisions | Required |
| Medical/legal advice | Required |

### How is this different from just prompting the AI to be safe?

Prompts are suggestions. AAA_MCP provides **enforcement**:

| Approach | Guarantee |
|----------|-----------|
| Prompt: "Be safe" | ❌ AI might ignore |
| AAA_MCP | ✅ Every output passes through validation |

### What are the "Constitutional Floors"?

13 hard constraints that every output must pass:

| Floor | Name | Requirement |
|-------|------|-------------|
| F1 | Amanah | Reversible actions only |
| F2 | Truth | Accuracy ≥ 99% |
| F3 | Tri-Witness | Agreement of human, AI, earth |
| F7 | Humility | Confidence bounds stated |
| F12 | Injection Defense | Block prompt injection |
| ... | ... | ... |

---

## Deployment

### Local Development

```bash
cd /path/to/arifOS
pip install -e .
python -m AAA_MCP
```

### Railway.app (Cloud)

```toml
# railway.toml
[deploy]
startCommand = "python -m AAA_MCP sse"
healthcheckPath = "/health"
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "AAA_MCP", "sse"]
```

---

## Troubleshooting

### MCP tools not appearing in Claude Desktop?

1. **Check config location:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Verify JSON syntax** (no trailing commas!)

3. **Restart Claude Desktop completely**

4. **Check logs:** Look for `claude_desktop.log`

### Tools appear but don't work?

```bash
# Verify Python and dependencies
python --version  # Should be 3.10+
pip install -e .  # Install arifOS

# Test module loads
python -c "from AAA_MCP import serve; print('OK')"
```

### HTTP/SSE connection failed?

```bash
# Start SSE server
python -m AAA_MCP sse --port 8000

# Check health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", "version": "v51.1.0", ...}
```

### "FloorCheckResult 'is_hard' error"?

This was a bug in v51.0.0, fixed in v51.1.0:

```bash
git pull origin main
```

### Rate limiting issues?

The rate limiter is configured in `arifos.core.enforcement.governance`:

```python
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter
limiter = get_rate_limiter()
result = limiter.check("agi_genius", session_id)
```

---

## Migration from arifos/mcp

If you're upgrading from the old `arifos/mcp` module, see the **[Migration Guide](MIGRATION.md)**.

**Quick summary:**
```bash
# OLD (deprecated)
python -m arifos.mcp trinity

# NEW
python -m AAA_MCP
```

---

## Related Resources

- [Model Context Protocol](https://modelcontextprotocol.io) — Official MCP documentation
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers) — Reference implementations
- [arifOS Core](../arifos/core/README.md) — The constitutional kernel
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — Official Python SDK
- [Migration Guide](MIGRATION.md) — Upgrading from arifos/mcp

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v51.1.0 | 2026-01-24 | Fixed FloorCheckResult `is_hard` bug, improved docs |
| v51.0.0 | 2026-01-22 | The Great Decoupling - AAA_MCP introduced |
| v50.5.x | 2026-01 | Legacy arifos/mcp (deprecated) |

---

## License

Part of the arifOS project. See [LICENSE](../LICENSE) for details.

---

**AAA = Artifact · Authority · Architecture**

*DITEMPA BUKAN DIBERI — Forged, Not Given*

*A bridge that validates, not just translates.*
