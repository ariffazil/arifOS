# geox.arif-fazil.com — Site Specification

> **Status:** SPECIFICATION READY
> **Authority:** Muhammad Arif bin Fazil
> **Seal:** 999_VAULT
> **Motto:** *DITEMPA BUKAN DIBERI*

---

## Core Message

**GEOX is not "AI that sees geology."**

**GEOX is governed intelligence that turns pixels into constrained, auditable geoscience decisions.**

**Physics > Narrative. Always.**

---

## MCP vs Apps: The Distinction

### MCP (Model Context Protocol)
**What it is:** Machine interface for AI agents
**Who uses it:** Claude, Cursor, other AI systems
**Format:** JSON schemas, tool definitions, structured I/O
**Location:** `geox.arif-fazil.com/mcp/`

### Apps
**What it is:** Human operator interfaces
**Who uses it:** Geoscientists, technicians, decision-makers
**Format:** Web UI, interactive tools, visual outputs
**Location:** `geox.arif-fazil.com/apps/`

### The Relationship
```
┌─────────────────────────────────────────────────────────────┐
│                     HUMAN OPERATOR                          │
│                         ↓                                   │
│                      WEB APPS                               │
│              (Visual, interactive, governed)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     MCP SERVER                              │
│              (Machine interface, schemas)                   │
│                         ↓                                   │
│                   AI AGENTS (Claude/Cursor)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    GEOX ENGINE                              │
│         (AC_Risk, ToAC governance, physics)                 │
└─────────────────────────────────────────────────────────────┘
```

**Same governance layer. Different interfaces.**

---

## Current MCP Tools (Existing)

### Seismic Tools
| Tool | Status | Description |
|------|--------|-------------|
| `geox_load_seismic_line` | ✅ Live | Load seismic + generate contrast views |
| `geox_build_structural_candidates` | ✅ Live | Multi-model structural interpretation |
| `geox_interpret_single_line` | ✅ Live | Full governed interpreter |
| `geox_extract_seismic_views` | ✅ Live | Contrast canon view generation |
| `geox_create_overlay` | ✅ Live | Fault/horizon overlay creation |

### Governance Tools
| Tool | Status | Description |
|------|--------|-------------|
| `geox_feasibility_check` | ✅ Live | Physical feasibility validation |
| `geox_verify_geospatial` | ✅ Live | Coordinate verification |
| `geox_evaluate_prospect` | ✅ Live | Prospect verdict with AC_Risk |

### Petrophysics Tools (Phase B)
| Tool | Status | Description |
|------|--------|-------------|
| `geox_select_sw_model` | 🟡 Partial | Saturation model selection |
| `geox_compute_petrophysics` | 🟡 Partial | Vsh, φ, Sw computation |
| `geox_validate_cutoffs` | 🟡 Partial | Net/pay cutoff validation |
| `geox_petrophysical_hold_check` | 🟡 Partial | Automatic hold triggers |

### Vision Tools (New)
| Tool | Status | Description |
|------|--------|-------------|
| `geox_georeference_map` | 🔴 Scaffold | Map georeferencing with AC_Risk |
| `geox_digitize_analog` | 🔴 Planned | Analog log/chart digitization |
| `geox_compute_ac_risk` | ✅ Live | AC_Risk calculation for any operation |

---

## Current Apps (Existing)

### Volume App
- **Status:** ✅ Functional
- **Path:** `arifos/geox/apps/volume_app/`
- **Features:** 3D volume rendering, slice views, horizon/fault overlays
- **Backend:** cigvis adapter

### Prefab Views
- **Status:** ✅ Functional
- **Path:** `arifos/geox/apps/prefab_views.py`
- **Features:** MCP host UIs (Claude Desktop, Cursor) for all tools
- **Views:** 9 view types covering seismic, petrophysics, governance

---

## Proposed Site Structure

### Navigation
```
geox.arif-fazil.com
├── /              (Hero + overview)
├── /apps          (Operator tools)
├── /mcp           (Machine interface)
├── /theory        (ToAC, AC_Risk)
├── /cases         (Real examples)
├── /docs          (Documentation)
└── /about         (Mission, philosophy)
```

---

## Page Specifications

### 1. Homepage (`/`)

**Hero Section**
```
Headline: "GEOX is governed geospatial and subsurface intelligence."
Subheadline: "Physics over narrative. Audit over guess. Decision discipline over hype."

Three Pillars:
1. Intelligence — Models, vision, reasoning
2. Tools — MCP APIs and operator apps
3. Governance — ToAC, AC_Risk, 888_HOLD

CTA Buttons:
- [Open Apps] → /apps
- [Use MCP] → /mcp
- [Read Charter] → /theory
```

