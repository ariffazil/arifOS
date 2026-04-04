# A820_RUNTIME — External Runtime Integration Guide

**Date:** 2026-03-13  
**Research Source:** arifOS AGENTS / OpenClaw Reference Architecture  
**Target:** arifOS_bot (Any LLM Primary)  
**Status:** OPERATIONAL WITH GAPS

---

## Executive Summary

Based on analysis of external runtime integration patterns, your arifOS-connected gateway is **70% operational**. The core gateway runs with an LLM as primary, but **16 critical skills/toolsets** are needed for full autonomous management.

**Current State:**
- ? Gateway: Running (port 18789)
- ? Primary Model: Configured (LLM-agnostic)
- ? Tools Profile: full
- ? Channel: Telegram configured
- ?? Skills: None installed via skill hub
- ?? MCP: arifos-mcp configured but protocol mismatch
- ?? Memory: Not wired to gateway directly

---

## Required Skill Categories (16 Total)

### Category 1: Core Gateway CLI Skills (CRITICAL - 5 skills)

These are built into the gateway CLI but need to be exposed as agent-accessible capabilities:

| Skill | CLI Command | Purpose | Priority |
|-------|-------------|---------|----------|
| **gateway-doctor** | `gateway doctor` | Health checks, config validation, auto-fixes | ?? CRITICAL |
| **gateway-lifecycle** | `gateway <start/stop/restart/status>` | Gateway lifecycle management | ?? CRITICAL |
| **gateway-update** | `gateway update` | Self-update mechanism | ?? CRITICAL |
| **gateway-config** | `gateway config <get/set/validate>` | Configuration management | ?? HIGH |
| **gateway-status** | `gateway status --deep` | Comprehensive health diagnostics | ?? HIGH |

**Implementation Notes:**
- These use containerized CLI (Node.js/Python binary in container)
- Gateway runs as process inside container (not systemd)
- Use `docker exec <gateway_container> <command>`

---

### Category 2: arifOS Bridge Skills (CRITICAL - 3 skills)

Direct integration with arifOS MCP server:

| Skill | Tool | Purpose | Status |
|-------|------|---------|--------|
| **arifos-memory** | `vector_memory` | Semantic search (BGE-M3 + Qdrant) | ?? Needs MCP fix |
| **arifos-governance** | `apex_judge` | Constitutional validation | ?? Needs MCP fix |
| **arifos-search** | `search_reality` | Web + vector hybrid search | ?? Needs MCP fix |

**Current Blocker:** MCP 2025-11-25 protocol mismatch
- Bridge expects: Simple HTTP POST
- arifOS requires: Session init ? JSON-RPC ? SSE response
- **Fix needed:** Update bridge client to full MCP client

---

### Category 3: Skill Registry Management (HIGH - 3 skills)

Manage skills ecosystem:

| Skill | CLI | Purpose |
|-------|-----|---------|
| **skillhub-search** | `skillhub search <query>` | Find skills in registry |
| **skillhub-install** | `skillhub install <slug>` | Install from registry |
| **skillhub-sync** | `skillhub sync` | Publish/sync local skills |

---

### Category 4: MCP Server Management (HIGH - 2 skills)

Manage MCP tool servers:

| Skill | CLI | Purpose |
|-------|-----|---------|
| **mcp-config** | `mcp config <add/remove>` | Manage MCP servers |
| **mcp-call** | `mcp call <tool>` | Direct tool execution |

**Current Issue:** arifos-mcp added but returns SSE error
- Needs proper MCP client configuration
- Consider: `npx @modelcontextprotocol/sdk@latest` for testing

---

### Category 5: Memory & Knowledge (MEDIUM - 3 skills)

| Skill | CLI/Tool | Purpose | Wiring |
|-------|----------|---------|--------|
| **memory-search** | `memory search` | Vector search over MEMORY.md | ? Native |
| **memory-index** | `memory index` | Reindex memory files | ? Native |
| **rag-constitutional** | Direct Python | BGE-M3 + Qdrant via arifosmcp | ?? Bridge needed |

---

## Detailed Gap Analysis

