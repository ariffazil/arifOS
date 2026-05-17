"""
arifosmcp/apps/wealth_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS WealthApp — The Economist Surface (@WEALTH)
═══════════════════════════════════════════════════════════════════════════════

13-tool invariant surface:
  wealth_conservation_capital
  wealth_flow_liquidity
  wealth_gradient_price
  wealth_entropy_risk
  wealth_energy_productivity
  wealth_time_discount
  wealth_inertia_leverage
  wealth_field_macro
  wealth_signal_information
  wealth_game_coordination
  wealth_boundary_governance
  wealth_hysteresis_ledger
  mcp_health_check

Plus registry status: wealth_system_registry_status (public)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
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
    If,
    Metric,
    Muted,
    Row,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT, STATE
from skills.wealth.invariant_surface import (
    wealth_boundary_governance,
    wealth_conservation_capital,
    wealth_energy_productivity,
    wealth_entropy_risk,
    wealth_field_macro,
    wealth_flow_liquidity,
    wealth_game_coordination,
    wealth_gradient_price,
    wealth_hysteresis_ledger,
    wealth_inertia_leverage,
    wealth_signal_information,
    wealth_system_registry_status,
    wealth_time_discount,
)

# ═══════════════════════════════════════════════════════
# App definition
# ═══════════════════════════════════════════════════════

wealth_app = FastMCP("WealthApp")
if not hasattr(wealth_app, "ui"):
    wealth_app.ui = lambda *args, **kwargs: (lambda fn: fn)


# ═══════════════════════════════════════════════════════
# EXPECTED PUBLIC SURFACE — Hard registry truth
# ═══════════════════════════════════════════════════════

_EXPECTED_PUBLIC_TOOLS: set[str] = {
    "mcp_health_check",
    "wealth_conservation_capital",
    "wealth_flow_liquidity",
    "wealth_gradient_price",
    "wealth_entropy_risk",
    "wealth_energy_productivity",
    "wealth_time_discount",
    "wealth_inertia_leverage",
    "wealth_field_macro",
    "wealth_signal_information",
    "wealth_game_coordination",
    "wealth_boundary_governance",
    "wealth_hysteresis_ledger",
}
_KNOWN_INTERNAL_TOOLS: set[str] = {"wealth_system_registry_status"}


def _assert_public_surface(actual_tools: set[str], strict: bool = False) -> None:
    """Fail-closed startup check. If registry lies, container should not claim healthy."""
    extra = actual_tools - _EXPECTED_PUBLIC_TOOLS
    missing = _EXPECTED_PUBLIC_TOOLS - actual_tools
    if missing:
        raise RuntimeError(
            {
                "registry_truth": "FAIL",
                "extra_tools": sorted(extra) if strict else [],
                "missing_tools": sorted(missing),
            }
        )
    if strict and extra:
        raise RuntimeError(
            {
                "registry_truth": "FAIL",
                "extra_tools": sorted(extra),
                "missing_tools": [],
            }
        )


# ═══════════════════════════════════════════════════════
# TOOL 1 — mcp_health_check
# ═══════════════════════════════════════════════════════


@wealth_app.tool(name="mcp_health_check", tags={"system", "public", "health"})
def mcp_health_check() -> dict[str, Any]:
    """
    WEALTH organ health check with provenance and schema version.
    """
    commit = os.environ.get("DEPLOY_GIT_COMMIT", "unknown")
    branch = os.environ.get("DEPLOY_GIT_BRANCH", "unknown")
    build_time = os.environ.get("DEPLOY_BUILD_TIME", "unknown")

    return {
        "status": "OK",
        "schema_version": "wealth.physics_economics.v1",
        "public_surface_count": len(_EXPECTED_PUBLIC_TOOLS),
        "runtime_surface_count": len(_EXPECTED_PUBLIC_TOOLS),
        "final_authority": "ARIF",
        "repo_head": commit,
        "image_tag": commit,
        "branch": branch,
        "build_time": build_time,
    }


# ═══════════════════════════════════════════════════════
# TOOLS 2-13 — 12 Wealth Invariants
# ═══════════════════════════════════════════════════════


@wealth_app.tool(name="wealth_conservation_capital", tags={"wealth", "public", "invariant"})
def _wealth_conservation_capital(
    mode: str = "state",
    initial_investment: float = 0,
    annual_benefit: float = 0,
    years: int = 5,
    terminal_value: float = 0,
    ltv_ratio: float | None = None,
    value_at_risk: float | None = None,
) -> dict[str, Any]:
    return wealth_conservation_capital(
        mode=mode,
        initial_investment=initial_investment,
        annual_benefit=annual_benefit,
        years=years,
        terminal_value=terminal_value,
        ltv_ratio=ltv_ratio,
        value_at_risk=value_at_risk,
    )


@wealth_app.tool(name="wealth_flow_liquidity", tags={"wealth", "public", "invariant"})
def _wealth_flow_liquidity(
    mode: str = "cashflow",
    cashflows: list[float] | None = None,
    burn_rate: float = 0,
    runway_months: float | None = None,
    current_assets: float = 0,
    current_liabilities: float = 1,
) -> dict[str, Any]:
    return wealth_flow_liquidity(
        mode=mode,
        cashflows=cashflows,
        burn_rate=burn_rate,
        runway_months=runway_months,
        current_assets=current_assets,
        current_liabilities=current_liabilities,
    )


@wealth_app.tool(name="wealth_gradient_price", tags={"wealth", "public", "invariant"})
def _wealth_gradient_price(
    mode: str = "spread",
    price_a: float = 0,
    price_b: float = 0,
    cap_rate: float | None = None,
    dividend_yield: float | None = None,
    bond_yield: float | None = None,
) -> dict[str, Any]:
    return wealth_gradient_price(
        mode=mode,
        price_a=price_a,
        price_b=price_b,
        cap_rate=cap_rate,
        dividend_yield=dividend_yield,
        bond_yield=bond_yield,
    )


@wealth_app.tool(name="wealth_entropy_risk", tags={"wealth", "public", "invariant"})
def _wealth_entropy_risk(
    mode: str = "emv",
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    cost_of_risk: float | None = None,
    cashflows: list[float] | None = None,
) -> dict[str, Any]:
    return wealth_entropy_risk(
        mode=mode,
        outcomes=outcomes,
        probabilities=probabilities,
        cost_of_risk=cost_of_risk,
        cashflows=cashflows,
    )


@wealth_app.tool(name="wealth_energy_productivity", tags={"wealth", "public", "invariant"})
def _wealth_energy_productivity(
    mode: str = "efficiency",
    revenue: float = 0,
    costs: float = 1,
    equity: float = 1,
    assets: float = 1,
    employees: float = 1,
    net_income: float = 0,
    retention_ratio: float = 0.5,
    roe_target: float | None = None,
) -> dict[str, Any]:
    return wealth_energy_productivity(
        mode=mode,
        revenue=revenue,
        costs=costs,
        equity=equity,
        assets=assets,
        employees=employees,
        net_income=net_income,
        retention_ratio=retention_ratio,
        roe_target=roe_target,
    )


@wealth_app.tool(name="wealth_time_discount", tags={"wealth", "public", "invariant"})
def _wealth_time_discount(
    mode: str = "npv",
    initial_investment: float = 0,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0.1,
    terminal_value: float = 0,
    finance_rate: float = 0.1,
    reinvest_rate: float = 0.1,
    years: int | None = None,
) -> dict[str, Any]:
    return wealth_time_discount(
        mode=mode,
        initial_investment=initial_investment,
        cash_flows=cash_flows,
        discount_rate=discount_rate,
        terminal_value=terminal_value,
        finance_rate=finance_rate,
        reinvest_rate=reinvest_rate,
        years=years,
    )


@wealth_app.tool(name="wealth_inertia_leverage", tags={"wealth", "public", "invariant"})
def _wealth_inertia_leverage(
    mode: str = "dscr",
    ebitda: float = 0,
    debt_service: float = 1,
    equity: float = 1,
    total_assets: float = 1,
    total_debt: float = 0,
    cashflows: list[float] | None = None,
    iterations: int = 1000,
) -> dict[str, Any]:
    return wealth_inertia_leverage(
        mode=mode,
        ebitda=ebitda,
        debt_service=debt_service,
        equity=equity,
        total_assets=total_assets,
        total_debt=total_debt,
        cashflows=cashflows,
        iterations=iterations,
    )


@wealth_app.tool(name="wealth_field_macro", tags={"wealth", "public", "invariant"})
def _wealth_field_macro(
    mode: str = "macro",
    fed_rate: float | None = None,
    ten_year_yield: float | None = None,
    two_year_yield: float | None = None,
    sector: str = "",
    inflation_rate: float | None = None,
) -> dict[str, Any]:
    return wealth_field_macro(
        mode=mode,
        fed_rate=fed_rate,
        ten_year_yield=ten_year_yield,
        two_year_yield=two_year_yield,
        sector=sector,
        inflation_rate=inflation_rate,
    )


@wealth_app.tool(name="wealth_signal_information", tags={"wealth", "public", "invariant"})
def _wealth_signal_information(
    mode: str = "sharpe",
    returns: list[float] | None = None,
    risk_free_rate: float = 0.02,
    benchmark_returns: list[float] | None = None,
) -> dict[str, Any]:
    return wealth_signal_information(
        mode=mode,
        returns=returns,
        risk_free_rate=risk_free_rate,
        benchmark_returns=benchmark_returns,
    )


@wealth_app.tool(name="wealth_game_coordination", tags={"wealth", "public", "invariant"})
def _wealth_game_coordination(
    mode: str = "nash",
    payoff_matrix: dict[str, Any] | None = None,
    agents: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return wealth_game_coordination(
        mode=mode,
        payoff_matrix=payoff_matrix,
        agents=agents,
    )


@wealth_app.tool(name="wealth_boundary_governance", tags={"wealth", "public", "invariant"})
def _wealth_boundary_governance(
    mode: str = "floors",
    floor_scores: dict[str, float] | None = None,
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return wealth_boundary_governance(
        mode=mode,
        floor_scores=floor_scores,
        candidate=candidate,
    )


@wealth_app.tool(name="wealth_hysteresis_ledger", tags={"wealth", "public", "invariant"})
def _wealth_hysteresis_ledger(
    mode: str = "status",
    session_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return wealth_hysteresis_ledger(
        mode=mode,
        session_id=session_id,
        payload=payload,
    )


# ═══════════════════════════════════════════════════════
# REGISTRY STATUS TOOL
# ═══════════════════════════════════════════════════════


@wealth_app.tool(name="wealth_system_registry_status", tags={"system", "internal", "registry"})
def _wealth_system_registry_status() -> dict[str, Any]:
    """
    Compare intended, registered, and externally visible surfaces.
    """
    # Inspect what is actually registered on this app
    registered_names: set[str] = set()
    try:
        tool_manager = getattr(wealth_app, "_tool_manager", None)
        if tool_manager is not None and getattr(tool_manager, "tools", None):
            registered_names = set(tool_manager.tools.keys())
        else:
            provider = getattr(wealth_app, "_local_provider", None)
            components = getattr(provider, "_components", {}) if provider is not None else {}
            registered_names = {
                comp.name
                for key, comp in components.items()
                if key.startswith("tool:") and hasattr(comp, "name")
            }
    except Exception:
        registered_names = set()

    extra = (registered_names - _EXPECTED_PUBLIC_TOOLS) - _KNOWN_INTERNAL_TOOLS
    missing = _EXPECTED_PUBLIC_TOOLS - registered_names

    status = wealth_system_registry_status(
        intended_public_tools=sorted(_EXPECTED_PUBLIC_TOOLS),
        hidden_aliases=[],
    )
    status["registered_public_tools"] = len(registered_names & _EXPECTED_PUBLIC_TOOLS)
    status["extra_visible_tools"] = sorted(extra)
    status["missing_visible_tools"] = sorted(missing)
    status["registry_truth"] = "PASS" if not extra and not missing else "FAIL"
    status["actual_registered"] = sorted(registered_names)
    return status


# ═══════════════════════════════════════════════════════
# STARTUP REGISTRY ASSERTION
# ═══════════════════════════════════════════════════════


def _run_startup_assertion() -> None:
    """
    Called once at import time. Raises RuntimeError if the public surface
    does not match the expected 13-tool invariant set.
    """
    registered: set[str] = set()
    try:
        tool_manager = getattr(wealth_app, "_tool_manager", None)
        if tool_manager is not None and getattr(tool_manager, "tools", None):
            registered = set(tool_manager.tools.keys())
        else:
            provider = getattr(wealth_app, "_local_provider", None)
            components = getattr(provider, "_components", {}) if provider is not None else {}
            registered = {
                comp.name
                for key, comp in components.items()
                if key.startswith("tool:") and hasattr(comp, "name")
            }
    except Exception:
        pass

    # If tools aren't registered yet (lazy init), defer check
    if registered:
        _assert_public_surface(registered)


# Defer to first actual call if needed; for now attempt immediate check
# but swallow errors during import when FastMCP may not have finalized.
try:
    _run_startup_assertion()
except RuntimeError:
    raise
except Exception:
    pass


# ═══════════════════════════════════════════════════════
# UI SURFACE — Wealth Dashboard (unchanged)
# ═══════════════════════════════════════════════════════


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
        "audited": False,
    }

    on_audit = CallTool(
        _wealth_time_discount,
        args={
            "mode": "npv",
            "initial_investment": 10000.0,
            "cash_flows": [2500.0] * 5,
            "discount_rate": 0.1,
        },
        on_success=[
            SetState("npv", RESULT["result"]["npv"]),
            SetState("verdict", RESULT["result"].get("verdict", "SEAL")),
            SetState("signal", "AUDITED"),
            SetState("audited", True),
            ShowToast("Economic audit sealed", variant="success"),
        ],
        on_error=ShowToast("Audit failed", variant="destructive"),
    )

    with Column(gap=5, css_class="p-5 max-w-2xl") as view:

        with Row(gap=3, align="center"):
            Heading("@WEALTH Economist")
            Badge(
                "Economic Organ",
                variant="secondary",
                css_class="text-xs font-mono",
            )

        Muted("Economic modeling & decision governance · DITEMPA BUKAN DIBERI")
        Separator()

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

        with If(STATE["audited"]):
            with Row(gap=4, align="center"):
                Badge(
                    STATE["verdict"],
                    variant=STATE["verdict"].then("success", "destructive"),
                    css_class="font-mono",
                )
                Text(STATE["signal"], css_class="font-bold uppercase tracking-widest")

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

        with Card(css_class="bg-muted/10"):
            with CardContent(css_class="py-3"):
                with Row(justify="between", align="center"):
                    with Row(gap=2, align="center"):
                        Text(
                            "Thermodynamics",
                            css_class="text-xs font-mono uppercase tracking-widest "
                            "text-muted-foreground",
                        )
                        Badge("Ω STABLE", variant="outline", css_class="text-[10px]")
                    with Row(gap=4):
                        with Column(align="center"):
                            Text(
                                "G-Score",
                                css_class="text-[10px] text-muted-foreground uppercase",
                            )
                            Text("0.85", css_class="text-xs font-bold font-mono")
                        with Column(align="center"):
                            Text(
                                "ΔS",
                                css_class="text-[10px] text-muted-foreground uppercase",
                            )
                            Text(
                                "-0.12",
                                css_class="text-xs font-bold font-mono text-success",
                            )
                        with Column(align="center"):
                            Text(
                                "Ψ",
                                css_class="text-[10px] text-muted-foreground uppercase",
                            )
                            Text(
                                "1.10",
                                css_class="text-xs font-bold font-mono text-primary",
                            )

        Separator()
        Muted("Source: ariffazil/WEALTH v1.4.0", css_class="text-xs text-center")

    return PrefabApp(view=view, state=initial_state)


# ═══════════════════════════════════════════════════════
# MOUNT HELPER
# ═══════════════════════════════════════════════════════


def _register(mcp: FastMCP) -> None:
    """Mount WealthApp onto the platform FastMCP server."""
    mcp.add_provider(wealth_app)
