# AAA MCP Server — Constitutional AI Governance

**Model-Agnostic · Platform-Universal · Constitutionally Hardened**

The AAA MCP server exposes arifOS constitutional governance as a [Model Context Protocol](https://modelcontextprotocol.io/) server. Any AI model (Claude, GPT, Gemini, Kimi, Llama) can call the 7 canonical tools through any MCP client (Claude Desktop, Cursor, VS Code, Windsurf) over any transport (stdio, SSE, HTTP).

## Quick Start

### Install

```bash
# From source (editable)
pip install -e ".[dev]"

# From PyPI
pip install aaa-mcp
```

### Run

```bash
# Auto-detect best transport
aaa-mcp

# Explicit transport selection
aaa-mcp-stdio                    # stdin/stdout (Claude Desktop, Cursor)
aaa-mcp-sse                      # HTTP/SSE (remote clients, Railway)

# Via Python module
python -m codebase.mcp            # auto
python -m codebase.mcp stdio      # explicit stdio
python -m codebase.mcp sse        # explicit SSE

# Docker (production)
docker build -t arifos:latest .
docker run -e PORT=8000 -p 8000:8000 arifos:latest
```

### Environment

```bash
HOST=0.0.0.0                     # Bind address (SSE/HTTP)
PORT=8000                        # Server port (SSE/HTTP)
LOG_LEVEL=info                   # debug|info|warning|error
GOVERNANCE_MODE=HARD             # HARD (all floors enforced) | SOFT (warnings only)
VAULT_PATH=./VAULT999            # Immutable ledger storage
ARIFOS_MODE=PROD                 # STUDIO|PROD|DEBUG
```

---

## Client Setup

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "aaa-mcp-stdio",
      "alwaysAllow": ["_init_", "_agi_", "_asi_", "_apex_", "_vault_", "_trinity_", "_reality_"]
    }
  }
}
```

### Cursor IDE

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "aaa-mcp-stdio",
      "args": [],
      "env": { "GOVERNANCE_MODE": "HARD" }
    }
  }
}
```

### VS Code (Continue / Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "aaa-mcp": {
      "command": "aaa-mcp-stdio",
      "args": []
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "aaa-mcp-stdio"
    }
  }
}
```

### Remote / HTTP (ChatGPT, Gemini, any client)

```bash
# Start SSE server
aaa-mcp-sse

# Connect from any HTTP MCP client
# Endpoint: http://localhost:8000/mcp
# Transport: SSE or Streamable HTTP
```

**Live public endpoint:** `https://arif-fazil.com/mcp`

---

## The 7 Canonical Tools

Every tool enforces constitutional floors and returns a verdict.

| Tool | Gate | Purpose | Floors Enforced |
|------|------|---------|-----------------|
| **`_init_`** | 000 | Session ignition, identity verification, injection scan | F1, F11, F12 |
| **`_agi_`** | 111-333 | Mind engine — truth, precision-weighted reasoning | F2, F4, F7, F10 |
| **`_asi_`** | 444-666 | Heart engine — safety, empathy, stakeholder protection | F1, F5, F6, F9 |
| **`_apex_`** | 888 | Soul engine — judgment, 9-paradox equilibrium, verdict | F3, F8, F11, F12 |
| **`_vault_`** | 999 | Immutable ledger — Merkle-sealed audit entry | F1, F8 |
| **`_trinity_`** | 000→999 | Full pipeline — runs all engines in sequence | All F1-F13 |
| **`_reality_`** | External | Fact-checker — external source verification | F7 |

### Tool Input (All tools)

```json
{
  "action": "sense | think | reflect | reason | forge | full | physics",
  "query": "User question or task",
  "session_id": "uuid-v4 (optional, auto-generated)"
}
```

### Tool Output (All tools)

```json
{
  "verdict": "SEAL | PARTIAL | VOID | 888_HOLD | SABAR",
  "response": "The governed response text",
  "reasoning": "Internal reasoning trace",
  "floor_results": {
    "F1_amanah": true,
    "F2_truth": 0.99
  },
  "vault": {
    "merkle_hash": "0xabc...",
    "timestamp": "2026-01-31T12:00:00Z"
  },
  "metadata": {
    "engine": "agi | asi | apex",
    "latency_ms": 28,
    "session_id": "..."
  }
}
```

### Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | All floors pass | ✅ Proceed |
| **PARTIAL** | Soft floor warning (F3, F5, F6, F8) | ⚠️ Proceed with caution |
| **VOID** | Hard floor failed (F1, F2, F4, F7, F9-F12) | ❌ Blocked |
| **888_HOLD** | High-stakes operation detected | ⏸️ Requires human confirmation |
| **SABAR** | Multiple floor concerns | 🧊 Cool down, review needed |

---

## Architecture (v55.0)

