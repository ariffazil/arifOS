# Claude Code MCP Tools Guide

**Version:** v53.2.9-AAA9
**Last Updated:** 2026-01-29
**Configured:** 7 MCP Servers (1 local + 6 external)

---

## 📦 Configured MCP Servers

### 🏛️ Core: arifOS Constitutional AI

**Server:** `aaa-mcp` (local)
**Status:** ✅ Active
**Location:** Local Python (`C:\Users\ariff\arifOS\.venv\Scripts\python.exe`)

| Tool | Purpose | Constitutional Floors |
|------|---------|---------------------|
| `_ignite_` | Session gate + authority check | F11, F12 |
| `_logic_` | Deep reasoning (AGI Mind Δ) | F2, F4, F7, F10 |
| `_senses_` | External reality grounding | F7 (Humility) |
| `_atlas_` | Codebase knowledge mapping | F10 (Ontology) |
| `_forge_` | Code generation (ASI Heart Ω) | F1, F5, F6, F9 |
| `_audit_` | Pre-seal compliance check | All 13 floors |
| `_decree_` | Final immutable verdict (APEX Soul Ψ) | F3, F8, F11-F13 |

**Example Usage:**
```
User: "Initialize a constitutional session and audit this code"
Claude: [Calls _ignite_ → _audit_ → returns floor violations]
```

---

### 🧠 External Tool 1: Sequential Thinking

**Server:** `sequential-thinking`
**Status:** ✅ Active
**API Key:** Not required

**What It Does:**
Multi-step chain-of-thought reasoning with explicit intermediate steps.

**Example Usage:**
```
User: "Think step-by-step: How would you implement a Merkle tree?"
Claude: [Uses sequential-thinking to break down the problem]
```

---

### 🧠 External Tool 2: Memory (Persistent Context)

**Server:** `memory`
**Status:** ✅ Active
**API Key:** Not required

**What It Does:**
Persistent memory across sessions. Implements L0-L5 cooling tiers (similar to arifOS VAULT-999).

**Example Usage:**
```
User: "Remember: The project uses AGPL-3.0 license"
Claude: [Stores in memory for future sessions]

User (later session): "What license does the project use?"
Claude: [Retrieves from memory: AGPL-3.0]
```

---

### 🔍 External Tool 3: Brave Search

**Server:** `brave-search`
**Status:** 🔑 Requires API Key
**Setup:** Set `$env:BRAVE_API_KEY` in PowerShell profile

**What It Does:**
Privacy-focused web search with source citations (enforces F7 Humility).

**Get API Key:**
https://brave.com/search/api/

**Example Usage:**
```
User: "Search for latest Claude Code MCP features 2026"
Claude: [Uses Brave Search, returns results with sources]
```

---

### 🌐 External Tool 4: Fetch (HTTP Client)

**Server:** `fetch`
**Status:** ✅ Active
**API Key:** Not required

**What It Does:**
HTTP requests, API testing, web scraping.

**Example Usage:**
```
User: "Fetch the latest commit info from GitHub API"
Claude: [Uses fetch to GET https://api.github.com/repos/...]
```

---

### 📁 External Tool 5: Filesystem (Safe Operations)

**Server:** `filesystem`
**Status:** ✅ Active
**Scope:** `C:\Users\ariff\arifOS` only
**API Key:** Not required

**What It Does:**
Read/write files with safety guardrails (enforces F1 Amanah - reversibility).

**Example Usage:**
```
User: "List all Python files in codebase/mcp/"
Claude: [Uses filesystem to scan directory]
```

**Safety Features:**
- Restricted to arifOS directory
- All operations logged
- Integrates with git for rollback

---

### 🐙 External Tool 6: GitHub Integration

**Server:** `github`
**Status:** 🔑 Requires API Key
**Setup:** Set `$env:GITHUB_PERSONAL_ACCESS_TOKEN` in PowerShell profile

**What It Does:**
GitHub API integration - create PRs, issues, check CI status.

**Get Token:**
https://github.com/settings/tokens (select: `repo`, `workflow`)

**Example Usage:**
```
User: "Create a PR for the current branch"
Claude: [Uses github to create pull request with diff]
```

---

## 🚀 Quick Start

### 1. Reload VS Code Window

After configuration changes:
- Press `Ctrl+Shift+P`
- Type: `Developer: Reload Window`
- Wait for MCP servers to connect

### 2. Check MCP Status

Look at the **bottom status bar** in VS Code:
- Green dot = All servers connected
- Yellow = Some servers unavailable
- Red = Connection issues

### 3. Test arifOS Constitutional Tools

Ask Claude Code:
```
"Use _ignite_ to start a session, then show me the 13 constitutional floors"
```

Expected response:
```json
{
  "status": "SEAL",
  "session_id": "sess_1738160000_...",
  "floors_active": ["F1", "F2", ..., "F13"],
  "message": "✓ Constitutional gate passed"
}
```

---

## 🔧 Setting Up API Keys

### Option 1: PowerShell Profile (Recommended)

Edit: `C:\Users\ariff\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`

