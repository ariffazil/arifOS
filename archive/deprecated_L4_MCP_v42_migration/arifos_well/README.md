# @WELL Universal - Governed File Care

**Version:** v42.0.0 | **License:** AGPL-3.0

> DITEMPA BUKAN DIBERI — Forged, not given

---

## What is @WELL?

@WELL extends the W@W Federation's "care" domain to file system operations. It provides **F1 Amanah-compliant** file migrations with:

- **Audit Trail**: Every operation logged with checksums
- **Reversibility**: Undo any operation
- **Protected Files**: System files cannot be modified
- **Cross-Platform**: Works with Claude, Copilot, ChatGPT, Gemini

---

## Quick Start

### Python

```python
from arifos_core.waw.well_file_care import create_well_file_care

well = create_well_file_care()
result = well.relocate("old.py", "new.py")
```

### REST API

```bash
python -m arifos_well.server.app
curl http://localhost:8042/well/check-health
```

### Claude MCP

```json
{
  "mcpServers": {
    "well": {
      "command": "python",
      "args": ["-m", "arifos_well.bindings.mcp_claude"]
    }
  }
}
```

---

## Directory Structure

```
arifos_well/
├── __init__.py           # Package exports
├── manifest.json         # Universal tool manifest
├── README.md             # This file
├── core/
│   └── __init__.py       # Re-exports from L3_KERNEL
├── server/
│   └── app.py            # FastAPI REST server
└── bindings/
    ├── mcp_claude.py     # Claude MCP binding
    ├── copilot_github.py # GitHub Copilot binding
    ├── chatgpt_codex.py  # OpenAI/ChatGPT binding
    └── gemini_cli.py     # Google Gemini binding
```

---

## Tools Available

| Tool | Description | Dangerous |
|------|-------------|-----------|
| `well_status` | Get @WELL configuration | No |
| `well_list_files` | List files with protection status | No |
| `well_check_health` | Check repository health | No |
| `well_heal_structure` | Create missing directories | No |
| `well_relocate` | Move file with audit | Yes |
| `well_duplicate` | Copy file | No |
| `well_retire` | Archive instead of delete | Yes |
| `well_undo_last` | Undo last operation | No |
| `well_batch_relocate` | Batch move (888_HOLD if >10) | Yes |
| `well_audit_history` | View audit trail | No |

---

## Documentation

- [Quick Start](../../docs/WELL_QUICK_START.md)
- [Universal Protocol](../../docs/WELL_UNIVERSAL_PROTOCOL.md)
- [API Docs](http://localhost:8042/docs) (when running)

---

## Core Logic Location

The platform-agnostic core is at:
`L3_KERNEL/arifos_core/waw/well_file_care.py`

This module provides REST API and platform bindings.

---

**arifOS v42 | L4_MCP**
