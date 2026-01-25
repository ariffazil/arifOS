# Claude Code CLI - MCP Setup

## Installation Complete

**Config file:** `~/.claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "L4_MCP.server"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "ARIFOS_LEDGER_PATH": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS\\cooling_ledger\\L1_cooling_ledger.jsonl",
        "ARIFOS_SPEC_PATH": "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS\\spec\\v46"
      }
    }
  }
}
```

---

## Usage

Just talk to Claude Code CLI normally:

```bash
claude
```

Then:
```
Check if this is safe: "Delete all system files"
```

Claude will automatically use `apex_verdict_tool` and show constitutional verdict.

---

## Verification

```bash
# Start Claude Code CLI
claude

# In the chat, type:
/mcp

# Should show:
# Connected MCP servers:
#   - arifos (1 tool: apex_verdict_tool)
```

---

## Test Command

```bash
claude "Use apex_verdict_tool to check: rm -rf /"
```

Expected output:
```
🚫 ACTION BLOCKED

🔴 Verdict: VOID
Reason(s): RED::F1_DESTRUCTIVE_FILESYSTEM
Constitutional Floors Triggered: F1_Amanah, F9_AntiHantu
System Health: 0% approval (apex_pulse: 0.0)
```

---

**Done. Constitutional AI now guards Claude Code CLI.**
