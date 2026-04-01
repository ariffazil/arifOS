#!/usr/bin/env python3
"""
GEOX MCP Server — FastMCP 3.0 Aligned
Dual-App Architecture: Map Context + Seismic Viewer

Model-Visible Tools (AI discovers and calls):
  - geox_health
  - geox_open_map_context
  - geox_open_seismic_viewer
  - geox_evaluate_prospect (legacy)

App-Visible Tools (UI calls, hidden from AI):
  - geox_compute_display_scale
  - geox_generate_overlay_reflectors
  - geox_generate_overlay_faults
  - geox_analyze_roi
  - geox_get_map_features
  - geox_select_map_feature
  - geox_open_section_from_feature
  - ... (see each app)

Run:
    python server.py                    # STDIO mode
    python server.py --transport http   # HTTP mode
    fastmcp run server.py               # Via CLI

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import argparse
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("geox.server")

# =============================================================================
# Bootstrap
# =============================================================================

_REPO_ROOT = Path(__file__).parent.resolve()
_ARIFOS_PATH = _REPO_ROOT / "arifos"

if _ARIFOS_PATH.exists() and str(_ARIFOS_PATH.parent) not in sys.path:
    sys.path.insert(0, str(_ARIFOS_PATH.parent))

# =============================================================================
# FastMCP Import
try:
    from fastmcp import FastMCP, Context
    _HAS_FASTMCP = True
    logger.info("✅ FastMCP loaded")
except ImportError:
    _HAS_FASTMCP = False
    logger.error("❌ FastMCP not installed. Install: pip install fastmcp==3.0.0")
    sys.exit(1)

# =============================================================================
# Import GEOX Modules
_GEOX_AVAILABLE = False
try:
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import GeoMemoryStore
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    _GEOX_AVAILABLE = True
    logger.info("✅ GEOX core modules loaded")
except ImportError as e:
    logger.warning("⚠️  GEOX core modules not available: %s", e)

# Import Seismic Image modules
_SEISMIC_IMAGE_AVAILABLE = False
try:
    from arifos.geox.seismic_image.schemas import (
        ImageType, VerticalUnit, PolarityStandard, Verdict
    )
    from arifos.geox.seismic_image.ingest import ingest_seismic_image
    from arifos.geox.seismic_image.schemas import SeismicImageIngestRequest
    _SEISMIC_IMAGE_AVAILABLE = True
    logger.info("✅ Seismic image modules loaded")
except ImportError as e:
    logger.warning("⚠️  Seismic image modules not available: %s", e)

# Import Viewer App
_VIEWER_AVAILABLE = False
try:
    from arifos.geox.seismic_viewer.app import (
        geox_open_seismic_viewer,
        geox_compute_display_scale,
        geox_generate_overlay_reflectors,
        geox_generate_overlay_faults,
        geox_generate_geology_insight_panel,
        geox_save_annotation,
        geox_export_view_snapshot,
        geox_analyze_roi,
    )
    _VIEWER_AVAILABLE = True
    logger.info("✅ Seismic viewer app loaded")
except ImportError as e:
    logger.warning("⚠️  Seismic viewer app not available: %s", e)

# Import Map Context App
_MAP_AVAILABLE = False
try:
    from arifos.geox.map_context.app import (
        geox_open_map_context,
        geox_get_map_features,
        geox_select_map_feature,
        geox_open_section_from_feature,
        geox_search_map_features,
    )
    _MAP_AVAILABLE = True
    logger.info("✅ Map context app loaded")
except ImportError as e:
    logger.warning("⚠️  Map context app not available: %s", e)


# =============================================================================
# Server State
# =============================================================================

class GEOXState:
    """Shared server state."""
    
    def __init__(self):
        self.config: Any = None
        self.agent: Any = None
        self.initialized = False
        self.start_time = datetime.now(timezone.utc)
    
    async def initialize(self) -> None:
        """Initialize GEOX core."""
        if self.initialized or not _GEOX_AVAILABLE:
            return
        try:
            self.config = GeoXConfig()
            self.agent = GeoXAgent(config=self.config)
            self.initialized = True
            logger.info("✅ GEOX core initialized")
        except Exception as e:
            logger.exception("Failed to initialize GEOX: %s", e)

_geox_state = GEOXState()


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[GEOXState]:
    """Manage server lifecycle."""
    logger.info("=" * 60)
    logger.info("🚀 GEOX MCP Server v0.5.0 — Dual-App Architecture")
    logger.info("   Map Context + Seismic Viewer")
    logger.info("   DITEMPA BUKAN DIBERI")
    logger.info("=" * 60)
    
    if _GEOX_AVAILABLE:
        await _geox_state.initialize()
    
    logger.info("✅ Server ready")
    yield _geox_state
    
    logger.info("👋 Server shutting down")


# =============================================================================
# Main FastMCP App
# =============================================================================

mcp = FastMCP(
    "GEOX",
    lifespan=app_lifespan,
    instructions="""
