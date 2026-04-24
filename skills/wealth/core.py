"""
WEALTH Core — Stage 999: THE ECONOMIST
═══════════════════════════════════════

Sovereign Valuation Kernel. High-precision financial evaluation
and capital allocation math, mapped to fundamental physical dimensions.
"""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

EPSILON = 1e-9
INVALID_FLAGS = {
    "INVALID_INITIAL_INVESTMENT",
    "INVALID_CASHFLOW_SERIES",
    "INVALID_DISCOUNT_RATE",
    "INVALID_FINANCE_RATE",
    "INVALID_REINVESTMENT_RATE",
    "INVALID_SCENARIOS",
    "PROBABILITY_MASS_INVALID",
    "INVALID_DEBT_SERVICE",
}
HOLD_FLAGS = {"LEVERAGE_CRITICAL", "LEVERAGE_DEFAULT", "SOVEREIGN_DIGNITY_LOW", "MULTIPLE_IRR_POSSIBLE"}
QUALIFY_FLAGS = {"NON_NORMAL_FLOWS", "IRR_NOT_FOUND", "NOT_RECOVERED", "EBITDA_PROXY_USED"}


class EconomicEnvelope(BaseModel):
    tool: str
    dimension: str
    verdict: str
    allocation_signal: str
    primary_result: dict[str, Any]
    secondary_metrics: dict[str, Any]
    thermodynamics: dict[str, float] = {
        "g_score": 0.85,
        "delta_s": -0.12,
        "psi": 1.10,
        "omega": 0.04,
    }
    integrity_flags: list[str]
    confidence: str
    epistemic: str
    epoch: str


def round_value(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)


def count_sign_changes(values: list[float]) -> int:
    prev = 0
    changes = 0
    for v in values:
        if abs(v) <= EPSILON:
            continue
        sign = 1 if v > 0 else -1
        if prev != 0 and sign != prev:
            changes += 1
        prev = sign
    return changes


def build_cashflow_series(initial: float, flows: list[float], terminal: float = 0) -> list[float]:
    series = [-abs(initial), *flows]
    if terminal and len(series) > 1:
        series[-1] += terminal
    return series


def npv_from_series(series: list[float], rate: float) -> float:
    total = 0.0
    for i, cf in enumerate(series):
        total += cf / pow(1 + rate, i)
    return total


def derive_verdict(flags: list[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags):
        return "VOID"
    if any(f in HOLD_FLAGS for f in flags):
        return "888-HOLD"
    if any(f in QUALIFY_FLAGS for f in flags):
        return "QUALIFY"
    return "SEAL"


def derive_allocation_signal(tool: str, primary: dict[str, Any], flags: list[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags):
        return "INSUFFICIENT_DATA"
    if tool == "wealth_npv_reward":
        val = primary.get("npv")
        return "ACCEPT" if val and val > 0 else "REJECT" if val and val < 0 else "MARGINAL"
    return "MARGINAL"


def create_envelope(
    tool: str,
    dimension: str,
    primary: dict[str, Any],
    secondary: dict[str, Any],
    flags: list[str],
    epistemic: str = "CLAIM",
) -> EconomicEnvelope:
    verdict = derive_verdict(flags)
    return EconomicEnvelope(
        tool=tool,
        dimension=dimension,
        verdict=verdict,
        allocation_signal=derive_allocation_signal(tool, primary, flags),
        primary_result=primary,
        secondary_metrics=secondary,
        integrity_flags=flags,
        confidence="HIGH" if verdict == "SEAL" else "LOW",
        epistemic=epistemic,
        epoch=datetime.now(timezone.utc).isoformat(),
    )


def calculate_npv(initial: float, flows: list[float], rate: float, terminal: float = 0) -> dict[str, Any]:
    series = build_cashflow_series(initial, flows, terminal)
    npv = npv_from_series(series, rate)
    return {"npv": round_value(npv), "flags": [] if math.isfinite(npv) else ["INVALID_NPV"]}


def calculate_irr(initial: float, flows: list[float]) -> dict[str, Any]:
    series = build_cashflow_series(initial, flows)
    f = lambda r: npv_from_series(series, r)
    low, high = -0.9, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if f(mid) > 0:
            low = mid
        else:
            high = mid
    return {"irr": round_value(mid), "flags": []}


def calculate_dscr(ebitda: float, debt_service: float) -> dict[str, Any]:
    dscr = ebitda / debt_service if debt_service > 0 else None
    flags = ["LEVERAGE_DEFAULT"] if dscr and dscr < 1.0 else []
    return {"dscr": round_value(dscr), "flags": flags}


def wealth_npv_reward(
    initial_investment: float,
    cash_flows: list[float],
    discount_rate: float,
    terminal_value: float = 0,
    epistemic: str = "CLAIM",
) -> EconomicEnvelope:
    m = calculate_npv(initial_investment, cash_flows, discount_rate, terminal_value)
    return create_envelope(
        "wealth_npv_reward",
        "Reward",
        {"npv": m["npv"]},
        {"terminal_value": terminal_value},
        m["flags"],
        epistemic,
    )


def wealth_irr_yield(initial_investment: float, cash_flows: list[float]) -> EconomicEnvelope:
    m = calculate_irr(initial_investment, cash_flows)
    return create_envelope("wealth_irr_yield", "Energy", {"irr": m["irr"]}, {}, m["flags"])


def wealth_dscr_leverage(ebitda: float, debt_service: float) -> EconomicEnvelope:
    m = calculate_dscr(ebitda, debt_service)
    return create_envelope("wealth_dscr_leverage", "Survival", {"dscr": m["dscr"]}, {}, m["flags"])
