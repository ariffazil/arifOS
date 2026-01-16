# arifOS Auto-Start Guide - 000 Stage Ignition

**Version**: v46.3
**Purpose**: Auto-start MCP and Docker REST API on system boot
**Status**: Production Ready

---

## 🎯 Overview

This guide shows you how to make both **MCP (local)** and **Docker REST API (cloud)** auto-start with **000-stage initialization**.

**Two deployment modes**:
1. **MCP stdio** (Local IDE) → Auto-start on Windows/Linux/Mac
2. **Docker REST API** (Cloud) → Auto-restart with docker-compose

---

## 📊 Auto-Start Options

| Platform | MCP (stdio) | Docker (REST API) | Recommended |
|----------|-------------|-------------------|-------------|
| **Windows** | Task Scheduler | Docker Desktop | ✅ PowerShell script |
| **Linux** | systemd | Docker with systemd | ✅ systemd service |
| **macOS** | launchd | Docker Desktop | ✅ launchd plist |
| **Docker** | Container mode | docker-compose | ✅ docker-compose |

---

## 🪟 Windows Auto-Start

### Option 1: PowerShell Script (Recommended)

**Quick Setup**:
```powershell
# 1. Install auto-start (runs on boot)
.\scripts\auto_start_mcp.ps1 -Install

# 2. Verify installation
.\scripts\auto_start_mcp.ps1 -Status

# 3. Manual start (optional)
.\scripts\auto_start_mcp.ps1 -Start
```

**Management**:
```powershell
# Check status
.\scripts\auto_start_mcp.ps1 -Status

# Stop MCP
.\scripts\auto_start_mcp.ps1 -Stop

# Uninstall auto-start
.\scripts\auto_start_mcp.ps1 -Uninstall
```

**What it does**:
- ✅ Creates Windows Task Scheduler job
- ✅ Starts MCP on system boot (000 stage)
- ✅ Logs to `logs/mcp_autostart.log`
- ✅ Saves PID to `logs/mcp.pid`
- ✅ Graceful shutdown on stop (999 stage)

**Files**:
- Script: [`scripts/auto_start_mcp.ps1`](scripts/auto_start_mcp.ps1)
- Logs: `logs/mcp_autostart.log`
- Status: `logs/mcp.pid`

---

### Option 2: Windows Service (Advanced)

**Using NSSM (Non-Sucking Service Manager)**:

```powershell
# 1. Download NSSM
# https://nssm.cc/download

# 2. Install service
nssm install arifOS-MCP "C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe" `
    "c:\Users\User\OneDrive\Documents\GitHub\arifOS\scripts\arifos_mcp_entry.py"

# 3. Configure service
nssm set arifOS-MCP AppDirectory "c:\Users\User\OneDrive\Documents\GitHub\arifOS"
nssm set arifOS-MCP DisplayName "arifOS MCP Server"
nssm set arifOS-MCP Description "Constitutional Governance Pipeline (000→999)"
nssm set arifOS-MCP Start SERVICE_AUTO_START
nssm set arifOS-MCP AppStdout "c:\Users\User\OneDrive\Documents\GitHub\arifOS\logs\mcp_stdout.log"
nssm set arifOS-MCP AppStderr "c:\Users\User\OneDrive\Documents\GitHub\arifOS\logs\mcp_stderr.log"

# 4. Start service
nssm start arifOS-MCP

# 5. Check status
nssm status arifOS-MCP
```

**Management**:
```powershell
# Service control
sc query arifOS-MCP
sc stop arifOS-MCP
sc start arifOS-MCP

# Or use services.msc GUI
services.msc
```

---

## 🐧 Linux Auto-Start

### Option 1: Systemd Service (Recommended)

**Installation**:
```bash
# 1. Edit the service file
nano scripts/arifos-mcp.service

# Replace these placeholders:
# - YOUR_USERNAME → your Linux username
# - /path/to/arifOS → actual path to arifOS directory

# 2. Copy to systemd
sudo cp scripts/arifos-mcp.service /etc/systemd/system/

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable auto-start
sudo systemctl enable arifos-mcp

# 5. Start now
sudo systemctl start arifos-mcp

# 6. Check status
sudo systemctl status arifos-mcp
```

**Management**:
```bash
# View logs (real-time)
journalctl -u arifos-mcp -f

# View logs (recent)
journalctl -u arifos-mcp -n 50

# Restart service
sudo systemctl restart arifos-mcp

# Stop service
sudo systemctl stop arifos-mcp