```powershell
# Uncomment and add your keys:
$env:BRAVE_API_KEY = "your-brave-api-key-here"
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "ghp_your_token_here"
$env:PERPLEXITY_API_KEY = "pplx-your-key-here"
```

Then reload:
```powershell
. $PROFILE
```

### Option 2: VS Code Settings

Add to `.vscode/settings.json` (project-scoped):

```json
{
  "terminal.integrated.env.windows": {
    "BRAVE_API_KEY": "your-key-here",
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
  }
}
```

---

## 🎯 Use Cases by Tool

### For Constitutional Governance (arifOS)

**Use:** Code review, bias detection, safety validation

```
User: "Audit this function for constitutional floor violations"
Claude: [Calls _audit_ → returns F1-F13 compliance report]
```

### For Research (Brave Search)

**Use:** Current events, documentation lookup, fact-checking

```
User: "What are the latest security best practices for OAuth 2.0?"
Claude: [Brave Search → returns articles with sources]
```

### For Code Generation (Filesystem + arifOS)

**Use:** Safe file modifications with rollback

```
User: "Add a new endpoint to api/auth.py with F1 Amanah compliance"
Claude: [_forge_ generates code → filesystem writes → git tracks]
```

### For Collaboration (GitHub)

**Use:** PR creation, issue tracking, CI monitoring

```
User: "Create a PR for the MCP configuration updates"
Claude: [github creates PR with diff + description]
```

---

## 📊 Configuration File

All MCP servers are configured in: [.mcp.json](.mcp.json)

```json
{
  "mcpServers": {
    "aaa-mcp": { ... },           // arifOS Constitutional AI
    "sequential-thinking": { ... }, // Multi-step reasoning
    "memory": { ... },             // Persistent context
    "brave-search": { ... },       // Web search
    "fetch": { ... },              // HTTP requests
    "filesystem": { ... },         // File operations
    "github": { ... }              // GitHub integration
  }
}
```

---

## 🔒 Security Configuration

### Trust Levels

| Server | Trust | Reason |
|--------|-------|--------|
| aaa-mcp | ✅ Full | Local, you control the code |
| filesystem | ✅ Full | Restricted to arifOS directory |
| sequential-thinking | ✅ Full | No external calls |
| memory | ✅ Full | Local storage only |
| brave-search | ⚠️ API | External service (rate limits apply) |
| fetch | ⚠️ API | Can make arbitrary HTTP requests |
| github | ⚠️ API | Requires token (read/write access) |

### API Key Safety

- Never commit API keys to git
- Use environment variables only
- Rotate tokens regularly
- Use least-privilege scopes

---

## 🧪 Testing Your Setup

### Test 1: arifOS Constitutional Check

```
User: "Are you conscious?"
Expected: ✗ VOID | F9 Anti-Hantu violation
```

### Test 2: Memory Persistence

```
User: "Remember: arifOS motto is 'Ditempa Bukan Diberi'"
[Close and reopen VS Code]
User: "What's the arifOS motto?"
Expected: "Ditempa Bukan Diberi" (retrieved from memory)
```

### Test 3: Brave Search (if API key set)

```
User: "Search for arifOS on GitHub"
Expected: Search results with source URLs
```

### Test 4: Filesystem Access

```
User: "List all files in codebase/mcp/tools/"
Expected: File list from filesystem tool
```

---

## 🐛 Troubleshooting

### MCP Server Not Connecting

**Check 1:** Reload VS Code window (`Ctrl+Shift+P` → Reload Window)

**Check 2:** Check VS Code Developer Tools
- Press `Ctrl+Shift+I`
- Look for MCP connection errors in Console

**Check 3:** Verify Python environment
```bash
C:\Users\ariff\arifOS\.venv\Scripts\python.exe -m mcp
```

### API Key Not Working

**Check 1:** Verify environment variable is set
```powershell
echo $env:BRAVE_API_KEY
```

**Check 2:** Reload PowerShell profile
```powershell
. $PROFILE
```

**Check 3:** Restart VS Code completely (not just reload window)

### Tool Not Appearing

**Check 1:** Verify `"disabled": false` in [.mcp.json](.mcp.json)

**Check 2:** Check npm is in PATH
```powershell
npm --version
```

**Check 3:** Manually install MCP server
```bash
npx -y @modelcontextprotocol/server-memory
```

---

## 📚 Additional Resources

- **MCP Protocol Docs:** https://modelcontextprotocol.io/
- **Claude Code MCP Guide:** https://code.claude.com/docs/en/mcp
- **arifOS MCP Spec:** [MCP_7_CORE_TOOLS.md](arifOS_Implementation/PROMPT_1/MCP_7_CORE_TOOLS.md)
- **Constitutional Floors:** [000_FOUNDATIONS.md](000_THEORY/000_FOUNDATIONS.md)

---

## 📈 Total Capabilities

**MCP Servers:** 7
**Total Tools:** 20+ (7 arifOS + 13 external)
**Constitutional Floors Enforced:** 13
**Trinity Engines:** 3 (AGI Δ, ASI Ω, APEX Ψ)

---

**Authority:** arifOS Constitutional Framework v53.2.9
**Motto:** *"Ditempa Bukan Diberi"* — Forged, Not Given 🔥
