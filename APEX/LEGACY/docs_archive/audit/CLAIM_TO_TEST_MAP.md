# Claim-to-Test Mapping

**Purpose:** Traceable evidence for every security/governance claim in the audit.
**Date:** 2026-02-02 | **Version:** v55.5

---

## Security Claims

| # | Claim | Test File | Test Case(s) | Expected Behavior | Status |
|---|-------|-----------|--------------|-------------------|--------|
| S1 | Prompt injection mitigated (F12) | `tests/constitutional/test_01_core_F1_to_F13.py` | `test_floor_exists_and_callable[F12-validate_f12_injection_defense]` | Validator exists and is callable | Wired |
| S2 | Prompt injection blocked (F12) | `tests/archive/deprecated_features/test_f12_injection.py` | Full test suite | Injection patterns detected, fail-closed | Archived (needs migration) |
| S3 | Ontology guard prevents confusion (F10) | `tests/constitutional/test_01_core_F1_to_F13.py` | `test_floor_exists_and_callable[F10-validate_f10_ontology]` | Validator exists and is callable | Wired |
| S4 | Ontology guard blocks claims (F10) | `tests/archive/deprecated_features/test_f10_ontology.py` | Full test suite | Consciousness claims blocked | Archived (needs migration) |
| S5 | Anti-Hantu blocks soul-claiming (F9) | `tests/constitutional/test_anti_hantu_f9.py` | `TestAntiHantuFloor::test_anti_hantu_false_marks_hard_failure` | anti_hantu=False -> VOID verdict | Active |
| S6 | Anti-Hantu EyeSentinel enforcement | `tests/constitutional/test_anti_hantu_f9.py` | `TestAntiHantuEyeSentinel::test_eye_sentinel_blocks_for_forbidden_pattern` | Forbidden phrases -> BLOCK alert | Active |
| S7 | Neutral text passes Anti-Hantu | `tests/constitutional/test_anti_hantu_f9.py` | `TestAntiHantuEyeSentinel::test_eye_sentinel_passes_for_neutral_text` | Clean text -> no alerts | Active |
| S8 | Command Auth verification (F11) | `tests/constitutional/test_01_core_F1_to_F13.py` | `test_floor_exists_and_callable[F11-validate_f11_command_auth]` | Validator exists and is callable | Wired |

## Governance Claims

| # | Claim | Test File | Test Case(s) | Expected Behavior | Status |
|---|-------|-----------|--------------|-------------------|--------|
| G1 | All 13 floor validators exist | `tests/constitutional/test_01_core_F1_to_F13.py` | `test_floor_exists_and_callable` (13 parameterized) | All validators importable and callable | Active |
| G2 | Aggregate validator exists | `tests/constitutional/test_01_core_F1_to_F13.py` | `test_validate_all_floors_exists` | `validate_all_floors` callable | Active |
| G3 | Full 000-999 pipeline runs | `tests/constitutional/test_pipeline_000_to_999_comprehensive.py` | Full pipeline test | Stages execute in order | Active |
| G4 | MCP tools respond to invocation | `tests/test_all_mcp_tools.py` | Tool-specific tests | Each tool returns expected schema | Active |
| G5 | Constitutional MCP integration | `tests/integration/test_complete_mcp_constitutional.py` | End-to-end tests | Full constitutional pass-through | Active |
| G6 | APEX 888 judgment pipeline | `tests/constitutional/test_apex_room_888_pipeline.py` | 888 pipeline tests | Paradox equilibrium computed | Active |

## Gaps Requiring New Tests

| # | Missing Claim | Proposed Test | Priority |
|---|---------------|---------------|----------|
| GAP-1 | Role confusion prevention | `tests/constitutional/test_role_boundary.py` | P1 |
| GAP-2 | Governance bypass resistance | `tests/constitutional/test_bypass_attempt.py` | P1 |
| GAP-3 | F12 injection (active, not archived) | Migrate from `tests/archive/deprecated_features/test_f12_injection.py` | P0 |
| GAP-4 | F10 ontology (active, not archived) | Migrate from `tests/archive/deprecated_features/test_f10_ontology.py` | P0 |
| GAP-5 | MCP roundtrip lifecycle | `tests/integration/test_mcp_roundtrip.py` | P1 |
| GAP-6 | Schema validation enforcement | `tests/mcp/test_schema_enforcement.py` | P0 |

---

## How to Run Verification

```bash
# Run all mapped tests (active only)
pytest tests/constitutional/ -v
pytest tests/test_all_mcp_tools.py -v
pytest tests/integration/test_complete_mcp_constitutional.py -v

# Run just the security claim tests
pytest tests/constitutional/test_anti_hantu_f9.py -v
pytest tests/constitutional/test_01_core_F1_to_F13.py -v

# Generate coverage report
pytest tests/ -v --cov=codebase --cov-report=html
```

---

**Note:** Claims S2 and S4 have tests in the `archive/deprecated_features/` directory.
These tests should be migrated to active test directories to provide current CI coverage.
