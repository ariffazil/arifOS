# HOW - Start and Use arifOS (3-Command Constitutional Setup)

**Constitutional Quick Start** | **Version:** v47.0.0 | **Authority:** SEALED

---

## 🚀 HOW to Start arifOS (3 Commands Only)

### **Option 1: MCP for Claude Desktop (Most Common)**
```powershell
# Run as Administrator (required for auto-start)
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
.\scripts\auto_start_mcp.ps1 -Install
.\scripts\auto_start_mcp.ps1 -Start
```

**What happens:**
- ✅ MCP server starts immediately
- ✅ Auto-starts on boot (Task Scheduler)
- ✅ 17 constitutional tools ready for Claude Desktop
- ✅ Logs: `logs\mcp_autostart.log`

**Verify:**
```powershell
.\scripts\auto_start_mcp.ps1 -Status
# Should show: Status: RUNNING
```

---

### **Option 2: Docker REST API (Remote Access)**
```bash
# Start Docker containers
docker-compose up -d

# Verify they're running
docker-compose ps
```

**What happens:**
- ✅ arifOS REST API on http://localhost:8000/docs
- ✅ Qdrant vector database on http://localhost:6335
- ✅ Auto-restart on failure
- ✅ Logs: `docker-compose logs -f`

**Verify:**
```bash
curl http://localhost:8000/health
# Should show: {"status": "healthy"}
```

---

### **Option 3: Both (Complete Setup)**
```powershell
# MCP auto-start (run as Administrator)
.\scripts\auto_start_mcp.ps1 -Install
.\scripts\auto_start_mcp.ps1 -Start

# Docker containers
docker-compose up -d
```

**What happens:**
- ✅ Local MCP for Claude Desktop
- ✅ Remote REST API for other applications
- ✅ Complete constitutional governance stack

---

## 🎯 HOW to Choose What You Need

| What You Want | Use This | Commands Above |
|---------------|----------|----------------|
| **Use arifOS in Claude Desktop** | MCP Only | Option 1 |
| **Call arifOS from apps/scripts** | Docker Only | Option 2 |
| **Both local IDE + remote API** | Both | Option 3 |
| **Just testing quickly** | Quick Test | See below |

---

## ⚡ HOW to Quick Test (No Setup)

**For immediate testing without auto-start:**
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
python scripts\arifos_mcp_entry.py
```

**Test if it's working (new window):**
```powershell
python -c "from arifos_core.mcp import list_tools; print('Working! Tools:', len(list_tools()))"
# Should show: Working! Tools: 17
```

**Stop:** Press `Ctrl+C` in the first window.

---

## 🧪 HOW to Test Constitutional Functions

### **Test Constitutional Pipeline:**
```python
from arifos_core.system.apex_prime import judge_output

result = judge_output(
    query="What is photosynthesis?",
    response="Photosynthesis converts light energy to chemical energy.",
    lane="HARD",  # Strict factual
    user_id="test_user"
)

print(f"Verdict: {result.status}")
if result.status == "SEAL":
    print(f"Safe response: {result.output}")
else:
    print(f"Blocked: {result.reason}")
```

### **Test MCP Tools:**
```python
from arifos_core.mcp import list_tools
tools = list_tools()
print(f"Constitutional tools available: {len(tools)}")
for tool in tools[:3]:  # Show first 3
    print(f"- {tool['name']}: {tool['description'][:50]}...")
```

### **Test Constitutional Reflexes:**
```python
from arifos_core.trinity import AgentLoader, SessionManager

loader = AgentLoader()
config = loader.get_agent_config("validator")
print(f"Validator config: {config.llm.provider} - {config.llm.model}")
```

---

## 🔧 HOW to Use Constitutional Features

### **Constitutional Search (AGI + ASI):**
```python
from arifos_core.integration import agi_search, asi_search

# AGI search (knowledge acquisition)
agi_results = agi_search("What is constitutional entropy?")

# ASI search (claim validation)  
asi_results = asi_search("Verify that constitutional entropy reduces hallucinations")
```

### **Memory Governance (Vault-999):**
```python
from arifos_core.memory import vault999_query, vault999_store

# Store constitutional insight
vault999_store(
    insight="Constitutional reflexes work at 8.7ms",
    structure="thermodynamic_cooling",
    truth_boundary="reflex_speed < 10ms",
    scar="prevents conscious override"
)

# Query constitutional memory
results = vault999_query("constitutional reflex speed")
```

### **Trinity Orchestration:**
```python
from arifos_core.trinity import AgentSession, SessionManager

manager = SessionManager()
with AgentSession(manager, "engineer", "session_001") as session:
    # Constitutional separation enforced
    # Engineer cannot audit own work
    pass
