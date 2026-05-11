# GEOX Map v3 — Spatial Commons Release Note

## What Changed

Complete rewrite of `geox/map/index.html` to v3 "Spatial Commons":
- 3-column grid layout: sidebar(400px) + map + inspector panel(300px)
- Layer contract registry (`layerCatalog` JS object) with 10 layer entries
- Right inspector panel (7 sections): Point Info, Geology Result, Earthquake Nearby, Coordinate Verification, MCP Chain Log, Provenance, Handoff
- Bottom query tray with 3 tabs: Query Log, Fetch Status, Errors
- GEBCO bathymetry via `L.tileLayer.wms()` — WMS layer confirmed live
- MacroSTRAT geologic units as point probe (inspector panel only, not map overlay)
- MacroSTRAT paleogeography as toggleable overlay
- USGS earthquake layer with `checkEarthquakesNearby()` — nearest 3 within 50km shown in inspector
- MCP chain log with timestamps
- Fetch status tracker for all 10 layer sources
- Handoff buttons (WELL, PROSPECT, EARTH3D, CROSS) — open in new tab with lat/lon params

## Layer Status

| Layer | Status | Detail |
|-------|--------|--------|
| OSM | live | XYZ tiles confirmed |
| Satellite | live | ArcGIS World Imagery confirmed |
| GEBCO Bathymetry | live | WMS GetMap 200, 131KB PNG tile confirmed |
| USGS Earthquakes | live | GeoJSON loaded, circleMarkers rendered |
| Paleogeography | live | MacroSTRAT GeoJSON confirmed |
| Geologic Units | live | MacroSTRAT point probe on click |
| Natural Earth Boundaries | partial | ArcGIS tile service partial |
| Quaternary Faults | blocked | No stable public GeoJSON/ArcGIS path |
| GEM Active Faults | blocked | No stable public GeoJSON path |
| SRTM Hillshade | deferred | Requires terrain tile pipeline |

## Architecture

- `layerCatalog[]` — 10 entries with full provenance fields
- Inspector panel sections 1-7 as specified
- Bottom tray tabs: [QUERY LOG] [FETCH STATUS] [ERRORS]
- Init: setView [4.5, 114.5] (SE Asia), earthquake GeoJSON auto-loaded, OSM default on
- Status: "GEOX MAP V3 INITIALIZED"

## Known Blockers

- Quaternary Faults: No stable public GeoJSON or ArcGIS API path found
- GEM Active Faults: No stable public GeoJSON download path
- SRTM Hillshade: Requires terrain tile generation pipeline

## Rollback

```bash
git checkout <previous-branch>
# or
git checkout HEAD~1 geox-site/map/index.html
```

## Files Changed

- `geox-site/map/index.html` — 1856 lines, ~78KB
- `GEOX_MAP_RELEASE_NOTE.md` — this file
