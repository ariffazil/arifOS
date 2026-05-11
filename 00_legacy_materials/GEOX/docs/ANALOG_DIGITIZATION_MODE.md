# ANALOG_DIGITIZATION_MODE.md — Raster-to-Digital Evolution

> **Status:** ARCHITECTURAL SPEC | **Authority:** 888_JUDGE
> **Focus:** Scanned Logs (1D) & Scanned Maps/Sections (2D)
> **Doctrine:** Trust through Provenance
> **Seal:** DITEMPA BUKAN DIBERI

---

## 🏛️ Executive Summary
Analog data (scanned images) contains the majority of legacy subsurface intelligence. GEOX must treat these not as static "pictures" but as **uncalibrated evidence**. This mode provides the tools to rectify, register, and digitize rasters into structured GEOX Canonical JSON.

## 🛠️ Module Tree (`analog-*`)

### 1. `analog-ingest`
- **Scope:** TIFF/JPEG/PDF scan intake.
- **Requirements:** DPI awareness, metadata extraction, brightness/contrast normalization.

### 2. `analog-calibrate`
- **1D (Scale):** Gridline/Track-edge detection, depth calibration (pixels-to-meters/feet).
- **2D (Spatial):** GCP (Ground Control Point) management, transformation model selection (Linear, Polynomial, Thin Plate Spline).
- **2D (Section):** Axis-based calibration for cross-sections (Horizontal distance vs. Vertical elevation).

### 3. `analog-digitize`
- **1D (Well):** Curve tracing (Manual, Semi-auto shortest-path, ML-assisted), track segmentation.
- **2D (Map):** Vectorization of points (wells), lines (faults/contacts), and polygons (lithology).

### 4. `analog-qc`
- **Scope:** Residual error reporting, transformation "warping" preview, human-in-the-loop verification.
- **Mandate:** No digitized product enters the structural model without a `Verified-By-Human` signature.

---

## 🔄 The MCP Contract: `Registration-First`

Before digitization, the MCP tool returns a **Registration Manifest**.

```json
{
  "type": "analog_registration",
  "source": "LOG_WELL_A_SCAN.JPG",
  "registration": {
    "system": "depth_linear",
    "calibration_points": [
      { "pixel_y": 100, "depth": 1500.0 },
      { "pixel_y": 5000, "depth": 2500.0 }
    ],
    "residual_error": 0.002
  }
}
```

---

## 🛠️ Build Order

1.  **Phase 1 (1D Analog):** Rectification and Depth Calibration → Curve Tracing → LAS Export.
2.  **Phase 2 (2D Analog):** GCP-based Map Georeferencing → Vector Digitization → GeoJSON Export.
3.  **Phase 3 (Integration):** Feed digitized logs to Petrophysics Engine; feed digitized maps to GemPy Structural Engine.

---

*Spec initialized by Gemini CLI | 2026.04.11*
