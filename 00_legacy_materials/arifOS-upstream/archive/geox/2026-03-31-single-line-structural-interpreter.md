# GEOX Single-Line Structural Interpreter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Band A (raster-only) of the GEOX single-line seismic image interpreter — a 6-tool MCP pipeline that converts a PNG/JPG seismic section into a governed structural interpretation with contrast-bias audit, geological plausibility ranking, and 2D-limit warnings.

**Architecture:** Image in → normalize → 6 contrast views → image-feature proxies → geological rule engine → candidate ranking → governed report. LLM never reads pixels directly. All outputs return the common `GEOXOutput` envelope. Epistemic labels (CLAIM / PLAUSIBLE / HYPOTHESIS) on every output.

**Tech Stack:** Python 3.10+, NumPy (pure — no scipy), Pydantic v2, pytest + pytest-asyncio, existing `SeismicVisualFilterTool` (reuse for contrast views). Pillow optional for PNG loading.

**Spec:** `docs/superpowers/specs/2026-03-31-single-line-structural-interpreter-design.md`

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `arifos/geox/schemas/geox_output.py` | CREATE | Common `GEOXOutput` envelope — every tool returns this |
| `arifos/geox/schemas/__init__.py` | CREATE | Package init |
| `arifos/geox/schemas/structural_interp.py` | CREATE | `SeismicImageInput`, `SeismicView`, `FeatureSet`, `StructuralCandidate`, `InterpretationResult` |
| `arifos/geox/tools/seismic_image_ingest.py` | CREATE | Stage 1: load + normalize image, return `GEOXOutput` |
| `arifos/geox/tools/seismic_contrast_views.py` | CREATE | Stage 2: 6 contrast variants wrapping `SeismicVisualFilterTool` |
| `arifos/geox/tools/seismic_feature_extract.py` | CREATE | Stage 3: lineaments, dip field, discontinuities — image proxies only |
| `arifos/geox/tools/seismic_structure_rules.py` | CREATE | Stage 5: geological rule engine — score candidates per family |
| `arifos/geox/tools/seismic_candidate_ranker.py` | CREATE | Stage 4+6: build + rank structural candidates |
| `arifos/geox/tools/seismic_report_writer.py` | CREATE | Stage 7: governed markdown + JSON report |
| `tests/tools/test_geox_output.py` | CREATE | Envelope schema tests |
| `tests/tools/test_structural_interp_schemas.py` | CREATE | Schema validation tests |
| `tests/tools/test_seismic_image_ingest.py` | CREATE | Ingest tests |
| `tests/tools/test_seismic_contrast_views.py` | CREATE | 6-view generation tests |
| `tests/tools/test_seismic_feature_extract.py` | CREATE | Feature extraction tests |
| `tests/tools/test_seismic_structure_rules.py` | CREATE | Rule engine tests |
| `tests/tools/test_seismic_candidate_ranker.py` | CREATE | Ranking tests |
| `tests/tools/test_seismic_report_writer.py` | CREATE | Report tests |
| `tests/test_single_line_integration.py` | CREATE | Bond synthetic end-to-end test |

---

## Shared Test Fixture

Every test task uses this synthetic seismic image. Define it in `conftest.py` OR copy inline.

```python
import numpy as np

def make_synthetic_seismic(h: int = 100, w: int = 200) -> np.ndarray:
    """
    Synthetic seismic section: horizontal reflectors + one diagonal fault.
    Deterministic (seed=42). Returns float64 [0, 1].
    """
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [20, 40, 60, 80]:         # reflectors
        img[max(0, y-1):y+2, :] = 0.8
    for y in range(h):                  # diagonal fault
        x = int(w * 0.5 + y * 0.3)
        if 0 <= x < w:
            img[y, max(0, x-1):min(w, x+2)] = 0.5
    img += rng.normal(0, 0.05, (h, w))
    return np.clip(img, 0, 1)
```

---

## Task 1: Common Output Envelope

**Files:**
- Create: `arifos/geox/schemas/__init__.py`
- Create: `arifos/geox/schemas/geox_output.py`
- Create: `tests/tools/__init__.py`
- Create: `tests/tools/test_geox_output.py`

- [ ] **Step 1.1: Write failing test**

```python
# tests/tools/test_geox_output.py
from arifos.geox.schemas.geox_output import GEOXOutput, GEOXUncertainty, GEOXContrastMeta, GEOXGovernance

def test_geox_output_minimal():
    out = GEOXOutput(
        ok=True,
        verdict="QUALIFY",
        uncertainty=GEOXUncertainty(level=0.11, type="image_only"),
    )
    assert out.ok is True
    assert out.verdict == "QUALIFY"
    assert out.source_domain == "geox-earth-witness"
    assert out.result == {}
    assert out.error is None

def test_geox_output_uncertainty_bounds():
    import pytest
    with pytest.raises(Exception):
        GEOXOutput(
            ok=True, verdict="PASS",
            uncertainty=GEOXUncertainty(level=0.02, type="test"),  # below floor 0.03
        )

def test_geox_output_serializes():
    out = GEOXOutput(
        ok=False,
        verdict="GEOX_BLOCK",
        uncertainty=GEOXUncertainty(level=0.15, type="no_trace_data", notes=["Image only"]),
        error="No trace data available",
    )
    d = out.model_dump()
    assert d["verdict"] == "GEOX_BLOCK"
    assert d["error"] == "No trace data available"
    assert d["uncertainty"]["notes"] == ["Image only"]
```

- [ ] **Step 1.2: Run test to verify it fails**

```
cd C:\ariffazil\GEOX
python -m pytest tests/tools/test_geox_output.py -v
```
Expected: `ModuleNotFoundError: No module named 'arifos.geox.schemas.geox_output'`

- [ ] **Step 1.3: Create package files**

```python
# arifos/geox/schemas/__init__.py
"""GEOX structural interpretation schemas."""
```

```python
# tests/tools/__init__.py
```

- [ ] **Step 1.4: Write `geox_output.py`**

```python
# arifos/geox/schemas/geox_output.py
"""
GEOXOutput — Common output envelope for all GEOX Band-A tools.
DITEMPA BUKAN DIBERI

Non-negotiable shape: every tool returns this wrapper.
Enforces: F4 Clarity (explicit uncertainty), F7 Humility (uncertainty floor 0.03).
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class GEOXUncertainty(BaseModel):
    level: float = Field(ge=0.03, le=0.15, description="F7 Humility: fractional uncertainty")
    type: str = Field(..., description="e.g. 'image_only_structural', 'trace_domain_aci'")
    notes: list[str] = Field(default_factory=list)


class GEOXContrastMeta(BaseModel):
    processing_steps: list[str] = Field(default_factory=list)
    display_bias_risk: Literal["low", "medium", "high"] = "medium"
    notes: list[str] = Field(default_factory=list)


class GEOXGovernance(BaseModel):
    floors_ok: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    verdict: Literal["PASS", "QUALIFY", "HOLD", "GEOX_BLOCK"] = "QUALIFY"


class GEOXOutput(BaseModel):
    """
    Common output envelope. Every GEOX Band-A tool returns this.

    Fields:
        ok               — False if tool encountered an error
        verdict          — PASS | QUALIFY | HOLD | GEOX_BLOCK
        source_domain    — Always "geox-earth-witness"
        uncertainty      — F7 calibrated uncertainty
        contrast_metadata — Contrast Canon metadata
        governance       — Floor compliance + warnings
        result           — Tool-specific payload
        error            — Error message if ok=False
    """

    ok: bool
    verdict: Literal["PASS", "QUALIFY", "HOLD", "GEOX_BLOCK"]
    source_domain: str = "geox-earth-witness"
    uncertainty: GEOXUncertainty
    contrast_metadata: GEOXContrastMeta = Field(default_factory=GEOXContrastMeta)
    governance: GEOXGovernance = Field(default_factory=GEOXGovernance)
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
```

- [ ] **Step 1.5: Run tests to verify they pass**

```
python -m pytest tests/tools/test_geox_output.py -v
```
Expected: `3 passed`

- [ ] **Step 1.6: Commit**

```bash
git add arifos/geox/schemas/__init__.py arifos/geox/schemas/geox_output.py tests/tools/__init__.py tests/tools/test_geox_output.py
git commit -m "feat(geox): add GEOXOutput common envelope — Band-A foundation"
```

---

## Task 2: Structural Interpretation Schemas

