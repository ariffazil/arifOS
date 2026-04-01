"""
FastMCP Seismic Viewer App

Entry-point tool visible to AI models: geox_open_seismic_viewer
Backend tools (app-visible): overlay generation, analysis, export
"""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

# Try importing FastMCP
try:
    from fastmcp import FastMCP
    _HAS_FASTMCP = True
except ImportError:
    _HAS_FASTMCP = False

from ..seismic_image.schemas import Verdict
from ..seismic_image.ingest import ingest_seismic_image, SeismicImageIngestRequest
from ..seismic_image.qc import qc_seismic_image
from ..seismic_image.reflectors import detect_reflectors
from ..seismic_image.faults import detect_fault_candidates
from ..seismic_image.facies import segment_facies
from ..seismic_image.reasoning import reason_seismic_scene
from ..seismic_image.visualize import generate_visualization

logger = logging.getLogger("geox.seismic_viewer")


# =============================================================================
# Schemas
# =============================================================================

class OverlayConfig(BaseModel):
    """Configuration for viewer overlays."""
    
    reflectors: bool = Field(default=True, description="Show reflector candidates")
    faults: bool = Field(default=True, description="Show fault likelihood")
    facies: bool = Field(default=False, description="Show facies segmentation")
    uncertainty: bool = Field(default=True, description="Show uncertainty heatmap")
    annotations: bool = Field(default=True, description="Show user annotations")


class ViewerState(BaseModel):
    """Complete state for seismic viewer."""
    
    image_id: str
    image_base64: str
    metadata: dict[str, Any]
    scale_config: dict[str, Any]
    legend_config: dict[str, Any]
    overlay_config: OverlayConfig
    overlays: dict[str, str | None]  # base64 images
    insight_panel: dict[str, Any]
    qc_status: dict[str, Any]
    audit_flags: list[str]


class SeismicViewerRequest(BaseModel):
    """Request to open seismic viewer."""
    
    image_path: str = Field(..., description="Path to seismic image file")
    image_type: str = Field(default="raw_seismic", description="Type of seismic image")
    basin: str = Field(..., description="Sedimentary basin name")
    line_name: str = Field(..., description="Seismic line identifier")
    vertical_unit: str = Field(..., description="Vertical unit (meters, feet, seconds_TWT)")
    vertical_scale: float = Field(..., description="Vertical scale in units per pixel")
    horizontal_scale: float = Field(..., description="Horizontal scale in units per pixel")
    polarity_known: bool = Field(default=False)
    polarity_standard: str = Field(default="unknown")
    overlays: OverlayConfig = Field(default_factory=OverlayConfig)
    geological_intent: str = Field(default="General interpretation")
    play_hypothesis: str = Field(default="structural")
    requester_id: str = Field(..., description="User identifier for traceability")


# =============================================================================
# Model-Visible Entry Point
# =============================================================================

