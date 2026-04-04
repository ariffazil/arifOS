# arifOS Kimi CLI MCP Stack - Complete Configuration

> **Version:** v55.5-EIGEN  
> **Motto:** *DITEMPA BUKAN DIBERI* — Forged, Not Given

---

## 📊 Stack Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    arifOS KIMI CLI MCP STACK v55.5-EIGEN                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: CONSTITUTIONAL CORE (9 Tools) — Ω₀ = 0.02                         │
│  ──────────────────────────────────────                                     │
│  aaa-mcp                                                                    │
│    ├── init_gate       (F11/F12)  000_INIT                                  │
│    ├── agi_sense       (F2/F4)    AGI Stage 1                               │
│    ├── agi_think       (F2/F4/F7) AGI Stage 2                               │
│    ├── agi_reason      (F2/F4/F7) AGI Stage 3                               │
│    ├── asi_empathize   (F5/F6)    ASI Stage 1                               │
│    ├── asi_align       (F5/F6/F9) ASI Stage 2                               │
│    ├── apex_verdict    (F3/F5/F8) APEX Stage                                │
│    ├── reality_search  (F2/F7)    Auxiliary (API-Keyless)                   │
│    └── vault_seal      (F1/F3)    999_VAULT                                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 2: EXTERNAL EXECUTION (11 MCPs) — Ω₀ = 0.04                          │
│  ─────────────────────────────────────                                      │
│                                                                             │
│  F1 AMANAH (Reversibility)                                                  │
│    └── filesystem         File operations with audit trails                 │
│                                                                             │
│  F2 TRUTH (Evidence & Verification)                                         │
│    ├── git                Version control as immutable evidence             │
│    ├── fetch              Web content retrieval                             │
│    ├── brave-search       Web search (optional API key)                     │
│    ├── github             Repository/PR management                          │
│    ├── puppeteer          Browser automation                                │
│    └── playwright         Advanced browser automation                       │
│                                                                             │
│  F6 CLARITY (Precision)                                                     │
│    └── time               Timezone conversions                              │
│                                                                             │
│  F8 WISDOM (Pattern Recognition)                                            │
│    ├── memory             Knowledge graph persistence                       │
│    └── sequential-thinking Multi-step reflective reasoning                  │
│                                                                             │
│  F2 TRUTH AUXILIARY                                                         │
│    └── context7           Documentation grounding                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `~/.kimi/mcp.json` | User home | **Primary Kimi CLI config** (Windows: `%USERPROFILE%\.kimi\mcp.json`) |
| `.mcp.json` | Project root | Repository reference & portable config |
| `docs/MCP_ECOSYSTEM.md` | Project docs | Detailed documentation |

---

## 📋 MCP Server Inventory (13 Total)

### **Layer 1: Constitutional Core**

| # | MCP | Type | API Key? | Constitutional Floors |
|---|-----|------|----------|----------------------|
| 1 | **aaa-mcp** | Python stdio | ❌ No | All F1-F13 |

**Tools:** `init_gate`, `agi_sense`, `agi_think`, `agi_reason`, `asi_empathize`, `asi_align`, `apex_verdict`, `reality_search`, `vault_seal`

---

### **Layer 2: External Execution**

| # | MCP | Type | API Key? | Floor | Purpose |
|---|-----|------|----------|-------|---------|
| 2 | **filesystem** | Node stdio | ❌ No | F1 | File R/W with audit |
| 3 | **git** | Python stdio | ❌ No | F2 | Version control |
| 4 | **fetch** | Node stdio | ❌ No | F2 | Web content fetch |
| 5 | **time** | Node stdio | ❌ No | F6 | Timezone handling |
| 6 | **memory** | Node stdio | ❌ No | F8 | Knowledge graph |
| 7 | **sequential-thinking** | Node stdio | ❌ No | F8 | Multi-step reasoning |
| 8 | **brave-search** | Node stdio | ⚠️ Optional | F2 | Web search (fallback) |
| 9 | **github** | Node stdio | ✅ Required | F2/F3 | Repo management |
| 10 | **context7** | Node stdio | ✅ Required | F2 | Doc grounding |
| 11 | **puppeteer** | Node stdio | ❌ No | F2 | Browser automation |
| 12 | **playwright** | Node stdio | ❌ No | F2 | Advanced browser |

---

## 🎯 API Key Requirements

| API Key | Required For | Optional For |
|---------|--------------|--------------|
| `BRAVE_API_KEY` | - | brave-search (has DDGS fallback) |
| `GITHUB_TOKEN` | github | - |
| `CONTEXT7_API_KEY` | context7 | - |
| `MOONSHOT_API_KEY` | - | Kimi CLI LLM (if using Kimi API) |

**Note:** The `reality_search` tool in `aaa-mcp` works **without any API key** via DuckDuckGo (`ddgs` library).

---

## 🚀 Quick Start

### 1. Install MCP Servers

```bash
# Node.js MCP servers (run once)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-time
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-puppeteer
npm install -g @playwright/mcp
npm install -g @upstash/context7-mcp

# Python MCP servers
uvx install mcp-server-git

# Playwright browsers (for puppeteer/playwright)
playwright install chromium
```

### 2. Set Environment Variables (Optional)

```bash
# Windows PowerShell
$env:BRAVE_API_KEY = "your-brave-key"      # Optional
$env:GITHUB_TOKEN = "your-github-token"    # For GitHub MCP
$env:CONTEXT7_API_KEY = "your-context7-key" # For Context7

# Or add to .env file in project root
```