**Files:**
- Create: `arifos/geox/schemas/structural_interp.py`
- Create: `tests/tools/test_structural_interp_schemas.py`

- [ ] **Step 2.1: Write failing tests**

```python
# tests/tools/test_structural_interp_schemas.py
import pytest
from arifos.geox.schemas.structural_interp import (
    SeismicImageInput, SeismicView, Lineament, Discontinuity, DipVector,
    FeatureSet, StructuralCandidate, InterpretationResult,
)

def test_seismic_image_input_defaults():
    inp = SeismicImageInput(image_path="/tmp/test.png", line_id="L001")
    assert inp.domain == "unknown"
    assert inp.polarity == "unknown"
    assert inp.scale_known is False

def test_seismic_view_has_view_id():
    view = SeismicView(
        source_line_id="L001",
        processing_chain=["clahe"],
        display_params={"contrast_mode": "clahe"},
    )
    assert view.view_id  # auto-generated
    assert len(view.processing_chain) == 1

def test_structural_candidate_composite_score_default():
    c = StructuralCandidate(family="normal_fault")
    assert 0.0 <= c.geometry_score <= 1.0
    assert 0.0 <= c.composite_score <= 1.0
    assert c.epistemic_tag in ("CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE")

def test_feature_set_note_contains_proxy():
    fs = FeatureSet(view_id="v1")
    assert "image_derived_proxy" in fs.note

def test_interpretation_result_requires_two_d_limits():
    result = InterpretationResult(
        line_id="L001",
        best_candidate_id="cand-001",
        confidence=0.55,
        bias_audit={"display_sensitivity": "medium"},
        summary="Test summary.",
        verdict="QUALIFY",
    )
    # 2D limits must be populated by caller
    assert isinstance(result.two_d_limits, list)
```

- [ ] **Step 2.2: Run to verify failure**

```
python -m pytest tests/tools/test_structural_interp_schemas.py -v
```
Expected: `ModuleNotFoundError: No module named 'arifos.geox.schemas.structural_interp'`

- [ ] **Step 2.3: Write `structural_interp.py`**

```python
# arifos/geox/schemas/structural_interp.py
"""
GEOX Structural Interpretation Schemas — Band-A Raster-only Pipeline.
DITEMPA BUKAN DIBERI

Schemas:
  SeismicImageInput     — image + metadata (no trace data)
  SeismicView           — one contrast variant of the image
  Lineament             — reflector-like linear feature (image proxy)
  Discontinuity         — break/offset in reflector pattern (image proxy)
  DipVector             — local dip estimate from image gradient
  FeatureSet            — all image features from one view
  StructuralCandidate   — one geological structural model candidate
  InterpretationResult  — final ranked output

All image-derived outputs carry note: "image_derived_proxy — not seismic trace attribute."
"""
from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field


class SeismicImageInput(BaseModel):
    image_path: str
    line_id: str
    domain: Literal["time", "depth", "unknown"] = "unknown"
    polarity: Literal["normal", "reverse", "unknown"] = "unknown"
    vertical_exaggeration: float | None = None
    scale_known: bool = False
    pixel_to_ms: float | None = None
    pixel_to_m: float | None = None
    notes: str | None = None


class SeismicView(BaseModel):
    view_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_line_id: str
    processing_chain: list[str]
    display_params: dict[str, Any]
    output_path: str | None = None


class Lineament(BaseModel):
    """Horizontal-ish reflector-like segment extracted from image edges."""
    x0: float
    y0: float
    x1: float
    y1: float
    strength: float = Field(ge=0.0, le=1.0)
    dip_deg: float | None = None


class Discontinuity(BaseModel):
    """Break or offset in reflector pattern — fault proxy from image."""
    x: float
    y: float
    discontinuity_type: str = "high_gradient_break"
    strength: float = Field(ge=0.0, le=1.0)


class DipVector(BaseModel):
    """Local dip estimate from image gradient direction."""
    x: float
    y: float
    dip_deg: float
    confidence: float = Field(ge=0.0, le=1.0)


class FeatureSet(BaseModel):
    view_id: str
    lineaments: list[Lineament] = Field(default_factory=list)
    discontinuities: list[Discontinuity] = Field(default_factory=list)
    dip_field: list[DipVector] = Field(default_factory=list)
    continuity_map_ref: str | None = None
    chaos_map_ref: str | None = None
    note: str = (
        "image_derived_proxy — not seismic trace attribute. "
        "Physical interpretation requires trace data."
    )


class StructuralCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    family: Literal[
        "normal_fault", "reverse_fault", "fold", "duplex",
        "stratigraphic", "flower", "inversion", "unknown"
    ]
    faults: list[dict[str, Any]] = Field(default_factory=list)
    horizons: list[dict[str, Any]] = Field(default_factory=list)
    support_views: list[str] = Field(default_factory=list)
    geometry_score: float = Field(ge=0.0, le=1.0, default=0.5)
    stability_score: float = Field(ge=0.0, le=1.0, default=0.5)
    geology_score: float = Field(ge=0.0, le=1.0, default=0.5)
    composite_score: float = Field(ge=0.0, le=1.0, default=0.5)
    warnings: list[str] = Field(default_factory=list)
    uncertainty: float = Field(ge=0.03, le=0.15, default=0.12)
    epistemic_tag: Literal["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE"] = "PLAUSIBLE"


class InterpretationResult(BaseModel):
    line_id: str
    best_candidate_id: str
    alternatives: list[StructuralCandidate] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    bias_audit: dict[str, Any]
    two_d_limits: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    summary: str
    verdict: Literal["PASS", "QUALIFY", "HOLD", "GEOX_BLOCK"] = "QUALIFY"
    telemetry: dict[str, Any] = Field(default_factory=dict)
```

- [ ] **Step 2.4: Run tests**

```
python -m pytest tests/tools/test_structural_interp_schemas.py -v
```
Expected: `5 passed`

- [ ] **Step 2.5: Commit**

```bash
git add arifos/geox/schemas/structural_interp.py tests/tools/test_structural_interp_schemas.py
git commit -m "feat(geox): add structural interpretation schemas (Band-A)"
```

---

## Task 3: Seismic Image Ingest

**Files:**
- Create: `arifos/geox/tools/seismic_image_ingest.py`
- Create: `tests/tools/test_seismic_image_ingest.py`

- [ ] **Step 3.1: Write failing tests**

```python
# tests/tools/test_seismic_image_ingest.py
import numpy as np
import pytest
from arifos.geox.tools.seismic_image_ingest import load_seismic_image, ingest_seismic_image
from arifos.geox.schemas.geox_output import GEOXOutput

def make_synthetic_seismic(h=100, w=200):
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [20, 40, 60, 80]:
        img[max(0, y-1):y+2, :] = 0.8
    for y in range(h):
        x = int(w * 0.5 + y * 0.3)
        if 0 <= x < w:
            img[y, max(0, x-1):min(w, x+2)] = 0.5
    img += rng.normal(0, 0.05, (h, w))
    return np.clip(img, 0, 1)

def test_load_seismic_image_from_npy(tmp_path):
    arr = make_synthetic_seismic()
    npy_path = tmp_path / "test.npy"
    np.save(str(npy_path), arr)
    meta, loaded = load_seismic_image(str(npy_path), {"line_id": "L001"})
    assert loaded.ndim == 2
    assert loaded.dtype == np.float64
    assert 0.0 <= loaded.min()
    assert loaded.max() <= 1.0
    assert meta.line_id == "L001"

def test_load_seismic_image_sets_domain(tmp_path):
    arr = make_synthetic_seismic()
    npy_path = tmp_path / "test.npy"
    np.save(str(npy_path), arr)
    meta, _ = load_seismic_image(str(npy_path), {"line_id": "L002", "domain": "time"})
    assert meta.domain == "time"

def test_ingest_seismic_image_returns_geox_output(tmp_path):
    arr = make_synthetic_seismic()
    npy_path = tmp_path / "test.npy"
    np.save(str(npy_path), arr)
    output = ingest_seismic_image(str(npy_path), {"line_id": "L003"})
    assert isinstance(output, GEOXOutput)
    assert output.ok is True
    assert output.verdict in ("PASS", "QUALIFY")
    assert "image_path" in output.result
    assert "shape" in output.result
    assert 0.03 <= output.uncertainty.level <= 0.15
```

