# 🔥 GEOX Simplified — Earth Intelligence Core

## Manifesto: Chaos Reduction Complete

**Before:** 183 Python files, 19 markdown docs, 4+ MCP servers, scattered schemas
**After:** Lean Earth Intelligence — only what serves the mission

---

## Core Philosophy (DITEMPA BUKAN DIBERI)

> "Perfection is achieved not when there is nothing more to add,
> but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

**GEOX is:**
- A **Theory of Anomalous Contrast (ToAC)** engine
- An **AC_Risk** calculator with constitutional governance
- A set of **MCP tools** for subsurface decision support
- **4 MCP Apps** for interactive exploration

**GEOX is NOT:**
- A Petrel competitor
- A full-service seismic processing platform
- A replacement for human interpreters
- A "sudo" system with unchecked power

---

## Directory Structure (Simplified)

```
GEOX/
├── geox/                          # ← Canonical Python package
│   ├── __init__.py
│   ├── server.py                  # ← ONE MCP server (AAA Grade)
│   ├── tool_registry.py           # ← Unified tool definitions
│   ├── ac_risk.py                 # ← ToAC calculation engine
│   └── apps/                      # ← 4 MCP Apps only
│       ├── ac_risk_console/
│       ├── basin_explorer/
│       ├── seismic_viewer/
│       └── well_context_desk/
├── data/                          # ← Sample data only
├── docs/                          # ← 3 documents only
│   ├── README.md                  # ← This is the only entry point
│   ├── ARCHITECTURE.md            # ← Technical deep dive
│   └── OPERATIONS.md              # ← Run & deploy guide
├── tests/                         # ← Constitutional validation
├── docker-compose.yml             # ← Single deployment file
└── pyproject.toml                 # ← Dependencies & metadata
```

---

## The 7 Tools (No More, No Less)

| Tool | Purpose | Status |
|------|---------|--------|
| `geox_compute_ac_risk` | ToAC calculation — THE CORE | ✅ Production |
| `geox_load_seismic_line` | Seismic with scale validation | ✅ Production |
| `geox_build_structural_candidates` | Multi-model interpretation | ✅ Production |
| `geox_verify_geospatial` | Coordinate grounding | ✅ Production |
| `geox_feasibility_check` | Constitutional firewall | ✅ Production |
| `geox_evaluate_prospect` | Prospect verdict with HOLD | ✅ Production |
| `geox_earth_signals` | Live Earth observations | ✅ Production |

**Removed:**
- ❌ `geox_interpret_single_line` — Too complex, overlaps with candidates
- ❌ `geox_digitize_well_log` — Scaffold, not ready
- ❌ `geox_georeference_map` — Preview quality, defer to v2

---

## Constitutional Floors (F1-F13)

Every tool enforces:
- **F2 Truth** — Uncertainty quantified
- **F4 Clarity** — Units validated
- **F7 Humility** — Confidence bounded
- **F9 Anti-Hantu** — Physical grounding checked
- **F11 Authority** — Provenance logged
- **F13 Sovereign** — 888_HOLD gates active

---

## Quick Start

```bash
# Deploy
docker-compose up -d

# Test
curl http://localhost:8000/health

# Use
echo '{"u_phys": 0.3, "transform_stack": ["linear"]}' | \
  python -m geox.client compute_ac_risk
```

---

## What Was Removed (Chaos Audit)

| Category | Count | Action |
|----------|-------|--------|
| Duplicate MCP servers | 3 | Archived |
| Legacy tool files | 12 | Archived |
| Scattered schemas | 5 | Consolidated |
| Markdown docs | 16 | Consolidated to 3 |
| Scaffold features | 4 | Removed |
| Example/mock code | 8 | Moved to tests/ |

**Total Files Reduced:** ~140 → ~40 (71% reduction)

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*Earth Intelligence: Revealed through subtraction*