**Live Capabilities (Honest Status)**
```
Capability Grid:
┌─────────────────────────┬──────────┬─────────────────────────────┐
│ Feature                 │ Status   │ Note                        │
├─────────────────────────┼──────────┼─────────────────────────────┤
│ Seismic interpretation  │ ✅ Live  │ Contrast canon, multi-view  │
│ Structural candidates   │ ✅ Live  │ Non-unique inverse models   │
│ Petrophysics (Phase B)  │ 🟡 Beta  │ Sw models, cutoff validation│
│ Map georeferencing      │ 🟡 Scaff │ Core working, AC_Risk next  │
│ Analog digitization     │ 🔴 Forge │ Architecture defined        │
│ Governed VLM            │ 🟡 Scaff │ Wrapper ready, backend TBD  │
└─────────────────────────┴──────────┴─────────────────────────────┘
```

**Trust Surface**
```
Verdict Examples:
- SEAL: "Fault interpretation confirmed by well tie"
- QUALIFY: "Channel candidate — requires amplitude validation"
- HOLD: "Image-only interpretation — cross-check prohibited"
- VOID: "Structural model violates regional dip"
```

---

### 2. Apps Page (`/apps`)

**Five Core Apps (V1)**

#### App 1: Georeference Map
- **Status:** 🟡 Scaffold
- **Function:** Upload map → detect/select GCPs → warp → GeoTIFF
- **Outputs:**
  - GeoTIFF with embedded transform
  - GCP residual table
  - AC_Risk score + verdict
- **Governance:** OCR validation, bound divergence check, scale consistency

#### App 2: Analog Digitizer
- **Status:** 🔴 Planned
- **Function:** Upload core photo / paper log / crossplot → trace curves → CSV/LAS
- **Outputs:**
  - Digitized curves with uncertainty
  - Depth calibration report
  - RATLAS validation results
  - AC_Risk score
- **Governance:** Physics checks, monotonicity validation, range enforcement

#### App 3: Seismic Vision Review
- **Status:** 🟡 Scaffold
- **Function:** Upload seismic image → multi-contrast analysis → governed interpretation
- **Outputs:**
  - 5 contrast views
  - Feature hypotheses
  - Cross-view consistency score
  - Physics anchoring check
  - Verdict + perception bridge warning
- **Governance:** Multi-view consistency, attribute reconciliation, AC_Risk

#### App 4: Attribute Audit
- **Status:** 🟡 Beta
- **Function:** Run coherence/dip/curvature → compare image-only vs physics path
- **Outputs:**
  - Attribute maps
  - Transform log
  - Image-only risk assessment (per Nature 2025)
  - Calibration quality metrics
- **Governance:** Transform logging, source attribution, AC_Risk by attribute

#### App 5: AC_Risk Console
- **Status:** ✅ Live
- **Function:** Inspect any workflow's AC_Risk components
- **Outputs:**
  - U_phys breakdown
  - D_transform (transform stack)
  - B_cog (bias model)
  - Why HOLD was triggered
  - Suggested mitigations

---

### 3. MCP Page (`/mcp`)

**Value Proposition**
> "GEOX MCP turns your AI agents into geospatial experts with built-in governance."

**Tool Catalog**
```yaml
Core Geospatial:
  - geox_georeference_raster:
      input: image_path, claimed_bounds
      output: geotiff_path, gcp_list, ac_risk, verdict

  - geox_detect_gcp_candidates:
      input: image_path
      output: candidate_points, ocr_confidence

Petrophysics:
  - geox_digitize_chart:
      input: image_path, chart_type
      output: traced_curves, uncertainty, ratlas_validation

  - geox_compute_petrophysics:
      input: interval_uri, model_id
      output: vsh, phi_t, phi_e, sw, uncertainty_envelopes

Seismic:
  - geox_generate_contrast_canon:
      input: seismic_image
      output: 5_contrast_views, transform_metadata

  - geox_interpret_with_governance:
      input: seismic_image, interpretation_goal
      output: hypotheses, consistency_score, ac_risk, verdict

  - geox_extract_attributes:
      input: seismic_data, attribute_list
      output: attribute_maps, source_attribution, risk_flags

Governance:
  - geox_compute_ac_risk:
      input: operation_type, transform_stack, evidence_quality
      output: ac_risk, verdict, explanation, mitigation_suggestions

  - geox_emit_verdict:
      input: evidence_bundle, confidence
      output: seal/qualify/hold/void, 888_hold_triggers

  - geox_get_transform_log:
      input: operation_id
      output: full_transform_chain, provenance
```

**Sample Agent Workflow**
```python
# Example: Agent interprets seismic section
result = await mcp.geox_generate_contrast_canon(
    seismic_image="section_001.png"
)

# Agent reviews all 5 views
for view in result.views:
    analysis = await agent.analyze(view.image)

# Agent requests governed interpretation
interpretation = await mcp.geox_interpret_with_governance(
    seismic_image="section_001.png",
    interpretation_goal="Identify faults and estimate throw"
)

# Check verdict
if interpretation.verdict == "HOLD":
    await agent.escalate_to_human(
        reason=interpretation.perception_bridge_warning
    )
```

---

### 4. Theory Page (`/theory`)

**Theory of Anomalous Contrast**

