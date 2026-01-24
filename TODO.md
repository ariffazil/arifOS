# TODO: AAA MCP Reconstruction (v51 → v52)

## Phase 0: Foundation
- [ ] Safety Net: Git branch and tagging <!-- id: 0 -->
- [ ] Archive current `AAA_MCP/` to `archive/AAA_MCP_v51_backup/` <!-- id: 1 -->
- [ ] Identify all integration points and save to `refactoring/integration_points.json` <!-- id: 2 -->
- [ ] Run full test suite to establish baseline (`coverage run -m pytest`) <!-- id: 3 -->

## Phase 1: Bridge Purification
- [ ] Migrate `AAA_MCP/rate_limiter.py` to `arifos/core/governance/rate_limiter.py` <!-- id: 4 -->
- [ ] Purify `AAA_MCP/bridge.py` (Remove all logic) <!-- id: 5 -->
- [ ] Remove Spec Duplication (Consolidate to `arifos/core/spec/constitutional/`) <!-- id: 6 -->

## Phase 2: Version Consolidation
- [ ] Create `arifos/VERSION.lock` <!-- id: 7 -->
- [ ] Implement `arifos/version_validator.py` <!-- id: 8 -->
- [ ] CI Integration for Version Validator <!-- id: 9 -->

## Phase 3: Strategic Merge
- [ ] Migrate Transport Layer (server.py, sse.py, __main__.py to `arifos/mcp/`) <!-- id: 10 -->
- [ ] Create Mode Selector in `arifos/mcp/mode_selector.py` <!-- id: 11 -->
- [ ] Delete `AAA_MCP/` package <!-- id: 12 -->

## Phase 4: Production Hardening
- [ ] Implement Performance Metrics and Health Endpoint <!-- id: 13 -->

## Phase 5: Deployment
- [ ] Railway Configuration Update <!-- id: 14 -->
- [ ] Final Release Checklist and Tagging <!-- id: 15 -->
