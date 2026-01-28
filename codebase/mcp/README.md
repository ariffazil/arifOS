# AAA MCP Server (v53.2.0-CODEBASE)
**Artifact · Authority · Architecture**

> The Metabolic Application Layer for arifOS.  
> *"DITEMPA BUKAN DIBERI"* — Forged, Not Given.

## 🌟 Overview

The **AAA MCP Server** is the comprehensive interface for arifOS v53.2.0, implementing the **Model Context Protocol (MCP)** to expose 6 constitutional tools. It unifies the metabolic system (Mind, Heart, Soul) into a single server that supports both **MCP Clients** (Claude Desktop, Cursor, Gemini) and **REST API Consumers** (ChatGPT, Webhooks).

### What's New in v53.2.0
- **6-Tool Architecture**: Added `trinity_loop` for complete pipeline execution
- **Streamable HTTP Transport**: New MCP protocol 2024-11-05+ support
- **Constitutional Physics**: Proxy kernels with real entropy calculations
- **Simplified Bridge**: Cleaner router architecture

---

## 🛠️ The 6 Trinity Tools

| Tool | Symbol | Role | Capability | Floors |
|------|--------|------|------------|--------|
| **init_000** | 🚪 | **Gate** | Constitutional ignition, identity verification, session management | F1, F11, F12 |
| **agi_genius** | Δ | **Mind** | **SENSE** → **THINK** → **REASON** → **FORGE** | F2, F4, F7, F10 |
| **asi_act** | Ω | **Heart** | **EVIDENCE** → **EMPATHY** → **EVALUATE** → **ACT** | F1, F5, F6, F9 |
| **apex_judge** | Ψ | **Soul** | **EUREKA** → **JUDGE** → **DECIDE** → **PROOF** | F3, F8, F11, F12, F13 |
| **vault_999** | 🔒 | **Seal** | Immutable ledger, Merkle proofs, cooling tiers | F1, F8 |
| **trinity_loop** | ♻️ | **Pipeline** | Complete AGI→ASI→APEX→VAULT metabolic cycle | All F1-F13 |

### Tool Actions Detail

#### `init_000` — Constitutional Ignition
```json
{
  "action": "init" | "gate" | "reset" | "validate" | "authorize",
  "query": "User greeting or context",
  "session_id": "optional-session-id",
  "user_token": "for-authorize-action"
}
```

#### `agi_genius` — Mind Engine (Δ)
```json
{
  "action": "sense" | "think" | "reflect" | "reason" | "atlas" | "forge" | "full" | "physics",
  "query": "Input to process",
  "session_id": "session-id",
  "context": {} // Optional additional context
}
```

#### `asi_act` — Heart Engine (Ω)
```json
{
  "action": "evidence" | "empathize" | "evaluate" | "act" | "witness" | "stakeholder" | "diffusion" | "audit" | "full",
  "text": "Input text",
  "query": "Alternative input",
  "session_id": "session-id",
  "reasoning": "For evaluate action",
  "agi_context": {} // AGI output for chaining
}
```

#### `apex_judge` — Soul Engine (Ψ)
```json
{
  "action": "eureka" | "judge" | "decide" | "proof" | "entropy" | "full",
  "query": "Query to evaluate",
  "response": "Response to judge",
  "session_id": "session-id",
  "reasoning": "For decide action",
  "safety_evaluation": {}, // ASI evaluation
  "authority_check": {} // Init authorization
}
```

#### `vault_999` — Immutable Memory
```json
{
  "action": "seal" | "list" | "read" | "write" | "propose",
  "session_id": "session-id",
  "verdict": "SEAL|VOID|SABAR|PARTIAL|888_HOLD",
  "target": "seal|ledger|canon|fag|tempa|phoenix|audit",
  "query": "Query context",
  "response": "Response to seal",
  "decision_data": {} // Full decision payload
}
```

#### `trinity_loop` — Complete Pipeline
```json
{
  "query": "User query to process",
  "session_id": "optional-session-id"
}
```
Runs: `init_000` → `agi_genius` → `asi_act` → `apex_judge` → `vault_999`

---

## 🚀 Execution Modes

### 1. Stdio Transport (Local Development)
For integration with desktop IDEs like Claude Desktop, Cursor, or Kimi CLI.

```bash
# Using Python module
python -m codebase.mcp

# Or using entry point (after pip install)
codebase-mcp-stdio
aaa-mcp-stdio  # Alias
```

**Use when:**
- Claude Desktop integration
- Cursor IDE
- Kimi CLI
- Local development

### 2. SSE/HTTP Transport (Production)
For Railway, Render, Fly.io, or any Docker host. Supports both Streamable HTTP and legacy SSE.

```bash
# Using Python module
python -m codebase.mcp sse

# Or using entry point (after pip install)
codebase-mcp-sse
aaa-mcp-sse  # Alias
```

**Endpoints:**

| Endpoint | Method | Transport | Description |
|----------|--------|-----------|-------------|
| `/mcp` | POST | Streamable HTTP | MCP 2024-11-05+ protocol |
| `/sse` | GET | Legacy SSE | Backward compatibility |
| `/messages` | POST | Legacy SSE | Message endpoint |
| `/health` | GET | HTTP | Railway/Docker liveness |
| `/metrics/json` | GET | HTTP | Constitutional telemetry |
| `/dashboard` | GET | HTTP | Live monitoring UI |
| `/` | GET | HTTP | Interactive discovery page |

---

## 🔌 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `ARIFOS_ENV` | Environment mode | `dev` |
| `ARIFOS_LOG_LEVEL` | Logging verbosity | `INFO` |
| `ARIFOS_VAULT_PATH` | Constitutional config path | `VAULT999` |
| `ARIFOS_LEDGER_PATH` | Cooling ledger path | `VAULT999/BBB_LEDGER` |
| `ARIFOS_MODE` | Server mode | `BRIDGE` |

