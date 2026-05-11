# VISION_INTELLIGENCE_ARCHITECTURE.md — The GEOX Integration & Visualization Shell

> **Status:** ARCHITECTURAL DRAFT
> **Authority:** 888_JUDGE
> **Paradigm:** Parse → Normalize → Manifest → Hydrate
> **Seal:** DITEMPA BUKAN DIBERI

## Executive Summary

GEOX is best framed as a governed geological interpretation shell rather than a pure visualization app, because the open stack already separates parsing, modeling, and rendering into distinct capabilities. The most robust web architecture is a three-layer system: an integration shell for dirty industry data, an interpretation engine for domain math and governance, and a hydration layer that turns manifests into interactive browser components. [justingosses.github](https://justingosses.github.io/wellioviz/)

## Layers

### 1. The Integration Shell

The foundation layer should convert heterogeneous source formats into GEOX Canonical JSON before any interpretation or rendering occurs. For 1D well data, Wellio.js and the Wellioviz pipeline show a practical browser-oriented path where LAS content is normalized before track rendering. For 2D seismic, a Python-side normalization path remains appropriate because seismic payloads are larger and usually need preprocessing before browser delivery, while coordinate reference system and unit normalization should be mandatory before any calculation or display. [github](https://github.com/PangJiutian/Seisvis)

### 2. The Interpretation Engine

The interpretation layer should host petrophysical equations, structural inference, and governance checks on normalized data rather than embedding logic in the frontend. GemPy is especially relevant here because it is described as an open-source 3D structural geological modeling engine, which places it in the geological modeling layer instead of the pure rendering layer. In GEOX terms, this is also the right place to enforce Floors F1–F13 on calculated outputs before any visual hydration is exposed to humans or agents. [gempy](https://www.gempy.org)

### 3. The Hydration Layer

The hydration layer should render manifests into interactive components selected by dimensional use case. For 1D, Wellioviz is aligned with SVG/D3-style track visualization for well logs. For 2D analyst views, Plotly.js is a strong default for crossplots, contours, and heatmap-style views, while Seisvis shows that browser-based seismic section and volume workflows are viable in a JS/TS stack. For 3D, vtk.js is the more scientific scene choice for subsurface objects, while Cesium-style globe experiences are better reserved for regional or planetary context rather than core subsurface interpretation. [plotly](https://plotly.com/javascript/)

## The MCP Contract: Manifest-First

Instead of returning opaque screenshots by default, GEOX MCP tools should emit hydration manifests that preserve semantic structure for both human UI and AI-side reasoning. This approach matches the declarative nature of Wellioviz configuration and Plotly figure schemas, making it easier to support both static exports and fully interactive clients from the same canonical data source. [justingosses.github](https://justingosses.github.io/wellioviz/)

```json
{
  "type": "well_log_track",
  "version": "1.0.0",
  "metadata": {
    "uwi": "LAYANG-1",
    "crs": "EPSG:4326"
  },
  "manifest": {
    "engine": "wellioviz",
    "template": "petrophysics_standard",
    "data_payload": {
      "curves": [],
      "depth": [],
      "units": {}
    }
  }
}
```

A practical contract split is `parse -> normalize -> manifest -> hydrate`, with parser tools never leaking raw vendor chaos directly to end-user components if canonical schemas can be enforced first. [gempy](https://www.gempy.org)

## Hardened Build Order

### Phase 1: 1D Dominance

The first production milestone should be LAS ingestion and well-log rendering, because the reviewed public stack is most mature in this dimension. A GEOX GUI that ingests LAS, normalizes curves and metadata, and renders standard petrophysical tracks would establish immediate value with relatively low frontend complexity compared with seismic or 3D structural scenes. [github](https://github.com/JustinGOSSES/wellioviz)

### Phase 2: 2D Analyst

The second phase should add Plotly-based crossplots and lightweight seismic heatmaps for analyst-speed iteration. In parallel, a lower-level WebGL or Canvas path should be scaffolded for high-density seismic textures and picking workflows, because research repositories such as Seisvis indicate that heavier browser seismic interaction needs specialized rendering strategies beyond generic charting. [plotly](https://plotly.com/javascript/)

### Phase 3: 3D Structural

The third phase should integrate GemPy-backed structural modeling and a browser scientific scene layer for faults, horizons, and block frameworks. This phase is where GEOX moves beyond display toward true constitutional interpretation, because the 3D scene becomes the visible consequence of governed geological inference rather than a standalone visual product. [gempy](https://www.gempy.org)

## Architectural Position

The key distinction is that commercial geological platforms derive value not only from polished rendering but also from data conditioning and interpretation machinery hidden behind the interface. GEOX should therefore treat visualization as the user-facing shell for a governed evidence graph, where humans and AI agents inspect and act on the same normalized geological state through MCP-compatible manifests. [github](https://github.com/PangJiutian/Seisvis)
