# Migration Guide: v41 → v42

**Version:** v42.0.0 | **Last Updated:** 2025-12-15

---

## Overview

v42 introduces **concern-based architecture** for `arifos_core`. Files are reorganized into logical subdirectories, but **all existing imports continue to work** via backward compatibility shims.

### Key Changes

| Change | Impact | Action Required |
|--------|--------|-----------------|
| Directory reorganization | None (shims active) | Optional: update imports |
| AGI·ASI naming | None | Already renamed in v41 |
| New docs | None | Reference as needed |
| Spec manifest | None | Informational |

**Bottom Line:** v42 is backward compatible. Your v41 code works without changes.

---

## Quick Migration Checklist

- [ ] Update `arifos` package: `pip install --upgrade arifos`
- [ ] (Optional) Update imports to new paths
- [ ] Run tests to verify: `pytest -v`
- [ ] Review deprecation warnings
- [ ] Plan for v43 (shims removed)

---

## What Changed

### Directory Structure (arifos_core)

**Before (v41):**
```
arifos_core/
├── APEX_PRIME.py          # Flat at root
├── pipeline.py
├── metrics.py
├── genius_metrics.py
├── fag.py
├── merkle.py
├── ...
```

**After (v42):**
```
arifos_core/
├── system/                # Core system
│   ├── apex_prime.py
│   ├── pipeline.py
│   ├── kernel.py
│   └── runtime_manifest.py
├── enforcement/           # Floor enforcement
│   ├── metrics.py
│   └── genius_metrics.py
├── governance/            # Safety & audit
│   ├── fag.py
│   └── merkle.py
├── integration/           # LLM adapters
├── memory/                # EUREKA memory
├── waw/                   # W@W Federation
└── utils/                 # Utilities
```

### Backward Compatibility

Every relocated file has a **shim** at its old location that re-exports from the new location:

```python
# arifos_core/pipeline.py (SHIM)
"""
arifos_core.pipeline - BACKWARD COMPATIBILITY SHIM (v42)
Moved to: arifos_core/system/pipeline.py
This shim will be removed in v43.0.
"""
from arifos_core.system.pipeline import *
```

---

## Import Path Migration

### Phase 1: No Changes Needed (v42)

Your existing imports work unchanged:

```python
# These all work in v42 (via shims)
from arifos_core.pipeline import Pipeline
from arifos_core.APEX_PRIME import apex_review
from arifos_core.metrics import Metrics
from arifos_core.genius_metrics import evaluate_genius_law
from arifos_core.fag import FAG
```

### Phase 2: Optional Update (Recommended)

Update to new paths to avoid deprecation warnings:

```python
# Old (deprecated, works until v43)
from arifos_core.pipeline import Pipeline
from arifos_core.APEX_PRIME import apex_review
from arifos_core.metrics import Metrics

# New (recommended)
from arifos_core.system.pipeline import Pipeline
from arifos_core.system.apex_prime import apex_review
from arifos_core.enforcement.metrics import Metrics
```

### Phase 3: Required for v43

In v43, shims will be removed. Update all imports before upgrading to v43.

---

## Full Import Path Mapping

| Old Path (v41) | New Path (v42+) |
|----------------|-----------------|
| `arifos_core.pipeline` | `arifos_core.system.pipeline` |
| `arifos_core.APEX_PRIME` | `arifos_core.system.apex_prime` |
| `arifos_core.metrics` | `arifos_core.enforcement.metrics` |
| `arifos_core.genius_metrics` | `arifos_core.enforcement.genius_metrics` |
| `arifos_core.fag` | `arifos_core.governance.fag` |
| `arifos_core.merkle` | `arifos_core.governance.merkle` |
| `arifos_core.zkpc_runtime` | `arifos_core.governance.zkpc_runtime` |
| `arifos_core.ledger_hashing` | `arifos_core.governance.ledger_hashing` |
| `arifos_core.vault_retrieval` | `arifos_core.governance.vault_retrieval` |
| `arifos_core.kernel` | `arifos_core.system.kernel` |
| `arifos_core.ignition` | `arifos_core.system.ignition` |
| `arifos_core.runtime_manifest` | `arifos_core.system.runtime_manifest` |
| `arifos_core.telemetry` | `arifos_core.utils.telemetry` |
| `arifos_core.eye_sentinel` | `arifos_core.utils.eye_sentinel` |
| `arifos_core.runtime_types` | `arifos_core.utils.runtime_types` |
| `arifos_core.context_injection` | `arifos_core.utils.context_injection` |
| `arifos_core.kms_signer` | `arifos_core.utils.kms_signer` |
| `arifos_core.guard` | `arifos_core.integration.guards.guard` |
| `arifos_core.governed_llm` | `arifos_core.integration.adapters.governed_llm` |
| `arifos_core.llm_interface` | `arifos_core.integration.adapters.llm_interface` |
| `arifos_core.cooling_ledger` | `arifos_core.memory.cooling_ledger` |

---

## Automated Migration Script

Run this script to find imports that need updating:

```bash
#!/bin/bash
# find_deprecated_imports.sh

echo "Searching for deprecated arifos_core imports..."

# List of deprecated paths
DEPRECATED=(
    "arifos_core.pipeline"
    "arifos_core.APEX_PRIME"
    "arifos_core.metrics"
    "arifos_core.genius_metrics"
    "arifos_core.fag"
    "arifos_core.merkle"
    "arifos_core.zkpc_runtime"
    "arifos_core.kernel"
    "arifos_core.ignition"
    "arifos_core.telemetry"
    "arifos_core.eye_sentinel"
    "arifos_core.guard"
    "arifos_core.governed_llm"
    "arifos_core.cooling_ledger"
)

for path in "${DEPRECATED[@]}"; do
    echo ""
    echo "=== $path ==="
    grep -r "from $path import\|import $path" --include="*.py" . 2>/dev/null || echo "No matches"
done
```

