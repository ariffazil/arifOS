# arifOS MCP Quickstart — GEOX & WEALTH

> **arifOS Platform-Client Agnostic Integration**
>
> One server. Five clients. Zero vendor lock. DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

---

## Executive Summary

arifOS exposes two sovereign MCP organs — **GEOX** (Earth Intelligence) and **WEALTH** (Capital Intelligence) — via a single OpenClaw MCP gateway that is **transport-agnostic** and **client-agnostic**. The same JSON-RPC contract, constitutional governance (F3–F13, OPS/777), and VAULT999 ledger work identically regardless of which MCP client invokes them.

This document provides copy-paste config snippets and test procedures for the top 5 AI MCP clients:
- Claude Desktop (P1)
- ChatGPT (P1)
- Cursor (P1)
- Windsurf (P1)
- VS Code + GitHub Copilot / Copilot-MCP (P1)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     arifOS OpenClaw Gateway                  │
│                                                              │
│  Transport layer (stdio ↔ SSE ↔ HTTP)                       │
│  Constitutional policy enforcement (F3/F6/F9 pre-exec)     │
│  Per-tool governance (F4/F8/OPS-777)                         │
│  VAULT999 verdict sealing (SEAL/HOLD/VOID/SABAR)            │
│  Human escalation via webhook (888_HOLD)                     │
└──────────────────────────────────────────────────────────────┘
              │                      │
       ┌──────▼──────┐        ┌──────▼──────┐
       │    GEOX     │        │   WEALTH     │
       │ (Geoscience)│        │  (Capital)   │
       └─────────────┘        └─────────────┘
              │                      │
    ┌─────────┴──────────┬────────────┴──────────┐
    ▼                   ▼                       ▼
┌────────┐      ┌──────────┐        ┌──────────────┐
│Claude  │      │  ChatGPT │        │  Cursor /    │
│Desktop │      │ (Remote) │        │  Windsurf /  │
│ (stdio)│      │  (SSE)   │        │  VS Code     │
└────────┘      └──────────┘        └──────────────┘
```

### Key Properties

| Property | Value |
|----------|-------|
| Transport (local) | `stdio` — Claude Desktop, Cursor, Windsurf, VS Code |
| Transport (remote) | `SSE` over HTTPS — ChatGPT, Claude.ai web |
| Auth (remote) | Bearer token via `Authorization` header |
| Governance parity | F3–F13 + OPS/777 apply identically across all clients |
| Tool namespaces | `GEOX_*`, `wealth_*`, `arifos_*` (disciplined, no collision) |
| Tool limit strategy | Lean surface — max 40 tools per organ to stay inside IDE limits |

---

## Server Endpoints

### Local (stdio)

```bash
# GEOX organ — stdio
arifos-mcp serve --organ GEOX --transport stdio

# WEALTH organ — stdio
arifos-mcp serve --organ wealth --transport stdio
```

### Remote (HTTPS + SSE)

| Organ | Remote URL | Auth |
|-------|-----------|------|
| GEOX | `https://mcp.arif-fazil.com/GEOX/mcp` | Bearer token (`AF_GEOX_TOKEN`) |
| WEALTH | `https://mcp.arif-fazil.com/wealth/mcp` | Bearer token (`AF_WEALTH_TOKEN`) |

---

## Tool Surface

### GEOX (Earth Intelligence)

