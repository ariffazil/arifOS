# Codex (OpenAI CLI) + AAA MCP Setup

## Quick Configuration

### Step 1: Install Codex CLI

```bash
# If not already installed
npm install -g @openai/codex
```

### Step 2: Configure MCP

Create or edit your Codex config file:

**macOS/Linux:**
```bash
~/.config/codex/config.json
```

**Windows:**
```bash
%APPDATA%\codex\config.json
```

**Add this configuration:**

```json
{
  "mcpServers": {
    "arifos-aaa": {
      "name": "AAA MCP",
      "url": "https://aaamcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Step 3: Verify Connection

```bash
# Check if MCP is connected
codex mcp list

# Expected output:
# ✅ arifos-aaa - https://aaamcp.arif-fazil.com/mcp
```

### Step 4: Use with Codex

```bash
# Start Codex with MCP tools
codex --mcp arifos-aaa

# Or set as default
codex config set mcp.default arifos-aaa
```

---

## Available Tools in Codex

Once connected, you can use these 7-Core tools:

| Tool | Command Example | Purpose |
|------|-----------------|---------|
| `_init_` | `/mcp arifos-aaa _init_` | Start constitutional session |
| `_agi_` | `/mcp arifos-aaa _agi_` | Deep reasoning on code |
| `_asi_` | `/mcp arifos-aaa _asi_` | Safety audit of changes |
| `_apex_` | `/mcp arifos-aaa _apex_` | Get judicial verdict |
| `_vault_` | `/mcp arifos-aaa _vault_` | Seal decision to ledger |
| `_trinity_` | `/mcp arifos-aaa _trinity_` | Full governance cycle |
| `_reality_` | `/mcp arifos-aaa _reality_` | Fact-check external sources |

---

## Example Workflows

### Workflow 1: Safe Code Review

```bash
# 1. Initialize session
/mcp arifos-aaa _init_ action=init query="Code review session"

# 2. Analyze with AGI (Mind)
/mcp arifos-aaa _agi_ action=reason query="Review this function for bugs"

# 3. Safety audit with ASI (Heart)
/mcp arifos-aaa _asi_ action=audit query="Check for security vulnerabilities"

# 4. Get verdict with APEX (Soul)
/mcp arifos-aaa _apex_ action=judge query="Final verdict on this code"

# 5. Seal to VAULT
/mcp arifos-aaa _vault_ action=seal verdict=SEAL
```

### Workflow 2: Quick Trinity Loop

```bash
# Full constitutional cycle in one call
/mcp arifos-aaa _trinity_ query="Refactor this authentication module"
```

---

## Constitutional Guarantees

Every interaction through Codex now has:

- ✅ **F2 Truth**: AI admits uncertainty (can't fake 100% confidence)
- ✅ **F5 Peace**: Serves weakest stakeholder (not just powerful)
- ✅ **F7 Humility**: Explicit uncertainty quantification
- ✅ **F9 Anti-Hantu**: Blocks fake emotions/consciousness claims
- ✅ **F10 Ontology**: Stays within reality boundaries
- ✅ **F1 Amanah**: Immutable audit trail in VAULT-999

---

## Troubleshooting

### Connection Failed

```bash
# Test endpoint manually
curl https://aaamcp.arif-fazil.com/health

# Should return:
# {"status": "healthy", "tools": 7, "architecture": "AAA-7CORE-v53.2.7"}
```

### Tool Not Found

```bash
# List available tools
codex mcp tools arifos-aaa
```

### Reset Connection

```bash
# Remove and re-add
codex mcp remove arifos-aaa
codex mcp add arifos-aaa https://aaamcp.arif-fazil.com/mcp
```

---

## Verdict Reference

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | All floors passed | Proceed with confidence |
| **SABAR** | Soft failure | Proceed with caution |
| **VOID** | Hard failure | Blocked - don't proceed |
| **PARTIAL** | Partial compliance | Proceed with caveats |
| **888_HOLD** | Emergency pause | Requires human review |

---

## Links

- **Dashboard**: https://arif-fazil.com/dashboard
- **Health**: https://aaamcp.arif-fazil.com/health
- **GitHub**: https://github.com/ariffazil/arifOS
- **MCP Endpoint**: https://aaamcp.arif-fazil.com/mcp

**DITEMPA BUKAN DIBERI** — Your code is now constitutionally governed.
