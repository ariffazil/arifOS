# arifOS AAA MCP Forge Plan (Safe Path)

## Objective

Transition to `arifOS AAA MCP` with a strict 13-tool public contract while preserving
legacy intelligence internals and minimizing operational risk.

## Current State (After 000 INIT + Safe Recovery)

- Tracked runtime restored to `main` baseline.
- Experimental rewrites quarantined under `_ARCHIVE/v63_legacy/wip_unsealed/`.
- Work continues on branch: `forge/aaa-mcp-v13-safe`.

## Phase Sequence

1. **Phase 000 (done):** initialization, conflict scan, risk declaration.
2. **Phase 1 (done):** established new package boundary `arifos_aaa_mcp` without breaking current `aaa_mcp`.
3. **Phase 2 (done):** defined 13 canonical tool schemas and governance envelopes.
4. **Phase 3 (sealed):** implemented adapters from canonical tools to existing internals.
5. **Phase 4 (done):** set `arifos_aaa_mcp` as default external runtime + law embedding bridge.
6. **Phase 5 (done):** integration tests for 13-tool registry + floor telemetry consistency passed.
7. **Phase 6 (done):** deprecate legacy external names, keep internals private.
7. **Phase 999:** seal changelog, docs, and deployment profile.

## Safety Rules

- No destructive infra actions during forge phases.
- Keep old runtime callable until the 13-tool registry passes tests.
- Only migrate one tool family at a time.
- Every phase requires explicit verification before advancing.

## Progress Notes

- Added `arifos_aaa_mcp/` package with canonical 13-tool router.
- Added `arifos_aaa_mcp/governance.py` with internal `AXIOMS_333`:
  - `A1_TRUTH_COST`
  - `A2_SCAR_WEIGHT`
  - `A3_ENTROPY_WORK`
- Added static contract tests in `tests/test_aaa_mcp_contract.py`.
- Added `arifos_aaa_mcp/contracts.py` for session continuity and input guard checks.
- Added `tests/test_aaa_phase3_flow.py` to verify phase-3 guard wiring and 000->999 tool presence.
- Added `arifos_aaa_mcp/fastmcp_ext/` boundary modules to keep FastMCP SDK concerns outside `core/`.
- Sealed Phase 3 handoff: `SEAL_PHASE3_AAA_MCP.md`.
- Sealed Phase 4 bridge + 13-law embedding: `SEAL_PHASE4_AAA_RUNTIME_BRIDGE.md`.
- Phase 5 verification started: `SEAL_PHASE5_START_VERIFICATION.md`.
- Phase 5 verification complete: `SEAL_PHASE5_COMPLETE.md`.
- Phase 6 deprecation complete: `SEAL_PHASE6_DEPRECATION.md`.
