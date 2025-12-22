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
*   **Requirement:** Verify that if N < 3 (or configured quorum), the system fails closed to `HOLD_888` or `PARTIAL` explicitly.
*   **Priority:** Medium (Stability Lock).
