# conformance/README.md — Negative Conformance Suite

> **WAJIB 1** — Every "must never happen" becomes a test.
> **DITEMPA BUKAN DIBERI.**

## Running

```bash
cd /root/arifOS
PYTHONPATH=. pytest conformance/ -q --tb=short
```

## Structure

```
conformance/
├── __init__.py              # Helpers (_call_tool, _init_session)
├── conftest.py              # Pytest config + kernel health fixture
├── kernel/
│   └── test_authority.py    # Tests 1-4: Authority + kernel state
├── execution/
│   └── test_mutation_gates.py  # Tests 5-8: Execution safety
├── delegation/
│   └── test_authority_attenuation.py  # Tests 9-11: Delegation safety
├── verification/
│   └── test_independent_verifier.py   # Tests 12-13: Verification
├── memory/
│   └── test_memory_integrity.py       # Tests 14-15: Memory safety
├── organs/
│   └── test_organ_boundaries.py       # Tests 16-18: Organ safety
├── deferred/
│   └── test_fire_time_reauth.py       # Deferred execution stubs
└── fixtures/                # Test data (future)
```

## The 18 Must-Never-Happen Tests

| # | Test | Status |
|---|------|--------|
| 1 | Model cannot grant itself authority | ✅ implemented |
| 2 | Executor cannot approve its own execution | ✅ implemented |
| 3 | Unleased mutation fails closed | ✅ implemented |
| 4 | Kernel state not self-contradictory | ✅ implemented |
| 5 | Command success ≠ outcome verification | ✅ implemented |
| 6 | A-FORGE cannot verify itself | ✅ implemented |
| 7 | No mutation without session | ✅ implemented |
| 8 | Sealed execution requires lease | ✅ implemented |
| 9 | Child authority ≤ parent | ✅ implemented |
| 10 | Expired delegation denied | ✅ implemented |
| 11 | Missing lineage denied | ✅ implemented |
| 12 | Evidence without provenance rejected | ✅ implemented |
| 13 | Confidence without uncertainty rejected | ✅ implemented |
| 14 | Memory cannot be silently modified | ✅ implemented |
| 15 | VAULT999 rejects unsigned events | ✅ implemented |
| 16 | Tool count ≠ AGI evidence | ✅ implemented |
| 17 | Human approval cannot be simulated | ✅ implemented |
| 18 | Organ conflict cannot silently resolve | ✅ implemented |

## WAJIB 3: Kernel State Normalization

The contradiction is documented at `session.py:554-568`. Fix plan:
1. Create one canonical `effective_state` block
2. All other authority fields derive from it
3. No field can report stronger authority than `effective_state`

**SOT:** 2026-07-19 | **seal_seq:** —