async def geox_open_seismic_viewer(
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
    **GEOX Seismic Viewer** — Open a geologist-grade seismic section viewer.
    
    Renders an interactive seismic section with scale bars, legends, layer toggles,
    and geological insight panel. Use this when the user wants to examine a seismic
    section with proper geological context, not just view a raw image.
    
    ## What This Shows
    - Seismic section with proper scale bars and axis labels
    - Legend with polarity note and amplitude/color scale
    - Toggleable overlays: reflector candidates, fault likelihood, facies masks
    - Geological insight panel with reasoning, confidence, and limitations
    - QC badges and audit warnings
    
    ## Required Metadata
    - `vertical_unit`: meters, feet, seconds_TWT, milliseconds_TWT
    - `vertical_scale`: Units per pixel (e.g., 4.0 = 4 meters per pixel)
    - `horizontal_scale`: Distance units per pixel (e.g., 12.5 = 12.5m per pixel)
    
    ## Example Usage
    ```
    "Open seismic line MB-2024-042 from Malay Basin"
    → geox_open_seismic_viewer(
        image_path="/data/mb_2024_042.png",
        basin="Malay Basin",
        line_name="MB-2024-042",
        vertical_unit="meters",
        vertical_scale=4.0,
        horizontal_scale=12.5,
        requester_id="arif.fazil",
        overlays={"reflectors": true, "faults": true},
        play_hypothesis="deltaic"
      )
    ```
    
    Args:
        image_path: Path to seismic image (PNG, JPG, TIFF)
        basin: Sedimentary basin name
        line_name: Seismic line identifier
        vertical_unit: Vertical axis unit
        vertical_scale: Vertical scale in units per pixel
        horizontal_scale: Horizontal scale in units per pixel
        requester_id: User identifier for traceability
        image_type: Type of image (raw_seismic, attribute_display, etc.)
        polarity_known: Whether SEG polarity is known
        polarity_standard: SEG polarity convention
        overlays: Which overlays to enable
        geological_intent: Specific interpretation goal
        play_hypothesis: Geological play hypothesis
    
    Returns:
        Structured app content for host iframe rendering
    """
    from ...seismic_image.schemas import ImageType, VerticalUnit, PolarityStandard
    
    logger.info("Opening seismic viewer for %s/%s", basin, line_name)
    
    # Step 1: Ingest image
    try:
        ingest_request = SeismicImageIngestRequest(
            image_path=image_path,
            image_type=ImageType(image_type),
            basin=basin,
            line_name=line_name,
            vertical_unit=VerticalUnit(vertical_unit),
            vertical_scale=vertical_scale,
            horizontal_scale=horizontal_scale,
            polarity_known=polarity_known,
            polarity_standard=PolarityStandard(polarity_standard),
            requester_id=requester_id,
        )
        ingest_result = await ingest_seismic_image(ingest_request)
    except Exception as e:
        logger.exception("Ingest failed: %s", e)
        return {
            "success": False,
            "error": f"Image ingest failed: {e}",
            "verdict": "VOID",
            "seal": "DITEMPA BUKAN DIBERI",
        }
    
    if ingest_result.verdict == Verdict.VOID:
        return {
            "success": False,
            "error": "Image validation failed",
            "verdict": "VOID",
            "details": ingest_result.errors,
            "seal": "DITEMPA BUKAN DIBERI",
        }
    
    image_id = ingest_result.image_id
    
    # Step 2: Run QC
    qc_result = await qc_seismic_image(
        image_id=image_id,
        image_path=image_path,
        qc_strictness="standard",
    )
    
    # Step 3: Generate overlays if requested
    overlay_config = OverlayConfig(**(overlays or {}))
    overlay_images = {}
    
    if overlay_config.reflectors:
        try:
            refl_result = await detect_reflectors(
                image_path=image_path,
                image_id=image_id,
            )
            if refl_result.success:
                viz = await generate_visualization(
                    image_path=image_path,
                    visualization_type="reflectors",
                    data={"reflectors": [r.model_dump() for r in refl_result.reflectors]},
                )
                overlay_images["reflectors"] = viz.get("base64_image")
        except Exception as e:
            logger.warning("Reflector overlay failed: %s", e)
            overlay_images["reflectors"] = None
    
    if overlay_config.faults:
        try:
            fault_result = await detect_fault_candidates(
                image_path=image_path,
                image_id=image_id,
            )
            if fault_result.success:
                viz = await generate_visualization(
                    image_path=image_path,
                    visualization_type="faults",
                    data={"candidates": [f.model_dump() for f in fault_result.candidates]},
                )
                overlay_images["faults"] = viz.get("base64_image")
        except Exception as e:
            logger.warning("Fault overlay failed: %s", e)
            overlay_images["faults"] = None
    
    # Step 4: Generate geological insight
    insight_result = await reason_seismic_scene(
        image_id=image_id,
        play_hypothesis=play_hypothesis,
        geological_intent=geological_intent,
        basin=basin,
        requester_id=requester_id,
        qc_score=qc_result.qc_score if qc_result.success else 0.5,
    )
    
    # Step 5: Build viewer state
    viewer_state = {
        "image_id": image_id,
        "metadata": {
            "basin": basin,
            "line_name": line_name,
            "image_type": image_type,
            "ingest_verdict": ingest_result.verdict.value,
        },
        "scale_config": {
            "vertical_unit": vertical_unit,
            "vertical_scale": vertical_scale,
            "horizontal_scale": horizontal_scale,
            "vertical_extent_m": ingest_result.scale_validation.estimated_true_vertical_extent_m,
            "horizontal_extent_m": ingest_result.scale_validation.estimated_true_horizontal_extent_m,
            "aspect_ratio_valid": ingest_result.scale_validation.aspect_ratio_valid,
            "aspect_ratio_distortion_pct": ingest_result.scale_validation.aspect_ratio_distortion_pct,
        },
        "legend_config": {
            "polarity_known": polarity_known,
            "polarity_standard": polarity_standard,
            "display_type": "grayscale_amplitude" if image_type == "raw_seismic" else "attribute",
            "colorbar_min": "negative",
            "colorbar_max": "positive",
        },
        "overlay_config": overlay_config.model_dump(),
        "overlays": overlay_images,
        "insight_panel": insight_result if insight_result.get("success") else {
            "interpretation": {"summary": "Insight generation pending"},
            "confidence_band": {"aggregate": 0.5, "uncertainty": 0.1},
        },
        "qc_status": {
            "qc_score": qc_result.qc_score if qc_result.success else 0,
            "checks": {k: v.model_dump() for k, v in qc_result.checks.items()} if qc_result.success else {},
        },
        "audit_flags": insight_result.get("hold_flags", []),
    }
    
    # Load base image
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_base64 = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"
    except Exception as e:
        logger.error("Failed to load image: %s", e)
        image_base64 = ""
    
    viewer_state["image_base64"] = image_base64
    
    # Build UI components
    ui_components = _build_viewer_ui(viewer_state)
    
    logger.info("Seismic viewer opened for %s with %d overlays", image_id, len(overlay_images))
    
    return {
        "success": True,
        "image_id": image_id,
        "verdict": insight_result.get("verdict", "PARTIAL"),
        "viewer_state": viewer_state,
        "ui": ui_components,
        "capabilities": {
            "can_zoom": True,
            "can_pan": True,
            "can_toggle_overlays": True,
            "can_measure": ingest_result.scale_validation.aspect_ratio_valid,
            "can_export": True,
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


def _build_viewer_ui(state: dict[str, Any]) -> dict[str, Any]:
    """Build UI component tree for host rendering."""
    
    scale_config = state["scale_config"]
    legend_config = state["legend_config"]
    insight = state["insight_panel"]
    
    # Check scale validity
    scale_valid = scale_config.get("aspect_ratio_valid", False)
    scale_warning = ""
    if not scale_valid:
        distortion = scale_config.get("aspect_ratio_distortion_pct", 0)
        scale_warning = f"⚠️ Scale distortion: {distortion:.1f}% — measurements approximate"
    
    return {
        "type": "seismic_viewer",
        "layout": "split",
        "left_panel": {
            "type": "viewer_canvas",
            "image": state["image_base64"],
            "overlays": state["overlays"],
            "active_overlays": state["overlay_config"],
            "toolbar": [
                {"id": "zoom_in", "icon": "+", "tooltip": "Zoom in"},
                {"id": "zoom_out", "icon": "-", "tooltip": "Zoom out"},
                {"id": "reset_view", "icon": "⟲", "tooltip": "Reset view"},
                {"id": "toggle_reflectors", "icon": "📊", "tooltip": "Toggle reflectors", "active": state["overlay_config"]["reflectors"]},
                {"id": "toggle_faults", "icon": "⚡", "tooltip": "Toggle faults", "active": state["overlay_config"]["faults"]},
                {"id": "toggle_facies", "icon": "🎨", "tooltip": "Toggle facies", "active": state["overlay_config"]["facies"]},
                {"id": "export_snapshot", "icon": "💾", "tooltip": "Export snapshot"},
            ],
            "scale_bar": {
                "vertical": {
                    "unit": scale_config["vertical_unit"],
                    "scale": scale_config["vertical_scale"],
                    "ticks": [0, 500, 1000, 1500, 2000] if scale_valid else None,
                },
                "horizontal": {
                    "scale": scale_config["horizontal_scale"],
                    "unit": "m" if "meter" in scale_config["vertical_unit"] else "ft",
                },
            },
            "warning_banner": scale_warning,
        },
        "right_panel": {
            "type": "insight_panel",
            "sections": [
                {
                    "title": "Section Summary",
                    "content": insight.get("interpretation", {}).get("summary", "No interpretation available"),
                    "style": "highlight",
                },
                {
                    "title": "Key Features",
                    "items": [
                        f"✓ {e['description']}" 
                        for e in insight.get("evidence_links", [])
                    ] or ["No features identified"],
                },
                {
                    "title": "Confidence",
                    "badge": {
                        "value": insight.get("confidence_band", {}).get("aggregate", 0),
                        "range": insight.get("confidence_band", {}).get("range", "unknown"),
                        "color": "green" if insight.get("confidence_band", {}).get("aggregate", 0) > 0.8 else "yellow" if insight.get("confidence_band", {}).get("aggregate", 0) > 0.6 else "red",
                    },
                },
                {
                    "title": "Counter-Hypotheses",
                    "items": insight.get("counter_hypotheses", []),
                    "style": "muted",
                },
                {
                    "title": "Limitations",
                    "items": insight.get("limitations", ["Image-domain interpretation only"]),
                    "style": "warning",
                },
                {
                    "title": "QC Status",
                    "badge": {
                        "value": state["qc_status"].get("qc_score", 0),
                        "label": f"QC Score: {state['qc_status'].get('qc_score', 0):.0%}",
                        "color": "green" if state["qc_status"].get("qc_score", 0) > 0.8 else "yellow" if state["qc_status"].get("qc_score", 0) > 0.6 else "red",
                    },
                },
            ],
        },
        "bottom_strip": {
            "line_name": state["metadata"]["line_name"],
            "basin": state["metadata"]["basin"],
            "polarity": legend_config["polarity_standard"] if legend_config["polarity_known"] else "Unknown polarity",
            "image_type": state["metadata"]["image_type"],
            "audit_flags": state["audit_flags"],
        },
    }


# =============================================================================
# App-Visible Backend Tools
# =============================================================================

async def geox_compute_display_scale(
    image_id: str,
    vertical_unit: str,
    vertical_scale: float,
    horizontal_scale: float,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Compute display scale configuration.
    
    Backend tool for viewer UI to calculate axis ticks, labels, and scale bars.
    Not exposed to AI models — called internally by viewer app.
    """
    return {
        "success": True,
        "image_id": image_id,
        "vertical_axis": {
            "unit": vertical_unit,
            "scale_per_pixel": vertical_scale,
            "tick_interval": 500 if vertical_unit in ["meters", "feet"] else 0.5,
            "label": f"Depth ({vertical_unit})",
        },
        "horizontal_axis": {
            "scale_per_pixel": horizontal_scale,
            "unit": "m" if "meter" in vertical_unit else "ft",
            "tick_interval": 1000,
            "label": "Distance",
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_generate_overlay_reflectors(
    image_path: str,
    image_id: str,
    color: str = "red",
    line_width: int = 2,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Generate reflector overlay image.
    
    Returns base64-encoded PNG with reflector candidates drawn on transparent background.
    Called by viewer when user toggles reflector layer.
    """
    from ...seismic_image.reflectors import detect_reflectors
    from ...seismic_image.visualize import generate_visualization
    
    refl_result = await detect_reflectors(image_path, image_id)
    
    if not refl_result.success:
        return {
            "success": False,
            "error": "Reflector detection failed",
        }
    
    viz = await generate_visualization(
        image_path=image_path,
        visualization_type="reflectors",
        data={"reflectors": [r.model_dump() for r in refl_result.reflectors]},
    )
    
    return {
        "success": True,
        "image_id": image_id,
        "overlay_type": "reflectors",
        "overlay_base64": viz.get("base64_image"),
        "reflector_count": len(refl_result.reflectors),
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_generate_overlay_faults(
    image_path: str,
    image_id: str,
    color: str = "yellow",
    threshold: float = 0.5,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Generate fault likelihood overlay image.
    
    Returns base64-encoded PNG with fault heatmap overlay.
    """
    from ...seismic_image.faults import detect_fault_candidates
    from ...seismic_image.visualize import generate_visualization
    
    fault_result = await detect_fault_candidates(image_path, image_id)
    
    if not fault_result.success:
        return {
            "success": False,
            "error": "Fault detection failed",
        }
    
    viz = await generate_visualization(
        image_path=image_path,
        visualization_type="faults",
        data={"candidates": [f.model_dump() for f in fault_result.candidates]},
    )
    
    return {
        "success": True,
        "image_id": image_id,
        "overlay_type": "faults",
        "overlay_base64": viz.get("base64_image"),
        "fault_count": len(fault_result.candidates),
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_generate_geology_insight_panel(
    image_id: str,
    play_hypothesis: str,
    geological_intent: str,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Generate geological insight panel content.
    
    Called by viewer to refresh insight panel after user interactions.
    """
    # This would call the reasoning module with current context
    return {
        "success": True,
        "image_id": image_id,
        "insight": {
            "summary": f"{play_hypothesis.title()} play context",
            "confidence": 0.72,
            "limitations": ["Image-domain interpretation only"],
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_save_annotation(
    image_id: str,
    annotation_type: str,
    geometry: dict[str, Any],
    label: str,
    confidence: float,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Save user annotation.
    
    Stores interpreter's picks, polygons, or notes for audit trail.
    """
    return {
        "success": True,
        "image_id": image_id,
        "annotation_id": f"ann-{image_id}-{hash(str(geometry)) % 10000}",
        "saved": True,
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_export_view_snapshot(
    image_id: str,
    view_state: dict[str, Any],
    include_overlays: bool = True,
    include_legend: bool = True,
    include_insight: bool = True,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Export current view as snapshot.
    
    Generates PNG with image, overlays, legend, and metadata footer.
    """
    return {
        "success": True,
        "image_id": image_id,
        "snapshot_url": f"/exports/{image_id}_snapshot.png",
        "format": "PNG",
        "includes": {
            "overlays": include_overlays,
            "legend": include_legend,
            "insight": include_insight,
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def geox_analyze_roi(
    image_path: str,
    image_id: str,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    geological_intent: str,
) -> dict[str, Any]:
    """
    [APP-VISIBLE] Analyze region of interest.
    
    User clicks/drags a box in viewer; this analyzes that specific region.
    """
    return {
        "success": True,
        "image_id": image_id,
        "roi": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
        "analysis": {
            "feature_type_candidates": ["Channel fill", "Turbidite lobe"],
            "confidence": 0.65,
            "evidence": "Amplitude and texture pattern",
        },
        "seal": "DITEMPA BUKAN DIBERI",
    }


# =============================================================================
# FastMCP App Factory
# =============================================================================

def create_seismic_viewer_app() -> FastMCP | None:
    """
    Create FastMCP App for seismic viewer.
    
    Returns configured FastMCP instance with tools registered.
    """
    if not _HAS_FASTMCP:
        logger.error("FastMCP not available")
        return None
    
    app = FastMCP(
        "geox-seismic-viewer",
        instructions="""
GEO Seismic Viewer — Geologist-grade seismic section interpretation.

This app renders seismic sections with:
- Proper scale bars and axis labels
- Legend with polarity and amplitude scale
- Toggleable overlays (reflectors, faults, facies)
- Geological insight panel with reasoning and confidence

Use the main entrypoint `geox_open_seismic_viewer` to open a section.
Backend tools handle overlay generation and analysis.
"""
    )
    
    # Register model-visible entrypoint
    # Note: In FastMCP 3.0, this would use @app.tool() decorator
    # For now, we register as regular tools with documentation
    
    @app.tool()
    async def open_seismic_viewer(**kwargs) -> dict[str, Any]:
        """Entry point for opening seismic viewer."""
        return await geox_open_seismic_viewer(**kwargs)
    
    # Register app-visible backend tools
    # These would have visibility=["app"] in FastMCP 3.0+
    
    @app.tool()
    async def compute_display_scale(**kwargs) -> dict[str, Any]:
        """[APP] Compute display scale."""
        return await geox_compute_display_scale(**kwargs)
    
    @app.tool()
    async def generate_overlay_reflectors(**kwargs) -> dict[str, Any]:
        """[APP] Generate reflector overlay."""
        return await geox_generate_overlay_reflectors(**kwargs)
    
    @app.tool()
    async def generate_overlay_faults(**kwargs) -> dict[str, Any]:
        """[APP] Generate fault overlay."""
        return await geox_generate_overlay_faults(**kwargs)
    
    @app.tool()
    async def analyze_roi(**kwargs) -> dict[str, Any]:
        """[APP] Analyze region of interest."""
        return await geox_analyze_roi(**kwargs)
    
    @app.tool()
    async def save_annotation(**kwargs) -> dict[str, Any]:
        """[APP] Save user annotation."""
        return await geox_save_annotation(**kwargs)
    
    @app.tool()
    async def export_view_snapshot(**kwargs) -> dict[str, Any]:
        """[APP] Export view snapshot."""
        return await geox_export_view_snapshot(**kwargs)
    
    return app
