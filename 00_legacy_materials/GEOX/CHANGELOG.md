# Changelog — GEOX MCP Apps

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.0] — 2026-04-11
### Added
- **GEOX Command Center**: New vanilla HTML/CSS website for operator interfaces.
- **Operator Tooling**: Interactive pages for AC Risk, RATLAS, Basin Explorer, Seismic Viewer, and Well Context Desk.
- **System Metrics**: Real-time status panel with resource usage monitoring.
- **Lucide Icons & Tailwind v4**: Modern, dependency-free UI stack.
- **6 Integrated Web Apps**: Connected all GEOX tools to a unified visual dashboard.

## [0.5.0] — 2026-04-09
### Added
- **Modular Architecture**: Complete refactor into modular `arifos.geox` namespace.
- **Phase B Petrophysics**: 4 new tools (`geox_calculate_saturation`, `geox_select_sw_model`, `geox_compute_petrophysics`, `geox_validate_cutoffs`).
- **9 Prefab UI Views**: Interactive views for Seismic, Structural, Feasibility, and Petrophysics.
- **37 Tests**: Comprehensive test suite for petrophysics logic and schema validation.
- **App Manifest & Event Contracts**: Standardized Pydantic schemas for discovery and interaction.
- **OpenAI Adapter Blueprint**: Scaffold for ChatGPT Apps integration.

### Changed
- **geox_mcp_server.py**: Now a thin backward-compatible wrapper.
- **Tool Outputs**: Standardized on `{ "_view": ..., **data }` dual-mode format.
- **Wiki**: Updated to v0.5.0 standard with refined orchestration prompts.

## [0.1.0] — 2026-04-08
### Added
- Initial GEOX MCP Server with 7 tools.
- Theory of Anomalous Contrast (ToAC) documentation.
- 888_HOLD governance foundations.

---
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
