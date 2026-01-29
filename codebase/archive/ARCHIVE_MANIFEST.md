# 📦 ARCHIVE MANIFEST - v54.0 HOUSEKEEPING

**Date:** 2026-01-29  
**Action:** Archived redundant non-hardened code  
**Reason:** Consolidated to hardened v53.4.0/v54.0 architecture

---

## Summary

This archive contains the **legacy/non-hardened** versions of AGI and ASI code that have been superseded by the hardened implementations.

**Rule:** If it's not hardened, it's archived.

---

## AGI Archive (`archive/agi/`)

### Archived Files

| File | Reason | Replacement |
|------|--------|-------------|
| `engine.py` | Old unified engine (v52+v53) | `engine_hardened.py` (v53.4.0) |
| `agi_components.py` | Component modules | Integrated into hardened engine |
| `evidence.py` | Evidence gathering | Superseded by precision weighting |
| `hardening.py` | Basic hardening | Enhanced in hardened engine |
| `kernel.py` | MCP interface | Integrated into hardened architecture |
| `metrics.py` | Metric collection | Integrated into hardened engine |
| `parallel.py` | Parallel execution | Integrated into hardened engine |
| `trinity_sync.py` | 6-paradox sync | `trinity_sync_hardened.py` |
| `stages/` | Stage modules | Integrated into hierarchy.py |

### Key Differences (Old vs Hardened)

| Feature | Old (Archived) | Hardened (Current) |
|---------|----------------|-------------------|
| Precision | Equal weighting | Kalman π = 1/σ² |
| Hierarchy | Flat 3-stage | 5-level cortex |
| Action | Passive observer | EFE minimization |
| Paradoxes | 6 paradoxes | 9 paradoxes |
| Equilibrium | None | Nash equilibrium solver |

---

## ASI Archive (`archive/asi/`)

### Archived Files

| File | Reason | Replacement |
|------|--------|-------------|
| `engine.py` | Old ASI engine | `engine_hardened.py` (v53.4.0) |
| `asi_components_v2.py` | Component modules | Integrated into hardened engine |
| `async_wrapper.py` | Async utilities | Native async in hardened |
| `kernel.py` | MCP interface | Integrated into hardened architecture |
| `empathy/` | Empathy modules | TrinitySelf in hardened |
| `integration/` | Integration code | Direct integration in hardened |

### Key Differences (Old vs Hardened)

| Feature | Old (Archived) | Hardened (Current) |
|---------|----------------|-------------------|
| Trinity | Basic | 3-Trinity architecture |
| Stakeholders | Flat list | Fractal recursion |
| Empathy | Simple κ | Full κᵣ with bias mirror |
| Peace | Basic | Peace² (internal×external) |

---

## Current Active Structure

### AGI (Hardened) - `codebase/agi/`

```
agi/
├── __init__.py              # Updated exports
├── action.py                # ⭐ NEW - Active Inference (EFE)
├── engine_hardened.py       # ⭐ HARDENED - Unified AGI v53.4.0
├── hierarchy.py             # ⭐ NEW - 5-level cortex
├── precision.py             # ⭐ NEW - Kalman weighting
└── trinity_sync_hardened.py # ⭐ HARDENED - 6-paradox sync
```

### ASI (Hardened) - `codebase/asi/`

```
asi/
├── __init__.py              # Updated exports
└── engine_hardened.py       # ⭐ HARDENED - 3-Trinity v53.4.0
```

### APEX (9-Paradox) - `codebase/apex/`

```
apex/
├── __init__.py                    # 9-paradox exports
├── trinity_nine.py                # ⭐ NEW - 9-paradox engine
├── equilibrium_finder.py          # ⭐ NEW - Equilibrium solver
├── demo_nine_paradox.py           # ⭐ NEW - Demo
├── NINE_PARADOX_ARCHITECTURE.md   # Documentation
├── 9PARADOX_SUMMARY.md            # Executive summary
└── 9PARADOX_VISUAL.txt            # ASCII diagram
```

---

## Recovery Instructions

If you need to recover an archived file:

```bash
# From arifOS/codebase/
cp archive/agi/engine.py agi/engine.py.old
cp archive/asi/engine.py asi/engine.py.old
```

**Note:** These files are NOT compatible with the hardened architecture. Use only for reference.

---

## Why Archive?

1. **Reduce confusion** - Only hardened code in main codebase
2. **Enforce usage** - Forces use of precision/hierarchy/action layers
3. **Clean imports** - No accidental imports of old code
4. **Document evolution** - Shows progression from v52 → v53 → v54

---

## Version History

| Version | Status | Location |
|---------|--------|----------|
| v52.x | ARCHIVED | `archive/` |
| v53.0-3 | ARCHIVED | `archive/` |
| v53.4.0 | **ACTIVE** | `agi/`, `asi/` |
| v54.0 | **ACTIVE** | `apex/` |

---

## DITEMPA BUKAN DIBERI

*The old code served its purpose. The hardened code is forged stronger.*
