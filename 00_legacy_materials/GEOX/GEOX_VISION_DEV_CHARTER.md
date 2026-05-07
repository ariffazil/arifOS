# GEOX Vision Intelligence Development Charter

> **Global Framing:** GEOX Vision is not "make pretty pictures" — it is:
> **"Recover physically-plausible, georeferenced information from images, under Theory of Anomalous Contrast."**

**Authority:** Muhammad Arif bin Fazil
**Status:** CANONICAL
**Seal:** 999_VAULT
**Motto:** *DITEMPA BUKAN DIBERI*

---

## The Three Questions (Non-Negotiable)

Every vision feature must answer explicitly:

1. **What is the physical quantity we care about?**
   - Must be measurable, units-declared, physics-grounded
   - Examples: `depth [m]`, `impedance [kg/m²·s]`, `closure height [m]`, `porosity [fraction]`

2. **What is the transform stack between that quantity and the pixels?**
   - Document every operation: capture → storage → display → enhancement → digitization
   - No hidden transforms allowed (F4 Clarity violation)

3. **How do we limit damage when pixels lie or mislead?**
   - AC_Risk calculation: `U_phys × D_transform × B_cog`
   - 888_HOLD triggers when AC_Risk > 0.5
   - Human override always available (F13 Sovereign)

---

## Working Rule (Violation = VOID)

> **Never ship a vision feature whose outputs can't be traced:**
> `pixels → transforms → physics → decision`

---

## Capability Domains

### 1. Georeferencing Maps (Status: 🟡 → Governed)

**Mental Model:** Map warping, not magic. Aligning an image to Earth.

**Architecture:**
```
georeference_map_core (pure geometry)
    ↓
GCPDetector (vision/OCR for tie points)
    ↓
GeoreferenceAuditor (ToAC enforcement)
    ↓
AC_Risk + Verdict
```

**ToAC Enforcement:**
- OCR collars / grid labels
- Extract scale bars
- Compare claimed vs detected bounds
- Evaluate realism (coastline shapes vs basemap)
- `ac_risk > 0.5` → draft mode, user confirmation required

**Storage Requirements:**
- Transform matrix
- GCP list + residuals
- OCR evidence
- Contrast metadata

---

### 2. Analog Petrophysics Digitization (Status: 🔴 → New Stack)

**Mental Model:** Document + chart digitization under physics constraints.

**Pipeline (Testable Units):**

```
Stage 1: Scale & Depth Detection
├── Detect scale bars, rulers, depth ticks
├── Hough lines + OCR (simple CV before fancy models)
└── Output: depth-pixel mapping with uncertainty

Stage 2: Axis / Label OCR
├── Charts/crossplots: detect axes, read min/max, units
├── Logs: track curves vs known templates
└── Output: axis calibration with confidence

Stage 3: Curve Tracing
├── Colored trace → polyline in axis space
├── User corrections: snap points, delete outliers
└── Output: digitized curve with provenance

Stage 4: Physics Checks
├── Monotonicity of depth
├── Range checks vs RATLAS
├── Sanity checks (RHOB limits, φ ≤ 0.5)
└── Output: physics plausibility score

Stage 5: Risk & Verdict
├── Combine: OCR confidence + scale consistency + physics
├── Compute AC_Risk
└── Emit: SEAL / QUALIFY / HOLD / VOID
```

**Optimization Priority:** Controlled error over speed. Show exactly where guessing, make human fix easy.

---

### 3. Visual Seismic Interpretation (Status: 🟡 Mock → Governed Real)

**Mental Model:** Perception bridge accepting SEGY or image, running vision models, reconciling with physics.

**Architecture:**
```
GovernedSeismicVLM
├── Input: image + interpretation_goal (faults/horizons/channels)
├── Stage 1: Contrast Canon
│   └── Generate multi-contrast views
├── Stage 2: Vision Inference
│   └── Call VLM/vision backends on each view
├── Stage 3: Multi-View Consistency
│   └── Features appearing only under aggressive enhancement → artifact
├── Stage 4: Physics Anchoring
│   ├── SEGY path: use existing attributes
│   └── Image path: infer transforms, label "display relative"
├── Stage 5: AC_Risk Calculation
│   └── U_phys × D_transform × B_cog
└── Stage 6: Verdict (SEAL/QUALIFY/HOLD/VOID)
```

**Hard Rule (F9 Anti-Hantu):**
Image-only interpretations **cannot** directly drive irreversible decisions without:
- Cross-check on underlying volumes or wells
- Human sign-off logged to 999_VAULT

**Agent Mindset:**
> "My job is not to say 'the channel is here'. My job is to say 'if you believe the channel is here based on this image, here is how risky that belief is, and here is what physics says.'"

---

### 4. Seismic Attributes from Images (Status: 🟡 → DL + ToAC)

**Mental Model:** Extend gradient-based attributes with DL-based attributes, clearly marking transform dependencies.

**Implementation:**
```
seismic_feature_extract v2
├── Existing: gradient-based (coherence, dip, curvature)
├── New: DL-based (UNet/Tiramisu for faults/salt/geobodies)
└── Metadata per attribute:
    ├── data_source (SEGY vs image)
    ├── transform_stack
    ├── calibration_link (wells / synthetic)
    └── ac_risk_contribution
```

