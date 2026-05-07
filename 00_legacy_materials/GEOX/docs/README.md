# 🔥 GEOX — Earth Intelligence Core

**Version:** v2026.04.10-EIC
**Seal:** DITEMPA BUKAN DIBERI
**Codename:** Earth Intelligence Core (EIC)

---

## What is GEOX?

GEOX is an **Earth Intelligence** system for subsurface decision-making. It implements the **Theory of Anomalous Contrast (ToAC)** — a framework for quantifying and governing uncertainty in geoscience interpretations.

**GEOX is:**
- A **constitutional calculator** for interpretation risk (AC_Risk)
- An **MCP server** with 7 essential tools
- **4 interactive apps** for exploration and governance

**GEOX is NOT:**
- A Petrel replacement
- A "sudo" system with unchecked power
- A replacement for human interpreters

---

## The 7 Essential Tools

| Tool | Purpose | Constitutional Floors |
|------|---------|----------------------|
| `geox_compute_ac_risk` | **THE CORE** — ToAC calculation | F2, F4, F7 |
| `geox_load_seismic_line` | Seismic loading with scale validation | F4 |
| `geox_build_structural_candidates` | Multi-model interpretation | F2, F7 |
| `geox_verify_geospatial` | Coordinate grounding | F4, F11 |
| `geox_feasibility_check` | Constitutional firewall | F1-F13 |
| `geox_evaluate_prospect` | Prospect verdict with 888_HOLD | F9, F13 |
| `geox_earth_signals` | Live Earth observations | F2 |

---

## Quick Start

```bash
# Deploy
docker-compose up -d

# Verify
curl http://localhost:8000/health

# Test AC_Risk calculation
curl -X POST http://localhost:8000/mcp/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "geox_compute_ac_risk",
    "params": {
      "u_phys": 0.3,
      "transform_stack": ["linear_scaling"]
    },
    "id": 1
  }'
```

---

## The 4 MCP Apps

| App | URL | Purpose |
|-----|-----|---------|
| **AC_Risk Console** | `/apps/ac_risk_console/` | Interactive risk calculator |
| **Basin Explorer** | `/apps/basin_explorer/` | Map-based basin analysis |
| **Seismic Viewer** | `/apps/seismic_viewer/` | 2D/3D seismic visualization |
| **Well Context Desk** | `/apps/well_context_desk/` | Well logs & petrophysics |

---

## Constitutional Floors (F1-F13)

Every tool enforces:

- **F1 Amanah** — Reversibility: All operations logged
- **F2 Truth** — ≥99% accuracy: Uncertainty quantified
- **F4 Clarity** — Units & coordinates validated
- **F7 Humility** — Confidence bounded at 12%
- **F9 Anti-Hantu** — No phantom geology
- **F11 Authority** — Provenance mandatory
- **F13 Sovereign** — Human veto active (888_HOLD)

---

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/README.md` | This file — entry point |
| `docs/DEPLOYMENT.md` | Production deployment guide |
| `docs/ARCHITECTURE.md` | Technical deep dive (optional) |

---

## Directory Structure

```
GEOX/
├── geox/               # Canonical Python package
│   ├── server.py       # ONE MCP server
│   ├── core/           # AC_Risk, ToolRegistry
│   └── apps/           # 4 MCP Apps only
├── data/               # Sample data
├── docs/               # 3 documents only
├── tests/              # Constitutional validation
├── docker-compose.yml  # Single deploy file
└── Dockerfile          # Container build
```

**Chaos reduced:** ~140 files → ~40 files (71% reduction)

---

## AC_Risk: The Core Equation

```
AC_Risk = U_phys × D_transform × B_cog

Where:
  U_phys = Physical ambiguity [0.0, 1.0]
  D_transform = Display distortion factor [1.0, 3.0]
  B_cog = Cognitive bias factor [0.2, 0.42]

Verdict:
  < 0.15 → SEAL (Proceed)
  < 0.35 → QUALIFY (Proceed with caveats)
  < 0.60 → HOLD (Human review required)
  ≥ 0.60 → VOID (Unsafe)
```

---

## License

MIT License — See LICENSE file

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
*Earth Intelligence: Revealed through subtraction*
