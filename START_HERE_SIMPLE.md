# START HERE - The Easiest Way (Just Copy/Paste!)

**No buttons to click. Just copy these commands and paste them in PowerShell.**

---

## 🎯 What Do You Want?

### Option A: "I just want to test it NOW" (Fastest)
→ Go to **[Quick Test](#quick-test-2-commands)** below

### Option B: "I want it to auto-start when I turn on my computer"
→ Go to **[Auto-Start Setup](#auto-start-setup-1-command)** below

### Option C: "I don't know, just tell me what to do!"
→ Start with **Option A**, then do **Option B** if you like it

---

## 🚀 Quick Test (2 Commands)

**Goal**: Start MCP server and see it working (does NOT auto-start on boot)

### Step 1: Open PowerShell

**How to open PowerShell**:
1. Press `Windows Key` + `R`
2. Type: `powershell`
3. Press `Enter`

You'll see a blue window (or black if you have Windows Terminal)

---

### Step 2: Go to arifOS folder

**Copy and paste this** (press `Enter` after pasting):
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
```

**What you should see**:
```
PS C:\Users\User\OneDrive\Documents\GitHub\arifOS>
```

If you see that, you're in the right place! ✅

---

### Step 3: Start MCP server

**Copy and paste this**:
```powershell
python scripts\arifos_mcp_entry.py
```

**What you should see** (this means it's working!):
```
[arifOS MCP] Initializing constitutional governance pipeline...
[arifOS MCP] 17 tools ready: Unified architecture with dual search
[arifOS MCP] - 5 constitutional pipeline + 2 search + 3 vault999 + 4 FAG + 1 validation + 2 system
[arifOS MCP] All tools enforce the 12 Constitutional Floors (F1-F12)
[arifOS MCP] DITEMPA BUKAN DIBERI - The server is forged.
```

**Then it will wait** (blank screen, cursor blinking) - **THIS IS GOOD!** ✅

The server is running and waiting for connections.

---

### Step 4: Test if it's working

**Open a NEW PowerShell window** (keep the first one open!):
1. Press `Windows Key` + `R`
2. Type: `powershell`
3. Press `Enter`

**In the NEW window, copy and paste this**:
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
python -c "from arifos_core.mcp import list_tools; print('MCP Server works! Tools:', len(list_tools()))"
```

**What you should see**:
```
MCP Server works! Tools: 17
```

**If you see that**: ✅ SUCCESS! MCP is running!

---

### Step 5: Stop the server (when you're done testing)

**Go back to the FIRST PowerShell window** (the one running the server)

Press: `Ctrl + C`

**You should see**:
```
[arifOS MCP] Received shutdown signal. Closing session...
[arifOS MCP] Session sealed. All audit trails preserved.
```

Server is now stopped.

---

## 🔄 Auto-Start Setup (1 Command)

**Goal**: Make MCP start automatically when you turn on your computer

### Step 1: Open PowerShell AS ADMINISTRATOR

**IMPORTANT**: You MUST run as Administrator!

**How**:
1. Press `Windows Key`
2. Type: `powershell`
3. **RIGHT-CLICK** on "Windows PowerShell"
4. Click "**Run as administrator**"
5. Click "Yes" if it asks permission

You'll see a PowerShell window. Check if it says "Administrator" in the title.

---

### Step 2: Go to arifOS folder

**Copy and paste this**:
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
```

---

### Step 3: Run the auto-start installer

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Install
```

**What you should see**:
```
[timestamp] [MCP-AUTO] === Installing MCP Auto-Start ===
[timestamp] [MCP-AUTO] Removing existing task...
[timestamp] [MCP-AUTO] ✅ Task Scheduler job created: arifOS-MCP-AutoStart
[timestamp] [MCP-AUTO] MCP will auto-start on next system boot
[timestamp] [MCP-AUTO] To test now, run: .\scripts\auto_start_mcp.ps1 -Start
```

**If you see "✅ Task Scheduler job created"**: SUCCESS! ✅

---

### Step 4: Start it NOW (without rebooting)

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Start
```

**What you should see**:
```
[timestamp] [MCP-AUTO] === 000 STAGE: MCP Auto-Ignition Starting ===
[timestamp] [MCP-AUTO] Starting MCP server...
[timestamp] [MCP-AUTO] Python: C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe
[timestamp] [MCP-AUTO] Entry: c:\Users\User\OneDrive\Documents\GitHub\arifOS\scripts\arifos_mcp_entry.py
[timestamp] [MCP-AUTO] ✅ MCP server started successfully (PID: 12345)
[timestamp] [MCP-AUTO] === 000 STAGE: MCP Auto-Ignition Complete ===
```

**If you see "✅ MCP server started successfully"**: SUCCESS! ✅

---

### Step 5: Check if it's running

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Status
```

**What you should see**:
```
[timestamp] [MCP-AUTO] === MCP Server Status ===
[timestamp] [MCP-AUTO] Status: RUNNING
[timestamp] [MCP-AUTO] PID: 12345
[timestamp] [MCP-AUTO] Started: 1/16/2026 3:45:12 PM
[timestamp] [MCP-AUTO] CPU: 0.5s
[timestamp] [MCP-AUTO] Memory: 45.23MB
[timestamp] [MCP-AUTO] Logs: c:\Users\User\OneDrive\Documents\GitHub\arifOS\logs
```

**If you see "Status: RUNNING"**: ✅ It's working!

---

### Step 6: Test auto-start (optional - requires reboot)

**Restart your computer**:
```powershell
Restart-Computer
```

**After your computer restarts**:
1. Open PowerShell (normal, not admin)
2. Copy and paste:
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
.\scripts\auto_start_mcp.ps1 -Status
```

**You should see "Status: RUNNING"** - MCP auto-started! ✅

---

## 🐳 Docker (Cloud API) - Optional

**Only do this if you want the REST API running** (for remote access, not needed for Claude Desktop)

### Step 1: Check if Docker is installed

**Copy and paste this in PowerShell**:
```powershell
docker --version
```

**If you see**: `Docker version 24.x.x` or similar → Docker is installed ✅

**If you see**: `docker : The term 'docker' is not recognized...` → Docker NOT installed ❌

**To install Docker**: Download from https://www.docker.com/products/docker-desktop

---

### Step 2: Start Docker containers

**Copy and paste this**:
```bash
docker-compose up -d
```

**What you should see** (first time will take 5-10 minutes to download):
```
[+] Running 2/2
 ✔ Container arifos-qdrant  Started
 ✔ Container arifos-api     Started
```

**If you see "Started"**: ✅ Docker is running!

---

### Step 3: Test Docker API

**Open your web browser** and go to:
```
http://localhost:8000/docs
```

**You should see**: A web page with "arifOS Constitutional API" and lots of API endpoints

**If you see that**: ✅ Docker REST API is working!

---

### Step 4: Stop Docker (when done)

**Copy and paste this**:
```bash
docker-compose down
```

Docker containers will stop.

---

## ❓ Which One Do I Need?

| What You Want | What to Use | Commands |
|---------------|-------------|----------|
| **Use arifOS in Claude Desktop** (local) | MCP only | Auto-Start Setup |
| **Call arifOS from other apps** (remote) | Docker only | Docker section |
| **Both** | Both MCP + Docker | Do both sections |
| **I'm just testing** | MCP Quick Test | Quick Test (2 commands) |

---

## 🆘 Troubleshooting

### "Python is not recognized..."

**Fix**: Install Python first
1. Go to: https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT**: Check "Add Python to PATH" during install
4. Try the commands again

---

### "Access denied" or "permission error"

**Fix**: Run PowerShell as Administrator
1. Close PowerShell
2. Press `Windows Key`
3. Type: `powershell`
4. **RIGHT-CLICK** → "Run as administrator"
5. Try again

---

### "Cannot find path..."

**Fix**: Make sure you're in the right folder
```powershell
# Copy and paste this:
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
pwd  # This shows where you are
```

You should see: `Path: C:\Users\User\OneDrive\Documents\GitHub\arifOS`

---

### "MCP server not running" after auto-start

**Fix**: Check the logs
```powershell
# Copy and paste this:
Get-Content logs\mcp_autostart.log -Tail 20
```

This shows the last 20 lines of the log. Look for errors.

**Common issues**:
- Python path wrong → Edit `scripts\auto_start_mcp.ps1` line 9
- Script path wrong → Edit `scripts\auto_start_mcp.ps1` line 10

---

### Docker containers not starting

**Fix 1**: Make sure Docker Desktop is running
- Look in your system tray (bottom-right corner)
- You should see a whale icon
- If not, open Docker Desktop from Start Menu

**Fix 2**: Check Docker status
```bash
docker ps
```

You should see running containers.

---

## 📝 Summary of All Commands

### Quick Test (MCP):
```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
python scripts\arifos_mcp_entry.py
# Press Ctrl+C to stop
```

### Auto-Start (MCP):
```powershell
# Run as Administrator
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
.\scripts\auto_start_mcp.ps1 -Install
.\scripts\auto_start_mcp.ps1 -Start
.\scripts\auto_start_mcp.ps1 -Status
```

### Docker (REST API):
```bash
docker-compose up -d           # Start
docker-compose ps              # Check status
docker-compose logs -f arifos  # View logs
docker-compose down            # Stop
```

### Check Everything:
```powershell
# MCP status
.\scripts\auto_start_mcp.ps1 -Status

# Docker status
docker-compose ps

# Open API docs in browser
start http://localhost:8000/docs
```

---

## 🎯 What To Do Right Now

**Copy and paste these 3 commands** (run as Administrator):

```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
.\scripts\auto_start_mcp.ps1 -Install
.\scripts\auto_start_mcp.ps1 -Start
```

**That's it!** MCP is now:
- ✅ Running right now
- ✅ Will auto-start on boot
- ✅ Ready for Claude Desktop

---

## 📁 Where Is Everything?

| What | Where |
|------|-------|
| **MCP server is running** | Background process (check with `-Status` command) |
| **MCP logs** | `c:\Users\User\OneDrive\Documents\GitHub\arifOS\logs\mcp_autostart.log` |
| **Docker containers** | Check with `docker ps` command |
| **Docker API** | Open browser: http://localhost:8000/docs |
| **All scripts** | `c:\Users\User\OneDrive\Documents\GitHub\arifOS\scripts\` |

---

**DITEMPA BUKAN DIBERI** - Just copy, paste, and it works!

**Next**: After MCP is running, configure Claude Desktop to use it (see config file in this folder)
