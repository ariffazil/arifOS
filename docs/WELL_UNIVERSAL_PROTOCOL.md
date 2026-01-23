# @WELL Universal Migration Protocol

**Version:** v42.0.0
**Status:** PRODUCTION
**License:** AGPL-3.0

**DITEMPA BUKAN DIBERI** — Forged, not given

---

## Overview

@WELL is the universal file care module for arifOS v42 architecture. It extends the W@W Federation's "care" domain to include governed file system operations.

### Key Features

- **F1 Amanah Compliance**: Full audit trail, checksum verification, reversibility
- **Protected File Safety**: System files (.git, LICENSE) cannot be modified
- **Cross-Platform**: Works with Claude, Copilot, ChatGPT, Gemini
- **888_HOLD Trigger**: Large batch operations require confirmation

---

## Architecture

```
L3_KERNEL/
└── arifos_core/waw/
    └── well_file_care.py          # Core logic (platform-agnostic)

L4_MCP/
└── arifos_well/
    ├── __init__.py
    ├── manifest.json              # Universal tool manifest
    ├── core/
    │   └── __init__.py            # Re-exports from L3
    ├── server/
    │   └── app.py                 # FastAPI REST API
    └── bindings/
        ├── mcp_claude.py          # Claude MCP binding
        ├── copilot_github.py      # GitHub Copilot binding
        ├── chatgpt_codex.py       # ChatGPT/OpenAI binding
        └── gemini_cli.py          # Google Gemini binding
```

---

## 7-Phase Migration Protocol

When using @WELL for architecture migrations, follow this protocol:

### Phase 1: Health Check

```python
# Check repository health before starting
health = well.check_health()
if not health.is_healthy:
    print(f"Issues: {health.issues}")
    print(f"Warnings: {health.warnings}")
```

### Phase 2: Snapshot

```python
# Save pre-migration snapshot
snapshot = well.save_snapshot("pre_v42_migration")
print(f"Snapshot saved: {snapshot}")
```

### Phase 3: Dry Run

```python
# Test operations without executing
operations = [
    {"source": "old/path.py", "target": "new/path.py"},
    # ... more operations
]
results = well.batch_relocate(operations, dry_run=True)
for r in results:
    print(f"{r.source_path}: {'OK' if r.success else r.message}")
```

### Phase 4: Execute

```python
# Execute with audit trail
results = well.batch_relocate(operations, dry_run=False)
successful = sum(1 for r in results if r.success)
print(f"Completed: {successful}/{len(results)}")
```

### Phase 5: Verify

```python
# Check health after migration
post_health = well.check_health()
assert post_health.is_healthy, "Migration broke structure!"
```

### Phase 6: Update Imports

```python
# Create backward-compatibility re-exports in __init__.py
# (Manual step - @WELL handles files, not code editing)
```

### Phase 7: Run Tests

```bash
# Verify no test breakage
pytest -v
```

---

## Platform Setup

### Claude MCP (Claude Desktop / Claude Code)

**claude_desktop_config.json:**
```json
{
    "mcpServers": {
        "well": {
            "command": "python",
            "args": ["-m", "arifos_well.bindings.mcp_claude"],
            "env": {
                "WELL_REPO_ROOT": "/path/to/arifOS"
            }
        }
    }
}
```

### GitHub Copilot

1. Add `L4_MCP/arifos_well/bindings/copilot_github.py` to workspace
2. Generate instructions:
   ```bash
   python -m arifos_well.bindings.copilot_github --generate-instructions > .github/copilot_instructions.md
   ```

### ChatGPT Codex / OpenAI

```python
from arifos_well.bindings.chatgpt_codex import get_openai_tools, WellToolExecutor

# Get tools for API
tools = get_openai_tools()

# Execute tool calls
executor = WellToolExecutor(repo_root="/path/to/arifOS")
result = executor.execute("well_relocate", {"source": "a.py", "target": "b.py"})
```

### Google Gemini

