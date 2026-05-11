# CHANGELOG

All notable changes to the arifOS project will be documented in this file.
DITEMPA BUKAN DIBERI.

## [2026.04.20] - THE NEXT HORIZON (Sovereign Kernel)

### Added
- **13-Tool Canonical Horizon**: Forged the complete metabolic and sovereign toolset (000–999).
- **Single Execution Spine (SES)**: Implemented `governance.py` in `runtime/` to enforce F1–F13 Floors on all tool calls.
- **Thermodynamic Vitality Harness**: Deployed `vitality.py` and `verify_arifos_tools.py` for closed-loop metabolic auditing.
- **Dynamic Tool Registry**: Implemented `registry.py` for auto-discovery of plane-based intelligence organs.
- **Distilled Intelligence Map**: Formalized the "Observer Frame", "Blind Bridge", and "Tri-Witness" invariants.
- **FORGET Ledger**: Established a protocol for archiving obsolete logic while preserving distilled structural eureka.
- **State-Active Sovereign Kernel v0.2**: Added `runtime/state.py` with metabolic states, identity continuity, witness tracking, autonomy caps, archive-to-vault behavior, and A-FORGE runtime contract emission.

### Changed
- **Naming Migration**: Standardized all MCP tool names from dotted notation (`arifos.000_init`) to underscore-only naming (`arifos_000_init`).
- **Plane Partitioning**: Reorganized tools into `control_plane`, `witness_plane`, `compute_plane`, and `execution_plane`.
- **Package Unification**: Consolidated all arifOS MCP logic into the canonical `arifosmcp/` repository structure.
- **Absolute Imports**: Refactored the entire codebase to use sovereign package routing.
- **Public MCP Surface**: Canonical public surface is now the sealed NEXT HORIZON contract — 13 tools, 11 prompts, 3 resources — with compatibility endpoints restored on `mcp.arif-fazil.com`.
- **Local/VPS MCP Wiring**: Standardized stdio launches on `python -m arifosmcp.mcp_server` and added `python -m arifosmcp.runtime stdio` compatibility via `runtime/__main__.py`.

### Fixed
- **Judicial Registry Gap**: Resolved `ThermodynamicMetrics` naming drift (`aman_lock` -> `amanah_lock`).
- **Import Collisions**: Fixed `Relative Import Error` by enforcing absolute package paths.
- **Public MCP Proxy**: Repaired the `mcp.arif-fazil.com` reverse-proxy path and restored `/api/status`, `/api/telemetry`, `/tools`, and `/.well-known/mcp/server.json`.
- **Genesis Bootstrap**: `arifos_000_init` now boots the cognitive envelope with `identity_continuity = 1.0`, `metabolic_state = SENSING`, and `runtime_contract = arifos://forge/v2026.04.20`.

---

## [2026.04.17] - Hardening & Unification

### Added
- Initial deployment of `Vault-999` cryptographic ledger.
- Implementation of `PhysicsGuard` as a hard gate for FORGE operations.
- Cross-organ consensus (GEOX × WEALTH × WELL).

### Changed
- Refactored `init_app` and `judge_app` into the metabolic pipeline.
- Consolidated fragmented repositories into the `arifOS` main branch.

---

## [2026.04.05] - Genesis of arifOS MCP

### Added
- First sovereign kernel implementation.
- 13 Constitutional Floors (F1–F13) draft.
- Initial FastMCP wrapper for Ollama.
