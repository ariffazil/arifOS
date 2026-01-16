# .env Loading Guide for arifOS

**Author:** Claude Code (Ω) - Engineer
**Date:** 2026-01-16
**Purpose:** Load .env variables into terminal and Antigravity

---

## 🚀 Quick Start

### **Option 1: Load into Current Terminal (Temporary)**

```powershell
# Navigate to project directory
cd C:\Users\User\OneDrive\Documents\GitHub\arifOS

# Load .env (quick version)
. .\load-env.ps1

# Verify
$env:GITHUB_TOKEN
```

**When to use:** Daily development, testing
**Duration:** Until you close terminal

---

### **Option 2: Load and Persist (Permanent)**

```powershell
# Navigate to project directory
cd C:\Users\User\OneDrive\Documents\GitHub\arifOS

# Load with persistence
.\scripts\load_env.ps1 -Persist

# Verify (will work even after restart)
$env:GITHUB_TOKEN
```

**When to use:** First-time setup, or when .env changes
**Duration:** Forever (until you manually remove)

---

### **Option 3: Auto-Load on Terminal Start**

Add this to your PowerShell profile:

```powershell
# Open profile
notepad $PROFILE

# Add this code:
function Load-ArifOSEnv {
    $arifosPath = "C:\Users\User\OneDrive\Documents\GitHub\arifOS"
    if (Test-Path "$arifosPath\.env") {
        Push-Location $arifosPath
        . .\load-env.ps1 -ErrorAction SilentlyContinue
        Pop-Location
    }
}

# Auto-load when starting terminal in arifOS directory
if ($PWD.Path -like "*arifOS*") {
    Load-ArifOSEnv
}
```

**When to use:** If you work on arifOS daily
**Duration:** Auto-loads every time

---

## 📋 Script Comparison

| Script | Path | Usage | Purpose |
|--------|------|-------|---------|
| **Quick Loader** | `load-env.ps1` | `. .\load-env.ps1` | Fast, minimal output |
| **Full Loader** | `scripts\load_env.ps1` | `.\scripts\load_env.ps1` | Detailed, with options |

---

## 🔧 Full Loader Options

```powershell
# Basic load (session only)
.\scripts\load_env.ps1

# Load and persist
.\scripts\load_env.ps1 -Persist

# Load and show what was loaded
.\scripts\load_env.ps1 -ShowVariables

# Load from different file
.\scripts\load_env.ps1 -Path "C:\other\path\.env"

# Combine options
.\scripts\load_env.ps1 -Persist -ShowVariables
```

---

## ✅ Verification Commands

**Check if variables are loaded:**

```powershell
# Check specific variable
$env:GITHUB_TOKEN
$env:ARIFOS_CONSTITUTIONAL_MODE

# List all env vars with "ARIFOS"
Get-ChildItem env: | Where-Object Name -like "*ARIFOS*"

# Check from Python
python -c "import os; print(os.getenv('GITHUB_TOKEN'))"
```

---

## 🔄 For Antigravity

**After loading .env:**

1. **Restart Antigravity** (to pick up environment variables)
2. **Verify MCP servers load:**
   - Open Antigravity
   - Check status bar for MCP indicators
   - Should show 5 servers connected
3. **Test GitHub MCP:**
   - Open Cascade
   - Try: "Use GitHub MCP to list my repositories"
   - Should work without authentication errors

---

## 🐛 Troubleshooting

### **Variables not loading?**

```powershell
# Check if .env exists
Test-Path .env

# Check .env content (first 5 lines, masked)
Get-Content .env -Head 5

# Try with administrator
# (Right-click PowerShell → Run as Administrator)
.\scripts\load_env.ps1 -Persist
```

### **Antigravity not seeing variables?**

```powershell
# 1. Load with -Persist flag
.\scripts\load_env.ps1 -Persist

# 2. Restart Antigravity completely
# Close all windows, then reopen

# 3. Check in Antigravity terminal
# Open Antigravity's integrated terminal
# Run: $env:GITHUB_TOKEN
```

### **Variables disappear after restart?**

You used session-only mode. Use `-Persist` flag:

```powershell
.\scripts\load_env.ps1 -Persist
```

---

## 🎯 Recommended Workflow

**For Daily Development:**
```powershell
# When you start working on arifOS:
cd arifOS
. .\load-env.ps1
# Work normally, variables available in this terminal
```

**For Antigravity Setup (One-time):**
```powershell
# Run once:
cd arifOS
.\scripts\load_env.ps1 -Persist
# Restart Antigravity
# Variables now available to all processes
```

---

## 🔐 Security Notes

- ✅ `.env` file is gitignored (safe from git)
- ✅ Scripts mask sensitive values when displaying
- ✅ Session-only mode doesn't persist secrets to registry
- ✅ Persist mode stores in User environment (not Machine)
- ⚠️ Persisted variables visible to all user processes

**Recommendation:** Use session-only for daily work, persist only when needed for tools like Antigravity.

---

## 📚 What Each Script Does

### **`load-env.ps1` (Quick Loader)**

**Lines:** ~20
**Speed:** ⚡ Fast
**Output:** Minimal

**Use when:**
- Quick terminal session
- Testing something fast
- Don't need detailed output

### **`scripts/load_env.ps1` (Full Loader)**

**Lines:** ~200
**Speed:** Normal
**Output:** Detailed, color-coded

**Features:**
- ✅ Shows success/skip/error for each variable
- ✅ Masks sensitive values when showing
- ✅ Summary statistics
- ✅ Optional persistence
- ✅ Multiple file support
- ✅ Constitutional colors (F4 ΔS - clarity)

**Use when:**
- First-time setup
- Debugging why variables aren't loading
- Want to see what's being loaded
- Need to persist for tools

---

**DITEMPA BUKAN DIBERI** - .env loading forged, not guessed!

**Version:** v1.0
**Status:** SEALED
**Floors:** F1 (Truth), F4 (Clarity), F6 (Amanah - reversible)
