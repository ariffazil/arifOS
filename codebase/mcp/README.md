# AAA MCP Server (v52.5.1-SEAL)
**Artifact · Authority · Architecture**

> The Metabolic Application Layer for arifOS.  
> *"DITEMPA BUKAN DIBERI"* — Forged, Not Given.

## 🌟 Overview

The **AAA MCP Server** is the comprehensive interface for arifOS v52.5.1, implementing the **Model Context Protocol (MCP)** to expose 5 constitutional tools. It unifies the metabolic system (Mind, Heart, Soul) into a single server that supports both **MCP Clients** (Claude Desktop, Cursor, Gemini) and **REST API Consumers** (ChatGPT, Webhooks).

## 🛠️ The 5 Trinity Tools

| Tool | Symbol | Role | Capability | Floors |
|------|--------|------|------------|--------|
| **init_000** | 🚪 | **Gate** | Authority verification, session injection defense, ATLAS-333 Routing | F1, F11, F12 |
| **agi_genius** | Δ | **Mind** | **SENSE** (Fact) → **THINK** (Reason) → **ATLAS** (Meta) → **FORGE** (Draft) | F2, F4, F7, F10 |
| **asi_act** | Ω | **Heart** | **EVIDENCE** (Stakeholders) → **EMPATHY** (Care) → **ACT** (Safety) | F1, F5, F6, F9, F13 |
| **apex_judge** | Ψ | **Soul** | **EUREKA** (Paradox) → **JUDGE** (Verdict) → **PROOF** (Seal) | F3, F8, F11, F12 |
| **vault_999** | 🔒 | **Seal** | Immutable Ledger IO, Merkle Proofs, Cooling Tier Management | F1, F8 |

## 🚀 Execution

### 1. Production (Railway/Cloud)
The unified server supporting MCP (SSE) and REST endpoints.
```bash
python -m arifos.mcp sse
```
*   **Port:** Default `8000` (set via `$PORT`)
*   **Endpoints:**
    *   `/sse` - MCP Protocol Stream (Tier 2)
    *   `/messages` - MCP Sampling (Tier 2)
    *   `/health` - System Health Check (Tier 5)
    *   `/docs` - Interactive API Docs (Tier 1)
    *   `/dashboard` - Live Telemetry UI (Tier 5)
    *   `/metrics/json` - Prometheus Metrics (Tier 5)
    *   `/checkpoint` - REST Wrapper (Tier 4)

### 2. Local Development (Stdio)
For integration with desktop IDEs like Claude Desktop or Cursor.
```bash
python -m arifos.mcp trinity
```

## 🔌 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `ARIFOS_ENV` | Environment mode | `dev` |
| `ARIFOS_LOG_LEVEL` | Logging verbosity | `INFO` |
| `ARIFOS_VAULT_PATH` | Path to constitutional config | `VAULT999` |
| `ARIFOS_LEDGER_PATH` | Path to cooling ledger | `VAULT999/BBB_LEDGER` |

### MCP Client Config (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "arifos.mcp", "trinity"],
      "env": {
        "PYTHONPATH": "/path/to/arifOS"
      }
    }
  }
}
```

## 🏗️ Architecture

The AAA MCP server is built on **FastMCP** and implements the **v52.5.1-SEAL** unified architecture:

1.  **Unified Entry:** Single `sse.py` handles all transport layers.
2.  **Parallel Execution:** AGI and ASI run asynchronously.
3.  **Constitutional Persistence:**
    *   **Volume Storage:** Ledger preserved at `/var/data`
    *   **Cryptographic Identity:** Ed25519 keys for F11 Authority
    *   **Genesis Hash:** Chain root validation on startup

## 📜 Verdict Types

*   **SEAL:** Approved. Proceed.
*   **PARTIAL:** Approved with warnings (soft floor breach).
*   **SABAR:** Retry required (cooling period).
*   **VOID:** Rejected (hard floor breach).
*   **888_HOLD:** Human intervention required (High Stakes).
