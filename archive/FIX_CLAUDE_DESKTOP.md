# ⚡ FIX CLAUDE DESKTOP - 2 Steps Only!

**Problem:** Claude Desktop can't find your MCP server because the path is wrong.

**Solution:** Copy 2 commands. Done in 10 seconds.

---

## ❌ IGNORE This Dialog!

The "Add custom connector" dialog you saw is for **REMOTE servers** (cloud services with URLs).

arifOS is a **LOCAL server** (runs on your computer, no URL needed).

**Don't use that dialog!** Close it.

---

## ✅ The REAL Fix (2 Commands)

### Step 1: Open PowerShell

1. Press `Windows Key`
2. Type: `powershell`
3. Press `Enter`

---

### Step 2: Copy & Paste These 2 Lines

**Click the copy button**, then **right-click in PowerShell** to paste:

```powershell
Copy-Item "C:\Users\User\OneDrive\Documents\GitHub\arifOS\CLAUDE_DESKTOP_CONFIG_WORKING.json" "$env:APPDATA\Claude\claude_desktop_config.json" -Force
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
```

Press `Enter`.

---

## ✅ What You Should See

You should see this appear in PowerShell:

```json
{
  "mcpServers": {
    "arifos-mcp": {
      "command": "C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python314\\python.exe",
      "args": [
        "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS\\scripts\\arifos_mcp_entry.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Look for:** `scripts\\arifos_mcp_entry.py` ✅ (this is CORRECT)

**If you see:** Just `arifos_mcp_entry.py` ❌ (this is WRONG - it's still broken)

---

## Step 3: Restart Claude Desktop

1. **Close Claude Desktop completely**
   - Right-click the Claude icon in your system tray (bottom-right)
   - Click "Quit"

2. **Wait 5 seconds**

3. **Open Claude Desktop again**
   - Press `Windows Key`
   - Type: `claude`
   - Press `Enter`

---

## ✅ How to Check It Worked

**In Claude Desktop**, type this message to Claude:

```
What MCP tools do you have available?
```

**If it worked**, Claude will say something like:
- "I have access to arifOS MCP tools..."
- Or list 17 tools

**If it's still broken**, Claude will say:
- "I don't have any MCP tools" or similar

---

## 🆘 If It's STILL Broken

**Run this command** in PowerShell to see what Claude is actually reading:

```powershell
Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
```

**Take a screenshot** of the output and show me.

---

## 📍 Where Is the Config File?

The file Claude Desktop reads is here:
```
C:\Users\User\AppData\Roaming\Claude\claude_desktop_config.json
```

You can open this location in File Explorer:
1. Press `Windows Key + R`
2. Type: `%APPDATA%\Claude`
3. Press `Enter`
4. You'll see `claude_desktop_config.json`

---

## 🎯 Quick Reference

| Question | Answer |
|----------|--------|
| **Where do I configure MCP?** | Config file at `%APPDATA%\Claude\claude_desktop_config.json` |
| **Can I use the "Add connector" UI?** | ❌ NO - That's for remote servers only |
| **What transport does arifOS use?** | stdio (local process, not HTTP) |
| **Do I need a URL?** | ❌ NO - Local servers don't have URLs |
| **Do I need OAuth credentials?** | ❌ NO - Local servers don't need auth |

---

## 📊 Comparison: Local vs Remote MCP

### Local MCP (arifOS) ✅ What You Have
- **Transport:** stdio
- **Configuration:** Config file only
- **Runs:** On your computer
- **Needs:** File path to Python script
- **Auth:** None needed

### Remote MCP (Cloud Services) ❌ Not What You Have
- **Transport:** SSE or HTTPS
- **Configuration:** "Add custom connector" UI dialog
- **Runs:** On remote server
- **Needs:** URL like `https://example.com`
- **Auth:** OAuth credentials

**You have LOCAL MCP!** Don't use the remote UI dialog.

---

## 🔄 Why Did This Happen?

Your Claude Desktop config had this **WRONG path**:
```
"C:\\...\\arifOS\\arifos_mcp_entry.py"
```

It should be this **CORRECT path**:
```
"C:\\...\\arifOS\\scripts\\arifos_mcp_entry.py"
```

**Missing:** The `scripts\\` folder!

The file `arifos_mcp_entry.py` is **inside** the `scripts\\` folder, not in the root folder.

---

## ✅ That's It!

**Total steps:**
1. Copy/paste 2 lines in PowerShell
2. Restart Claude Desktop
3. Test by asking Claude about MCP tools

**Total time:** ~30 seconds

---

**If this works**, you'll see the MCP tools in Claude Desktop and we can move on to the auto-start setup!

**If this doesn't work**, run that verification command and show me the output.
