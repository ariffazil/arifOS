# Architecture Hardening Phase 1 (2026-03-06)

## Implemented

- Canonical L5 composite naming is now `metabolic_loop` in `arifosmcp.transport/server.py`.
- Legacy compatibility is preserved with a non-canonical Python alias:
  `metabolicloop -> metabolic_loop`.
- Contract alias mapping added in `arifosmcp.transport/protocol/aaa_contract.py`:
  `"metabolicloop": "metabolic_loop"`.
- New boundary guardrail tests added in `tests/canonical/test_architecture_boundaries_contract.py`:
  - AST-only import checks enforce that `core/` does not import transport/surface roots
    (`fastmcp`, `fastapi`, `starlette`, `arifosmcp.transport`, `arifosmcp.runtime`).
  - L5 composite contract is pinned to exactly `{"metabolic_loop"}` to prevent naming drift.

## Phase 2 Remaining

- Extend boundary checks to cover additional architectural seams (e.g., transport->core call shape).
- Add stronger runtime contract checks for alias behavior across all exposed entrypoints.
- Integrate these guardrails into broader CI quality gates (lint/type/test bundles).
