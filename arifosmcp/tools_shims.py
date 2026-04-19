"""
arifosmcp/tools_shims.py — Shim Layer (Phase 2)
================================================
INTERNAL ROUTING ONLY — not registered as MCP tools.
Supports AgentZero and any client using old P/T/V/E/M tool names.
SHIM_HIT logging enables zero-hit confirmation before shim removal.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations
import logging

logger = logging.getLogger("arifos.shims")

# Import canonical engines from tools_canonical.py
try:
    from arifosmcp.tools_canonical import (
        arifos_compute_physics,
        arifos_compute_finance,
        arifos_compute_civilization,
        arifos_oracle_bio,
        arifos_oracle_world,
    )
    SHIMS_AVAILABLE = True
except ImportError:
    SHIMS_AVAILABLE = False
    logger.warning("tools_canonical.py not available — shims will return error")


# ═══════════════════════════════════════════════════════════════════════════════
# PERCEPTION SHIMS (P) — Well state + Geox + Wealth oracle
# ═══════════════════════════════════════════════════════════════════════════════

def P_well_state_read(session_id: str | None = None, ctx=None) -> dict:
    logger.warning("SHIM_HIT: P_well_state_read → arifos_oracle_bio[snapshot_read]")
    return arifos_oracle_bio("snapshot_read", session_id=session_id) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_well_readiness_check(session_id: str | None = None, ctx=None) -> dict:
    logger.warning("SHIM_HIT: P_well_readiness_check → arifos_oracle_bio[readiness_check]")
    return arifos_oracle_bio("readiness_check", session_id=session_id) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_well_floor_scan(session_id: str | None = None, ctx=None) -> dict:
    logger.warning("SHIM_HIT: P_well_floor_scan → arifos_oracle_bio[floor_scan]")
    return arifos_oracle_bio("floor_scan", session_id=session_id) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_geox_scene_load(
    session_id: str | None = None,
    scene_type: str | None = None,
    path: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: P_geox_scene_load → arifos_oracle_world[geox_scene_load]")
    return arifos_oracle_world("geox_scene_load", session_id=session_id, scene_type=scene_type, path=path) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_geox_skills_query(
    session_id: str | None = None,
    query: str = "",
    domain: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: P_geox_skills_query → arifos_oracle_world[geox_skills_query]")
    return arifos_oracle_world("geox_skills_query", session_id=session_id, query=query, domain=domain) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_wealth_snapshot_fetch(
    session_id: str | None = None,
    geography: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: P_wealth_snapshot_fetch → arifos_oracle_world[macro_snapshot]")
    return arifos_oracle_world("macro_snapshot", session_id=session_id, geography=geography) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_wealth_series_fetch(
    session_id: str | None = None,
    source: str | None = None,
    series_id: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: P_wealth_series_fetch → arifos_oracle_world[series_fetch]")
    return arifos_oracle_world("series_fetch", session_id=session_id, source=source, series_id=series_id) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def P_wealth_vintage_fetch(
    session_id: str | None = None,
    series_id: str | None = None,
    vintage_date: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: P_wealth_vintage_fetch → arifos_oracle_world[series_vintage_fetch]")
    return arifos_oracle_world("series_vintage_fetch", session_id=session_id, series_id=series_id, vintage_date=vintage_date) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSFORMATION SHIMS (T) — Physics + Math
# ═══════════════════════════════════════════════════════════════════════════════

def T_petrophysics_compute(
    session_id: str | None = None,
    well_id: str | None = None,
    computation: str | None = None,
    params: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_petrophysics_compute → arifos_compute_physics[petrophysics]")
    return arifos_compute_physics("petrophysics", session_id=session_id, well_id=well_id, computation=computation, params=params) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_stratigraphy_correlate(
    session_id: str | None = None,
    wells: list[str] | None = None,
    section_id: str | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_stratigraphy_correlate → arifos_compute_physics[stratigraphy_correlate]")
    return arifos_compute_physics("stratigraphy_correlate", session_id=session_id, wells=wells, section_id=section_id) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_geometry_build(
    session_id: str | None = None,
    horizons: list[dict] | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_geometry_build → arifos_compute_physics[geometry_build]")
    return arifos_compute_physics("geometry_build", session_id=session_id, horizons=horizons) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_math_irr_compute(
    session_id: str | None = None,
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    finance_rate: float = 0,
    reinvest_rate: float = 0,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_math_irr_compute → arifos_compute_finance[irr]")
    return arifos_compute_finance(
        "irr", session_id=session_id,
        initial_investment=initial_investment, cash_flows=cash_flows,
        finance_rate=finance_rate, reinvest_rate=reinvest_rate,
    ) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_math_monte_carlo(
    session_id: str | None = None,
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    iterations: int = 1000,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_math_monte_carlo → arifos_compute_physics[monte_carlo]")
    return arifos_compute_physics("monte_carlo", session_id=session_id, outcomes=outcomes, probabilities=probabilities, iterations=iterations) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_math_entropy_audit(
    session_id: str | None = None,
    cashflows: list[float] | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_math_entropy_audit → arifos_compute_physics[entropy_audit]")
    return arifos_compute_physics("entropy_audit", session_id=session_id, cashflows=cashflows) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def T_growth_runway_compute(
    session_id: str | None = None,
    cashflows: list[float] | None = None,
    burn_rate: float | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: T_growth_runway_compute → arifos_compute_physics[growth_runway]")
    return arifos_compute_physics("growth_runway", session_id=session_id, cashflows=cashflows, burn_rate=burn_rate) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# VALUATION SHIMS (V) — Finance + Economic
# ═══════════════════════════════════════════════════════════════════════════════

def V_npv_evaluate(
    session_id: str | None = None,
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    terminal_value: float = 0,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_npv_evaluate → arifos_compute_finance[npv]")
    return arifos_compute_finance(
        "npv", session_id=session_id,
        initial_investment=initial_investment, cash_flows=cash_flows,
        discount_rate=discount_rate, terminal_value=terminal_value,
    ) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_emv_evaluate(
    session_id: str | None = None,
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_emv_evaluate → arifos_compute_finance[emv]")
    return arifos_compute_finance("emv", session_id=session_id, outcomes=outcomes, probabilities=probabilities) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_dscr_evaluate(
    session_id: str | None = None,
    ebitda: float | None = None,
    debt_service: float | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_dscr_evaluate → arifos_compute_finance[dscr]")
    return arifos_compute_finance("dscr", session_id=session_id, ebitda=ebitda, debt_service=debt_service) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_profitability_index(
    session_id: str | None = None,
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    terminal_value: float = 0,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_profitability_index → arifos_compute_finance[profitability_index]")
    return arifos_compute_finance(
        "profitability_index", session_id=session_id,
        initial_investment=initial_investment, cash_flows=cash_flows,
        discount_rate=discount_rate, terminal_value=terminal_value,
    ) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_payback_evaluate(
    session_id: str | None = None,
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_payback_evaluate → arifos_compute_finance[payback]")
    return arifos_compute_finance("payback", session_id=session_id, initial_investment=initial_investment, cash_flows=cash_flows, discount_rate=discount_rate) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_allocation_rank(
    session_id: str | None = None,
    candidates: list[dict] | None = None,
    constraints: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_allocation_rank → arifos_compute_finance[allocation_rank]")
    return arifos_compute_finance("allocation_rank", session_id=session_id, candidates=candidates, constraints=constraints) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_personal_decision_rank(
    session_id: str | None = None,
    alternatives: list[dict] | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_personal_decision_rank → arifos_compute_finance[personal_decision_rank]")
    return arifos_compute_finance("personal_decision_rank", session_id=session_id, alternatives=alternatives) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_agent_budget_optimize(
    session_id: str | None = None,
    tasks: list[dict] | None = None,
    resources: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_agent_budget_optimize → arifos_compute_finance[budget_optimize]")
    return arifos_compute_finance("budget_optimize", session_id=session_id, tasks=tasks, resources=resources) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def V_civilization_sustainability(
    session_id: str | None = None,
    current_state: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: V_civilization_sustainability → arifos_compute_finance[civilization_sustainability]")
    return arifos_compute_finance("civilization_sustainability", session_id=session_id, current_state=current_state) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION SHIMS (E) — Well anchor + log
# ═══════════════════════════════════════════════════════════════════════════════

def E_well_log(
    session_id: str | None = None,
    dimensions: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: E_well_log → arifos_oracle_bio[log_update]")
    return arifos_oracle_bio("log_update", session_id=session_id, dimensions=dimensions) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def E_well_anchor(
    session_id: str | None = None,
    dimensions: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: E_well_anchor → arifos_oracle_bio[log_update]")
    return arifos_oracle_bio("log_update", session_id=session_id, dimensions=dimensions) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# META SHIMS (M) — Game theory + Cross evidence
# ═══════════════════════════════════════════════════════════════════════════════

def M_game_theory_solve(
    session_id: str | None = None,
    agents: list[dict] | None = None,
    payoff_matrix: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: M_game_theory_solve → arifos_compute_civilization[game_theory]")
    return arifos_compute_civilization("game_theory", session_id=session_id, agents=agents, payoff_matrix=payoff_matrix) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


def M_cross_evidence_synthesize(
    session_id: str | None = None,
    scene_id: str | None = None,
    current_state: dict | None = None,
    ctx=None,
) -> dict:
    logger.warning("SHIM_HIT: M_cross_evidence_synthesize → arifos_compute_civilization[cross_evidence_synthesize]")
    return arifos_compute_civilization("cross_evidence_synthesize", session_id=session_id, scene_id=scene_id, current_state=current_state) if SHIMS_AVAILABLE else {"error": "shims unavailable"}


# ═══════════════════════════════════════════════════════════════════════════════
# SHIM HIT COUNTER — for zero-hit confirmation
# ═══════════════════════════════════════════════════════════════════════════════

import threading as _threading

_SHIM_HIT_COUNTS: dict[str, int] = {}
_SHIM_LOCK = _threading.Lock()


def _record_shim_hit(shim_name: str) -> None:
    """Thread-safe shim hit counter for zero-hit monitoring."""
    with _SHIM_LOCK:
        _SHIM_HIT_COUNTS[shim_name] = _SHIM_HIT_COUNTS.get(shim_name, 0) + 1


def get_shim_hit_counts() -> dict[str, int]:
    """Return all shim hit counts. Use for monitoring."""
    with _SHIM_LOCK:
        return dict(_SHIM_HIT_COUNTS)


def reset_shim_hit_counts() -> None:
    """Reset all counters. Use for new monitoring window."""
    with _SHIM_LOCK:
        _SHIM_HIT_COUNTS.clear()
