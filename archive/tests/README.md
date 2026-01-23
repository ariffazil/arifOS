# Archived Legacy Tests

This directory contains tests from previous arifOS versions that are no longer actively maintained but preserved for historical reference.

## v37/ — Version 37 Tests

**Archived:** 2026-01-10
**Reason:** v37 is 3 versions behind current (v46)

| File | Purpose | Status |
|------|---------|--------|
| `test_memory_enforcement_v37.py` | v37 memory enforcement logic | Superseded by current tests |
| `test_memory_stack_v37.py` | v37 memory stack implementation | Superseded by `test_memory_trinity.py` |

## v39/ — Version 39 Tests

**Archived:** 2026-01-10
**Reason:** v39 is 2 versions behind current (v46)

| File | Purpose | Status |
|------|---------|--------|
| `test_v39_ci_guardrails.py` | v39 CI guardrails | Superseded by v44/v45 CI tests |

---

## Why Archive Instead of Delete?

**Preservation Principle:** Legacy tests contain historical context about:
- How features evolved
- What requirements existed in older versions
- Migration patterns from v37 → v46

**When to Reference:**
- Understanding architectural evolution
- Investigating regressions
- Migrating legacy systems still on v37/v39

---

## Running Archived Tests

**Warning:** Archived tests may not pass on current codebase.

```bash
# Run archived tests (may fail)
pytest archive/tests/v37/
pytest archive/tests/v39/

# Expected outcome: Most will fail due to API changes
```

---

**Last Updated:** 2026-01-10
**Archived Tests:** 3 files (v37: 2, v39: 1)