### MCP Client Config

**Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_MODE": "BRIDGE"
      }
    }
  }
}
```

**Kimi CLI (`.mcp.json`):**
```json
{
  "mcpServers": {
    "arifOS-Constitutional": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "C:/Users/User/arifOS",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1",
        "ARIFOS_MODE": "BRIDGE"
      }
    }
  }
}
```

**HTTP/SSE Client:**
```json
{
  "mcpServers": {
    "aaa-mcp-sse": {
      "url": "https://arifos.arif-fazil.com/sse"
    }
  }
}
```

---

## 🏗️ Architecture

The AAA MCP server implements the **v53.2.0-CODEBASE** architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     AAA MCP SERVER v53.2.0                       │
├─────────────────────────────────────────────────────────────────┤
│  Transport Layer                                                  │
│    ├── Stdio (codebase.mcp.server) ← Claude Desktop, Kimi       │
│    └── Streamable HTTP (codebase.mcp.sse) ← Railway, Web        │
├─────────────────────────────────────────────────────────────────┤
│  Bridge Layer (codebase.mcp.bridge)                              │
│    ├── bridge_init_router     → TrinityHatTool                  │
│    ├── bridge_agi_router      → AGITool (Δ Mind)                │
│    ├── bridge_asi_router      → ASITool (Ω Heart)               │
│    ├── bridge_apex_router     → APEXTool (Ψ Soul)               │
│    ├── bridge_vault_router    → VaultTool (🔒 Seal)             │
│    └── bridge_trinity_loop_router → TrinityLoop                 │
├─────────────────────────────────────────────────────────────────┤
│  Tool Classes (codebase.mcp.tools)                               │
│    ├── TrinityHatTool  : Gate, Auth, Injection defense          │
│    ├── AGITool         : Reasoning, truth, clarity              │
│    ├── ASITool         : Empathy, care, ethics                  │
│    ├── APEXTool        : Judgment, consensus, proof             │
│    ├── VaultTool       : Ledger, sealing, audit                 │
│    └── TrinityLoop     : Full pipeline orchestration            │
├─────────────────────────────────────────────────────────────────┤
│  Engine Layer (codebase.*)                                       │
│    ├── AGI (agi/)      : Mind engine with native kernel         │
│    ├── ASI (asi/)      : Heart engine with native kernel        │
│    ├── APEX (apex/)    : Soul engine with judicial core         │
│    └── VAULT (stages/) : Immutable ledger & cooling             │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Unified Entry**: Single codebase handles all transport layers
2. **Parallel Execution**: AGI and ASI run asynchronously when possible
3. **Constitutional Persistence**:
   - **Volume Storage**: Ledger preserved at `/var/data` (Railway)
   - **Cryptographic Identity**: Ed25519 keys for F11 Authority
   - **Genesis Hash**: Chain root validation on startup
4. **Proxy Kernels**: Constitutional physics with real entropy calculations
5. **Rate Limiting**: F11 protection against abuse

---

## 📜 Verdict Types

| Verdict | Meaning | Symbol | Action |
|---------|---------|--------|--------|
| **SEAL** | Approved | ✓ | Proceed with output |
| **PARTIAL** | Approved with warnings | ⚠️ | Proceed, note soft floor breach |
| **SABAR** | Retry required | ⏳ | Cooling period, retry with adjustments |
| **VOID** | Rejected | ✗ | Block output, explain hard floor breach |
| **888_HOLD** | Human intervention required | ⏸️ | High stakes, require human confirmation |

---

## 🧪 Development

### Running Tests

```bash
# Test MCP imports
python -m pytest tests/test_agi_imports_fixed.py -v

# Test specific tool
python -c "from codebase.mcp.tools import TrinityHatTool; print('OK')"

# Full test suite
pytest tests/ -m "mcp" -v
```

### Local Server Development

```bash
# Stdio mode (for Claude Desktop testing)
python -m codebase.mcp

# SSE mode with auto-reload
uvicorn codebase.mcp.sse:app --reload --port 8000

# Or use the entry point
python -m codebase.mcp sse
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["codebase-mcp-sse"]
```

```bash
docker build -t aaa-mcp .
docker run -p 8000:8000 aaa-mcp
```

---

## 📚 Related Documentation

| Document | Description |
|----------|-------------|
| `HUMAN_LANGUAGE_GUIDE.md` | Using tools with natural language |
| `HUMAN_LANGUAGE_BRIDGE.md` | Bridge implementation details |
| `HUMAN_LANGUAGE_REFLECTION.md` | Design philosophy |
| `../README.md` | Main arifOS documentation |
| `../../AGENTS.md` | Agent integration guide |

---

## 🔗 Entry Points Reference

```toml
# pyproject.toml [project.scripts]
codebase-mcp      = "codebase.mcp.server:main"      # Stdio
codebase-mcp-stdio = "codebase.mcp.server:main"     # Stdio (explicit)
codebase-mcp-sse  = "codebase.mcp.sse:main"         # SSE/HTTP

# Aliases (backward compatibility)
aaa-mcp           = "arifos.mcp.__main__:main"       # Legacy
codebase-mcp      = "codebase.mcp.server:main"      # Current
```

---

**Version:** v53.2.0-CODEBASE  
**Authority:** Muhammad Arif bin Fazil  
**License:** AGPL-3.0  
**Live Server:** https://arifos.arif-fazil.com

---

*DITEMPA BUKAN DIBERI — Constitutional intelligence is forged through governance, not given through computation.*
