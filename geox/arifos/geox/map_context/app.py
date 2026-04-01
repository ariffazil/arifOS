"""
FastMCP Map Context App

Geographic navigation and context for GEOX seismic interpretation.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

try:
    from fastmcp import FastMCP
    _HAS_FASTMCP = True
except ImportError:
    _HAS_FASTMCP = False

logger = logging.getLogger("geox.map_context")


# =============================================================================
# Schemas
# =============================================================================

class MapFeature(BaseModel):
    """Geographic feature for map display."""
    
    feature_id: str
    feature_type: str = Field(..., description="prospect, line, well, aoi, fault_trace")
    name: str
    geometry: dict[str, Any]  # GeoJSON-like
    properties: dict[str, Any]
    source: str
    confidence: float = Field(default=1.0, ge=0, le=1)
    linked_assets: list[dict[str, Any]] = Field(default_factory=list)


class MapContextRequest(BaseModel):
    """Request to open map context."""
    
    query: str = Field(..., description="Geographic query or feature name")
    basin: str | None = Field(default=None, description="Basin filter")
    prospect: str | None = Field(default=None, description="Prospect filter")
    line_name: str | None = Field(default=None, description="Specific line")
    center_lat: float | None = None
    center_lon: float | None = None
    zoom_level: int = Field(default=10, ge=1, le=20)
    layers: list[str] = Field(default_factory=lambda: ["basemap", "basin", "lines", "wells"])
    requester_id: str = Field(..., description="User identifier")


class MapContextState(BaseModel):
    """Complete state for map context."""
    
    center: dict[str, float]
    zoom: int
    bounds: dict[str, float]
    features: list[MapFeature]
    selected_feature: MapFeature | None = None
    available_layers: list[str]
    active_layers: list[str]


# =============================================================================
# Model-Visible Entry Point
# =============================================================================

async def geox_open_map_context(
    query: str,
    requester_id: str,
    basin: str | None = None,
    prospect: str | None = None,
    line_name: str | None = None,
    center_lat: float | None = None,
    center_lon: float | None = None,
    zoom_level: int = 10,
    layers: list[str] | None = None,
) -> dict[str, Any]:
    """
    **GEOX Map Context** — Open geographic navigation and basin context map.
    
    Shows seismic lines, wells, prospects, and AOIs in geographic space.
    Click features to view metadata and link to seismic section viewer.
    
    ## What This Shows
    - Interactive map with satellite/street basemap
    - Seismic line footprints (polylines)
    - Well locations with status indicators
    - Prospect polygons with confidence
    - Basin boundaries
    - Click-to-select for detailed view
    
    ## Example Usage
    ```
    "Show me NW Sabah prospects"
    → geox_open_map_context(
        query="NW Sabah",
        basin="NW Sabah Basin",
        layers=["basemap", "basin", "prospects", "lines", "wells"],
        requester_id="arif.fazil"
      )
    ```
    
    Args:
        query: Geographic search query
        requester_id: User identifier for traceability
        basin: Filter by basin name
        prospect: Focus on specific prospect
        line_name: Highlight specific line
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom_level: Initial zoom (1-20)
        layers: Active layers (basemap, basin, lines, wells, prospects, faults)
    
    Returns:
        Structured map app content for host iframe rendering
    """
    logger.info("Opening map context for query: %s, basin: %s", query, basin)
    
    # Mock data for demonstration
    # In production, this would query a spatial database
    
    center = {
        "lat": center_lat or 6.5,
        "lon": center_lon or 116.5,
    }
    
    bounds = {
        "north": center["lat"] + 0.5,
        "south": center["lat"] - 0.5,
        "east": center["lon"] + 0.5,
        "west": center["lon"] - 0.5,
    }
    
    # Generate mock features
    features = _generate_mock_features(query, basin, bounds)
    
    map_state = {
        "center": center,
        "zoom": zoom_level,
        "bounds": bounds,
        "features": [f.model_dump() for f in features],
        "selected_feature": None,
        "available_layers": ["basemap", "satellite", "basin", "lines", "wells", "prospects", "faults", "aoi"],
        "active_layers": layers or ["basemap", "basin", "lines"],
    }
    
    # Build UI
    ui_components = _build_map_ui(map_state, query)
    
    logger.info("Map context opened with %d features", len(features))
    
    return {
        "success": True,
        "query": query,
        "basin": basin,
        "map_state": map_state,
        "ui": ui_components,
        "capabilities": {
            "can_zoom": True,
            "can_pan": True,
            "can_select": True,
            "can_search": True,
            "can_link_to_section": True,
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


def _generate_mock_features(
    query: str,
    basin: str | None,
    bounds: dict[str, float],
) -> list[MapFeature]:
    """Generate mock geographic features for demonstration."""
    
    features = []
    
    # Seismic lines
    lines = [
        {"name": "MB-2024-001", "type": "2D", "status": "interpreted"},
        {"name": "MB-2024-042", "type": "2D", "status": "new"},
        {"name": "MB-2023-107", "type": "2D", "status": "legacy"},
    ]
    
    for i, line in enumerate(lines):
        # Generate line geometry (simplified)
        lat_start = bounds["south"] + 0.1 + i * 0.15
        lon_start = bounds["west"] + 0.1
        lat_end = lat_start
        lon_end = bounds["east"] - 0.1
        
        features.append(MapFeature(
            feature_id=f"line-{line['name']}",
            feature_type="line",
            name=line["name"],
            geometry={
                "type": "LineString",
                "coordinates": [
                    [lon_start, lat_start],
                    [lon_end, lat_end],
                ],
            },
            properties={
                "line_type": line["type"],
                "status": line["status"],
                "length_km": 45.0,
                "orientation": "E-W",
            },
            source="PETRONAS Seismic Database",
            confidence=0.95,
            linked_assets=[
                {"type": "section_image", "name": f"{line['name']}.png", "available": True},
                {"type": "seg_y", "name": f"{line['name']}.sgy", "available": line["status"] == "new"},
            ],
        ))
    
    # Wells
    wells = [
        {"name": "Bunga Raya-1", "status": "producer", "type": "oil"},
        {"name": "Bunga Raya-2", "status": "abandoned", "type": "dry"},
        {"name": "Tembikai-1", "status": "appraisal", "type": "gas"},
    ]
    
    for i, well in enumerate(wells):
        lat = bounds["south"] + 0.2 + i * 0.2
        lon = bounds["west"] + 0.2 + i * 0.1
        
        features.append(MapFeature(
            feature_id=f"well-{well['name']}",
            feature_type="well",
            name=well["name"],
            geometry={
                "type": "Point",
                "coordinates": [lon, lat],
            },
            properties={
                "well_status": well["status"],
                "hydrocarbon_type": well["type"],
                "td_m": 3200,
                "completion_date": "2023-06",
            },
            source="Wells Database",
            confidence=1.0,
            linked_assets=[
                {"type": "well_log", "name": f"{well['name']}_logs.las", "available": True},
                {"type": "report", "name": f"{well['name']}_ geological.pdf", "available": True},
            ],
        ))
    
    # Prospects
    prospects = [
        {"name": "Bunga Raya Deep", "confidence": 0.75, "volume_mmboe": 45},
        {"name": "Tembikai West", "confidence": 0.60, "volume_mmboe": 120},
    ]
    
    for i, prospect in enumerate(prospects):
        center_lat = bounds["south"] + 0.3 + i * 0.25
        center_lon = bounds["west"] + 0.3
        
        # Polygon (simplified rectangle)
        coords = [
            [center_lon - 0.05, center_lat - 0.05],
            [center_lon + 0.05, center_lat - 0.05],
            [center_lon + 0.05, center_lat + 0.05],
            [center_lon - 0.05, center_lat + 0.05],
            [center_lon - 0.05, center_lat - 0.05],
        ]
        
        features.append(MapFeature(
            feature_id=f"prospect-{prospect['name'].replace(' ', '-')}",
            feature_type="prospect",
            name=prospect["name"],
            geometry={
                "type": "Polygon",
                "coordinates": [coords],
            },
            properties={
                "confidence": prospect["confidence"],
                "volume_mmboe": prospect["volume_mmboe"],
                "play_type": "Deltaic",
                "risk_level": "medium",
            },
            source="Prospect Inventory",
            confidence=prospect["confidence"],
            linked_assets=[
                {"type": "prospect_report", "name": f"{prospect['name']}_prospect.pdf", "available": True},
            ],
        ))
    
    return features


def _build_map_ui(state: dict[str, Any], query: str) -> dict[str, Any]:
    """Build map UI component tree."""
    
    features = state["features"]
    
    # Count by type
    counts = {
        "lines": len([f for f in features if f["feature_type"] == "line"]),
        "wells": len([f for f in features if f["feature_type"] == "well"]),
        "prospects": len([f for f in features if f["feature_type"] == "prospect"]),
    }
    
    return {
        "type": "map_context",
        "layout": "full",
        "map": {
            "type": "leaflet_map",
            "center": state["center"],
            "zoom": state["zoom"],
            "bounds": state["bounds"],
            "layers": state["active_layers"],
            "base_map": "satellite",
        },
        "sidebar": {
            "title": f"Map Context: {query}",
            "sections": [
                {
                    "title": "Features",
                    "badge": f"{len(features)} total",
                    "items": [
                        f"📊 {counts['lines']} seismic lines",
                        f"🗼 {counts['wells']} wells",
                        f"🎯 {counts['prospects']} prospects",
                    ],
                },
                {
                    "title": "Layers",
                    "toggle_list": [
                        {"id": "basemap", "label": "Base Map", "active": True},
                        {"id": "satellite", "label": "Satellite", "active": False},
                        {"id": "basin", "label": "Basin Boundary", "active": True},
                        {"id": "lines", "label": "Seismic Lines", "active": True},
                        {"id": "wells", "label": "Wells", "active": "wells" in state["active_layers"]},
                        {"id": "prospects", "label": "Prospects", "active": "prospects" in state["active_layers"]},
                        {"id": "faults", "label": "Fault Traces", "active": False},
                    ],
                },
                {
                    "title": "Selected Feature",
                    "content": "Click a feature on the map to view details",
                    "placeholder": True,
                },
            ],
        },
        "feature_popup_template": {
            "line": {
                "title": "{name}",
                "fields": ["line_type", "status", "length_km", "orientation"],
                "actions": [
                    {"id": "open_section", "label": "Open Seismic Section", "primary": True},
                    {"id": "view_metadata", "label": "View Metadata"},
                ],
            },
            "well": {
                "title": "{name}",
                "fields": ["well_status", "hydrocarbon_type", "td_m"],
                "actions": [
                    {"id": "view_logs", "label": "View Well Logs"},
                    {"id": "view_report", "label": "View Report"},
                ],
            },
            "prospect": {
                "title": "{name}",
                "fields": ["play_type", "confidence", "volume_mmboe", "risk_level"],
                "actions": [
                    {"id": "view_prospect", "label": "View Prospect Details"},
                    {"id": "compare_to_analogs", "label": "Compare to Analogs"},
                ],
            },
        },
        "toolbar": [
            {"id": "search", "icon": "🔍", "tooltip": "Search features"},
            {"id": "zoom_in", "icon": "+", "tooltip": "Zoom in"},
            {"id": "zoom_out", "icon": "-", "tooltip": "Zoom out"},
            {"id": "reset_bounds", "icon": "⟲", "tooltip": "Reset view"},
            {"id": "measure_distance", "icon": "📏", "tooltip": "Measure distance"},
        ],
        "status_bar": {
            "coordinates": "Lat: {lat:.4f}, Lon: {lon:.4f}",
            "scale": "1:{scale}",
            "crs": "WGS-84",
        },
    }


# =============================================================================
# App-Visible Backend Tools
# =============================================================================

async def geox_get_map_features(
    bbox: dict[str, float],
    layers: list[str],
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Query map features within bounding box.
    
    Called by map UI when user pans/zooms to load features dynamically.
    """
    # In production, query spatial database
    return {
        "success": True,
        "bbox": bbox,
        "features": [],  # Would be populated from DB
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_select_map_feature(
    feature_id: str,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Select and highlight a feature.
    
    Called when user clicks a feature on the map.
    """
    return {
        "success": True,
        "feature_id": feature_id,
        "selected": True,
        "details": {
            "linked_assets": [],
            "related_features": [],
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_open_section_from_feature(
    feature_id: str,
    feature_type: str,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Open seismic section from line feature.
    
    Bridge from map to section viewer.
    """
    if feature_type != "line":
        return {
            "success": False,
            "error": "Can only open sections from line features",
        }
    
    # Extract line name from feature_id
    line_name = feature_id.replace("line-", "")
    
    return {
        "success": True,
        "feature_id": feature_id,
        "line_name": line_name,
        "action": "OPEN_SECTION_VIEWER",
        "params": {
            "line_name": line_name,
            # Would include actual image_path from database
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_search_map_features(
    query: str,
    feature_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Search for features by name or attribute.
    
    Called by map search box.
    """
    return {
        "success": True,
        "query": query,
        "results": [],  # Would be populated from search
        "seal": "DITEMPA BUKAN DIBERI",
    }


# =============================================================================
# FastMCP App Factory
# =============================================================================

def create_map_context_app() -> FastMCP | None:
    """Create FastMCP App for map context."""
    
    if not _HAS_FASTMCP:
        logger.error("FastMCP not available")
        return None
    
    app = FastMCP(
        "geox-map-context",
        instructions="""
GEO Map Context — Geographic navigation for seismic interpretation.

Shows basin overview, seismic lines, wells, and prospects on an interactive map.
Click features to view details and open seismic sections.
"""
    )
    
    @app.tool()
    async def open_map_context(**kwargs) -> dict[str, Any]:
        """Entry point for opening map context."""
        return await geox_open_map_context(**kwargs)
    
    @app.tool()
    async def get_map_features(**kwargs) -> dict[str, Any]:
        """[APP] Query map features."""
        return await geox_get_map_features(**kwargs)
    
    @app.tool()
    async def select_map_feature(**kwargs) -> dict[str, Any]:
        """[APP] Select feature."""
        return await geox_select_map_feature(**kwargs)
    
    @app.tool()
    async def open_section_from_feature(**kwargs) -> dict[str, Any]:
        """[APP] Open section from line."""
        return await geox_open_section_from_feature(**kwargs)
    
    @app.tool()
    async def search_map_features(**kwargs) -> dict[str, Any]:
        """[APP] Search features."""
        return await geox_search_map_features(**kwargs)
    
    return app
