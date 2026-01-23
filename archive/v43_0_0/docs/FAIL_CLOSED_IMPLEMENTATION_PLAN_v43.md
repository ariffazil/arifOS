# arifOS v43 Fail-Closed Implementation Plan  

**Date**: 2025-12-19T21:05:16+08:00  
**Status**: P0 CRITICAL - Immediate Implementation Required  
**Auditor**: Antigravity AGI CODER  
**Scope**: @EYE Sentinel + Metrics + Cooling Ledger Fail-Closed Enforcement

---

## Executive Summary

This plan implements **P0 fail-closed governance fixes** for arifOS v43 to ensure that **ANY** failure in safety-critical components (@EYE Sentinel, metrics computation, ledger writes) results in **SABAR or VOID**—never silent SEAL.

### Current State (AUDIT_FAIL_CLOSED_2025-12-19.md findings)

- ✅ **APEX PRIME** internally fail-closed (hard floor failures → VOID)
- 🚨 **@EYE error handling** fail-open (errors → `eye_blocking=False`)
- 🚨 **Metrics=None fallback** indirect fail-closed (should be explicit)
- ❓ **Ledger write failures** unknown behavior (potentially fail-open)

### Fail-Closed Law (v43 Canon)
>
> **ANY** safety component failure ⇒ System returns SABAR or VOID, **NEVER** silent SEAL.

---

## Critical Code Locations Discovered

### 1. @EYE Sentinel Invocation

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_run_eye_sentinel()`  
**Lines**: 606-687

**Current Behavior** (FAIL-OPEN):

```python
# Line 652-655
except Exception:
    # @EYE failures must not crash the pipeline
    eye_report = None
    eye_blocking = False  # ← ASSUMES SAFE on error
```

**Current Behavior** (FAIL-OPEN #2):

```python
# Line 684-685
except Exception:
    pass  # ← Silent failure in @EYE adapter
```

---

### 2. Metrics Computation

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_compute_888_metrics()`  
**Lines**: 512-556

**Current Behavior** (NO EXCEPTION HANDLING):

```python
# Line 529-534
if compute_metrics:
    metrics = compute_metrics(
        state.query,
        state.draft_response,
        {"stakes_class": state.stakes_class.value},
    )  # ← If this throws, pipeline crashes (undefined behavior)
```

**Function**: `_apply_apex_floors()`  
**Lines**: 589-594

**Current Behavior** (INDIRECT FAIL-CLOSED):

```python
# Line 589-594
if state.metrics is None:
    # Fallback: create empty metrics if somehow missing
    state.metrics = Metrics(
        truth=0.5,  # Below threshold → APEX returns VOID
        amanah=False,  # Hard floor fail → APEX returns VOID
        ...
    )
```

**Problem**: Relies on APEX catching broken metrics instead of explicit VOID.

---

### 3. Cooling Ledger Writes

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_write_memory_for_verdict()`  
**Lines**: 862-1010

**Current Behavior** (NO VERIFICATION):

```python
# Line 989-995
write_results = state.memory_band_router.route_write(...)

# Record in audit layer
if state.memory_audit_layer is not None:
    for band_name, result in write_results.items():
        if result.success:
            state.memory_audit_layer.record_memory_write(...)
```

**Problem**: No check if ledger write **fails**. If `route_write()` raises exception, it's **uncaught**.

**Function**: `stage_999_seal()`  
**Lines**: 1167-1243

**Current Behavior** (NO LEDGER VERIFICATION):

```python
# Line 1211
_write_memory_for_verdict(state, actor_role=ActorRole.ENGINE, ...)
# Line 1180-1208: Response is emitted regardless of ledger status
```

**Problem**: Output emitted even if ledger write fails.

---

## Files to Patch

### Priority Order (P0 → P1)

| Priority | File | Function | Issue |
|----------|------|----------|-------|
| **P0-1** | `pipeline.py` | `_run_eye_sentinel()` | @EYE error → fail-open |
| **P0-2** | `pipeline.py` | `_compute_888_metrics()` | No exception handling for `compute_metrics()` |
| **P0-3** | `pipeline.py` | `_apply_apex_floors()` | Indirect fail-closed (should be explicit VOID) |
| **P0-4** | `pipeline.py` | `_write_memory_for_verdict()` | No ledger write failure handling |
| **P0-5** | `pipeline.py` | `stage_999_seal()` | No ledger verification before SEAL emission |

---

## P0 Patches (Diffs Ready for Paste)

### P0-1: Fix @EYE Sentinel Fail-Open Error Handling

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_run_eye_sentinel()`  
**Lines**: 652-655 + 684-685

