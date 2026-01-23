# Fail-Closed Governance Audit Report

**Date**: 2025-12-19  
**Auditor**: Antigravity AI  
**Scope**: arifOS Fail-Closed Governance (Error Handling for Verdict Paths)  
**Repository**: c:\Users\User\OneDrive\Documents\GitHub\arifOS  
**Focus Files**: apex_prime.py, pipeline.py, floor detectors  

**Status**: ⚠️ MIXED - Some areas fail-closed, some areas RISKY

---

## Executive Summary (Human Language)

Arif, here's the plain-English status:

### **The Good News** ✅

The core verdict logic (apex_prime.py) **DOES fail-closed**. If an error happens during floor checks or GENIUS LAW evaluation, the system defaults to **VOID or PARTIAL**, NOT SEAL.

### **The Moderate Risk** ⚠️  

Pipeline error handling has **some fail-open risks** where exceptions are silently caught with `pass`, which COULD allow unsafe outputs if critical validation fails.

### **The Critical Finding** 🚨

**Line 589-594 in pipeline.py** has a **FALLBACK TO FAIL-OPEN**:

- If metrics computation fails (returns None)
- System creates **FAKE LOW-SECURITY METRICS**: `amanah=False, truth=0.5`
- Then passes these to APEX
- **APEX sees broken floors → returns VOID** ✅
- **BUT** this is an indirect fail-closed, not explicit

**Verdict**: System is **mostly fail-closed** but has weak spots.

---

## Detailed Findings

### Finding 1: APEX PRIME Verdict Logic (apex_prime.py)

**Lines**: 303-484  
**Function**: `apex_review()`  
**Status**: ✅ **FAIL-CLOSED** (SAFE)

#### How It Works

```python
# Line 361-369: Hard floor check
if not floors.hard_ok:
    return ApexVerdict(
        verdict=Verdict.VOID,  # ← FAIL-CLOSED: Returns VOID
        pulse=0.0,
        reason=reason,
        floors=floors,
    )
```

**Behavior**:

1. Checks all hard floors (Truth, ΔS, Amanah, etc.)
2. **If ANY fail** → Returns **VOID**
3. **No way to accidentally SEAL** if floors fail

**Exception Handling**:

```python
# Line 455-457: Import error fallback
except ImportError:
    # Fallback to v35 behavior if genius_metrics not available
    pass
```

**After exception**:

- Falls through to line 459-484 (v35 fallback)
- Still checks floors
- **Still returns VOID if floors fail**
- **SAFE**: Cannot return SEAL on error

---

### Finding 2: Pipeline Metrics Computation (_compute_888_metrics)

**Lines**: 512-556  
**Function**: `_compute_888_metrics()`  
**Status**: ⚠️ **PARTIAL RISK**

#### The Code

```python
# Line 529-546: Metrics computation
if compute_metrics:
    metrics = compute_metrics(...)  # External callback
else:
    # Stub metrics for testing
    metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        ...
        amanah=True,  # ← DEFAULT SAFE
    )
```

**Behavior**:

- If `compute_metrics` callback provided → Uses it
- If callback is **None** → Uses **SAFE STUB** (amanah=True, truth=0.99)
- **No explicit exception handling for compute_metrics() call**

**RISK**:

- What if `compute_metrics()` **throws an exception**?
- **Uncaught exception** → Pipeline crashes
- ❓ Does it crash-to-VOID or crash-to-undefined?

**Current State**: **UNKNOWN** - Need to test exception path

---

### Finding 3: Pipeline APEX Floor Application (_apply_apex_floors)

**Lines**: 559-603  
**Function**: `_apply_apex_floors()`  
**Status**: 🚨 **FAIL-OPEN RISK** (Line 589-594)

#### The Critical Code