# Disable auto-start
sudo systemctl disable arifos-mcp
```

**What it includes**:
- ✅ Auto-restart on failure (F6 Amanah)
- ✅ Resource limits (2GB RAM, 200% CPU)
- ✅ Security hardening (read-only filesystem)
- ✅ Graceful shutdown (999 stage)
- ✅ Journal logging

**Files**:
- Service: [`scripts/arifos-mcp.service`](scripts/arifos-mcp.service)
- Logs: `journalctl -u arifos-mcp`

---

### Option 2: Cron @reboot (Simple)

**Setup**:
```bash
# 1. Edit crontab
crontab -e

# 2. Add this line
@reboot cd /path/to/arifOS && python3 scripts/arifos_mcp_entry.py >> logs/mcp_cron.log 2>&1 &

# 3. Save and exit
```

**Limitations**:
- ⚠️ No automatic restart on failure
- ⚠️ No resource limits
- ⚠️ Basic logging only

---

## 🍎 macOS Auto-Start

### Option 1: launchd (Recommended)

**Create plist file**:
```bash
# 1. Create plist
nano ~/Library/LaunchAgents/com.arifos.mcp.plist
```

**Paste this** (adjust paths):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.arifos.mcp</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/arifOS/scripts/arifos_mcp_entry.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/path/to/arifOS</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/path/to/arifOS/logs/mcp_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/arifOS/logs/mcp_stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
        <key>ARIFOS_ENV</key>
        <string>production</string>
    </dict>

    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
```

**Enable and start**:
```bash
# Load the agent
launchctl load ~/Library/LaunchAgents/com.arifos.mcp.plist

# Check if running
launchctl list | grep arifos

# View logs
tail -f ~/path/to/arifOS/logs/mcp_stdout.log
```

**Management**:
```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.arifos.mcp.plist

# Start
launchctl load ~/Library/LaunchAgents/com.arifos.mcp.plist

# Restart
launchctl unload ~/Library/LaunchAgents/com.arifos.mcp.plist && \
launchctl load ~/Library/LaunchAgents/com.arifos.mcp.plist
```

---

## 🐳 Docker Auto-Start (All Platforms)

### Docker REST API Auto-Restart

**Already configured!** The `docker-compose.yml` has:
```yaml
services:
  arifos:
    restart: unless-stopped  # ✅ Auto-restart enabled
  qdrant:
    restart: unless-stopped  # ✅ Auto-restart enabled
```

**Start services**:
```bash
# Start in background (auto-restart enabled)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f arifos

# Services will auto-restart:
# - On container failure
# - On system reboot (if Docker starts automatically)
```

**Restart policies**:
- `unless-stopped`: Always restart, except when explicitly stopped
- `always`: Always restart (even after `docker stop`)
- `on-failure`: Only restart on failure (exit code != 0)

**Current config**: `unless-stopped` (best for production)

---

### Docker Desktop Auto-Start (Windows/Mac)

**Windows**:
1. Open Docker Desktop
2. Settings → General
3. ✅ Check "Start Docker Desktop when you log in"
4. Containers will auto-start if restart policy is set

**macOS**:
1. Open Docker Desktop
2. Preferences → General
3. ✅ Check "Start Docker Desktop when you log in"
4. Containers will auto-start if restart policy is set

---

### Docker with Systemd (Linux)

**Enable Docker to start on boot**:
```bash
# Enable Docker service
sudo systemctl enable docker

# Start Docker now
sudo systemctl start docker

# Check status
sudo systemctl status docker
```

**Then start containers**:
```bash
# Start containers (they'll auto-restart)
docker-compose up -d

# Verify restart policy
docker inspect arifos-api | grep -A 5 RestartPolicy
```

**Output should show**:
```json
"RestartPolicy": {
    "Name": "unless-stopped",
    "MaximumRetryCount": 0
},
```

---

## 🔄 Both MCP and Docker (Dual Auto-Start)

### Windows Example:
```powershell
# 1. Install MCP auto-start
.\scripts\auto_start_mcp.ps1 -Install

# 2. Enable Docker Desktop auto-start
# Docker Desktop → Settings → General → ✅ Start on login

# 3. Start Docker containers
docker-compose up -d

# 4. Verify both running
.\scripts\auto_start_mcp.ps1 -Status
docker-compose ps
```

### Linux Example:
```bash
# 1. Install MCP systemd service
sudo cp scripts/arifos-mcp.service /etc/systemd/system/
# (Edit file first to set paths)
sudo systemctl enable arifos-mcp
sudo systemctl start arifos-mcp

# 2. Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# 3. Start Docker containers
docker-compose up -d

# 4. Verify both running
sudo systemctl status arifos-mcp
docker-compose ps
```

---

## 🧪 Testing Auto-Start

### Test MCP Auto-Start:

**Windows**:
```powershell
# 1. Install
.\scripts\auto_start_mcp.ps1 -Install

# 2. Reboot system
Restart-Computer

# 3. After reboot, check status
.\scripts\auto_start_mcp.ps1 -Status

# Expected output:
# Status: RUNNING
# PID: <process_id>
```

