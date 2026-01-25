# Changelog

All notable changes to the **arifOS** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v52.5.1] - 2026-01-25 "ATLAS Integration"

**Status:** SEALED (Constitutional Verified)
**Authority:** Muhammad Arif bin Fazil (888 Judge)

### 🧭 Major Feature: ATLAS-333 Lane Routing

Integrated GPV (Governance Placement Vector) routing into the metabolic pipeline. Every prompt is now classified into one of 4 lanes with lane-specific governance:

| Lane | Purpose | Verdict | Engines Activated |
|------|---------|---------|-------------------|
| 🚨 **CRISIS** | Life/safety at stake | 888_HOLD | APEX only (human confirm) |
| 📊 **FACTUAL** | Facts/logic needed | SEAL | Full Trinity (AGI+ASI+APEX) |
| 💚 **CARE** | Emotional support | SEAL | Heart-first (ASI+APEX) |
| 💬 **SOCIAL** | Casual chat | SEAL | Light touch (APEX only) |

### 🌡️ Thermodynamic Tuning (LANE_PROFILES)

Each lane now has dedicated thermodynamic parameters:

```python
LANE_PROFILES = {
    "CRISIS":  {"S_factor": 0.5, "omega_0": 0.05, "energy": 1.0, "time_budget": 180},
    "FACTUAL": {"S_factor": 0.6, "omega_0": 0.03, "energy": 0.9, "time_budget": 90},
    "CARE":    {"S_factor": 0.7, "omega_0": 0.04, "energy": 0.7, "time_budget": 60},
    "SOCIAL":  {"S_factor": 0.8, "omega_0": 0.03, "energy": 0.5, "time_budget": 15},
}
```

### ⚙️ Selective Engine Activation (LANE_ENGINES)

Engines now activate selectively based on lane requirements:

```python
LANE_ENGINES = {
    "CRISIS":  {"AGI_Mind": "IDLE",  "ASI_Heart": "IDLE",  "APEX_Soul": "READY"},
    "FACTUAL": {"AGI_Mind": "READY", "ASI_Heart": "READY", "APEX_Soul": "READY"},
    "CARE":    {"AGI_Mind": "IDLE",  "ASI_Heart": "READY", "APEX_Soul": "READY"},
    "SOCIAL":  {"AGI_Mind": "IDLE",  "ASI_Heart": "IDLE",  "APEX_Soul": "READY"},
}
```

### ⏸️ 888_HOLD Verdict

New verdict type for high-stakes situations:
- **Trigger:** CRISIS lane detection (life, safety, irreversible harm)
- **Behavior:** Pauses execution, requires explicit human confirmation
- **Location:** After Step 3 in 000_init flow

### 🛡️ Constitutional Compliance

- **F7 Verified:** All `omega_0` values within constitutional bounds [0.03, 0.05]
- **Test Coverage:** All 4 lanes tested and passing:
  - CRISIS → 888_HOLD ✓
  - FACTUAL → SEAL ✓
  - CARE → SEAL ✓
  - SOCIAL → SEAL ✓

### 📁 Files Modified

- `arifos/mcp/tools/mcp_trinity.py` — LANE_PROFILES, LANE_ENGINES, 888_HOLD logic
- `arifos/mcp/sse.py` — Version bump to v52.5.1-SEAL

---

## [v52.0.0] - 2026-01-24 "The Unified Core"

**Status:** SEALED (Production Authority)
**Authority:** Muhammad Arif bin Fazil (888 Judge)

### 🚀 Major Milestone: Core Unification
- **Merged Body into Brain**: Eliminated `AAA_MCP` as a standalone package. The entire application layer is now unified within `arifos.mcp`.
- **Pure Bridge Architecture**: Implemented zero-logic delegation in `arifos/mcp/bridge.py`. The bridge now acts as a pure wiring layer (F1 Amanah), moving all governance logic into the core engines.
- **Unified Versioning**: Established `VERSION.lock` at `v52.0.0-SEAL` across all components (Core, MCP, Specs).
- **Mode Selector**: Added `arifos/mcp/mode_selector.py` allowing dynamic switching between BRIDGE (production) and STANDALONE (development) modes.

### 🛡️ Constitutional Hardening
- **F11 Command Authority**: Migrated rate limiting to `arifos/core/governance/rate_limiter.py` as a first-class constitutional auth check.
- **Spec Consolidation**: Moved all constitutional floor definitions to canonical `arifos/core/spec/constitutional/` with strict version validation.
- **CI Alignment**: Added `.github/workflows/constitutional_alignment.yaml` to ensure no version drift occurs in future updates.

### 📊 Observability & Metrics
- **Rolling SEAL Rate**: Implemented real-time performance tracking in `arifos/mcp/constitutional_metrics.py`.
- **Enhanced Health Endpoint**: Added `/health` telemetry returning status, mode, and SEAL rate.

---

## [v50.5.24] - 2026-01-23 "The Sovereign Ignition"

**Status:** SEALED (Production Ready)
**Authority:** 888 Judge

### 🚀 Major Features (Ignition)
- **Body API (`/v1/govern`)**: Successfully forged the "Mouth" of arifOS. The metabolic loop is now accessible via standard HTTP REST, enabling "Governance-as-a-Service".
- **Unified Kernel**: Consolidated `MCP-SSE` and `Body API` into a single `FastAPI` application (`arifos.core.integration.api.app`).
- **Loop Detection (F4)**: Implemented thermodynamic circuit breakers to detect and VOID infinite repetition loops in AI reasoning.

### 🛡️ Constitutional Calibration
- **100% Integrity**: All 16 Constitutional Floor tests passed.
- **Tri-Witness Fix**: Recalibrated consensus logic to correctly veto when AI logic dissents.
- **F1 Amanah**: Hardened keyword detection for irreversible actions (delete, destroy, purge).
- **F12 Injection**: Expanded threat library for advanced prompt injection patterns.

### 📚 Documentation
- **Universal Codex**: Rewrote `README.md` as a visionary manifesto connecting Physics, Math, and Code.
- **Wisdom Reactor**: Added Mermaid diagram visualizing the AGI-ASI-APEX flow.

---

## [v50.0.0] - 2026-01-20

### Added
- **Trinity Architecture**: Formal separation of AGI (Mind), ASI (Heart), and APEX (Soul).
- **AHA Principle**: Defined Wisdom as Akal × Haluan.
