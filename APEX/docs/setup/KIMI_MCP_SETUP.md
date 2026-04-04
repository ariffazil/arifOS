# arifOS MCP → Kimi Code Setup Guide

**DITEMPA BUKAN DIBERI — Forged, Not Given**

---

## 📍 Configuration File Locations

| Platform | Location | Purpose |
|----------|----------|---------|
| **Windows** | `C:\Users\<User>\.kimi\mcp.json` | **PRIMARY** — Kimi CLI config |
| **macOS/Linux** | `~/.kimi/mcp.json` | **PRIMARY** — Kimi CLI config |
| **VS Code** | `%APPDATA%\Code\User\mcp.json` | VS Code extension config (different format!) |

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Backup Existing Config

```powershell
# Windows
Copy-Item "$env:USERPROFILE\.kimi\mcp.json" "$env:USERPROFILE\.kimi\mcp.json.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Or manually copy the file before proceeding
```

### Step 2: Deploy New Config

```powershell
# Copy the generated config to Kimi directory
Copy-Item "C:\arifosmcp\kimi-mcp-config.json" "$env:USERPROFILE\.kimi\mcp.json"
```

### Step 3: Verify Environment

```powershell
# Load your secrets (if you have the loader script)
. $env:USERPROFILE\.arifos\load-env.ps1

# Or manually verify these env vars exist:
$env:ARIFOS_GOVERNANCE_SECRET
$env:BRAVE_API_KEY
$env:FIRECRAWL_API_KEY
```

---

## 🧪 Testing the Setup

### Test 1: Check MCP Server List

```bash
# In terminal
kimi mcp list
```

**Expected output:**
```
┌─────────────────────┬─────────┬──────────────────────────────────────┐
│ Name                │ Type    │ Status                               │
├─────────────────────┼─────────┼──────────────────────────────────────┤
│ arifosmcp           │ stdio   │ C:/arifosmcp/.venv/Scripts/python.exe│
│ brave-search        │ stdio   │ npx                                  │
│ context7            │ stdio   │ npx                                  │
│ filesystem          │ stdio   │ npx                                  │
│ github              │ stdio   │ npx                                  │
│ git                 │ stdio   │ uvx                                  │
│ memory              │ stdio   │ npx                                  │
│ sequential-thinking │ stdio   │ npx                                  │
│ sqlite              │ stdio   │ uvx                                  │
│ time                │ stdio   │ uvx                                  │
└─────────────────────┴─────────┴──────────────────────────────────────┘
```

### Test 2: Test arifOS Connection

```bash
kimi mcp test arifosmcp
```

### Test 3: Runtime Health Check

In Kimi Chat:
```
/check_vital
```

Or ask:
```
Use arifOS.kernel to initialize a constitutional session for "deployment verification"
```

---

## 🔀 Hybrid Workflow: My Tools vs arifOS MCP

| Task | Use My Tools (Internal) | Use arifOS MCP |
|------|------------------------|----------------|
| **Read/Edit Code** | ✅ `ReadFile`, `WriteFile`, `StrReplaceFile` | ❌ No direct filesystem |
| **Shell Commands** | ✅ `Shell` | ❌ No shell access |
| **Codebase Analysis** | ✅ `Grep`, `Glob`, direct file access | ❌ Limited via ingest |
| **Web Search** | ✅ Basic `SearchWeb` | ✅ `search_reality` (F2 Truth) |
| **Constitutional Check** | ✅ Basic `apex_judge` | ✅ Full Trinity ΔΩΨ pipeline |
| **Evidence Ingest** | ❌ No direct URL ingest | ✅ `ingest_evidence` |
| **Session Memory** | ❌ Stateless | ✅ `session_memory` (vector recall) |
| **GitHub Operations** | ✅ `github` MCP tools | ✅ Same (external) |
| **Deployments** | ❌ No deployment tools | ✅ Via `arifOS.kernel` + extensions |

---

## 🎯 Recommended Workflows

### Workflow 1: Code Development (My Tools Primary)

```
1. I analyze your codebase using direct file access
2. I suggest changes using WriteFile/StrReplaceFile
3. Before committing, you can ask: "Run arifOS.kernel to validate this refactor"
4. arifOS checks F1-F13 compliance and gives SEAL/VOID verdict
```

### Workflow 2: External Operations (arifOS Primary)