**ToAC Rule:**
If attribute comes from image-only AND transform stack is aggressive (CLAHE, exotic colormap) → `D_transform` high → AC_Risk high → 888_HOLD likely.

---

## AC_Risk Calculation (Canonical)

```python
AC_Risk = U_phys × D_transform × B_cog

Where:
- U_phys (Physical Ambiguity): Non-uniqueness of inverse problem
  - Measured: candidate model divergence, well control distance
  - Range: [0.0, 1.0]

- D_transform (Display Distortion): Non-invertibility of transform stack
  - Measured: sum of (1 - invertibility) for each transform
  - Range: [0.0, 1.0]
  - Reference transforms in TRANSFORM_REGISTRY

- B_cog (Cognitive Bias): Observer overconfidence
  - Baseline: 0.79 (Bond et al. 2007 failure rate)
  - Adjusted: 0.40 (multi-interpreter), 0.20 (physics-validated)
  - Range: [0.0, 1.0]

Thresholds:
- AC_Risk < 0.25: SEAL (auto-proceed)
- 0.25 ≤ AC_Risk < 0.50: QUALIFY (proceed with caveats)
- 0.50 ≤ AC_Risk < 0.75: HOLD (human review required)
- AC_Risk ≥ 0.75: VOID (unsafe to proceed)
```

---

## Agent Briefing Pattern

When assigning vision tasks, use this template:

### 1. State the Physical Target
> "We want depth-calibrated porosity from this scanned neutron-density chart."

### 2. State the Known Transforms
> "This is a scan, unknown gamma, unknown contrast. We will have to estimate axis mapping and color mapping."

### 3. State ToAC Expectations
> "You must:
> - Identify the transform chain
> - Compute AC_Risk
> - Refuse to SEAL if AC_Risk > 0.5
> - Expose all assumptions for human QC"

### 4. Point to External Reality
> "We know georeferencers, digitization shops, seismic AI systems already exist. Use them as reference points, not as truth."

### 5. Define "Done" in Governance Terms
> "Done =:
> - Function works
> - Transforms logged
> - AC_Risk computed
> - 888 HOLD triggers wired for high-risk outputs
> - Example notebooks showing failure cases"

---

## Transform Registry (Reference)

| Transform | Invertibility | Risk Weight | Typical Use |
|-----------|---------------|-------------|-------------|
| Linear scaling | 1.0 | Low | Amplitude normalization |
| Colormap mapping | 0.7 | Medium | Visual display |
| AGC (rms window) | 0.4 | High | Dynamic range compression |
| CLAHE | 0.2 | Very High | Local contrast enhancement |
| Vertical exaggeration > 2x | 0.3 | High | Structural visualization |
| Perspective warp (georeferencing) | 0.8 | Medium | Map projection |
| OCR digitization | 0.5 | High | Text extraction |
| Curve tracing | 0.6 | Medium | Chart digitization |

---

## Implementation Roadmap

### Phase 0: Foundation (Now)
- [ ] Implement AC_Risk calculator in `GEOX/ENGINE/ac_risk.py`
- [ ] Create TransformRegistry with invertibility scores
- [ ] Add B_cog baseline from Bond 2007

### Phase 1: Georeferencing (0-30 days)
- [ ] Build GCPDetector with OCR
- [ ] Implement GeoreferenceAuditor
- [ ] Wire AC_Risk to 888_HOLD

### Phase 2: Analog Digitization (30-90 days)
- [ ] Scale/depth detection module
- [ ] Axis/label OCR pipeline
- [ ] Curve tracing with user correction
- [ ] Physics validation vs RATLAS

### Phase 3: Vision Models (60-120 days)
- [ ] GovernedSeismicVLM adapter
- [ ] Multi-contrast view generation
- [ ] Cross-view consistency checking
- [ ] VLM-to-physics reconciliation

### Phase 4: DL Attributes (90-180 days)
- [ ] UNet/Tiramisu fault detection
- [ ] Salt body segmentation
- [ ] Geobody extraction
- [ ] Transform-aware metadata

---

## Constitutional Floors for Vision

| Floor | Vision Implementation |
|-------|----------------------|
| **F1 Amanah** | Every transform reversible; rollback paths documented |
| **F2 Truth** | Physical quantities explicit; no inferred units |
| **F4 Clarity** | Transform stack logged; display vs physics separated |
| **F7 Humility** | Uncertainty ≥ 0.15 for all vision-derived quantities |
| **F9 Anti-Hantu** | DISPLAY-ONLY triggers automatic HOLD |
| **F11 Audit** | Full provenance: pixels → transforms → output |
| **F13 Sovereign** | Human override on all high AC_Risk outputs |

---

## References

- Bond et al. (2007): 79% expert failure rate on seismic interpretation
- ToAC: Theory of Anomalous Contrast (GEOX Core Doctrine)
- EARTH.CANON_9: Physics foundation for validation
- RATLAS: Material database for analog cross-reference

---

*DITEMPA BUKAN DIBERI*
*Vision Intelligence: Governed, Not Given*
*AC_Risk: Calculated for Every Pixel*
