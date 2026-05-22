# 🚀 MIGRATION RUNBOOK: Windows PowerShell → WSL2 Ubuntu (arifOS Federation)

> **Context:** You currently run arifOS Federation development on Windows PowerShell.
> Your stack is 100% Linux-native (Docker, bash, Makefile, Python uv, Node.js).
> This runbook migrates your entire dev environment to WSL2 Ubuntu so your AI agent
> speaks native bash instead of translating through PowerShell.
>
> **Target:** WSL2 Ubuntu 22.04/24.04 with all configs, API keys, tools, and repos
> mirrored from Windows. The VPS deployment at `/root` should be reproducible locally.

---

## 📋 PHASE 1: WSL2 Foundation

### 1.1 Install / Verify WSL2

Run in **Windows PowerShell (as Administrator):**

```powershell
# Fresh install
wsl --install -d Ubuntu

# Or if already installed — force WSL2
wsl --set-default-version 2
wsl --update
```

### 1.2 Create WSL user (match Windows username)

```bash
# Inside Ubuntu:
sudo usermod -l "$(cmd.exe /c 'echo %USERNAME%' | tr -d '\r')" "$(whoami)"
```

### 1.3 Windows-side prep — Export configs & secrets

Run these in **Windows PowerShell first**. All outputs land in `C:\Users\<You>\wsl-migrate\`.

```powershell
$MIGRATE = "C:\Users\$env:USERNAME\wsl-migrate"
New-Item -ItemType Directory -Force -Path "$MIGRATE\ssh"
New-Item -ItemType Directory -Force -Path "$MIGRATE\dotenvs"

# SSH keys
Copy-Item "$env:USERPROFILE\.ssh\*" "$MIGRATE\ssh\" -Recurse -Force -ErrorAction SilentlyContinue

# Git config
Copy-Item "$env:USERPROFILE\.gitconfig" "$MIGRATE\gitconfig" -Force -ErrorAction SilentlyContinue

# PowerShell profile (for reference)
Copy-Item $PROFILE "$MIGRATE\Microsoft.PowerShell_profile.ps1" -Force -ErrorAction SilentlyContinue

# Environment variables (filter for API keys)
Get-ChildItem Env: | Where-Object {
    $_.Name -match "API|KEY|TOKEN|SECRET|PASSWORD|ARIFOS|LANGFUSE|POSTGRES|REDIS|QDRANT"
} | Format-Table -AutoSize | Out-File "$MIGRATE\env-api-keys.txt"

# Docker & npm configs
Copy-Item "$env:USERPROFILE\.docker\config.json" "$MIGRATE\docker-config.json" -Force -ErrorAction SilentlyContinue
Copy-Item "$env:USERPROFILE\.npmrc" "$MIGRATE\npmrc" -Force -ErrorAction SilentlyContinue

# Cloud credentials
@("aws", "gcloud", "azure") | ForEach-Object {
    if (Test-Path "$env:USERPROFILE\.$_") {
        Copy-Item "$env:USERPROFILE\.$_\" "$MIGRATE\$_\" -Recurse -Force
    }
}

# arifOS-specific secrets & registry
$arifPaths = @(
    "C:\Users\$env:USERNAME\arifOS\.env",
    "C:\Users\$env:USERNAME\arifOS\**\.env.local",
    "C:\Users\$env:USERNAME\.arifos\**",
    "C:\Users\$env:USERNAME\.config\arifos\**"
)
Get-ChildItem -Path "C:\Users\$env:USERNAME" -Recurse -Include ".env",".env.local","secrets.json","vault.env" `
    -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Replace("C:\Users\$env:USERNAME\", "").Replace("\", "-")
        Copy-Item $_.FullName "$MIGRATE\dotenvs\$rel" -Force
    }

# Registry files (arifOS-specific)
if (Test-Path "C:\Users\$env:USERNAME\arifOS\registry") {
    Copy-Item "C:\Users\$env:USERNAME\arifOS\registry\*" "$MIGRATE\registry\" -Recurse -Force
}

Write-Host "`n✅ Staged to $MIGRATE" -ForegroundColor Green
```

> ⚠️ **ACTION REQUIRED:** Open `$MIGRATE\env-api-keys.txt` and keep it handy for Phase 4.

---

## 📋 PHASE 2: WSL2 Ubuntu Setup

### 2.1 Update & install base tools

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    git curl wget make build-essential \
    ca-certificates gnupg lsb-release \
    software-properties-common apt-transport-https \
    jq tree htop ncdu unzip zip \
    bash-completion
```

### 2.2 Install Docker

```bash
# Docker Engine (matches VPS setup)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"

# Verify (re-log or newgrp required)
docker ps
```

> 💡 **Tip:** If using Docker Desktop, ensure *"Use the WSL 2 based engine"* is checked in Settings → General.

### 2.3 Install Python 3.12 + `uv`

```bash
# Python 3.12 (arifOS target)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# uv — fast Python package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
uv --version
python3.12 --version
```

### 2.4 Install Node.js 22

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

node --version   # expect v22.x
npm --version    # expect 10.x
```

### 2.5 Global npm packages

```bash
npm install -g npm@latest
```
