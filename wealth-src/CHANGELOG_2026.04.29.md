# WEALTH 2026.04.29 — Temporal Kernel Canonical Release

## [2026.04.29] - 2026-04-29
### Added
- **13 Sovereign Primitives**: Public surface redefined into doctrinal dimensions (Future Value, Present Expectation, Future Simulation, Info Value, Truth Validation, Survival Liquidity, Survival Leverage, Rule Enforcement, Allocate Optimization, Game Coordination, Sense Ingest, Past Record, Future Steward).
- **7 Civilizational Invariants**: Theoretical anchoring in Time, Uncertainty, Survival, Truth, Constraint, Coordination, and Boundaries.

### Changed
- **Architecture Migration**: Transitioned from a flat "tool zoo" (V1) and "namespace aliases" (V2) to a unified Temporal Kernel (2026.04.29).
- **Public MCP Surface**: Canonical runtime now exports only the 13 sovereign primitives; legacy alias names are no longer published as tools.
- **Isolation of Civilization Logic**: Moved all civilization stewardship functions to `wealth_future_steward`, removing them from liquidity and allocation logic.
- **Consolidated Balance Sheet**: `wealth_survival_leverage` now handles both DSCR and Net Worth (`networth_state`).
- **Engine Marking**: All legacy canonical functions marked as `# INTERNAL ENGINE — DO NOT EXPOSE PUBLICLY`.
- **Versioning Policy**: Switched from semantic versioning (v3) to chronological truth (2026.04.29).

### Removed
- **Redundant Primitives**: `wealth_state_balance` and `wealth_networth_state` (primitive) removed in favor of `wealth_survival_leverage` modes.
- **Redundant mcp.run calls**: Consolidated into a single hardened production entry point.

### Verified
- **Tool Count**: 13 canonical MCP tools.
- **Test Compliance**: Passed V2 Systemic Intelligence Suite (SIS: 1.0).
- **Safety**: No public alias layer remains in the canonical MCP export surface.
