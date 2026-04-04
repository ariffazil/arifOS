# v45 Sovereign Witness - Follow-up Tasks

**Status:** Tracked Technical Debt
**Epoch:** v45.0.0

## 1. Pydantic v2 Migration
*   **Context:** `EvidencePack` and `ApexTelemetry` currently use Pydantic v1 style `@validator`.
*   **Issue:** Pydantic v2 warns about deprecation.
*   **Task:** Migrate all validators to `@field_validator` (v2 native).
*   **Priority:** Low (Runtime compatible).

## 2. Receipt Serialization Hygiene
*   **Context:** `ProofOfGovernance` uses a polyfill `json.dumps(obj.dict(), ...)` to ensure deterministic hashing.
*   **Task:** Once Pydantic v2 is fully adopted, switch to `model_dump_json()` *if* it supports stable key sorting, or standardize on a custom JSON encoder that guarantees it.
*   **Priority:** Medium (Maintenance).

## 3. Missing Witness Policy Test
*   **Context:** PR-4 implementation of `WitnessCouncil` handles missing witnesses via quorum math (low agreement -> PARTIAL/HOLD).
*   **Task:** Add an explicit test case `test_missing_witness_policy` to `tests/judiciary/test_witness_council.py`.
- [ ] **Test Coverage**: Add test case for `missing_witness` policy in `tests/judiciary/test_witness_council.py`
- [ ] **QC Recalibration**: Recalibrate QC metric to distinguish "major release churn" vs "unsafe drift" (Post-v45).
- [ ] **Revert Variance**: Revert F2 DeltaS threshold in `qc.py` from 8.0 back to 5.0 after v45 stabilization..
*   **Requirement:** Verify that if N < 3 (or configured quorum), the system fails closed to `HOLD_888` or `PARTIAL` explicitly.
*   **Priority:** Medium (Stability Lock).