- [ ] **Step 3.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_image_ingest.py -v
```
Expected: `ModuleNotFoundError: No module named 'arifos.geox.tools.seismic_image_ingest'`

- [ ] **Step 3.3: Write `seismic_image_ingest.py`**

```python
# arifos/geox/tools/seismic_image_ingest.py
"""
GEOX Stage 1 — Seismic Image Ingest (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Loads a 2D seismic section image, normalizes to float64 [0,1] grayscale.
All outputs labelled as perception-layer, not trace-domain attributes.

Supports: .npy (NumPy arrays), .png / .jpg / .tif (via Pillow, optional).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from arifos.geox.schemas.geox_output import (
    GEOXOutput, GEOXUncertainty, GEOXContrastMeta, GEOXGovernance,
)
from arifos.geox.schemas.structural_interp import SeismicImageInput


def load_seismic_image(
    path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> tuple[SeismicImageInput, np.ndarray]:
    """
    Load seismic image from file. Normalize to float64 [0, 1] grayscale.

    Args:
        path: Path to .npy, .png, .jpg, or .tif file.
        metadata: Optional dict with line_id, domain, polarity, etc.

    Returns:
        (SeismicImageInput, normalized_array)
    """
    path = Path(path)
    meta = metadata or {}

    if path.suffix == ".npy":
        arr = np.load(str(path))
    else:
        try:
            from PIL import Image
            arr = np.array(Image.open(str(path)).convert("L"), dtype=np.float64)
        except ImportError as e:
            raise ImportError("Pillow required for image loading: pip install Pillow") from e

    # Flatten to 2D grayscale
    if arr.ndim == 3:
        arr = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    arr = arr.astype(np.float64)

    # Normalize to [0, 1]
    if arr.max() > arr.min():
        arr = (arr - arr.min()) / (arr.max() - arr.min())

    input_meta = SeismicImageInput(
        image_path=str(path),
        line_id=meta.get("line_id", path.stem),
        domain=meta.get("domain", "unknown"),
        polarity=meta.get("polarity", "unknown"),
        vertical_exaggeration=meta.get("vertical_exaggeration"),
        scale_known=bool(meta.get("scale_known", False)),
        pixel_to_ms=meta.get("pixel_to_ms"),
        pixel_to_m=meta.get("pixel_to_m"),
        notes=meta.get("notes"),
    )

    return input_meta, arr


def ingest_seismic_image(
    path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> GEOXOutput:
    """
    Band-A Stage 1: Load + normalize seismic image, return GEOXOutput.

    Uncertainty floor: 0.15 (perception layer — raster image only).
    Verdict: QUALIFY (no trace data → cannot be PASS).
    """
    try:
        input_meta, arr = load_seismic_image(path, metadata)
    except Exception as exc:
        return GEOXOutput(
            ok=False,
            verdict="GEOX_BLOCK",
            uncertainty=GEOXUncertainty(level=0.15, type="load_error"),
            error=str(exc),
        )

    h, w = arr.shape
    has_scale = input_meta.scale_known
    warnings = []
    if not has_scale:
        warnings.append("No scale provided — pixel-to-physical mapping unknown.")
    if input_meta.domain == "unknown":
        warnings.append("Domain unknown (time vs depth) — dip measurements uncalibrated.")
    if input_meta.polarity == "unknown":
        warnings.append("Polarity unknown — phase interpretation unreliable.")

    return GEOXOutput(
        ok=True,
        verdict="QUALIFY",
        uncertainty=GEOXUncertainty(
            level=0.15,
            type="image_only_raster",
            notes=["Raster image — no trace-domain attributes available."],
        ),
        contrast_metadata=GEOXContrastMeta(
            processing_steps=["grayscale_normalize"],
            display_bias_risk="medium",
            notes=["Original display encoding unknown."],
        ),
        governance=GEOXGovernance(
            floors_ok=["F4", "F7"],
            warnings=warnings,
        ),
        result={
            "image_path": str(path),
            "line_id": input_meta.line_id,
            "shape": [h, w],
            "domain": input_meta.domain,
            "polarity": input_meta.polarity,
            "scale_known": has_scale,
            "epistemic_tag": "CLAIM",
            "note": "image_derived_proxy — not seismic trace attribute.",
        },
    )
```

- [ ] **Step 3.4: Run tests**

```
python -m pytest tests/tools/test_seismic_image_ingest.py -v
```
Expected: `3 passed`

- [ ] **Step 3.5: Commit**

```bash
git add arifos/geox/tools/seismic_image_ingest.py tests/tools/test_seismic_image_ingest.py
git commit -m "feat(geox): Stage 1 seismic image ingest (Band-A)"
```

---

## Task 4: Contrast Views

**Files:**
- Create: `arifos/geox/tools/seismic_contrast_views.py`
- Create: `tests/tools/test_seismic_contrast_views.py`

- [ ] **Step 4.1: Write failing tests**

```python
# tests/tools/test_seismic_contrast_views.py
import numpy as np
import pytest
from arifos.geox.tools.seismic_contrast_views import generate_contrast_views, contrast_views_output
from arifos.geox.schemas.structural_interp import SeismicView
from arifos.geox.schemas.geox_output import GEOXOutput

def make_synthetic_seismic(h=100, w=200):
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [20, 40, 60, 80]:
        img[max(0, y-1):y+2, :] = 0.8
    img += rng.normal(0, 0.05, (h, w))
    return np.clip(img, 0, 1)

def test_generates_six_views():
    image = make_synthetic_seismic()
    views = generate_contrast_views(image, "L001")
    assert len(views) == 6
    for view, arr in views:
        assert isinstance(view, SeismicView)
        assert arr.shape == image.shape
        assert arr.dtype == np.float64

def test_views_are_distinct():
    image = make_synthetic_seismic()
    views = generate_contrast_views(image, "L001")
    arrays = [arr for _, arr in views]
    # At least some views should differ from the first
    diffs = [not np.allclose(arrays[0], arr) for arr in arrays[1:]]
    assert any(diffs), "All 6 views are identical — contrast processing failed"

def test_views_values_in_range():
    image = make_synthetic_seismic()
    views = generate_contrast_views(image, "L001")
    for _, arr in views:
        assert arr.min() >= 0.0
        assert arr.max() <= 1.0 + 1e-6  # small float tolerance

def test_contrast_views_output_returns_geox_output():
    image = make_synthetic_seismic()
    output = contrast_views_output(image, "L001")
    assert isinstance(output, GEOXOutput)
    assert output.ok is True
    assert "views" in output.result
    assert len(output.result["views"]) == 6
    assert output.governance.warnings  # bias warning mandatory
```

- [ ] **Step 4.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_contrast_views.py -v
```
Expected: `ModuleNotFoundError: No module named 'arifos.geox.tools.seismic_contrast_views'`

- [ ] **Step 4.3: Write `seismic_contrast_views.py`**

```python
# arifos/geox/tools/seismic_contrast_views.py
"""
GEOX Stage 2 — Contrast View Generation (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Generates 6 controlled display variants for bias and stability testing.
Wraps existing SeismicVisualFilterTool filter functions.

Bond et al. (2007): display choices affect structural interpretation.
If a feature appears in only 1 of 6 views → stability_score < 0.3.
"""
from __future__ import annotations

import numpy as np

from arifos.geox.schemas.geox_output import (
    GEOXOutput, GEOXUncertainty, GEOXContrastMeta, GEOXGovernance,
)
from arifos.geox.schemas.structural_interp import SeismicView
from arifos.geox.tools.seismic_visual_filter import (
    _gaussian_filter,
    _clahe_filter,
    _sobel_filter,
)


def generate_contrast_views(
    image: np.ndarray,
    line_id: str,
) -> list[tuple[SeismicView, np.ndarray]]:
    """
    Generate 6 contrast variants for bias testing.

    Variant families:
      1. Linear stretch (identity)
      2. Histogram equalization
      3. CLAHE (adaptive local contrast)
      4. Edge-enhanced (Gaussian + Sobel overlay)
      5. Gamma brightened (γ=0.5)
      6. Gamma darkened (γ=2.0)

    Returns list of (SeismicView metadata, float64 [0,1] array).
    """
    img = np.clip(image.astype(np.float64), 0, 1)
    img_uint8 = (img * 255).astype(np.uint8)

    views: list[tuple[SeismicView, np.ndarray]] = []

    # 1. Linear stretch
    v1_arr = img.copy()
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["linear_stretch"],
                    display_params={"contrast_mode": "linear", "gamma": 1.0}),
        v1_arr,
    ))

    # 2. Histogram equalization (global)
    hist, bins = np.histogram(img.flatten(), bins=256, range=(0.0, 1.0))
    cdf = hist.cumsum().astype(np.float64)
    cdf_min = cdf[cdf > 0].min() if (cdf > 0).any() else 0.0
    if cdf.max() > cdf_min:
        cdf_norm = (cdf - cdf_min) / (cdf.max() - cdf_min)
    else:
        cdf_norm = np.zeros(256)
    v2_arr = np.interp(img, bins[:-1], cdf_norm)
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["histogram_equalization"],
                    display_params={"contrast_mode": "histeq"}),
        np.clip(v2_arr, 0.0, 1.0),
    ))

    # 3. CLAHE
    clahe_res = _clahe_filter(img_uint8, clip_limit=2.0, tile_size=8)
    v3_arr = clahe_res.output_array.astype(np.float64) / 255.0
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["clahe"],
                    display_params={"contrast_mode": "clahe", "clip_limit": 2.0}),
        np.clip(v3_arr, 0.0, 1.0),
    ))

    # 4. Edge-enhanced (Gaussian smooth → Sobel → normalize to [0,1])
    gauss_res = _gaussian_filter(img_uint8, kernel_size=5, sigma=1.4)
    sobel_res = _sobel_filter(gauss_res.output_array)
    v4_raw = sobel_res.output_array.astype(np.float64)
    v4_arr = v4_raw / (v4_raw.max() + 1e-10)
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["gaussian_k5", "sobel_edge"],
                    display_params={"contrast_mode": "edge_enhanced"}),
        np.clip(v4_arr, 0.0, 1.0),
    ))

    # 5. Gamma brightened (γ=0.5)
    v5_arr = np.power(img, 0.5)
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["gamma_0.5"],
                    display_params={"gamma": 0.5, "contrast_mode": "gamma_bright"}),
        np.clip(v5_arr, 0.0, 1.0),
    ))

    # 6. Gamma darkened (γ=2.0)
    v6_arr = np.power(img, 2.0)
    views.append((
        SeismicView(source_line_id=line_id,
                    processing_chain=["gamma_2.0"],
                    display_params={"gamma": 2.0, "contrast_mode": "gamma_dark"}),
        np.clip(v6_arr, 0.0, 1.0),
    ))

    return views


def contrast_views_output(image: np.ndarray, line_id: str) -> GEOXOutput:
    """Band-A Stage 2: generate contrast views, return GEOXOutput."""
    views = generate_contrast_views(image, line_id)
    view_metas = [
        {
            "view_id": v.view_id,
            "processing_chain": v.processing_chain,
            "display_params": v.display_params,
        }
        for v, _ in views
    ]
    return GEOXOutput(
        ok=True,
        verdict="QUALIFY",
        uncertainty=GEOXUncertainty(
            level=0.15,
            type="image_only_display_variant",
            notes=["Contrast variants — display-domain only."],
        ),
        contrast_metadata=GEOXContrastMeta(
            processing_steps=["multi_variant_contrast_generation"],
            display_bias_risk="medium",
            notes=["Bond et al. (2007): display choices affect interpretation."],
        ),
        governance=GEOXGovernance(
            floors_ok=["F4", "F7", "F9"],
            warnings=[
                "Features seen in <2 of 6 views are weak evidence (stability_score < 0.3).",
                "Contrast variants test display sensitivity, not geological certainty.",
            ],
        ),
        result={"line_id": line_id, "views": view_metas, "n_views": len(views)},
    )
```

- [ ] **Step 4.4: Run tests**

```
python -m pytest tests/tools/test_seismic_contrast_views.py -v
```
Expected: `4 passed`

- [ ] **Step 4.5: Commit**

```bash
git add arifos/geox/tools/seismic_contrast_views.py tests/tools/test_seismic_contrast_views.py
git commit -m "feat(geox): Stage 2 contrast view generation — 6 variants with bias audit"
```

---

## Task 5: Feature Extraction

**Files:**
- Create: `arifos/geox/tools/seismic_feature_extract.py`
- Create: `tests/tools/test_seismic_feature_extract.py`

- [ ] **Step 5.1: Write failing tests**

```python
# tests/tools/test_seismic_feature_extract.py
import numpy as np
from arifos.geox.tools.seismic_feature_extract import extract_features, feature_extract_output
from arifos.geox.schemas.structural_interp import FeatureSet
from arifos.geox.schemas.geox_output import GEOXOutput

def make_synthetic_seismic(h=100, w=200):
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [20, 40, 60, 80]:
        img[max(0, y-1):y+2, :] = 0.8
    for y in range(h):
        x = int(w * 0.5 + y * 0.3)
        if 0 <= x < w:
            img[y, max(0, x-1):min(w, x+2)] = 0.5
    img += rng.normal(0, 0.05, (h, w))
    return np.clip(img, 0, 1)

def test_extract_features_returns_feature_set():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    assert isinstance(fs, FeatureSet)
    assert fs.view_id == "v1"

def test_extract_features_finds_lineaments():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    # Synthetic has 4 horizontal reflectors — should find lineaments
    assert len(fs.lineaments) > 0

def test_extract_features_finds_discontinuities():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    # Synthetic has a diagonal fault — should find discontinuities
    assert len(fs.discontinuities) > 0

def test_extract_features_note_contains_proxy():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    assert "image_derived_proxy" in fs.note

def test_feature_extract_output_returns_geox_output():
    image = make_synthetic_seismic()
    output = feature_extract_output(image, "v1")
    assert isinstance(output, GEOXOutput)
    assert output.ok is True
    assert "n_lineaments" in output.result
    assert "n_discontinuities" in output.result
```

- [ ] **Step 5.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_feature_extract.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 5.3: Write `seismic_feature_extract.py`**

```python
# arifos/geox/tools/seismic_feature_extract.py
"""
GEOX Stage 3 — Image Feature Extraction (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Extracts lineaments, discontinuities, and dip field from seismic image.
ALL outputs are image-derived proxies — NOT trace-domain seismic attributes.
Labels mandatory: "image_derived_proxy".

Physics grounding: image gradients ≈ acoustic impedance contrast proxy.
This is an approximation — quality degrades without trace amplitude data.
"""
from __future__ import annotations

import numpy as np

from arifos.geox.schemas.geox_output import (
    GEOXOutput, GEOXUncertainty, GEOXContrastMeta, GEOXGovernance,
)
from arifos.geox.schemas.structural_interp import (
    FeatureSet, Lineament, Discontinuity, DipVector,
)
from arifos.geox.tools.seismic_visual_filter import (
    _gaussian_filter, _canny_filter, _convolve2d,
)

_KX = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
_KY = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)


def extract_features(image: np.ndarray, view_id: str) -> FeatureSet:
    """
    Extract geological feature proxies from a seismic image view.

    Args:
        image: Float64 [0, 1] 2D grayscale array.
        view_id: View identifier from SeismicView.view_id.

    Returns:
        FeatureSet with lineaments, discontinuities, dip_field.
        All labelled as image_derived_proxy.
    """
    img_uint8 = (np.clip(image, 0, 1) * 255).astype(np.uint8)

    # Smooth for gradient stability
    smooth = _gaussian_filter(img_uint8, kernel_size=5, sigma=1.4).output_array.astype(np.float64)

    # Gradient field
    gx = _convolve2d(smooth, _KX)
    gy = _convolve2d(smooth, _KY)
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    mag_max = magnitude.max() + 1e-10

    # Dip field (sampled every 20 pixels)
    h, w = image.shape[:2]
    dip_vectors: list[DipVector] = []
    for y in range(20, h - 20, 20):
        for x in range(20, w - 20, 20):
            dip_deg = float(np.degrees(np.arctan2(float(gy[y, x]), float(gx[y, x]) + 1e-10)))
            conf = float(min(magnitude[y, x] / mag_max, 1.0))
            dip_vectors.append(DipVector(x=float(x), y=float(y), dip_deg=dip_deg, confidence=conf))

    # Lineaments from Canny edges (horizontal-ish segments)
    edge_map = _canny_filter(img_uint8, low_threshold=40, high_threshold=120).output_array
    lineaments: list[Lineament] = []
    for y in range(0, h, 3):
        seg_start: int | None = None
        for x in range(w):
            if edge_map[y, x] > 0 and seg_start is None:
                seg_start = x
            elif (edge_map[y, x] == 0 or x == w - 1) and seg_start is not None:
                seg_len = x - seg_start
                if seg_len >= 8:
                    strength = float(min(
                        magnitude[y, seg_start:x].mean() / mag_max, 1.0
                    ))
                    lineaments.append(Lineament(
                        x0=float(seg_start), y0=float(y),
                        x1=float(x), y1=float(y),
                        strength=strength,
                        dip_deg=0.0,
                    ))
                seg_start = None
    lineaments = lineaments[:500]

    # Discontinuities: magnitude > mean + 2*std (high-gradient breaks)
    mag_mean = float(magnitude.mean())
    mag_std = float(magnitude.std())
    threshold = mag_mean + 2.0 * mag_std
    disc_y, disc_x = np.where(magnitude > threshold)
    discontinuities: list[Discontinuity] = []
    for y, x in zip(disc_y[::5], disc_x[::5]):
        discontinuities.append(Discontinuity(
            x=float(x),
            y=float(y),
            discontinuity_type="high_gradient_break",
            strength=float(min(magnitude[y, x] / mag_max, 1.0)),
        ))
    discontinuities = discontinuities[:200]

    return FeatureSet(
        view_id=view_id,
        lineaments=lineaments,
        discontinuities=discontinuities,
        dip_field=dip_vectors,
    )


def feature_extract_output(image: np.ndarray, view_id: str) -> GEOXOutput:
    """Band-A Stage 3: extract features, return GEOXOutput."""
    fs = extract_features(image, view_id)
    return GEOXOutput(
        ok=True,
        verdict="QUALIFY",
        uncertainty=GEOXUncertainty(
            level=0.15,
            type="image_gradient_proxy",
            notes=["Image gradients ≈ impedance contrast proxy. Noisy without trace data."],
        ),
        contrast_metadata=GEOXContrastMeta(
            processing_steps=["gaussian_smooth", "sobel_gradient", "canny_edge"],
            display_bias_risk="medium",
        ),
        governance=GEOXGovernance(
            floors_ok=["F4", "F7", "F9"],
            warnings=["All features are image-derived proxies. Trace data required for physical attributes."],
        ),
        result={
            "view_id": view_id,
            "n_lineaments": len(fs.lineaments),
            "n_discontinuities": len(fs.discontinuities),
            "n_dip_vectors": len(fs.dip_field),
            "epistemic_tag": "ESTIMATE",
            "note": "image_derived_proxy — not seismic trace attribute.",
        },
    )
```

- [ ] **Step 5.4: Run tests**

```
python -m pytest tests/tools/test_seismic_feature_extract.py -v
```
Expected: `5 passed`

- [ ] **Step 5.5: Commit**

```bash
git add arifos/geox/tools/seismic_feature_extract.py tests/tools/test_seismic_feature_extract.py
git commit -m "feat(geox): Stage 3 image feature extraction — lineaments, discontinuities, dip field"
```

---

## Task 6: Structure Rules Engine

**Files:**
- Create: `arifos/geox/tools/seismic_structure_rules.py`
- Create: `tests/tools/test_seismic_structure_rules.py`

- [ ] **Step 6.1: Write failing tests**

```python
# tests/tools/test_seismic_structure_rules.py
import numpy as np
import pytest
from arifos.geox.tools.seismic_structure_rules import (
    score_candidate, build_candidate, FAMILY_TEMPLATES, ALL_FAMILIES,
)
from arifos.geox.schemas.structural_interp import (
    StructuralCandidate, FeatureSet, Lineament, Discontinuity,
)

def make_rich_feature_set(n_disc=20, n_lin=30) -> FeatureSet:
    discs = [Discontinuity(x=float(i*5), y=float(i*3), strength=0.7) for i in range(n_disc)]
    lins = [Lineament(x0=0.0, y0=float(i*3), x1=50.0, y1=float(i*3), strength=0.8) for i in range(n_lin)]
    return FeatureSet(view_id="v1", discontinuities=discs, lineaments=lins)

def make_sparse_feature_set() -> FeatureSet:
    return FeatureSet(view_id="v1", discontinuities=[], lineaments=[])

def test_score_candidate_fault_with_evidence():
    fs = make_rich_feature_set()
    c = StructuralCandidate(family="normal_fault", support_views=["v1","v2","v3"])
    score, warnings = score_candidate(c, fs)
    assert 0.0 <= score <= 1.0
    assert score > 0.4  # should score reasonably with evidence

def test_score_candidate_fault_without_evidence():
    fs = make_sparse_feature_set()
    c = StructuralCandidate(family="normal_fault", support_views=["v1"])
    score, warnings = score_candidate(c, fs)
    assert score < 0.5  # penalized for no evidence
    assert len(warnings) > 0

def test_bond_warning_for_inversion():
    fs = make_sparse_feature_set()
    c = StructuralCandidate(family="inversion", support_views=["v1"])
    score, warnings = score_candidate(c, fs)
    bond_warnings = [w for w in warnings if "Bond" in w]
    assert len(bond_warnings) > 0

def test_all_families_are_defined():
    assert "normal_fault" in ALL_FAMILIES
    assert "inversion" in ALL_FAMILIES
    assert "fold" in ALL_FAMILIES
    assert len(ALL_FAMILIES) >= 7

def test_build_candidate_returns_scored_candidate():
    fs = make_rich_feature_set()
    c = build_candidate("fold", fs, support_views=["v1","v2","v3","v4"])
    assert isinstance(c, StructuralCandidate)
    assert c.family == "fold"
    assert 0.0 <= c.geology_score <= 1.0
    assert c.epistemic_tag in ("CLAIM","PLAUSIBLE","HYPOTHESIS","ESTIMATE")
```

- [ ] **Step 6.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_structure_rules.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 6.3: Write `seismic_structure_rules.py`**

```python
# arifos/geox/tools/seismic_structure_rules.py
"""
GEOX Stage 5 — Geological Rule Engine (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Applies geological plausibility rules to structural candidates.
Scores candidates; flags Bond-style bias warnings for ambiguous cases.

Bond et al. (2007): only 21% of experts correctly identified inversion
from an uninterpreted synthetic section. Rule engine must not be
overconfident — always present alternatives.

Constitutional floors: F4 (explicit criteria), F7 (bounded uncertainty),
F9 (no hallucinated geology — rules require evidence, not assumptions).
"""
from __future__ import annotations

from arifos.geox.schemas.structural_interp import FeatureSet, StructuralCandidate

FAMILY_TEMPLATES: dict[str, dict] = {
    "normal_fault": {
        "description": "Extensional faulting — hanging wall drops",
        "needs_discontinuity": True,
        "needs_lineaments": False,
        "min_discontinuities": 3,
    },
    "reverse_fault": {
        "description": "Compressional faulting — shallower dip, repeated section",
        "needs_discontinuity": True,
        "needs_lineaments": False,
        "min_discontinuities": 3,
    },
    "fold": {
        "description": "Folding without major faulting — reflector curvature",
        "needs_discontinuity": False,
        "needs_lineaments": True,
        "min_lineaments": 10,
    },
    "inversion": {
        "description": "Pre-existing extensional faults reactivated in compression",
        "needs_discontinuity": True,
        "needs_lineaments": True,
        "min_discontinuities": 3,
        "min_lineaments": 8,
        "bond_risk": True,
    },
    "duplex": {
        "description": "Thrust duplex — stacked thrust horses with consistent vergence",
        "needs_discontinuity": True,
        "needs_lineaments": False,
        "min_discontinuities": 5,
    },
    "stratigraphic": {
        "description": "Stratigraphic feature — truncation, onlap, no fault required",
        "needs_discontinuity": False,
        "needs_lineaments": True,
        "min_lineaments": 5,
    },
    "flower": {
        "description": "Flower structure — transpressional/transtensional diverging faults",
        "needs_discontinuity": True,
        "needs_lineaments": False,
        "min_discontinuities": 4,
    },
    "unknown": {
        "description": "Cannot classify — insufficient evidence",
        "needs_discontinuity": False,
        "needs_lineaments": False,
    },
}

ALL_FAMILIES: list[str] = list(FAMILY_TEMPLATES.keys())


def score_candidate(
    candidate: StructuralCandidate,
    feature_set: FeatureSet,
) -> tuple[float, list[str]]:
    """
    Apply geological rules to score a candidate.

    Returns (geology_score in [0.0, 1.0], warnings).
    """
    warnings: list[str] = []
    score = 0.5  # neutral baseline
    family = candidate.family
    template = FAMILY_TEMPLATES.get(family, {})
    n_disc = len(feature_set.discontinuities)
    n_lin = len(feature_set.lineaments)
    n_views = len(candidate.support_views)

    # Evidence checks
    if template.get("needs_discontinuity"):
        min_d = template.get("min_discontinuities", 3)
        if n_disc < min_d:
            score -= 0.2
            warnings.append(
                f"'{family}' requires discontinuity evidence (min {min_d}), found {n_disc}."
            )
        else:
            score += 0.15

    if template.get("needs_lineaments"):
        min_l = template.get("min_lineaments", 5)
        if n_lin < min_l:
            score -= 0.2
            warnings.append(
                f"'{family}' requires reflector continuity (min lineaments {min_l}), found {n_lin}."
            )
        else:
            score += 0.1

    # Inversion: Bond bias warning — always flag
    if template.get("bond_risk"):
        warnings.append(
            "Bond et al. (2007): inversion was the most-missed tectonic setting "
            "(79% expert failure rate on uninterpreted synthetics). "
            "High conceptual bias risk. Present multiple alternatives. "
            "Do not treat as CLAIM without orthogonal data or section restoration."
        )
        score -= 0.1  # additional humility penalty

    # Cross-view stability penalty
    if n_views <= 1:
        score -= 0.2
        warnings.append(
            f"Candidate seen in only {n_views} contrast view(s). "
            "Bond-style display bias risk — feature may be display artifact."
        )
    elif n_views >= 4:
        score += 0.1  # bonus for multi-view stability

    return float(max(0.0, min(1.0, score))), warnings


def build_candidate(
    family: str,
    feature_set: FeatureSet,
    support_views: list[str],
) -> StructuralCandidate:
    """
    Build a scored StructuralCandidate from features for one family.
    """
    # Extract fault proxies from discontinuities (cap at 20)
    faults = [
        {"x": d.x, "y": d.y, "type": family, "strength": d.strength}
        for d in feature_set.discontinuities[:20]
    ]
    # Extract horizon proxies from lineaments (cap at 30)
    horizons = [
        {"x0": l.x0, "y0": l.y0, "x1": l.x1, "y1": l.y1, "strength": l.strength}
        for l in feature_set.lineaments[:30]
    ]

    # Score against rules
    _temp_candidate = StructuralCandidate(
        family=family,  # type: ignore[arg-type]
        support_views=support_views,
    )
    geology_score, warnings = score_candidate(_temp_candidate, feature_set)

    # Uncertainty and epistemic tag
    is_high_risk = family in ("inversion", "duplex", "flower")
    uncertainty = 0.15 if is_high_risk else 0.12
    epistemic = "PLAUSIBLE" if len(support_views) >= 3 else "HYPOTHESIS"
    if family == "inversion":
        epistemic = "HYPOTHESIS"  # always HYPOTHESIS for inversion

    stability = min(len(support_views) / 6.0, 1.0)

    return StructuralCandidate(
        family=family,  # type: ignore[arg-type]
        faults=faults,
        horizons=horizons,
        support_views=support_views,
        geology_score=geology_score,
        stability_score=round(stability, 4),
        geometry_score=0.5,  # placeholder — ranker updates this
        warnings=warnings,
        uncertainty=uncertainty,
        epistemic_tag=epistemic,
    )
```

- [ ] **Step 6.4: Run tests**

```
python -m pytest tests/tools/test_seismic_structure_rules.py -v
```
Expected: `5 passed`

- [ ] **Step 6.5: Commit**

```bash
git add arifos/geox/tools/seismic_structure_rules.py tests/tools/test_seismic_structure_rules.py
git commit -m "feat(geox): Stage 5 geological rule engine — Bond-aware candidate scoring"
```

---

## Task 7: Candidate Ranker

**Files:**
- Create: `arifos/geox/tools/seismic_candidate_ranker.py`
- Create: `tests/tools/test_seismic_candidate_ranker.py`

- [ ] **Step 7.1: Write failing tests**

```python
# tests/tools/test_seismic_candidate_ranker.py
import numpy as np
from arifos.geox.tools.seismic_candidate_ranker import (
    build_candidates_from_features, rank_candidates, build_interpretation_result,
)
from arifos.geox.tools.seismic_feature_extract import extract_features
from arifos.geox.schemas.structural_interp import InterpretationResult
from arifos.geox.tools.seismic_structure_rules import ALL_FAMILIES

def make_synthetic_seismic(h=100, w=200):
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [20, 40, 60, 80]:
        img[max(0, y-1):y+2, :] = 0.8
    for y in range(h):
        x = int(w * 0.5 + y * 0.3)
        if 0 <= x < w:
            img[y, max(0, x-1):min(w, x+2)] = 0.5
    img += rng.normal(0, 0.05, (h, w))
    return np.clip(img, 0, 1)

def test_build_candidates_returns_all_families():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    feature_sets = [("v1", fs)]
    candidates = build_candidates_from_features(feature_sets)
    assert len(candidates) == len(ALL_FAMILIES)

def test_rank_candidates_sorted_descending():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    candidates = build_candidates_from_features([("v1", fs)])
    ranked = rank_candidates(candidates)
    scores = [c.composite_score for c in ranked]
    assert scores == sorted(scores, reverse=True)

def test_build_interpretation_result_has_2d_limits():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    candidates = rank_candidates(build_candidates_from_features([("v1", fs)]))
    result = build_interpretation_result(candidates, "L001")
    assert isinstance(result, InterpretationResult)
    assert len(result.two_d_limits) >= 4
    assert result.verdict in ("PASS", "QUALIFY", "HOLD", "GEOX_BLOCK")

def test_interpretation_result_confidence_bounded():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    candidates = rank_candidates(build_candidates_from_features([("v1", fs)]))
    result = build_interpretation_result(candidates, "L001")
    assert 0.0 <= result.confidence <= 1.0

def test_bias_audit_populated():
    image = make_synthetic_seismic()
    fs = extract_features(image, "v1")
    candidates = rank_candidates(build_candidates_from_features([("v1", fs)]))
    result = build_interpretation_result(candidates, "L001")
    assert "display_sensitivity" in result.bias_audit
    assert "n_views_used" in result.bias_audit
```

- [ ] **Step 7.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_candidate_ranker.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 7.3: Write `seismic_candidate_ranker.py`**

```python
# arifos/geox/tools/seismic_candidate_ranker.py
"""
GEOX Stages 4+6 — Candidate Builder + Ranker (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Builds one structural candidate per geological family from image features,
then ranks by composite score: 0.4*geometry + 0.3*stability + 0.3*geology.

Bond et al. (2007) bias flag: if top candidate stability < 0.4,
warn that multiple hypotheses must be maintained.
"""
from __future__ import annotations

from arifos.geox.schemas.structural_interp import FeatureSet, StructuralCandidate, InterpretationResult
from arifos.geox.tools.seismic_structure_rules import (
    ALL_FAMILIES, build_candidate, FAMILY_TEMPLATES,
)

_TWO_D_LIMITS = [
    "No true 3D trap geometry, closure area, or spill point — 2D line only.",
    "No reliable areal extent or volumetrics from single line.",
    "No confident fault network connectivity — out-of-plane effects possible.",
    "No direct HC claims — all amplitude anomalies require 3D + well ties.",
    "Apparent fault throw is 2D apparent throw — true throw unknown without strike data.",
]

_MISSING_INFORMATION = [
    "Well ties for depth calibration and polarity verification.",
    "Orthogonal 2D lines or 3D seismic volume for true geometry.",
    "Velocity model for depth conversion.",
    "Acquisition parameters for acquisition footprint assessment.",
]


def _compute_composite_score(c: StructuralCandidate) -> float:
    return 0.4 * c.geometry_score + 0.3 * c.stability_score + 0.3 * c.geology_score


def build_candidates_from_features(
    feature_sets: list[tuple[str, FeatureSet]],
) -> list[StructuralCandidate]:
    """Build one candidate per structural family from all view feature sets."""
    all_view_ids = [vid for vid, _ in feature_sets]
    # Use merged feature set: max features across all views for richest evidence
    merged = max(feature_sets, key=lambda vfs: len(vfs[1].discontinuities) + len(vfs[1].lineaments))[1]

    candidates: list[StructuralCandidate] = []
    for family in ALL_FAMILIES:
        # Fault families: support views = views with any discontinuity evidence
        if FAMILY_TEMPLATES.get(family, {}).get("needs_discontinuity"):
            support = [vid for vid, fs in feature_sets if len(fs.discontinuities) >= 2]
        else:
            support = all_view_ids  # fold/strat supported by all views
        c = build_candidate(family, merged, support_views=support)
        candidates.append(c)

    return candidates


def rank_candidates(candidates: list[StructuralCandidate]) -> list[StructuralCandidate]:
    """Rank by composite score; set composite_score field on each."""
    scored = [
        c.model_copy(update={"composite_score": round(_compute_composite_score(c), 4)})
        for c in candidates
    ]
    return sorted(scored, key=lambda c: c.composite_score, reverse=True)


def build_interpretation_result(
    ranked_candidates: list[StructuralCandidate],
    line_id: str,
    n_views: int = 1,
) -> InterpretationResult:
    """Build final InterpretationResult with bias audit and 2D limits."""
    if not ranked_candidates:
        return InterpretationResult(
            line_id=line_id,
            best_candidate_id="none",
            confidence=0.0,
            bias_audit={"display_sensitivity": "high", "n_views_used": n_views,
                        "notes": ["No candidates — insufficient features."]},
            summary="Insufficient image features to build structural interpretation.",
            verdict="GEOX_BLOCK",
            two_d_limits=_TWO_D_LIMITS,
            missing_information=_MISSING_INFORMATION,
        )

    best = ranked_candidates[0]
    alts = ranked_candidates[1:]

    # Bias audit
    stability = best.stability_score
    disp_sens = "low" if stability > 0.6 else ("medium" if stability > 0.3 else "high")
    bias_notes: list[str] = []
    if stability < 0.4:
        bias_notes.append(
            "Bond et al. (2007) display-bias risk: best candidate has low cross-view stability. "
            "Multiple working hypotheses must be maintained."
        )
    if best.family == "inversion":
        bias_notes.append(
            "Inversion: highest conceptual bias risk per Bond et al. (2007) — 79% expert failure rate."
        )

    # Confidence: composite score reduced if gap to 2nd is small
    confidence = best.composite_score
    if alts:
        gap = best.composite_score - alts[0].composite_score
        if gap < 0.1:
            confidence *= 0.8
            bias_notes.append(
                f"Score gap to 2nd candidate = {gap:.3f} — interpretations are ambiguous."
            )

    # Verdict
    if confidence >= 0.5 and stability >= 0.4:
        verdict = "QUALIFY"
    elif confidence < 0.35 or stability < 0.2:
        verdict = "HOLD"
    else:
        verdict = "QUALIFY"

    return InterpretationResult(
        line_id=line_id,
        best_candidate_id=best.candidate_id,
        alternatives=alts,
        confidence=round(confidence, 3),
        bias_audit={
            "display_sensitivity": disp_sens,
            "stability_score_best": round(stability, 3),
            "n_views_used": n_views,
            "notes": bias_notes,
        },
        two_d_limits=_TWO_D_LIMITS,
        missing_information=_MISSING_INFORMATION,
        summary=(
            f"Best structural candidate: {best.family} "
            f"(composite={best.composite_score:.3f}, uncertainty={best.uncertainty}). "
            f"Display sensitivity: {disp_sens}. "
            f"{len(alts)} alternatives ranked. "
            "All features are image-derived proxies — trace data required for physical attributes."
        ),
        verdict=verdict,
        telemetry={
            "agent": "@GEOX",
            "tool": "SingleLineRanker",
            "version": "0.3.0",
            "pipeline": "222_REFLECT",
            "floors": ["F1", "F4", "F7", "F9"],
            "seal": "DITEMPA BUKAN DIBERI",
        },
    )
```

- [ ] **Step 7.4: Run tests**

```
python -m pytest tests/tools/test_seismic_candidate_ranker.py -v
```
Expected: `5 passed`

- [ ] **Step 7.5: Commit**

```bash
git add arifos/geox/tools/seismic_candidate_ranker.py tests/tools/test_seismic_candidate_ranker.py
git commit -m "feat(geox): Stages 4+6 candidate builder and ranker — Bond-bias composite scoring"
```

---

## Task 8: Report Writer

**Files:**
- Create: `arifos/geox/tools/seismic_report_writer.py`
- Create: `tests/tools/test_seismic_report_writer.py`

- [ ] **Step 8.1: Write failing tests**

```python
# tests/tools/test_seismic_report_writer.py
import numpy as np
from arifos.geox.tools.seismic_report_writer import write_markdown_report, write_json_result
from arifos.geox.tools.seismic_feature_extract import extract_features
from arifos.geox.tools.seismic_candidate_ranker import (
    build_candidates_from_features, rank_candidates, build_interpretation_result,
)
from arifos.geox.schemas.structural_interp import SeismicImageInput

def make_result():
    rng = np.random.default_rng(42)
    img = np.clip(rng.normal(0.5, 0.2, (100, 200)), 0, 1)
    fs = extract_features(img, "v1")
    candidates = rank_candidates(build_candidates_from_features([("v1", fs)]))
    return build_interpretation_result(candidates, "L001", n_views=6)

def test_markdown_report_has_2d_limits():
    result = make_result()
    report = write_markdown_report(result, SeismicImageInput(image_path="test.png", line_id="L001"))
    assert "2D Data Limits" in report

def test_markdown_report_has_seal():
    result = make_result()
    report = write_markdown_report(result, SeismicImageInput(image_path="test.png", line_id="L001"))
    assert "DITEMPA BUKAN DIBERI" in report

def test_markdown_report_has_verdict():
    result = make_result()
    report = write_markdown_report(result, SeismicImageInput(image_path="test.png", line_id="L001"))
    assert result.verdict in report

def test_json_result_serializes():
    import json
    result = make_result()
    json_str = write_json_result(result)
    parsed = json.loads(json_str)
    assert "line_id" in parsed
    assert "verdict" in parsed
    assert "two_d_limits" in parsed

def test_markdown_report_saves_to_file(tmp_path):
    result = make_result()
    meta = SeismicImageInput(image_path="test.png", line_id="L001")
    write_markdown_report(result, meta, output_dir=tmp_path)
    out = tmp_path / "L001_interpretation.md"
    assert out.exists()
    assert "2D Data Limits" in out.read_text()
```

- [ ] **Step 8.2: Run to verify failure**

```
python -m pytest tests/tools/test_seismic_report_writer.py -v
```
Expected: `ModuleNotFoundError`

- [ ] **Step 8.3: Write `seismic_report_writer.py`**

```python
# arifos/geox/tools/seismic_report_writer.py
"""
GEOX Stage 7 — Governed Report Writer (Band-A Raster-only)
DITEMPA BUKAN DIBERI

Writes InterpretationResult to markdown and JSON.
LLM writes summary text ONLY after receiving structured outputs.
2D limits block is mandatory in every report.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from arifos.geox.schemas.structural_interp import InterpretationResult, SeismicImageInput


def write_markdown_report(
    result: InterpretationResult,
    input_meta: SeismicImageInput,
    output_dir: str | Path | None = None,
) -> str:
    """Write governed markdown interpretation report."""
    ts = datetime.now(timezone.utc).isoformat()
    lines = [
        f"# GEOX Seismic Interpretation — {result.line_id}",
        f"**Generated:** {ts}",
        f"**Verdict:** `{result.verdict}`",
        f"**Confidence:** {result.confidence:.3f}",
        f"**Source:** {input_meta.image_path}",
        "",
        "## Governed Summary",
        "",
        result.summary,
        "",
        "## 2D Data Limits (MANDATORY — read before acting on any output)",
        "",
    ]
    for limit in result.two_d_limits:
        lines.append(f"- {limit}")

    lines += [
        "",
        "## Structural Interpretation",
        "",
        f"**Best candidate ID:** `{result.best_candidate_id}`",
        f"**Alternatives:** {len(result.alternatives)} ranked",
        "",
        "## Bias Audit",
        "",
        f"**Display sensitivity:** {result.bias_audit.get('display_sensitivity', 'unknown')}",
        f"**Cross-view stability:** {result.bias_audit.get('stability_score_best', 'N/A')}",
        f"**Views used:** {result.bias_audit.get('n_views_used', 'N/A')}",
        "",
    ]
    for note in result.bias_audit.get("notes", []):
        lines.append(f"> {note}")
        lines.append("")

    lines += [
        "## Missing Information",
        "",
    ]
    for m in result.missing_information:
        lines.append(f"- {m}")

    lines += [
        "",
        "---",
        "*arifOS telemetry v2.1 · @GEOX · pipeline 222_REFLECT · "
        "floors F1 F4 F7 F9 · image_derived_proxy · DITEMPA BUKAN DIBERI*",
    ]

    report = "\n".join(lines)
    if output_dir:
        out = Path(output_dir) / f"{result.line_id}_interpretation.md"
        out.write_text(report, encoding="utf-8")
    return report


def write_json_result(
    result: InterpretationResult,
    output_dir: str | Path | None = None,
) -> str:
    """Serialize InterpretationResult to JSON string."""
    json_str = result.model_dump_json(indent=2)
    if output_dir:
        out = Path(output_dir) / f"{result.line_id}_interpretation.json"
        out.write_text(json_str, encoding="utf-8")
    return json_str
```

- [ ] **Step 8.4: Run tests**

```
python -m pytest tests/tools/test_seismic_report_writer.py -v
```
Expected: `5 passed`

- [ ] **Step 8.5: Commit**

```bash
git add arifos/geox/tools/seismic_report_writer.py tests/tools/test_seismic_report_writer.py
git commit -m "feat(geox): Stage 7 report writer — governed markdown + JSON output"
```

---

## Task 9: Integration Test (Bond Synthetic)

**Files:**
- Create: `tests/test_single_line_integration.py`

- [ ] **Step 9.1: Write integration test**

```python
# tests/test_single_line_integration.py
"""
End-to-end test: Band-A single-line structural interpreter.
Uses synthetic seismic (reflectors + fault) as Bond et al. (2007) proxy.

Validates:
  - Full pipeline runs without error
  - Output is honest (no overconfident PASS on ambiguous data)
  - 2D limits populated
  - Bias audit populated
  - Bond warning present for inversion candidate
  - All features labelled as image_derived_proxy
"""
import json
import numpy as np
import pytest

from arifos.geox.tools.seismic_image_ingest import load_seismic_image, ingest_seismic_image
from arifos.geox.tools.seismic_contrast_views import generate_contrast_views, contrast_views_output
from arifos.geox.tools.seismic_feature_extract import extract_features
from arifos.geox.tools.seismic_candidate_ranker import (
    build_candidates_from_features, rank_candidates, build_interpretation_result,
)
from arifos.geox.tools.seismic_report_writer import write_markdown_report, write_json_result
from arifos.geox.schemas.structural_interp import SeismicImageInput


def make_bond_synthetic(h=100, w=200) -> np.ndarray:
    """
    Synthetic seismic mimicking Bond et al. (2007) ambiguity:
    horizontal reflectors + diagonal fault + noise.
    Deliberately ambiguous — could be normal fault, inversion, or fold-fault.
    """
    rng = np.random.default_rng(42)
    img = np.zeros((h, w), dtype=np.float64)
    for y in [15, 30, 45, 60, 75, 90]:
        img[max(0, y-1):y+2, :] = 0.8
    # Diagonal fault — cuts reflectors
    for y in range(h):
        x = int(w * 0.5 + y * 0.25)
        if 0 <= x < w:
            img[y, max(0, x-1):min(w, x+2)] = 0.5
    img += rng.normal(0, 0.08, (h, w))
    return np.clip(img, 0, 1)


def test_bond_synthetic_full_pipeline(tmp_path):
    """Full Band-A pipeline: image → 6 views → features → rank → report."""
    image = make_bond_synthetic()

    # Stage 1: Save as .npy and ingest
    npy_path = tmp_path / "bond_synthetic.npy"
    np.save(str(npy_path), image)
    ingest_out = ingest_seismic_image(str(npy_path), {"line_id": "BOND-001"})
    assert ingest_out.ok is True
    assert ingest_out.verdict == "QUALIFY"  # raster → never PASS

    # Stage 2: Contrast views
    views = generate_contrast_views(image, "BOND-001")
    assert len(views) == 6

    # Stage 3: Feature extraction (from all 6 views)
    feature_sets = [(v.view_id, extract_features(arr, v.view_id)) for v, arr in views]
    for vid, fs in feature_sets:
        assert "image_derived_proxy" in fs.note  # Contract 2 compliance

    # Stage 4+6: Build and rank candidates
    candidates = rank_candidates(build_candidates_from_features(feature_sets))
    assert len(candidates) > 0

    # Stage 6: Interpretation result
    result = build_interpretation_result(candidates, "BOND-001", n_views=6)

    # Validate honesty — Bond synthetic is ambiguous, should not be PASS
    assert result.verdict != "PASS", "Ambiguous synthetic should never be PASS"
    assert result.confidence < 0.9, "Overconfident on ambiguous Bond synthetic"

    # 2D limits must be populated
    assert len(result.two_d_limits) >= 4

    # Bias audit must be populated
    assert "display_sensitivity" in result.bias_audit
    assert "n_views_used" in result.bias_audit

    # Inversion candidate must have Bond warning
    inversion_cand = next(
        (c for c in candidates if c.family == "inversion"), None
    )
    assert inversion_cand is not None
    bond_warnings = [w for w in inversion_cand.warnings if "Bond" in w]
    assert len(bond_warnings) > 0, "Bond et al. (2007) warning missing from inversion candidate"

    # Stage 7: Reports
    meta = SeismicImageInput(image_path=str(npy_path), line_id="BOND-001")
    report_md = write_markdown_report(result, meta, output_dir=tmp_path)
    report_json = write_json_result(result, output_dir=tmp_path)

    assert "2D Data Limits" in report_md
    assert "DITEMPA BUKAN DIBERI" in report_md

    parsed = json.loads(report_json)
    assert parsed["line_id"] == "BOND-001"
    assert len(parsed["two_d_limits"]) >= 4

    # Output files exist
    assert (tmp_path / "BOND-001_interpretation.md").exists()
    assert (tmp_path / "BOND-001_interpretation.json").exists()
```

- [ ] **Step 9.2: Run integration test**

```
python -m pytest tests/test_single_line_integration.py -v
```
Expected: `1 passed`

- [ ] **Step 9.3: Run full test suite**

```
python -m pytest tests/ -v --tb=short
```
Expected: All tests pass.

- [ ] **Step 9.4: Commit**

```bash
git add tests/test_single_line_integration.py
git commit -m "test(geox): Bond synthetic integration test — Band-A pipeline end-to-end"
```

---

## Task 10: Final Run + Tag

- [ ] **Step 10.1: Run all tests with coverage**

```
python -m pytest tests/ -v
```
Expected: All pass, no failures.

- [ ] **Step 10.2: Commit all new files**

```bash
git add docs/superpowers/specs/ docs/superpowers/plans/
git add arifos/geox/knowledge/seismic_attribute_taxonomy.yaml
git commit -m "docs(geox): design spec + implementation plan — Band-A single-line interpreter"
```

- [ ] **Step 10.3: Summary of what was built**

```
Band-A Single-Line Structural Interpreter — SEALED
=====================================================
New schemas:     geox_output.py, structural_interp.py
New tools (6):   seismic_image_ingest, seismic_contrast_views,
                 seismic_feature_extract, seismic_structure_rules,
                 seismic_candidate_ranker, seismic_report_writer
New tests:       8 unit test files + 1 integration test (Bond synthetic)
Knowledge:       seismic_attribute_taxonomy.yaml (40 attributes, sprint map)
Design docs:     spec + plan in docs/superpowers/

Capabilities forged:
  ✅ Structural interpretation from single PNG/NPY seismic image
  ✅ 6-variant contrast-bias testing (Bond et al. 2007 aware)
  ✅ Geological rule engine (8 structural families)
  ✅ Bond-bias warnings mandatory for inversion candidates
  ✅ 2D limits block on every report
  ✅ Epistemic labels (CLAIM/PLAUSIBLE/HYPOTHESIS) on all outputs
  ✅ Common GEOXOutput envelope — all tools, same shape

Not yet built (Band B + C):
  ⏳ Trace-domain attributes (SEG-Y, AVO, inversion)
  ⏳ HC attribute summary
  ⏳ Event/waveform context

arifOS telemetry v2.1 · @GEOX v0.3.0 · floors F1 F4 F7 F9 F13
DITEMPA BUKAN DIBERI
```

---

*Plan saved to `docs/superpowers/plans/2026-03-31-single-line-structural-interpreter.md`*
*Spec at `docs/superpowers/specs/2026-03-31-single-line-structural-interpreter-design.md`*
