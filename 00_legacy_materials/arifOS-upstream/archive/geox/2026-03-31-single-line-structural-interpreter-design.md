# GEOX Single-Line Structural Interpreter — Design Spec
**Date:** 2026-03-31
**Status:** SEALED — approved by Arif Fazil
**Version:** 0.1.0
**Floors:** F1 · F4 · F7 · F9 · F13
**Seal:** DITEMPA BUKAN DIBERI

---

## 0. Architecture Update (2026-03-31 — post-brainstorm refinement)

**Three-band MCP split:**

| Band | Scope | Tools |
|---|---|---|
| **A — Raster-only** ← this plan | PNG/JPG seismic image | load, contrast_views, feature_extract, build_candidates, rank, report |
| **B — Trace-domain** | SEG-Y / ZGY seismic | load_line, compute_attributes_2d, compute_attributes, hc_summary |
| **C — Event/waveform** | Microseismic, earthquake | event_context, compare_interpretations |

This plan implements **Band A only**. Bands B and C are separate plans.

**Non-negotiable: Common Output Envelope**
Every GEOX tool must return the same JSON envelope shape:
```json
{
  "ok": true,
  "verdict": "QUALIFY",
  "source_domain": "geox-earth-witness",
  "uncertainty": { "level": 0.11, "type": "...", "notes": [] },
  "contrast_metadata": { "processing_steps": [], "display_bias_risk": "medium" },
  "governance": { "floors_ok": ["F1","F4","F7"], "warnings": [] },
  "result": {}
}
```

---

## 1. Problem Statement

Given a single 2D seismic section (image or SEG-Y), produce a governed structural interpretation that:
- Does **not** let an LLM guess geology directly from pixels
- Forces the correct order: data → physics attributes → ruled geology → interpretation
- Labels every output with epistemic confidence (CLAIM / PLAUSIBLE / HYPOTHESIS)
- Directly addresses Bond et al. (2007) display-bias failure: 79% expert error on uninterpreted synthetic

---

## 2. What Already Exists (do not re-forge)

| Component | Location | Status |
|---|---|---|
| Contrast Canon views (CLAHE, Gaussian, Sobel) | `tools/seismic_visual_filter.py` | ✅ complete |
| `ContrastMetadata` schema | `geox_schemas.py:167` + `tools/contrast_metadata.py` | ✅ complete |
| `AttributeStack` + `AttributeVolume` schemas | `geox_schemas.py:500–578` | ✅ complete |
| `SeismicAttributesTool` (mock compute) | `geox_tools.py:681` + `tools/seismic_attributes_tool.py` | ✅ mock, needs real compute |
| Seismic attribute taxonomy | `knowledge/seismic_attribute_taxonomy.yaml` | ✅ complete |

---

## 3. What Needs to Be Forged

### 3.1 New Pydantic Schemas

Location: `arifos/geox/schemas/structural_interp.py` (new file)

```python
class SeismicImageInput(BaseModel):
    image_path: str
    line_id: str
    domain: Literal["time", "depth", "unknown"] = "unknown"
    polarity: Literal["normal", "reverse", "unknown"] = "unknown"
    vertical_exaggeration: float | None = None
    scale_known: bool = False
    pixel_to_ms: float | None = None  # ms per pixel (vertical)
    pixel_to_m: float | None = None   # m per pixel (horizontal)
    notes: str | None = None

class SeismicView(BaseModel):
    view_id: str
    source_line_id: str
    processing_chain: list[str]       # ["grayscale", "clahe", "edge_enhance"]
    display_params: dict[str, Any]
    output_path: str | None = None

class FeatureSet(BaseModel):
    view_id: str
    lineaments: list[dict[str, Any]]       # [{x0,y0,x1,y1, strength, dip_deg}]
    discontinuities: list[dict[str, Any]]  # [{x,y, type, strength}]
    dip_field: list[dict[str, Any]]        # [{x,y, dip_deg, azimuth_deg}]
    continuity_map_ref: str | None = None
    chaos_map_ref: str | None = None

class StructuralCandidate(BaseModel):
    candidate_id: str
    family: Literal["normal_fault", "reverse_fault", "fold", "duplex",
                    "stratigraphic", "flower", "inversion", "unknown"]
    faults: list[dict[str, Any]]
    horizons: list[dict[str, Any]]
    support_views: list[str]           # view_ids supporting this candidate
    geometry_score: float              # [0,1] — structural plausibility
    stability_score: float             # [0,1] — stable across contrast views
    geology_score: float               # [0,1] — rule engine pass rate
    warnings: list[str]
    uncertainty: float                 # F7 — [0.03, 0.15]
    epistemic_tag: Literal["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE"]

class InterpretationResult(BaseModel):
    line_id: str
    best_candidate_id: str
    alternatives: list[StructuralCandidate]
    confidence: float                  # [0, 1], bounded
    bias_audit: dict[str, Any]         # display_sensitivity, notes
    two_d_limits: list[str]            # what cannot be claimed on 2D
    missing_information: list[str]
    summary: str                       # LLM-written, after all structured inputs
    verdict: Literal["PASS", "QUALIFY", "HOLD", "GEOX_BLOCK"]
    telemetry: dict[str, Any]
```

### 3.2 New Tool Modules

#### `tools/seismic_image_ingest.py` — Stage 1
- Read PNG/JPG/NPY
- Detect and crop seismic panel (remove colorbar, axis labels)
- Normalize to grayscale canonical form
- Extract/store metadata: `display_params`, `source_quality`, `domain`, `scale_known`
- Output: `SeismicImageInput` + normalized array

