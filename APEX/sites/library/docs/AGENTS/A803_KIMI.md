# OpenClaw KIMI Skill Requirements Analysis
**Date:** 2026-03-07  
**Research Source:** docs.openclaw.ai  
**Target:** arifOS_bot (Kimi K2.5 Primary)  
**Status:** OPERATIONAL WITH GAPS

---

## Executive Summary

Based on deep research of OpenClaw documentation, your OpenClaw instance is **70% operational**. The core gateway runs with Kimi K2.5 as primary, but **16 critical skills/toolsets** are needed for full autonomous management.

**Current State:**
- ✅ Gateway: Running (port 18789)
- ✅ Primary Model: kimi/kimi-k2.5
- ✅ Tools Profile: full
- ✅ Channel: Telegram configured
- ⚠️ Skills: None installed via clawhub
- ⚠️ MCP: arifos-mcp configured but protocol mismatch
- ⚠️ Memory: Not wired to OpenClaw directly

---

## Required Skill Categories (16 Total)

### Category 1: Core OpenClaw CLI Skills (CRITICAL - 5 skills)

These are built into OpenClaw CLI but need to be exposed as agent-accessible capabilities:

| Skill | CLI Command | Purpose | Priority |
|-------|-------------|---------|----------|
| **openclaw-doctor** | `openclaw doctor` | Health checks, config validation, auto-fixes | 🔴 CRITICAL |
| **openclaw-gateway** | `openclaw gateway <start/stop/restart/status>` | Gateway lifecycle management | 🔴 CRITICAL |
| **openclaw-update** | `openclaw update` | Self-update mechanism | 🔴 CRITICAL |
| **openclaw-config** | `openclaw config <get/set/validate>` | Configuration management | 🟡 HIGH |
| **openclaw-status** | `openclaw status --deep` | Comprehensive health diagnostics | 🟡 HIGH |

**Implementation Notes:**
- These use `openclaw` CLI (Node.js binary in container)
- Gateway runs as process inside container (not systemd)
- Use `docker exec openclaw_gateway openclaw <command>`

---

### Category 2: arifOS Bridge Skills (CRITICAL - 3 skills)

Direct integration with arifOS MCP server:

| Skill | Tool | Purpose | Status |
|-------|------|---------|--------|
| **arifos-memory** | `vector_memory` | Semantic search (BGE-M3 + Qdrant) | ⚠️ Needs MCP fix |
| **arifos-governance** | `apex_judge` | Constitutional validation | ⚠️ Needs MCP fix |
| **arifos-search** | `search_reality` | Web + vector hybrid search | ⚠️ Needs MCP fix |

**Current Blocker:** MCP 2025-11-25 protocol mismatch
- Bridge expects: Simple HTTP POST
- arifOS requires: Session init → JSON-RPC → SSE response
- **Fix needed:** Update `/home/node/.local/bin/arifos` to full MCP client

---

### Category 3: Skill Registry Management (HIGH - 3 skills)

Manage OpenClaw skills ecosystem:

| Skill | CLI | Purpose |
|-------|-----|---------|
| **clawhub-search** | `clawhub search <query>` | Find skills in registry |
| **clawhub-install** | `clawhub install <slug>` | Install from registry |
| **clawhub-sync** | `clawhub sync` | Publish/sync local skills |

**Registry URL:** https://clawhub.openclaw.ai (default)

---

### Category 4: MCP Server Management (HIGH - 2 skills)

Manage MCP tool servers:

| Skill | CLI | Purpose |
|-------|-----|---------|
| **mcporter-config** | `mcporter config <add/remove>` | Manage MCP servers |
| **mcporter-call** | `mcporter call <tool>` | Direct tool execution |

**Current Issue:** arifos-mcp added but returns SSE error
- Needs proper MCP client configuration
- Consider: `npx @anthropic-ai/mcp@latest` for testing

---

### Category 5: Memory & Knowledge (MEDIUM - 3 skills)

| Skill | CLI/Tool | Purpose | Wiring |
|-------|----------|---------|--------|
| **memory-search** | `openclaw memory search` | Vector search over MEMORY.md | ✅ Native |
| **memory-index** | `openclaw memory index` | Reindex memory files | ✅ Native |
| **rag-constitutional** | Direct Python | BGE-M3 + Qdrant via arifosmcp | ⚠️ Bridge needed |

---

## Detailed Gap Analysis

### Gap 1: No `openclaw-doctor` Integration

**What it does:**
- Validates config against schema
- Checks gateway health
- Detects common misconfigurations
- Auto-fixes safe issues (`--fix`)
- Security audit (`--deep`)

**Why needed:**
- First line of troubleshooting
- Catches config drift
- Validates after updates

**Implementation:**
```bash
docker exec openclaw_gateway openclaw doctor [--fix] [--deep]
```

---

### Gap 2: Gateway Lifecycle Management

**Missing capabilities:**
- Graceful restart with config reload
- Health probing with retries
- Service dependency checks
- Log rotation triggering

**Commands needed:**
```bash
openclaw gateway restart [--force]
openclaw gateway status [--deep]
openclaw gateway probe
openclaw logs --follow
```

