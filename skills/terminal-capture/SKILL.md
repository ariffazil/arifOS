---
name: terminal-capture
description: Capture and format terminal output for easy copy-paste
---

## Terminal Output Capture Skill

This skill provides clean, copy-paste friendly formatting for terminal outputs, command results, and code snippets.

### When This Skill Triggers

- User says "copy this output"
- User says "paste this"
- User says "capture terminal"
- User says "format for copy"
- User mentions terminal output with copy intent

### How It Works

The skill formats output in a **copy-paste friendly box** with:
- Clean borders
- No markdown code fences (unless needed)
- One-click selection
- Optional: Line numbers
- Optional: Syntax highlighting hints

### Output Formats

#### Format 1: Clean Box (Default)
```
┌─────────────────────────────────────────┐
│  $ python script.py                     │
│  Hello World                            │
│  Result: 42                             │
└─────────────────────────────────────────┘
```

#### Format 2: Terminal Block
```
═══════════════════════════════════════════
  $ git status
  On branch main
  nothing to commit, working tree clean
═══════════════════════════════════════════
```

#### Format 3: Minimal (For quick copy)
```
$ echo "Quick output"
Quick output
```

### Usage Examples

**User:** "Copy this terminal output"
**Kimi responds with:**
```
┌─────────────────────────────────────────┐
│  $ pip install arifos                   │
│  Successfully installed arifos-v53.2.1  │
└─────────────────────────────────────────┘
```

**User:** "Format this for paste"
```
═══════════════════════════════════════════
  Error: Connection timeout
  File: "server.py", line 42
  Fix: Check REDIS_URL env var
═══════════════════════════════════════════
```

### Quick Commands Reference

| User Says | Skill Response |
|-----------|---------------|
| "copy output" | Clean box format |
| "paste this" | Minimal format |
| "capture terminal" | Terminal block |
| "with line numbers" | Numbered format |
| "as code" | Markdown code block |

---

**DITEMPA BUKAN DIBERI**
