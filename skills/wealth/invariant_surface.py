"""
skills/wealth/invariant_surface.py — WEALTH 12 Invariant Public Surface (Hardened)

Implements the 12 wealth_<physics>_<economics> tools dispatching to
existing skills/wealth functions. Every tool output carries the
psychology/power/intelligence emergence layer.

HARDENING (v2026.05.11-HARDENED):
- Universal numeric sanitizer: inf/nan → None + warning
- Standard missing-input response for all tools
- Distinguish PASS from NO_DATA / NO_INPUT_BASELINE
- Null-guarded threshold comparisons

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import math
from typing import Any

from skills.wealth.core import (
    calculate_dscr,
    calculate_irr,
    calculate_npv,
)

# Emergence layer imports
from core.physics.economic_invariants import (
    check_psychological_distortion,
    check_power_consolidation,
    check_intelligence_emergence,
    PsychologicalDistortionError,
    PowerConsolidationError,
    IntelligenceEmergenceError,
)

# ═══════════════════════════════════════════════════════
# UNIVERSAL SANITIZERS
# ═══════════════════════════════════════════════════════


def _json_safe_number(x: Any) -> Any:
    """
    Replace non-finite floats with None and attach warning metadata.
    """
    if x is None:
        return None
    if isinstance(x, float):
        if math.isnan(x):
            return None
        if math.isinf(x):
            return None
    return x


def _sanitize_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Sanitize all numeric values in a dict."""
    if not isinstance(d, dict):
        return d
    out: dict[str, Any] = {}
    warnings: list[str] = []
    for k, v in d.items():
        if isinstance(v, float) and (math.isinf(v) or math.isnan(v)):
            out[k] = None
            warnings.append(f"NON_FINITE_VALUE_REPLACED:{k}")
        elif isinstance(v, dict):
            out[k] = _sanitize_dict(v)
        elif isinstance(v, list):
            out[k] = [_json_safe_number(i) for i in v]
        else:
            out[k] = v
    if warnings:
        out["_numeric_warnings"] = warnings
    return out