#### `tools/seismic_contrast_views.py` — Stage 2
- Reuse `SeismicVisualFilterTool` filter stack
- Add: linear stretch, histogram equalization, multiple VE display modes
- Output: `list[SeismicView]` — 5–7 variants
- **Key rule**: if a structural feature appears in only 1 of 6 views → `stability_score < 0.3`

#### `tools/seismic_feature_extract.py` — Stage 3
- From each view: extract lineaments (Sobel + Canny from existing filter tool)
- Estimate local dip field (gradient direction)
- Build continuity map (per-pixel coherence proxy)
- Detect discontinuities (high-gradient breaks in lineaments)
- Output: `FeatureSet` per view — labelled `image_derived_proxy`, NOT `seismic_attribute`
- All outputs carry `ContrastMetadata` with `physical_axes: ["image_gradient_proxy"]`

#### `tools/seismic_structure_rules.py` — Stage 5 (geological rule engine)
- Reject impossible geometries:
  - Faults without displacement evidence → penalize `geometry_score`
  - Horizons crossing without fault evidence → reject
  - Thrust interpretations inconsistent with observed vergence → penalize
  - Fold limbs violating continuity without fault → penalize
- Template families: extensional, fold-only, reverse/thrust, flower, stratigraphic
- Output: scored `list[StructuralCandidate]`

#### `tools/seismic_candidate_ranker.py` — Stage 4+6
- Build structural candidates from feature sets
- Aggregate: `stability_score` from view-count agreement
- Apply rule engine scores
- Rank by: `0.4 * geometry + 0.3 * stability + 0.3 * geology`
- Flag: Bond-style bias warning if `stability_score < 0.4`
- Output: ranked `list[StructuralCandidate]` + `InterpretationResult` draft

#### `tools/seismic_report_writer.py` — Stage 7
- LLM writes `summary` ONLY after receiving structured outputs
- Mandatory 2D limits block: out-of-plane, no true 3D geometry, no volumetrics
- Output: `InterpretationResult` + markdown report + JSON artifact

---

## 4. MCP Verbs (exposed to LLM)

| Verb | Chains to |
|---|---|
| `geox_load_seismic_image` | `seismic_image_ingest.py` |
| `geox_generate_contrast_views` | `seismic_contrast_views.py` |
| `geox_extract_image_features` | `seismic_feature_extract.py` |
| `geox_build_structural_candidates` | `seismic_structure_rules.py` + `seismic_candidate_ranker.py` |
| `geox_rank_structural_models` | `seismic_candidate_ranker.py` |
| `geox_interpret_single_line` | All of the above, chained |

LLM should call only `geox_interpret_single_line`. GEOX internally chains the rest.

---

## 5. Governance Contracts

### GEOX_BLOCK triggers
- Image-only with no scale/polarity → verdict `HOLD`, output labelled `HYPOTHESIS`
- Structural candidate only in 1 of 6 contrast views → `stability_score < 0.3` → warned
- Any HC/DHI claim from image-only → `GEOX_BLOCK`, route to EarthModelTool
- 3D geometry or volumetric claim → `GEOX_BLOCK`, log to VAULT_999

### Epistemic labelling (mandatory on every output)
```
CLAIM       — visible reflector/fault/fold pattern (image evidence)
PLAUSIBLE   — structural family ranking from rule engine
HYPOTHESIS  — HC implication from image-only evidence
```

### 2D limits block (mandatory in every report)
```
- No true 3D trap geometry, closure area, or spill point
- No reliable areal extent or true volumetrics
- No confident fault network connectivity (out-of-plane effects)
- No direct "HC here" claims — always "DHI candidate with high uncertainty"
```

---

## 6. Best First Milestone (MVP)

**Input:** `section.png` + minimal metadata
**Output:**
- `contrast-panel.png` — 6-view grid (linear, CLAHE, edge-enhanced, etc.)
- `fault-overlay.png` — discontinuity candidates on original section
- `horizon-overlay.png` — reflector candidates on original section
- `interpretation.json` — `InterpretationResult` with all scores
- `interpretation.md` — short governed markdown report

---

## 7. Bond et al. (2007) Test Case

The paper's uninterpreted synthetic (Figure 1) is the validation target.
Only 21% of 79 experts correctly identified the inversion tectonic setting.

GEOX pipeline would deliver:
1. 6 contrast views showing same ambiguity in all → `stability_score` reflects true difficulty
2. Feature extraction: three fault strands + fold geometry extracted
3. Rule engine: inversion candidate (fold-thrust with opposing dip panels) scores highest
4. Bias audit: "Multiple tectonic models fit equally well — Bond et al. (2007) failure mode detected"
5. Output: `verdict: QUALIFY`, `confidence: 0.55–0.65`, `best_candidate: inversion_fold_thrust`

This is honest uncertainty, not false precision.

---

## 8. Implementation Order

1. `structural_interp.py` — schemas first (Pydantic, no compute)
2. `seismic_image_ingest.py` — loader + normalize (pure image ops)
3. `seismic_contrast_views.py` — thin wrapper over SeismicVisualFilterTool
4. `seismic_feature_extract.py` — lineament + dip extraction
5. `seismic_structure_rules.py` — rule engine (geological templates)
6. `seismic_candidate_ranker.py` — scoring + ranking
7. `seismic_report_writer.py` — structured output
8. MCP verb wiring (`geox_mcp_server.py`)
9. Test: Bond synthetic PNG → full pipeline

---

*arifOS telemetry v2.1 · @GEOX v0.3.0 · pipeline 222_REFLECT · floors F1 F4 F7 F9 F13 · seal DITEMPA BUKAN DIBERI*
