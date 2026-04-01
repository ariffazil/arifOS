# GEOX Seismic Image MCP Tool Specification

> **Version:** 0.1.0-alpha  
> **Status:** PRE-PRODUCTION — Subject to 888 AUDIT  
> **Domain:** Image-First Seismic Intelligence  
> **Physics Basis:** Texture analysis, structure tensor, ridge detection  
> **Scale:** 2D seismic sections (PNG/JPG/TIFF)  
> **Seal:** DITEMPA BUKAN DIBERI

---

## Tool Registry

| Tool | Purpose | Floor Enforcement | Verdict Output |
|------|---------|-------------------|----------------|
| `geox_ingest_seismic_image` | Load and validate image | F4 (units required) | SEAL/SABAR/VOID |
| `geox_qc_seismic_image` | Quality control | F9 (artifact detection) | SEAL/PARTIAL/VOID |
| `geox_extract_texture_attributes` | Compute texture proxies | F2 (proxy labeling) | SEAL/PARTIAL |
| `geox_detect_reflectors` | Horizon candidate extraction | F7 (uncertainty) | SEAL/PARTIAL/SABAR |
| `geox_detect_fault_candidates` | Discontinuity detection | F7 (uncertainty) | SEAL/PARTIAL |
| `geox_segment_facies` | Deep learning facies | F7 (confidence ceiling 0.95) | PARTIAL/SEAL |
| `geox_compare_sections` | Analog retrieval | F4 (metadata matching) | SEAL/SABAR |
| `geox_reason_seismic_scene` | Governed interpretation | F2 (evidence convergence) | PARTIAL/SEAL |
| `geox_audit_seismic_interpretation` | 888 AUDIT layer | All floors | SEAL/PARTIAL/SABAR/VOID |

---

## Tool Specifications

### 1. `geox_ingest_seismic_image`

**Purpose:** Load seismic section image with metadata attachment.

**Input Schema:**
```json
{
  "image_path": {
    "type": "string",
    "description": "Path to image file (PNG, JPG, TIFF)",
    "example": "/data/seismic/malay_basin_line_42.png"
  },
  "image_type": {
    "type": "string",
    "enum": ["raw_seismic", "attribute_display", "interpretation_overlay", "unknown"],
    "description": "Type of image content — F4 Clarity requirement"
  },
  "basin": {
    "type": "string",
    "description": "Sedimentary basin name",
    "example": "Malay Basin"
  },
  "line_name": {
    "type": "string",
    "description": "Seismic line or survey identifier",
    "example": "MB-2024-042"
  },
  "vertical_unit": {
    "type": "string",
    "enum": ["meters", "feet", "seconds_TWT", "milliseconds_TWT", "samples"],
    "description": "Vertical axis unit — F4 MANDATORY"
  },
  "vertical_scale": {
    "type": "number",
    "description": "Vertical scale: units per pixel (e.g., 4.0 = 4 meters/pixel)",
    "minimum": 0
  },
  "horizontal_scale": {
    "type": "number",
    "description": "Horizontal scale: distance per pixel (e.g., 12.5 = 12.5 meters/pixel)",
    "minimum": 0
  },
  "polarity_known": {
    "type": "boolean",
    "description": "Whether SEG standard polarity is known"
  },
  "polarity_standard": {
    "type": "string",
    "enum": ["SEG_normal", "SEG_reverse", "unknown"],
    "description": "SEG polarity convention if known"
  },
  "requester_id": {
    "type": "string",
    "description": "Unique requester identifier — F11 AUTH"
  }
}
```

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "SEAL",
  "ingest_metadata": {
    "width_px": 1200,
    "height_px": 800,
    "format": "PNG",
    "color_mode": "grayscale",
    "file_size_mb": 2.4
  },
  "scale_validation": {
    "vertical_scale_declared": 4.0,
    "horizontal_scale_declared": 12.5,
    "aspect_ratio_valid": true,
    "estimated_true_vertical_extent_m": 3200
  },
  "constitutional_compliance": {
    "F4_clarity": "PASS — units and scales declared",
    "F11_authority": "PASS — requester authenticated"
  },
  "next_steps": ["geox_qc_seismic_image"],
  "seal": "DITEMPA BUKAN DIBERI"
}
```

**888 HOLD Triggers:**
- `vertical_unit` not provided → **VOID** (F4 violation)
- `image_type` = "unknown" → **SABAR** (require clarification)
- File not found or unreadable → **VOID**

---

### 2. `geox_qc_seismic_image`

**Purpose:** Quality control — detect artifacts, annotations, compression, distortion.

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Image identifier from ingest"
  },
  "qc_strictness": {
    "type": "string",
    "enum": ["lenient", "standard", "strict"],
    "default": "standard",
    "description": "QC strictness level"
  }
}
```

