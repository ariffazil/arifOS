# GEOX Architecture: Open Earth Stack 🌍

> **Status:** APPROVED | **Authority:** 888_JUDGE
> **Reference:** Open-source Earth Engine, Terrain, and Imagery substrate for arifOS Ring 3.

## 1. Core Runtime (The Engines)
GEOX standardizes on the following engines for 3D and 2D spatial grounding:

*   **3D Earth Engine:** `CesiumGS/cesium` (Apache 2.0). High-precision WGS84 visualization using 3D Tiles.
*   **2D Map Engine:** `maplibre/maplibre-gl-js`. GPU-accelerated ArcGIS-style interaction using the MapLibre Style Spec.
*   **Explorer Shell:** `TerriaJS/terriajs`. Catalog-driven UI for federated geospatial data discovery.

## 2. Data Standards (The Models)
To ensure zero-entropy data exchange, GEOX mandates these cloud-native formats:

| Layer | Standard | Purpose |
| :--- | :--- | :--- |
| **Catalog** | **STAC** | SpatioTemporal Asset Catalog for discovery. |
| **Raster** | **COG** | Cloud Optimized GeoTIFF for seismic/imagery. |
| **3D/Mesh** | **3D Tiles** | Streaming terrain, buildings, and point clouds. |
| **Vector Tiles** | **PMTiles** | Single-file static tile archives. |
| **Analytics** | **GeoParquet** | Columnar storage for vector warehousing. |

## 3. Spatial Infrastructure (The Backend)
The "Body" of GEOX spatial operations is built on:

*   **Database:** `PostGIS` (PostgreSQL) + **GDAL** for translation.
*   **Vector Serving:** `maplibre/martin` for PostGIS/PMTiles tile delivery.
*   **Raster Serving:** `developmentseed/titiler` for dynamic COG/STAC queries.
*   **Interoperability:** `geoserver/geoserver` for legacy OGC API (WMS/WFS) support.

## 4. Canonical Data Sources (The Earth Witness)
GEOX defines "Reality" through these open sources:

*   **Basemap:** OpenStreetMap (via **Protomaps** PMTiles).
*   **Terrain:** **Copernicus DEM GLO-30** (Primary) | NASADEM/SRTM (Fallback).
*   **Imagery:** **Sentinel-2** (10m modern) | **Landsat Collection 2** (Historical context).
*   **Bathymetry:** **GEBCO 2025** Grid (15 arc-second ocean terrain).
*   **Geology:** **Macrostrat** (Homogenized geologic maps) | **OneGeology** (Global web services).

## 5. Subsurface Source Architecture
Unlike global Earth data, subsurface data is split into two governance tiers:
1.  **Sovereign Tier:** Private enterprise lakes (SEG-Y, ZGY, LAS, DLIS).
2.  **Public Tier:** National portals (**USGS NAMSS**, **SODIR** Norway, **Australia NOPIMS**).

---
*Ditempa Bukan Diberi — G = A × P × X × E²*