```python
# Line 588-594: Fallback for missing metrics
if state.metrics is None:
    # Fallback: create empty metrics if somehow missing
    state.metrics = Metrics(
        truth=0.5,      # ← BELOW THRESHOLD (0.99 required)
        delta_s=0.0,    # ← AT THRESHOLD (OK)
        peace_squared=0.5,  # ← BELOW THRESHOLD (1.0 required)
        kappa_r=0.5,    # ← BELOW THRESHOLD (0.95 required)
        omega_0=0.05,   # ← AT THRESHOLD (OK)
        psi=0.5,        # ← BELOW THRESHOLD (1.0 required)
        amanah=False,   # ← FAILS HARD FLOOR
        tri_witness=0.5 # ← BELOW THRESHOLD (0.95 required)
    )
```

#### What This Means

1. **IF** metrics computation totally failed (returned None)
2. **THEN** system creates **FAKE BROKEN METRICS**
3. **These metrics WILL fail floors** (amanah=False, truth=0.5 < 0.99)
4. **APEX will see failed floors → return VOID**

**Is This Fail-Closed?**

- **Technically YES**: Fake metrics → fail floors → VOID
- **But indirectly**: Relies on APEX catching the low metrics
- **Not explicit**: Comment says "somehow missing" - shouldn't happen

**Better Approach**:

```python
if state.metrics is None:
    # EXPLICIT FAIL-CLOSED
    return ApexVerdict(
        verdict=Verdict.VOID,
        pulse=0.0,
        reason="Metrics computation failed - refusing for safety",
        floors=None,
    )
```

---

### Finding 4: Exception Handling in Pipeline Stages

**Location**: Multiple stage functions (111, 222, 555, etc.)  
**Pattern**: `try/except: pass`  
**Status**: ⚠️ **FAIL-OPEN RISK**

#### Examples

**Line 317-319 (stage_111_sense)**:

```python
except Exception:
    # Fail-open: L7 errors don't break pipeline
    pass
```

**Line 652-655 (_run_eye_sentinel)**:

```python
except Exception:
    # @EYE failures must not crash the pipeline
    eye_report = None
    eye_blocking = False  # ← NOT blocking on error
```

**Line 684-685 (@EYE adapter)**:

```python
except Exception:
    pass  # ← Silent failure
```

#### What Happens

1. Critical validation component fails (L7 memory, @EYE sentinel, etc.)
2. Exception silently caught
3. Pipeline continues **AS IF VALIDATION PASSED**
4. **No verdict downgrade** from SEAL to VOID

#### Is This Fail-Closed?

**NO** - This is **fail-open** (fail-permissive).

**Why It's Risky**:

- @EYE Sentinel is supposed to catch jailbreaks
- If @EYE **crashes** instead of running → `eye_blocking = False`
- Result: **Jailbreak might pass** when it should have been blocked

**Safer Pattern**:

```python
except Exception as e:
    # Log the error
    logger.error(f"@EYE Sentinel failed: {e}")
    # FAIL-CLOSED: Assume blocking issue
    eye_blocking = True
    eye_report = EyeReport(
        has_errors=True,
        error_message=str(e)
    )
```

---

### Finding 5: Pipeline Finalization (_finalize)

**Lines**: Not shown in scan (after line 1102)  
**Status**: ⚠️ **UNCERTAIN**

**What We Know**:

- From code search: `_finalize()` logs to ledger
- Handles verdict serialization
- Has fallback logic for verdict types

**Risk**:

- If ledger writing **fails**, does pipeline still emit the output?
- **Fail-open**: Output emitted even if audit failed
- **Fail-closed**: Output blocked if audit failed

**Need to verify**: Does ledger failure block the response?

---

## Summary Table: Fail-Closed Status

| Component | Location | Current Behavior | Status | Priority |
|-----------|----------|------------------|--------|----------|
| **APEX verdict logic** | apex_prime.py:361-369 | Hard floor fail → VOID | ✅ SAFE | - |
| **GENIUS LAW error** | apex_prime.py:455-457 | Import fail → v35 fallback → still checks floors | ✅ SAFE | - |
| **Metrics stub** | pipeline.py:536-546 | No callback → safe defaults | ✅ SAFE | - |
| **Metrics=None fallback** | pipeline.py:589-594 | Creates broken metrics → APEX returns VOID | ⚠️ INDIRECT | P0 |
| **L7 Memory error** | pipeline.py:317-319 | Silent fail → continue pipeline | 🚨 FAIL-OPEN | P1 |
| **@EYE error** | pipeline.py:652-655 | Silent fail → `eye_blocking=False` | 🚨 FAIL-OPEN | P0 |
| **@EYE adapter error** | pipeline.py:684-685 | Silent fail → continue | 🚨 FAIL-OPEN | P1 |
| **Ledger write error** | pipeline.py:_finalize | Unknown | ❓ VERIFY | P0 |