**QC Checks:**

| Check | Method | Threshold | Failure Action |
|-------|--------|-----------|----------------|
| Aspect ratio | Detect known display ratios | >10% distortion | SABAR |
| Annotation overlay | OCR + edge detection | Any text/logo detected | PARTIAL (flag) |
| Colorbar presence | Template matching | Colorbar found | CLARIFY (image is attribute) |
| Compression artifacts | JPEG artifact detection | Quality < 70% | SABAR |
| Grayscale suitability | Color channel variance | Not grayscale | CONVERT or VOID |
| Contrast | Histogram analysis | < 20% dynamic range | ENHANCE or SABAR |
| Trace banding | Frequency domain analysis | No banding detected | FLAG (may be processed) |

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "SEAL",
  "qc_score": 0.94,
  "checks": {
    "aspect_ratio": {"status": "PASS", "distortion_pct": 0.5},
    "annotation_overlay": {"status": "PASS", "confidence": 0.02},
    "colorbar_present": {"status": "PASS", "detected": false},
    "compression_artifacts": {"status": "PASS", "quality_estimate": 95},
    "grayscale_suitability": {"status": "PASS", "is_grayscale": true},
    "contrast": {"status": "PASS", "dynamic_range_pct": 78},
    "trace_banding": {"status": "WARNING", "banding_strength": 0.3, "note": "Weak banding — may be migrated data"}
  },
  "recommendations": ["Proceed with texture extraction"],
  "warnings": ["Weak trace banding — verify if this is processed migration output"],
  "seal": "DITEMPA BUKAN DIBERI"
}
```

---

### 3. `geox_extract_texture_attributes`

**Purpose:** Extract image texture proxies for seismic character.

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Validated image ID"
  },
  "methods": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["lbp", "glcm", "gabor", "structure_tensor", "steerable_pyramid", "curvelet"]
    },
    "description": "Texture analysis methods to apply"
  },
  "window_size_px": {
    "type": "integer",
    "default": 32,
    "description": "Analysis window size in pixels"
  },
  "overlap_pct": {
    "type": "number",
    "default": 50,
    "minimum": 0,
    "maximum": 90,
    "description": "Window overlap percentage"
  }
}
```

**Physics Mapping:**

