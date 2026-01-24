# Cursor IDE Integration

**AAA MCP for Cursor** - Constitutional AI governance via Model Context Protocol.

---

## Quick Install

### macOS / Linux

```bash
./scripts/install_cursor.sh
```

### Windows (PowerShell)

```powershell
# Run from arifOS directory
python scripts/install_cursor.py
```

### Windows (Git Bash / WSL)

```bash
./scripts/install_cursor.sh
```

---

## Manual Installation

### 1. Locate Config File

| Platform | Config Location |
|----------|-----------------|
| macOS | `~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json` |
| Linux | `~/.config/Cursor/User/globalStorage/cursor.mcp/mcp.json` |
| Windows | `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json` |

### 2. Add MCP Server

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python3",
      "args": ["-m", "AAA_MCP"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS"
      }
    }
  }
}
```

Replace `/path/to/arifOS` with your actual arifOS directory path.

### 3. Restart Cursor

Close and reopen Cursor to load the new MCP server.

---

## Available Tools

| Tool | Description | Key Floors |
|------|-------------|------------|
| `000_init` | Constitutional gateway - all requests start here | F1, F11, F12 |
| `agi_genius` | Truth & reasoning engine (AGI Mind) | F2, F4, F7 |
| `asi_act` | Safety & empathy engine (ASI Heart) | F3, F5, F6 |
| `apex_judge` | Final judgment & sealing (APEX Soul) | F1, F8, F9 |
| `999_vault` | Immutable audit trail | F1, F8 |

---

## Usage in Cursor

### Via Chat

Ask Cursor's AI:
> "Use the 000_init tool to validate the system"

### Via Command Palette

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Search "MCP: List Servers"
3. Verify "arifos-trinity" appears
4. Search "MCP: Call Tool"
5. Select tool and provide parameters

### Inline Tool Calls

In chat, use tool syntax:
```
@mcp arifos-trinity 000_init {"action": "validate"}
```

---

## Pipeline Example

For constitutional AI governance, use the full pipeline:

```
Step 1: Initialize session
@mcp arifos-trinity 000_init {"action": "init"}

Step 2: Analyze with truth engine
@mcp arifos-trinity agi_genius {"action": "sense", "query": "your question"}

Step 3: Check empathy/safety
@mcp arifos-trinity asi_act {"action": "empathize", "query": "your question"}

Step 4: Get final verdict
@mcp arifos-trinity apex_judge {"action": "judge"}

Step 5: Seal to ledger
@mcp arifos-trinity 999_vault {"action": "seal"}
```

---

## Troubleshooting

### Server Not Found

1. Check config file path for your OS
2. Verify JSON syntax is valid
3. Ensure `python3` is in PATH
4. Restart Cursor completely

### Check Installation

```bash
./scripts/install_cursor.sh --check
```

### Test Server Manually

```bash
cd /path/to/arifOS
PYTHONPATH="." python3 -m AAA_MCP
```

Should print banner and await MCP commands.

### View Cursor Logs

- macOS: `~/Library/Application Support/Cursor/logs/`
- Linux: `~/.config/Cursor/logs/`
- Windows: `%APPDATA%\Cursor\logs\`

---

## Verify MCP Connection

In Cursor:
1. Open a new chat
2. Type: "List available MCP tools"
3. Should see the 5 arifos-trinity tools

---

## Uninstall

```bash
./scripts/install_cursor.sh --uninstall
```

Or manually remove `arifos-trinity` from `mcp.json`.

---

## Integration Tips

### With Cursor Composer

The AAA MCP tools work well with Cursor Composer for multi-file edits:

1. Use `agi_genius` to analyze code before changes
2. Use `asi_act` to check impact on stakeholders
3. Use `apex_judge` to validate changes meet standards
4. Use `999_vault` to log the operation

### With Cursor Tab

For autocomplete context, AAA MCP provides constitutional guardrails on suggested completions when integrated with your prompts.

---

**F6 Empathy Floor:** This guide serves new users.
**DITEMPA BUKAN DIBERI**
