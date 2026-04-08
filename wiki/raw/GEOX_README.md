# GEOX — Earth Witness & Inverse Modelling Supervisor

> **Version:** v0.4.3 · **Status:** 🔐 SEALED ✅  
> **Motto:** *DITEMPA BUKAN DIBERI* — Forged, not given.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEOX CONSTITUTIONAL TELEMETRY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  arifOS telemetry    : v2.1                                                 │
│  pipeline            : 999 SEAL                                             │
│  floors active       : F1 F2 F3 F4 F7 F9 F11 F13                            │
│  confidence          : CLAIM                                                │
│  P² (Peace²)         : 1.0                                                  │
│  hold status         : CLEAR                                                │
│  uncertainty band    : Ω₀ ∈ [0.03, 0.08]                                    │
│  seal                : DITEMPA BUKAN DIBERI ✅                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📖 Founder's Thesis

**New to GEOX?** Start with the founder's manifesto:
- **[MANIFESTO.md](MANIFESTO.md)** — Why GEOX, Why Now, Why Not Plain LLMs, and Why arifOS
- **[View Online](geox-gui/public/manifesto.html)** — Styled landing page version

> *"GEOX makes AI see the Earth. arifOS makes sure it does not lie about what it sees."*

---

## Table of Contents

1. [What Is GEOX? (30-Second Briefing)](#what-is-geox-30-second-briefing)
2. [Who Is This For?](#who-is-this-for)
3. [GEOX in the arifOS Federation](#geox-in-the-arifos-federation)
4. [Forward vs Inverse Modelling](#forward-vs-inverse-modelling)
5. [The Theory of Anomalous Contrast (ToAC)](#the-theory-of-anomalous-contrast-toac)
6. [The 13 Constitutional Floors in GEOX](#the-13-constitutional-floors-in-geox)
7. [Tool Reference](#tool-reference)
8. [Quick Start](#quick-start)
9. [Deployment](#deployment)
10. [Tri-App Architecture](#tri-app-architecture)
    - [RATLAS — Reference Atlas of Earth Materials](#ratlas--reference-atlas-of-earth-materials)
11. [Repository Structure](#repository-structure)
12. [Integration with arifOS](#integration-with-arifos)
13. [Success Criteria](#success-criteria)
14. [Roadmap](#roadmap)
15. [References](#references)

---

## What Is GEOX? (30-Second Briefing)

**GEOX is the Earth Witness organ in the arifOS constitutional federation.**

It serves as the **reality gatekeeper** for all geoscience operations: every reasoning output, every structural interpretation, and every subsurface decision must be:

- ✅ **Physically possible** (thermodynamics, rock mechanics)
- ✅ **Geospatially grounded** (verified coordinates, CRS, jurisdiction)
- ✅ **Consistent with world-state evidence** (seismic, well data, outcrops)

Before any verdict is **SEALED**.

### The One-Line Promise

> *GEOX prevents AI from making physically impossible claims about the Earth by enforcing constitutional verification on every geoscience output.*

---

## Who Is This For?

| Audience | What GEOX Means To You |
|----------|------------------------|
| **Geoscience Manager** | A "sanity check" layer that stops AI from giving physically impossible answers about subsurface prospects. Reduces technical risk before drilling decisions. |
| **Expert Geologist** | Enforces multi-model inverse reasoning, bias auditing (Bond et al. 2007), and physical-attribute grounding before any structural verdict is sealed. |
| **AI Agent / Developer** | A governed FastMCP server exposing bounded geoscience tools under the `geox.*` namespace with sealed telemetry on every output. |
| **Data Scientist** | A framework for uncertainty quantification in geoscience interpretation with explicit confidence bounds and audit trails. |
| **Regulatory / Compliance** | Immutable audit logs (999_VAULT) for every interpretation decision, enabling post-hoc review and regulatory compliance. |

---

## GEOX in the arifOS Federation

arifOS is **not a monolithic AI**. It is a **constitutional federation** of specialized organs, each with a bounded role, governed by the 13 Binding Floors.

### The Federation Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        arifOS CONSTITUTIONAL FEDERATION                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   HUMAN OPERATOR                                                            │
│        │                                                                    │
│        ▼                                                                    │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│   │  @RIF   │◄──►│  GEOX   │◄──►│ @WEALTH │◄──►│ @WELL   │◄──►│ @PROMPT │  │
│   │ REASON  │    │ EARTH   │    │ ECONOMY │    │ HUMAN   │    │ ORCH    │  │
│   │  ΔΩΨ    │    │ WITNESS │    │ MODEL   │    │ WELLBE  │    │ TASK    │  │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘  │
│        │              │              │              │              │       │
│        └──────────────┴──────────────┴──────────────┴──────────────┘       │
│                                   │                                         │
│                                   ▼                                         │
│                          ┌─────────────────┐                                │
│                          │  13 FLOORS (Ω)  │                                │
│                          │  F1-F13         │                                │
│                          │  Constitutional │                                │
│                          │  Law            │                                │
│                          └────────┬────────┘                                │
│                                   │                                         │
│                                   ▼                                         │
│                          ┌─────────────────┐                                │
│                          │  999_VAULT      │                                │
│                          │  Immutable      │                                │
│                          │  Audit Log      │                                │
│                          └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Organ Roles

| Organ | Role | Plain-Language Analogy | Key Function |
|-------|------|------------------------|--------------|
| **@RIF** | Reasoning & hypothesis generation | The geologist's brain | Proposes structural models, interprets data |
| **GEOX** | Earth verification & forward modelling | The lab that stress-tests every model | Validates physical possibility, grounds in evidence |
| **@WEALTH** | Economic & decision modelling | The economist | Cost-benefit, NPV, portfolio optimization |
| **@WELL** | Human energy & wellbeing modelling | The safety officer | Crew safety, operational risk |
| **@PROMPT** | Task shaping & orchestration | The project manager | Workflow coordination, intent parsing |
| **@JUDGE** | Human veto & governance | The final authority | Always human — 888_HOLD release |

### Constitutional Governance

No organ can override the **13 Binding Floors**. GEOX specifically enforces:

| Floor | Name | GEOX Enforcement |
|-------|------|------------------|
| **F1** | AMANAH (Reversibility) | All interpretations are revisable; no irreversible claims without human signoff |
| **F2** | TRUTH (≥99% accuracy) | Every claim grounded in evidence; uncertainty declared when <99% |
| **F3** | TRI-WITNESS (W³ ≥ 0.95) | Human + AI + Evidence must agree before SEAL |
| **F4** | CLARITY (ΔS ≤ 0) | Scale, CRS, provenance must be explicit or declared unknown |
| **F7** | HUMILITY (Ω₀ ∈ [0.03, 0.08]) | Confidence bounded; overclaim prohibited |
| **F9** | ANTI-HANTU | No consciousness claims; no anthropomorphization of geological processes |
| **F11** | AUDITABILITY | Every decision logged with full provenance |
| **F13** | SOVEREIGN | Human retains final veto (888_HOLD) |

---

## Forward vs Inverse Modelling

Understanding these two modes is the foundation of GEOX's role in the interpretation loop.

### Forward Modelling

> **"Given this Earth model, what data would we observe?"**

GEOX tools simulate:
- Seismic responses from structural geometries
- Feasibility envelopes for drilling scenarios
- Physical constraints on rock properties

**Driver:** GEOX tools  
**MCP Role:** Exposed as `geox.*` tools

### Inverse Modelling

> **"Given observed data, what Earth model best explains it?"**

@RIF (the reasoning organ) proposes hypotheses, calls GEOX tools to test them against real constraints.

**Driver:** @RIF + GEOX collaboration  
**MCP Role:** @RIF calls `geox.*` tools to constrain hypotheses

### The Interpretation Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GEOX INTERPRETATION LOOP                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   OBSERVED DATA          INVERSE MODEL          FORWARD MODEL              │
│   (seismic, wells)  ──►  (hypothesis)    ──►   (prediction)               │
│        │                      │                      │                      │
│        │                      │                      ▼                      │
│        │                      │               SYNTHETIC DATA                │
│        │                      │                      │                      │
│        │                      ▼                      ▼                      │
│        │               ┌─────────────────────────────────────┐              │
│        │               │         GEOX VALIDATION             │              │
│        │               │  • Physically possible? (F1)        │              │
│        │               │  • Grounded in evidence? (F2)       │              │
│        │               │  • Multi-model maintained? (F7)     │              │
│        │               │  • Bias audited? (ToAC)             │              │
│        │               └─────────────────────────────────────┘              │
│        │                      │                                             │
│        └──────────────────────┘                                             │
│               COMPARE                                                       │
│                                                                             │
│   If mismatch: Update model → Repeat                                        │
│   If match: Proceed to 888_JUDGE → 999_SEAL                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Modelling Matrix

| Type | Question | Driver | MCP Role |
|------|----------|--------|----------|
| **Forward** | "What would we observe?" | GEOX tools | `geox.*` namespace |
| **Inverse** | "What model explains this?" | @RIF + GEOX | @RIF calls `geox.*` |

---

## 🌍 The Source of Earth (Canonical Reality)

GEOX defines "Reality" through a buildable, open-source substrate. We do not depend on proprietary basemaps as our core anchor.

| Layer | Canonical Source | Engine / Standard |
| :--- | :--- | :--- |
| **3D Earth** | **WGS84 High-Precision** | `CesiumJS` |
| **2D Map** | **ArcGIS-Style GPU** | `MapLibre GL JS` |
| **Basemap** | **OpenStreetMap** | `Protomaps (PMTiles)` |
| **Terrain** | **Copernicus DEM** | `GLO-30 (30m Global)` |
| **Imagery** | **Sentinel-2 / Landsat** | `COG / STAC` |
| **Geology** | **Macrostrat** | `Macrostrat API v2` |

---

## 🏗️ Spatial Infrastructure (Body)

The GEOX spatial backend is built for zero-latency, cloud-native data delivery:
- **Serving:** `Martin` (Vector Tiles) + `TiTiler` (Raster/COG).
- **Storage:** `PostGIS` + `GeoParquet`.
- **Discovery:** `STAC` (SpatioTemporal Asset Catalog).

---

## The Theory of Anomalous Contrast (ToAC)

### The Problem

AI seismic interpretation fails not because of wrong physics, but because of **display artifacts and processing biases** — what GEOX calls **Anomalous Contrast**. These fool both human interpreters and AI models into seeing structures that do not exist.

### Known Failure Modes

| Artifact | Description | Risk |
|----------|-------------|------|
| **Polarity conventions** | Wrong impedance assumption | Misidentified fluid contacts |
| **Gain artifacts** | AGC distortions | False amplitude anomalies |
| **Migration smiles** | Processing artifacts | Phantom structures |
| **Display stretch** | Vertical exaggeration | Misinterpreted dip angles |

### The Contrast Canon

GEOX formalizes three rules to prevent anomalous contrast:

#### 1. Multi-Model Candidates (Non-Uniqueness Principle)

> **Never collapse to a single inverse solution prematurely.**

Maintain a ranked ensemble of structural hypotheses. The Earth is underdetermined — multiple models can explain the same data.

#### 2. Physical Attributes First

> **All visual interpretation must be anchored in deterministic physics.**

- Coherence
- Dip-azimuth
- Curvature
- Spectral decomposition

**No interpretation from aesthetics alone.**

#### 3. Bias Audit Before Seal

> **Run an explicit professional bias check before `geox_evaluate_prospect` seals the verdict.**

Reference: Bond et al. (2007) on cognitive bias in seismic interpretation.

---

## The 13 Constitutional Floors in GEOX

### Floor Enforcement Matrix

| Floor | Name | Threshold | GEOX Implementation |
|-------|------|-----------|---------------------|
| **F1** | AMANAH | Reversibility | All interpretations revisable; 888_HOLD on irreversible claims |
| **F2** | TRUTH | τ ≥ 0.99 | Evidence grounding; uncertainty band declaration |
| **F3** | TRI-WITNESS | W³ ≥ 0.95 | Human + AI + Evidence consensus before SEAL |
| **F4** | CLARITY | ΔS ≤ 0 | Scale, CRS, provenance explicit or "UNKNOWN" declared |
| **F5** | PEACE² | P² ≥ 1.0 | No destructive recommendations without mitigation |
| **F6** | EMPATHY | κᵣ ≥ 0.95 | Stakeholder impact assessment |
| **F7** | HUMILITY | Ω₀ ∈ [0.03, 0.08] | Confidence bounded; overclaim prohibited |
| **F8** | GENIUS | G ≥ 0.80 | System health monitoring |
| **F9** | ANTI-HANTU | C_dark < 0.30 | No anthropomorphization; physical processes remain physical |
| **F10** | ONTOLOGY | Category lock | AI ≠ Human; Model ≠ Reality |
| **F11** | AUDITABILITY | 100% logging | Every decision to 999_VAULT |
| **F12** | INJECTION | Risk < 0.15 | Block adversarial inputs |
| **F13** | SOVEREIGN | Human veto | 888_HOLD until human release |

### 888 HOLD Triggers in GEOX

The following conditions trigger an automatic **888_HOLD** (awaiting human decision):

| Condition | Rationale |
|-----------|-----------|
| Borehole spacing > 10km | Continuity claims unreliable |
| Unit correlation confidence < 0.6 | High uncertainty in stratigraphy |
| Vertical exaggeration > 2x undisclosed | Misleading visual appearance |
| Fault geometry not seismic-constrained | Unverified structural model |
| Pinchout/truncation in interpreted zone | High-risk interpretation |
| Interval of interest has zero well control | No ground truth |
| Scale unknown or unverified | F4 violation |

---

## Tool Reference

### GEOX Tool Surface (v0.4.3)

| Tool | Purpose | Stage | Floors | Output |
|------|---------|-------|--------|--------|
| `geox_load_seismic_line` | Load seismic data with QC | 111_SENSE | F4, F11 | Interactive Seismic Section App |
| `geox_build_structural_candidates` | Generate multi-model hypotheses | 333_MIND | F2, F7 | Multi-Model Candidates View |
| `geox_feasibility_check` | Check physical possibility | 222_REFLECT | F1, F4, F7 | Constitutional Floor Panel |
| `geox_verify_geospatial` | Validate coordinates/CRS | 111_SENSE | F4, F11 | Geospatial Verification Card |
| `geox_evaluate_prospect` | Seal prospect verdict | 888_JUDGE | F1-F13 | Prospect Verdict Card |

### Tool Details

#### `geox_load_seismic_line`

```python
geox_load_seismic_line(
    line_id: str,              # Seismic line identifier
    survey_path: str,          # Path to survey data
    generate_views: bool = True  # Generate interactive views
) -> ToolResult
```

**Returns:** Interactive Seismic Section App with QC badges, ToAC warnings, and 888_HOLD checklist.

#### `geox_build_structural_candidates`

```python
geox_build_structural_candidates(
    line_id: str,              # Seismic line identifier
    focus_area: str | None = None  # Optional focus region
) -> ToolResult
```

**Returns:** Multi-model candidate ensemble with confidence scores. **Non-uniqueness principle enforced** — collapse to single model prohibited.

#### `geox_feasibility_check`

```python
geox_feasibility_check(
    plan_id: str,              # Plan identifier
    constraints: list[str]     # Physical constraints to verify
) -> ToolResult
```

**Returns:** Constitutional floor panel with F1-F13 status and SEAL/HOLD verdict.

#### `geox_verify_geospatial`

```python
geox_verify_geospatial(
    lat: float,                # Latitude (WGS84)
    lon: float,                # Longitude (WGS84)
    radius_m: float = 1000.0   # Verification radius
) -> ToolResult
```

**Returns:** Geospatial verification card with province, jurisdiction, and F4/F11 compliance.

#### `geox_evaluate_prospect`

```python
geox_evaluate_prospect(
    prospect_id: str,          # Prospect identifier
    interpretation_id: str     # Interpretation to evaluate
) -> ToolResult
```

**Returns:** Prospect verdict card with 888_HOLD status, confidence, and required actions before SEAL.

---

## Quick Start

### Prerequisites

```bash
# Python 3.10+
python --version

# UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

```bash
# Clone repository
git clone https://github.com/ariffazil/GEOX.git
cd GEOX

# Install with uv
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Verify Installation

```bash
# CLI entry point should resolve
which geox

# Health check
geox --health
```

### Development Mode

```bash
# Auto-detects fastmcp.json
fastmcp run

# With inspector UI
fastmcp dev
```

---

## Deployment

### STDIO Mode (Default)

```bash
# Default transport for Claude Desktop
python geox_mcp_server.py

# Or via CLI
geox --transport stdio
```

### HTTP Mode

```bash
# Deploy as arifOS federation service
python geox_mcp_server.py --transport http --port 8000

# Or via CLI
geox --transport http --port 8000 --host 0.0.0.0
```

### Docker

```bash
# Build image
docker build -t geox-earth-witness .

# Run
docker run -p 8000:8000 geox-earth-witness
```

### Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Minimal health check (returns "OK") |
| `GET /health/details` | Structured health payload with version, mode, timestamp |

---

## Tri-App Architecture

GEOX owns the **visual semantics**, not the LLM. The LLM handles intent; GEOX produces deterministic state.

### Four Views

| App | Purpose | Data Source | Key Distinction |
|-----|---------|-------------|-----------------|
| **Map App** | Geographic context | Basin, coordinates, assets | Spatial overview |
| **Cross Section App** | Interpreted earth model | Wells, tops, faults, stratigraphy | **INTERPRETED** — observed vs inferred |
| **Seismic Section App** | Sensor evidence | Seismic image/line | **OBSERVATIONAL** — raw evidence |
| **RATLAS** | Physics reference atlas | 99-material database | **MATERIAL INTELLIGENCE** — symbolic + numeric |

### RATLAS — Reference Atlas of Earth Materials

RATLAS is GEOX's **material intelligence layer** — a physics-backed reference atlas of 99 canonical Earth material states across 11 families. It serves as the symbolic grounding layer for GEOX reasoning agents.

**Scope:** Forward-modelled log responses (GR, CAL, DEN, NPHI, DT, RT), matrix physics, and symbolic token vocabulary for geo-reasoning.

**Not a classifier.** RATLAS provides reference physics — actual formation evaluation requires calibrated field data.

**Access:**
- Live: https://aaa.arif-fazil.com/geox/geox_ratlas.html
- CSV: https://aaa.arif-fazil.com/geox/geox_atlas_99_materials.csv
- Source: [geox_ratlas.html](../geox_ratlas.html), [geox_atlas_99_materials.csv](../geox_atlas_99_materials.csv)

**11 Material Families:**
- Sedimentary Clastic (18) · Sedimentary Carbonate (9) · Sedimentary Chemical/Organic (9)
- Igneous Felsic (9) · Igneous Intermediate/Mafic (9) · Igneous Ultramafic/Altered (9)
- Metamorphic Foliated (9) · Metamorphic Non-Foliated (9)
- Unconsolidated/Soil (9) · Engineered Materials (9)

**Symbolic Token Set** — drives GEOX reasoning engine:
- `SAND_QZ_CLEAN` · `SHALE_ILL` · `LIMESTONE_CC` · `DOLOMITE_DOL` · `ANHYDRITE` · `HALITE`
- `GRANITE_K` · `BASALT_MAF` · `PERIDOTITE_OL` · `SERPENTINE` · `SCHIST_BT`
- `STEEL_Fe` · `CONCRETE_RF` · `COAL_LIG` · `BITUMEN` · `CHERT_SIL`

**Forward Models (reference only):**
```
ρb = (1−φ)·ρm + φ·ρf           # Bulk density mixing law
NPHI ≈ φ·Σ(Si·HIi)             # Neutron hydrogen index
Rt = a·Rw / (φm·Swⁿ)            # Archie resistivity (clean)
Vsh = (GRlog − GRmin) / (GRmax − GRmin)  # Gamma ray shale index
```

**Constitutional alignment:** F1 Reversibility, F2 Truth (≥99%), F4 Clarity (scale/provenance explicit), F7 Humility (uncertainty bounded), F9 Anti-Hantu (no anthropomorphization), F13 Sovereign (human veto).

> *"Anak Nusantara, bukan software Barat. Real data, physics law, constitutional verification."*

| App | Purpose | Data Source | Key Distinction |
|-----|---------|-------------|-----------------|
| **Map App** | Geographic context | Basin, coordinates, assets | Spatial overview |
| **Cross Section App** | Interpreted earth model | Wells, tops, faults, stratigraphy | **INTERPRETED** — observed vs inferred |
| **Seismic Section App** | Sensor evidence | Seismic image/line | **OBSERVATIONAL** — raw evidence |

### Critical: Never Merge Cross Section and Seismic Section

- **Geologic Cross Section**: Interpretive earth model product
- **Seismic Section**: Observational sensor image
- Confusing them leads to overclaim and bad UI semantics

### Sync Mode

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPLIT-SCREEN SYNC MODE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────┐    ┌─────────────────────────┐               │
│   │   CROSS SECTION APP     │    │   SEISMIC SECTION APP   │               │
│   │   (Interpreted Model)   │◄──►│   (Observational Data)  │               │
│   │                         │    │                         │               │
│   │  • Wells with tops      │    │  • Seismic amplitude    │               │
│   │  • Fault polygons       │    │  • Reflector picks      │               │
│   │  • Stratigraphic units  │    │  • ToAC contrast        │               │
│   │  • Observed vs inferred │    │  • QC badges            │               │
│   │                         │    │                         │               │
│   └─────────────────────────┘    └─────────────────────────┘               │
│              │                              │                               │
│              └──────────────┬───────────────┘                               │
│                             │                                               │
│                    SHARED PROFILE CURSOR                                    │
│                                                                             │
│   • Click well in cross section → highlight well tie in seismic            │
│   • Fault selection synced between views                                   │
│   • Distance coordinate synchronized along line                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
GEOX/
├── geox_mcp_server.py          # FastMCP server entry point
├── geox_ratlas.html            # RATLAS — Earth Material Atlas (99 materials)
├── geox_atlas_99_materials.csv # Material physics reference database
├── fastmcp.json                # Declarative deployment config
├── pyproject.toml              # Package metadata & dependencies
├── smithery.yaml               # Smithery registry config
│
├── arifos/                     # arifOS constitution integration
│   └── geox/
│       ├── seismic_image_ingest.py
│       ├── contrast_wrapper.py
│       ├── geox_validator.py
│       ├── geox_hardened.py
│       ├── schemas/            # Canonical schemas
│       ├── governance/         # Floor enforcement
│       ├── renderers/          # Visualization adapters
│       └── examples/           # Demo workflows
│
├── knowledge/                  # Subsurface knowledge base
│   └── basin_profiles/
│
├── ops/                        # Operational runbooks
│   └── deployment/
│
├── tests/                      # Test suite
│   ├── unit/
│   └── integration/
│
├── docs/                       # Extended documentation
│
├── CHANGELOG.md                # Version history
├── UNIFIED_ROADMAP.md          # Development roadmap
├── WIRING_GUIDE.md             # Federation wiring instructions
├── HARDENED_SEAL.md            # Seal protocol specification
├── GEOX_SUCCESS_CRITERIA.md    # Acceptance criteria per tool
└── SECURITY.md                 # Security & disclosure policy
```

---

## Integration with arifOS

### MCP Client Configuration

```json
{
  "mcpServers": {
    "geox": {
      "command": "uvx",
      "args": ["arifos-geox"],
      "env": {
        "GEOX_MODE": "federation",
        "ARIFOS_VAULT_URL": "https://vault.arif-fazil.com"
      }
    }
  }
}
```

### Federation Wiring

See [WIRING_GUIDE.md](WIRING_GUIDE.md) for detailed integration instructions with:
- @RIF (reasoning organ)
- @WEALTH (economic organ)
- @JUDGE (human veto)
- 999_VAULT (audit log)

---

## Success Criteria

GEOX success is measured across six axes:

| Axis | Target | Measurement |
|------|--------|-------------|
| **Usability** | Query → rendered view < 60s | E2E timer |
| **Geological Quality** | 100% views show scale or "SCALE UNKNOWN" | F4 enforcement |
| **Governance** | 100% out-of-scope requests trigger 888_HOLD | Floor monitoring |
| **Interoperability** | Same state across ≥2 MCP hosts | Cross-host test |
| **Performance** | Render latency < 5s | Benchmark suite |
| **Repo Maturity** | Test coverage > 80% | CI/CD metrics |

See [GEOX_SUCCESS_CRITERIA.md](GEOX_SUCCESS_CRITERIA.md) for full details.

---

## Roadmap

### Current: v0.4.3 (SEALED)

- ✅ FastMCP server with stdio/HTTP transports
- ✅ 5 core tools with interactive Prefab UI
- ✅ F1-F13 floor enforcement
- ✅ 999_VAULT integration
- ⚠️ Visualization: stubbed (awaiting cigvis integration)

### Next: v0.5.0 (FORGE-3)

- [ ] cigvis 3D seismic rendering integration
- [ ] Full Tri-App architecture (Map + Cross Section + Seismic)
- [ ] SEG-Y ingest pipeline
- [ ] Well-tie calibration workflow

### Future: v1.0.0 (SOVEREIGN)

- [ ] Production hardening
- [ ] Full test coverage
- [ ] Regulatory compliance audit
- [ ] Human-in-the-loop 888_HOLD release UI

See [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md) for detailed roadmap.

---

## References

### Academic

- **Bond, C.E., Gibbs, A.D., Shipton, Z.K., Jones, S. (2007).** "What do you think this is? 'Conceptual uncertainty' in geoscience interpretation." *GSA Today*, 17(11), 4–10.

### Technical

- **FastMCP:** https://github.com/jlowin/fastmcp
- **cigvis:** https://github.com/cigvis (3D seismic visualization)
- **arifOS Architecture:** See `arifos/` directory

### Related Repositories

| Repository | Relationship |
|------------|--------------|
| [arifOS](https://github.com/ariffazil/arifOS) | Constitutional federation kernel |
| [APEX](https://github.com/ariffazil/APEX) | Theory & philosophy (CC0) |

---

## License

```
Theory (APEX):        CC0 (Public Domain)
Runtime (GEOX):       AGPL-3.0
Trademark (GEOX):     Proprietary
```

---

## Contact

**Muhammad Arif bin Fazil**  
Sovereign Architect, arifOS & GEOX

- GitHub: [@ariffazil](https://github.com/ariffazil)
- Website: [arif-fazil.com](https://arif-fazil.com)
- Email: arif@arif-fazil.com

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given*

```
ΔΩΨ | GEOX | 888_JUDGE | EARTH WITNESS
```

---

*Version: v0.4.3*  
*Status: SEALED ✅*  
*Last Updated: 2026-04-01*
