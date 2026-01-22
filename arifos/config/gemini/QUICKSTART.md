# Gemini CLI Quick Start - arifOS Integration

## Initial Setup (Run Once)

After installing Gemini CLI with `npm install -g @google/gemini-cli`:

1. **Let Gemini CLI initialize** (first run creates `.gemini` directory):
   ```cmd
   gemini
   ```
   Press `Esc` to exit after initialization completes.

2. **Apply arifOS configuration**:
   ```cmd
   cd C:\Users\User\OneDrive\Documents\GitHub\arifOS
   scripts\setup_gemini_config.bat
   ```

3. **Verify setup**:
   ```cmd
   scripts\gemini_doctor.bat
   ```

4. **Start using Gemini CLI**:
   ```cmd
   gemini
   ```

---

## Daily Usage

### Start Gemini in arifOS project:
```cmd
cd C:\Users\User\OneDrive\Documents\GitHub\arifOS
gemini
```

### Essential Commands (once in Gemini CLI):

| Command | Description | Constitutional Check |
|---------|-------------|---------------------|
| `/init` | Initialize arifOS session | Required first action |
| `/sense` | Gather facts (Stage 111) | F2 Truth validation |
| `/reason` | Logical analysis (Stage 333) | F4 Clarity check |
| `/judge` | Get verdict (Stage 888) | Full 12-floor validation |
| `/seal` | Finalize decision (Stage 999) | Ledger commitment |
| `/witness` | Query witness logs | Cross-agent verification |
| `/test` | Run pytest suite | F6 Amanah (reversible) |
| `/check` | Constitutional alignment | Pre-commit validation |

### File Operations:
- **Read files**: Just ask "show me file.py"
- **Edit code**: "modify function X in file.py to do Y"
- **Create files**: "create new_module.py with Z" (searches first, per anti-pollution rule)

### Git Operations (Constitutional):
```
/status          → git status (always safe)
/diff            → git diff (always safe)
/log             → git log (always safe)

For push/merge:  → Requires 888_HOLD confirmation
                   Gemini will prompt before execution
```

---

## MCP Integration

Gemini CLI connects to arifOS MCP server automatically, enabling:

- **Constitutional checkpoints** before actions
- **Cross-agent witness logging** (panopticon)
- **12-floor validation** (F1-F12)
- **Ledger persistence** (immutable audit trail)

Status shown in CLI: `1 MCP server` (should be green when connected)

---

## Troubleshooting

### "Unable to load MCP status"
```cmd
# Check if arifOS MCP gateway is accessible
python arifos\orchestrator\mcp_gateway.py --help

# Verify Python environment
.venv\Scripts\activate.bat

# Reinstall config
scripts\setup_gemini_config.bat
```

### "No MCP servers configured"
```cmd
scripts\setup_gemini_config.bat
```

### "Command not recognized"
Aliases not loaded. Check if `%USERPROFILE%\.gemini\aliases.json` exists.

### Complete reset (if broken):
```cmd
# Backup first (if you have working config)
scripts\backup_gemini_config.bat

# Delete user config
rmdir /s /q "%USERPROFILE%\.gemini"

# Reinstall
npm install -g @google/gemini-cli

# Reconfigure
scripts\setup_gemini_config.bat
```

---

## Configuration Backup

**Before making config changes**, always backup:
```cmd
scripts\backup_gemini_config.bat
```

Backups stored in: `config\gemini\backups\`

---

## Constitutional Governance

All Gemini actions pass through 12-floor validation:

| Floor | Check | Trigger |
|-------|-------|---------|
| F1 (Truth) | ≥0.99 accuracy | AGI verification |
| F2 (Clarity) | ≥0 entropy reduction | AGI analysis |
| F6 (Amanah) | Reversible operations | ASI mandate check |
| F12 (Injection) | <0.85 injection risk | ASI defense |

**Verdicts:**
- **SEAL**: Approved, proceed
- **VOID**: Blocked, hard floor violated
- **888_HOLD**: Requires explicit human confirmation
- **PARTIAL**: Warning, soft floor concern

---

## Identity

- **Role**: Architect (Δ)
- **Authority**: Design and planning
- **Witness**: Stages 111/222/333 (Sense/Reflect/Atlas)
- **Floors**: F2 (Truth), F4 (Clarity), F7 (Humility)

---

**DITEMPA BUKAN DIBERI** - Forged, not given.

See: [GEMINI.md](../../GEMINI.md) for full integration details.