| Tool | Description | Uncertainty |
|------|-------------|-------------|
| `GEOX_check_hazard` | Physical hazard risk (seismic/volcanic/flood/landslide/subsidence) | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_subsurface_model` | Porosity, permeability, pressure at depth | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_seismic_interpret` | Seismic survey interpretation | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_prospect_score` | Hydrocarbon prospect scoring (OOIP, GIP, chance factor) | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_physical_constraint` | Pressure/temperature/mud weight safe operating window | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_uncertainty_tag` | F8 uncertainty classification for any claim | F8 tag |
| `GEOX_witness_triad` | Tri-Witness W³ consensus verification | W³ verdict |
| `GEOX_ground_truth` | F8 grounding check for physical claims | grounded boolean |
| `GEOX_log_interpreter` | Triple-combo wireline log interpreter (GR/RT/RHOB/NPHI) | ESTIMATE/HYPOTHESIS/UNKNOWN |
| `GEOX_maraoh_impact` | F6 maruah dignity impact assessment | maruah score |
| `GEOX_extraction_limits` | Max safe extraction rate and cumulative limits | rate/depletion |
| `GEOX_climate_bounds` | Climate bounds (temperature rise, sea level, carbon budget) | optimistic/pessimistic |

### WEALTH (Capital Intelligence)

| Tool | Description | Verdict |
|------|-------------|---------|
| `wealth_evaluate_ROI` | Investment ROI against objective function | PROCEED/HOLD/VOID |
| `wealth_ping` | Health check for WEALTH organ | status + verdict |
| `wealth_market_snapshot` | Current market data snapshot | tagged |
| `wealth_risk_assess` | Risk assessment for a position | risk tier |

### arifOS Governance Tools (all clients)

| Tool | Description |
|------|-------------|
| `forge_check_governance` | Run F3/F6/F9 constitutional checks |
| `forge_health` | Server health + floor status |
| `forge_run` | Full governed agent task |
| `forge_hold` | Stage action for 888_HOLD approval |
| `forge_approve` | Approve a held action |
| `forge_route_approval` | Route PlannerOutput through policy gates |
| `forge_apply_patches` | Apply unified diffs |
| `forge_remember` | Store memory in MemoryContract |
| `forge_recall` | Query MemoryContract |
| `forge_ticket_status` | Query approval ticket by ID |

---

## Per-Client Config Snippets

### 1. Claude Desktop

**Config file**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos_GEOX": {
      "command": "node",
      "args": ["/usr/local/bin/arifos-mcp", "serve", "--organ", "GEOX", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_wealth": {
      "command": "node",
      "args": ["/usr/local/bin/arifos-mcp", "serve", "--organ", "wealth", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_forge": {
      "command": "node",
      "args": ["/usr/local/bin/arifos-mcp", "serve", "--organ", "forge", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    }
  }
}
```

**Test procedure**:
1. Restart Claude Desktop
2. Ask: `"Call GEOX_check_hazard for Jakarta, Indonesia"`
3. Ask: `"Call wealth_ping to check WEALTH status"`
4. Ask: `"Call forge_check_governance for 'delete all files'"` → expect `BLOCK`

---

### 2. ChatGPT (Remote MCP)

**Connect via**: Settings → Apps & Connectors → Developer → MCP Servers → Add Server

| Field | GEOX | WEALTH | arifOS Forge |
|-------|------|--------|--------------|
| Name | `arifos_GEOX` | `arifos_wealth` | `arifos_forge` |
| URL | `https://mcp.arif-fazil.com/GEOX/mcp` | `https://mcp.arif-fazil.com/wealth/mcp` | `https://mcp.arif-fazil.com/mcp` |
| Auth | Bearer token | Bearer token | Bearer token |

**Token setup** (environment variables on your VPS):
```bash
export AF_GEOX_TOKEN="your-GEOX-token"
export AF_WEALTH_TOKEN="your-wealth-token"
export AF_FORGE_TOKEN="your-forge-token"
```

**Test procedure**:
1. Go to Settings → Apps & Connectors → Developer → MCP Servers
2. Add each server with URL and bearer token
3. Test with: `"Use arifos_GEOX to check seismic hazard for Tokyo"`
4. Test with: `"Use arifos_wealth to evaluate ROI with initial_investment=10000, scenarios=[{probability:0.6,cash_flow:5000},{probability:0.4,cash_flow:-2000}]"`
5. Test with: `"Use arifos_forge to check governance for 'deploy to production'"` → expect `BLOCK`

---

### 3. Cursor

