# Enable Kimi CLI Autocomplete for PowerShell

## 🎯 Quick Start

**Run this command to enable autocomplete:**
```powershell
. ".\setup_kimi_autocomplete.ps1"
```

**Then restart PowerShell or run:**
```powershell
. $PROFILE
```

## ✅ What You Get

### Enhanced Autocomplete:
- **Tab completion** for kimi commands and arguments
- **Command history search** (Ctrl+R)
- **arifOS skill completion** (`/000<TAB>`, `/gitQC<TAB>`)
- **Constitutional skill helpers** (`khelp`, `ks`)

### Constitutional Skills Available:
```
Core Skills:           APEX PRIME Skills:
/000                    /audit-constitution
/gitforge               /verify-trinity  
/gitQC                  /verify-sources
/gitseal                /issue-verdict
/sabar                  /track-alignment
                        /anti-bypass-scan
                        /ledger-audit
```

## 🔧 Usage Examples

### Basic Kimi CLI:
```powershell
kimi --help              # Show help
kimi --skills            # List skills
kimi --provider<TAB>     # Autocomplete providers
```

### Constitutional Workflow:
```powershell
/000          # Initialize session
/gitforge     # Analyze entropy
/gitQC        # Validate constitutional compliance  
/gitseal      # Request constitutional seal
```

### Helper Functions:
```powershell
khelp         # Show Kimi CLI reference
ks            # List all constitutional skills
```

## 🛡️ Constitutional Compliance

**All autocomplete respects:**
- **F1-F9 floors** - No constitutional bypass
- **No self-sealing** - Kimi cannot approve own work
- **Proper authority chain** - Human ratification required
- **Audit trail compatibility** - All actions logged to THE EYE

## 📋 Installation Details

The setup:
1. **Configures PSReadLine** for enhanced autocomplete
2. **Adds Kimi-specific completions** for commands and skills
3. **Creates helper functions** (khelp, ks)
4. **Maintains constitutional governance** throughout

## 🚨 Important Notes

- **Restart PowerShell** after setup for full effect
- **Terminal must support** basic autocomplete (works in Windows Terminal, VS Code)
- **Predictive suggestions** require VT support (may not work in all terminals)
- **Constitutional workflow** still required: `/000 → /gitforge → /gitQC → /gitseal → /999`

## 🔍 Troubleshooting

If autocomplete doesn't work:
1. Check PSReadLine is available: `Get-Module PSReadLine`
2. Reload profile: `. $PROFILE`
3. Test basic completion: `khelp`
4. Verify config loaded: `Get-PSReadLineOption`

**For full Claude Code-like experience**, this provides the closest PowerShell equivalent to interactive shell features.

---

**DITEMPA BUKAN DIBERI** - Forged through constitutional clarity, not complexity. 🔒