```

---

## 📊 HOW to Monitor Constitutional Health

### **System Health:**
```powershell
# Constitutional metrics
curl http://localhost:8000/health

# MCP server status
.\scripts\auto_start_mcp.ps1 -Status

# Docker containers
docker-compose ps
```

### **Constitutional Metrics:**
```python
from arifos_core.enforcement.metrics import get_constitutional_metrics

metrics = get_constitutional_metrics()
print(f"Truth Score: {metrics.get('truth_score', 0):.3f}")
print(f"Empathy (κᵣ): {metrics.get('empathy_conductance', 0):.3f}")
print(f"Clarity (ΔS): {metrics.get('clarity_delta_s', 0):.3f}")
```

---

## 🛠️ HOW to Manage Your Setup

### **Start/Stop Services:**
```powershell
# MCP Management
.\scripts\auto_start_mcp.ps1 -Start      # Start now
.\scripts\auto_start_mcp.ps1 -Stop       # Stop
.\scripts\auto_start_mcp.ps1 -Status     # Check status
.\scripts\auto_start_mcp.ps1 -Uninstall  # Remove auto-start

# Docker Management
docker-compose start     # Start
docker-compose stop      # Stop
docker-compose restart   # Restart
docker-compose logs -f   # View logs
```

### **View Constitutional Logs:**
```powershell
# MCP constitutional logs
Get-Content logs\mcp_autostart.log -Tail 20

# Docker constitutional logs
docker-compose logs -f arifos-api

# All constitutional logs
Get-ChildItem logs\ | Where-Object {$_.Name -match "constitutional"}
```

---

## 🎯 HOW to Configure Claude Desktop

**After MCP is running, configure Claude Desktop:**

1. **Find config file:** `config\arifos-mcp-config.json`
2. **Copy path:** Full path to this JSON file
3. **Claude Desktop:** Settings → Developer → Edit Config
4. **Paste the JSON content** from the config file
5. **Restart Claude Desktop**
6. **Test:** Ask "What constitutional tools do you have?"

**Expected response:** Should list 17 constitutional tools

---

## 🆘 HOW to Troubleshoot

### **"MCP not running"**
```powershell
# Check what's wrong
.\scripts\auto_start_mcp.ps1 -Status
Get-Content logs\mcp_autostart.log -Tail 20

# Common fixes
# 1. Python path: Edit scripts\auto_start_mcp.ps1 line 9
# 2. Script path: Edit scripts\auto_start_mcp.ps1 line 10
# 3. Permissions: Run PowerShell as Administrator
```

### **"Docker containers not starting"**
```bash
# Check Docker Desktop is running
docker --version
docker ps

# Check logs
docker-compose logs -f

# Common fixes
# 1. Docker Desktop not running → Start from Start Menu
# 2. Port conflicts → Check what's using ports 8000/6333
# 3. Image issues → docker-compose pull
```

### **"Python not recognized"**
```powershell
# Install Python with PATH
# Download: https://www.python.org/downloads/
# IMPORTANT: Check "Add Python to PATH" during install
```

---

## 📋 HOW Summary (Quick Reference)

### **3-Command Constitutional Setup:**
```powershell
# 1. Navigate to arifOS
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS

# 2. Install auto-start (Administrator)
.\scripts\auto_start_mcp.ps1 -Install

# 3. Start services
.\scripts\auto_start_mcp.ps1 -Start
docker-compose up -d  # Optional: for REST API
```

### **Essential Commands:**
```powershell
# Status check
.\scripts\auto_start_mcp.ps1 -Status
docker-compose ps

# View logs
Get-Content logs\mcp_autostart.log -Tail 20
docker-compose logs -f

# Browser URLs
http://localhost:8000/docs   # API documentation
http://localhost:6335        # Qdrant dashboard
```

---

## 🏛️ HOW Constitutional Authority Works

**Every command executes through the 000→999 pipeline:**
```
Your Command → 000 VOID (validation) → 111 SENSE (context) → ... → 999 SEAL (audit trail)
```

**Constitutional Guarantees:**
- ✅ **F6 Clarity:** All commands documented and reversible
- ✅ **F2 Truth:** Status reports are accurate and complete  
- ✅ **F4 Empathy:** Error messages help, don't hinder
- ✅ **F8 Tri-Witness:** Multiple verification methods available

**Authority:** Muhammad Arif bin Fazil > arifOS Governor  
**Status:** SEALED under v47.0.0 constitutional governance  
**Entropy:** ΔS = -0.3 (simplified clarity achieved)

**DITEMPA BUKAN DIBERI** - Constitutional setup forged, not given. Truth must cool before it rules.