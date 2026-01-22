# Phoenix-72 Guardrail Rollout Plan

**Status:** WARN mode (staged enforcement)
**Current Violations:** 426 threshold violations detected
**Deadline:** 2026-01-15 (transition to STRICT mode)
**Entropy Status:** PASSING (baseline enforced in STRICT mode)

---

## Summary

Phoenix-72 Guardrail is now active in **WARN mode** for threshold drift detection:

- **Threshold Check:** WARN mode (reports 426 violations, does not block CI)
- **Entropy Check:** STRICT mode (blocks on net LOC growth)

By **2026-01-15**, threshold check will transition to **STRICT mode** and block CI on violations.

---

## Current Violation Count: 426

Reduced from ~560 initial violations through scanner improvements:
- ✅ Multi-line docstring detection
- ✅ String literal filtering
- ✅ Public API file exclusion (__init__.py)
- ✅ Comment detection

Remaining violations are **real enforcement literals** in runtime code that need migration.

---

## Top 10 Offenders

| Rank | File | Violations | Category |
|------|------|------------|----------|
| 1 | `arifos_core/system/apex_prime.py` | 29 | Core judiciary |
| 2 | `arifos_core/integration/memory_scars.py` | 28 | Memory system |
| 3 | `arifos_core/enforcement/genius_metrics.py` | 22 | GENIUS metrics |
| 4 | `arifos_core/waw/prompt.py` | 18 | W@W federation |
| 5 | `arifos_core/waw/well.py` | 17 | W@W @WELL agent |
| 6 | `arifos_core/enforcement/metrics.py` | 14 | Floor metrics |
| 7 | `arifos_core/governance/fag.py` | 14 | File access gov |
| 8 | `arifos_core/system/verdict_emission.py` | 14 | Verdict output |
| 9 | `arifos_core/memory/eureka_receipt.py` | 13 | Memory receipts |
| 10 | `arifos_core/mcp/tools/mcp_222_reflect.py` | 12 | MCP tools |

---

## Migration Patterns

### Pattern 1: Import from Spec-Loaded Constants (PREFERRED)

**Before:**
```python
# arifos_core/system/apex_prime.py:195-199
PEACE_SQ_MIN = 1.0
KAPPA_MIN = 0.95
OMEGA_MIN = 0.03
OMEGA_MAX = 0.05
TRI_MIN = 0.95
```

**After:**
```python
from arifos_core.enforcement.metrics import (
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_MIN_THRESHOLD,
    OMEGA_MAX_THRESHOLD,
    TRI_WITNESS_THRESHOLD,
)

PEACE_SQ_MIN = PEACE_SQUARED_THRESHOLD  # 1.0 from spec/v44
KAPPA_MIN = KAPPA_R_THRESHOLD  # 0.95 from spec/v44
OMEGA_MIN = OMEGA_MIN_THRESHOLD  # 0.03 from spec/v44
OMEGA_MAX = OMEGA_MAX_THRESHOLD  # 0.05 from spec/v44
TRI_MIN = TRI_WITNESS_THRESHOLD  # 0.95 from spec/v44
```

**Note:** `apex_prime.py` already imports `TRUTH_THRESHOLD` correctly (line 26). Extend this pattern to other thresholds.

---

### Pattern 2: Add Spec Anchor Comments (WHEN IMPORT NOT AVAILABLE)

**Before:**
```python
# arifos_core/adapters/llm_claude.py:32
temperature: float = 0.3,
```

**After:**
```python
# Temperature default matches C_dark SEAL threshold (intentional)
temperature: float = 0.3,  # spec/v44/genius_law.json:43 (F9 C_dark SEAL)
```

**Use cases:**
- LLM adapter default parameters (temperature, top_p)
- API model validation bounds
- Test fixture thresholds
- Configuration defaults

---

### Pattern 3: Load from Spec JSON Dynamically

**Before:**
```python
# arifos_core/audit/eye_adapter.py:65-67
c_budi_thresholds = thresholds.get("c_budi", {"pass": 0.8, "partial_min": 0.6})
psi_audit_min = thresholds.get("psi_audit_min", 1.0)
```

