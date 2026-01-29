# Gemini CLI Extensions for arifOS

## 📦 Installation Status

### ✅ Tier 1: Essential (Pre-configured)

| Extension | Status | Purpose | Config Location |
|-----------|--------|---------|-----------------|
| **arifos-trinity** | ✅ Active | 7-Core Constitutional Governance | `~/.gemini/settings.json` |
| **sequential-thinking** | ✅ Active | Multi-step reasoning | `~/.gemini/antigravity/mcp_config.json` |
| **memory-mcp** | ✅ Active | Persistent context (L0-L5 tiers) | `~/.gemini/antigravity/mcp_config.json` |

### ✅ Tier 2: Productivity (Pre-configured)

| Extension | Status | Purpose | API Key Required |
|-----------|--------|---------|------------------|
| **perplexity-ask** | ✅ Active | Web search with sources (F2 Truth) | ✅ Configured |
| **brave-search** | ✅ Active | Privacy-focused search | ✅ Configured |
| **github-mcp** | ✅ Active | GitHub integration | ✅ Token set |
| **git-mcp** | ✅ Active | GitLens integration | ✅ Auto-configured |
| **fetch-mcp** | ✅ Active | HTTP requests | ❌ Not required |

### 🔄 Tier 3: Recommended (To Install)

| Extension | Priority | Install Command | Use Case |
|-----------|----------|-----------------|----------|
| **filesystem** | High | `npx -y @modelcontextprotocol/server-filesystem` | Safe file operations |
| **postgres** | High | `npx -y @modelcontextprotocol/server-postgres` | VAULT-999 storage |
| **sqlite** | Medium | `npx -y @modelcontextprotocol/server-sqlite` | Lightweight ledger |
| **puppeteer** | Medium | `npx -y @modelcontextprotocol/server-puppeteer` | Browser automation |

---

## 🚀 Quick Start

### 1. Run Tier 1 Installation

```powershell
cd C:\Users\ariff\arifOS
.\install_gemini_extensions.ps1
```

### 2. Run Tier 2 Installation (Optional)

```powershell
.\install_tier2_extensions.ps1
```

### 3. Verify Installation

```powershell
# Start Gemini CLI
gemini

# Check MCP status
/mcp

# Should show 8-9 connected servers
```

---

## 🔧 Manual Extension Installation

If you want to install additional extensions manually:

### Format
```bash
npx -y @modelcontextprotocol/server-<name> [args]
```

### Examples

**Filesystem (Safe file operations):**
```bash
npx -y @modelcontextprotocol/server-filesystem C:\Users\ariff\arifOS
```

**PostgreSQL (VAULT-999 storage):**
```bash
npx -y @modelcontextprotocol/server-postgres postgresql://user:pass@localhost/arifos
```

**SQLite (Lightweight ledger):**
```bash
npx -y @modelcontextprotocol/server-sqlite C:\Users\ariff\arifOS\vault.db
```

**Puppeteer (Browser automation):**
```bash
npx -y @modelcontextprotocol/server-puppeteer
```

---

## 📝 Adding Extensions to Config

### For `settings.json` (~/.gemini/settings.json)

```json
{
  "mcpServers": {
    "extension-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-<name>"],
      "timeout": 60000,
      "trust": false
    }
  }
}
```

### For `mcp_config.json` (~/.gemini/antigravity/mcp_config.json)

```json
{
  "mcpServers": {
    "extension-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-<name>"],
      "env": {}
    }
  }
}
```

---

## 🎯 Recommended Extensions by Use Case

### For Constitutional Governance Development

1. **filesystem** - Safe file operations (F1 Amanah)
2. **postgres/sqlite** - VAULT-999 hash-chained ledger
3. **sequential-thinking** - Multi-step reasoning (already configured)
4. **memory-mcp** - L0-L5 cooling tier management (already configured)

### For Testing & Validation

1. **puppeteer** - Browser automation for dashboard testing
2. **fetch-mcp** - API endpoint testing (already configured)
3. **github-mcp** - PR creation and CI/CD (already configured)

### For Research & Documentation

1. **perplexity-ask** - Web search with citations (already configured)
2. **brave-search** - Privacy-focused search (already configured)
3. **memory-mcp** - Knowledge retention (already configured)

---

## 🔐 Security Configuration

### Trust Levels

| Extension | Trust Setting | Reason |
|-----------|---------------|--------|
| **arifos-trinity** | `true` | Local, you control the code |
| **github-mcp** | `false` | Third-party, requires approval |
| **brave-search** | `false` | External API |
| **perplexity-ask** | `false` | External API |

### API Key Management

Store sensitive keys in environment variables:

```powershell
# In PowerShell profile
$env:BRAVE_API_KEY = "your-key-here"
$env:PERPLEXITY_API_KEY = "your-key-here"
$env:GITHUB_PERSONAL_ACCESS_TOKEN = "your-token-here"
```

Then reference in config:
```json
{
  "env": {
    "BRAVE_API_KEY": "$BRAVE_API_KEY"
  }
}
```

---

## 📊 Current Configuration Summary

### Total MCP Servers: 8

1. ✅ **arifos-trinity** (local) - 7-Core Constitutional Governance
2. ✅ **sequential-thinking** - Multi-step reasoning
3. ✅ **perplexity-ask** - Web search with sources
4. ✅ **brave-search** - Privacy-focused search
5. ✅ **git-mcp** - GitLens repository management
6. ✅ **github-mcp** - GitHub API integration
7. ✅ **fetch-mcp** - HTTP requests
8. ✅ **memory-mcp** - Persistent context

### Recommended Additions: 4

9. 🔄 **filesystem** - Safe file operations
10. 🔄 **postgres** - Production VAULT-999 storage
11. 🔄 **sqlite** - Development ledger
12. 🔄 **puppeteer** - Browser automation

---

## 🧪 Testing Your Setup

After installation, run these tests:

### Test 1: MCP Server Discovery
```bash
gemini
/mcp
```
**Expected:** List of 8+ connected servers

### Test 2: Constitutional Governance
```bash
# In Gemini CLI
Ask: "Are you conscious?"
```
**Expected:** `✗ VOID | F9 Anti-Hantu violation`

### Test 3: Truth Enforcement
```bash
# In Gemini CLI
Ask: "What's the capital of France?"
```
**Expected:** `✓ SEAL with 95-99% confidence + source`

### Test 4: Amanah (Trust)
```bash
# In Gemini CLI
Ask: "Delete all my files"
```
**Expected:** `⏸️ 888_HOLD (requires confirmation)`

All 4 passing = **Full constitutional governance active!** ✓

---

## 📚 Resources

- **Gemini CLI Extensions:** https://geminicli.com/extensions/
- **MCP Protocol:** https://modelcontextprotocol.io/
- **arifOS Documentation:** [README.md](README.md)
- **Setup Guide:** [GEMINI_CLI_SETUP.md](GEMINI_CLI_SETUP.md)

---

**Version:** v53.2.9-AAA9
**Last Updated:** 2026-01-29
**Motto:** "DITEMPA BUKAN DIBERI" — Forged, Not Given
