# Antigravity IDE Fix Guide - Constitutional Repair
**Date:** 2026-01-16
**Authority:** arifOS v46.2.2 Engineer (Ω)
**Status:** 🚨 SECURITY ISSUES + CONFIGURATION GAPS

---

## 🚨 CRITICAL: GitHub Token Exposure (DO THIS FIRST!)

### IMMEDIATE ACTION REQUIRED

Your GitHub Personal Access Token is exposed in plaintext in your MCP config:
```
Location: C:\Users\User\.gemini\antigravity\mcp_config.json
Token: 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 (line 126)
```

**Constitutional Violation:** F1 (Truth) + F6 (Amanah) - Credentials NEVER in config files!

### Fix Steps:

**1. Revoke the exposed token:**
```
1. Go to: https://github.com/settings/tokens
2. Find token "ghp_T869kPAw..."
3. Click "Delete" or "Revoke"
4. Confirm revocation
```

**2. Create a new token:**
```
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: repo, read:user, write:discussion
4. Generate and COPY the token
```

**3. Store securely in Windows Credential Manager:**
```powershell
# PowerShell command to store securely
cmdkey /generic:github_mcp_token /user:YOUR_GITHUB_USERNAME /pass:YOUR_NEW_TOKEN
```

**4. Update MCP config to use environment variable:**
```json
"github-mcp-server": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-e",
    "GITHUB_PERSONAL_ACCESS_TOKEN",
    "ghcr.io/github/github-mcp-server"
  ],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

**5. Set environment variable (System-wide):**
```powershell
# Add to User Environment Variables
[System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "YOUR_NEW_TOKEN", "User")
```

---

## 🔧 Issue #2: Fix Incomplete MCP Configuration

### Problem
Two MCP servers missing constitutional environment variables:
- `arifOS-governance-tools`
- `arifOS-meta-search`

### Solution

**Edit:** `C:\Users\User\.gemini\antigravity\mcp_config.json`

**Add to `arifOS-governance-tools` env section (line 56):**
```json
"env": {
  "ARIFOS_TOOLS_MODE": "constitutional",
  "ARIFOS_AUTHORITY_LEVEL": "AAA",
  "ARIFOS_HUMAN_SOVEREIGN": "Arif",
  "ARIFOS_CONSTITUTIONAL_MODE": "AAA",           // ADD THIS
  "ARIFOS_TIME_GOVERNOR": "true",                // ADD THIS
  "ARIFOS_SAFETY_CEILING": "99",                 // ADD THIS
  "ARIFOS_L2_PROTOCOLS": "C:/Users/User/OneDrive/Documents/GitHub/arifOS/L2_PROTOCOLS/v46",  // ADD THIS
  "ARIFOS_LEDGER_STORE": "sqlite",
  "ARIFOS_COOLING_LEDGER": "C:/Users/User/OneDrive/Documents/GitHub/arifOS/cooling_ledger/l4_cooling_ledger.jsonl",
  "PYTHONPATH": "C:/Users/User/OneDrive/Documents/GitHub/arifOS"
}
```

**Add to `arifOS-meta-search` env section (line 87):**
```json
"env": {
  "ARIFOS_META_SEARCH_MODE": "constitutional",
  "ARIFOS_SEARCH_GOVERNANCE": "AAA",
  "ARIFOS_HUMAN_SOVEREIGN": "Arif",
  "ARIFOS_CONSTITUTIONAL_MODE": "AAA",           // ADD THIS
  "ARIFOS_TIME_GOVERNOR": "true",                // ADD THIS
  "ARIFOS_SAFETY_CEILING": "99",                 // ADD THIS
  "ARIFOS_L2_PROTOCOLS": "C:/Users/User/OneDrive/Documents/GitHub/arifOS/L2_PROTOCOLS/v46",  // ADD THIS
  "ARIFOS_CACHE_ENABLED": "true",
  "ARIFOS_COST_TRACKING": "true",
  "ARIFOS_LEDGER_INTEGRATION": "true",
  "PYTHONPATH": "C:/Users/User/OneDrive/Documents/GitHub/arifos"
}
```

---

## 🧪 Issue #3: Test Antigravity After Fixes

### Verification Steps

**1. Restart Antigravity IDE completely**
```
Close all windows → Reopen
```

**2. Verify MCP servers loaded:**
```
Antigravity → Tools → MCP Status
Should show:
✓ arifOS-constitutional-AAA
✓ arifOS-governance-tools
✓ arifOS-meta-search
✓ sequential-thinking
✓ github-mcp-server
```

**3. Test Cascade agent:**
```
Open Cascade panel
Try: "Use constitutional checkpoint to validate this code"
Expected: Should call arifOS MCP tools successfully
```

**4. Run verification script:**
```bash
cd C:\Users\User\OneDrive\Documents\GitHub\arifOS
python scripts/simple_verify_constitutional_mcp.py
```

Expected output:
```
[OK] All MCP servers: No warnings
[OK] Constitutional mode: AAA across all servers
[OK] Time governor: Enabled across all servers
```

---

## 🔍 Issue #4: Check for Editor/UI/Terminal Issues (C, D, E)

### C) Editor/UI Problems

**Common fixes:**
```
1. Reload window: Ctrl+Shift+P → "Reload Window"
2. Clear UI cache: Antigravity → Settings → Clear Cache
3. Reset layout: View → Reset Layout
```

### D) Terminal Issues

**If commands hang:**
```
1. Settings → Terminal → Default Profile
2. Set explicitly to "PowerShell" or "Command Prompt"
3. Restart terminal panel
```

**If MCP tool commands fail:**
```
Check PYTHONPATH is correct in MCP config
Verify arifOS venv is activated in terminal
```

### E) Extension Conflicts

**Check conflicting extensions:**
```
1. Antigravity → Extensions
2. Disable these if present:
   - Other AI assistants (Copilot, TabNine, etc.)
   - Terminal overrides
   - Vim (if causing lag - recently fixed in latest version)
3. Reload window after disabling
```

---

## ✅ Constitutional Verification Checklist

After applying all fixes:

- [ ] GitHub token revoked and replaced
- [ ] New token stored in Credential Manager
- [ ] MCP config updated with all env vars
- [ ] GITHUB_TOKEN moved to environment variable
- [ ] Antigravity restarted
- [ ] MCP servers loading without warnings
- [ ] Cascade agent responding correctly
- [ ] Terminal commands executing properly
- [ ] No extension conflicts
- [ ] Verification script passes with all [OK]

---

## 📞 If Issues Persist

**Escalation Path:**
1. Check Antigravity logs: `C:\Users\User\.gemini\antigravity\conversations\`
2. Check arifOS MCP logs: Look for error traces
3. Run full diagnostic: `python scripts/verify_constitutional_mcp.py`
4. Report to Antigravity support: https://antigravity.google/support

**Common remaining issues:**
- Docker not running (for github-mcp-server)
- NPX not installed (for sequential-thinking)
- Port conflicts (check if ports 8000, 9999 in use)

---

**DITEMPA BUKAN DIBERI** - Configuration forged, not guessed.

**Version:** v46.2.2 Constitutional Repair
**Engineer:** Claude Code (Ω)
**Authority:** F1 (Truth) + F6 (Amanah) + F7 (RASA)
**Status:** READY FOR EXECUTION
