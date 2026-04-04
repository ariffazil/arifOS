# Migration Guide: v54 → v55

**Date:** 2026-02-01  
**Target Audience:** Existing arifOS users upgrading from v54.x to v55.5  
**Breaking Changes:** None (backward compatible via deprecation aliases)  
**Migration Window:** 72 days (Phoenix-72 cooling period) until v56.0

---

## TL;DR

**v55.5 splits multi-action tools into 9 explicit tools for better LLM discoverability.**

- ✅ **Your code still works** - Legacy tool names (`_agi_`, `_asi_`, etc.) maintained as aliases
- ⚠️ **You'll see deprecation warnings** - Update tool names at your convenience
- 🗓️ **Legacy tools removed in v56.0** - Expected release: ~72 days from v55.5

---

## What Changed

### Before (v54): Hidden Actions

```python
# 7 tools with hidden action enums
await _agi_(action="sense", query="What is AI?")
await _agi_(action="think", query="Generate ideas")
await _agi_(action="reason", query="Build argument")
```

**Problem:** LLMs couldn't discover which actions existed without reading docs.

### After (v55): Explicit Tools

```python
# 9 explicit tools (no action parameter)
await agi_sense(query="What is AI?")
await agi_think(query="Generate ideas")
await agi_reason(query="Build argument")
```

**Benefits:**
- ✅ Tools are self-documenting (LLMs see purpose in name)
- ✅ Structured error codes (`F2_TRUTH` instead of generic `"error"`)
- ✅ Session state propagation via `session_id` parameter
- ✅ Constitutional floors declared in schemas

---

## Tool Mapping Table

| **Old Tool (v54)** | **Action** | **New Tool (v55)** | **Status** |
|--------------------|------------|-------------------|------------|
| `_init_` | (single) | `init_reboot` | ✅ Renamed |
| `_agi_` | `action="sense"` | `agi_sense` | ✅ Split |
| `_agi_` | `action="think"` | `agi_think` | ✅ Split |
| `_agi_` | `action="reason"` | `agi_reason` | ✅ Split |
| `_asi_` | `action="empathize"` | `asi_empathize` | ✅ Split |
| `_asi_` | `action="align"` | `asi_align` | ✅ Split |
| `_asi_` | `action="act"` | `asi_insight` | ✅ Split |
| `_apex_` | `action="judge"` | `apex_verdict` | ✅ Renamed |
| `_reality_` | (single) | `reality_search` | ✅ Renamed |
| `_trinity_` | (unchanged) | `_trinity_` | ⚪ No change |
| `_vault_` | (unchanged) | `_vault_` | ⚪ No change |

---

## Migration Path

### Option 1: Keep Using Old Names (Easiest)

```python
# This still works in v55.5
result = await _agi_(action="sense", query="...")
```

**Note:** You'll see `DeprecationWarning` in logs:
```
DeprecationWarning: _agi_ is deprecated. Use agi_sense instead. 
Old name will be removed in v56.0.
```

**When to use:** If you have existing production code and need time to migrate.

---

### Option 2: Update to New Names (Recommended)

```python
# v54 code
result = await _agi_(action="sense", query="What is AI?")

# v55 code
result = await agi_sense(query="What is AI?")
```

**Migration steps:**
1. Find all calls to `_agi_(action="sense")` → Replace with `agi_sense()`
2. Find all calls to `_agi_(action="think")` → Replace with `agi_think()`
3. Find all calls to `_agi_(action="reason")` → Replace with `agi_reason()`
4. Repeat for `_asi_`, `_init_`, `_apex_`, `_reality_`

**Regex pattern for search:**
```
_agi_\(action="(sense|think|reason)"
```

**When to use:** For new projects or when refactoring existing code.

---

### Option 3: Use Session State (Advanced)

New in v55: Multi-step workflows with session propagation.

```python
# Step 1: Sense (parse input)
session_id = "sess_workflow_abc12345"
sense_result = await agi_sense(query="Explain quantum computing", session_id=session_id)

# Step 2: Think (generate hypotheses)
think_result = await agi_think(session_id=session_id)  # Accesses prior sense result

# Step 3: Reason (build full argument)
reason_result = await agi_reason(session_id=session_id, mode="atlas")
```

**Benefits:**
- Tools share context via session cache
- No need to manually pass results between tools
- Enables complex multi-agent workflows

**When to use:** When building multi-step reasoning pipelines.

---

## API Changes

### Input Schema: New `session_id` Parameter

All 9 tools now accept optional `session_id`:

```python
{
  "session_id": {
    "type": "string",
    "description": "Optional session identifier for chaining tools",
    "pattern": "^sess_[a-zA-Z0-9]{8,}$"
  }
}
```

**Example:**
```python
# Without session (isolated call)
result = await agi_sense(query="...")

# With session (chained workflow)
result = await agi_sense(query="...", session_id="sess_abc12345")
```

---

### Output Schema: Structured Errors

Errors now include floor codes:

