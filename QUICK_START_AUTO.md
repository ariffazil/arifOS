# Quick Start - Auto-Ignition (000 Stage)

**Goal**: Make MCP and Docker auto-start on boot in **3 commands**

---

## 🚀 One-Command Setup (Windows)

```powershell
# Run this as Administrator
.\scripts\setup_auto_start.ps1
```

**What it does**:
1. ✅ Installs MCP auto-start (Task Scheduler)
2. ✅ Starts Docker containers (auto-restart enabled)
3. ✅ Tests health endpoints
4. ✅ Creates logs directory

---

## 🎯 Manual Setup (3 Commands)

### Option 1: MCP Only (Local IDE)

```powershell
# Install auto-start
.\scripts\auto_start_mcp.ps1 -Install

# Check status
.\scripts\auto_start_mcp.ps1 -Status

# Reboot and verify
Restart-Computer
```

---

### Option 2: Docker Only (Cloud API)

```bash
# Start with auto-restart
docker-compose up -d

# Verify restart policy
docker inspect arifos-api | grep -A 5 RestartPolicy

# Test auto-restart
docker kill arifos-api && sleep 10 && docker-compose ps
```

---

### Option 3: Both (Complete Setup)

```powershell
# 1. MCP auto-start
.\scripts\auto_start_mcp.ps1 -Install

# 2. Docker auto-restart
docker-compose up -d

# 3. Verify both
.\scripts\auto_start_mcp.ps1 -Status
docker-compose ps
```

---

## ✅ Verification

### After Setup:
```powershell
# MCP status
.\scripts\auto_start_mcp.ps1 -Status
# Expected: Status: RUNNING

# Docker status
docker-compose ps
# Expected: arifos-api Up, qdrant Up

# Health checks
curl http://localhost:8000/health  # arifOS API
curl http://localhost:6333/health  # Qdrant
```

### After Reboot:
```powershell
# Same checks - should auto-start
.\scripts\auto_start_mcp.ps1 -Status
docker-compose ps
```

---

## 📊 What's Auto-Starting

| Service | Method | Status |
|---------|--------|--------|
| **MCP Server** | Windows Task Scheduler | ✅ Auto-start on boot |
| **Docker API** | docker-compose restart policy | ✅ Auto-restart on failure |
| **Qdrant** | docker-compose restart policy | ✅ Auto-restart on failure |

---

## 🛑 Management Commands

### MCP:
```powershell
.\scripts\auto_start_mcp.ps1 -Start      # Start now
.\scripts\auto_start_mcp.ps1 -Stop       # Stop
.\scripts\auto_start_mcp.ps1 -Status     # Check status
.\scripts\auto_start_mcp.ps1 -Uninstall  # Remove auto-start
```

### Docker:
```bash
docker-compose start     # Start
docker-compose stop      # Stop
docker-compose restart   # Restart
docker-compose logs -f   # View logs
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `scripts/auto_start_mcp.ps1` | MCP auto-start manager (Windows) |
| `scripts/arifos-mcp.service` | Systemd service (Linux) |
| `scripts/setup_auto_start.ps1` | Unified setup script |
| `logs/mcp_autostart.log` | MCP auto-start logs |
| `logs/mcp.pid` | MCP process ID |

---

## 🎓 Platform-Specific

### Linux:
```bash
# Install systemd service
sudo cp scripts/arifos-mcp.service /etc/systemd/system/
# (Edit file first to set paths)
sudo systemctl enable arifos-mcp
sudo systemctl start arifos-mcp

# Docker
docker-compose up -d
```

### macOS:
```bash
# Create launchd plist (see AUTO_START_GUIDE.md)
launchctl load ~/Library/LaunchAgents/com.arifos.mcp.plist

# Docker
docker-compose up -d
```

---

## 📚 Full Documentation

For detailed instructions, troubleshooting, and platform-specific guides:

→ **[AUTO_START_GUIDE.md](AUTO_START_GUIDE.md)** - Complete auto-start guide

---

**DITEMPA BUKAN DIBERI** - Ready for 000-stage auto-ignition.

**Status**: ✅ Production Ready
**Platforms**: Windows, Linux, macOS
**Verdict**: SEAL
