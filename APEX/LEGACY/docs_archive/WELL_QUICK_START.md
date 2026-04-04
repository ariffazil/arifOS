# @WELL Quick Start Guide

**Get governed file operations in 5 minutes**

---

## Installation

```bash
# Install arifOS (includes @WELL)
pip install arifos

# Or install from source
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

---

## Quick Usage

### Python API

```python
from arifos_core.waw.well_file_care import create_well_file_care

# Create @WELL instance
well = create_well_file_care()

# Check health
health = well.check_health()
print(f"Healthy: {health.is_healthy}")

# Move a file
result = well.relocate("old/path.py", "new/path.py")
print(f"Success: {result.success}")

# Undo if needed
if not result.success:
    well.undo_last()
```

### REST API

```bash
# Start server
python -m arifos_well.server.app

# Check health
curl http://localhost:8042/well/check-health

# Move file
curl -X POST http://localhost:8042/well/relocate \
  -H "Content-Type: application/json" \
  -d '{"source": "old.py", "target": "new.py"}'
```

### Claude MCP

Add to `claude_desktop_config.json`:

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

Then in Claude: "Use @WELL to check repository health"

---

## Common Operations

### Check Repository Health

```python
health = well.check_health()
print(f"Issues: {health.issues}")
print(f"Warnings: {health.warnings}")
print(f"Layers: {health.layer_status}")
```

### Move File with Audit

```python
result = well.relocate(
    source="arifos_core/pipeline.py",
    target="arifos_core/system/pipeline.py",
    create_backup=True  # Default
)
```

### Batch Move (Migration)

```python
operations = [
    {"source": "file1.py", "target": "new/file1.py"},
    {"source": "file2.py", "target": "new/file2.py"},
]

# Dry run first
results = well.batch_relocate(operations, dry_run=True)

# Then execute
results = well.batch_relocate(operations, dry_run=False)
```

### Archive Instead of Delete

```python
# Moves to archive/ with timestamp
result = well.retire("deprecated_file.py")
```

### Undo Last Operation

```python
result = well.undo_last()
print(result.message)
```

---

## Platform Guides

### For Claude Users

Tools available:
- `well_check_health` - Check repo structure
- `well_relocate` - Move file
- `well_batch_relocate` - Batch move
- `well_undo_last` - Undo operation

### For Copilot Users

Generate instructions:
```bash
python -m arifos_well.bindings.copilot_github --generate-instructions
```

### For ChatGPT/OpenAI Users

```python
from arifos_well.bindings.chatgpt_codex import get_openai_tools
tools = get_openai_tools()  # Use with ChatCompletion API
```

### For Gemini Users

```python
from arifos_well.bindings.gemini_cli import get_gemini_tools
tools = get_gemini_tools()  # Use with Gemini API
```

---

## Protected Files

These cannot be moved:
- `.git/`, `.gitignore`
- `LICENSE`, `README.md`
- `pyproject.toml`, `setup.py`
- `.env`, `CLAUDE.md`, `AGENTS.md`

---

## Troubleshooting

### "Source not found"
Check that the file path is relative to repo root.

### "BLOCKED: Protected file"
You're trying to move a protected file. This is intentional.

### "888_HOLD: Batch size exceeds limit"
Split into smaller batches (≤10 files) or use `dry_run=True` first.

### Undo not working
Only the most recent reversible operation can be undone.

---

## Next Steps

- Read [WELL_UNIVERSAL_PROTOCOL.md](WELL_UNIVERSAL_PROTOCOL.md) for full documentation
- Check [manifest.json](../L4_MCP/arifos_well/manifest.json) for tool definitions
- See API docs at http://localhost:8042/docs when running the server

---

**DITEMPA BUKAN DIBERI** — Forged, not given
