# Legacy Tests (Deprecated)

**Scope:** Pre-v49 Compatibility Stubs
**Status:** DEPRECATED - Tests marked `@pytest.mark.skip`

This directory contains **deprecated tests** from the old `arifos_core` package that existed before the v49 consolidation.

---

## Test Files

| File | Status | Description |
|------|--------|-------------|
| `test_constitutional_floors.py` | SKIPPED | Legacy floor tests (replaced by `tests/constitutional/`) |
| `test_mcp_fixes.py` | SKIPPED | Legacy MCP fixes (superseded by `tests/mcp/`) |

---

## Why Legacy?

The arifOS codebase underwent major consolidation in v49:
- `arifos_core/` → merged into `arifos/core/`
- `arifos_mcp/` → merged into `arifos/mcp/`
- Test patterns updated to match new structure

These tests are preserved for:
1. Historical reference
2. Potential backward compatibility checks
3. Migration validation

---

## Do NOT Run These

```bash
# These tests are marked skip and will not execute
pytest tests/legacy/ -v

# Output: All tests SKIPPED
```

---

## Migration Path

If you need the equivalent functionality:
- **Floor tests** → `tests/constitutional/`
- **MCP tests** → `tests/mcp/`
- **Core tests** → `tests/core/`

---

**Status:** ARCHIVED
**DITEMPA BUKAN DIBERI**
