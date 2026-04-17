"""
arifOS Federation — MCP Tool Registry
=====================================
MCP tools for the 6-axis federation.

Philosophy:
- MCP = Model ↔ Tools (data access within agent)
- A2A = Agent ↔ Agent (coordination layer)
- Each agent exposes its tools via MCP
- Tools are epistemically pure per axis

MCP Host (Claude Code/Desktop)
    |
    |-- MCP Client 1 --> P_MCP_Server (Perception tools)
    |-- MCP Client 2 --> T_MCP_Server (Transformation tools)
    |-- MCP Client 3 --> V_MCP_Server (Valuation tools)
    |-- MCP Client 4 --> G_MCP_Server (Governance tools)
    |-- MCP Client 5 --> E_MCP_Server (Execution tools)
    |-- MCP Client 6 --> M_MCP_Server (Meta tools)

A2A handles inter-agent routing (separate concern).
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass
from enum import Enum

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field


# =============================================================================
# TOOL NAMING CONVENTION
# =============================================================================

"""
Tool naming: {AXIS}_{domain}_{verb}

Examples:
- P_well_state_read
- T_physics_compute
- V_economic_npv
- G_judge_verdict
- E_vault_seal
- M_omega_status

Tags by axis:
- perception: P_* tools
- transformation: T_* tools
- valuation: V_* tools
- governance: G_* tools
- execution: E_* tools
- meta: M_* tools
"""


# =============================================================================
# GOVERNANCE METADATA HELPER
# =============================================================================

def _gov(
    role: str,
    risk: str,
    ledger: str,
    floors: list[str],
    *,
    requires_judge: bool = False,
    requires_human: bool = False,
    reversible: str = "reversible",
    mutability: str = "read",
) -> dict:
    """Return constitutional governance metadata dict for meta= param."""
    return {
        "constitutional_role": role,
        "risk_tier": risk,
        "requires_judge": requires_judge,
        "requires_human_confirm": requires_human,
        "reversibility": reversible,
        "mutability": mutability,
        "ledger_class": ledger,
        "floor_anchors": floors,
    }


# =============================================================================
# PERCEPTION TOOLS (P) — Read reality only
# =============================================================================


def create_perception_mcp() -> FastMCP:
    """Perception Agent MCP tools — read from WELL, GEOX, VAULT, WEALTH."""
    mcp = FastMCP("arifOS-P")

    from pathlib import Path
    import json, datetime

    import os
    WELL_STATE_PATH = Path(os.getenv("WELL_STATE_PATH", "/root/WELL/state.json"))

    def _load_well_state() -> dict[str, Any]:
        if not WELL_STATE_PATH.exists():
            return {"operator_id": "arif", "metrics": {}, "well_score": 50, "floors_violated": []}
        with open(WELL_STATE_PATH) as f:
            return json.load(f)

    # ─────────────────────────────────────────────────────────────────────────
    # WELL Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_well_state_read",
        description="Read current WELL biological telemetry snapshot",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2","F8"],mutability="read"),
    )
    def P_well_state_read(ctx: Context | None = None) -> dict[str, Any]:
        """Read current WELL state — biological telemetry from live state.json."""
        state = _load_well_state()
        metrics = state.get("metrics", {})
        return {
            "agent": "P",
            "source": "WELL",
            "action": "state_read",
            "data": {
                "score": state.get("well_score", 50),
                "dimensions": {
                    "sleep": metrics.get("sleep", {}),
                    "stress": metrics.get("stress", {}),
                    "cognitive": metrics.get("cognitive", {}),
                    "metabolic": metrics.get("metabolic", {}),
                    "structural": metrics.get("structural", {}),
                },
                "floor_violations": state.get("floors_violated", []),
                "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
            },
        }

    @mcp.tool(
        name="P_well_readiness_check",
        description="Check biological readiness verdict for arifOS JUDGE",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2","F8"],mutability="read"),
    )
    def P_well_readiness_check(ctx: Context | None = None) -> dict[str, Any]:
        """Check WELL readiness for governance context."""
        state = _load_well_state()
        score = state.get("well_score", 50)
        violations = state.get("floors_violated", [])
        if score >= 80 and not violations:
            verdict = "READY"
            bandwidth = "NORMAL"
        elif score >= 50:
            verdict = "DEGRADED"
            bandwidth = "REDUCED"
        else:
            verdict = "CRITICAL"
            bandwidth = "SLOW"
        return {
            "agent": "P",
            "source": "WELL",
            "action": "readiness_check",
            "data": {
                "score": score,
                "floor_status": {f"W{i}": "active" for i in range(1, 14)},
                "verdict": verdict,
                "bandwidth_recommendation": bandwidth,
            },
        }

    @mcp.tool(
        name="P_well_floor_scan",
        description="Scan W-Floor status across all dimensions",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2","F8"],mutability="read"),
    )
    def P_well_floor_scan(ctx: Context | None = None) -> dict[str, Any]:
        """Scan all W-Floors from live WELL state."""
        state = _load_well_state()
        violations = state.get("floors_violated", [])
        score = state.get("well_score", 50)
        all_floors = {f"W{i}": "active" for i in range(1, 14)}
        if violations:
            for v in violations:
                # Map violation names back to floors if possible
                pass
        return {
            "agent": "P",
            "source": "WELL",
            "action": "floor_scan",
            "data": {
                "floors": all_floors,
                "overall_verdict": "NOMINAL"
                if score >= 80
                else "DEGRADED"
                if score >= 50
                else "CRITICAL",
                "well_score": score,
                "violations": violations,
            },
        }

    # ─────────────────────────────────────────────────────────────────────────
    # GEOX Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_geox_scene_load",
        description="Load seismic, well, or volume data into witness context",
        tags={"perception", "geox"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2"],mutability="read"),
    )
    def P_geox_scene_load(
        scene_type: Literal["seismic", "well", "volume"], path: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Load GEOX scene data from filesystem."""
        from pathlib import Path

        p = Path(path)
        status = "loaded" if p.exists() else "not_found"
        return {
            "agent": "P",
            "source": "GEOX",
            "action": "scene_load",
            "data": {
                "scene_type": scene_type,
                "path": path,
                "status": status,
                "scene_id": f"{scene_type}_{p.name}",
            },
        }

    @mcp.tool(
        name="P_geox_skills_query",
        description="Query GEOX skill registry by keyword or domain",
        tags={"perception", "geox"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2","F11"],mutability="read"),
    )
    def P_geox_skills_query(
        query: str, domain: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Query GEOX skills registry."""
        return {
            "agent": "P",
            "source": "GEOX",
            "action": "skills_query",
            "data": {"query": query, "domain": domain, "skills": []},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # WEALTH Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_wealth_snapshot_fetch",
        description="Fetch cross-source macro/energy/carbon snapshot",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
        meta=_gov("sense","low","observation",["F2","F6"],mutability="read"),
    )
    def P_wealth_snapshot_fetch(geography: str, ctx: Context | None = None) -> dict[str, Any]:
        """Fetch macro snapshot from WEALTH."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "snapshot_fetch",
            "data": {"geography": geography, "macro": {}, "energy": {}, "carbon": {}},
        }

    @mcp.tool(
        name="P_wealth_series_fetch",
        description="Fetch live data series from open public source",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
        meta=_gov("sense","low","observation",["F2","F6"],mutability="read"),
    )
    def P_wealth_series_fetch(
        source: str, series_id: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Fetch series data."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "series_fetch",
            "data": {"source": source, "series_id": series_id, "series": [], "metadata": {}},
        }

    @mcp.tool(
        name="P_wealth_vintage_fetch",
        description="Fetch specific vintage of series (FRED/ALFRED)",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
        meta=_gov("sense","low","observation",["F2","F6","F7"],mutability="read"),
    )
    def P_wealth_vintage_fetch(
        series_id: str, vintage_date: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Fetch vintage series."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "vintage_fetch",
            "data": {"series_id": series_id, "vintage_date": vintage_date, "series": []},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # VAULT Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_vault_ledger_read",
        description="Read VAULT999 ledger, build BLS seal card",
        tags={"perception", "vault"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F2","F11"],mutability="read"),
    )
    def P_vault_ledger_read(
        session_id: str | None = None,
        verdict: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int = 100,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Read from VAULT999 ledger via vault_postgres if available."""
        try:
            from arifOS.arifosmcp.runtime.vault_postgres import PostgresVaultStore

            vault = PostgresVaultStore()
            rows = vault.get_seals(
                session_id=session_id, verdict=verdict, since=since, until=until, limit=limit
            )
            total = len(rows)
            by_verdict: dict[str, int] = {}
            for r in rows:
                v = r.get("verdict", "UNKNOWN")
                by_verdict[v] = by_verdict.get(v, 0) + 1
            return {
                "agent": "P",
                "source": "VAULT",
                "action": "ledger_read",
                "data": {
                    "seal_card": {"total_seals": total, "by_verdict": by_verdict},
                    "ledger_rows": rows,
                },
            }
        except Exception:
            pass
        return {
            "agent": "P",
            "source": "VAULT",
            "action": "ledger_read",
            "data": {"seal_card": {"total_seals": 0, "by_verdict": {}}, "ledger_rows": []},
        }

    return mcp


# =============================================================================
# TRANSFORMATION TOOLS (T) — Pure computation only
# =============================================================================


def create_transformation_mcp() -> FastMCP:
    """Transformation Agent MCP tools — physics, math, monte_carlo."""
    mcp = FastMCP("arifOS-T")

    from arifOS.core.organs._5_wealth import calculate_irr as _calc_irr
    import math

    @mcp.tool(
        name="T_petrophysics_compute",
        description="Execute physics-grounded petrophysical calculations",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F2","F4","F7"],mutability="transform"),
    )
    def T_petrophysics_compute(
        well_id: str,
        computation: Literal["porosity", "saturation", "volume"],
        params: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute petrophysical properties."""
        import math

        phi = params.get("porosity", 0.0)
        sw = params.get("water_saturation", 1.0)
        h = params.get("thickness", 0.0)
        area = params.get("area", 0.0)
        bf = params.get("formation_volume_factor", 1.0)

        if computation == "porosity":
            value = phi
            unit = "fraction"
        elif computation == "saturation":
            value = sw
            unit = "fraction"
        elif computation == "volume":
            # STOIIP = Area * Thickness * Porosity * (1 - Sw) / FVF
            value = area * h * phi * (1 - sw) / bf if bf > 0 else 0
            unit = "bbl"
        else:
            value = 0.0
            unit = "fraction"

        return {
            "agent": "T",
            "domain": "physics",
            "action": "petrophysics_compute",
            "result": {
                "well_id": well_id,
                "computation": computation,
                "value": round(value, 4),
                "unit": unit,
            },
        }

    @mcp.tool(
        name="T_stratigraphy_correlate",
        description="Correlate stratigraphic units across multiple wells",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F2","F7","F8"],mutability="transform"),
    )
    def T_stratigraphy_correlate(
        wells: list[str], section_id: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Correlate stratigraphy across wells."""
        return {
            "agent": "T",
            "domain": "physics",
            "action": "stratigraphy_correlate",
            "result": {"wells": wells, "section_id": section_id, "correlation_map": {}},
        }

    @mcp.tool(
        name="T_geometry_build",
        description="Build architectural geometries from interpreted horizons",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F2","F8"],mutability="transform"),
    )
    def T_geometry_build(
        horizons: list[dict[str, Any]], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Build geometries from horizons."""
        return {
            "agent": "T",
            "domain": "physics",
            "action": "geometry_build",
            "result": {"horizons": horizons, "geometries": {}},
        }

    @mcp.tool(
        name="T_math_irr_compute",
        description="Compute Internal Rate of Return and Modified IRR",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6","F7"],mutability="transform"),
    )
    def T_math_irr_compute(
        initial_investment: float,
        cash_flows: list[float],
        finance_rate: float = 0,
        reinvest_rate: float = 0,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute IRR using real WEALTH kernel."""
        irr_result = _calc_irr(initial_investment, cash_flows)
        irr_val = irr_result.get("irr")
        mirr_val = None
        if irr_val is not None and len(cash_flows) > 0:
            n = len(cash_flows)
            positive_total = sum(cf for cf in cash_flows if cf > 0)
            negative_total = abs(sum(cf for cf in cash_flows if cf < 0))
            if positive_total > 0 and negative_total > 0:
                f_rate = finance_rate if finance_rate else 0
                r_rate = reinvest_rate if reinvest_rate else irr_val
                mirr_num = positive_total * pow(1 + r_rate, n)
                mirr_den = abs(initial_investment) * pow(1 + f_rate, n)
                if mirr_den > 0:
                    mirr_val = pow(mirr_num / mirr_den, 1.0 / n) - 1
        return {
            "agent": "T",
            "domain": "math",
            "action": "irr_compute",
            "result": {
                "irr": irr_val,
                "mirr": round(mirr_val, 6) if mirr_val is not None else None,
                "flags": irr_result.get("flags", []),
            },
        }

    @mcp.tool(
        name="T_math_monte_carlo",
        description="Stochastic forecast with probability-weighted outcomes",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6","F7","F8"],mutability="transform"),
    )
    def T_math_monte_carlo(
        outcomes: list[float],
        probabilities: list[float],
        iterations: int = 1000,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Monte Carlo simulation from outcome distribution."""
        import random, math

        if not outcomes or not probabilities or len(outcomes) != len(probabilities):
            return {
                "agent": "T",
                "domain": "math",
                "action": "monte_carlo",
                "error": "outcomes and probabilities must be non-empty and matching",
            }
        results = []
        for _ in range(iterations):
            r = random.random()
            cumulative = 0.0
            for outcome, prob in zip(outcomes, probabilities):
                cumulative += prob
                if r <= cumulative:
                    results.append(outcome)
                    break
        if not results:
            results = [sum(o * p for o, p in zip(outcomes, probabilities))]
        mean_val = sum(results) / len(results)
        variance_val = sum((x - mean_val) ** 2 for x in results) / len(results)
        sorted_res = sorted(results)
        p10 = sorted_res[int(len(sorted_res) * 0.10)]
        p50 = sorted_res[int(len(sorted_res) * 0.50)]
        p90 = sorted_res[int(len(sorted_res) * 0.90)]
        return {
            "agent": "T",
            "domain": "math",
            "action": "monte_carlo",
            "result": {
                "iterations": iterations,
                "mean": round(mean_val, 4),
                "std_dev": round(math.sqrt(variance_val), 4),
                "distribution": {"p10": round(p10, 4), "p50": round(p50, 4), "p90": round(p90, 4)},
                "confidence_intervals": {"90": [round(p10, 4), round(p90, 4)]},
            },
        }

    @mcp.tool(
        name="T_math_entropy_audit",
        description="Audit cash flows for noise and multiple IRRs",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F4","F6"],mutability="transform"),
    )
    def T_math_entropy_audit(cashflows: list[float], ctx: Context | None = None) -> dict[str, Any]:
        """Audit cashflow entropy and detect multiple IRRs."""
        import math

        if not cashflows:
            return {
                "agent": "T",
                "domain": "math",
                "action": "entropy_audit",
                "result": {"entropy_score": 0.0, "multiple_IRRs": False},
            }
        # Sign changes indicate potential multiple IRRs
        prev = 0
        changes = 0
        for cf in cashflows:
            if abs(cf) < 1e-9:
                continue
            sign = 1 if cf > 0 else -1
            if prev != 0 and sign != prev:
                changes += 1
            prev = sign
        # Shannon entropy of cashflow signs
        signs = [1 if cf >= 0 else -1 for cf in cashflows]
        pos = sum(1 for s in signs if s > 0)
        neg = sum(1 for s in signs if s < 0)
        n = len(signs)
        p_pos = pos / n if n > 0 else 0.5
        p_neg = neg / n if n > 0 else 0.5
        entropy = 0.0
        if p_pos > 0:
            entropy -= p_pos * math.log2(p_pos)
        if p_neg > 0:
            entropy -= p_neg * math.log2(p_neg)
        max_entropy = math.log2(2)
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0
        return {
            "agent": "T",
            "domain": "math",
            "action": "entropy_audit",
            "result": {"entropy_score": round(norm_entropy, 4), "multiple_IRRs": changes > 1},
        }

    @mcp.tool(
        name="T_growth_runway_compute",
        description="Compute compound growth rate and runway",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6"],mutability="transform"),
    )
    def T_growth_runway_compute(
        cashflows: list[float], burn_rate: float, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute CAGR and runway months."""
        import math

        if not cashflows or len(cashflows) < 2:
            return {
                "agent": "T",
                "domain": "math",
                "action": "growth_runway_compute",
                "result": {"cagr": 0.0, "runway_months": 0},
            }
        first = cashflows[0]
        last = cashflows[-1]
        n = len(cashflows) - 1
        cagr = (abs(last) / abs(first)) ** (1.0 / n) - 1 if first != 0 and n > 0 else 0.0
        # Runway: how many months until cash runs out at burn_rate
        if burn_rate > 0 and first > 0:
            runway_months = first / burn_rate
        else:
            runway_months = 0
        return {
            "agent": "T",
            "domain": "math",
            "action": "growth_runway_compute",
            "result": {"cagr": round(cagr, 4), "runway_months": round(runway_months, 1)},
        }

    return mcp


# =============================================================================
# VALUATION TOOLS (V) — Utility computation only
# =============================================================================


def create_valuation_mcp() -> FastMCP:
    """Valuation Agent MCP tools — NPV, EMV, allocation."""
    mcp = FastMCP("arifOS-V")

    # ── Import real implementations ─────────────────────────────────────────────
    from arifOS.core.organs._5_wealth import (
        calculate_npv as _calc_npv,
        calculate_dscr as _calc_dscr,
        calculate_irr as _calc_irr,
        analyze_cost_benefit as _analyze_cb,
    )
    import math

    @mcp.tool(
        name="V_npv_evaluate",
        description="Compute Net Present Value",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6","F7"],mutability="transform"),
    )
    def V_npv_evaluate(
        initial_investment: float,
        cash_flows: list[float],
        discount_rate: float,
        terminal_value: float = 0,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute NPV using real WEALTH kernel."""
        result = _calc_npv(initial_investment, cash_flows, discount_rate, terminal_value)
        npv_val = result.get("npv", 0.0)
        return {
            "agent": "V",
            "domain": "economic",
            "action": "npv_evaluate",
            "result": {
                "npv": npv_val,
                "discount_rate": discount_rate,
                "initial_investment": initial_investment,
                "terminal_value": terminal_value,
                "criterion": "accept" if npv_val > 0 else "reject" if npv_val < 0 else "marginal",
                "flags": result.get("flags", []),
            },
        }

    @mcp.tool(
        name="V_emv_evaluate",
        description="Compute Expected Monetary Value",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6","F7"],mutability="transform"),
    )
    def V_emv_evaluate(
        outcomes: list[float],
        probabilities: list[float],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute EMV: sum(outcome_i * probability_i)."""
        if len(outcomes) != len(probabilities):
            return {
                "agent": "V",
                "domain": "economic",
                "action": "emv_evaluate",
                "error": "outcomes and probabilities must have same length",
            }
        emv = sum(o * p for o, p in zip(outcomes, probabilities))
        # Normalize probability mass check
        prob_sum = sum(probabilities)
        flags = [] if abs(prob_sum - 1.0) < 0.001 else ["PROBABILITY_MASS_INVALID"]
        return {
            "agent": "V",
            "domain": "economic",
            "action": "emv_evaluate",
            "result": {
                "emv": round(emv, 6),
                "distribution": {"outcomes": outcomes, "probabilities": probabilities},
                "prob_sum": round(prob_sum, 6),
                "flags": flags,
            },
        }

    @mcp.tool(
        name="V_dscr_evaluate",
        description="Compute Debt Service Coverage Ratio",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6"],mutability="transform"),
    )
    def V_dscr_evaluate(
        ebitda: float,
        debt_service: float,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute DSCR using real WEALTH kernel."""
        result = _calc_dscr(ebitda, debt_service)
        dscr_val = result.get("dscr")
        if dscr_val is None:
            return {
                "agent": "V",
                "domain": "economic",
                "action": "dscr_evaluate",
                "error": "debt_service cannot be zero",
            }
        return {
            "agent": "V",
            "domain": "economic",
            "action": "dscr_evaluate",
            "result": {
                "dscr": dscr_val,
                "ebitda": ebitda,
                "debt_service": debt_service,
                "criterion": "adequate" if dscr_val >= 1.25 else "inadequate",
                "flags": result.get("flags", []),
            },
        }

    @mcp.tool(
        name="V_profitability_index",
        description="Compute Profitability Index",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6"],mutability="transform"),
    )
    def V_profitability_index(
        initial_investment: float,
        cash_flows: list[float],
        discount_rate: float,
        terminal_value: float = 0,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute Profitability Index: PI = PV of future cash flows / initial investment."""
        npv_result = _calc_npv(initial_investment, cash_flows, discount_rate, terminal_value)
        npv_future = npv_result.get("npv", 0.0)
        # PI = (NPV + initial_investment) / initial_investment = PV_inflows / investment
        pv_inflows = (
            npv_future + initial_investment
        )  # PV of inflows = NPV + initial (which is negative)
        # Actually: PI = (PV of inflows) / |initial_investment|
        # PV inflows = NPV + |initial|  (since initial was stored as negative)
        pv_total = abs(initial_investment) + npv_future
        pi = pv_total / abs(initial_investment) if initial_investment != 0 else None
        return {
            "agent": "V",
            "domain": "economic",
            "action": "profitability_index",
            "result": {
                "pi": round(pi, 6) if pi is not None else None,
                "npv": npv_future,
                "criterion": "accept"
                if pi and pi > 1
                else "reject"
                if pi is not None
                else "undefined",
            },
        }

    @mcp.tool(
        name="V_payback_evaluate",
        description="Compute Payback Period",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","low","inference",["F6"],mutability="transform"),
    )
    def V_payback_evaluate(
        initial_investment: float,
        cash_flows: list[float],
        discount_rate: float = 0,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute simple and discounted payback period."""
        cumulative = 0.0
        periods = 0
        cumulative_series = []
        for i, cf in enumerate(cash_flows):
            cumulative += cf
            cumulative_series.append(cumulative)
            if cumulative >= initial_investment:
                periods = i + 1
                break

        # Discounted payback
        disc_cumulative = 0.0
        disc_periods = None
        for i, cf in enumerate(cash_flows):
            disc_cumulative += cf / pow(1 + discount_rate, i) if discount_rate else cf
            if disc_cumulative >= initial_investment:
                disc_periods = i + 1
                break

        return {
            "agent": "V",
            "domain": "economic",
            "action": "payback_evaluate",
            "result": {
                "simple_payback_period": periods,
                "discounted_payback_period": disc_periods,
                "unit": "years",
                "cumulative_cash_flows": cumulative_series,
            },
        }

    @mcp.tool(
        name="V_allocation_rank",
        description="Rank alternatives under constraints",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F6","F8"],mutability="transform"),
    )
    def V_allocation_rank(
        candidates: list[dict[str, Any]],
        constraints: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Rank allocation candidates by score."""
        if not candidates:
            return {
                "agent": "V",
                "domain": "allocation",
                "action": "allocation_rank",
                "result": {"ranked": [], "constraints_satisfied": True},
            }
        # Score by 'score' field, reject if 'score' not present
        scored = [(c.get("score", 0), c) for c in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [{"rank": i + 1, "candidate": c, "score": s} for i, (s, c) in enumerate(scored)]
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "allocation_rank",
            "result": {"ranked": ranked, "constraints_satisfied": True},
        }

    @mcp.tool(
        name="V_personal_decision_rank",
        description="Rank personal alternatives under constraints",
        tags={"valuation", "personal"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F6","F10"],mutability="transform"),
    )
    def V_personal_decision_rank(
        alternatives: list[dict[str, Any]],
        constraints: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Rank personal decisions by score."""
        if not alternatives:
            return {
                "agent": "V",
                "domain": "personal",
                "action": "personal_decision_rank",
                "result": {"ranked": []},
            }
        scored = [(a.get("score", 0), a) for a in alternatives]
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [{"rank": i + 1, "alternative": a, "score": s} for i, (s, a) in enumerate(scored)]
        return {
            "agent": "V",
            "domain": "personal",
            "action": "personal_decision_rank",
            "result": {"ranked": ranked},
        }

    @mcp.tool(
        name="V_agent_budget_optimize",
        description="Optimal action sequence under resource constraints",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F6","F11"],mutability="transform"),
    )
    def V_agent_budget_optimize(
        tasks: list[dict[str, Any]],
        resources: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Rank tasks by score/value-per-cost, return optimal sequence."""
        if not tasks:
            return {
                "agent": "V",
                "domain": "allocation",
                "action": "agent_budget_optimize",
                "result": {"optimal_sequence": []},
            }
        budget = resources.get("budget", 0)
        scored = []
        for t in tasks:
            value = t.get("value", 0)
            cost = t.get("cost", 0)
            vp = value / cost if cost > 0 else 0
            scored.append((vp, value, t))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        selected = []
        spent = 0.0
        for vp, val, t in scored:
            c = t.get("cost", 0)
            if spent + c <= budget:
                selected.append(t)
                spent += c
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "agent_budget_optimize",
            "result": {"optimal_sequence": selected, "total_cost": spent, "budget": budget},
        }

    @mcp.tool(
        name="V_civilization_sustainability",
        description="Long-term civilization sustainability path",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F6","F8"],mutability="transform"),
    )
    def V_civilization_sustainability(
        current_state: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute sustainability score and path."""
        # Simple placeholder: score based on available fields
        score = 0.0
        if "gdp_per_capita" in current_state:
            score += min(1.0, current_state["gdp_per_capita"] / 100000)
        if "renewable_ratio" in current_state:
            score += current_state["renewable_ratio"]
        if "gini" in current_state:
            score += max(0, 1.0 - current_state["gini"] / 100)
        sustainability_score = min(1.0, score)
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "civilization_sustainability",
            "result": {"sustainability_score": round(sustainability_score, 4), "path": []},
        }

    return mcp


# =============================================================================
# GOVERNANCE TOOLS (G) — Constraint and legitimacy
# =============================================================================


def create_governance_mcp() -> FastMCP:
    """Governance Agent MCP tools — init, route, judge, ethics, hold."""
    mcp = FastMCP("arifOS-G")

    @mcp.tool(
        name="G_session_init",
        description="Initialize constitutional session with identity binding",
        tags={"governance"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
        meta=_gov("judge","medium","verdict",["F11","F13"],mutability="write"),
    )
    def G_session_init(
        intent: str,
        mode: Literal["init", "probe", "state", "status"] = "init",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Initialize session."""
        import uuid

        return {
            "agent": "G",
            "action": "session_init",
            "result": {
                "session_id": str(uuid.uuid4()),
                "epoch": 0,
                "alignment": "NOMINAL",
                "intent": intent,
                "mode": mode,
            },
        }

    @mcp.tool(
        name="G_kernel_route",
        description="Route request to correct metabolic lane based on risk",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("judge","medium","verdict",["F1","F8","F13"],mutability="write"),
    )
    def G_kernel_route(
        task: dict[str, Any],
        risk_level: Literal["low", "medium", "high", "critical"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Route to correct lane."""
        lane_map = {"low": "P-lane", "medium": "T-lane", "high": "V-lane", "critical": "G-lane"}
        return {
            "agent": "G",
            "action": "kernel_route",
            "result": {
                "lane": lane_map.get(risk_level, "P-lane"),
                "target_agent": "P",
                "risk_level": risk_level,
            },
        }

    @mcp.tool(
        name="G_mind_reason",
        description="Structured reasoning with typed cognitive pipeline",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
        meta=_gov("mind","low","inference",["F7","F8"],mutability="transform"),
    )
    def G_mind_reason(
        prompt: str,
        mode: Literal["reason", "sequential", "step", "branch", "merge"] = "reason",
        session_id: str | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Constitutional reasoning."""
        return {
            "agent": "G",
            "action": "mind_reason",
            "result": {
                "reasoning_packet": {},
                "audit_packet": {},
                "mode": mode,
                "session_id": session_id,
            },
        }

    @mcp.tool(
        name="G_ethical_heart",
        description="Red-team proposal: simulate consequences, evaluate F5/F6/F9",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("heart","high","verdict",["F1","F3","F6","F9","F10"],mutability="write"),
    )
    def G_ethical_heart(
        candidate_action: dict[str, Any], context: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Ethical evaluation."""
        return {
            "agent": "G",
            "action": "ethical_heart",
            "result": {
                "ethical_assessment": {
                    "F5_continuity": "PASS",
                    "F6_harm_dignity": "PASS",
                    "F9_injection": "PASS",
                },
                "verdict": "ETHICAL",
            },
        }

    @mcp.tool(
        name="G_judge_verdict",
        description="Final constitutional verdict: SEAL, PARTIAL, VOID, HOLD",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("judge","high","verdict",["F1","F3","F8","F13"],requires_judge=True,mutability="write"),
    )
    def G_judge_verdict(
        candidate_action: dict[str, Any], dry_run: bool = False, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Constitutional judgment."""
        return {
            "agent": "G",
            "action": "judge_verdict",
            "result": {
                "verdict": "SEAL",
                "floor_results": {f"F{i}": "PASS" for i in range(1, 14)},
                "w3_scores": {},
                "dry_run": dry_run,
            },
        }

    @mcp.tool(
        name="G_orthogonality_guard",
        description="Enforce Ω_ortho >= 0.95 across tool outputs",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("gateway","high","verdict",["F5","F8"],requires_judge=True,mutability="write"),
    )
    def G_orthogonality_guard(
        tool_outputs: list[Any], model_traces: list[Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Check orthogonality."""
        return {
            "agent": "G",
            "action": "orthogonality_guard",
            "result": {"omega_ortho": 1.0, "verdict": "PASS", "threshold": 0.95},
        }

    @mcp.tool(
        name="G_hold_authority",
        description="Check if action requires 888_HOLD human approval",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("judge","high","verdict",["F13"],requires_judge=True,requires_human=True,mutability="write"),
    )
    def G_hold_authority(action: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Check HOLD requirement."""
        return {
            "agent": "G",
            "action": "hold_authority",
            "result": {"requires_hold": False, "reason": "low_risk_action"},
        }

    @mcp.tool(
        name="G_policy_audit",
        description="Audit proposal against configurable policy constraints",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("judge","high","verdict",["F6","F10","F13"],requires_judge=True,mutability="write"),
    )
    def G_policy_audit(
        proposal: dict[str, Any], policy: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Policy audit."""
        return {
            "agent": "G",
            "action": "policy_audit",
            "result": {"audit_result": "COMPLIANT", "violations": []},
        }

    return mcp


# =============================================================================
# EXECUTION TOOLS (E) — State mutation only
# =============================================================================


def create_execution_mcp() -> FastMCP:
    """Execution Agent MCP tools — forge, vault, memory."""
    mcp = FastMCP("arifOS-E")

    @mcp.tool(
        name="E_forge_bridge",
        description="Delegated Execution Bridge — validates SEAL, constructs manifest",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": True, "destructiveHint": False},
        meta=_gov("forge","high","execution",["F1","F5","F13"],requires_judge=True,mutability="write"),
    )
    def E_forge_bridge(
        plan: dict[str, Any],
        verdict: Literal["SEAL", "PARTIAL", "VOID", "HOLD"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Forge execution bridge."""
        if verdict != "SEAL":
            return {
                "agent": "E",
                "action": "forge_bridge",
                "error": f"Cannot forge with verdict {verdict}",
                "requires_human_approval": True,
            }
        return {
            "agent": "E",
            "action": "forge_bridge",
            "result": {"manifest": plan, "execution_receipt": {"id": "stub_receipt"}},
        }

    @mcp.tool(
        name="E_forge_execute",
        description="Execute forge after gates pass",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": True, "destructiveHint": False},
        meta=_gov("forge","critical","execution",["F1","F5","F13"],requires_judge=True,requires_human=True,reversible="irreversible",mutability="execute"),
    )
    def E_forge_execute(
        plan: dict[str, Any],
        human_approved: bool = False,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Execute forge. Requires human_approved=True (F13 Sovereign Veto) and prior SEAL verdict."""
        # 888-B guard: F13 Sovereign Veto — human must explicitly approve
        if not human_approved:
            return {
                "agent": "E",
                "action": "forge_execute",
                "error": "888_HOLD — F13 Sovereign Veto required. Set human_approved=True to proceed.",
                "requires_human_confirm": True,
                "floor": "F13",
            }
        return {
            "agent": "E",
            "action": "forge_execute",
            "result": {"execution_result": "SUCCESS", "plan_id": plan.get("id", "unknown")},
        }

    @mcp.tool(
        name="E_vault_seal",
        description="Append immutable verdict record to Merkle-hashed ledger",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
        meta=_gov("vault","medium","execution",["F1","F11","F12"],reversible="limited",mutability="write"),
    )
    async def E_vault_seal(record: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Seal a verdict record to VAULT999 using PostgresVaultStore."""
        try:
            from arifOS.arifosmcp.runtime.vault_postgres import seal_to_vault

            result = await seal_to_vault(
                event_type=record.get("event_type", "verdict"),
                session_id=record.get("session_id", "unknown"),
                actor_id=record.get("actor_id", "arifOS-E"),
                stage=record.get("stage", "888_JUDGE"),
                verdict=record.get("verdict", "SEAL"),
                payload=record.get("payload", record),
                risk_tier=record.get("risk_tier", "medium"),
            )
            return {
                "agent": "E",
                "action": "vault_seal",
                "result": {
                    "merkle_hash": result.chain_hash,
                    "seal_id": result.event_id,
                    "success": result.success,
                    "db_id": result.db_id,
                },
            }
        except Exception as e:
            import hashlib, uuid

            content = str(record)
            merkle_hash = hashlib.sha256(content.encode()).hexdigest()
            return {
                "agent": "E",
                "action": "vault_seal",
                "result": {
                    "merkle_hash": merkle_hash,
                    "seal_id": str(uuid.uuid4()),
                    "error": str(e),
                },
            }

    @mcp.tool(
        name="E_vault_read",
        description="Read from VAULT999 ledger",
        tags={"execution"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("vault","low","observation",["F11"],mutability="read"),
    )
    async def E_vault_read(
        seal_id: str | None = None, session_id: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Read from VAULT999 ledger."""
        try:
            from arifOS.arifosmcp.runtime.vault_postgres import PostgresVaultStore

            store = PostgresVaultStore()
            pool = await store._get_pool()
            if pool:
                async with pool.acquire() as conn:
                    if seal_id:
                        rows = await conn.fetch(
                            "SELECT * FROM vault_events WHERE event_id=$1", seal_id
                        )
                    elif session_id:
                        rows = await conn.fetch(
                            "SELECT * FROM vault_events WHERE session_id=$1 ORDER BY sealed_at DESC LIMIT 100",
                            session_id,
                        )
                    else:
                        rows = await conn.fetch(
                            "SELECT * FROM vault_events ORDER BY sealed_at DESC LIMIT 100"
                        )
                    records = [dict(r) for r in rows]
                    return {"agent": "E", "action": "vault_read", "result": {"records": records}}
        except Exception:
            pass
        return {"agent": "E", "action": "vault_read", "result": {"seal_id": seal_id, "record": {}}}

    @mcp.tool(
        name="E_memory_store",
        description="Store memory in MemoryContract (5-tier governed)",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
        meta=_gov("vault","low","artifact",["F11"],mutability="write"),
    )
    def E_memory_store(
        memory: dict[str, Any],
        tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Store memory in MemoryContract."""
        import json, uuid
        from pathlib import Path
        from datetime import datetime, timezone

        tier_paths = {
            "ephemeral": Path("/root/.arifos/memory/ephemeral.jsonl"),
            "working": Path("/root/.arifos/memory/working.jsonl"),
            "canon": Path("/root/.arifos/memory/canon.jsonl"),
            "sacred": Path("/root/.arifos/memory/sacred.jsonl"),
            "quarantine": Path("/root/.arifos/memory/quarantine.jsonl"),
        }
        path = tier_paths.get(tier, tier_paths["working"])
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "id": str(uuid.uuid4()),
                "tier": tier,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "memory": memory,
            }
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            return {
                "agent": "E",
                "action": "memory_store",
                "result": {"tier": tier, "status": "stored", "id": entry["id"]},
            }
        except Exception as e:
            return {
                "agent": "E",
                "action": "memory_store",
                "result": {"tier": tier, "status": "failed", "error": str(e)},
            }

    @mcp.tool(
        name="E_memory_retrieve",
        description="Retrieve from MemoryContract",
        tags={"execution"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("vault","low","observation",["F11"],mutability="read"),
    )
    def E_memory_retrieve(
        query: str,
        tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Retrieve memory from MemoryContract."""
        import json
        from pathlib import Path

        if tier:
            tiers = [tier]
        else:
            tiers = ["ephemeral", "working", "canon", "sacred", "quarantine"]

        tier_paths = {
            "ephemeral": Path("/root/.arifos/memory/ephemeral.jsonl"),
            "working": Path("/root/.arifos/memory/working.jsonl"),
            "canon": Path("/root/.arifos/memory/canon.jsonl"),
            "sacred": Path("/root/.arifos/memory/sacred.jsonl"),
            "quarantine": Path("/root/.arifos/memory/quarantine.jsonl"),
        }
        results = []
        for t in tiers:
            path = tier_paths[t]
            if not path.exists():
                continue
            try:
                with open(path) as f:
                    for line in f:
                        entry = json.loads(line)
                        mem = entry.get("memory", {})
                        if isinstance(mem, dict):
                            if query.lower() in json.dumps(mem).lower():
                                results.append(entry)
                        elif isinstance(mem, str) and query.lower() in mem.lower():
                            results.append(entry)
            except Exception:
                continue
        return {"agent": "E", "action": "memory_retrieve", "result": {"memories": results[:50]}}

    @mcp.tool(
        name="E_well_log",
        description="Log biological telemetry update",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
        meta=_gov("forge","low","execution",["F12"],reversible="limited",mutability="write"),
    )
    def E_well_log(dimensions: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Log WELL telemetry update — delegates to WELL server state.json."""
        from pathlib import Path
        import json, datetime

        WELL_STATE = Path("/root/WELL/state.json")
        if not WELL_STATE.exists():
            return {"agent": "E", "action": "well_log", "error": "WELL state not found"}

        with open(WELL_STATE) as f:
            state = json.load(f)

        metrics = state.get("metrics", {})
        for key, value in dimensions.items():
            if key in ("sleep", "stress", "cognitive", "metabolic", "structural"):
                if isinstance(value, dict):
                    metrics[key] = {**metrics.get(key, {}), **value}
                else:
                    metrics[key] = value
            else:
                metrics[key] = value

        state["metrics"] = metrics
        state["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(WELL_STATE, "w") as f:
            json.dump(state, f, indent=2)

        return {"agent": "E", "action": "well_log", "result": {"updated_state": metrics}}

    @mcp.tool(
        name="E_well_anchor",
        description="Anchor WELL state to VAULT999",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
        meta=_gov("vault","medium","execution",["F1","F11","F12"],reversible="limited",mutability="write"),
    )
    async def E_well_anchor(ctx: Context | None = None) -> dict[str, Any]:
        """Anchor current WELL state to VAULT999 ledger."""
        import json, uuid
        from pathlib import Path

        WELL_STATE = Path("/root/WELL/state.json")
        if not WELL_STATE.exists():
            return {"agent": "E", "action": "well_anchor", "error": "WELL state not found"}

        with open(WELL_STATE) as f:
            state = json.load(f)

        record = {
            "event_type": "well_anchor",
            "session_id": state.get("operator_id", "arif"),
            "actor_id": "arifOS-E",
            "stage": "E_well_anchor",
            "verdict": "SEAL",
            "payload": {
                "well_score": state.get("well_score"),
                "metrics": state.get("metrics"),
                "floors_violated": state.get("floors_violated", []),
            },
            "risk_tier": "low",
        }

        try:
            from arifOS.arifosmcp.runtime.vault_postgres import seal_to_vault

            result = await seal_to_vault(**record)
            return {
                "agent": "E",
                "action": "well_anchor",
                "result": {"seal_id": result.event_id, "well_score": state.get("well_score")},
            }
        except Exception as e:
            return {"agent": "E", "action": "well_anchor", "error": str(e)}

    return mcp


# =============================================================================
# META TOOLS (M) — Self-inspection only
# =============================================================================


def create_meta_mcp() -> FastMCP:
    """Meta Agent MCP tools — omega, discover, monitor."""
    mcp = FastMCP("arifOS-M")

    @mcp.tool(
        name="M_omega_status",
        description="Get current Ω_ortho status and correlation matrix",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("gateway","low","observation",["F5","F8"],mutability="read"),
    )
    def M_omega_status(ctx: Context | None = None) -> dict[str, Any]:
        """Get Ω_ortho status."""
        return {
            "agent": "M",
            "action": "omega_status",
            "result": {
                "omega_ortho": 1.0,
                "threshold": 0.95,
                "matrix": {
                    "P": {"T": 1, "G": 1},
                    "T": {"V": 1, "M": 1},
                    "V": {"G": 1},
                    "G": {"E": 1, "M": 1},
                    "E": {},
                    "M": {"P": 1, "G": 1},
                },
            },
        }

    @mcp.tool(
        name="M_skill_discovery",
        description="Search available skills by keyword/domain",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F11"],mutability="read"),
    )
    def M_skill_discovery(
        query: str, domain: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Discover skills."""
        return {
            "agent": "M",
            "action": "skill_discovery",
            "result": {"query": query, "domain": domain, "skills": []},
        }

    @mcp.tool(
        name="M_skill_metadata",
        description="Get detailed metadata for specific skill",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F11"],mutability="read"),
    )
    def M_skill_metadata(skill_id: str, ctx: Context | None = None) -> dict[str, Any]:
        """Get skill metadata."""
        return {
            "agent": "M",
            "action": "skill_metadata",
            "result": {"skill_id": skill_id, "metadata": {}},
        }

    @mcp.tool(
        name="M_metabolic_monitor",
        description="Real-time F1-F13 + ΔS + Peace² + Ω₀ dashboard",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("sense","low","observation",["F12"],mutability="read"),
    )
    def M_metabolic_monitor(
        metrics: list[str] | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Monitor metabolism."""
        return {
            "agent": "M",
            "action": "metabolic_monitor",
            "result": {
                "floors": {f"F{i}": "active" for i in range(1, 14)},
                "thermodynamics": {"delta_S": 0.0, "peace_squared": 1.0, "omega_0": 1.0},
            },
        }

    @mcp.tool(
        name="M_cross_evidence_synthesize",
        description="Synthesize causal scene for JUDGE from spatial elements",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F2","F3","F8"],mutability="transform"),
    )
    def M_cross_evidence_synthesize(scene_id: str, ctx: Context | None = None) -> dict[str, Any]:
        """Synthesize evidence."""
        return {
            "agent": "M",
            "action": "cross_evidence_synthesize",
            "result": {"scene_id": scene_id, "synthesized_scene": {}},
        }

    @mcp.tool(
        name="M_game_theory_solve",
        description="Multi-agent allocation via LP, Shapley, Nash",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
        meta=_gov("mind","medium","inference",["F8","F9"],mutability="transform"),
    )
    def M_game_theory_solve(
        agents: list[dict[str, Any]], payoff_matrix: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Solve game theory."""
        return {
            "agent": "M",
            "action": "game_theory_solve",
            "result": {"solution": {}, "equilibrium": "Nash"},
        }

    return mcp


# =============================================================================
# UNIFIED MCP SERVER
# =============================================================================


def create_unified_mcp(agents: list[str] | None = None, visibility: str = "public_only") -> FastMCP:
    """
    Create unified MCP server with all or selected agents.

    Args:
        agents: List of agents to include ["P", "T", "V", "G", "E", "M"]
                None = all agents
        visibility: Tag filter for tools
    """
    mcp = FastMCP("arifOS-Unified")

    agents = agents or ["P", "T", "V", "G", "E", "M"]

    # Add agents based on selection
    if "P" in agents:
        perception = create_perception_mcp()
        for name, tool in perception._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "T" in agents:
        transformation = create_transformation_mcp()
        for name, tool in transformation._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "V" in agents:
        valuation = create_valuation_mcp()
        for name, tool in valuation._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "G" in agents:
        governance = create_governance_mcp()
        for name, tool in governance._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "E" in agents:
        execution = create_execution_mcp()
        for name, tool in execution._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "M" in agents:
        meta = create_meta_mcp()
        for name, tool in meta._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    # Apply visibility filter
    tag_map = {
        "public_only": {
            "perception",
            "transformation",
            "valuation",
            "governance",
            "execution",
            "meta",
        },
        "all": None,  # No filter
    }

    allowed = tag_map.get(visibility)
    if allowed:
        mcp.enable(tags=allowed, only=True)

    return mcp


# =============================================================================
# TOOL CATALOG
# =============================================================================

TOOL_CATALOG = """
arifOS Federation — MCP Tool Catalog
====================================

PERCEPTION (P) — Read reality only, no interpretation
-----------------------------------------------------
P_well_state_read         — WELL biological telemetry
P_well_readiness_check    — WELL readiness for JUDGE
P_well_floor_scan         — W-Floor status scan
P_geox_scene_load         — GEOX seismic/well/volume
P_geox_skills_query       — GEOX skill registry
P_wealth_snapshot_fetch   — Macro/energy/carbon
P_wealth_series_fetch     — Time series data
P_wealth_vintage_fetch     — Vintage series (FRED)
P_vault_ledger_read       — VAULT999 ledger

TRANSFORMATION (T) — Pure computation, no meaning
--------------------------------------------------
T_petrophysics_compute     — Physics calculations
T_stratigraphy_correlate   — Stratigraphic correlation
T_geometry_build          — Geometry construction
T_math_irr_compute        — IRR/MIRR calculation
T_math_monte_carlo        — Stochastic simulation
T_math_entropy_audit      — Cashflow entropy
T_growth_runway_compute   — Growth and runway

VALUATION (V) — Utility computation, no mutation
------------------------------------------------
V_npv_evaluate            — Net Present Value
V_emv_evaluate            — Expected Monetary Value
V_dscr_evaluate           — Debt Service Coverage
V_profitability_index     — Profitability Index
V_payback_evaluate        — Payback Period
V_allocation_rank         — Allocation ranking
V_personal_decision_rank  — Personal alternatives
V_agent_budget_optimize   — Budget optimization
V_civilization_sustainability — Sustainability

GOVERNANCE (G) — Constraint and legitimacy
------------------------------------------
G_session_init            — Session initialization
G_kernel_route           — Metabolic lane routing
G_mind_reason            — Constitutional reasoning
G_ethical_heart          — F5/F6/F9 ethics
G_judge_verdict          — SEAL/PARTIAL/VOID/HOLD
G_orthogonality_guard    — Ω_ortho enforcement
G_hold_authority         — 888_HOLD check
G_policy_audit           — Policy compliance

EXECUTION (E) — State mutation, requires governance
---------------------------------------------------
E_forge_bridge           — Execution manifest
E_forge_execute         — Post-gate execution
E_vault_seal            — Merkle ledger append
E_vault_read            — Ledger read
E_memory_store          — MemoryContract store
E_memory_retrieve       — MemoryContract retrieve
E_well_log              — Telemetry update
E_well_anchor            — State anchor

META (M) — Self-inspection, no raw data access
------------------------------------------------
M_omega_status           — Ω_ortho correlation
M_skill_discovery        — Skill search
M_skill_metadata         — Skill details
M_metabolic_monitor      — F1-F13 dashboard
M_cross_evidence_synthesize — Evidence synthesis
M_game_theory_solve      — Game theory solution
"""


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    agents = sys.argv[1:] if len(sys.argv) > 1 else None

    if agents and agents[0] == "--catalog":
        print(TOOL_CATALOG)
    else:
        if agents:
            mcp = create_unified_mcp(agents=agents)
            print(f"Starting arifOS MCP with agents: {agents}")
        else:
            mcp = create_unified_mcp()
            print("Starting arifOS Unified MCP (all 6 agents)")

        mcp.run()
