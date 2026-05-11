# FORGE HARDENED: Vision Intelligence Roadmap

> **Status:** HARDENED FOR EXECUTION
> **Date:** 2026-04-10
> **Seal:** 999_VAULT
> **Motto:** *DITEMPA BUKAN DIBERI*

---

## Executive Summary

**Previous State:** Vision architecture scaffolded, AC_Risk calculated, no external integration
**Current State:** Complete external ecosystem mapped, integration patterns defined
**Next State:** Working integrations with ToAC governance

**Time to MVP:** 6-8 weeks (vs 12-18 months from scratch)

---

## Phase 1: Georeferencing (Weeks 1-2)

### Sprint Goal
Working georeferencing with MapWarper patterns + ToAC governance

### Tasks

#### Day 1-2: Study External Code
```bash
# Clone and analyze
git clone https://github.com/timwaters/mapwarper.git
git clone https://github.com/vitec-memorix/GeoReferencer.git

# Extract patterns:
# - GCP data model (point pairs: image_x, image_y, world_x, world_y)
# - Residual calculation (RMS error per GCP)
# - Warp transforms (affine, polynomial order 1-3)
# - GeoTIFF metadata structure
```

#### Day 3-4: Build GCPDetector
```python
# GEOX/arifos/geox/vision/gcp_detector.py
class GCPDetector:
    """
    Detect candidate GCPs from map collars using CV + OCR.
    """

    def detect_grid_intersections(self, image):
        """Hough lines for grid line detection."""
        # OpenCV HoughLinesP
        # Return candidate intersection points

    def ocr_grid_labels(self, image, regions):
        """OCR for longitude/latitude labels."""
        # Tesseract or EasyOCR
        # Return text + confidence per region

    def detect_scale_bar(self, image):
        """Detect scale bar for ground truth validation."""
        # Template matching or heuristics
        # Return scale in px/unit
```

#### Day 5-7: Build GeoreferenceAuditor
```python
# GEOX/arifos/geox/vision/georeference_auditor.py
class GeoreferenceAuditor:
    """
    ToAC governance layer for georeferencing.
    """

    def audit_georeference(self, gcp_list, image, claimed_bounds):
        # 1. Calculate residuals from external warp
        residuals = self.calculate_residuals(gcp_list)

        # 2. Detect vs claimed bounds
        detected_bounds = self.ocr_detect_bounds(image)
        bound_divergence = self.compare_bounds(claimed_bounds, detected_bounds)

        # 3. Scale consistency
        scale_from_bar = self.detect_scale_bar(image)
        scale_from_bounds = self.calculate_scale(claimed_bounds, image.size)
        scale_consistency = self.compare_scales(scale_from_bar, scale_from_bounds)

        # 4. AC_Risk
        from ..ENGINE.ac_risk import VisionGovernance
        risk_result = VisionGovernance.assess_georeferencing(
            bound_divergence=bound_divergence,
            scale_consistency=scale_consistency,
            ocr_confidence=detected_bounds.confidence,
            gcp_residuals=residuals,
        )

        # 5. Verdict
        return {
            "warp_result": external_warp_result,  # From MapWarper pattern
            "gcp_residuals": residuals,
            "bound_divergence": bound_divergence,
            "ac_risk": risk_result,
            "verdict": risk_result.verdict,
            "requires_human_approval": risk_result.verdict in [Verdict.HOLD, Verdict.VOID],
        }
```

#### Day 8-10: Integration & Testing
- Wire into existing `georeference_map.py`
- Test with Malay Basin map samples
- Validate AC_Risk triggers correctly

### Deliverable
```python
# Usage
result = await georeference_map_governed(
    image_path="malay_basin_map.png",
    claimed_bounds=[102.0, 3.0, 107.0, 7.5],
)
# result.geotiff_path
# result.gcp_list
# result.residuals
# result.ac_risk.ac_risk  # e.g., 0.32
# result.verdict  # QUALIFY
# result.requires_human_approval  # False
```

---

## Phase 2: Analog Digitization (Weeks 3-4)

### Sprint Goal
Working digitization pipeline with physics validation

### Tasks

#### Day 1-3: Study External Patterns
- Analyze WebPlotDigitizer interaction model
- Study Geomega digitization workflows
- Document typical error patterns

