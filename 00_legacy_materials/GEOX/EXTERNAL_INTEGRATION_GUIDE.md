# GEOX Vision: External Integration Guide

> **Strategy:** Leverage proven domain repos + ToAC governance layer
> **Status:** INTEGRATION ROADMAP
> **Seal:** DITEMPA BUKAN DIBERI

---

## Integration Philosophy

**Don't reinvent. Govern.**

External codebases provide:
- Battle-tested algorithms
- Proven UX patterns
- Training data pipelines

GEOX provides:
- AC_Risk calculation
- Transform logging
- 888_HOLD triggers
- Constitutional enforcement

**Pattern:** External tool → GEOX wrapper → AC_Risk → Verdict

---

## 1. Georeferencing (MapWarper + GeoReferencer)

### External Resources
| Resource | What It Does | GEOX Value |
|----------|--------------|------------|
| [MapWarper](https://github.com/timwaters/mapwarper) | Full open georeferencer (GCP picking, warping, GeoTIFF) | GCP data model, residual calc, warp pipeline |
| [GeoReferencer](https://github.com/vitec-memorix/GeoReferencer) | GCP application and raster warping | Warp algorithms, transform chains |
| [Mundi AI](https://mundi.ai/ai-georeferencing-for-aerial-imagery) | AI-assisted GCP proposal | Pattern for AI-proposed + human-confirm |

### Integration Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ EXTERNAL: MapWarper / GeoReferencer                          │
│ ├── GCP data model (point pairs)                             │
│ ├── Residual error calculation                               │
│ ├── Warp algorithms (affine, polynomial)                     │
│ └── GeoTIFF export                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│ GEOX: GeoreferenceAuditor (ToAC Wrapper)                     │
│ ├── GCPDetector (CV + OCR for candidate GCPs)                │
│ ├── Human approval/edit interface                            │
│ ├── AC_Risk calculation:                                     │
│ │   U_phys = f(GCP residuals, bound divergence)              │
│ │   D_transform = warp complexity                            │
│ │   B_cog = 0.79 (unaided) or 0.40 (verified)                │
│ └── Verdict: SEAL/QUALIFY/HOLD                               │
└─────────────────────────────────────────────────────────────┘
```

### Concrete Steps
1. **Study MapWarper's GCP model** → Copy data structures
2. **Study GeoReferencer's warp pipeline** → Adapt algorithms
3. **Build GCPDetector**:
   - Hough lines for grid detection
   - OCR (Tesseract/EasyOCR) for labels
   - Scale bar detection
4. **Wrap in GeoreferenceAuditor**:
   - Log all transforms
   - Calculate residuals
   - AC_Risk > 0.5 → HOLD

---

## 2. Analog Digitization (WebPlotDigitizer + Geomega)

### External Resources
| Resource | What It Does | GEOX Value |
|----------|--------------|------------|
| [Geomega](http://www.geomega.hu/digitization-of-logs-and-maps/) | Legacy map/log digitization workflows | Error patterns, QA steps |
| [Seismic-well-tie](https://github.com/raquelsilva/Seismic-well-tie) | Well tie notebooks | Curve calibration patterns |
| [Geophysical notes](https://github.com/aadm/geophysical_notes) | Petrophysics workflows | Typical digitization errors |
| WebPlotDigitizer (concept) | Pick axes → map pixels → trace | Core interaction pattern |

### Integration Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ EXTERNAL PATTERNS: WebPlotDigitizer / Geomega                │
│ ├── User clicks reference points (axes, depth)               │
│ ├── Pixel→value transform inferred                           │
│ ├── Curve tracing (auto + manual)                            │
│ └── Export to CSV/LAS                                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│ GEOX: AnalogDigitizationPipeline                             │
│ Stage 1: Scale & Depth Detection                             │
│   ├── Hough lines (external OpenCV)                          │
│   └── OCR with confidence (external Tesseract)               │
│ Stage 2: Axis/Label OCR                                      │
│   └── Pattern matching vs known log templates                │
│ Stage 3: Curve Tracing                                       │
│   ├── Color separation                                       │
│   └── User correction interface                              │
│ Stage 4: Physics Checks (GEOX native)                        │
│   ├── Depth monotonicity                                     │
│   ├── RATLAS plausibility                                    │
│   └── Range checks (RHOB, φ limits)                          │
│ Stage 5: AC_Risk & Verdict                                   │
│   └── High risk on: few anchors, low OCR, physics mismatch   │
└─────────────────────────────────────────────────────────────┘
```

### Concrete Steps
1. **Study Geomega workflows** → Document typical error modes
2. **Implement pixel→value mapper** (WebPlotDigitizer pattern)
3. **Add curve tracing**:
   - OpenCV color clustering
   - Skeletonization
   - Point snapping
4. **Physics validation layer**:
   - Query RATLAS for expected ranges
   - Flag outliers
5. **AC_Risk integration**:
   - Few manual anchors = high U_phys
   - Low OCR confidence = high D_transform
   - Physics mismatch = AC_Risk spike

---

## 3. Seismic Vision (seismiqb + Seismic-App)

### External Resources
| Resource | What It Does | GEOX Value |
|----------|--------------|------------|
| [seismiqb](https://github.com/BEEugene/seismiqb) | DL for seismic (horizons, faults, geobodies) | Model architectures, training patterns |
| [MS seismic-deeplearning](https://github.com/microsoft/seismic-deeplearning/) | Curated models + training | Production-ready pipelines |
| [Seismic-App](https://github.com/gecos-lab/Seismic-App) | SAM2 + seismic GUI | Image-centric segmentation pattern |
| [GeoX](https://github.com/Alpha-Innovator/GeoX) / [GeoGround](https://github.com/zytx121/GeoGround) / [GeoPixel](https://github.com/mbzuai-oryx/GeoPixel) | Geo VLMs | Vision encoders for RS/maps |

### Integration Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ EXTERNAL: seismiqb / MS seismic-deeplearning                 │
│ ├── Volume patching & augmentation                           │
│ ├── UNet/Tiramisu architectures                              │
│ ├── Fault/salt/geobody segmentation                          │
│ └── Attribute-conditioned predictions                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│ EXTERNAL: Seismic-App                                        │
│ ├── SAM-style segmentation from clicks                       │
│ ├── Seismic GUI interactions                                 │
│ └── Image-centric workflows                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│ GEOX: GovernedSeismicVLM (ToAC Orchestrator)                 │
│ Stage 1: Multi-Contrast Generation (5 views)                 │
│ Stage 2: External Model Inference                            │
│   ├── seismiqb attributes (physics path)                     │
│   ├── SAM segmentation (image path)                          │
│   └── GeoX VLM (language path)                               │
│ Stage 3: Cross-View Consistency (GEOX native)                │
│   └── Flag features only appearing under enhancement         │
│ Stage 4: Physics Reconciliation (GEOX native)                │
│   └── Compare VLM to computed attributes                     │
│ Stage 5: AC_Risk & Verdict                                   │
│   └── Image-only + aggressive transforms = HOLD              │
└─────────────────────────────────────────────────────────────┘
```

### Concrete Steps
1. **Study seismiqb** → Copy volume patching, model architectures
2. **Study Seismic-App** → Adapt SAM-click interaction
3. **Implement multi-view wrapper**:
   - Generate 5 contrast variants
   - Run external model on each
   - Aggregate with consistency check
4. **AC_Risk for seismic**:
   - SEGY available: lower U_phys
   - Image-only + CLAHE: high D_transform
   - Cross-view inconsistency: HOLD

---

## 4. Attributes from Images (2025 Nature Paper)

### External Resource
[Nature 2025: "Exploring the potential of extracting seismic attributes from image"](https://www.nature.com/articles/s41598-025-21949-9)

### Key Findings to Encode
| Attribute | Image-Only Feasibility | D_transform Default |
|-----------|------------------------|---------------------|
| Coherence | Moderate (edge-based) | 0.4 |
| Dip/Azimuth | Low (phase loss) | 0.6 |
| Curvature | Low (smoothing artifacts) | 0.6 |
| Spectral decomposition | Very low | 0.8 |
| Amplitude envelope | Moderate | 0.4 |

### Integration
```python
# In seismic_feature_extract.py
ATTRIBUTE_IMAGE_RISK = {
    "coherence": {"feasible": True, "d_transform": 0.4},
    "dip": {"feasible": False, "d_transform": 0.6, "requires_segy": True},
    "spectral": {"feasible": False, "d_transform": 0.8, "requires_segy": True},
}

def compute_attribute_with_risk(attribute_type, source_type):
    if source_type == "image" and not ATTRIBUTE_IMAGE_RISK[attribute_type]["feasible"]:
        return {
            "value": None,
            "verdict": Verdict.HOLD,
            "explanation": f"{attribute_type} requires SEG-Y (see Nature 2025)"
        }
```

---

## 5. Vision-Language Backends (GeoX + GeoGround + GeoPixel)

### External Resources
| Resource | What It Provides |
|----------|------------------|
| [GeoX](https://github.com/Alpha-Innovator/GeoX) | RS vision encoders + VLM |
| [GeoGround](https://github.com/zytx121/GeoGround) | Grounding for RS imagery |
| [GeoPixel](https://github.com/mbzuai-oryx/GeoPixel) | Fine-grained geo semantic segmentation |
| [G-RSIM](https://github.com/mbzuai-oryx/GeoPixel) | Remote sensing interpretation models |
| [HOOK](https://github.com/mbzuai-oryx/GeoPixel) | Tokenizers for geo RS |

### Integration Pattern
```
┌─────────────────────────────────────────────────────────────┐
│ EXTERNAL: GeoX / GeoGround / GeoPixel (Vision Towers)        │
│ ├── Pre-trained RS vision encoders                           │
│ ├── High-res image tokenizers                                │
│ └── Domain-finetuned VLM heads                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│ GEOX: Adapter Layer                                          │
│ ├── Input: seismic/map image                                 │
│ ├── Preprocess: Contrast Canon (5 views)                     │
│ ├── External VLM inference (GeoX/etc)                        │
│ └── Postprocess: AC_Risk calculation                         │
└─────────────────────────────────────────────────────────────┘
```

### Concrete Steps
1. **Evaluate towers** on seismic/map data
2. **Build adapter** for best performer
3. **Keep ToAC layer unchanged** regardless of tower

---

## Integration Checklist

### Week 1-2: Georeferencing
- [ ] Clone MapWarper, study GCP data model
- [ ] Clone GeoReferencer, study warp algorithms
- [ ] Design GCPDetector (Hough + OCR)
- [ ] Integrate with GeoreferenceAuditor
- [ ] Test with Malay Basin maps

### Week 3-4: Analog Digitization
- [ ] Study Geomega workflows
- [ ] Implement pixel→value mapper
- [ ] Build curve tracing (OpenCV)
- [ ] Add RATLAS physics checks
- [ ] Integrate with AC_Risk

### Month 2: Seismic Vision
- [ ] Clone seismiqb, study architectures
- [ ] Clone Seismic-App, study SAM integration
- [ ] Implement multi-view wrapper
- [ ] Build cross-view consistency check
- [ ] Integrate with GovernedSeismicVLM

### Month 3: Attributes & VLM
- [ ] Read Nature 2025 paper, encode attribute risks
- [ ] Evaluate GeoX/GeoGround/GeoPixel
- [ ] Build adapter for best tower
- [ ] End-to-end testing

---

## AC_Risk Integration Points

For each external tool, add:

```python
# 1. Transform logging
transform_stack = [
    "mapwarper_warp",      # external
    "gcp_manual_edit",     # external + human
    "ocr_extraction",      # GEOX
]

# 2. U_phys calculation
u_phys = calculate_physical_ambiguity(
    gcp_residuals=external_tool.residuals,
    bound_divergence=detected_vs_claimed,
)

# 3. AC_Risk
result = ACRiskCalculator.calculate(
    u_phys=u_phys,
    transform_stack=transform_stack,
    bias_scenario="ai_with_human_verify",
)

# 4. Verdict enforcement
if result.verdict == Verdict.HOLD:
    trigger_888_hold(reason=result.explanation)
```

---

## Risk: External Dependencies

| Risk | Mitigation |
|------|------------|
| External repo unmaintained | Fork and vendor critical code |
| License incompatibility | Check licenses before integration |
| Performance mismatch | Benchmark before production |
| API drift | Pin versions, wrap interfaces |

---

## Summary

| Capability | External Base | GEOX Addition | Time Saved |
|------------|---------------|---------------|------------|
| Georeferencing | MapWarper + GeoReferencer | GeoreferenceAuditor + AC_Risk | 3-4 months |
| Analog Digitization | WebPlotDigitizer pattern + Geomega | Physics validation + AC_Risk | 4-6 months |
| Seismic Vision | seismiqb + Seismic-App | Multi-view + AC_Risk | 6-8 months |
| Attributes | seismiqb + Nature 2025 | Transform-aware metadata | 2-3 months |
| VLM | GeoX/GeoGround/GeoPixel | ToAC governance layer | 3-4 months |

**Net acceleration: 18-25 months of development**

---

*DITEMPA BUKAN DIBERI*
*Leverage external strength. Add GEOX governance. Forge faster.*
