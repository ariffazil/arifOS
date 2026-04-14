"""
arifosmcp/runtime/hardened_kernel.py — Hardened Kernel Entry Point (Next Horizon)

This module implements the canonical "Clean Rebuild" of the arifOS kernel:
1.  Fail-Closed Tool Dispatch: Zero identity loopholes.
2.  Data-Driven Philosophical Atlas: S × G × Ω coordinate-based character.
3.  Law Capsule Guards: Pre-execution constitutional verification.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import logging
from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope, Stage, Verdict
from arifosmcp.runtime.tools_hardened_dispatch import dispatch_with_fail_closed
from arifosmcp.runtime.philosophy import select_atlas_philosophy, AtlasScores
from arifosmcp.runtime.continuity_contract import seal_runtime_envelope

logger = logging.getLogger(__name__)

async def kernel_metabolic_execute(
    tool_name: str,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """
    Unified entry point for tool execution with fail-closed security and 
    philosophical grounding.
    """
    session_id = kwargs.get("session_id")
    
    # 1. FAIL-CLOSED DISPATCH (Gem 1)
    # This enforces identity gates and schema validation.
    result = await dispatch_with_fail_closed(tool_name, kwargs)
    
    # Check if we were fail-closed (VOID result)
    if result.get("fail_closed") or result.get("verdict") == "VOID":
        return result

    # 2. PHILOSOPHICAL GROUNDING (Gem 2)
    # Inject character and stance based on the metabolic metrics of the result.
    try:
        # Extract metrics from result if available (g_star, delta_s, omega_score)
        # Note: If result is a dict, we look into its payload
        payload = result.get("payload", {}) if isinstance(result, dict) else {}
        
        # Approximate score inputs for this horizon
        scores = AtlasScores(
            delta_s=float(result.get("delta_s", payload.get("delta_s", -0.01))),
            g_score=float(result.get("g_score", payload.get("truth_score", 0.85))),
            omega_score=float(result.get("omega_score", payload.get("confidence", 0.04))),
            lyapunov_sign="stable",
            verdict=result.get("verdict", "SABAR"),
            session_stage=str(result.get("stage", "444_KERNEL")),
        )
        
        phi = select_atlas_philosophy(scores, session_id=session_id)
        
        # Inject philosophy into result
        if isinstance(result, dict):
            # If result already has a philosophy field, we might override it
            result["philosophy"] = phi
            
            # Surface the quote in the detail/hint for the human
            primary_quote = phi.get("primary_quote", {})
            quote_text = primary_quote.get("quote", "")
            if quote_text:
                current_detail = result.get("detail", "")
                if current_detail:
                    result["detail"] = f"{current_detail}\n\n\"{quote_text}\" — {primary_quote.get('author')}"
                else:
                    result["detail"] = f"\"{quote_text}\" — {primary_quote.get('author')}"
                    
    except Exception as e:
        logger.warning(f"Hardened Kernel: Philosophy injection failed: {e}")

    return result


def is_side_effect_tool(tool_name: str) -> bool:
    """Check if tool has side effects requiring ratification."""
    side_effects = {"arifos_forge", "arifos_vault", "arifos_repo_seal"}
    return tool_name in side_effects