**After:**
```python
from arifos_core.spec.loader import load_genius_spec

_genius_spec = load_genius_spec()  # Loads spec/v44/genius_law.json
c_budi_thresholds = _genius_spec["metrics"]["c_budi"]["thresholds"]
psi_audit_min = _genius_spec["vitality"]["threshold"]
```

**Use cases:**
- Derived metrics (G, C_dark, C_budi)
- Complex threshold structures
- Multi-level configurations

---

## Actionable Steps (Priority Order)

### Phase 1: Core Judiciary (Weeks 1-2)
**Target:** Reduce violations by 60% (426 → 170)

1. **apex_prime.py** (29 violations)
   - Import `PEACE_SQUARED_THRESHOLD`, `KAPPA_R_THRESHOLD`, `TRI_WITNESS_THRESHOLD` from metrics.py
   - Replace hardcoded floor thresholds on lines 195-199
   - Expected: -15 violations

2. **genius_metrics.py** (22 violations)
   - Load G, C_dark thresholds from `spec/v44/genius_law.json`
   - Use spec loader instead of hardcoded 0.80, 0.50, 0.30 values
   - Expected: -18 violations

3. **metrics.py** (14 violations)
   - Already uses spec loader; violations likely in fallback defaults
   - Add spec anchor comments to hardcoded fallbacks
   - Expected: -10 violations

### Phase 2: Memory & Integration (Weeks 3-4)
**Target:** Reduce violations by 20% (170 → 136)

4. **memory_scars.py** (28 violations)
   - Import floor thresholds for scar metadata
   - Expected: -20 violations

5. **eureka_receipt.py** (13 violations)
   - Import floor thresholds for receipt validation
   - Expected: -10 violations

### Phase 3: W@W Federation (Weeks 5-6)
**Target:** Reduce violations by 10% (136 → 122)

6. **waw/prompt.py** (18 violations)
   - Add spec anchor comments for prompt thresholds
   - Expected: -12 violations

7. **waw/well.py** (17 violations)
   - Import from metrics.py for floor checks
   - Expected: -10 violations

### Phase 4: Infrastructure (Weeks 7-8)
**Target:** Reduce violations by 10% (122 → <50)

8. **governance/fag.py** (14 violations)
9. **system/verdict_emission.py** (14 violations)
10. **mcp/tools/*.py** (12+ violations)
    - Systematic migration using Patterns 1-3
    - Expected: -70+ violations

---

## Testing Strategy

After each phase:

```bash
# Run guardrail to verify violation count decreased
python scripts/phoenix_72_guardrail.py --check thresholds --mode warn

# Verify tests still pass
pytest -xvs

# Check specific file was fixed
python scripts/phoenix_72_guardrail.py --check thresholds --mode strict 2>&1 | grep <filename>
```

---

## Transition to STRICT Mode

**Date:** 2026-01-15
**Target:** <50 violations remaining
**Action:** Update `.phoenix_config.json`:

```json
{
  "threshold_mode": "strict",
  "entropy_mode": "strict",
  "target_violation_max": 0,
  "deadline": "2026-01-15"
}
```

CI will then **block** on any remaining threshold violations.

---

## Configuration

Current `.phoenix_config.json`:
```json
{
  "threshold_mode": "warn",
  "entropy_mode": "strict",
  "target_violation_max": 50,
  "deadline": "2026-01-15"
}
```

**Local Development:**
```bash
# Check violations locally (warn mode)
python scripts/phoenix_72_guardrail.py --mode warn

# Test strict mode enforcement
python scripts/phoenix_72_guardrail.py --mode strict

# Update baseline after approved LOC growth
python scripts/phoenix_72_guardrail.py --update-baseline
```

---

## Success Metrics

- ✅ CI tests passing (WARN mode for thresholds, STRICT for entropy)
- ✅ Violation count tracked weekly
- ✅ Top 10 offenders reduced by 80% before deadline
- ✅ Zero entropy growth (net LOC stable or decreasing)
- ✅ 100% of new code uses spec-loaded constants

---

**DITEMPA BUKAN DIBERI** — Constitutional thresholds are forged from spec, not given by code.
