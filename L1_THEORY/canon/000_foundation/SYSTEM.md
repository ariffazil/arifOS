# arifOS System Operations Guide - v47.0

**Authority:** `AGENTS.md` Section 1.3: System Lifecycle
**Motto:** *DITEMPA BUKAN DIBERI* (Forged, Not Given)

---

## 🎯 The Unified Lifecycle

arifOS operations are organized into a **Trinity** of stages, orchestrated via the `/000` workflow and canonical scripts in `scripts/`.

### 1. [SETUP] Environment Forge
**Command:** `powershell .\scripts\setup_system.ps1`
**When:** First-time clone or after major environment changes.
**What:**
- Installs Python dependencies (`.venv`).
- Configures arifOS packages.
- Sets up Windows Task Scheduler for MCP auto-start.
- Verifies system integrity.

### 2. [BOOT] Warm Ignition
**Command:** `powershell .\scripts\boot_system.ps1`
**When:** At the start of every development session (via `/000`).
**What:**
- Checks Docker Desktop (activates if needed).
- Starts Docker dependencies (`docker-compose up -d`).
- Launches the MCP Server in a separate window.

### 3. [REBOOT] Cold Reset
**Command:** `powershell .\scripts\reboot_system.ps1`
**When:** System instability, session lock collision, or clearing stale memory.
**What:**
- Gracefully stops all Docker containers.
- Terminates running MCP servers.
- Cleans up stale session `.lock` files.
- Triggers a full `[BOOT]` for a clean state.

---

## 🛠️ Operational Reference

### Directory Map
- `scripts/`: Implementation scripts for lifecycle stages.
- `logs/`: Runtime logs for MCP, API, and setup.
- `.agent/workflows/000.md`: The workflow that orchestrates these scripts.

### Common Troubleshooting
- **Docker Unresponsive**: Run `[BOOT]` again; it will attempt to wake the daemon.
- **Session Locked**: Run `[REBOOT]` to sweep stale locks from crashed processes.
- **Dependency Errors**: Run `[SETUP]` to refresh the virtual environment and package links.

---

## 🎓 Constitutional Principles

| Stage | Floor | Implementation |
|-------|-------|----------------|
| **000 (Init)** | F1 (Amanah) | Identity & Time established first |
| **000 (Init)** | F2 (Truth) | Verification step clears environment drift |
| **999 (Seal)** | F6 (Amanah) | Graceful shutdown prevents information leak |

**Status:** ✅ Production Ready
**Compliance Canary:** `[v47.0 | 12F | LIFECYCLE UNIFIED]`

---

*For historical context or platform-specific guides, see `docs/archive/legacy_guides/`.*