GEOX — Geological Intelligence Coprocessor

**Model-Visible Tools** (Call these):
- geox_open_map_context — Geographic navigation and basin overview
- geox_open_seismic_viewer — Geologist-grade seismic section viewer
- geox_health — Server status

**Apps:**
- Map Context: Interactive map with seismic lines, wells, prospects
- Seismic Viewer: Section interpretation with overlays and insight panel

**Workflow:**
1. Open map context to explore basin
2. Click seismic line → Open section viewer
3. Toggle overlays, examine features, view geological insight

All outputs include uncertainty quantification and constitutional governance.
"""
)


# =============================================================================
# MODEL-VISIBLE TOOLS (AI discovers and calls these)
# =============================================================================

@mcp.tool()
async def geox_health(ctx: Context) -> dict[str, Any]:
    """
    GEOX server health check.
    
    Returns status of all modules and apps.
    """
    return {
        "success": True,
        "status": "healthy",
        "version": "0.5.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modules": {
            "geox_core": _GEOX_AVAILABLE,
            "seismic_image": _SEISMIC_IMAGE_AVAILABLE,
            "seismic_viewer": _VIEWER_AVAILABLE,
            "map_context": _MAP_AVAILABLE,
        },
        "capabilities": {
            "map_context": _MAP_AVAILABLE,
            "seismic_viewer": _VIEWER_AVAILABLE,
            "dual_app_workflow": _MAP_AVAILABLE and _VIEWER_AVAILABLE,
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


@mcp.tool()
async def geox_open_map_context(
    ctx: Context,
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
    **🗺️ GEOX Map Context** — Open geographic navigation map.
    
    Shows seismic lines, wells, prospects, and basin boundaries on an interactive map.
    Use this first when exploring a basin or locating seismic data.
    
    **When to use:**
    - "Show me NW Sabah basin"
    - "Where is the Bunga Raya prospect?"
    - "Map all seismic lines in Malay Basin"
    - "Show wells near this area"
    
    **Features:**
    - Interactive satellite/street map
    - Seismic line footprints (click to view metadata)
    - Well locations with status (producer, abandoned, etc.)
    - Prospect polygons with confidence
    - Click any feature to view details and link to section viewer
    
    **Example:**
    ```
    query="NW Sabah"
    basin="NW Sabah Basin"
    layers=["basemap", "basin", "lines", "wells", "prospects"]
    ```
    
    Args:
        query: Geographic search (basin name, coordinates, feature name)
        requester_id: User identifier for traceability
        basin: Filter by basin name
        prospect: Focus on specific prospect
        line_name: Highlight specific seismic line
        center_lat: Map center latitude
        center_lon: Map center longitude
        zoom_level: Zoom level 1-20 (default: 10)
        layers: Active layers [basemap, basin, lines, wells, prospects, faults]
    
    Returns:
        Map app content with feature list and interactive UI
    """
    if not _MAP_AVAILABLE:
        return {
            "success": False,
            "error": "Map context app not available",
            "seal": "DITEMPA BUKAN DIBERI",
        }
    
    return await geox_open_map_context(
        query=query,
        requester_id=requester_id,
        basin=basin,
        prospect=prospect,
        line_name=line_name,
        center_lat=center_lat,
        center_lon=center_lon,
        zoom_level=zoom_level,
        layers=layers,
    )


