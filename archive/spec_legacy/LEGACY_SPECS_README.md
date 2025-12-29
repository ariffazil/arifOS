# Legacy Spec Files — Backward Compatibility Reference

**Status:** DEPRECATED (retained for history/tests only)
**Authoritative Source:** [spec/v44/](v44/) (Track B Authority v44.0)
**Last Updated:** 2025-12-25

---

## Summary

As of **v44.0 (TEARFRAME consolidation)**, all runtime spec loading has been unified under a single authority: **spec/v44/**.

Legacy spec files in this directory and subdirectories (v42/, v43/) are **DEPRECATED** but **NOT DELETED** for:
- Historical reference
- Legacy test compatibility
- Backward compatibility fallback (explicit opt-in)

---

## Authoritative Specs (v44.0)

**All runtime loaders MUST use spec/v44/ by default (fail-closed):**

| Spec File | Purpose | Loader Module |
|-----------|---------|---------------|
| [v44/constitutional_floors.json](v44/constitutional_floors.json) | F1-F9 floor thresholds, verdicts, red patterns | `arifos_core/enforcement/metrics.py` |
| [v44/session_physics.json](v44/session_physics.json) | TEARFRAME physics (budget, burst, streaks) | `arifos_core/governance/session_physics.py` |
| [v44/genius_law.json](v44/genius_law.json) | GENIUS LAW metrics (G, C_dark, Psi) | `arifos_core/enforcement/genius_metrics.py` |
| [v44/waw_prompt_floors.json](v44/waw_prompt_floors.json) | W@W Federation config | `arifos_core/waw/` |
| [v44/cooling_ledger_phoenix.json](v44/cooling_ledger_phoenix.json) | Cooling Ledger + Phoenix-72 config | `arifos_core/memory/` |

---

## Legacy Spec Files (Deprecated)

### Root spec/ Directory

| File | Version | Status | Notes |
|------|---------|--------|-------|
| `constitutional_floors_v35Omega.json` | v35Omega | DEPRECATED | Pre-dual-order; retained for v35 test cases |
| `constitutional_floors_v38Omega.json` | v38.3.0 | DEPRECATED | Dual-order equilibrium; pre-TEARFRAME |
| `genius_law_v38Omega.json` | v38Omega | DEPRECATED | Pre-v42 GENIUS LAW consolidation |
| `waw_prompt_floors_v38Omega.json` | v38Omega | DEPRECATED | Pre-v42 W@W config |
| `cooling_ledger_phoenix_v38.json` | v38 | DEPRECATED | Pre-v42 memory config |

### spec/v42/ Subdirectory

| File | Version | Status | Notes |
|------|---------|--------|-------|
| `constitutional_floors.json` | v42.1 | DEPRECATED | Pre-TEARFRAME consolidation (v44.0) |
| `genius_law.json` | v42.1 | DEPRECATED | Pre-v44 GENIUS LAW |
| `waw_prompt_floors.json` | v42.1 | DEPRECATED | Pre-v44 W@W config |
| `cooling_ledger_phoenix.json` | v42.0 | DEPRECATED | Pre-v44 memory config |

### spec/v43/ Subdirectory

| File | Version | Status | Notes |
|------|---------|--------|-------|
| `constitutional_floors.json` | v43.0 | DEPRECATED | Experimental; superseded by v44.0 |

---

## Loader Priority Order (v44.0)

All spec loaders follow this strict priority order (fail-closed by default):

### Default Behavior (Recommended)

```
A) ARIFOS_<SPEC>_SPEC env var (explicit operator override)
   └─ Example: ARIFOS_FLOORS_SPEC=/custom/path/floors.json

B) spec/v44/<spec_file>.json (AUTHORITATIVE)
   └─ Example: spec/v44/constitutional_floors.json

C) HARD FAIL (raise RuntimeError)
   └─ Clear error message guides operator to fix (ensure v44 exists)
```

### Legacy Fallback Mode (Opt-In)

If `ARIFOS_ALLOW_LEGACY_SPEC=1` is set (NOT RECOMMENDED), loaders fall back to:

```
C) spec/v42/<spec_file>.json (if exists)
D) spec/<spec_file>_v38Omega.json (if exists)
E) spec/<spec_file>_v35Omega.json (if exists)
F) Hardcoded defaults (last resort)
```

---

## Environment Variables

### Primary Authority Control

| Variable | Purpose | Example |
|----------|---------|---------|
| `ARIFOS_FLOORS_SPEC` | Override constitutional floors spec path | `/path/to/custom_floors.json` |
| `ARIFOS_PHYSICS_SPEC` | Override session physics spec path | `/path/to/custom_physics.json` |
| `ARIFOS_GENIUS_SPEC` | Override GENIUS LAW spec path | `/path/to/custom_genius.json` |

### Fallback Control

| Variable | Default | Purpose |
|----------|---------|---------|
| `ARIFOS_ALLOW_LEGACY_SPEC` | `0` (OFF) | Enable legacy fallback to v42/v38/v35/hardcoded |

**Usage:**
```bash
# Enable legacy fallback (NOT RECOMMENDED for production)
export ARIFOS_ALLOW_LEGACY_SPEC=1

# Use custom spec override (recommended for testing)
export ARIFOS_FLOORS_SPEC=/path/to/test_floors.json
```

---

## Migration Guide

### For Operators

**If you have custom spec overrides:**

1. **Option A (Recommended):** Copy your custom values to spec/v44/ files
   ```bash
   cp my_custom_floors.json spec/v44/constitutional_floors.json
   ```

2. **Option B:** Use environment variable override
   ```bash
   export ARIFOS_FLOORS_SPEC=/path/to/my_custom_floors.json
   ```

3. **Option C (Not Recommended):** Enable legacy fallback
   ```bash
   export ARIFOS_ALLOW_LEGACY_SPEC=1
   ```

**If you rely on legacy spec files:**

- Runtime will HARD FAIL if spec/v44/ is missing (unless legacy fallback enabled)
- To preserve old behavior temporarily: `export ARIFOS_ALLOW_LEGACY_SPEC=1`
- Permanent fix: Migrate custom values to spec/v44/ files

### For Developers

**If you have tests that load legacy specs:**

1. Tests that verify legacy fallback behavior: Enable `ARIFOS_ALLOW_LEGACY_SPEC=1` in test setup
2. Tests that verify v44 authority: No changes needed (default behavior)
3. Tests that verify hard-fail: No changes needed (default behavior)

**If you modify specs:**

- ✅ Edit spec/v44/ files (authoritative)
- ❌ Do NOT edit legacy spec files (deprecated)

---

## Why v44.0 Consolidation?

**Problem (pre-v44):**
- Multiple spec versions (v35Omega, v38Omega, v42) created ambiguity
- Shadow defaults hardcoded in Python modules (drift risk)
- Silent fallback behavior made debugging difficult

**Solution (v44.0):**
- **Single source of truth:** spec/v44/ is supreme authority
- **Fail-closed by default:** Missing spec → clear error (not silent fallback)
- **Explicit legacy support:** Legacy fallback available via opt-in switch
- **No shadow defaults:** All thresholds loaded from spec (including new session_physics.json)

**Benefits:**
- Clear spec authority (no ambiguity)
- Easier debugging (know exactly which spec is loaded)
- Safer deployments (hard-fail prevents drift)
- Governance alignment (Track A Canon → Track B Spec → Track C Code)

---

## Track A vs Track B vs Track C

**Governance Hierarchy:**

```
Track A (Canon) > Track B (Spec) > Track C (Code)
```

| Track | Location | Authority | Mutability |
|-------|----------|-----------|------------|
| **Track A** | `L1_THEORY/canon/` | Constitutional interpretation | Immutable (except Phoenix-72 amendments) |
| **Track B** | `spec/v44/` | Machine-readable thresholds | Tunable (operator override) |
| **Track C** | `arifos_core/` | Implementation | Follows Track B |

**Rule:** Track B (spec/v44/) is the **SOLE RUNTIME AUTHORITY** for tunable thresholds. Track A (canon) defines interpretation; Track B defines thresholds; Track C implements.

---

## Questions?

**Q: Why are legacy specs retained if they're deprecated?**
A: Backward compatibility, historical reference, and legacy test cases. They do NOT affect runtime unless `ARIFOS_ALLOW_LEGACY_SPEC=1` is set.

**Q: Can I delete legacy spec files?**
A: Not recommended. They serve as historical reference and enable legacy fallback mode. Disk space cost is minimal (~100KB).

**Q: What if spec/v44/ is missing?**
A: Runtime will HARD FAIL with clear error message (unless `ARIFOS_ALLOW_LEGACY_SPEC=1` is set).

**Q: How do I test with custom thresholds?**
A: Use environment variable override: `export ARIFOS_FLOORS_SPEC=/path/to/custom.json`

**Q: When should I use legacy fallback mode?**
A: Only during migration or testing. NOT RECOMMENDED for production. Permanent fix: migrate to spec/v44/.

---

**Version:** v44.0
**Created:** 2025-12-25
**Authority:** Track B Spec Consolidation (TEARFRAME)
**Governance:** DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
