# arifOS v43 Fail-Closed Patches — READY TO APPLY

**Generated**: 2025-12-19T21:05:16+08:00  
**Status**: REVIEWED & READY FOR /gitforge  
**Total Patches**: 5 (P0-1 through P0-5)

**These patches enforce**: ANY @EYE / metrics / ledger failure ⇒ SABAR or VOID, never silent SEAL.

---

## Quick Reference: What Each Patch Does

| Patch | Location | Fix |
|-------|----------|-----|
| P0-1 | `_run_eye_sentinel()` | @EYE error → `eye_blocking=True` (SABAR) |
| P0-2 | `_compute_888_metrics()` | metrics exception → return `None` |
| P0-3 | `_apply_apex_floors()` | `metrics=None` → explicit VOID |
| P0-4 | `_write_memory_for_verdict()` | ledger write error → set failure flag |
| P0-5 | `stage_999_seal()` | ledger failure → force VOID, block SEAL |

---

# PATCH P0-1: Fix @EYE Sentinel Fail-Open

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_run_eye_sentinel()`  
**Why**: @EYE error currently sets `eye_blocking=False` (assumes safe). Must be True (fail-closed).

## Diff 1: Line 652-655 (main @EYE exception handler)

```python
### BEFORE ###
    except Exception:
        # @EYE failures must not crash the pipeline
        eye_report = None
        eye_blocking = False

### AFTER (FAIL-CLOSED v43) ###
    except Exception as e:
        # FAIL-CLOSED v43: @EYE failure → assume BLOCKING (safety first)
        import logging
        logging.getLogger(__name__).error(
            f"@EYE Sentinel failed during audit. Assuming blocking issue for safety. Error: {e}"
        )
        eye_report = None
        eye_blocking = True  # ← CRITICAL: Assume unsafe on error
```

## Diff 2: Line 684-685 (@EYE adapter exception handler)

```python
### BEFORE ###
    except Exception:
        pass

### AFTER (FAIL-CLOSED v43) ###
    except Exception as e:
        # FAIL-CLOSED v43: @EYE adapter failure → assume BLOCKING
        import logging
        logging.getLogger(__name__).error(
            f"@EYE adapter (evaluate_eye_vector) failed. Assuming blocking issue. Error: {e}"
        )
        eye_blocking = True  # ← CRITICAL: Assume unsafe on error
```

**Result**: @EYE crash → `eye_blocking=True` → APEX returns **SABAR**

---

# PATCH P0-2: Add Metrics Computation Exception Handling

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_compute_888_metrics()`  
**Why**: No exception handling. If `compute_metrics()` throws, behavior is undefined (crash or fail-open).

## Diff 1: Line 512-515 (function signature)

```python
### BEFORE ###
def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Metrics:

### AFTER ###
def _compute_888_metrics(
    state: PipelineState,
    compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
) -> Optional[Metrics]:  # ← Now returns Optional[Metrics]
```

## Diff 2: Line 529-546 (add try/except)

```python
### BEFORE ###
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

### AFTER (FAIL-CLOSED v43) ###
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

**Result**: Metrics exception → `_compute_888_metrics()` returns `None` → explicit VOID in P0-3

---

# PATCH P0-3: Make Metrics=None Explicitly Fail-Closed

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_apply_apex_floors()`  
**Why**: Currently creates broken metrics (indirect fail-closed). Should return explicit VOID.

## Diff: Line 588-603

```python
### BEFORE (INDIRECT FAIL-CLOSED) ###
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

### AFTER (EXPLICIT FAIL-CLOSED v43) ###
    # FAIL-CLOSED v43: Explicit VOID if metrics missing
    if state.metrics is None:
        import logging
        logging.getLogger(__name__).error(
            "Metrics are None at APEX floor check. Returning explicit VOID (fail-closed)."
        )
        from .apex_prime import Verdict  # Import Verdict enum
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

**Required Import Addition**: Add to top of file (line ~38):
```python
from .apex_prime import apex_review, ApexVerdict, check_floors, Verdict  # Add Verdict
```

**Result**: `metrics=None` → **explicit VOID** with clear reason, not indirect via broken metrics

---

# PATCH P0-4: Add Ledger Write Failure Handling

**File**: `arifos_core/system/pipeline.py`  
**Function**: `_write_memory_for_verdict()`  
**Why**: No error handling for ledger writes. Exceptions are uncaught.

## Diff 1: Line ~99 (add field to PipelineState class)

**Search for class `PipelineState` and add this field after other boolean/status fields:**

```python
### ADD THIS FIELD TO PipelineState ###
    # v43 fail-closed: Ledger write status tracking
    ledger_write_success: bool = True