@mcp.tool()
async def geox_open_seismic_viewer(
    ctx: Context,
    image_path: str,
    basin: str,
    line_name: str,
    vertical_unit: str,
    vertical_scale: float,
    horizontal_scale: float,
    requester_id: str,
    image_type: str = "raw_seismic",
    polarity_known: bool = False,
    polarity_standard: str = "unknown",
    overlays: dict[str, bool] | None = None,
    geological_intent: str = "General interpretation",
    play_hypothesis: str = "structural",
) -> dict[str, Any]:
    """
    **📊 GEOX Seismic Viewer** — Open geologist-grade seismic section viewer.
    
    Renders seismic section with scale bars, legends, overlays, and geological insight panel.
    Use this for detailed interpretation of seismic sections.
    
    **When to use:**
    - "Open seismic line MB-2024-042"
    - "Show me the section with reflectors and faults"
    - "Interpret this seismic image"
    - "What do you see in this section?"
    
    **Features:**
    - Proper scale bars (vertical and horizontal)
    - Legend with polarity and amplitude scale
    - Toggleable overlays:
      - Reflector candidates (red lines)
      - Fault likelihood (yellow heatmap)
      - Facies segmentation (colored masks)
    - Geological insight panel with:
      - Section summary
      - Key features with confidence
      - Counter-hypotheses
      - Limitations and uncertainty
    - QC badges and audit warnings
    
    **Required Metadata:**
    You MUST provide scale information:
    - vertical_unit: meters, feet, seconds_TWT, milliseconds_TWT
    - vertical_scale: Units per pixel (e.g., 4.0 = 4 meters/pixel)
    - horizontal_scale: Distance per pixel (e.g., 12.5 = 12.5m/pixel)
    
    **Example:**
    ```
    image_path="/data/mb_2024_042.png"
    basin="Malay Basin"
    line_name="MB-2024-042"
    vertical_unit="meters"
    vertical_scale=4.0
    horizontal_scale=12.5
    overlays={"reflectors": true, "faults": true}
    play_hypothesis="deltaic"
    ```
    
    Args:
        image_path: Path to seismic image (PNG, JPG, TIFF)
        basin: Sedimentary basin name
        line_name: Seismic line identifier
        vertical_unit: Vertical axis unit (meters, feet, seconds_TWT)
        vertical_scale: Vertical scale in units per pixel
        horizontal_scale: Horizontal scale in units per pixel
        requester_id: User identifier
        image_type: Type of image (raw_seismic, attribute_display)
        polarity_known: Whether SEG polarity known
        polarity_standard: SEG polarity convention
        overlays: Toggle overlays {reflectors, faults, facies, uncertainty}
        geological_intent: Specific interpretation goal
        play_hypothesis: Geological play hypothesis
    
    Returns:
        Seismic viewer app with image, overlays, and insight panel
    """
    if not _VIEWER_AVAILABLE:
        return {
            "success": False,
            "error": "Seismic viewer app not available",
            "seal": "DITEMPA BUKAN DIBERI",
        }
    
    # Import here to avoid circular import
    from arifos.geox.seismic_viewer.app import geox_open_seismic_viewer as viewer_main
    
    return await viewer_main(
        image_path=image_path,
        basin=basin,
        line_name=line_name,
        vertical_unit=vertical_unit,
        vertical_scale=vertical_scale,
        horizontal_scale=horizontal_scale,
        requester_id=requester_id,
        image_type=image_type,
        polarity_known=polarity_known,
        polarity_standard=polarity_standard,
        overlays=overlays,
        geological_intent=geological_intent,
        play_hypothesis=play_hypothesis,
    )


# =============================================================================
# APP-VISIBLE TOOLS (UI calls, not AI-visible)
# =============================================================================
# These would be marked with visibility=["app"] in FastMCP 3.0+
# For now, they follow naming convention: geox_* but are internal

@mcp.tool()
async def geox_app_compute_display_scale(
    ctx: Context,
    image_id: str,
    vertical_unit: str,
    vertical_scale: float,
    horizontal_scale: float,
) -> dict[str, Any]:
    """
    [APP TOOL] Compute display scale for viewer.
    Called by seismic viewer UI. Not for AI use.
    """
    if not _VIEWER_AVAILABLE:
        return {"success": False, "error": "Viewer not available"}
    return await geox_compute_display_scale(image_id, vertical_unit, vertical_scale, horizontal_scale)