| Method | Output | Seismic Proxy | Geological Relevance |
|--------|--------|---------------|---------------------|
| **LBP** | Local binary patterns | Amplitude roughness | Bedform style, grain size proxy |
| **GLCM** | Contrast, correlation, energy, homogeneity | Texture homogeneity | Facies uniformity |
| **Gabor** | Frequency-direction energy | Tuning response | Bed thickness, channel fills |
| **Structure Tensor** | Eigenvalues (λ₁, λ₂), orientation | Coherence, dip | Reflector continuity, structural dip |
| **Steerable Pyramid** | Multi-scale orientation | Multi-scale texture | Hierarchical stratigraphy |
| **Curvelet** | Curvelet coefficients | Edge/curve representation | Fault edges, unconformities |

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "SEAL",
  "attributes": {
    "structure_tensor": {
      "coherence": [[0.8, 0.7, ...], ...],
      "orientation_deg": [[15.2, 16.1, ...], ...],
      "energy": [[0.9, 0.85, ...], ...]
    },
    "lbp": {
      "histograms": [...],
      "uniformity_score": 0.72
    }
  },
  "metadata": {
    "proxy_nature": "IMAGE_DOMAIN_PROXY",
    "not_equivalent_to": ["instantaneous_attributes", "trace_derived_attributes"],
    "physical_basis": "Local intensity variation patterns correlated with reflector geometry"
  },
  "uncertainty": {
    "pixel_scale_confidence": 0.92,
    "texture_reliability": 0.88,
    "geological_interpretation_ceiling": 0.75
  },
  "seal": "DITEMPA BUKAN DIBERI"
}
```

**F2 Truth Labeling:**
```yaml
output_label: "PROXY — Image Domain Texture Attributes"
disclaimer: "These are not true seismic attributes derived from trace amplitudes. They are image-domain proxies suitable for pattern recognition and qualitative interpretation assistance."
```

---

### 4. `geox_detect_reflectors`

**Purpose:** Extract horizon candidates using ridge detection and continuity analysis.

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Validated image ID"
  },
  "method": {
    "type": "string",
    "enum": ["ridge_detection", "structure_tensor_ridges", "deep_learning"],
    "default": "structure_tensor_ridges"
  },
  "continuity_threshold": {
    "type": "number",
    "default": 0.6,
    "minimum": 0,
    "maximum": 1,
    "description": "Minimum coherence for ridge acceptance"
  },
  "min_reflector_length_px": {
    "type": "integer",
    "default": 50,
    "description": "Minimum pixel length for valid reflector"
  }
}
```

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "PARTIAL",
  "reflectors": [
    {
      "reflector_id": "refl-001",
      "pixels": [[x1, y1], [x2, y2], ...],
      "length_px": 342,
      "length_m": 4275,
      "average_dip_deg": 12.5,
      "dip_variance": 2.3,
      "coherence": 0.84,
      "continuity_score": 0.78,
      "termination_type": "gradual"
    }
  ],
  "statistics": {
    "total_reflectors": 23,
    "avg_dip_deg": 11.2,
    "dip_direction_consistency": 0.91,
    "dominant_azimuth": "NW-SE"
  },
  "uncertainty": {
    "detection_confidence": 0.82,
    "dip_accuracy_estimate": "±3 degrees (image domain)",
    "physical_validation": "REQUIRES_TRACE_DOMAIN_CONFIRMATION"
  },
  "verdict_reason": "PARTIAL: Reflectors detected as candidates. True horizon picking requires interpreter validation and trace-domain tie.",
  "seal": "DITEMPA BUKAN DIBERI"
}
```

---

### 5. `geox_detect_fault_candidates`

**Purpose:** Identify discontinuities and lineaments as fault likelihood map.

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Validated image ID"
  },
  "method": {
    "type": "string",
    "enum": ["gradient_discontinuity", "coherence_drop", "ant_tracking_style", "deep_learning"],
    "default": "gradient_discontinuity"
  },
  "sensitivity": {
    "type": "string",
    "enum": ["low", "medium", "high"],
    "default": "medium"
  }
}
```

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "PARTIAL",
  "fault_likelihood_map": "base64_encoded_png",
  "candidates": [
    {
      "fault_id": "fault-001",
      "pixels": [[x1, y1], ...],
      "length_px": 156,
      "dip_direction": "SW",
      "likelihood_score": 0.76,
      "offset_estimate_px": 12,
      "confidence": 0.68
    }
  ],
  "uncertainty": {
    "false_positive_risk": "HIGH — many discontinuities are not faults",
    "validation_required": "Cross-line confirmation and trace-domain analysis"
  },
  "seal": "DITEMPA BUKAN DIBERI"
}
```

**Critical Note:** Fault candidates are **not fault interpretations**. They are prior probabilities for interpreter attention.

---

### 6. `geox_segment_facies`

**Purpose:** Deep learning seismic facies segmentation.

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Validated image ID"
  },
  "model_name": {
    "type": "string",
    "enum": ["deeplabv3_plus", "unet", "segformer"],
    "default": "deeplabv3_plus"
  },
  "classes": {
    "type": "array",
    "items": {"type": "string"},
    "example": ["shale", "sandstone", "limestone", "chaotic", "salt"],
    "description": "Target facies classes"
  },
  "compute_uncertainty": {
    "type": "boolean",
    "default": true,
    "description": "Enable Monte Carlo dropout uncertainty"
  }
}
```

**Output Schema:**
```json
{
  "success": true,
  "image_id": "img-mb-2024-042-a7f3d9",
  "verdict": "PARTIAL",
  "segmentation_map": "base64_encoded_png",
  "class_probabilities": {
    "shale": [[0.1, 0.2, ...], ...],
    "sandstone": [[0.7, 0.6, ...], ...]
  },
  "uncertainty_map": [[0.15, 0.22, ...], ...],
  "statistics": {
    "class_distribution": {"shale": 0.45, "sandstone": 0.30, ...},
    "boundary_sharpness": 0.72,
    "uncertainty_hotspots": [{"x": 450, "y": 320, "uncertainty": 0.45}]
  },
  "model_info": {
    "architecture": "DeepLabv3+",
    "trained_on": "Published seismic facies datasets",
    "confidence_ceiling": 0.95,
    "F7_compliance": "Uncertainty quantified and exposed"
  },
  "warnings": [
    "Segmentation is image-domain prediction, not lithology identification",
    "Classes are seismic facies proxies, not rock types",
    "High uncertainty regions require interpreter attention"
  ],
  "seal": "DITEMPA BUKAN DIBERI"
}
```

---

### 7. `geox_compare_sections`