```
┌─────────────────────────────────────────────────┐
│  MCP CLIENT (Claude / GPT / Gemini / Cursor)    │
└──────────────────────┬──────────────────────────┘
                       │ JSON-RPC 2.0
┌──────────────────────▼──────────────────────────┐
│  TRANSPORT (stdio / SSE / HTTP)                  │
│  transports/auto.py → best transport             │
├─────────────────────────────────────────────────┤
│  MODEL ADAPTER (normalize request/response)      │
│  adapters/ → Anthropic / OpenAI / Universal      │
├─────────────────────────────────────────────────┤
│  TOOL REGISTRY (7 canonical tools)               │
│  core/tool_registry.py → single source of truth  │
├─────────────────────────────────────────────────┤
│  CONSTITUTION ENFORCER (F1-F13)                  │
│  constitution/enforcer.py → pre/post validation  │
├─────────────────────────────────────────────────┤
│  GOVERNANCE BRIDGE → arifOS Kernels              │
│  AGI (Δ Mind) → ASI (Ω Heart) → APEX (Ψ Soul)  │
├─────────────────────────────────────────────────┤
│  VAULT-999 (Merkle-sealed immutable ledger)      │
│  sessions/ + metrics/ + integration/vault.py     │
└─────────────────────────────────────────────────┘
```

### Directory Structure

```
mcp/
├── core/              Protocol layer (models, schemas, tool registry)
├── transports/        Transport implementations (stdio, SSE, HTTP)
├── adapters/          Model adapters (Anthropic, OpenAI, Google, Universal)
├── clients/           Client configs (Claude Desktop, Cursor, VS Code)
├── tools/             7 canonical constitutional tools
├── constitution/      F1-F13 floor enforcement
├── sessions/          Session management + pluggable backends
├── governance/        APEX PRIME judge + bridge to kernels
├── metrics/           Observability (constitutional + performance)
├── presenters/        Output formatting (human, JSON, markdown)
├── infrastructure/    Rate limiting, circuit breaker, health checks
├── external_gateways/ External integrations (Brave Search, Context7)
├── integration/       arifOS kernel/loop/vault hooks
└── config/            Configuration management
```

### Key Design Principles

1. **Model Agnosticism** — No AI model assumes privileged position. Model-specific quirks isolated in `adapters/`.
2. **Platform Universality** — Works identically on any MCP client. Client configs generated by `clients/`.
3. **Transport Pluggability** — `BaseTransport` ABC allows stdio, SSE, HTTP without changing tool logic.
4. **Constitutional Hardening** — Every tool call passes through `constitution/enforcer.py` (F1-F13).
5. **Single Tool Registry** — Tools defined once in `core/tool_registry.py`, consumed by all transports.

See [AAA_MCP_ARCHITECTURE_v55.md](./AAA_MCP_ARCHITECTURE_v55.md) for full architecture spec, migration map, and interface definitions.

---

## Compatibility Matrix

| Category | Supported |
|----------|-----------|
| **AI Models** | Claude, GPT-4, Gemini, Kimi K2.5, Llama, SEA-LION, any JSON-RPC |
| **MCP Clients** | Claude Desktop, Cursor, VS Code, Windsurf, ChatGPT Dev, any MCP client |
| **Transports** | stdio, SSE, HTTP (Streamable HTTP recommended for production) |
| **Platforms** | Linux, macOS, Windows |
| **Python** | 3.10, 3.11, 3.12, 3.13 |
| **Session Backends** | Memory, File (JSON), Redis, SQLite |

---

## Development

```bash
# Run MCP tests
pytest tests/mcp/ -v

# Quick smoke test
pytest tests/mcp/test_mcp_quick.py -v

# Full tool coverage
pytest tests/test_mcp_all_tools.py -v --cov=codebase.mcp

# Lint & format
ruff check codebase/mcp/
black codebase/mcp/ --line-length=100

# Type check
mypy codebase/mcp/ --ignore-missing-imports
```

## Health Check

```bash
# Local
curl http://localhost:8000/health

# Production
curl https://arif-fazil.com/health
```

---

## Constitutional Floors (F1-F13)

| # | Floor | What It Checks | Threshold | Type |
|---|-------|---------------|-----------|------|
| F1 | Amanah | Is the action reversible? | LOCK | Hard |
| F2 | Truth | Is it factually accurate? | ≥0.99 | Hard |
| F3 | Tri-Witness | Do Mind·Heart·Human agree? | ≥0.95 | Soft |
| F4 | Clarity | Does it reduce confusion? | ΔS≤0 | Hard |
| F5 | Peace² | Is it non-destructive? | ≥1.0 | Hard |
| F6 | Empathy | Does it serve the weakest? | κᵣ≥0.95 | Soft |
| F7 | Humility | Does it state uncertainty? | Ω₀∈[0.03,0.05] | Soft |
| F8 | Genius | Is intelligence governed? | G≥0.80 | Soft |
| F9 | Anti-Hantu | No false consciousness? | Φ≤0.30 | Hard |
| F10 | Ontology | Domain boundaries held? | LOCK | Hard |
| F11 | Authority | Identity verified? | LOCK | Hard |
| F12 | Hardening | Injection blocked? | ≥0.85 | Hard |
| F13 | Curiosity | Alternatives explored? | >0 | Guide |

---

**Version:** v55.0 | **License:** AGPL-3.0 | **Author:** Muhammad Arif bin Fazil
**DITEMPA BUKAN DIBERI** — Forged, Not Given