**BEFORE** (lines 652-655):

```python
    except Exception:
        # @EYE failures must not crash the pipeline
        eye_report = None
        eye_blocking = False
```

**AFTER** (FAIL-CLOSED):

```python
    except Exception as e:
        # FAIL-CLOSED v43: @EYE failure → assume BLOCKING (safety first)
        import logging
        logging.getLogger(__name__).error(
            f"@EYE Sentinel failed during audit. Assuming blocking issue for safety. Error: {e}"
        )
        eye_report = None
        eye_blocking = True  # ← FAIL-CLOSED: Assume unsafe on error
```

**BEFORE** (lines 684-685):

```python
    except Exception:
        pass
```

**AFTER** (FAIL-CLOSED):

```python
    except Exception as e:
        # FAIL-CLOSED v43: @EYE adapter failure → assume BLOCKING
        import logging
        logging.getLogger(__name__).error(
            f"@EYE adapter (evaluate_eye_vector) failed. Assuming blocking issue. Error: {e}"
        )
        eye_blocking = True  # ← FAIL-CLOSED: Assume unsafe on error
```

**Why Fail-Closed**:  

- @EYE Sentinel is the **witness** that must **never be blind** while judge (APEX) rules
- If @EYE crashes while scanning for jailbreaks/drift, we **assume jailbreak detected**
- Result: `eye_blocking=True` → APEX returns **SABAR**

---

### P0-2: Add Exception Handling for `compute_metrics()`

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_compute_888_metrics()`  
**Lines**: 529-546

**BEFORE**:

```python
    if compute_metrics:
        metrics = compute_metrics(
            state.query,
            state.draft_response,
            {"stakes_class": state.stakes_class.value},
        )
    else:
        # Stub metrics for testing
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )
```

**AFTER** (FAIL-CLOSED):

```python
    if compute_metrics:
        try:
            metrics = compute_metrics(
                state.query,
                state.draft_response,
                {"stakes_class": state.stakes_class.value},
            )
        except Exception as e:
            # FAIL-CLOSED v43: Metrics computation failure → return None
            # Will be caught in _apply_apex_floors() and turned into explicit VOID
            import logging
            logging.getLogger(__name__).error(
                f"Metrics computation failed. Will return explicit VOID. Error: {e}"
            )
            return None  # ← Signal failure to caller
    else:
        # Stub metrics for testing
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.2,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            rasa=True,
        )
```

**Change to function signature** (lines 512-515):

```python
def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Optional[Metrics]:  # ← Now returns Optional[Metrics]
```

**Why Fail-Closed**:  

- If metrics computation throws (LLM timeout, API error, etc.), we **return None**
- Explicit signal that metrics are unavailable → forces explicit VOID in next step

---

### P0-3: Make `_apply_apex_floors()` Explicitly Fail-Closed

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_apply_apex_floors()`  
**Lines**: 588-603

**BEFORE**:

```python
    # Get APEX verdict
    # Ensure metrics exist before passing (should always be set by stage 444)
    if state.metrics is None:
        # Fallback: create empty metrics if somehow missing
        state.metrics = Metrics(
            truth=0.5, delta_s=0.0, peace_squared=0.5, kappa_r=0.5,
            omega_0=0.05, psi=0.5, amanah=False, tri_witness=0.5
        )
    
    apex_verdict: ApexVerdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
    )

    return apex_verdict
```

**AFTER** (EXPLICIT FAIL-CLOSED):

```python
    # FAIL-CLOSED v43: Explicit VOID if metrics missing
    if state.metrics is None:
        import logging
        logging.getLogger(__name__).error(
            "Metrics are None at APEX floor check. Returning explicit VOID (fail-closed)."
        )
        return ApexVerdict(
            verdict=Verdict.VOID,
            pulse=0.0,
            reason="Metrics computation failed - refusing for safety (fail-closed)",
            floors=None,
        )
    
    # Get APEX verdict
    apex_verdict: ApexVerdict = apex_review(
        state.metrics,
        high_stakes=high_stakes,
        tri_witness_threshold=0.95,
        eye_blocking=eye_blocking,
    )

    return apex_verdict
```

**Required Import** (add to top of file if not present):

```python
from .apex_prime import apex_review, ApexVerdict, check_floors, Verdict  # Add Verdict here
```

**Why Fail-Closed**:  

- **No longer relies on APEX to catch broken metrics**
- **Explicit VOID** with clear reason: "Metrics computation failed"
- Transparent to auditors: ledger shows "fail-closed" reason

---

