# Cursor IDE Integration (v52)

**arifOS MCP for Cursor** - Constitutional AI governance via Model Context Protocol.

---

## Quick Install

### macOS / Linux

```bash
./scripts/install_cursor.sh
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
      "args": ["-m", "arifos.mcp", "trinity"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_MODE": "production"
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
| `init_000` | Constitutional gateway - all requests start here | F1, F11, F12 |
| `agi_genius` | Truth & reasoning engine (AGI Mind) | F2, F4, F7 |
| `asi_act` | Safety & empathy engine (ASI Heart) | F3, F5, F6 |
| `apex_judge` | Final judgment & sealing (APEX Soul) | F1, F8, F9 |
| `vault_999` | Immutable audit trail | F1, F8 |

---

## Usage in Cursor

### Via Chat

Ask Cursor's AI:
> "Use the init_000 tool to validate the system"

### Via Command Palette

1. Open Command Palette (`Cmd/Ctrl + Shift + P`)
2. Search "MCP: List Servers"
3. Verify "arifos-trinity" appears
4. Search "MCP: Call Tool"
5. Select tool and provide parameters

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
PYTHONPATH="." python3 -m arifos.mcp trinity
```

Should print banner and await MCP commands.

---

## Uninstall

```bash
./scripts/install_cursor.sh --uninstall
```

Or manually remove `arifos-trinity` from `mcp.json`.

---

**F6 Empathy Floor:** This guide serves new users.
**DITEMPA BUKAN DIBERI**