**Config file**: `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project-level)

```json
{
  "mcpServers": {
    "arifos_GEOX": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "GEOX", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_wealth": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "wealth", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_forge": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "forge", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    }
  }
}
```

**Test procedure**:
1. Open Cursor → Settings → MCP → Add new server
2. Paste each config block (or use file path `~/.cursor/mcp.json`)
3. Press "Test connection" on each
4. In Cursor AI chat: `"@arifos_GEOX check seismic hazard for Jakarta"`
5. In Cursor AI chat: `"@arifos_wealth evaluate ROI for initial_investment=50000"`
6. In Cursor AI chat: `"@arifos_forge check governance for 'rm -rf /'"` → expect `BLOCK`

---

### 4. Windsurf

**Config file**: `~/.windsurf/mcp.json` (global) or `.windsurf/mcp.json` (project-level)

```json
{
  "mcpServers": {
    "arifos_GEOX": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "GEOX", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_wealth": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "wealth", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_forge": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "forge", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    }
  }
}
```

**Test procedure**:
1. Open Windsurf → Cascade settings → MCP servers
2. Add servers with same config blocks
3. Test: `"@arifos_GEOX what are the extraction limits for a sandstone at 2500m depth?"`
4. Test: `"@arifos_wealth run wealth_evaluate_ROI with initial_investment=75000"`
5. Test: `"@arifos_forge run forge_health"` → expect floor status

---

### 5. VS Code + GitHub Copilot / Copilot-MCP

**Two pathways**:

**Path A — Copilot-MCP extension**:
- Install [Copilot-MCP extension](https://marketplace.visualstudio.com/) from VS Code marketplace
- Config file: `.vscode/mcp.json`

```json
{
  "servers": {
    "arifos_GEOX": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "GEOX", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_wealth": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "wealth", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    },
    "arifos_forge": {
      "command": "arifos-mcp",
      "args": ["serve", "--organ", "forge", "--transport", "stdio"],
      "env": {
        "AF_FORGE_MODE": "internal_mode"
      }
    }
  }
}
```

**Path B — GitHub Copilot agent mode**:
- Enable Copilot agent mode in Copilot settings
- Register GEOX/WEALTH as allowed MCP servers in project or enterprise settings
- Use agentic prompts to invoke tools

**Test procedure**:
1. Install Copilot-MCP extension
2. Add config to `.vscode/mcp.json`
3. Test: `"Use arifos_GEOX to interpret triple-combo logs for a sandstone formation"`
4. Test: `"Use arifos_wealth to evaluate ROI with scenarios=[{probability:0.7,cash_flow:30000}]"`
5. Test: `"Use arifos_forge forge_hold to stage a critical investment decision"`

---

## arifOS MCP Binary Setup

### Install arifOS MCP globally

```bash
# Build
npm run build

# Link as global CLI
npm link

# Verify
arifos-mcp --help
```

### Serve by organ

```bash
# Serve GEOX organ (stdio)
arifos-mcp serve --organ GEOX --transport stdio

# Serve WEALTH organ (stdio)
arifos-mcp serve --organ wealth --transport stdio

# Serve arifOS Forge (full governance server)
arifos-mcp serve --organ forge --transport stdio

# Remote HTTPS mode (for ChatGPT and web clients)
AF_FORGE_MODE=external_safe_mode AF_GEOX_TOKEN=xxx arifos-mcp serve --organ GEOX --transport sse --port 3001
```

### Docker (remote hosting)

```bash
# Build the container
docker build -t arifos-mcp .

# Run GEOX organ
docker run -p 3001:3001 \
  -e AF_FORGE_MODE=external_safe_mode \
  -e AF_GEOX_TOKEN=your-token \
  arifos-mcp serve --organ GEOX --transport sse --port 3001

# Run WEALTH organ
docker run -p 3002:3002 \
  -e AF_FORGE_MODE=external_safe_mode \
  -e AF_WEALTH_TOKEN=your-token \
  arifos-mcp serve --organ wealth --transport sse --port 3002
```

---

## Governance & Constitutional Floors

All MCP tool calls pass through arifOS constitutional floors **regardless of which client initiated them**:

| Floor | Name | Trigger | Verdict |
|-------|------|---------|---------|
| F3 | Input Clarity | Pre-execution | SABAR (block vague input) |
| F6 | Harm/Dignity | Pre-execution + per-tool | VOID (block harm) |
| F9 | Injection | Pre-execution | VOID (block injection) |
| F4 | Entropy | Per-tool | HOLD (budget exceeded) |
| F8 | Grounding | Per-tool | HOLD (ungrounded claim) |
| OPS/777 | Thermodynamic | Per-tool | PASS/HOLD/VOID (Landauer bounds) |
| F7 | Confidence | Post-execution | HOLD (low confidence) |
| F13 | Sovereign | Dangerous tools | 888_HOLD (human approval) |

### 888_HOLD Flow

```
Client tool call → F13 gate triggered → HOLD verdict
    ↓
Hold ticket created in ApprovalBoundary
    ↓
arifOS sends webhook to HUMAN_ESCALATION_WEBHOOK_URL
    ↓
Human reviews → APPROVE/REJECT/MODIFY
    ↓
VAULT999 seal recorded
```

### Test governance with forge_check_governance

```bash
# All clients: test governance checks
forge_check_governance task="deploy to production and delete all test data"
# Expected: BLOCK (F6 harm + F13 sovereign)

