"""
arifosmcp/apps/geox_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS GeoxApp — The Earth Witness Surface (@GEOX)
═══════════════════════════════════════════════════════════════════════════════

Implements the geospatial/subsurface organ interface as a FastMCPApp:

  @app.ui()   geox_map_surface  — entry; renders geospatial verify card + 3D Earth link
  @app.tool() verify_location    — backend; calls core.organs.geox

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations
from typing import Any
from fastmcp import FastMCP
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Button,
    Card,
    CardContent,
    Column,
    Grid,
    Heading,
    Metric,
    Muted,
    Row,
    Separator,
    Text,
    Alert,
    If,
    Link
)
from prefab_ui.rx import RESULT, STATE

# ── App definition ────────────────────────────────────────────────────────────

geox_app = FastMCP("GeoxApp")

@geox_app.tool()
async def verify_location(lat: float, lon: float) -> dict[str, Any]:
    """
    Verify a geospatial location against the constitutional Earth Witness.
    """
    try:
        from core.organs import verify_geospatial
        res = verify_geospatial(lat, lon)
        return {
            "success": True,
            "lat": res["lat"],
            "lon": res["lon"],
            "valid": res["valid"],
            "jurisdiction": res["jurisdiction"],
            "crs": res["crs"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@geox_app.ui(title="@GEOX Earth Witness")
def geox_map_surface() -> PrefabApp:
    """
    Open the arifOS Geospatial Verification Surface.
    F4 Clarity: Ensuring all data is anchored in real-world coordinates.
    """
    initial_state: dict[str, Any] = {
        "lat": 0.0,
        "lon": 0.0,
        "valid": False,
        "jurisdiction": "Unknown",
        "crs": "WGS84",
        "verified": False
    }

    on_verify = CallTool(
        verify_location,
        args={"lat": 3.139, "lon": 101.686}, # Kuala Lumpur default
        on_success=[
            SetState("lat",          RESULT["lat"]),
            SetState("lon",          RESULT["lon"]),
            SetState("valid",        RESULT["valid"]),
            SetState("jurisdiction", RESULT["jurisdiction"]),
            SetState("crs",          RESULT["crs"]),
            SetState("verified",     True),
            ShowToast("Location verified by Earth Witness", variant="success"),
        ],
        on_error=ShowToast("Verification failed", variant="destructive"),
    )

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("@GEOX Earth Witness")
            Badge(
                "Subsurface Organ",
                variant="secondary",
                css_class="text-xs font-mono",
            )

        Muted("Geospatial grounding & physical verification · DITEMPA BUKAN DIBERI")
        Separator()

        # ── Verification Card ───────────────────────────────────────────────
        with Card():
            with CardContent(css_class="py-4"):
                with Row(gap=4, align="center"):
                    with Column(gap=1):
                        Text("Verify Coordinate", css_class="font-semibold")
                        Muted("Ensure interpreted prospects are physically grounded")
                    
                    Button(
                        "Verify (Kuala Lumpur)",
                        on_click=on_verify,
                        variant="default"
                    )

        # ── Results ─────────────────────────────────────────────────────────
        with If(STATE["verified"]):
            with Grid(columns=2, gap=4):
                with Card():
                    with CardContent(css_class="py-3"):
                        Metric(label="Latitude", value=STATE["lat"])
                with Card():
                    with CardContent(css_class="py-3"):
                        Metric(label="Longitude", value=STATE["lon"])

            with Card(css_class="mt-4"):
                with CardContent(css_class="py-3"):
                    with Row(gap=2, align="center"):
                        Badge(
                            STATE["valid"].then("VALID", "INVALID"),
                            variant=STATE["valid"].then("success", "destructive")
                        )
                        Text(STATE["jurisdiction"])
                    Muted(f"Coordinate Reference System: {STATE['crs']}", css_class="text-xs mt-2")

        Separator()

        # ── External Links ──────────────────────────────────────────────────
        Muted("Reality Substrates", css_class="text-xs uppercase tracking-wider")
        with Row(gap=3):
            Link("3D Earth (Cesium)", href="https://cesium.com", css_class="text-sm text-blue-500")
            Link("Macrostrat Geology", href="https://macrostrat.org", css_class="text-sm text-blue-500")

        Separator()
        Muted("arifOS · @GEOX · Earth Witness Protocol", css_class="text-xs text-center")

    return PrefabApp(view=view, state=initial_state)

def _register(mcp: FastMCP) -> None:
    """Mount GeoxApp onto the platform FastMCP server."""
    mcp.add_provider(geox_app)
