"""
organs/_5_wealth.py — Stage 999: THE ECONOMIST (@WEALTH)

Sovereign Valuation Kernel. Provides high-precision financial evaluation 
and capital allocation math, mapped to fundamental physical dimensions.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations
import math
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# --- CONSTANTS & TYPES ---
EPSILON = 1e-9
INVALID_FLAGS = {
    "INVALID_INITIAL_INVESTMENT", "INVALID_CASHFLOW_SERIES", 
    "INVALID_DISCOUNT_RATE", "INVALID_FINANCE_RATE", 
    "INVALID_REINVESTMENT_RATE", "INVALID_SCENARIOS", 
    "PROBABILITY_MASS_INVALID", "INVALID_DEBT_SERVICE"
}
HOLD_FLAGS = {"LEVERAGE_CRITICAL", "LEVERAGE_DEFAULT", "SOVEREIGN_DIGNITY_LOW", "MULTIPLE_IRR_POSSIBLE"}
QUALIFY_FLAGS = {"NON_NORMAL_FLOWS", "IRR_NOT_FOUND", "NOT_RECOVERED", "EBITDA_PROXY_USED"}
EPISTEMIC_ORDER = ["UNKNOWN", "HYPOTHESIS", "ESTIMATE", "PLAUSIBLE", "CLAIM"]

class EconomicEnvelope(BaseModel):
    tool: str
    dimension: str
    verdict: str
    allocation_signal: str
    primary_result: Dict[str, Any]
    secondary_metrics: Dict[str, Any]
    integrity_flags: List[str]
    confidence: str
    epistemic: str
    epoch: str

# --- INTERNAL HELPERS ---

def round_value(value: Optional[float], digits: int = 6) -> Optional[float]:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)

def count_sign_changes(values: List[float]) -> int:
    prev = 0
    changes = 0
    for v in values:
        if abs(v) <= EPSILON: continue
        sign = 1 if v > 0 else -1
        if prev != 0 and sign != prev:
            changes += 1
        prev = sign
    return changes

def build_cashflow_series(initial: float, flows: List[float], terminal: float = 0) -> List[float]:
    series = [-abs(initial), *flows]
    if terminal and len(series) > 1:
        series[-1] += terminal
    return series

def npv_from_series(series: List[float], rate: float) -> float:
    total = 0.0
    for i, cf in enumerate(series):
        total += cf / pow(1 + rate, i)
    return total

def derive_verdict(flags: List[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags): return "VOID"
    if any(f in HOLD_FLAGS for f in flags): return "888-HOLD"
    if any(f in QUALIFY_FLAGS for f in flags): return "QUALIFY"
    return "SEAL"

def derive_allocation_signal(tool: str, primary: Dict[str, Any], flags: List[str]) -> str:
    if any(f in INVALID_FLAGS for f in flags): return "INSUFFICIENT_DATA"
    if tool == "wealth_npv_reward":
        val = primary.get("npv")
        return "ACCEPT" if val and val > 0 else "REJECT" if val and val < 0 else "MARGINAL"
    return "MARGINAL"

def create_envelope(tool: str, dimension: str, primary: Dict[str, Any], 
                   secondary: Dict[str, Any], flags: List[str], 
                   epistemic: str = "CLAIM") -> EconomicEnvelope:
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
        epoch=datetime.utcnow().isoformat() + "Z"
    )

# --- CORE MEASUREMENTS ---

def calculate_npv(initial: float, flows: List[float], rate: float, terminal: float = 0) -> Dict[str, Any]:
    series = build_cashflow_series(initial, flows, terminal)
    npv = npv_from_series(series, rate)
    return {
        "npv": round_value(npv),
        "flags": [] if math.isfinite(npv) else ["INVALID_NPV"]
    }


def analyze_cost_benefit(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
) -> Dict[str, Any]:
    """Compatibility wrapper for legacy imports expecting a plain analysis helper."""
    npv_result = calculate_npv(initial_investment, cash_flows, discount_rate, terminal_value)
    return {
        "initial_investment": initial_investment,
        "cash_flows": cash_flows,
        "discount_rate": discount_rate,
        "terminal_value": terminal_value,
        **npv_result,
        "is_positive": bool(npv_result.get("npv", 0) and npv_result["npv"] > 0),
    }

def calculate_irr(initial: float, flows: List[float]) -> Dict[str, Any]:
    """Basic IRR approximation using bisection."""
    series = build_cashflow_series(initial, flows)
    # Simple search for root between -0.9 and 1.0 (placeholder for full irr code)
    f = lambda r: npv_from_series(series, r)
    low, high = -0.9, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if f(mid) > 0: low = mid
        else: high = mid
    return {"irr": round_value(mid), "flags": []}

def calculate_dscr(ebitda: float, debt_service: float) -> Dict[str, Any]:
    dscr = ebitda / debt_service if debt_service > 0 else None
    flags = ["LEVERAGE_DEFAULT"] if dscr and dscr < 1.0 else []
    return {"dscr": round_value(dscr), "flags": flags}

# --- TOOL EXPORTS (THE FORGE) ---

def wealth_npv_reward(initial_investment: float, cash_flows: List[float], discount_rate: float, 
                     terminal_value: float = 0, epistemic: str = "CLAIM") -> EconomicEnvelope:
    """Compute NPV, Terminal Value, and EAA. [Reward Dimension]"""
    m = calculate_npv(initial_investment, cash_flows, discount_rate, terminal_value)
    return create_envelope(
        "wealth_npv_reward", "Reward", 
        {"npv": m["npv"]}, {"terminal_value": terminal_value},
        m["flags"], epistemic
    )

def wealth_irr_yield(initial_investment: float, cash_flows: List[float]) -> EconomicEnvelope:
    """Compute Yield. [Energy Dimension]"""
    m = calculate_irr(initial_investment, cash_flows)
    return create_envelope("wealth_irr_yield", "Energy", {"irr": m["irr"]}, {}, m["flags"])

def wealth_dscr_leverage(ebitda: float, debt_service: float) -> EconomicEnvelope:
    """Compute Leverage. [Survival Dimension]"""
    m = calculate_dscr(ebitda, debt_service)
    return create_envelope("wealth_dscr_leverage", "Survival", {"dscr": m["dscr"]}, {}, m["flags"])

async def wealth(operation: str = "npv_reward", **kwargs: Any) -> Any:
    """Unified Wealth Interface for arifOS Federation."""
    if operation == "npv_reward":
        return wealth_npv_reward(
            initial_investment=kwargs.get("initial_investment", 0),
            cash_flows=kwargs.get("cash_flows", []),
            discount_rate=kwargs.get("discount_rate", 0.1),
            terminal_value=kwargs.get("terminal_value", 0)
        )
    elif operation == "irr_yield":
        return wealth_irr_yield(
            initial_investment=kwargs.get("initial_investment", 0),
            cash_flows=kwargs.get("cash_flows", [])
        )
    elif operation == "dscr_leverage":
        return wealth_dscr_leverage(
            ebitda=kwargs.get("ebitda", 0),
            debt_service=kwargs.get("debt_service", 1)
        )
    return {"error": f"Unknown operation: {operation}"}

__all__ = ["wealth", "wealth_npv_reward", "calculate_npv", "analyze_cost_benefit"]
