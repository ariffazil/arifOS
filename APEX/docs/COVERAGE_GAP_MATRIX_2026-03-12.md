# Coverage Gap Matrix — 2026-03-12

This matrix labels recent coverage and risk claims against the current
`C:\arifosmcp` checkout.

Legend:
- `VERIFIED` — direct repo evidence
- `ESTIMATE ONLY` — heuristic or forecast, not repo-derived
- `FALSE` — contradicted by repo state
- `UNKNOWN` — no direct evidence either way

## Projection Audit

| Claim | Status | Evidence |
| --- | --- | --- |
| Current global coverage is `39%` | `ESTIMATE ONLY` | Coverage is configured in `pyproject.toml`, but this checkout did not yield a clean coverage artifact during audit. |
| P0 work gets coverage to `50-55%` in 7 days | `ESTIMATE ONLY` | Planning heuristic; not derivable from current repo state alone. |
| P0+P1 gets coverage to `68-78%` in 30 days | `ESTIMATE ONLY` | Planning heuristic; not derivable from current repo state alone. |
| Canonical floor module is `core/floors.py` | `FALSE` | Current canonical floor implementation is `core/shared/floors.py`. |
| P0 tests still need to be invented | `FALSE` | Ordered tests already exist in `tests/adversarial/judicial_orders/test_p0_orders.py`. |
| Physics is disabled everywhere in tests | `FALSE` | Test harness defaults physics off, but adversarial suites explicitly force physics on. |
| Physics is disabled by default in most tests | `VERIFIED` | `tests/conftest.py` sets `ARIFOS_PHYSICS_DISABLED=1` by default. |
| AKI boundary was under-tested | `VERIFIED` | A direct test module has now been added for `AKIContract`, `SovereignGate`, and `L0KernelGatekeeper`. |
| Existing VAULT coverage was mostly helper/replay level | `VERIFIED` | The repo now includes record/ledger verification helpers plus a tamper-blocking `trace_replay` path, but not a full quarantine flow. |

## Critical Path Snapshot

### `core/shared/floors.py`

Status: `PATCHED P0`

Direct explicit floor tests present:
- `F1` in `tests/test_constitutional_core.py`
- `F2` in `tests/test_constitutional_core.py` and `tests/adversarial/test_p3_hardening.py`
- `F4` in `tests/test_constitutional_core.py`
- `F7` in `tests/adversarial/test_p3_hardening.py`
- `F9` in `tests/adversarial/test_p3_hardening.py`
- `F11` in `tests/adversarial/test_p3_hardening.py`
- `F12` in `tests/test_constitutional_core.py`, `tests/adversarial/test_p3_hardening.py`, and `tests/adversarial/judicial_orders/test_p0_orders.py`
- `F13` threshold and signature-path coverage in `tests/test_constitutional_core.py` and `tests/adversarial/judicial_orders/test_p0_orders.py`

Patch action:
- direct tests added in `tests/core/test_floor_gap_paths.py`

### `core/enforcement/aki_contract.py`

Status: `PATCHED P0`

Boundary objects:
- `AKIContract`
- `SovereignGate`
- `L0KernelGatekeeper`

Gap prior to patch:
- no direct test file targeting this module

Patch action:
- direct boundary tests added in `tests/core/test_aki_contract.py`

### VAULT integrity path

Status: `PATCHED P0`

Verified current coverage:
- `merkle_root` helper checks in `tests/test_constitutional_core.py`
- replay-path checks in `tests/test_trace_replay.py`
- conceptual tamper mismatch check in `tests/adversarial/judicial_orders/test_p0_orders.py`
- record and ledger verification helpers in `tests/core/test_vault_integrity.py`
- tamper-blocking replay path in `tests/test_trace_replay.py`

Remaining gap:
- no verified end-to-end test that escalates a tampered ledger into a quarantine state beyond replay rejection

### `core/physics/thermodynamics_hardened.py`

Status: `STRONGER THAN CLAIMED`

Verified adversarial coverage includes:
- Landauer violations
- entropy increase rejection
- budget exhaustion
- cheap-truth hardening

Primary evidence:
- `tests/adversarial/test_p3_hardening.py`
- `tests/adversarial/judicial_orders/test_p0_orders.py`

## Adversarial Coverage Map

### `tests/adversarial/test_p3_hardening.py`

Verified direct focus:
- `F2`
- `F7`
- `F9`
- `F11`
- `F12`
- Landauer / thermodynamic budget enforcement
- outcome ledger / post-action accountability

### `tests/adversarial/judicial_orders/test_p0_orders.py`

Verified direct focus:
- `F1`
- `F12`
- `F13`
- cheap-truth thermodynamic rejection
- merkle mismatch detection

## Next P0 Additions

Highest-value remaining tests:
1. A runtime integration test proving vault integrity failure triggers a hard degraded, hold, or quarantine behavior beyond replay rejection.
2. A targeted coverage run for critical files only, once the local Python import/test contention is cleaned up.