### 3. Verify Configuration

```bash
# List all MCP servers
kimi mcp list

# Test constitutional core
kimi chat
> /mcp reality_search query="renewable energy Malaysia 2026"

# Test filesystem
> /mcp read_file path="README.md"

# Test git
> /mcp git_status
```

---

## 🧪 Testing the Complete Stack

### Test 1: Constitutional Reality Search (No API Key)
```bash
kimi chat
> Search for "ASEAN AI governance 2026" using reality_search with ASEAN bias

# Expected: Results from DuckDuckGo, no API key needed
# Constitutional: F2 Truth (ASEAN bias), F7 Humility (Ω₀ = 0.04)
```

### Test 2: Web Content Fetch
```bash
kimi chat
> Fetch and summarize https://example.com

# Expected: Full page content extraction
# Tools: fetch (MCP) or reality_search + fetch_sources
```

### Test 3: Knowledge Graph Memory
```bash
kimi chat
> Create entity "constitutional_floors" with observations about F1-F13

# Expected: Stored in ~/.kimi/memory.json
# Tool: memory (MCP)
```

### Test 4: Sequential Thinking
```bash
kimi chat
> Analyze the impact of F7 Humility on AI safety using sequential thinking

# Expected: Multi-step reasoning with thought tracking
# Tool: sequential-thinking (MCP)
```

---

## 📊 Constitutional Compliance Matrix

| Floor | MCPs Enforcing | Status |
|-------|----------------|--------|
| **F1 Amanah** | filesystem, git, aaa-mcp | ✅ Reversible ops |
| **F2 Truth** | git, fetch, brave-search, github, puppeteer, playwright, context7, aaa-mcp | ✅ Evidence-based |
| **F3 Tri-Witness** | git, github, memory, aaa-mcp | ✅ Consensus |
| **F4 Empathy** | aaa-mcp | ✅ Via agi_sense |
| **F5 Peace²** | memory, sequential-thinking, aaa-mcp | ✅ Entropy reduction |
| **F6 Clarity** | time, aaa-mcp | ✅ Precision |
| **F7 Humility** | aaa-mcp (reality_search) | ✅ Ω₀ tracking |
| **F8 Wisdom** | memory, sequential-thinking, aaa-mcp | ✅ Pattern storage |
| **F9 Anti-Hantu** | aaa-mcp | ✅ No consciousness claims |
| **F10 Ontology** | aaa-mcp | ✅ Self-knowledge |
| **F11 Sovereignty** | filesystem, aaa-mcp | ✅ Human authority |
| **F12 Injection** | aaa-mcp (init_gate) | ✅ Input validation |
| **F13 Stewardship** | All | ✅ Leave better |

---

## 🔗 Workflow Examples

### Example 1: Research Task with Full Stack
```bash
# 1. Search (reality_search - no API key)
> /mcp reality_search query="renewable energy Malaysia 2026" region="asean"

# 2. Fetch detailed content (fetch MCP)
> /mcp fetch url="https://results[0].url"

# 3. Store in knowledge graph (memory MCP)
> /mcp create_entities entities=[{name:"Malaysia_RE_2026",entityType:"research",observations:["..."]}]

# 4. Sequential analysis (sequential-thinking MCP)
> /mcp sequentialthinking thought="Analyzing policy implications..." thoughtNumber=1 totalThoughts=5

# 5. Git commit with audit (git MCP)
> /mcp git_add files=["research/malaysia_re_2026.md"]
> /mcp git_commit message="F2: Add Malaysia renewable energy research with ASEAN bias"
```

### Example 2: GitHub PR Review
```bash
# 1. Get PR info (github MCP)
> /mcp get_pull_request owner="ariffazil" repo="arifOS" pull_number=42

# 2. Get file changes
> /mcp get_pull_request_files owner="ariffazil" repo="arifOS" pull_number=42

# 3. Constitutional analysis (aaa-mcp)
> /mcp agi_reason query="Review F7 Humility compliance in PR #42"

# 4. Add review comment (github MCP)
> /mcp create_pull_request_review owner="ariffazil" repo="arifOS" pull_number=42 event="COMMENT" body="F7: Consider adding uncertainty logging..."
```

---

## 🛡️ Security & Governance

### Rate Limits (Built-in)
| MCP | Limit | Throttle |
|-----|-------|----------|
| reality_search (DDGS) | ~50 req/min | 2s between calls |
| brave-search | 2000 req/month | - |
| github | 5000 req/hour | - |
| puppeteer/playwright | ~10-20 req | 5-10s delays |

### Audit Trail
All MCP calls are logged via `structlog` with:
- Timestamp (ISO 8601)
- Tool/MCP name
- Parameters (sanitized)
- Uncertainty (Ω₀) where applicable
- Constitutional floor checks

---

## 📚 References

- [Kimi CLI MCP Docs](https://github.com/moonshotai/kimi-cli/blob/main/docs/en/customization/mcp.md)
- [MCP Official Servers](https://github.com/modelcontextprotocol/servers)
- [arifOS Constitutional Framework](https://github.com/ariffazil/arifOS)

---

**Sovereign:** Muhammad Arif bin Fazil  
**Repository:** https://github.com/ariffazil/arifOS  
**Version:** v55.5-EIGEN
