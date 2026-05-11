# GEOX Analog Digitization Mode (Spec v0.1.0)
## DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

This document defines the high-precision specification for the GEOX "Analog Forge"—the specialized mode for calibrating, georeferencing, and digitizing analog legacy data (scanned logs, maps, and seismic).

---

## 1. Core Philosophy: The Interpretive Manifest
Analog digitization is not a side-task; it is a **primary evidence-capture mode**. All analog source data must be registered to either physical scale (1D) or geographic coordinate (2D) systems before being admitted to the interpretation flow.

### Architectural Philosophy
- **Provenance**: Every digitized point must track its source scan, DPI, calibration anchors, and human override log.
- **Uncertainty**: GEOX emits a mandatory **Residual Error** report for each georeferenced product.
- **Evidence-Grade Objects**: Digitized outputs are stored as "Evidence-Grade Derived Objects," requiring **Human Confirmation** before promotion to modeling flows.
- **Bimodal Support**: Support for both **1D scale-calibrated** (depth/value) and **2D georeferenced** (coordinate/projection) pipelines.

---

## 2. 1D Workflow: Scanned Well-Log Digitization
**Reference Path**: KGS DEWL, NeuraLog precision.

1.  **Ingest**: Intake of TIFF/JPEG scan (DPI-aware processing).
2.  **Preprocessing**: De-skewing, noise reduction, and track-edge detection.
3.  **Spatial Calibration**:
    *   **Anchor Set**: Define absolute Depth (Top/Bottom) and Value (Left/Right) axis anchors.
    *   **Scale Detection**: Automatic detection of gridline spacing to confirm vertical/horizontal scale consistency.
4.  **Digitization (Triple-Mode)**:
    *   **Manual Pick**: Click-by-click plotting.
    *   **Semi-Auto Tracing**: Shortest-path curve extraction between two points.
    *   **AI Extraction**: CNN-based curve segmentation and classification.
5.  **Export**: Manifest generation for `Wellioviz` and standard LAS 2.0 output via `lasio`.

---

## 3. 2D Workflow: Map & Section Georeferencing
**Reference Path**: QGIS Georeferencer, MapWarper, GDAL.

1.  **GCP Management**: Capture Ground Control Points (GCPs) by matching image pixels (X, Y) to real-world coordinates (Lat/Lon) or Seismic Grid indices (CDP/Time).
2.  **Transformation Selection**:
    *   **Polynomial**: For simple rotation/scale.
    *   **Thin Plate Spline (TPS)**: For warping distorted/folded paper map scans.
3.  **Warp & Preview**: Real-time browser-native warp preview against a global basemap (Leaflet/Cesium).
4.  **Vectorization**: Digitization of points, lines (contacts/faults), and polygons (lithology).
5.  **Export**: GeoJSON/GeoPackage manifests for `Plotly` and `arifOS` geospatial tools.

---

## 4. MCP Manifest Schema: `analog_digitization_state`

```json
{
  "type": "analog_digitization_manifest",
  "source_uri": "s3://geox-vault/analog/well_A1_scan.jpg",
  "mode": "1d_log",
  "calibration": {
    "engine": "analog-calibrate-1d",
    "anchors": [
      { "pixel": [100, 500], "depth": 1500.0, "value": 0.0 },
      { "pixel": [1100, 500], "depth": 1500.0, "value": 150.0 }
    ],
    "residual_error": 0.02
  },
  "vectors": [
    { "id": "GR", "points": "[[x1,y1,v1], [x2,y2,v2]]", "status": "human_confirmed" }
  ]
}
```

---

## 5. Required Module Tree (`analog-*`)

- `analog-ingest`: Intake, metadata, DPI normalization.
- `analog-calibrate-1d`: Scale/depth/value axis calibration logic.
- `analog-georef-2d`: GCP management, transformation (GDAL b-backend), CRS handling.
- `analog-digitize-1d`: Curve tracing, assisted picks, LAS export.
- `analog-digitize-2d`: Vector capture (contacts, faults), GeoJSON export.
- `analog-qc`: Error reporting, residual analysis, provenance logs.
- `analog-ai`: OCR, legend extraction, curve classification.

---

## 6. Build Order

1.  **Borehole First**: Implement 1D Log Rectifier and Depth Calibration. Simple axis system, high immediate value.
2.  **Map Logic**: Implement 2D GCP capturing and GDAL-based warping for image alignment.
3.  **The 3D Bridge**: Connect analog-derived outputs as constraints for **GemPy** structural modeling.

*DITEMPA BUKAN DIBERI. SEALED.*