---

## Key Architectural Observations

### What's Good ✅

1. **APEX PRIME is solid**: Core judiciary logic fails-closed
2. **Floor checks are explicit**: No "default to SEAL" anywhere
3. **Verdict hierarchy is clear**: VOID \u003e SABAR \u003e 888_HOLD \u003e PARTIAL \u003e SEAL

### What's Risky 🚨

1. **Silent exception handling**: Many `except: pass` blocks
2. **Fail-permissive @EYE**: Error → assumes safe instead of unsafe
3. **Indirect fail-closed**: Relies on downstream catching problems
4. **No explicit "on error = VOID" policy**

---

## Recommended Actions (Priority Order)

### P0 - CRITICAL (Do First)

**1. Fix @EYE error handling** (Line 652-655, 684-685)

```python
# BEFORE (FAIL-OPEN):
except Exception:
    eye_blocking = False  # Assumes safe

# AFTER (FAIL-CLOSED):
except Exception as e:
    logger.error(f"@EYE failed: {e}")
    eye_blocking = True  # Assume unsafe on error
```

**2. Verify ledger write failure behavior**

- Test: Break ledger writing intentionally
- Check: Does output still get emitted?
- Fix: If yes, block output on ledger failure

**3. Make metrics=None explicitly fail-closed** (Line 589-594)

```python
# BEFORE (INDIRECT):
if state.metrics is None:
    state.metrics = Metrics(amanah=False, truth=0.5, ...)  # Broken metrics

# AFTER (EXPLICIT):
if state.metrics is None:
    return ApexVerdict(verdict=Verdict.VOID, reason="Metrics computation failed")
```

### P1 - HIGH (Do Second)

**4. Add error logging to silent failures**

```python
# BEFORE:
except Exception:
    pass

# AFTER:
except Exception as e:
    logger.warning(f"L7 Memory failed (non-critical): {e}")
    pass  # Still continue, but logged
```

**5. Document fail-closed guarantee**

- Add to SECURITY.md: "System fails-closed on errors"
- List exceptions (where fail-open is intentional)

### P2 - MEDIUM (Nice to Have)

**6. Add fail-closed tests**

```python
def test_metrics_error_fails_closed():
    """Verify that metrics computation error → VOID"""
    def failing_metrics(*args):
        raise RuntimeError("Metrics computation crashed")
    
    pipeline = Pipeline(compute_metrics=failing_metrics)
    state = pipeline.run("test query")
    
    assert state.verdict == "VOID", "Should VOID on metrics error"
```

---

## Current Verdict: MOSTLY FAIL-CLOSED ⚠️

**Overall Assessment**:

- **Core logic**: Fail-closed ✅
- **Error paths**: Mixed (some fail-open) ⚠️
- **Critical risk**: @EYE error handling 🚨

**Recommendation**: **FIX P0 items before production use**.

The system won't accidentally SEAL on floor failures, but it **MIGHT** miss jailbreaks if @EYE crashes.

---

## Files for Your Review

### apex_prime.py

**Line 303-484**: Core verdict logic (SAFE - fail-closed)  
**Line 455-457**: GENIUS LAW import error (SAFE - has fallback)

### pipeline.py

**Line 589-594**: Metrics=None fallback (⚠️ INDIRECT - should be explicit)  
**Line 652-655**: @EYE error handling (🚨 FAIL-OPEN - critical fix needed)  
**Line 684-685**: @EYE adapter error (🚨 FAIL-OPEN - critical fix needed)  
**Line 317-319**: L7 Memory error (⚠️ FAIL-OPEN - but L7 is non-critical)

---

**Next Step**: You review these specific lines, decide if P0 fixes are needed before production.

**Ditempa, bukan diberi.** Truth over speed. ✊