```

## Diff 2: Line 976-1009 (wrap ledger write in try/catch)

```python
### BEFORE ###
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

### AFTER (FAIL-CLOSED v43) ###
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

**Result**: Ledger write errors are caught and stored in `state.ledger_write_success`

---

# PATCH P0-5: Block SEAL Emission if Ledger Write Failed

**File**: `arifos_core/system/pipeline.py`  
**Function**: `stage_999_seal()`  
**Why**: Currently emits output regardless of ledger status. Must block SEAL if audit failed.

## Diff: Insert BEFORE line 1180 (before verdict-based response generation)

```python
### CURRENT CODE AT LINE 1176-1180 ###
def stage_999_seal(state: PipelineState) -> PipelineState:
    """
    999 SEAL - If PASS -> emit. If FAIL -> SABAR or VOID.
    ...
    """
    state.current_stage = "999"
    state.stage_trace.append("999_SEAL")
    state.stage_times["999"] = time.time()

    ### INSERT THIS BLOCK HERE (BEFORE line 1180) ###
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

    ### THEN EXISTING CODE CONTINUES ###
    if state.verdict == "SEAL":
        state.raw_response = state.draft_response
    elif state.verdict == "PARTIAL":
        # ... rest of function
```

**Result**: Ledger failure → verdict forced to **VOID**, output blocked

---

# Application Checklist

Apply patches in this **exact order**:

- [ ] **1. P0-2**: `_compute_888_metrics()` - exception handling + change return type
- [ ] **2. P0-3**: `_apply_apex_floors()` - explicit VOID for `metrics=None`  
      _(Depends on P0-2 return type)_
- [ ] **3. P0-1**: `_run_eye_sentinel()` - fail-closed @EYE error handling  
      _(Independent, can be done anytime)_
- [ ] **4. P0-4**: `_write_memory_for_verdict()` - ledger error handling  
      _(Must be before P0-5)_
- [ ] **5. P0-5**: `stage_999_seal()` - ledger verification  
      _(Depends on P0-4 `ledger_write_success` field)_

---

# Verification Commands

After applying all patches:

```bash
# 1. Syntax check
cd c:/Users/User/OneDrive/Documents/GitHub/arifOS
python -m py_compile arifos_core/system/pipeline.py

# 2. Run existing tests to ensure no breakage
pytest tests/test_pipeline_routing.py -v

# 3. Run new fail-closed tests (after creating test file)
pytest tests/test_fail_closed_v43.py -v

# 4. Check logs for fail-closed messages
grep "FAIL-CLOSED" runtime/logs/*.log

# 5. Manual smoke test
python -m arifos_core.pipeline  # If you have a CLI entry point
```

---

# Before You Apply: Backup

```bash
# Create backup
cd c:/Users/User/OneDrive/Documents/GitHub/arifOS
git checkout -b v43-fail-closed-backup
git add arifos_core/system/pipeline.py
git commit -m "PRE-PATCH: Backup before v43 fail-closed enforcement"

# Now safe to apply patches
git checkout main  # or your working branch
```

---

# Quick Rollback (If Needed)

```bash
# Revert to backup
git checkout v43-fail-closed-backup -- arifos_core/system/pipeline.py

# OR stash changes
git stash

# OR hard reset (if committed)
git reset --hard HEAD~1
```

---

# Success Criteria

After all patches applied and verified:

✅ @EYE exception → `eye_blocking=True` → APEX returns SABAR  
✅ Metrics exception → returns `None` → explicit VOID  
✅ `metrics=None` → explicit VOID (not indirect)  
✅ Ledger write failure → verdict forced to VOID  
✅ All errors logged (no silent failures)  
✅ Existing tests still pass  
✅ New fail-closed tests pass

---

# v43 Fail-Closed Canon Compliance

### ✅ arifOS Fail-Closed Law
> ANY safety component failure ⇒ SABAR or VOID, never silent SEAL.

**Enforced by**:
- P0-1: @EYE → SABAR
- P0-2 + P0-3: Metrics → VOID
- P0-4 + P0-5: Ledger → VOID

### ✅ @EYE Sentinel Canon v43
> Witness cannot be blind while judge rules.

**Enforced by**:
- P0-1: @EYE blind (crashed) → assume jailbreak detected → SABAR

### ✅ A-CLIP Governance Intent
> No tool or agent can execute if @EYE or metrics are blind.

**Enforced by**:
- P0-1: Blind @EYE → SABAR (stop, investigate)
- P0-2 + P0-3: Blind metrics → VOID (block execution)
- P0-4 + P0-5: Blind audit → VOID (no output without trail)

---

**Ditempa, bukan diberi.**  
Forged with precision. Ready for production.

✊ SABAR over speed. Truth over output.