```
The Problem:
79% of expert interpreters fail on synthetic seismic data.
Not because data is poor — because display artifacts
are mistaken for geological signal.

The Solution:
pixels → transforms → physics → decision

Every vision operation must answer:
1. What physical quantity do we care about?
2. What transforms between pixels and that quantity?
3. How do we limit damage when pixels lie?

AC_Risk = U_phys × D_transform × B_cog

Where:
- U_phys: Non-uniqueness of inverse problem
- D_transform: Non-invertibility of display operations
- B_cog: Observer overconfidence (Bond et al. 2007)
```

**Visual Diagram**
```
PHYSICAL DOMAIN          DISPLAY DOMAIN          PERCEPTUAL DOMAIN
(Truth)                  (Visualization)         (Human/AI)
    ↓                        ↓                        ↓
Impedance contrast    →  Colormap choice      →  Edge detection
Waveform similarity   →  Dynamic range       →  Pattern completion
Geological reality    →  Filter kernels      →  "I see a fault"

⚠️ ANOMALOUS CONTRAST ⚠️
When display features are mistaken for physical reality
```

---

### 5. Cases Page (`/cases`)

**Case 1: Map Georeference**
- Input: Scanned Malay Basin geological map
- Challenge: No embedded coordinates, unknown projection
- Process: GCP detection → OCR validation → AC_Risk = 0.42 → QUALIFY
- Output: GeoTIFF with uncertainty envelope

**Case 2: Analog Log Digitization**
- Input: 1980s paper neutron-density log
- Challenge: Faded ink, non-standard scale
- Process: Scale detection → Curve tracing → RATLAS validation → AC_Risk = 0.38 → QUALIFY
- Output: LAS file with per-point uncertainty

**Case 3: Seismic Vision Review**
- Input: Screenshot of seismic section from conference presentation
- Challenge: Unknown processing, no well control
- Process: Multi-contrast analysis → Cross-view consistency = 0.45 → AC_Risk = 0.67 → HOLD
- Output: "Cannot verify apparent fault without SEG-Y data"

---

### 6. Docs Page (`/docs`)

**Documentation Structure**
```
Getting Started:
- Quickstart for operators
- Quickstart for AI agents
- Installation & setup

Core Concepts:
- Theory of Anomalous Contrast
- AC_Risk calculation
- Constitutional floors (F1-F13)
- Verdict system (SEAL/QUALIFY/HOLD/VOID)

API Reference:
- MCP tool schemas
- App endpoints
- Python SDK

Governance:
- GEOX Vision Dev Charter
- External Integration Guide
- Forge Hardened Roadmap
```

---

## What NOT to Include

### ❌ No Hype SaaS Copy
- "Revolutionizing subsurface intelligence"
- "AI-powered insights"
- "Transform your workflow"

### ❌ No Fake Dashboards
- Polished screenshots of non-existent features
- Mock data presented as real
- "Live demo" that doesn't work

### ❌ No Product Sprawl
- 20 tools when 5 are serious
- Feature parity claims
- Roadmap promises without dates

### ❌ No Black Box Claims
- "Our AI detects faults"
- "Proprietary algorithms"
- Missing transform documentation

---

## Technical Implementation

### Stack Recommendation
```
Frontend: Static site (Astro/Next.js) or simple HTML
- No complex auth required for public site
- Apps hosted separately with proper auth

Hosting: Cloudflare Pages / Vercel / Netlify
- CDN for global access
- Free tier sufficient

Domain: geox.arif-fazil.com
- CNAME to hosting provider
- SSL automatic

MCP Endpoint: geox.arif-fazil.com/mcp/v1/
- FastMCP server
- SSE or stdio transport
- OpenAPI schema
```

### Content Sources
```
Site content pulls from:
- GEOX_VISION_DEV_CHARTER.md
- EXTERNAL_INTEGRATION_GUIDE.md
- FORGE_HARDENED_VISION.md
- Tool schemas (auto-generated)
- App manifests (auto-generated)
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Site clarity | < 30s to understand GEOX | User testing |
| MCP adoption | 100+ tool calls/week | Telemetry |
| App usage | 10+ sessions/week | Analytics |
| HOLD trigger rate | 15-25% of vision ops | AC_Risk logs |
| Documentation completeness | All tools documented | Checklist |

---

## Immediate Next Steps

### Week 1: Site Skeleton
- [ ] Set up Astro/Next.js project
- [ ] Create page structure
- [ ] Write homepage copy
- [ ] Deploy to geox.arif-fazil.com

### Week 2: MCP Documentation
- [ ] Auto-generate tool schemas
- [ ] Write sample workflows
- [ ] Create /mcp page
- [ ] Test with Claude Desktop

### Week 3: Apps Showcase
- [ ] Create /apps page
- [ ] Add status badges
- [ ] Link to working tools
- [ ] Add AC_Risk console

### Week 4: Content Polish
- [ ] /theory page with ToAC explanation
- [ ] /cases with real examples
- [ ] /docs with full API reference
- [ ] SEO optimization

---

*DITEMPA BUKAN DIBERI*
*The site is the trust surface. Make it honest.*