**Purpose:** Retrieve analog seismic sections based on texture similarity.

**Input Schema:**
```json
{
  "query_image_id": {
    "type": "string",
    "description": "Query image ID"
  },
  "library_basins": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Basins to search for analogs"
  },
  "top_k": {
    "type": "integer",
    "default": 5,
    "minimum": 1,
    "maximum": 20
  },
  "similarity_method": {
    "type": "string",
    "enum": ["texture_embedding", "structural_similarity", "hybrid"],
    "default": "hybrid"
  }
}
```

---

### 8. `geox_reason_seismic_scene`

**Purpose:** Governed interpretation synthesis (NOT raw model output).

**Input Schema:**
```json
{
  "image_id": {
    "type": "string",
    "description": "Image with existing analysis"
  },
  "play_hypothesis": {
    "type": "string",
    "enum": ["deltaic", "deep_water", "carbonate_buildup", "rift", "passive_margin"],
    "description": "Geological play hypothesis — F2 constraint"
  },
  "geological_intent": {
    "type": "string",
    "description": "Specific interpretation goal",
    "example": "Identify potential reservoir intervals in deltaic topsets"
  },
  "evidence_types": {
    "type": "array",
    "items": {
      "type": "string",
      "enum": ["reflectors", "faults", "facies", "texture", "external_well"]
    },
    "default": ["reflectors", "facies", "texture"]
  }
}
```

---

### 9. `geox_audit_seismic_interpretation`

**Purpose:** 888 AUDIT layer for seismic interpretation.

**Input Schema:**
```json
{
  "result_id": {
    "type": "string",
    "description": "Interpretation result to audit"
  },
  "audit_depth": {
    "type": "string",
    "enum": ["surface", "standard", "deep"],
    "default": "standard"
  }
}
```

**Audit Checks:**

| Floor | Check | Violation Action |
|-------|-------|------------------|
| F1 | No irreversible claims | Flag if interpretation stated as fact |
| F2 | Evidence supports claims | HOLD if claim > evidence |
| F4 | Units/scale declared | VOID if missing |
| F7 | Uncertainty declared | ENFORCE Ω₀ minimum |
| F9 | No hallucination | HOLD if pattern not in image |
| F11 | Authority verified | VOID if requester unauthorized |
| F13 | Human veto possible | ENSURE signoff pathway |

---

## A2A Tool Discovery

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "result": {
    "tools": [
      {
        "name": "geox_ingest_seismic_image",
        "description": "Load seismic section with Earth-scale metadata",
        "inputSchema": { ... }
      },
      {
        "name": "geox_qc_seismic_image", 
        "description": "Quality control — detect artifacts and distortions",
        "inputSchema": { ... }
      }
      // ... all 9 tools
    ]
  }
}
```

---

## Constitutional Compliance Matrix

| Tool | F1 | F2 | F4 | F7 | F9 | F11 | F13 |
|------|----|----|----|----|----|----|----|
| ingest | ✅ | ✅ | **ENFORCE** | ✅ | ✅ | **ENFORCE** | ✅ |
| qc | ✅ | ✅ | ✅ | ✅ | **ENFORCE** | ✅ | ✅ |
| extract_texture | ✅ | **LABEL** | ✅ | **ENFORCE** | ✅ | ✅ | ✅ |
| detect_reflectors | ✅ | **LABEL** | ✅ | **ENFORCE** | ✅ | ✅ | ✅ |
| detect_faults | ✅ | **LABEL** | ✅ | **ENFORCE** | ✅ | ✅ | ✅ |
| segment_facies | ✅ | **LABEL** | ✅ | **CEILING** | ✅ | ✅ | ✅ |
| compare | ✅ | ✅ | **ENFORCE** | ✅ | ✅ | ✅ | ✅ |
| reason | ✅ | **CONSTRAIN** | ✅ | ✅ | **ENFORCE** | ✅ | **ENFORCE** |
| audit | **ALL** | **ALL** | **ALL** | **ALL** | **ALL** | **ALL** | **ALL** |

**Legend:**
- **ENFORCE** — Active validation with HOLD/VOID possible
- **LABEL** — Explicit proxy/disclaimer labeling required
- **CEILING** — Confidence ceiling enforced (0.95 for image-first)
- **CONSTRAIN** — Evidence-constrained reasoning required
- **ALL** — Full floor enforcement

---

*Specification Version: 0.1.0-alpha*  
*Physics Validation: PASS (with proxy scope acknowledged)*  
*Earth Scale: ENFORCED (units mandatory)*  
*Seal: DITEMPA BUKAN DIBERI*