**Linux**:
```bash
# 1. Install
sudo systemctl enable arifos-mcp
sudo systemctl start arifos-mcp

# 2. Reboot
sudo reboot

# 3. After reboot, check
sudo systemctl status arifos-mcp

# Expected: active (running)
```

---

### Test Docker Auto-Restart:

```bash
# 1. Start containers
docker-compose up -d

# 2. Kill container (simulate crash)
docker kill arifos-api

# 3. Wait 10 seconds

# 4. Check if restarted
docker-compose ps

# Expected: arifos-api shows "Up X seconds" (auto-restarted)

# 5. Reboot system (test boot persistence)
# After reboot:
docker-compose ps
# Expected: Containers running (if Docker auto-starts)
```

---

## 📊 Status Monitoring

### Check All Services:

**Windows**:
```powershell
# MCP status
.\scripts\auto_start_mcp.ps1 -Status

# Docker status
docker-compose ps

# Full health check
docker-compose ps && .\scripts\auto_start_mcp.ps1 -Status
```

**Linux**:
```bash
# MCP status
sudo systemctl status arifos-mcp

# Docker status
docker-compose ps

# Full health check
sudo systemctl status arifos-mcp && docker-compose ps
```

---

## 🎯 Quick Start Checklist

### For Local IDE (MCP):
- [ ] Install auto-start script/service
- [ ] Test with reboot
- [ ] Verify logs location
- [ ] Configure Claude Desktop to use MCP

### For Cloud Deployment (Docker):
- [ ] Enable Docker auto-start
- [ ] Run `docker-compose up -d`
- [ ] Verify restart policy (`unless-stopped`)
- [ ] Test with `docker kill` and reboot
- [ ] Check health endpoints

---

## 📁 Files Reference

| File | Purpose | Platform |
|------|---------|----------|
| [`scripts/auto_start_mcp.ps1`](scripts/auto_start_mcp.ps1) | PowerShell auto-start | Windows |
| [`scripts/arifos-mcp.service`](scripts/arifos-mcp.service) | Systemd service | Linux |
| [`docker-compose.yml`](docker-compose.yml) | Docker auto-restart | All |
| `logs/mcp_autostart.log` | MCP auto-start logs | Windows |
| `logs/mcp.pid` | MCP process ID | Windows |

---

## 🛠️ Troubleshooting

### MCP Not Starting:

**Windows**:
```powershell
# Check logs
Get-Content logs\mcp_autostart.log -Tail 50

# Check Task Scheduler
Get-ScheduledTask -TaskName "arifOS-MCP-AutoStart"

# Test manual start
python scripts\arifos_mcp_entry.py
```

**Linux**:
```bash
# Check logs
journalctl -u arifos-mcp -n 50

# Check service status
sudo systemctl status arifos-mcp

# Test manual start
python3 scripts/arifos_mcp_entry.py
```

---

### Docker Not Auto-Restarting:

```bash
# Check restart policy
docker inspect arifos-api | grep -A 5 RestartPolicy

# If policy is wrong, update docker-compose.yml:
# restart: unless-stopped

# Then recreate container:
docker-compose up -d --force-recreate

# Verify policy again
docker inspect arifos-api | grep -A 5 RestartPolicy
```

---

### Logs Not Appearing:

**Create log directory**:
```bash
# Linux/Mac
mkdir -p logs
chmod 755 logs

# Windows
New-Item -ItemType Directory -Force -Path logs
```

---

## 🎓 Constitutional Validation

| Floor | Auto-Start Feature | Status |
|-------|-------------------|--------|
| **F1 (Amanah)** | All operations reversible (can uninstall) | ✅ |
| **F2 (Truth)** | Accurate logging of start/stop events | ✅ |
| **F5 (Peace²)** | Graceful shutdown (999 stage) | ✅ |
| **F6 (Amanah)** | Resource limits configured | ✅ |
| **F7 (Ω₀)** | Failure states logged, not hidden | ✅ |

**Verdict**: SEAL ✅

---

## 🎯 Next Steps

After setting up auto-start:

1. **Test MCP**: Add to Claude Desktop config
2. **Test Docker**: Visit `http://localhost:8000/docs`
3. **Monitor**: Check logs regularly
4. **Optimize**: Adjust resource limits if needed

---

**DITEMPA BUKAN DIBERI** - Forged, not given; auto-ignition through 000-stage initialization.

**Version**: v46.3
**Status**: Production Ready
**Floors**: F1, F2, F5, F6, F7 validated
**Verdict**: SEAL

🎯 **Both MCP and Docker now auto-start on system boot!** 🎯
