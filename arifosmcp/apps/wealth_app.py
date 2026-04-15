"""
arifosmcp/apps/wealth_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS WealthApp — The Economist Surface (@WEALTH)
═══════════════════════════════════════════════════════════════════════════════

Implements the economic organ interface as a FastMCPApp:

  @app.ui()   wealth_dashboard_surface  — entry; renders economic metrics + analysis tool
  @app.tool() perform_economic_audit    — backend; calls core.organs.wealth

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
    If
)
from prefab_ui.rx import RESULT, STATE

# ── App definition ────────────────────────────────────────────────────────────

wealth_app = FastMCP("WealthApp", domain="arifos.fastmcp.app")

@wealth_app.tool()
async def perform_economic_audit(
    initial_cost: float,
    annual_benefit: float,
    years: int
) -> dict[str, Any]:
    """
    Perform a constitutional economic audit.
    """
    try:
        from core.organs import analyze_cost_benefit
        res = analyze_cost_benefit(
            initial_cost=initial_cost,
            annual_benefit=annual_benefit,
            years=years
        )
        return {
            "success": True,
            "npv": res.npv,
            "roi": res.roi,
            "verdict": res.verdict,
            "recommendation": res.recommendation,
            "floors": res.floor_alignment
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@wealth_app.ui(title="@WEALTH Optimizer")
def wealth_dashboard_surface() -> PrefabApp:
    """
    Open the arifOS Economic Dashboard.
    F4 Clarity: Visualizing resource metabolism and decision ROI.
    """
    initial_state: dict[str, Any] = {
        "npv": 0.0,
        "roi": 0.0,
        "verdict": "PENDING",
        "recommendation": "Awaiting audit input",
        "floors": {},
        "audited": False
    }

    on_audit = CallTool(
        perform_economic_audit,
        args={
            "initial_cost": 1000.0,
            "annual_benefit": 250.0,
            "years": 5
        },
        on_success=[
            SetState("npv",             RESULT["npv"]),
            SetState("roi",             RESULT["roi"]),
            SetState("verdict",         RESULT["verdict"]),
            SetState("recommendation",  RESULT["recommendation"]),
            SetState("floors",          RESULT["floors"]),
            SetState("audited",         True),
            ShowToast("Economic audit sealed", variant="success"),
        ],
        on_error=ShowToast("Audit failed", variant="destructive"),
    )

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("@WEALTH Economist")
            Badge(
                "Economic Organ",
                variant="secondary",
                css_class="text-xs font-mono",
            )

        Muted("Economic modeling & decision governance · DITEMPA BUKAN DIBERI")
        Separator()

        # ── Metrics ─────────────────────────────────────────────────────────
        with Grid(columns=3, gap=3):
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Metric(label="NPV", value=STATE["npv"])
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Metric(label="ROI %", value=STATE["roi"])
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Badge(
                        STATE["verdict"],
                        variant=STATE["verdict"].then("success", "destructive"),
                        css_class="mt-4"
                    )

        Separator()

        # ── Recommendation ──────────────────────────────────────────────────
        with If(STATE["audited"]):
            Alert(
                title=STATE["verdict"].then("Investment Recommended", "Investment Warning"),
                description=STATE["recommendation"],
                variant=STATE["verdict"].then("default", "warning"),
            )
        
        # ── Audit Controls ──────────────────────────────────────────────────
        with Card():
            with CardContent(css_class="py-4"):
                Text("Simulate Investment (Demo Defaults)", css_class="font-semibold mb-2")
                Muted("Initial: $1000 | Benefit: $250 | 5 Years", css_class="mb-4")
                Button(
                    "Perform Economic Audit",
                    on_click=on_audit,
                    variant="default",
                    css_class="w-full",
                )

        Separator()

        # ── Floors ──────────────────────────────────────────────────────────
        Muted("Constitutional Alignment", css_class="text-xs uppercase tracking-wider")
        with Card(css_class="bg-muted/30"):
            with CardContent(css_class="py-3"):
                with Grid(columns=2, gap=2):
                    # In a real app, I would iterate over STATE["floors"]
                    # For now, let's show placeholders until audited
                    with Row(gap=2, align="center"):
                        Badge("F1", variant="outline")
                        Text("Amanah (Stewardship)")
                    with Row(gap=2, align="center"):
                        Badge("F2", variant="outline")
                        Text("Truth (Thermodynamics)")

    return PrefabApp(view=view, state=initial_state)

def _register(mcp: FastMCP) -> None:
    """Mount WealthApp onto the platform FastMCP server."""
    mcp.add_provider(wealth_app)