```python
# v54 error (generic)
{
  "error": "Truth check failed"
}

# v55 error (structured)
{
  "verdict": "VOID",
  "error": {
    "code": "F2_TRUTH",
    "message": "Confidence 0.87 below threshold 0.99",
    "suggestion": "Add citations or reduce claim certainty"
  }
}
```

**Floor error codes:**
- `F2_TRUTH` - Factual accuracy below 0.99
- `F3_TRI_WITNESS` - Consensus failed (H/A/E disagreement)
- `F4_CLARITY` - Entropy increased (ΔS > 0)
- `F5_PEACE` - Destructive action detected
- `F6_EMPATHY` - Empathy score below 0.95
- `F7_HUMILITY` - Uncertainty not stated (Ω₀ missing)
- `F10_ONTOLOGY` - Reality confusion (consciousness claims)
- `F12_HARDENING` - Injection attack detected
- `INTERNAL_ERROR` - System error (not floor violation)

---

## MCP Client Updates

### Claude Desktop

**v54 config:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "mcp"]
    }
  }
}
```

**v55 config:** (No change required)

Claude will see 16 tools (9 new + 5 deprecated + 2 utility). Old names still work.

---

### ChatGPT Actions / GPT Builder

**v54 OpenAPI:** 7 tools listed  
**v55 OpenAPI:** 16 tools listed (9 primary)

**No action required.** OpenAPI spec auto-updates to include new tools.

---

### Cursor IDE

**v54:** MCP extension sees 7 tools  
**v55:** MCP extension sees 16 tools

**What to do:** Refresh MCP tool list in Cursor settings. New tools will appear automatically.

---

## Testing Your Migration

### 1. Verify Tool Discovery

```bash
# List all tools
python -c "
from mcp.core.tool_registry import ToolRegistry
reg = ToolRegistry()
tools = reg.list_tools()
print(f'Total tools: {len(tools)}')
for name in sorted(tools.keys()):
    print(f'  - {name}')
"
```

**Expected output:**
```
Total tools: 16
  - _agi_ (DEPRECATED)
  - _apex_ (DEPRECATED)
  - _asi_ (DEPRECATED)
  - _init_ (DEPRECATED)
  - _reality_ (DEPRECATED)
  - _trinity_
  - _vault_
  - agi_reason
  - agi_sense
  - agi_think
  - apex_verdict
  - asi_align
  - asi_empathize
  - asi_insight
  - init_reboot
  - reality_search
```

---

### 2. Test Backward Compatibility

```python
import warnings

# This should work and emit a deprecation warning
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    result = await _agi_(action="sense", query="test")
    
    assert len(w) == 1
    assert "deprecated" in str(w[0].message).lower()
    print("✅ Backward compatibility verified")
```

---

### 3. Test New Tools

```python
# Test explicit tool calls
result = await agi_sense(query="What is AI?")
assert "verdict" in result or "vote" in result
print("✅ New tool interface verified")
```

---

## Timeline

| Date | Version | Status | Action |
|------|---------|--------|--------|
| **2026-02-01** | v55.5 | ✅ Released | Both old and new tools available |
| **Now → +72 days** | v55.x | ⚠️ Migration Period | Update code at your convenience |
| **~2026-04-14** | v56.0 | ❌ Legacy Removed | Old tool names (_agi_, _asi_, etc.) no longer work |

**Phoenix-72 Protocol:** 72-day cooling period for all breaking changes.

---

## FAQ

### Q: Do I have to migrate now?

**A:** No. You have 72 days to migrate at your convenience. Old names work in v55.5.

---

### Q: What happens if I don't migrate before v56.0?

**A:** Your code will break. Calls to `_agi_`, `_asi_`, etc. will raise `ToolNotFoundError`.

---

### Q: Can I use both old and new names in the same codebase?

**A:** Yes. They coexist in v55.5. This allows gradual migration.

---

### Q: How do I silence deprecation warnings during migration?

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="mcp")
```

**Note:** Not recommended for production. Warnings help track migration progress.

---

### Q: Will my MCP Inspector still work?

**A:** Yes. It will show 16 tools instead of 7. Both old and new tools are testable.

---

### Q: Do constitutional floors (F1-F13) work differently?

**A:** No. Floor enforcement is identical. Only the tool interface changed.

---

### Q: What if I use `_trinity_` or `_vault_`?

**A:** No change needed. These tools are unchanged in v55.5.

---

## Support

**Issues:** https://github.com/ariffazil/arifOS/issues  
**Discussions:** https://github.com/ariffazil/arifOS/discussions  
**Email:** arifbfazil@gmail.com

---

**Governance Audit:**
- **F1 (Amanah):** Fully reversible - old code continues working
- **F2 (Truth):** All claims verified against v55.5 implementation
- **F4 (Clarity):** Step-by-step migration guide with examples
- **F7 (Humility):** 72-day timeline acknowledges migration complexity

**DITEMPA BUKAN DIBERI**