### Python Migration Helper

```python
#!/usr/bin/env python3
"""migrate_imports.py - Update v41 imports to v42 paths."""

import re
import sys
from pathlib import Path

IMPORT_MAP = {
    "arifos_core.pipeline": "arifos_core.system.pipeline",
    "arifos_core.APEX_PRIME": "arifos_core.system.apex_prime",
    "arifos_core.metrics": "arifos_core.enforcement.metrics",
    "arifos_core.genius_metrics": "arifos_core.enforcement.genius_metrics",
    "arifos_core.fag": "arifos_core.governance.fag",
    "arifos_core.merkle": "arifos_core.governance.merkle",
    "arifos_core.zkpc_runtime": "arifos_core.governance.zkpc_runtime",
    "arifos_core.kernel": "arifos_core.system.kernel",
    "arifos_core.ignition": "arifos_core.system.ignition",
    "arifos_core.telemetry": "arifos_core.utils.telemetry",
    "arifos_core.eye_sentinel": "arifos_core.utils.eye_sentinel",
    "arifos_core.guard": "arifos_core.integration.guards.guard",
    "arifos_core.governed_llm": "arifos_core.integration.adapters.governed_llm",
    "arifos_core.cooling_ledger": "arifos_core.memory.cooling_ledger",
}

def migrate_file(filepath: Path, dry_run: bool = True) -> list:
    """Migrate imports in a single file."""
    content = filepath.read_text()
    changes = []

    for old_path, new_path in IMPORT_MAP.items():
        if old_path in content:
            if not dry_run:
                content = content.replace(old_path, new_path)
            changes.append(f"  {old_path} -> {new_path}")

    if changes and not dry_run:
        filepath.write_text(content)

    return changes

def main():
    dry_run = "--apply" not in sys.argv
    root = Path(".")

    print(f"{'DRY RUN' if dry_run else 'APPLYING'} import migration...")
    print("")

    total_changes = 0
    for pyfile in root.rglob("*.py"):
        if "archive" in str(pyfile) or ".venv" in str(pyfile):
            continue
        changes = migrate_file(pyfile, dry_run)
        if changes:
            print(f"{pyfile}:")
            for c in changes:
                print(c)
            total_changes += len(changes)

    print("")
    print(f"Total changes: {total_changes}")
    if dry_run:
        print("Run with --apply to make changes")

if __name__ == "__main__":
    main()
```

---

## Testing Migration

After updating imports, verify everything works:

```bash
# Run full test suite
pytest -v

# Check for import errors
python -c "from arifos_core import apex_review, Metrics; print('OK')"

# Check new paths work
python -c "from arifos_core.system.apex_prime import apex_review; print('OK')"
python -c "from arifos_core.enforcement.metrics import Metrics; print('OK')"
```

---

## New Features in v42

### 1. Concern-Based Organization

Files are now grouped by concern:
- `system/` — Core runtime (pipeline, apex, kernel)
- `enforcement/` — Floor checks and metrics
- `governance/` — Safety, audit, FAG
- `integration/` — LLM adapters
- `memory/` — EUREKA memory system
- `waw/` — W@W Federation
- `utils/` — Shared utilities

### 2. New Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE_v42.md](ARCHITECTURE_v42.md) | Architecture + naming reference |
| [API_STABILITY.md](API_STABILITY.md) | Full API stability contract |
| [SPEC_MANIFEST.md](../spec/SPEC_MANIFEST.md) | Canonical spec version |

### 3. @WELL File Care

New migration governance tool:
```python
from arifos_core.waw.well_file_care import create_well_file_care

well = create_well_file_care()
well.move_file("src.py", "dest/src.py")  # Governed move with audit trail
```

---

## Deprecation Timeline

| Version | Status | Action |
|---------|--------|--------|
| v42.0 | CURRENT | Shims active, optional warnings |
| v42.1 | PLANNED | Deprecation warnings enabled by default |
| v43.0 | FUTURE | Shims removed, new paths required |

### Enabling Deprecation Warnings

To see deprecation warnings now:

```python
import warnings
warnings.filterwarnings("default", category=DeprecationWarning)

# Now deprecated imports will show warnings
from arifos_core.pipeline import Pipeline
# DeprecationWarning: arifos_core.pipeline is deprecated...
```

---

## Troubleshooting

### Import Error: Module Not Found

If you see `ModuleNotFoundError` after upgrade:

1. **Verify installation:** `pip show arifos`
2. **Reinstall:** `pip install --force-reinstall arifos`
3. **Clear cache:** `find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -delete`

### Circular Import Error

If you see circular import errors:

1. **Use lazy imports** in your code
2. **Import from top-level** `arifos_core` instead of submodules
3. **Check for custom patches** that may conflict

### Test Failures

If tests fail after migration:

1. **Check mock patches** — Update patch paths from old to new
2. **Check fixture imports** — Ensure conftest.py uses correct paths
3. **Run with verbose:** `pytest -v --tb=long`

---

## Getting Help

- **GitHub Issues:** [https://github.com/ariffazil/arifOS/issues](https://github.com/ariffazil/arifOS/issues)
- **Docs:** [README.md](../README.md)
- **API Reference:** [API_STABILITY.md](API_STABILITY.md)

---

## Summary

| Question | Answer |
|----------|--------|
| Do I need to change my code? | No (until v43) |
| Will my imports break? | No |
| Should I update imports? | Recommended but not required |
| When will shims be removed? | v43.0 |
| How to find deprecated imports? | Use migration script above |

---

**DITEMPA BUKAN DIBERI** — Migration is governance. Plan before you move.