```python
from arifos_well.bindings.gemini_cli import get_gemini_tools, GeminiWellExecutor

# Get tools for Gemini
tools = get_gemini_tools()

# Execute function calls
executor = GeminiWellExecutor(repo_root="/path/to/arifOS")
result = executor.execute_by_name("well_check_health", {})
```

### REST API (Universal)

```bash
# Start server
python -m arifos_well.server.app

# Or with custom config
WELL_HOST=0.0.0.0 WELL_PORT=8042 WELL_REPO_ROOT=/path/to/repo python -m arifos_well.server.app
```

**Endpoints:**
- `GET /health` - Server health
- `GET /well/status` - @WELL status
- `GET /well/list-files?path=.&pattern=*.py` - List files
- `GET /well/check-health` - Repository health
- `POST /well/heal-structure` - Create missing directories
- `POST /well/relocate` - Move file
- `POST /well/duplicate` - Copy file
- `POST /well/retire` - Archive file
- `POST /well/undo-last-care` - Undo last operation
- `POST /well/batch-relocate` - Batch move
- `GET /well/audit-history` - View audit trail

---

## Protected Files

These files **CANNOT** be moved or deleted:

| File | Reason |
|------|--------|
| `.git/` | Version control |
| `.gitignore` | Git config |
| `LICENSE` | Legal |
| `README.md` | Project docs |
| `pyproject.toml` | Package config |
| `setup.py` | Legacy config |
| `.env` | Secrets |
| `CLAUDE.md` | AI instructions |
| `AGENTS.md` | Agent config |
| `vault_999/` | Constitutional vault |
| `cooling_ledger/` | Audit trail |

---

## 888_HOLD Triggers

Operations that trigger 888_HOLD (require confirmation):

1. **Batch relocate > 10 files**: Large migrations need review
2. **Protected file operations**: Automatically blocked
3. **Cross-layer moves**: Moving files between L1-L7

---

## Audit Trail Format

All operations are logged to `well_audit_trail.jsonl`:

```json
{
  "operation_id": "WELL_20241215_143022_123456",
  "operation_type": "relocate",
  "source_path": "arifos_core/pipeline.py",
  "target_path": "arifos_core/system/pipeline.py",
  "checksum_before": "sha256:abc123...",
  "checksum_after": "sha256:abc123...",
  "status": "success",
  "timestamp": "2024-12-15T14:30:22.123456Z",
  "reversible": true,
  "backup_path": ".well_snapshots/pipeline.py.WELL_20241215_143022_123456"
}
```

---

## Error Recovery

### Undo Last Operation

```python
result = well.undo_last()
if result.success:
    print(f"Undone: {result.message}")
else:
    print(f"Cannot undo: {result.message}")
```

### Restore from Backup

Backups are stored in `.well_snapshots/`. Each backup has the original filename plus operation ID.

```python
# Find backup
import os
for f in os.listdir(".well_snapshots"):
    print(f)

# Manual restore if needed
shutil.copy(".well_snapshots/file.WELL_xxx", "original/path/file")
```

---

## Integration with v42 Migration

@WELL is specifically designed for Phase 2 of v42 migration:

1. **Phase 1 (Complete)**: Create L1-L7 directories
2. **Phase 1.5 (This)**: Forge @WELL for governed migrations
3. **Phase 2**: Reorganize arifos_core by concern
4. **Phase 3**: Extract MCP + API with double-shim
5. **Phase 4**: Finalize and tag v42.0.0

---

## Governance Compliance

@WELL enforces arifOS governance:

| Floor | Enforcement |
|-------|-------------|
| **F1 Amanah** | All operations auditable, reversible |
| **F2 Truth** | Checksum verification |
| **F6 Amanah** | No destructive actions on protected files |
| **F8 Tri-Witness** | Audit trail is human-readable |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v42.0.0 | 2024-12-15 | Initial universal release |

---

**DITEMPA BUKAN DIBERI** — The tool is forged. Use it wisely.
