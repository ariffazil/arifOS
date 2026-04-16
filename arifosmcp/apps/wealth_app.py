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

wealth_app = FastMCP("WealthApp")

@wealth_app.tool()
async def perform_economic_audit(
    initial_cost: float,
    annual_benefit: float,
    years: int,
    ebitda: float = 120000.0,
    debt_service: float = 100000.0
) -> dict[str, Any]:
    """
    Perform a constitutional economic audit.
    """
    try:
        from core.organs import wealth
        flows = [annual_benefit] * years
        
        npv_res = wealth(operation="npv_reward", initial_investment=initial_cost, cash_flows=flows)
        irr_res = wealth(operation="irr_yield", initial_investment=initial_cost, cash_flows=flows)
        dscr_res = wealth(operation="dscr_leverage", ebitda=ebitda, debt_service=debt_service)

        return {
            "success": True,
            "npv": npv_res.primary_result["npv"],
            "irr": irr_res.primary_result["irr"],
            "dscr": dscr_res.primary_result["dscr"],
            "verdict": npv_res.verdict,
            "signal": npv_res.allocation_signal,
            "audited": True
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
        "irr": 0.0,
        "dscr": 0.0,
        "verdict": "PENDING",
        "signal": "INSUFFICIENT",
        "audited": False
    }

    on_audit = CallTool(
        perform_economic_audit,
        args={
            "initial_cost": 10000.0,
            "annual_benefit": 2500.0,
            "years": 5,
            "ebitda": 150000.0,
            "debt_service": 100000.0
        },
        on_success=[
            SetState("npv",             RESULT["npv"]),
            SetState("irr",             RESULT["irr"]),
            SetState("dscr",            RESULT["dscr"]),
            SetState("verdict",         RESULT["verdict"]),
            SetState("signal",          RESULT["signal"]),
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
                    Metric(label="IRR", value=STATE["irr"])
            with Card():
                with CardContent(css_class="py-3 text-center"):
                    Metric(label="DSCR", value=STATE["dscr"])

        Separator()

        # ── Signal & Verdict ────────────────────────────────────────────────
        with If(STATE["audited"]):
            with Row(gap=4, align="center"):
                Badge(
                    STATE["verdict"],
                    variant=STATE["verdict"].then("success", "destructive"),
                    css_class="font-mono"
                )
                Text(STATE["signal"], css_class="font-bold uppercase tracking-widest")
        
        # ── Audit Controls ──────────────────────────────────────────────────
        with Card():
            with CardContent(css_class="py-4"):
                Text("Simulate Project (Demo)", css_class="font-semibold mb-2")
                Muted("Asset: Production Line | Value: $10,000", css_class="text-xs mb-4")
                Button(
                    "Calculate Dimension Scores",
                    on_click=on_audit,
                    variant="default",
                    css_class="w-full",
                )

        Separator()
        Muted("Source: ariffazil/WEALTH v1.4.0", css_class="text-xs text-center")

    return PrefabApp(view=view, state=initial_state)

    return PrefabApp(view=view, state=initial_state)

def _register(mcp: FastMCP) -> None:
    """Mount WealthApp onto the platform FastMCP server."""
    mcp.add_provider(wealth_app)