### P0-4: Add Ledger Write Failure Handling

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_write_memory_for_verdict()`  
**Lines**: 976-1009

**BEFORE**:

```python
    # Route write if allowed (and EUREKA routing did not DROP)
    if write_decision.allowed and eureka_decision_allowed:
        content = {
            "query_hash": hashlib.sha256(state.query.encode()).hexdigest()[:16],
            "verdict": verdict_str,
            "floor_checks_summary": {
                "passed": len([f for f in floor_checks if f.get("passed")]),
                "failed": len([f for f in floor_checks if not f.get("passed")]),
            },
            "stakes_class": state.stakes_class.value,
            "timestamp": timestamp,
        }

        write_results = state.memory_band_router.route_write(
            verdict=verdict_str,
            content=content,
            writer_id="888_JUDGE",
            evidence_hash=state.memory_evidence_hash,
            metadata={"job_id": state.job_id},
        )

        # Record in audit layer
        if state.memory_audit_layer is not None:
            for band_name, result in write_results.items():
                if result.success:
                    state.memory_audit_layer.record_memory_write(
                        band=band_name,
                        entry_data=content,
                        verdict=verdict_str,
                        evidence_hash=state.memory_evidence_hash,
                        entry_id=result.entry_id,
                        writer_id="888_JUDGE",
                        metadata={"job_id": state.job_id},
                    )
```

**AFTER** (FAIL-CLOSED with error propagation):

```python
    # Route write if allowed (and EUREKA routing did not DROP)
    if write_decision.allowed and eureka_decision_allowed:
        content = {
            "query_hash": hashlib.sha256(state.query.encode()).hexdigest()[:16],
            "verdict": verdict_str,
            "floor_checks_summary": {
                "passed": len([f for f in floor_checks if f.get("passed")]),
                "failed": len([f for f in floor_checks if not f.get("passed")]),
            },
            "stakes_class": state.stakes_class.value,
            "timestamp": timestamp,
        }

        try:
            write_results = state.memory_band_router.route_write(
                verdict=verdict_str,
                content=content,
                writer_id="888_JUDGE",
                evidence_hash=state.memory_evidence_hash,
                metadata={"job_id": state.job_id},
            )

            # FAIL-CLOSED v43: Check if any write failed
            write_success = False
            for band_name, result in write_results.items():
                if result.success:
                    write_success = True
                    # Record in audit layer
                    if state.memory_audit_layer is not None:
                        state.memory_audit_layer.record_memory_write(
                            band=band_name,
                            entry_data=content,
                            verdict=verdict_str,
                            evidence_hash=state.memory_evidence_hash,
                            entry_id=result.entry_id,
                            writer_id="888_JUDGE",
                            metadata={"job_id": state.job_id},
                        )
            
            # Store ledger write status for 999_SEAL check
            state.ledger_write_success = write_success
            
        except Exception as e:
            # FAIL-CLOSED v43: Ledger write exception → mark as failed
            import logging
            logging.getLogger(__name__).error(
                f"Ledger write failed with exception. Error: {e}"
            )
            state.ledger_write_success = False
    else:
        # Write not allowed by policy
        state.ledger_write_success = True  # Policy decision, not a failure
```

**Add to PipelineState** (line ~99, in PipelineState class fields):

```python
    # v43 fail-closed: Ledger write status tracking
    ledger_write_success: bool = True
```

**Why Fail-Closed**:  

- Captures **any** ledger write exception
- Stores success/failure in `state.ledger_write_success`
- 999_SEAL can check this before emitting output

---

### P0-5: Block SEAL Emission if Ledger Write Failed

**File**: `arifos_core/system/pipeline.py`  
**Function**: `stage_999_seal()`  
**Lines**: 1176-1211

**INSERT BEFORE line 1180** (before verdict-based response generation):

```python
    # FAIL-CLOSED v43: Block SEAL emission if ledger write failed
    if not getattr(state, 'ledger_write_success', True):
        # Ledger write failed - downgrade verdict to VOID
        import logging
        logging.getLogger(__name__).error(
            f"Ledger write failed for job {state.job_id}. "
            f"Original verdict was {state.verdict}, forcing VOID (fail-closed)."
        )
        state.verdict = "VOID"
        # Add to floor_failures for transparency
        state.floor_failures.append("LEDGER_WRITE_FAILED (fail-closed enforcement)")
        state.sabar_reason = "Ledger write failure - cannot emit governed output without audit trail"
