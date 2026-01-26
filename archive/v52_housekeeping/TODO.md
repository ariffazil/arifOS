# TODO: AAA MCP Reconstruction (v51 → v52)

## Phase 0: Foundation
- [x] Safety Net: Git branch and tagging <!-- id: 0 -->
- [x] Archive current `AAA_MCP/` to `archive/AAA_MCP_v51_backup/` <!-- id: 1 -->
- [x] Identify all integration points and save to `refactoring/integration_points.json` <!-- id: 2 -->
- [x] Run full test suite to establish baseline (`coverage run -m pytest`) <!-- id: 3 -->

## Phase 1: Bridge Purification
- [x] Migrate `AAA_MCP/rate_limiter.py` to `arifos/core/governance/rate_limiter.py` <!-- id: 4 -->
- [x] Purify `AAA_MCP/bridge.py` (Purified and moved to `arifos/mcp/bridge.py`) <!-- id: 5 -->
- [x] Remove Spec Duplication (Consolidated to `arifos/core/spec/constitutional/`) <!-- id: 6 -->

## Phase 2: Version Consolidation
- [x] Create `arifos/VERSION.lock` <!-- id: 7 -->
- [x] Implement `arifos/version_validator.py` <!-- id: 8 -->
- [x] CI Integration for Version Validator <!-- id: 9 -->

## Phase 3: Strategic Merge
- [x] Migrate Transport Layer (server.py, sse.py, __main__.py to `arifos/mcp/`) <!-- id: 10 -->
- [x] Create Mode Selector in `arifos/mcp/mode_selector.py` <!-- id: 11 -->
- [x] Delete `AAA_MCP/` package <!-- id: 12 -->

## Phase 4: Production Hardening
- [x] Implement Performance Metrics and Health Endpoint <!-- id: 13 -->

## Phase 5: Deployment
- [x] Railway Configuration Update <!-- id: 14 -->
- [x] Final Release Checklist and Tagging <!-- id: 15 -->