#### Day 4-7: Build Core Pipeline
```python
# GEOX/arifos/geox/vision/analog_digitizer.py
class AnalogDigitizer:
    """
    Digitize scanned logs, charts, core photos with ToAC governance.
    """

    async def digitize_log(self, image_path, log_type="neutron_density"):
        # Stage 1: Detect scale markers
        scale_result = await self.detect_scale_markers(image_path)

        # Stage 2: OCR axis labels
        axis_result = await self.ocr_axis_labels(image_path, scale_result.roi)

        # Stage 3: User-guided anchor points (WebPlotDigitizer pattern)
        anchors = await self.get_user_anchors_or_auto(image_path)

        # Stage 4: Curve tracing
        pixel_curve = await self.trace_curve(image_path, anchors)

        # Stage 5: Transform to physical values
        physical_curve = self.pixel_to_physical(pixel_curve, anchors)

        # Stage 6: Physics validation
        physics_check = await self.validate_vs_ratlas(physical_curve, log_type)

        # Stage 7: AC_Risk
        risk = self.calculate_digitization_risk(
            ocr_confidence=axis_result.confidence,
            anchor_count=len(anchors),
            physics_plausibility=physics_check.score,
        )

        return DigitizationResult(
            curve=physical_curve,
            ac_risk=risk,
            verdict=risk.verdict,
        )
```

#### Day 8-10: Physics Validation Layer
- RATLAS integration for expected ranges
- Monotonicity checks
- Outlier detection

### Deliverable
```python
result = await digitize_log_curve(
    image_path="legacy_neutron_log.png",
    log_type="NPHI",
)
# result.depth  # [m]
# result.values  # [fraction]
# result.uncertainty  # per-point
# result.ac_risk.ac_risk  # e.g., 0.45
# result.verdict  # QUALIFY
# result.physics_warnings  # ["Value 0.52 exceeds RATLAS max for clean sand"]
```

---

## Phase 3: Seismic Vision (Weeks 5-8)

### Sprint Goal
GovernedSeismicVLM with real backends

### Tasks

#### Day 1-4: Study External Code
```bash
# Deep learning architectures
git clone https://github.com/BEEugene/seismiqb.git
git clone https://github.com/microsoft/seismic-deeplearning.git

# Image-centric workflows
git clone https://github.com/gecos-lab/Seismic-App.git

# Extract:
# - UNet/Tiramisu model definitions
# - Volume patching strategies
# - SAM integration patterns
# - Training data formats
```

#### Day 5-10: Build Integration Layer
```python
# GEOX/arifos/geox/vision/backends/
class SeismiqbBackend:
    """Adapter for seismiqb models."""

    def load_fault_model(self, checkpoint_path):
        # Load seismiqb UNet

    def predict_faults(self, seismic_volume):
        # Run inference
        # Return fault probability volume

class SeismicAppBackend:
    """Adapter for SAM-style segmentation."""

    def segment_from_click(self, image, click_point):
        # SAM-based segmentation
        # Return mask

class GeoXVLMBackend:
    """Adapter for GeoX/GeoGround vision towers."""

    async def infer(self, image, prompt):
        # Run geo-domain VLM
        # Return structured interpretation
```

#### Day 11-16: Enhance GovernedSeismicVLM
```python
class GovernedSeismicVLM:
    async def interpret(self, image, goal, backends=None):
        # Stage 1: Contrast views (existing)
        views = self.generate_contrast_views(image)

        # Stage 2: Multi-backend inference (new)
        all_hypotheses = []
        for backend in backends or [self.default_backend]:
            for view in views:
                result = await backend.infer(view.image, goal)
                all_hypotheses.extend(result.hypotheses)

        # Stage 3: Cross-view consistency (existing)
        consistency = self.check_consistency(all_hypotheses)

        # Stage 4: Physics anchoring with seismiqb (new)
        if "seismiqb" in backends:
            attributes = await self.compute_attributes(image)
            physics_agreement = self.validate_hypotheses(all_hypotheses, attributes)

        # Stage 5: AC_Risk (existing)
        risk = self.calculate_risk(consistency, physics_agreement, ...)

        return InterpretationResult(...)
```

### Deliverable
```python
result = await governed_vlm.interpret(
    image="seismic_section.png",
    goal="Identify faults and horizons",
    backends=["seismiqb", "geox_vlm", "sam"],
)
# result.hypotheses  # From multiple backends
# result.consistency_score  # Cross-view agreement
# result.physics_agreement  # Match to attributes
# result.ac_risk.ac_risk  # e.g., 0.28
# result.verdict  # QUALIFY
```

---

## Phase 4: Attributes from Images (Weeks 9-10)

### Sprint Goal
Attribute extraction with Nature 2025 risk model

### Tasks

#### Day 1-2: Encode Nature 2025 Findings
```python
# GEOX/arifos/geox/vision/attribute_risk.py
ATTRIBUTE_IMAGE_FEASIBILITY = {
    # From Nature 2025 paper
    "coherence": {
        "feasible": True,
        "d_transform": 0.4,
        "notes": "Edge-based, moderately robust"
    },
    "dip_magnitude": {
        "feasible": False,
        "d_transform": 0.6,
        "notes": "Phase information lost in image"
    },
    "spectral_decomposition": {
        "feasible": False,
        "d_transform": 0.8,
        "notes": "Frequency content destroyed by colormap"
    },
    "curvature": {
        "feasible": False,
        "d_transform": 0.6,
        "notes": "Second-order derivative, noise-sensitive"
    },
}
```