```

**Full patch context** (lines 1176-1188):

```python
def stage_999_seal(state: PipelineState) -> PipelineState:
    """
    999 SEAL - If PASS -> emit. If FAIL -> SABAR or VOID.

    Final gate. All verdicts are immutably recorded.

    v38.1: Enhanced diagnostic messages for SABAR/VOID.
    v38.2-alpha: L7 Memory store with EUREKA Sieve (fail-open).
    v43: FAIL-CLOSED - blocks SEAL if ledger write failed.
    """
    state.current_stage = "999"
    state.stage_trace.append("999_SEAL")
    state.stage_times["999"] = time.time()

    # FAIL-CLOSED v43: Block SEAL emission if ledger write failed
    if not getattr(state, 'ledger_write_success', True):
        # Ledger write failed - downgrade verdict to VOID
        import logging
        logging.getLogger(__name__).error(
            f"Ledger write failed for job {state.job_id}. "
            f"Original verdict was {state.verdict}, forcing VOID (fail-closed)."
        )
        state.verdict = "VOID"
        # Add to floor_failures for transparency
        state.floor_failures.append("LEDGER_WRITE_FAILED (fail-closed enforcement)")
        state.sabar_reason = "Ledger write failure - cannot emit governed output without audit trail"

    if state.verdict == "SEAL":
        state.raw_response = state.draft_response
    # ... rest of function unchanged
```

**Why Fail-Closed**:  

- **No governed output without audit trail** (v43 Law)
- If ledger write fails, verdict is **forced to VOID**
- User sees explicit message: "Ledger write failure"
- Prevents silent SEAL when audit failed

---

## Minimal Test Plan

Create these test stubs to verify fail-closed behavior:

### Test File: `tests/test_fail_closed_v43.py`

```python
"""
Test suite for v43 fail-closed governance enforcement.

Verifies that ANY safety component failure → SABAR/VOID, never silent SEAL.
"""
import pytest
from arifos_core.pipeline import Pipeline, PipelineState
from arifos_core.enforcement.metrics import Metrics


class TestEyeSentinelFailClosed:
    """Verify @EYE failures result in SABAR/VOID, not SEAL."""
    
    def test_eye_sentinel_exception_blocks(self):
        """@EYE Sentinel exception → eye_blocking=True → SABAR."""
        from arifos_core.utils.eye_sentinel import EyeSentinel
        
        # Create a broken @EYE that raises exception
        class BrokenEye(EyeSentinel):
            def audit(self, *args, **kwargs):
                raise RuntimeError("@EYE crashed")
        
        pipeline = Pipeline(eye_sentinel=BrokenEye())
        state = pipeline.run("Test query")
        
        # Should be SABAR or VOID, never SEAL
        assert state.verdict in ("SABAR", "VOID"), \
            f"Expected SABAR/VOID on @EYE failure, got {state.verdict}"


class TestMetricsFailClosed:
    """Verify metrics computation failures result in VOID."""
    
    def test_metrics_exception_returns_void(self):
        """Metrics computation exception → explicit VOID."""
        def broken_metrics(query, response, context):
            raise RuntimeError("Metrics computation crashed")
        
        pipeline = Pipeline(compute_metrics=broken_metrics)
        state = pipeline.run("Test query")
        
        assert state.verdict == "VOID", \
            f"Expected VOID on metrics failure, got {state.verdict}"
        assert "fail-closed" in state.sabar_reason.lower() or \
               "metrics" in str(state.floor_failures).lower(), \
            "Verdict should mention metrics failure"
    
    def test_metrics_none_returns_void(self):
        """Metrics=None → explicit VOID (not indirect via broken metrics)."""
        # Directly test _apply_apex_floors with None metrics
        from arifos_core.pipeline import PipelineState, _apply_apex_floors
        
        state = PipelineState(query="test")
        state.metrics = None
        state.stakes_class = state.stakes_class  # Keep as CLASS_A
        
        verdict = _apply_apex_floors(state, eye_blocking=False)
        
        assert verdict.verdict.value == "VOID", \
            f"Expected explicit VOID for None metrics, got {verdict.verdict.value}"
        assert "fail-closed" in verdict.reason.lower() or \
               "metrics" in verdict.reason.lower(), \
            f"Reason should mention fail-closed or metrics: {verdict.reason}"


class TestLedgerFailClosed:
    """Verify ledger write failures block SEAL emission."""
    
    def test_ledger_write_failure_blocks_seal(self):
        """Ledger write failure → VOID, not SEAL."""
        # Create pipeline with broken memory router
        pipeline = Pipeline()
        state = pipeline.run("What is 2+2?")
        
        # Manually break ledger write status
        state.ledger_write_success = False
        state.verdict = "SEAL"  # Pretend APEX approved
        
        # Run 999_SEAL
        from arifos_core.pipeline import stage_999_seal
        state = stage_999_seal(state)
        
        assert state.verdict == "VOID", \
            f"Expected VOID when ledger fails, got {state.verdict}"
        assert "LEDGER_WRITE_FAILED" in state.floor_failures, \
            "Should have ledger failure in floor_failures"


