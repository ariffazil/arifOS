# WHERE - Everything Is Located (Visual Constitutional Map)

**Constitutional Navigation Guide** | **Version:** v47.0.0 | **Authority:** SEALED

---

## 🗺️ WHERE Constitutional Components Live

### **Root Directory Structure:**
```
arifOS/
├── 📋 Core Documentation (Immediate Access)
│   ├── WHAT.md                    ← This file: What arifOS does
│   ├── WHERE.md                   ← This file: Where everything is
│   ├── HOW.md                     ← How to start and use
│   ├── README.md                  ← Project overview
│   ├── AGENTS.md                  ← Constitutional governance
│   └── CHANGELOG.md               ← Version history
│
├── 🚀 Quick Start (3-Command Setup)
│   ├── START_HERE_SIMPLE.md       ← Copy/paste commands
│   ├── QUICK_START_DOCKER.md      ← Docker deployment
│   └── DOCUMENTATION_INDEX.md     ← Complete navigation hub
│
├── 🏛️ Constitutional Hierarchy
│   ├── L1_THEORY/canon/           ← Supreme constitutional law (L1)
│   ├── L2_PROTOCOLS/v47/          ← Operational specifications (L2)
│   └── arifos_core/               ← Implementation code (L3)
│
├── 📊 Analysis & Reports
│   ├── docs/analysis/             ← Constitutional analysis
│   ├── reports/                   ← Operational completion reports
│   └── docs/testing/              ← Testing documentation
│
└── ⚙️ Operational Components
    ├── scripts/                   ← Setup and management scripts
    ├── config/                    ← Configuration files
    ├── logs/                      ← All operational logs
    └── .venv/                     ← Virtual environment
```

---

## 🔍 WHERE Specific Components Are

### **Constitutional Pipeline (000→999):**
```
000 VOID:   arifos_core/system/stages/stage_000_void.py
111 SENSE:  arifos_core/agi/                              ← AGI Kernel (Δ)
222 REFLECT: arifos_core/agi/                              ← AGI Kernel (Δ)  
333 ATLAS:   arifos_core/agi/                              ← AGI Kernel (Δ)
444 ALIGN:  arifos_core/asi/                              ← ASI Kernel (Ω)
555 EMPATHIZE: arifos_core/asi/                           ← ASI Kernel (Ω)
666 BRIDGE: arifos_core/asi/                              ← ASI Kernel (Ω)
777 EUREKA: arifos_core/integration/                      ← Integration
888 JUDGE:  arifos_core/system/apex_prime.py              ← APEX Kernel (Ψ)
999 SEAL:   arifos_core/memory/                            ← Memory & Sealing
```

### **Constitutional Agents:**
```
Architect (Δ): .antigravity/ + identities/architect.md
Engineer (Ω):  .claude/ + identities/engineer.md  
Auditor (Ψ):   .codex/ + identities/auditor.md
Validator (Κ): .kimi/ + identities/validator.md
```

---

## 🖥️ WHERE Running Services Are Located

### **MCP Server (Constitutional Tools):**
```
Location: Background process (invisible)
Check Status: .\scripts\auto_start_mcp.ps1 -Status
Process: python.exe running arifos_mcp_entry.py
Auto-Start: Task Scheduler → arifOS-MCP-AutoStart
Logs: logs\mcp_autostart.log
Tools: 17 constitutional tools (pipeline + search + vault + validation)
Port: Uses stdio (not HTTP - can't see in browser)
```

### **Docker Containers (REST API):**
```
Location: Docker Desktop containers
Check Status: docker ps
Containers: 
  ├── arifos-api (Port 8000) → http://localhost:8000/docs
  └── arifos-qdrant (Port 6333) → http://localhost:6335
Auto-Restart: docker-compose restart policies
Logs: docker-compose logs -f
```

---

## 📁 WHERE Key Files Are

### **Setup & Management:**
```
Auto-Start Script: scripts\auto_start_mcp.ps1
MCP Entry Point:  scripts\arifos_mcp_entry.py  
Docker Config:    docker-compose.yml
Bootstrap:        setup\bootstrap\bootstrap.py
Config Files:     config\agents.yaml
```

