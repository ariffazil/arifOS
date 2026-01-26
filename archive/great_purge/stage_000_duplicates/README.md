# Stage 000 Duplicates - Archived

**Date:** 2026-01-26
**Reason:** The Great Purge - consolidated to `canonical_core/stage_000.py`

## Archived Files

| Original Location | Notes |
|-------------------|-------|
| `arifos/core/stage/stage_000_void.py` | 83 lines, minimal stub |
| `arifos/core/system/stages/stage_000_void.py` | 650 lines, full implementation |
| `arifos/core/enforcement/stages/stage_000_amanah.py` | 236 lines, Amanah subsystem |
| `arifos/core/system/pipeline/stage_000_hypervisor.py` | Stub, placeholder only |

## Canonical Source

All Stage 000 functionality now lives in:
```
canonical_core/stage_000.py  (~1060 lines)
```

Import from there:
```python
from canonical_core import (
    Stage000VOID,
    stage_000_void,  # Singleton instance
    VerdictType,
    InjectionDefense,
    AmanahSignals,
    compute_amanah_score,
)
```

## Constitutional Authority

**Motto:** DITEMPA BUKAN DIBERI - Forged, Not Given

This consolidation enforces the single-source-of-truth principle.
Duplicates are forbidden by constitutional law.