# Run with: pytest tests/test_fail_closed_v43.py -v
```

### Minimal Manual Test Commands

```bash
# 1. Test @EYE failure
# Run pipeline with broken @EYE mock → should SABAR/VOID

# 2. Test metrics failure  
# Run pipeline with compute_metrics that raises → should VOID

# 3. Test ledger failure
# Break ledger path permissions → should VOID, not SEAL

# 4. Verify logs
# Check that errors are logged (not silent)
grep "FAIL-CLOSED" runtime/logs/*.log
```

---

## Rollback Plan

If patches cause issues:

### Quick Rollback (Git)

```bash
cd c:/Users/User/OneDrive/Documents/GitHub/arifOS
git stash  # Stash all changes
# OR
git checkout HEAD -- arifos_core/system/pipeline.py  # Revert pipeline.py only
```

### Manual Rollback

1. Remove `try/except` blocks added to `_compute_888_metrics()`
2. Change `eye_blocking = True` back to `eye_blocking = False` in `_run_eye_sentinel()`
3. Remove `ledger_write_success` checks from `stage_999_seal()`
4. Remove explicit VOID return in `_apply_apex_floors()`

### Verification After Rollback

```bash
pytest tests/test_pipeline_routing.py -v  # Core pipeline tests should pass
```

---

## Application Order

**CRITICAL**: Apply patches in this exact order:

1. **P0-2** first: `_compute_888_metrics()` exception handling
   - Changes function signature to return `Optional[Metrics]`
   - Must be done before P0-3

2. **P0-3** second: `_apply_apex_floors()` explicit VOID
   - Depends on P0-2 (expects `None` from metrics computation)

3. **P0-1** third: `_run_eye_sentinel()` fail-closed
   - Independent, can be done anytime

4. **P0-4** fourth: `_write_memory_for_verdict()` error handling
   - Adds `ledger_write_success` to state
   - Must be done before P0-5

5. **P0-5** fifth: `stage_999_seal()` ledger verification
   - Depends on P0-4 (`ledger_write_success` field)

---

## Success Criteria

After applying all P0 patches:

✅ **@EYE failure** → `eye_blocking=True` → APEX returns **SABAR**  
✅ **Metrics exception** → `_compute_888_metrics()` returns `None` → **explicit VOID**  
✅ **Metrics=None** → **explicit VOID** (not indirect via broken metrics)  
✅ **Ledger write failure** → **VOID** verdict, output blocked  
✅ **All errors logged** (not silent)  
✅ **Tests pass**: `pytest tests/test_fail_closed_v43.py -v`

---

## v43 Fail-Closed Canon Compliance

### @EYE Sentinel Canon v43

- ✅ **"Witness cannot be blind while judge rules"**
  - If @EYE fails → assume **blind witness** → **SABAR** (stop and investigate)

### arifOS Fail-Closed Law

- ✅ **"Any safety component failure ⇒ SABAR/VOID"**
  - @EYE fails → SABAR
  - Metrics fails → VOID
  - Ledger fails → VOID

### A-CLIP Governance Intent

- ✅ **"No tool or agent can execute if @EYE or metrics are blind"**
  - Enforced at 888_JUDGE (metrics) and 999_SEAL (ledger)

---

## Summary Diff Table

| File | Lines | Change | Old Behavior | New Behavior |
|------|-------|--------|--------------|--------------|
| `pipeline.py` | 652-655 | @EYE error handler | `eye_blocking=False` | `eye_blocking=True` + log |
| `pipeline.py` | 684-685 | @EYE adapter error | Silent pass | `eye_blocking=True` + log |
| `pipeline.py` | 529-546 | Metrics exception | Uncaught (crash) | Return `None` + log |
| `pipeline.py` | 512-515 | Function signature | `-> Metrics` | `-> Optional[Metrics]` |
| `pipeline.py` | 588-603 | Metrics=None handling | Indirect VOID | Explicit VOID + reason |
| `pipeline.py` | 976-1009 | Ledger write | No error handling | Try/catch + status flag |
| `pipeline.py` | ~99 | PipelineState field | - | Add `ledger_write_success` |
| `pipeline.py` | 1180 (insert) | 999_SEAL check | No check | Block SEAL if ledger failed |

---

**Ditempa, bukan diberi.** (Forged, not given.)  
Truth over speed. SABAR over silent failure.

✊ **Ready for /gitforge**.
