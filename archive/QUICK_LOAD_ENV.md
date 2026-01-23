# Quick .env Loading - 30 Second Guide

## 🚀 **FASTEST WAY (Daily Use)**

Open PowerShell in arifOS directory:

```powershell
. .\load-env.ps1
```

**That's it!** Variables loaded into current terminal.

---

## 🔒 **FOR ANTIGRAVITY (One-Time Setup)**

```powershell
.\scripts\load_env.ps1 -Persist
```

Then **restart Antigravity**.

---

## ✅ **TEST IF IT WORKED**

```powershell
# Should show your token
$env:GITHUB_TOKEN

# Should show AAA
$env:ARIFOS_CONSTITUTIONAL_MODE
```

---

## 📋 **QUICK REFERENCE**

| Command | Effect | Duration |
|---------|--------|----------|
| `. .\load-env.ps1` | Load to current terminal | Until you close terminal |
| `.\scripts\load_env.ps1 -Persist` | Save to Windows | Forever (survives restart) |
| `.\scripts\load_env.ps1 -ShowVariables` | Load + show what loaded | Current session + see output |

---

## 🔄 **WHEN TO USE WHICH**

**Use quick loader (`. .\load-env.ps1`):**
- Every time you open a new terminal
- For daily development
- Testing commands

**Use persist (`.\scripts\load_env.ps1 -Persist`):**
- First-time Antigravity setup
- After changing .env file
- Want variables available everywhere

---

## 🎯 **COMMON TASKS**

### Make Antigravity see GITHUB_TOKEN:
```powershell
.\scripts\load_env.ps1 -Persist
# Restart Antigravity
```

### Load vars for terminal session:
```powershell
. .\load-env.ps1
python script.py  # Can now see env vars
```

### Check what's in .env (safely):
```powershell
.\scripts\load_env.ps1 -ShowVariables
# Tokens are masked for security
```

---

**DITEMPA BUKAN DIBERI** - .env loading made simple! 🚀