### Gap 1: No `gateway-doctor` Integration

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
docker exec <gateway_container> gateway doctor [--fix] [--deep]
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
gateway restart [--force]
gateway status [--deep]
gateway probe
gateway logs --follow
```

---

### Gap 3: MCP Protocol Bridge (CRITICAL)

**Current broken flow:**
```
External Gateway ? arifos CLI ? HTTP POST ? arifOS MCP ? ? 404/406
```

**Required flow (MCP 2025-11-25):**
```
External Gateway ? MCP Client ? GET /mcp (session) ? POST /mcp (JSON-RPC) ? SSE response
```

**Implementation options:**

Option A: Fix bridge script to handle SSE
- Parse `event: message\ndata: {...}` format
- Extract session ID from headers
- Manage session lifecycle

Option B: Install proper MCP SDK
```bash
npm install -g @modelcontextprotocol/sdk@latest
# Use: npx @modelcontextprotocol/sdk call arifos-mcp vector_memory
```

Option C: Use mcp client as bridge
```bash
mcp call arifos-mcp/vector_memory query="test"
```

---

### Gap 4: Model Provider Management

**Missing:** Dynamic model switching and health checks

**Needed commands:**
```bash
models status [--probe]
models set <model>
models fallbacks list/add/remove
models auth order set <provider> <order...>
```

**Use case:** Fallback chain verification when primary LLM is down

---

### Gap 5: Channel Health Monitoring

**Missing:** Proactive channel diagnostics

**Needed:**
```bash
channels status [--probe]
channels logs [--lines 100]
health [--timeout 5000]
```

---

## Recommended Skill Installation Order

### Phase 1: Foundation (Critical)
1. **gateway-doctor** - Health diagnostics
2. **gateway-lifecycle** - Lifecycle management
3. **arifos-mcp-fixed** - Working MCP bridge

### Phase 2: Operations (High)
4. **gateway-config** - Configuration management
5. **skillhub-manager** - Skill registry
6. **mcp-client** - MCP servers

### Phase 3: Intelligence (Medium)
7. **memory-search-enhanced** - Vector + constitutional
8. **rag-hybrid** - BGE-M3 + web search
9. **model-fallback** - Automatic failover

### Phase 4: Advanced (Low)
10. **cron-manager** - Scheduled jobs
11. **browser-automation** - Headless browser
12. **node-controller** - Device nodes

---

## Immediate Action Items

### 1. Fix MCP Bridge (CRITICAL)
```bash
# Test current state
docker exec <gateway_container> arifos health

# Options:
# A. Install MCP CLI
npm install -g @modelcontextprotocol/sdk@latest

# B. Update arifos script to parse SSE
docker cp /opt/arifos/data/gateway/bin/arifos <gateway_container>:/home/node/.local/bin/arifos

# C. Use direct RAG (immediate workaround)
docker exec arifosmcp_server python3 -c "from scripts.arifos_rag import ConstitutionalRAG; ..."
```

### 2. Install Core Skills
```bash
docker exec <gateway_container> skillhub search "doctor"
docker exec <gateway_container> skillhub install gateway-doctor
docker exec <gateway_container> skillhub install gateway-lifecycle-manager
```

### 3. Validate Full Chain
```bash
# Health check
docker exec <gateway_container> gateway doctor

# Memory test
docker exec <gateway_container> memory search "constitutional law"

# MCP test
docker exec <gateway_container> mcp call arifos-mcp/vector_memory query="test"
```

---

## Reference: External Gateway Architecture

```
+---------------------------------------------------------------+
¦                     External Gateway                          ¦
¦                     (Container process)                       ¦
+---------------------------------------------------------------¦
¦  +--------------+  +--------------+  +--------------------+  ¦
¦  ¦  WebSocket   ¦  ¦   HTTP API   ¦  ¦     Control UI     ¦  ¦
¦  ¦   (18789)    ¦  ¦  (/mcp)      ¦  ¦    (Dashboard)     ¦  ¦
¦  +--------------+  +--------------+  +--------------------+  ¦
¦         ¦                 ¦                    ¦             ¦
¦  +----------------------------------------------------+      ¦
¦  ¦                    Agent Core                      ¦      ¦
¦  ¦  +----------+  +----------+  +----------------+   ¦      ¦
¦  ¦  ¦ Sessions ¦  ¦  Skills  ¦  ¦ Memory (BGE)   ¦   ¦      ¦
¦  ¦  ¦ (chat)   ¦  ¦ (tools)  ¦  ¦ (vector)       ¦   ¦      ¦
¦  ¦  +----------+  +----------+  +----------------+   ¦      ¦
¦  +---------------------------------------------------+      ¦
¦                              ¦                                ¦
+------------------------------+--------------------------------+
                               ¦ MCP 2025-11-25
                               ?
+---------------------------------------------------------------+
¦                    arifOS MCP Server                          ¦
¦                    (Python/FastMCP)                           ¦
+---------------------------------------------------------------¦
¦  +----------+  +----------+  +------------------------+      ¦
¦  ¦  BGE-M3  ¦  ¦  Qdrant  ¦  ¦   Constitutional       ¦      ¦
¦  ¦ (1024d)  ¦  ¦ (vectors)¦  ¦     Kernel (F1-F13)    ¦      ¦
¦  +----------+  +----------+  +------------------------+      ¦
+---------------------------------------------------------------+
```

---

## Conclusion

**Current Capability: 70%**
- Core gateway: ? Operational
- LLM primary: ? Configured (model-agnostic)
- Basic bridge: ?? Protocol mismatch
- Skill registry: ? Not utilized
- Full diagnostics: ? Not automated

**Path to 100%:**
1. Fix MCP bridge (immediate)
2. Install skillhub skills (Phase 1)
3. Configure mcp client properly
4. Automate health checks

**Estimated effort:** 2-4 hours for full operational capability

---

*DITEMPA BUKAN DIBERI* ??????
*Reference Architecture for LLM-Agnostic Integration, 2026-03-13*
