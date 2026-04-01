"""
GEOX Seismic Viewer — FastMCP App

Geologist-grade seismic section viewer for AI chat.
Renders in host iframe with scale bars, legends, overlays, and geological insight.

Architecture:
- Model-visible: geox_open_seismic_viewer (entrypoint)
- App-visible: Backend tools for overlays, analysis, export

Components:
- Viewer canvas: Base seismic image with zoom/pan
- Legend panel: Colorbar, polarity, units
- Overlay layers: Reflectors, faults, facies (toggleable)
- Insight panel: Geological reasoning, confidence, limitations
- QC badges: Audit warnings, scale status

DITEMPA BUKAN DIBERI
"""

__version__ = "0.1.0-alpha"
__app_id__ = "geox-seismic-viewer"

from .app import create_seismic_viewer_app, geox_open_seismic_viewer

__all__ = ["create_seismic_viewer_app", "geox_open_seismic_viewer"]
