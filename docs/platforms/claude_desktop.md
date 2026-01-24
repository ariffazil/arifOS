# Claude Desktop Integration

**AAA MCP for Claude Desktop** - Constitutional AI governance via Model Context Protocol.

---

## Quick Install (Windows)

```batch
scripts\install_claude_desktop.bat
```

This automatically:
1. Detects your arifOS installation
2. Creates/updates Claude Desktop config
3. Verifies the installation

---

## Manual Installation

### 1. Locate Config File

```
%APPDATA%\Claude\claude_desktop_config.json
```

Typically: `C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json`

### 2. Add MCP Server

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arifos-trinity": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "C:\\path\\to\\arifOS",
      "env": {
        "PYTHONPATH": "C:\\path\\to\\arifOS"
      }
    }
  }
}
```

Replace `C:\\path\\to\\arifOS` with your actual arifOS directory path.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

---

## Available Tools

Once installed, you'll have access to 5 constitutional tools:

| Tool | Description | Key Floors |
|------|-------------|------------|
| `000_init` | Constitutional gateway - all requests start here | F1, F11, F12 |
| `agi_genius` | Truth & reasoning engine (AGI Mind) | F2, F4, F7 |
| `asi_act` | Safety & empathy engine (ASI Heart) | F3, F5, F6 |
| `apex_judge` | Final judgment & sealing (APEX Soul) | F1, F8, F9 |
| `999_vault` | Immutable audit trail | F1, F8 |

---

## Usage Examples

### Basic Initialization

Ask Claude:
> "Call 000_init with action=validate"

Response includes constitutional status and session ID.

### Full Pipeline

```
1. 000_init (action=init) → Get session_id
2. agi_genius (action=sense, query="your question") → Truth analysis
3. asi_act (action=empathize, query="your question") → Empathy check
4. apex_judge (action=judge, query="your question") → Final verdict
5. 999_vault (action=seal) → Immutable record
```

### Quick Analysis

> "Use agi_genius to analyze: Is quantum computing a threat to encryption?"

Claude will call the tool and return a truth-scored analysis.

---

## Troubleshooting

### Server Not Appearing

1. Check config file exists at correct location
2. Verify JSON is valid (use JSONLint)
3. Ensure Python is in PATH
4. Restart Claude Desktop

### Import Errors

```batch
cd C:\path\to\arifOS
pip install -e .
```

### Check Installation

```batch
scripts\install_claude_desktop.bat --check
```

### View Server Logs

Claude Desktop logs are at:
```
%APPDATA%\Claude\logs\
```

---

## Verify Installation

```batch
REM Check config
type "%APPDATA%\Claude\claude_desktop_config.json"

REM Test server manually
cd C:\path\to\arifOS
python -m AAA_MCP
```

The server should print a banner and wait for MCP commands.

---

## Uninstall

```batch
scripts\install_claude_desktop.bat --uninstall
```

Or manually remove the `arifos-trinity` entry from `claude_desktop_config.json`.

---

## Security Notes

- AAA MCP enforces 13 constitutional floors on all operations
- Rate limiting (F11) prevents API abuse
- Injection defense (F12) blocks malicious inputs
- All operations are logged to the cooling ledger

---

**F6 Empathy Floor:** This guide serves new users.
**DITEMPA BUKAN DIBERI**
