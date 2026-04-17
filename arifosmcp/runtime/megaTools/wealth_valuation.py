"""
arifosmcp/runtime/megaTools/wealth_valuation.py — @WEALTH Implementation
═══════════════════════════════════════════════════════════════════════════════

Delegated handlers for context-aware financial valuation.
Connects the arifOS gateway to the WEALTH sovereign organ.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from core.organs._5_wealth import wealth_dscr_leverage, wealth_irr_yield, wealth_npv_reward

logger = logging.getLogger(__name__)

async def wealth_npv_reward_handler(
    initial_investment: float,
    cash_flows: list[float],
    discount_rate: float,
    terminal_value: float = 0,
    epistemic: str = "CLAIM",
    session_id: str | None = None
) -> dict[str, Any]:
    """Handler for wealth_npv_reward tool."""
    result = wealth_npv_reward(
        initial_investment=initial_investment,
        cash_flows=cash_flows,
        discount_rate=discount_rate,
        terminal_value=terminal_value,
        epistemic=epistemic
    )
    return result.model_dump()

async def wealth_irr_yield_handler(
    initial_investment: float,
    cash_flows: list[float],
    session_id: str | None = None
) -> dict[str, Any]:
    """Handler for wealth_irr_yield tool."""
    result = wealth_irr_yield(
        initial_investment=initial_investment,
        cash_flows=cash_flows
    )
    return result.model_dump()

async def wealth_dscr_leverage_handler(
    ebitda: float,
    debt_service: float,
    session_id: str | None = None
) -> dict[str, Any]:
    """Handler for wealth_dscr_leverage tool."""
    result = wealth_dscr_leverage(
        ebitda=ebitda,
        debt_service=debt_service
    )
    return result.model_dump()