### **Constitutional Documentation:**
```
L1 Canon:     L1_THEORY/canon/000_foundation/000_CONSTITUTIONAL_CORE_v47.md
L2 Protocols: L2_PROTOCOLS/v47/000_foundation/constitutional_floors.json
Agent Config: config/agents.yaml
Identity:     identities/[architect|engineer|auditor|validator].md
```

### **Analysis & Reports:**
```
Entropy Analysis: docs/analysis/CONSTITUTIONAL_ENTROPY_REPORT.md
Seal Verification: docs/analysis/CONSTITUTIONAL_SEAL_VERIFICATION_v47.md
Forging Reports: reports/MCP_CODEX_FORGING_COMPLETE.md
Test Plans: docs/testing/TEST_UNIFICATION_PLAN_v47.md
```

---

## 🔎 WHERE to Check If Things Are Running

### **Quick Status Check (Copy/Paste):**
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
Write-Host "=== MCP Status ===" -ForegroundColor Cyan
.\scripts\auto_start_mcp.ps1 -Status
Write-Host "=== Docker Status ===" -ForegroundColor Cyan  
docker ps
Write-Host "=== Browser URLs ===" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs"
Write-Host "Qdrant:   http://localhost:6335"
```

### **Individual Checks:**
```powershell
# MCP Status
.\scripts\auto_start_mcp.ps1 -Status

# Docker Containers  
docker ps

# Task Scheduler (Auto-Start)
Get-ScheduledTask -TaskName "*arifOS*"

# Process List (MCP)
Get-Process python | Where-Object {$_.CommandLine -match "arifos"}
```

---

## 🌐 WHERE to Access Services

### **Browser Access:**
```
arifOS REST API:    http://localhost:8000/docs
Qdrant Dashboard:   http://localhost:6335
Health Check:       http://localhost:8000/health
```

### **Command Line Access:**
```powershell
# MCP Tools (via Claude Desktop)
# Config: config\arifos-mcp-config.json

# Docker API (HTTP requests)
# Base: http://localhost:8000/arifos/govern

# Direct Python
python -c "from arifos_core.mcp import list_tools; print(len(list_tools()))"
```

---

## 📊 WHERE Logs Are Located

### **All Logs Directory:** `logs/`
```
MCP Auto-Start:     logs\mcp_autostart.log
MCP Standard Out:   logs\mcp_stdout.log  
MCP Standard Error: logs\mcp_stderr.log
Docker Compose:     logs\docker_compose.log
Constitutional:     logs\constitutional_audit.log
```

### **View Logs:**
```powershell
# Last 20 lines of MCP log
Get-Content logs\mcp_autostart.log -Tail 20

# Real-time Docker logs
docker-compose logs -f

# All log files
Get-ChildItem logs\
```

---

## 🛠️ WHERE to Find Help

### **Documentation:**
```
Complete Guide: DOCUMENTATION_INDEX.md
Setup Guide:    START_HERE_SIMPLE.md  
Docker Guide:   QUICK_START_DOCKER.md
System Guide:   SYSTEM.md
Agent Specs:    AGENTS.md
```

### **Constitutional Support:**
```
Entropy Analysis: docs/analysis/CONSTITUTIONAL_ENTROPY_REPORT.md
Seal Verification: docs/analysis/CONSTITUTIONAL_SEAL_VERIFICATION_v47.md
Test Analysis:    docs/testing/TEST_IMPORT_FAILURES_ANALYSIS.md
```

---

## 🎯 WHERE to Go Next

**Choose your constitutional path:**

1. **[HOW.md](HOW.md)** → How to start and use arifOS
2. **[WHAT.md](WHAT.md)** → What arifOS does constitutionally  
3. **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** → Complete navigation hub

**Constitutional Principle:** Everything has a place, every place serves the constitution.

**Authority:** Muhammad Arif bin Fazil > arifOS Governor  
**Status:** SEALED under v47.0.0 constitutional governance  
**Entropy:** ΔS = -0.2 (organized clarity achieved)