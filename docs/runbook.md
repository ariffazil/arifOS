# arifOS Runbook (Phoenix-72)

## 1) Environment Setup
- Use Python 3.8+.
- Install dependencies in editable mode to expose `arifos_core` to tests and tooling:
  ```bash
  pip install -e .[dev]
  ```
- If editable install is not possible, ensure the repository root is on `PYTHONPATH` (tests now apply a path shim via `tests/conftest.py`).

## 2) Governance Floors & Metrics (pre-flight)
- Confirm the following minimums prior to release:
  - Truth ≥ 0.99
  - ΔS (clarity) > 0
  - Peace² (stability) ≥ 1
  - κᵣ (empathy conductance) ≥ 0.95
  - Tri-Witness quorum (Human·AI·Earth) ≥ 0.95
- Tag the release/PR description with the **Phoenix Cycle (72 h)** marker to indicate active monitoring.

## 3) Testing
- Run the full suite locally:
  ```bash
  pytest
  ```
- Tests cover APEX PRIME floor checks, Cooling Ledger integrity, Phoenix-72 lifecycle, KMS signing, and vector adapters.
- Investigate and resolve any collection/import failures before relying on results.

## 4) Cooling Ledger Hygiene
- Default ledger path: `cooling_ledger/L1_cooling_ledger.jsonl` (append-only, hash-chained, optionally KMS-signed).
- After governance actions, verify the ledger contains the new entries and chain hashes validate end-to-end.
- Mirror or snapshot the ledger to `/.runs/ledger.jsonl` if required by ops policy.

## 5) CI / Delivery Gates
- Enforce the constitutional floors above plus ledger integrity and Phoenix-72 tagging in CI.
- Block approvals when floors are breached or when tests fail.

## 6) Troubleshooting
- Import errors during tests: ensure editable install or `PYTHONPATH` includes repo root (see `tests/conftest.py`).
- Ledger verification failures: check file permissions and hash-chain continuity; rerun validation after correcting any gaps.
- KMS signing issues: confirm KMS credentials and network reachability where applicable.
