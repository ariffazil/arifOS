# TAILSCALE.md — Remote Windows PC Installation via Tailscale SSH

## Connection Details

| Node | Tailscale IP | Role |
|:---|:---|:---|
| VPS (arifOS) | 100.111.84.52 | Where I am now |
| Windows PC (ARIFFAZIL) | 100.109.203.23 | Target for installation |

## Connection Method

SSH from VPS → Windows PC via Tailscale:
```bash
ssh ariffazil@100.109.203.23
```

## Installation Steps

Once connected, install these tools via PowerShell:

### 1. 1Password CLI
```powershell
winget install AgileBits.1Password.CLI --accept-source-agreements --accept-package-agreements
```

### 2. GitHub CLI (gh)
```powershell
winget install GitHub.cli --accept-source-agreements --accept-package-agreements
```

### 3. Refresh Environment
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### 4. Verify Installation
```powershell
op --version
gh --version
```

### 5. Authenticate (Manual - requires browser)
```powershell
# 1Password (you'll need to sign in)
op account add --address my.1password.com --email your@email.com

# GitHub (opens browser)
gh auth login
```

---

## Pre-flight Check

Before SSH, verify Windows PC is accessible:
```bash
tailscale ping 100.109.203.23
```