```
1. "Search for latest FastMCP documentation using arifOS"
   → arifOS.search_reality(query="FastMCP v3 stdio transport")
   
2. "Ingest this URL into constitutional context"
   → arifOS.ingest_evidence(url="...")
   
3. "Check deployment readiness"
   → arifOS.check_vital()
   
4. "Run full constitutional review"
   → arifOS.arifOS.kernel(intent={query: "review deployment", mode: "audit"})
```

### Workflow 3: Full Trinity Pipeline

```
User: "Plan a new feature for arifOS"

1. 000 INIT → arifOS.kernel initializes session
2. I (Kimi) analyze codebase using my tools
3. 111 MIND → arifOS.reason_mind_synthesis
4. 666 HEART → arifOS.assess_heart_impact  
5. 777 APEX → arifOS.quantum_eureka_forge
6. 888 JUDGE → arifOS.apex_judge_verdict
7. I implement based on SEAL verdict
8. 999 VAULT → arifOS.seal_vault_commit
```

---

## ⚙️ Advanced Configuration

### Using Project-Specific Config

If you want to keep the default `~/.kimi/mcp.json` but use arifOS for this project only:

```bash
# Run Kimi with project-specific MCP config
kimi --mcp-config-file C:/arifosmcp/kimi-mcp-config.json
```

### Environment Variable Reference

Create/edit `~/.arifos/env`:

```bash
# Core arifOS secrets
ARIFOS_GOVERNANCE_SECRET=your-secret-here

# External APIs
BRAVE_API_KEY=your-brave-key
FIRECRAWL_API_KEY=your-firecrawl-key
PERPLEXITY_API_KEY=your-perplexity-key
BROWSERBASE_API_KEY=your-browserbase-key

# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
```

Load with:
```powershell
. $env:USERPROFILE\.arifos\load-env.ps1
```

---

## 🛠️ Troubleshooting

### Issue: "arifosmcp not found"

```powershell
# Verify Python path
Test-Path "C:/arifosmcp/.venv/Scripts/python.exe"

# If missing, recreate venv
cd C:/arifosmcp
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
```

### Issue: "Module not found: arifosmcp"

```powershell
# Verify PYTHONPATH
cd C:/arifosmcp
.venv\Scripts\python -c "import arifosmcp; print('OK')"

# If fails:
.venv\Scripts\pip install -e .
```

### Issue: Environment variables not loading

```powershell
# Check if vars are set
$env:ARIFOS_GOVERNANCE_SECRET

# If empty, load them:
. $env:USERPROFILE\.arifos\load-env.ps1

# Or set manually for session:
$env:ARIFOS_GOVERNANCE_SECRET = "your-secret"
```

### Issue: Port conflicts (if using HTTP mode)

```powershell
# arifOS MCP uses stdio by default (no ports)
# But if you switch to HTTP:
$env:PORT = 8081  # Use different port
```

---

## 📊 Verifying the Hybrid Setup

Run this diagnostic in Kimi Chat:

```
Please:
1. Use check_vital from arifOS MCP to verify constitutional kernel health
2. List all available tools from both my internal set and arifOS MCP
3. Confirm we have:
   - Direct file access (my tools)
   - Constitutional governance (arifOS MCP)
   - Web grounding (search_reality)
   - Session memory (session_memory)
```

---

## 🔐 Security Notes

- **YOLO Mode**: Disabled by default for constitutional compliance
- **Approval Required**: All `write_file`, `git_commit`, `create_pull_request` require human confirmation
- **VAULT999**: Audit trail stored at `C:/arifosmcp/VAULT999/`
- **Session Isolation**: Each 000→999 loop has unique session_id

---

## 📝 Summary

| Config File | Location | Action |
|------------|----------|--------|
| **New arifOS MCP Config** | `C:/arifosmcp/kimi-mcp-config.json` | ✅ Created |
| **Kimi CLI Config** | `~/.kimi/mcp.json` | 🔲 Copy new config here |
| **Environment** | `~/.arifos/env` | 🔲 Verify secrets loaded |
| **Test** | Run `kimi mcp list` | 🔲 Verify arifosmcp appears |

**Next Step:** Copy `kimi-mcp-config.json` to `~/.kimi/mcp.json` and test!

---

**Motto:** *DITEMPA BUKAN DIBERI — Forged, Not Given*  
**Seal:** 2026.03.12-SEAL