forge_check_governance task="check the weather"
# Expected: PASS
```

---

## Support Matrix

| Client | Priority | Transport | GEOX | WEALTH | Forge | Governance Parity |
|--------|----------|-----------|------|--------|-------|-------------------|
| Claude Desktop | P1 | stdio | ✅ | ✅ | ✅ | ✅ |
| ChatGPT | P1 | HTTPS/SSE | ✅ | ✅ | ✅ | ✅ |
| Cursor | P1 | stdio | ✅ | ✅ | ✅ | ✅ |
| Windsurf | P1 | stdio | ✅ | ✅ | ✅ | ✅ |
| VS Code + Copilot | P1 | stdio/HTTP | ✅ | ✅ | ✅ | ✅ |
| Continue.dev | P2 | JSON config | 🟡 | 🟡 | 🟡 | ✅ |
| Cline | P2 | stdio/HTTP | 🟡 | 🟡 | 🟡 | ✅ |
| Claude Code | P2 | stdio | 🟡 | 🟡 | 🟡 | ✅ |
| Zed | P3 | stdio | 🟡 | 🟡 | 🟡 | ✅ |
| JetBrains AI Assistant | P3 | stdio | 🟡 | 🟡 | 🟡 | ✅ |

✅ = Verified working | 🟡 = Next target | 🔴 = Not yet supported

---

## VAULT999 Ledger

All terminal verdicts are sealed into the VAULT999 append-only ledger:

```bash
# View ledger
cat ~/.arifos/vault.jsonl | jq '.verdict'

# Query by verdict
cat ~/.arifos/vault.jsonl | jq 'select(.verdict == "HOLD")'

# Query by session
cat ~/.arifos/vault.jsonl | jq 'select(.sessionId == "abc123")'
```

Sample VAULT999 entry:
```json
{
  "sealId": "VAULT999-20260415-001",
  "verdict": "SEAL",
  "organ": "WEALTH",
  "tool": "wealth_evaluate_ROI",
  "sessionId": "mcp-chatgpt-001",
  "client": "chatgpt",
  "timestamp": "2026-04-15T10:30:00Z",
  "thermodynamicCost": 0.003,
  "floorsPassed": ["F3", "F6", "F7", "F8", "F13"],
  "emv": 12500,
  "npv": 8200
}
```

---

## Troubleshooting

### Connection refused

```bash
# Check if arifos-mcp is running
ps aux | grep arifos-mcp

# Test stdio locally
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | arifos-mcp serve --organ GEOX
```

### Auth failures (remote)

```bash
# Verify token is set
echo $AF_GEOX_TOKEN

# Test with verbose curl
curl -v -H "Authorization: Bearer $AF_GEOX_TOKEN" https://mcp.arif-fazil.com/GEOX/mcp
```

### Tools not appearing in client

- Restart the MCP client after config change
- Check namespace collisions (max 40 tools per server)
- Verify config JSON syntax with `jq` validator

### Governance false positives

- F3/SABAR: Input is too vague — add specificity
- F6/VOID: Harm pattern detected — review for dignity risk
- F9/VOID: Injection pattern detected — sanitize input
- OPS/777/HOLD: Thermodynamic cost exceeds Landauer bound — reduce complexity

---

## Glama Registration

To register arifOS GEOX and WEALTH on Glama's MCP registry:

1. Go to [glama.ai/mcp/servers](https://glama.ai/mcp/servers)
2. Submit server entry with:
   - **Name**: `arifos_GEOX`
   - **Description**: `Earth intelligence — hazard analysis, subsurface modeling, seismic interpretation, hydrocarbon prospect scoring`
   - **Tags**: `geoscience`, `earth-intelligence`, `constitutional-ai`, `evidence-based`
   - **URL**: `https://mcp.arif-fazil.com/GEOX/mcp`
   - **Transport**: `sse`
3. Submit separately for:
   - **Name**: `arifos_wealth`
   - **Tags**: `finance`, `capital-intelligence`, `constitutional-ai`, `ROI`, `thermodynamic`
   - **URL**: `https://mcp.arif-fazil.com/wealth/mcp`

---

## Next Steps

1. **Today**: Deploy arifOS MCP on your VPS (`npm run build && npm link`)
2. **This week**: Get GEOX + WEALTH working on Claude Desktop and ChatGPT
3. **This month**: Expand to Cursor, Windsurf, VS Code/Copilot
4. **Ongoing**: Register on Glama, build out GEOX/WEALTH tool surface

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*

