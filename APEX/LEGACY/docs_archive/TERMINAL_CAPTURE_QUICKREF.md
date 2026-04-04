# Terminal Capture Quick Reference ☕

## Setup (First Time Only)

```bash
# Windows
mkdir %USERPROFILE%\.arifos_clip

# Linux/macOS
mkdir -p ~/.arifos_clip
```

## Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/tpaste` | Capture & paste last 50 lines | `/tpaste` |
| `/texplain` | Capture & explain output | `/texplain` |
| `/tdebug` | Capture for debugging | `/tdebug -l 100` |
| `/tcap` | Custom capture command | `/tcap /analyze` |

## VS Code Shortcuts

- `Ctrl+Shift+T` - Capture terminal to Kimi
- `Ctrl+Shift+L` - Capture last 100 lines
- `Alt+Shift+C` - Copy selection

## Power Usage

```bash
# Capture more lines
/tpaste -l 200

# Use different command
/tcap /review

# Show preview first
/tpaste --preview

# Full control
python scripts/kimi_terminal_bridge.py -l 150 --preview /complexity
```

## Files Location

- **Output:** `~/.arifos_clip/terminal_output.log`
- **Scripts:** `scripts/kimi_terminal_bridge.py`
- **Config:** `.kimi/settings.json`
- **VS Code:** `.vscode/tasks.json`

## Troubleshooting

**File not found?** → Run setup task
**No content?** → Check terminal has output
**Kimi not found?** → Install: `pip install kimi-cli`

---
**Full Guide:** `docs/TERMINAL_CAPTURE_GUIDE.md`
