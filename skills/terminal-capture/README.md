# Terminal Capture Skill

Quickly capture terminal output for Kimi CLI with clean formatting.

## Installation

Copy this folder to your Kimi CLI skills directory:

```bash
# Windows
xcopy /E "C:\Users\User\arifOS\skills\terminal-capture" "%USERPROFILE%\.config\agents\skills\terminal-capture"

# Or manually copy SKILL.md to:
# %USERPROFILE%\.config\agents\skills\terminal-capture\SKILL.md
```

## Usage

### Option 1: PowerShell Helper Script

```powershell
# Default clean format
./capture.ps1 -Command "git status"

# Box format
./capture.ps1 -Command "python -m pytest" -Box

# With line numbers
./capture.ps1 -Command "cat server.py" -WithLineNumbers -Lines 30

# Minimal (just text)
./capture.ps1 -Command "echo hello" -Minimal
```

### Option 2: Just Ask Kimi

Simply tell Kimi:
- "Copy this output: [paste your output]"
- "Format this for paste"
- "Capture terminal output"

Kimi will automatically use this skill to format cleanly.

## Copy-Paste Tips

### Windows Terminal
1. Select text with mouse
2. Right-click to copy
3. Right-click in Kimi to paste

### VS Code Terminal
1. Select text
2. Ctrl+C to copy
3. Ctrl+V in Kimi

### PowerShell
```powershell
# Pipe to clipboard
python script.py | Set-Clipboard

# Then paste in Kimi
```

## Why This Exists

Regular terminal output has issues:
- Markdown breaks with special characters
- Line wrapping makes selection hard
- Code blocks interfere with copy-paste

This skill gives you **clean, predictable formatting** that just works.

---

**DITEMPA BUKAN DIBERI**
