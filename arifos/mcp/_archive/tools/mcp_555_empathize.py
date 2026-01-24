"""
MCP Tool 555: EMPATHIZE

Power-aware recalibration through Peace² and κᵣ (kappa recalibration).

Constitutional validation:
- F5 (Peace²): Detect aggression, dismissiveness, emotional harm
- F6 (κᵣ/Empathy): Power-aware recalibration for vulnerable stakeholders

This tool analyzes tone and power dynamics to ensure warm, contextual responses.
Returns PASS/PARTIAL based on peace score and empathy recalibration.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from arifos.core.enforcement.floor_validators import validate_f5_peace, validate_f6_empathy
from arifos.core.mcp.models import VerdictResponse

# =============================================================================
# MCP TOOL IMPLEMENTATION
# =============================================================================

async def mcp_555_empathize(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 555: EMPATHIZE - Power-aware recalibration.

    Constitutional role:
    - F5 (Peace²): Detects aggression, dismissal, harm
    - F6 (κᵣ): Power-aware recalibration

    Args:
        request: {
            "response_text": str,           # Response to analyze
            "recipient_context": dict,      # Audience/power context
        }

    Returns:
        VerdictResponse.
    """
    from arifos.core.asi.kernel import ASIActionCore

    # Extract inputs
    response_text = request.get("response_text", "")
    recipient_context = request.get("recipient_context", {})

    # Validate inputs
    if not isinstance(response_text, str):
        response_text = ""

    if not isinstance(recipient_context, dict):
        recipient_context = {}

    # 1. Canonical Floor Validation (Deep Logic)
    # F5 Peace Check
    # Context expects 'response' key for F3/F6, and F5 checks query usually but can check response
    # validate_f5_peace(query, context). In tool context, 'response_text' is the logic to check.
    # We treat 'response_text' as the query for the validator to check for destructive terms.
    f5_result = validate_f5_peace(response_text, context={"response": response_text})

    # F6 Empathy Check
    # validate_f6_empathy(query, context). It checks context.get("response") for keywords.
    f6_result = validate_f6_empathy("", context={
        "response": response_text,
        **recipient_context
    })

    peace_score = f5_result.get("score", 1.0)
    kappa_r = f6_result.get("score", 0.95)

    # 2. Call ASI Kernel (Simulation of Empathy Action)
    # The Kernel expects "text" and "context"
    # It returns a dict with "omega_verdict" (SEAL/PARTIAL/VOID)
    kernel_result = await ASIActionCore.empathize(
        text=response_text,
        context=recipient_context
    )

    omega_verdict = kernel_result.get("omega_verdict", "PARTIAL")
    vulnerability_score = kernel_result.get("vulnerability_score", 0.5)
    action = kernel_result.get("action", "Neutral")

    # Map to Tool Verdict
    # ASI uses SEAL/PARTIAL/VOID
    # Tool uses PASS/PARTIAL/VOID
    # We combine Kernel verdict with Validator results

    if not f5_result["pass"]:
        verdict = "VOID"
        reason = f"F5 Violation: {f5_result.get('reason')}"
    elif not f6_result["pass"]:
        verdict = "PARTIAL"
        reason = f"F6 Recalibration Needed: {f6_result.get('reason')}"
    else:
        # If validators pass, defer to Kernel's logic
        verdict = "PASS" if omega_verdict == "SEAL" else omega_verdict
        reason = f"ASI Empathy Action: {action} (Vuln: {vulnerability_score:.2f}, Verdict: {omega_verdict}, κᵣ: {kappa_r:.2f})"

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    return VerdictResponse(
        verdict=verdict,
        reason=reason,
        side_data={
            "peace_score": peace_score,
            "kappa_r": kappa_r,
            "f5_result": f5_result,
            "f6_result": f6_result,
            "asi_meta": kernel_result
        },
        timestamp=timestamp,
    )


def mcp_555_empathize_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_555_empathize."""
    return asyncio.run(mcp_555_empathize(request))
