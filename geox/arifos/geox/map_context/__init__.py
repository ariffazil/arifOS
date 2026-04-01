"""
GEOX Map Context — FastMCP App

Geographic context and navigation for seismic interpretation.
Shows basin overview, prospect locations, seismic line footprints, wells.
Links to seismic section viewer for detailed interpretation.

Architecture:
- Model-visible: geox_open_map_context (entrypoint)
- App-visible: Backend tools for feature queries, selection, section linking

Use Cases:
- Basin overview and navigation
- Prospect location context
- Seismic line selection
- Well-to-section correlation

DITEMPA BUKAN DIBERI
"""

__version__ = "0.1.0-alpha"
__app_id__ = "geox-map-context"

from .app import create_map_context_app, geox_open_map_context

__all__ = ["create_map_context_app", "geox_open_map_context"]
