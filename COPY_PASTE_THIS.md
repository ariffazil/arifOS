# ⚡ COPY/PASTE THIS - 3 Commands Only!

**Just follow these 3 steps. Don't read anything else.**

---

## Step 1: Open PowerShell AS ADMINISTRATOR

1. Press `Windows Key`
2. Type: `powershell`
3. **RIGHT-CLICK** on "Windows PowerShell"
4. Click "**Run as administrator**"
5. Click "Yes"

You'll see a blue/black window.

---

## Step 2: Copy and Paste These 3 Lines

**Click the copy button** on the right of this code block, then **right-click in PowerShell** to paste:

```powershell
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS
.\scripts\auto_start_mcp.ps1 -Install
.\scripts\auto_start_mcp.ps1 -Start
```

Press `Enter` after pasting.

---

## Step 3: Look for This Message

You should see:
```
✅ MCP server started successfully
```

**If you see that**: ✅ **DONE!** MCP is running and will auto-start on boot.

**If you see errors**: Go to [START_HERE_SIMPLE.md](START_HERE_SIMPLE.md) → Troubleshooting section

---

## ✅ How to Check It's Working

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Status
```

You should see: `Status: RUNNING`

---

## 🛑 How to Stop It

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Stop
```

---

## 🔄 How to Restart It

**Copy and paste this**:
```powershell
.\scripts\auto_start_mcp.ps1 -Stop
.\scripts\auto_start_mcp.ps1 -Start
```

---

## 📋 Cheat Sheet (Save This!)

```powershell
# Go to arifOS folder
cd c:\Users\User\OneDrive\Documents\GitHub\arifOS

# Check status
.\scripts\auto_start_mcp.ps1 -Status

# Start
.\scripts\auto_start_mcp.ps1 -Start

# Stop
.\scripts\auto_start_mcp.ps1 -Stop

# View logs
Get-Content logs\mcp_autostart.log -Tail 20

# Remove auto-start
.\scripts\auto_start_mcp.ps1 -Uninstall
```

---

## 🆘 If Something Goes Wrong

**Open this file**: [START_HERE_SIMPLE.md](START_HERE_SIMPLE.md)

Look at the "Troubleshooting" section.

Or run this to see what's happening:
```powershell
Get-Content logs\mcp_autostart.log
```

---

**That's it! You're done.**

After this, MCP will:
- ✅ Be running right now
- ✅ Auto-start every time you boot your computer
- ✅ Be ready for Claude Desktop to use

---

**Next step**: Configure Claude Desktop to use this MCP server
→ See your `config\arifos-mcp-config.json` file