@mcp.tool()
async def geox_app_generate_overlay_reflectors(
    ctx: Context,
    image_path: str,
    image_id: str,
) -> dict[str, Any]:
    """
    [APP TOOL] Generate reflector overlay.
    Called when user toggles reflector layer.
    """
    if not _VIEWER_AVAILABLE:
        return {"success": False, "error": "Viewer not available"}
    return await geox_generate_overlay_reflectors(image_path, image_id)


@mcp.tool()
async def geox_app_generate_overlay_faults(
    ctx: Context,
    image_path: str,
    image_id: str,
) -> dict[str, Any]:
    """
    [APP TOOL] Generate fault overlay.
    Called when user toggles fault layer.
    """
    if not _VIEWER_AVAILABLE:
        return {"success": False, "error": "Viewer not available"}
    return await geox_generate_overlay_faults(image_path, image_id)


@mcp.tool()
async def geox_app_analyze_roi(
    ctx: Context,
    image_path: str,
    image_id: str,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    geological_intent: str,
) -> dict[str, Any]:
    """
    [APP TOOL] Analyze region of interest.
    Called when user selects ROI in viewer.
    """
    if not _VIEWER_AVAILABLE:
        return {"success": False, "error": "Viewer not available"}
    return await geox_analyze_roi(image_path, image_id, x0, y0, x1, y1, geological_intent)


@mcp.tool()
async def geox_app_get_map_features(
    ctx: Context,
    bbox: dict[str, float],
    layers: list[str],
) -> dict[str, Any]:
    """
    [APP TOOL] Query map features.
    Called when user pans/zooms map.
    """
    if not _MAP_AVAILABLE:
        return {"success": False, "error": "Map not available"}
    return await geox_get_map_features(bbox, layers)


@mcp.tool()
async def geox_app_select_map_feature(
    ctx: Context,
    feature_id: str,
) -> dict[str, Any]:
    """
    [APP TOOL] Select map feature.
    Called when user clicks feature.
    """
    if not _MAP_AVAILABLE:
        return {"success": False, "error": "Map not available"}
    return await geox_select_map_feature(feature_id)


@mcp.tool()
async def geox_app_open_section_from_feature(
    ctx: Context,
    feature_id: str,
    feature_type: str,
) -> dict[str, Any]:
    """
    [APP TOOL] Open section from line feature.
    Bridge from map to section viewer.
    """
    if not _MAP_AVAILABLE:
        return {"success": False, "error": "Map not available"}
    return await geox_open_section_from_feature(feature_id, feature_type)


# =============================================================================
# Legacy Tool
# =============================================================================

@mcp.tool()
async def geox_evaluate_prospect(
    ctx: Context,
    query: str,
    prospect_name: str,
    latitude: float,
    longitude: float,
    basin: str,
    play_type: str,
    risk_tolerance: str,
    requester_id: str,
    depth_m: float | None = None,
    available_data: list[str] | None = None,
) -> dict[str, Any]:
    """
    Legacy prospect evaluation (general geology).
    
    For seismic image interpretation, use geox_open_seismic_viewer instead.
    """
    return {
        "success": True,
        "verdict": "PARTIAL",
        "message": "For seismic image interpretation, use geox_open_seismic_viewer",
        "capabilities": ["map_context", "seismic_viewer"],
        "seal": "DITEMPA BUKAN DIBERI",
    }


# =============================================================================
# Entrypoint
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GEOX MCP Server — Map + Seismic Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                    # STDIO mode (Claude Desktop)
  python server.py --transport http   # HTTP mode on port 8100

Apps:
  - Map Context: geox_open_map_context
  - Seismic Viewer: geox_open_seismic_viewer

Workflow:
  1. Call geox_open_map_context to explore basin
  2. Click seismic line → UI calls geox_app_open_section_from_feature
  3. Seismic viewer opens with section, overlays, insight panel
        """
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode"
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP bind host")
    parser.add_argument("--port", type=int, default=8100, help="HTTP bind port")
    args = parser.parse_args()
    
    if args.transport == "http":
        logger.info("Starting HTTP transport on %s:%d", args.host, args.port)
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        logger.info("Starting STDIO transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