#### Day 3-7: Extend seismic_feature_extract
```python
async def extract_attribute_with_risk(attribute_type, source_type, image):
    if source_type == "image":
        risk_info = ATTRIBUTE_IMAGE_FEASIBILITY[attribute_type]

        if not risk_info["feasible"]:
            return {
                "attribute": None,
                "verdict": Verdict.HOLD,
                "explanation": f"{attribute_type} requires SEG-Y data",
                "reference": "Nature 2025, doi:10.1038/s41598-025-21949-9"
            }

        # Compute with elevated uncertainty
        value = await compute_approximate_attribute(image, attribute_type)

        return {
            "attribute": value,
            "uncertainty": 0.20,  # High for image-only
            "d_transform": risk_info["d_transform"],
            "verdict": Verdict.QUALIFY,
        }
```

### Deliverable
```python
result = await extract_seismic_attribute(
    attribute="coherence",
    source_type="image",  # vs "segy"
    image=seismic_image,
)
# result.attribute  # Computed value
# result.uncertainty  # 0.20
# result.d_transform  # 0.4
# result.verdict  # QUALIFY

# vs

result = await extract_seismic_attribute(
    attribute="spectral_decomposition",
    source_type="image",
)
# result.verdict  # HOLD
# result.explanation  # "Requires SEG-Y (Nature 2025)"
```

---

## Phase 5: Integration & Hardening (Weeks 11-12)

### Tasks
- End-to-end testing with real data
- Performance optimization
- Documentation
- Example notebooks

---

## Resource Requirements

### Compute
- GPU for seismiqb/GeoX inference (A10G or equivalent)
- Standard CPU for georeferencing/digitization

### External Dependencies
```txt
# requirements-vision.txt
opencv-python>=4.8.0      # GCP detection, curve tracing
pytesseract>=0.3.10       # OCR
easyocr>=1.7.0            # Alternative OCR
rasterio>=1.3.8           # Georeferencing
pillow>=10.0.0            # Image processing

# Optional DL backends
torch>=2.0.0              # seismiqb, GeoX
transformers>=4.30.0      # VLM adapters
segment-anything>=1.0     # SAM integration
```

### Human Resources
- 1 CV engineer (georeferencing + digitization)
- 1 ML engineer (seismic vision + attributes)
- 1 geoscientist (validation, RATLAS integration)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Georeferencing accuracy | < 50m RMS error | Benchmark maps |
| Digitization accuracy | < 5% vs ground truth | Synthetic logs |
| Seismic VLM consistency | > 0.7 cross-view | Test sections |
| AC_Risk precision | 90% correlation with expert error | Blind test |
| 888_HOLD trigger rate | 15-25% of image-only | Telemetry |

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| External repo unmaintained | Medium | Fork, vendor, document |
| License conflict | Low | Audit before integration |
| Performance issues | Medium | Benchmark early, optimize |
| Domain mismatch | Medium | Fine-tune on seismic data |
| Over-reliance on external | Medium | Abstract interfaces |

---

## Checkpoints

### Week 2 Checkpoint
- [ ] MapWarper patterns extracted
- [ ] GCPDetector working
- [ ] GeoreferenceAuditor with AC_Risk

### Week 4 Checkpoint
- [ ] WebPlotDigitizer pattern implemented
- [ ] Physics validation vs RATLAS
- [ ] Analog digitization pipeline

### Week 8 Checkpoint
- [ ] seismiqb backend integrated
- [ ] Multi-view consistency working
- [ ] GovernedSeismicVLM with real backends

### Week 10 Checkpoint
- [ ] Nature 2025 risks encoded
- [ ] Attribute extraction with risk
- [ ] End-to-end workflows

### Week 12 Checkpoint
- [ ] All components integrated
- [ ] Documentation complete
- [ ] Example notebooks
- [ ] Performance validated

---

## Final Deliverable

```python
# Complete GEOX Vision stack
from geox.vision import (
    GeoreferenceAuditor,
    AnalogDigitizer,
    GovernedSeismicVLM,
    SeismicAttributeExtractor,
)

# All operations return AC_Risk + Verdict
georef = await GeoreferenceAuditor().audit(image, bounds)
digitized = await AnalogDigitizer().digitize(log_image)
seismic = await GovernedSeismicVLM().interpret(section_image)
attributes = await SeismicAttributeExtractor().extract(image, "coherence")

# Common interface: AC_Risk + Verdict
for result in [georef, digitized, seismic, attributes]:
    assert result.ac_risk is not None
    assert result.verdict in [Verdict.SEAL, Verdict.QUALIFY, Verdict.HOLD, Verdict.VOID]
    if result.verdict == Verdict.HOLD:
        await notify_human_for_review(result)
```

---

*DITEMPA BUKAN DIBERI*
*External tools leveraged. ToAC governance applied. Vision forged.*