---

### Gap 3: MCP Protocol Bridge (CRITICAL)

**Current broken flow:**
```
OpenClaw → arifos CLI → HTTP POST → arifOS MCP → ❌ 404/406
```

**Required flow (MCP 2025-11-25):**
```
OpenClaw → MCP Client → GET /mcp (session) → POST /mcp (JSON-RPC) → SSE response
```

**Implementation options:**

Option A: Fix `arifos` bash script to handle SSE
- Parse `event: message\ndata: {...}` format
- Extract session ID from headers
- Manage session lifecycle

Option B: Install proper MCP SDK
```bash
npm install -g @anthropic-ai/mcp@latest
# Use: npx @anthropic-ai/mcp call arifos-mcp vector_memory
```

Option C: Use mcporter as bridge
```bash
mcporter call arifos-mcp/vector_memory query="test"
```

---

### Gap 4: Model Provider Management

**Missing:** Dynamic model switching and health checks

**Needed commands:**
```bash
openclaw models status [--probe]
openclaw models set <model>
openclaw models fallbacks list/add/remove
openclaw models auth order set <provider> <order...>
```

**Use case:** Fallback chain verification when Kimi is down

---

### Gap 5: Channel Health Monitoring

**Missing:** Proactive channel diagnostics

**Needed:**
```bash
openclaw channels status [--probe]
openclaw channels logs [--lines 100]
openclaw health [--timeout 5000]
```

---

## Recommended Skill Installation Order

### Phase 1: Foundation (Critical)
1. **openclaw-doctor** - Health diagnostics
2. **openclaw-gateway** - Lifecycle management
3. **arifos-mcp-fixed** - Working MCP bridge

### Phase 2: Operations (High)
4. **openclaw-config** - Configuration management
5. **clawhub-manager** - Skill registry
6. **mcporter-client** - MCP servers

### Phase 3: Intelligence (Medium)
7. **memory-search-enhanced** - Vector + constitutional
8. **rag-hybrid** - BGE-M3 + web search
9. **model-fallback** - Automatic failover

### Phase 4: Advanced (Low)
10. **cron-manager** - Scheduled jobs
11. **browser-automation** - Headless browser
12. **node-controller** - Mac/node devices

---

## Immediate Action Items

### 1. Fix MCP Bridge (CRITICAL)
```bash
# Test current state
docker exec openclaw_gateway arifos health

# Options:
# A. Install MCP CLI
npm install -g @anthropic-ai/mcp@latest

# B. Update arifos script to parse SSE
docker cp /opt/arifos/data/openclaw/bin/arifos openclaw_gateway:/home/node/.local/bin/arifos

# C. Use direct RAG (immediate workaround)
docker exec arifosmcp_server python3 -c "from scripts.arifos_rag import ConstitutionalRAG; ..."
```

### 2. Install Core Skills
```bash
docker exec openclaw_gateway clawhub search "doctor"
docker exec openclaw_gateway clawhub install openclaw-doctor
docker exec openclaw_gateway clawhub install openclaw-gateway-manager
```

### 3. Validate Full Chain
```bash
# Health check
docker exec openclaw_gateway openclaw doctor

# Memory test
docker exec openclaw_gateway openclaw memory search "constitutional law"

# MCP test
docker exec openclaw_gateway mcporter call arifos-mcp/vector_memory query="test"
```

---

## Reference: OpenClaw Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                             │
│                     (Node.js process)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  WebSocket  │  │   HTTP API  │  │     Control UI          │ │
│  │   (18789)   │  │  (/mcp)     │  │    (Dashboard)          │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────────┘ │
│         │                │                     │                │
│  ┌──────┴────────────────┴─────────────────────┴──────────┐   │
│  │                    Agent Core                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  Sessions   │  │   Skills    │  │  Memory (BGE)   │  │   │
│  │  │  (chat)     │  │  (tools)    │  │  (vector)       │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌───────────────────────────┼─────────────────────────────┐   │
│  │                          ▼                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │  Telegram   │  │  WhatsApp   │  │  Discord        │  │   │
│  │  │  (active)   │  │  (config)   │  │  (config)       │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP 2025-11-25
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    arifOS MCP Server                             │
│                    (Python/FastMCP)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  BGE-M3     │  │   Qdrant    │  │   Constitutional        │ │
│  │  (1024d)    │  │  (vectors)  │  │     Kernel (F1-F13)     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conclusion

**Current Capability: 70%**
- Core gateway: ✅ Operational
- Kimi primary: ✅ Configured
- Basic bridge: ⚠️ Protocol mismatch
- Skill registry: ❌ Not utilized
- Full diagnostics: ❌ Not automated

**Path to 100%:**
1. Fix MCP bridge (immediate)
2. Install clawhub skills (Phase 1)
3. Configure mcporter properly
4. Automate health checks

**Estimated effort:** 2-4 hours for full operational capability

---

*DITEMPA BUKAN DIBERI* 🔱💎🧠
*Research based on docs.openclaw.ai, 2026-03-07*