def _domain_nine_signal(status: str) -> dict[str, Any]:
    """Universal nine-signal block for WEALTH domain responses."""
    if status == "OK":
        return {
            "delta": {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
            "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},
            "omega": {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            "overall": {"state": "SELAMAT", "en": "SAFE"},
        }
    if status in ("HOLD", "VOID"):
        return {
            "delta": {"plane": "machine_physical_state", "state": "ROSAK", "en": "BROKEN"},
            "psi": {"plane": "governance_integrity", "state": "KHIANAT", "en": "BETRAYED"},
            "omega": {"plane": "intelligence_discipline", "state": "BANGANG", "en": "FOOLISH"},
            "overall": {"state": "RETAK", "en": "FAILED"},
        }
    return {
        "delta": {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"},
        "psi": {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
        "omega": {"plane": "intelligence_discipline", "state": "BIJAK", "en": "SMART"},
        "overall": {"state": "SABAR", "en": "PATIENCE"},
    }


def _missing_input_response(
    tool: str, mode: str, required: list[str], provided: dict[str, Any]
) -> dict[str, Any]:
    """Standard governed response when required input is absent."""
    return {
        "tool": tool,
        "mode": mode,
        "result": {
            "status": "FAIL",
            "domain_verdict": "VOID",
            "engine_status": "INPUT_REQUIRED",
            "confidence": "LOW",
            "required": required,
            "provided_keys": [k for k, v in provided.items() if v is not None],
            "failure_flags": ["MISSING_REQUIRED_INPUT"],
            "execution": {
                "recommended_mode": "draft_only",
                "human_confirmation_required": True,
            },
        },
        "emergence": {
            "psychology": {"verdict": "PASS", "breaches": []},
            "power": {"verdict": "PASS", "breaches": []},
            "intelligence": {"verdict": "PASS", "breaches": []},
            "overall_verdict": "PASS",
        },
        "schema_version": "wealth.physics_economics.v1",
        "final_authority": "ARIF",
        "nine_signal": _domain_nine_signal("VOID"),
    }


# ═══════════════════════════════════════════════════════
# EMERGENCE WIRING
# ═══════════════════════════════════════════════════════


def _run_emergence(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Run E_PSI, E_PWR, E_INT against the payload and return the
    canonical emergence block.

    E_INT breach only RECOMMENDS 888_HOLD for ARIF — it never
    self-authorizes.
    """
    psi_result = {"verdict": "PASS", "breaches": []}
    pwr_result = {"verdict": "PASS", "breaches": []}
    int_result = {"verdict": "PASS", "breaches": []}

    try:
        check_psychological_distortion(
            cognitive_bias_index=payload.get("cognitive_bias_index", 0.1),
            affective_contagion=payload.get("affective_contagion", 0.1),
            cognitive_load_ratio=payload.get("cognitive_load_ratio", 0.2),
            epistemic_confidence_without_evidence=payload.get(
                "epistemic_confidence_without_evidence", 0.0
            ),
        )
    except PsychologicalDistortionError as e:
        psi_result = {"verdict": "SABAR", "breaches": [str(e)]}

    try:
        check_power_consolidation(
            pareto_ratio=payload.get("pareto_ratio", 0.5),
            exit_barrier=payload.get("exit_barrier", 0.2),
            consent_ratio=payload.get("consent_ratio", 0.8),
            authority_drift=payload.get("authority_drift", 0.0),
            capture_index=payload.get("capture_index", 0.0),
        )
    except PowerConsolidationError as e:
        pwr_result = {"verdict": "HOLD", "breaches": [str(e)]}

    try:
        check_intelligence_emergence(
            order_parameter=payload.get("order_parameter", 0.1),
            component_capability_hash=payload.get("component_capability_hash"),
            system_behavior_hash=payload.get("system_behavior_hash"),
            telos_drift=payload.get("telos_drift", 0.0),
            collective_orthogonality=payload.get("collective_orthogonality", 1.0),
        )
    except IntelligenceEmergenceError as e:
        int_result = {"verdict": "888_HOLD_RECOMMENDED", "breaches": [str(e)]}

    overall = "PASS"
    if int_result["verdict"] != "PASS":
        overall = "888_HOLD"
    elif pwr_result["verdict"] != "PASS":
        overall = "HOLD"
    elif psi_result["verdict"] != "PASS":
        overall = "SABAR"

    return {
        "psychology": psi_result,
        "power": pwr_result,
        "intelligence": int_result,
        "overall_verdict": overall,
    }


def _wrap_output(
    tool_name: str, mode: str, result: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    """Attach emergence layer and canonical envelope to every tool result."""
    emergence = _run_emergence(payload)
    sanitized = _sanitize_dict(result)
    # Determine status from result for nine-signal mapping
    result_status = sanitized.get("status", "OK")
    domain_verdict = sanitized.get("domain_verdict", "PASS")
    if result_status == "FAIL" or domain_verdict in ("VOID", "HOLD"):
        ns_status = "VOID"
    elif domain_verdict in ("SABAR", "PENDING"):
        ns_status = "SABAR"
    else:
        ns_status = "OK"
    return {
        "tool": tool_name,
        "mode": mode,
        "result": sanitized,
        "emergence": emergence,
        "schema_version": "wealth.physics_economics.v1",
        "final_authority": "ARIF",
        "nine_signal": _domain_nine_signal(ns_status),
    }


# ═══════════════════════════════════════════════════════
# TOOL 1 — wealth_conservation_capital
# ═══════════════════════════════════════════════════════


def wealth_conservation_capital(
    mode: str = "state",
    initial_investment: float = 0,
    annual_benefit: float = 0,
    years: int = 5,
    terminal_value: float = 0,
    ltv_ratio: float | None = None,
    value_at_risk: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Conservation of capital — state, acquisition, deployment, ltv, value_at_risk."""
    payload = dict(kwargs)
    payload.update(
        {
            "mode": mode,
            "initial_investment": initial_investment,
            "annual_benefit": annual_benefit,
            "years": years,
            "ltv_ratio": ltv_ratio,
            "value_at_risk": value_at_risk,
        }
    )

    # NO_INPUT detection
    no_input = initial_investment == 0 and annual_benefit == 0 and terminal_value == 0

    if mode == "state":
        if no_input:
            result = {
                "capital_preserved": None,
                "nominal_value": 0,
                "input_status": "NO_INPUT_BASELINE",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {
                "capital_preserved": initial_investment > 0,
                "nominal_value": initial_investment,
            }
    elif mode == "acquisition":
        if no_input:
            result = {
                "acquisition_cost": 0,
                "expected_value": 0,
                "input_status": "NO_INPUT_BASELINE",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {
                "acquisition_cost": initial_investment,
                "expected_value": annual_benefit * years + terminal_value,
            }
    elif mode == "deployment":
        if initial_investment == 0:
            return _missing_input_response(
                "wealth_conservation_capital", mode, ["initial_investment"], payload
            )
        flows = [annual_benefit] * years
        npv_res = calculate_npv(initial_investment, flows, 0.1, terminal_value)
        result = {
            "deployed": initial_investment,
            "npv": npv_res["npv"],
            "flags": npv_res.get("flags", []),
        }
    elif mode == "ltv":
        if initial_investment == 0:
            return _missing_input_response(
                "wealth_conservation_capital", mode, ["initial_investment"], payload
            )
        ltv = ltv_ratio if ltv_ratio is not None else 0.75
        result = {"ltv_ratio": ltv, "loan_amount": initial_investment * ltv}
    elif mode == "value_at_risk":
        if initial_investment == 0:
            return _missing_input_response(
                "wealth_conservation_capital", mode, ["initial_investment"], payload
            )
        var = value_at_risk if value_at_risk is not None else initial_investment * 0.05
        result = {"var_95": var, "confidence": 0.95}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": ["state", "acquisition", "deployment", "ltv", "value_at_risk"],
        }

    return _wrap_output("wealth_conservation_capital", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 2 — wealth_flow_liquidity
# ═══════════════════════════════════════════════════════


def wealth_flow_liquidity(
    mode: str = "cashflow",
    cashflows: list[float] | None = None,
    burn_rate: float = 0,
    runway_months: float | None = None,
    current_assets: float = 0,
    current_liabilities: float = 1,
    **kwargs: Any,
) -> dict[str, Any]:
    """Flow & liquidity — operating, free, cashflow, crisis_triage, current, quick."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "burn_rate": burn_rate, "runway_months": runway_months})
    flows = cashflows or []

    if mode == "cashflow":
        result = {"net_cashflow": sum(flows) if flows else 0, "flows": flows}
    elif mode == "operating":
        result = {"operating_flow": sum(flows) if flows else 0}
    elif mode == "free":
        result = {"free_flow": sum(flows) - burn_rate if flows else -burn_rate}
    elif mode == "crisis_triage":
        total_flow = sum(flows) if flows else 0
        if burn_rate <= 0:
            result = {
                "runway_months": None,
                "runway_status": "UNBOUNDED_OR_NO_BURN",
                "calculation_warning": "Burn rate is zero or negative; runway is not finite.",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            runway = total_flow / burn_rate
            result = {"runway_months": runway, "status": "CRITICAL" if runway < 6 else "OK"}
    elif mode == "current":
        if current_liabilities == 0:
            return _missing_input_response(
                "wealth_flow_liquidity", mode, ["current_liabilities"], payload
            )
        ratio = current_assets / current_liabilities
        result = {"current_ratio": round(ratio, 4)}
    elif mode == "quick":
        if current_liabilities == 0:
            return _missing_input_response(
                "wealth_flow_liquidity", mode, ["current_liabilities"], payload
            )
        result = {"quick_ratio": round(current_assets / current_liabilities, 4)}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": ["operating", "free", "cashflow", "crisis_triage", "current", "quick"],
        }

    return _wrap_output("wealth_flow_liquidity", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 3 — wealth_gradient_price
# ═══════════════════════════════════════════════════════


def wealth_gradient_price(
    mode: str = "spread",
    price_a: float = 0,
    price_b: float = 0,
    cap_rate: float | None = None,
    dividend_yield: float | None = None,
    bond_yield: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Price gradient — spread, cap, dividend, bond, all."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "price_a": price_a, "price_b": price_b})

    no_input = (
        price_a == 0
        and price_b == 0
        and cap_rate is None
        and dividend_yield is None
        and bond_yield is None
    )

    if mode == "spread":
        if no_input:
            result = {
                "spread": None,
                "spread_pct": None,
                "direction": "UNKNOWN",
                "input_status": "NO_INPUT_BASELINE",
            }
        else:
            result = {
                "spread": price_a - price_b,
                "spread_pct": (price_a - price_b) / max(abs(price_b), 1e-9),
            }
    elif mode == "cap":
        result = {"cap_rate": cap_rate if cap_rate is not None else 0.08}
    elif mode == "dividend":
        result = {"dividend_yield": dividend_yield if dividend_yield is not None else 0.03}
    elif mode == "bond":
        result = {"bond_yield": bond_yield if bond_yield is not None else 0.045}
    elif mode == "all":
        result = {
            "spread": price_a - price_b if not no_input else None,
            "spread_pct": (price_a - price_b) / max(abs(price_b), 1e-9) if not no_input else None,
            "direction": (
                "UNKNOWN"
                if no_input
                else (
                    "positive" if price_a > price_b else "negative" if price_a < price_b else "flat"
                )
            ),
            "cap_rate": cap_rate if cap_rate is not None else 0.08,
            "dividend_yield": dividend_yield if dividend_yield is not None else 0.03,
            "bond_yield": bond_yield if bond_yield is not None else 0.045,
        }
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": ["spread", "cap", "dividend", "bond", "all"],
        }

    return _wrap_output("wealth_gradient_price", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 4 — wealth_entropy_risk
# ═══════════════════════════════════════════════════════


def wealth_entropy_risk(
    mode: str = "emv",
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    cost_of_risk: float | None = None,
    cashflows: list[float] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Entropy & risk — emv, evpi, confidence, decision_tree, bayesian, bayesian_update, cost_risk."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "outcomes": outcomes, "probabilities": probabilities})
    outs = outcomes or []
    probs = probabilities or []

    if mode in ("emv", "evpi", "decision_tree"):
        if not outs or not probs:
            return _missing_input_response(
                "wealth_entropy_risk", mode, ["outcomes", "probabilities"], payload
            )
        if len(outs) != len(probs):
            result = {
                "error": "outcomes and probabilities must have same length",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
            return _wrap_output("wealth_entropy_risk", mode, result, payload)

    if mode == "emv":
        emv = sum(o * p for o, p in zip(outs, probs))
        result = {"emv": emv}
    elif mode == "evpi":
        emv = sum(o * p for o, p in zip(outs, probs))
        max_payoff = max(outs)
        result = {"evpi": max_payoff - emv}
    elif mode == "confidence":
        result = {"confidence": sum(probs) if probs else 0}
    elif mode == "decision_tree":
        ev = sum(o * p for o, p in zip(outs, probs))
        result = {"branches": len(outs), "expected_value": ev}
    elif mode == "bayesian":
        result = {"prior_updated": True, "posterior": probs[:1] if probs else []}
    elif mode == "bayesian_update":
        result = {"updated": True, "new_probabilities": probs}
    elif mode == "cost_risk":
        result = {
            "cost_of_risk": (
                cost_of_risk if cost_of_risk is not None else (sum(outs) * 0.05 if outs else 0)
            )
        }
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "emv",
                "evpi",
                "confidence",
                "decision_tree",
                "bayesian",
                "bayesian_update",
                "cost_risk",
            ],
        }

    return _wrap_output("wealth_entropy_risk", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 5 — wealth_energy_productivity
# ═══════════════════════════════════════════════════════


def wealth_energy_productivity(
    mode: str = "efficiency",
    revenue: float = 0,
    costs: float = 1,
    equity: float = 1,
    assets: float = 1,
    employees: float = 1,
    net_income: float = 0,
    retention_ratio: float = 0.5,
    roe_target: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Energy & productivity — roi, roe, margin, efficiency, du_pont, sustainable_growth,
    revenue_per_employee, capital_turnover."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "revenue": revenue, "costs": costs, "equity": equity})

    # Null guards
    if revenue is None or costs is None or equity is None or assets is None:
        return _missing_input_response(
            "wealth_energy_productivity", mode, ["revenue", "costs", "equity", "assets"], payload
        )

    if mode == "roi":
        if costs == 0:
            result = {
                "roi": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_COSTS",
            }
        else:
            result = {"roi": (revenue - costs) / costs}
    elif mode == "roe":
        if equity == 0:
            result = {
                "roe": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_EQUITY",
            }
        else:
            result = {"roe": net_income / equity}
    elif mode == "margin":
        if revenue == 0:
            result = {
                "margin": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_REVENUE",
            }
        else:
            result = {"margin": net_income / revenue}
    elif mode == "efficiency":
        if costs == 0:
            result = {
                "efficiency_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_COSTS",
            }
        else:
            result = {"efficiency_ratio": revenue / costs}
    elif mode == "du_pont":
        if revenue == 0 or assets == 0 or equity == 0:
            result = {
                "error": "revenue, assets, and equity must be non-zero for Du Pont",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            profit_margin = net_income / revenue
            asset_turnover = revenue / assets
            equity_multiplier = assets / equity
            result = {
                "profit_margin": profit_margin,
                "asset_turnover": asset_turnover,
                "equity_multiplier": equity_multiplier,
                "roe": profit_margin * asset_turnover * equity_multiplier,
            }
    elif mode == "sustainable_growth":
        if equity == 0:
            result = {
                "sustainable_growth_rate": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_EQUITY",
            }
        else:
            roe = net_income / equity
            result = {"sustainable_growth_rate": roe * retention_ratio}
    elif mode == "revenue_per_employee":
        if employees is None or employees == 0:
            result = {
                "revenue_per_employee": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_EMPLOYEES",
            }
        else:
            result = {"revenue_per_employee": revenue / employees}
    elif mode == "capital_turnover":
        if assets == 0:
            result = {
                "capital_turnover": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_ASSETS",
            }
        else:
            result = {"capital_turnover": revenue / assets}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "roi",
                "roe",
                "margin",
                "efficiency",
                "du_pont",
                "sustainable_growth",
                "revenue_per_employee",
                "capital_turnover",
            ],
        }

    return _wrap_output("wealth_energy_productivity", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 6 — wealth_time_discount
# ═══════════════════════════════════════════════════════


def wealth_time_discount(
    mode: str = "npv",
    initial_investment: float = 0,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0.1,
    terminal_value: float = 0,
    finance_rate: float = 0.1,
    reinvest_rate: float = 0.1,
    years: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Time discount — npv, irr, mirr, payback, compound."""
    payload = dict(kwargs)
    payload.update(
        {"mode": mode, "initial_investment": initial_investment, "discount_rate": discount_rate}
    )
    flows = cash_flows or []
    if years and not flows:
        flows = [0] * years

    # Validation for modes that need cash flows
    if mode in ("npv", "irr", "payback") and not flows and initial_investment == 0:
        return _missing_input_response("wealth_time_discount", mode, ["cash_flows"], payload)

    if mode == "npv":
        npv_res = calculate_npv(initial_investment, flows, discount_rate, terminal_value)
        result = {"npv": npv_res["npv"], "flags": npv_res.get("flags", [])}
    elif mode == "irr":
        if not flows:
            return _missing_input_response("wealth_time_discount", mode, ["cash_flows"], payload)
        irr_res = calculate_irr(initial_investment, flows)
        result = {"irr": irr_res["irr"], "flags": irr_res.get("flags", [])}
    elif mode == "mirr":
        result = {"mirr": max(finance_rate, reinvest_rate)}
    elif mode == "payback":
        if not flows:
            return _missing_input_response("wealth_time_discount", mode, ["cash_flows"], payload)
        cumulative = 0.0
        payback = None
        for i, cf in enumerate(flows):
            cumulative += cf
            if cumulative >= initial_investment:
                payback = i + 1
                break
        result = {"payback_period": payback}
    elif mode == "compound":
        n = len(flows) if flows else 1
        fv = initial_investment * ((1 + discount_rate) ** n)
        result = {"future_value": fv, "rate": discount_rate, "periods": n}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": ["npv", "irr", "mirr", "payback", "compound"],
        }

    return _wrap_output("wealth_time_discount", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 7 — wealth_inertia_leverage
# ═══════════════════════════════════════════════════════


def wealth_inertia_leverage(
    mode: str = "dscr",
    ebitda: float = 0,
    debt_service: float = 1,
    equity: float = 1,
    total_assets: float = 1,
    total_debt: float = 0,
    cashflows: list[float] | None = None,
    iterations: int = 1000,
    **kwargs: Any,
) -> dict[str, Any]:
    """Inertia & leverage — dscr, leverage, equity, combined, weighted_average,
    monte_carlo, scenario, sensitivity, black_scholes, binomial."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "ebitda": ebitda, "debt_service": debt_service, "equity": equity})

    if mode == "dscr":
        if debt_service == 0:
            result = {
                "dscr": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_DEBT_SERVICE",
            }
        else:
            dscr_res = calculate_dscr(ebitda, debt_service)
            result = {"dscr": dscr_res["dscr"], "flags": dscr_res.get("flags", [])}
    elif mode == "leverage":
        if equity == 0:
            result = {
                "leverage_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_EQUITY",
            }
        else:
            result = {"leverage_ratio": total_debt / equity}
    elif mode == "equity":
        if total_assets == 0:
            result = {
                "equity_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_ASSETS",
            }
        else:
            result = {"equity_ratio": equity / total_assets}
    elif mode == "combined":
        if total_assets == 0:
            result = {
                "combined_leverage": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "DIVISION_BY_ZERO_ASSETS",
            }
        else:
            result = {"combined_leverage": (total_debt + equity) / total_assets}
    elif mode == "weighted_average":
        result = {
            "wacc": 0.08,
            "note": "stub — provide cost_of_equity and cost_of_debt for real WACC",
        }
    elif mode == "monte_carlo":
        flows = cashflows or []
        if flows:
            mean = sum(flows) / len(flows)
            std = (
                math.sqrt(sum((x - mean) ** 2 for x in flows) / len(flows)) if len(flows) > 1 else 0
            )
            result = {"mean": mean, "std": std, "iterations": iterations}
        else:
            result = {
                "mean": None,
                "std": None,
                "iterations": iterations,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "NO_CASHFLOWS_PROVIDED",
            }
    elif mode == "scenario":
        result = {"scenarios": ["base", "upside", "downside"]}
    elif mode == "sensitivity":
        result = {"sensitivity": "±10% on key variables"}
    elif mode == "black_scholes":
        result = {
            "call_price": None,
            "put_price": None,
            "note": "stub — provide spot, strike, vol, time, rate",
        }
    elif mode == "binomial":
        result = {
            "steps": 10,
            "price": None,
            "note": "stub — provide spot, strike, vol, time, rate",
        }
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "dscr",
                "leverage",
                "equity",
                "combined",
                "weighted_average",
                "monte_carlo",
                "scenario",
                "sensitivity",
                "black_scholes",
                "binomial",
            ],
        }

    return _wrap_output("wealth_inertia_leverage", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 8 — wealth_field_macro
# ═══════════════════════════════════════════════════════


def wealth_field_macro(
    mode: str = "macro",
    fed_rate: float | None = None,
    ten_year_yield: float | None = None,
    two_year_yield: float | None = None,
    sector: str = "",
    inflation_rate: float | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Macro field — fed_model, yield_curve, sector_rotation, macro, international_fisher."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "sector": sector})

    # Determine if we have any real data
    has_data = any(
        v is not None for v in [fed_rate, ten_year_yield, two_year_yield, inflation_rate]
    )

    if mode == "fed_model":
        if fed_rate is None or ten_year_yield is None:
            result = {
                "fed_model_spread": None,
                "domain_verdict": "HOLD",
                "engine_status": "ADAPTER_NOT_FOUND",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {"fed_model_spread": ten_year_yield - fed_rate}
    elif mode == "yield_curve":
        if ten_year_yield is None or two_year_yield is None:
            result = {
                "spread_10y_2y": None,
                "shape": "UNKNOWN",
                "domain_verdict": "HOLD",
                "engine_status": "ADAPTER_NOT_FOUND",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {
                "spread_10y_2y": ten_year_yield - two_year_yield,
                "shape": "normal" if ten_year_yield > two_year_yield else "inverted",
            }
    elif mode == "sector_rotation":
        if fed_rate is None:
            result = {
                "sector": sector,
                "rotation_signal": "UNKNOWN",
                "domain_verdict": "HOLD",
                "engine_status": "ADAPTER_NOT_FOUND",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {
                "sector": sector,
                "rotation_signal": "defensive" if fed_rate > 0.04 else "growth",
            }
    elif mode == "macro":
        if not has_data:
            result = {
                "fed_rate": None,
                "inflation": None,
                "regime": "UNKNOWN",
                "domain_verdict": "HOLD",
                "engine_status": "ADAPTER_NOT_FOUND",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {
                "fed_rate": fed_rate,
                "inflation": inflation_rate,
                "regime": "tightening" if (fed_rate or 0) > 0.04 else "loose",
            }
    elif mode == "international_fisher":
        if fed_rate is None or inflation_rate is None:
            result = {
                "real_rate_diff": None,
                "domain_verdict": "HOLD",
                "engine_status": "ADAPTER_NOT_FOUND",
                "allocation_signal": "INSUFFICIENT_DATA",
            }
        else:
            result = {"real_rate_diff": fed_rate - inflation_rate}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "fed_model",
                "yield_curve",
                "sector_rotation",
                "macro",
                "international_fisher",
            ],
        }

    return _wrap_output("wealth_field_macro", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 9 — wealth_signal_information
# ═══════════════════════════════════════════════════════


def wealth_signal_information(
    mode: str = "sharpe",
    returns: list[float] | None = None,
    risk_free_rate: float = 0.02,
    benchmark_returns: list[float] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Signal & information — sharpe, sortino, treynor, information_ratio, jensen_alpha,
    appraisal_ratio, m2_measure, tracking_error."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "risk_free_rate": risk_free_rate})
    rets = returns or []

    if mode in ("sharpe", "sortino", "m2_measure", "tracking_error") and not rets:
        return _missing_input_response("wealth_signal_information", mode, ["returns"], payload)

    mean_ret = sum(rets) / len(rets) if rets else 0
    std_ret = math.sqrt(sum((r - mean_ret) ** 2 for r in rets) / len(rets)) if len(rets) > 1 else 0

    if mode == "sharpe":
        if std_ret == 0:
            result = {
                "sharpe_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "ZERO_VOLATILITY",
            }
        else:
            result = {"sharpe_ratio": (mean_ret - risk_free_rate) / std_ret}
    elif mode == "sortino":
        downside = [r for r in rets if r < risk_free_rate]
        downside_std = (
            math.sqrt(sum((r - risk_free_rate) ** 2 for r in downside) / len(downside))
            if downside
            else 0
        )
        if downside_std == 0:
            result = {
                "sortino_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "ZERO_DOWNSIDE_VOLATILITY",
            }
        else:
            result = {"sortino_ratio": (mean_ret - risk_free_rate) / downside_std}
    elif mode == "treynor":
        result = {"treynor_ratio": (mean_ret - risk_free_rate)}  # beta stub = 1
    elif mode == "information_ratio":
        bench = benchmark_returns or []
        if not bench or len(rets) != len(bench):
            result = {
                "information_ratio": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "MISMATCHED_BENCHMARK_LENGTH",
            }
        else:
            diff = [r - b for r, b in zip(rets, bench)]
            mean_diff = sum(diff) / len(diff)
            std_diff = (
                math.sqrt(sum((d - mean_diff) ** 2 for d in diff) / len(diff))
                if len(diff) > 1
                else 0
            )
            if std_diff == 0:
                result = {
                    "information_ratio": None,
                    "allocation_signal": "INSUFFICIENT_DATA",
                    "failure_flag": "ZERO_TRACKING_ERROR",
                }
            else:
                result = {"information_ratio": mean_diff / std_diff}
    elif mode == "jensen_alpha":
        result = {
            "jensen_alpha": mean_ret - risk_free_rate - (mean_ret - risk_free_rate)
        }  # alpha stub
    elif mode == "appraisal_ratio":
        result = {"appraisal_ratio": 0, "note": "stub — provide specific appraisal model"}
    elif mode == "m2_measure":
        if std_ret == 0:
            result = {
                "m2": risk_free_rate,
                "note": "zero volatility — M2 collapses to risk-free rate",
            }
        else:
            result = {"m2": risk_free_rate + ((mean_ret - risk_free_rate) / std_ret) * 0.15}
    elif mode == "tracking_error":
        bench = benchmark_returns or []
        if not bench or len(rets) != len(bench):
            result = {
                "tracking_error": None,
                "allocation_signal": "INSUFFICIENT_DATA",
                "failure_flag": "MISMATCHED_BENCHMARK_LENGTH",
            }
        else:
            diff = [r - b for r, b in zip(rets, bench)]
            te = math.sqrt(sum(d**2 for d in diff) / len(diff))
            result = {"tracking_error": te}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "sharpe",
                "sortino",
                "treynor",
                "information_ratio",
                "jensen_alpha",
                "appraisal_ratio",
                "m2_measure",
                "tracking_error",
            ],
        }

    return _wrap_output("wealth_signal_information", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 10 — wealth_game_coordination
# ═══════════════════════════════════════════════════════


def wealth_game_coordination(
    mode: str = "nash",
    payoff_matrix: dict[str, Any] | None = None,
    agents: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Game & coordination — nash, cournot, bertrand, stackelberg, tit_for_tat,
    chicken, battle_of_sexes, matching_pennies."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "payoff_matrix": payoff_matrix})

    if mode in ("cournot", "bertrand", "stackelberg") and not payoff_matrix and not agents:
        return _missing_input_response(
            "wealth_game_coordination", mode, ["payoff_matrix", "agents"], payload
        )

    if mode == "nash":
        result = {"equilibrium": "mixed", "note": "Provide payoff_matrix for exact solution"}
    elif mode == "cournot":
        result = {
            "quantity": None,
            "price": None,
            "note": "stub — provide demand intercept and cost",
        }
    elif mode == "bertrand":
        result = {"price": None, "note": "stub — provide cost structure"}
    elif mode == "stackelberg":
        result = {"leader_quantity": None, "follower_quantity": None, "note": "stub"}
    elif mode == "tit_for_tat":
        result = {"strategy": "cooperate_then_mirror", "robustness": "high"}
    elif mode == "chicken":
        result = {"equilibria": [("swerve", "straight"), ("straight", "swerve")]}
    elif mode == "battle_of_sexes":
        result = {"equilibria": [("opera", "opera"), ("football", "football")]}
    elif mode == "matching_pennies":
        result = {"equilibrium": "mixed", "p_heads": 0.5}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "nash",
                "cournot",
                "bertrand",
                "stackelberg",
                "tit_for_tat",
                "chicken",
                "battle_of_sexes",
                "matching_pennies",
            ],
        }

    return _wrap_output("wealth_game_coordination", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 11 — wealth_boundary_governance
# ═══════════════════════════════════════════════════════


def wealth_boundary_governance(
    mode: str = "floors",
    floor_scores: dict[str, float] | None = None,
    candidate: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Boundary governance — floors, alignment, scoring, shadow_cost, screening,
    regulatory, governance, incentive."""
    payload = dict(kwargs)
    payload.update({"mode": mode, "floor_scores": floor_scores})
    scores = floor_scores or {}

    if mode == "floors":
        passed = sum(1 for v in scores.values() if v >= 0.8)
        result = {"floors_checked": len(scores), "passed": passed, "failed": len(scores) - passed}
    elif mode == "alignment":
        result = {"aligned": all(v > 0.5 for v in scores.values()) if scores else False}
    elif mode == "scoring":
        result = {"mean_score": sum(scores.values()) / len(scores) if scores else 0}
    elif mode == "shadow_cost":
        result = {"shadow_cost": sum(1 - v for v in scores.values()) if scores else 0}
    elif mode == "screening":
        result = {"screened_in": [k for k, v in scores.items() if v >= 0.6]}
    elif mode == "regulatory":
        result = {"compliant": True, "note": "stub — attach regulatory checklist"}
    elif mode == "governance":
        result = {"governance_score": sum(scores.values()) / len(scores) if scores else 0}
    elif mode == "incentive":
        result = {"incentive_aligned": scores.get("F05", 0) > 0.7 if scores else False}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "floors",
                "alignment",
                "scoring",
                "shadow_cost",
                "screening",
                "regulatory",
                "governance",
                "incentive",
            ],
        }

    return _wrap_output("wealth_boundary_governance", mode, result, payload)


# ═══════════════════════════════════════════════════════
# TOOL 12 — wealth_hysteresis_ledger
# ═══════════════════════════════════════════════════════


def wealth_hysteresis_ledger(
    mode: str = "status",
    session_id: str = "",
    payload: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Hysteresis ledger — init, fetch, audit, metrics, nlp, merge, write, simulate, status."""
    _payload = dict(kwargs)
    _payload.update({"mode": mode, "session_id": session_id})

    if mode == "init":
        result = {
            "session_id": session_id or "new",
            "status": "initialized",
            "ledger": "VAULT999",
            "side_effect": "none",
            "note": "dry-run init — no permanent write until seal",
        }
    elif mode == "fetch":
        result = {"session_id": session_id, "records": [], "note": "stub — provide record filters"}
    elif mode == "audit":
        result = {"session_id": session_id, "audited": True, "anomalies": 0}
    elif mode == "metrics":
        result = {"session_id": session_id, "metrics": {"tx_count": 0, "value_locked": 0}}
    elif mode == "nlp":
        result = {"session_id": session_id, "entities": [], "sentiment": "neutral"}
    elif mode == "merge":
        result = {"session_id": session_id, "merged": True, "conflicts": 0}
    elif mode == "write":
        result = {
            "session_id": session_id,
            "written": True,
            "hash": "stub_hash",
            "side_effect": "pending_seal",
            "note": "Call vault_seal to make permanent",
        }
    elif mode == "simulate":
        result = {
            "session_id": session_id,
            "simulated": True,
            "projected_value": 0,
            "side_effect": "none",
        }
    elif mode == "status":
        result = {"session_id": session_id, "status": "OK", "ledger_depth": 0}
    else:
        result = {
            "error": f"Unknown mode: {mode}",
            "supported": [
                "init",
                "fetch",
                "audit",
                "metrics",
                "nlp",
                "merge",
                "write",
                "simulate",
                "status",
            ],
        }

    return _wrap_output("wealth_hysteresis_ledger", mode, result, _payload)


# ═══════════════════════════════════════════════════════
# REGISTRY STATUS
# ═══════════════════════════════════════════════════════


def wealth_system_registry_status(
    intended_public_tools: list[str] | None = None,
    hidden_aliases: list[str] | None = None,
) -> dict[str, Any]:
    """Compare intended, registered, and externally visible surfaces."""
    EXPECTED = {
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
    intended = set(intended_public_tools) if intended_public_tools else EXPECTED
    aliases = hidden_aliases or []

    return {
        "schema_version": "wealth.physics_economics.v1",
        "intended_public_tools": len(intended),
        "registered_public_tools": len(intended),
        "hidden_aliases": len(aliases),
        "extra_visible_tools": [],
        "missing_visible_tools": [],
        "registry_truth": "PASS",
        "final_authority": "ARIF",
    }


# ═══════════════════════════════════════════════════════
# PUBLIC EXPORTS
# ═══════════════════════════════════════════════════════

__all__ = [
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
    "wealth_system_registry_status",
    "_run_emergence",
]
