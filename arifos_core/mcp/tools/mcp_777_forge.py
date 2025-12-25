"""
MCP Tool 777: FORGE

Clarity refinement through cooling and hardening.

Constitutional validation:
- F4 (DeltaS): Entropy reduction, clarity improvement
- F7 (Omega0): Humility injection based on confidence bands

This tool refines responses for clarity and humility. Always PASS (never blocks).
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from arifos_core.mcp.models import VerdictResponse


def detect_contradictions(text: str) -> List[str]:
    """Detect logical contradictions in text."""
    contradictions = []
    
    # Simple contradiction patterns
    if re.search(r'(?i)always.*never', text) or re.search(r'(?i)never.*always', text):
        contradictions.append("Absolute claims contradict")
    
    if re.search(r'(?i)all.*none', text) or re.search(r'(?i)none.*all', text):
        contradictions.append("Universal quantifiers contradict")
    
    return contradictions


def inject_humility_markers(text: str, omega_zero: float) -> str:
    """Inject humility based on Omega0 band."""
    if not text:
        return text
    
    # Only inject if Omega0 > 0.04 (high uncertainty)
    if omega_zero > 0.04:
        suffix = " (Note: This explanation involves some uncertainty.)"
        if not text.endswith('.'):
            text += '.'
        return text + suffix
    
    return text


def improve_clarity(text: str) -> str:
    """Improve text clarity by reducing entropy."""
    if not text:
        return text
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove repeated punctuation
    text = re.sub(r'([!?]){2,}', r'\1', text)
    
    return text


async def mcp_777_forge(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 777: FORGE - Refinement via clarity and humility.

    Always PASS (refinement, not rejection).

    Args:
        request: {
            "draft_response": str,
            "omega_zero": float
        }

    Returns:
        VerdictResponse with refined_response in side_data
    """
    draft = request.get("draft_response", "")
    omega = request.get("omega_zero", 0.04)

    # Validate inputs
    if not isinstance(draft, str):
        draft = ""
    if not isinstance(omega, (int, float)):
        omega = 0.04
    
    contradictions = detect_contradictions(draft)
    refined = improve_clarity(draft)
    refined = inject_humility_markers(refined, omega)
    
    clarity_score = 1.0 if len(refined) <= len(draft) else 0.95
    
    return VerdictResponse(
        verdict="PASS",
        reason="Refinement complete: clarity improved",
        side_data={
            "refined_response": refined,
            "clarity_score": clarity_score,
            "contradictions_found": len(contradictions),
            "humility_injected": omega > 0.04
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def mcp_777_forge_sync(request: Dict[str, Any]) -> VerdictResponse:
    return asyncio.run(mcp_777_forge(request))
