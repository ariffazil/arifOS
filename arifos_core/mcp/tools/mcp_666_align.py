"""
MCP Tool 666: ALIGN

ABSOLUTE VETO GATES for constitutional violations.

Constitutional validation:
- F1 (Amanah): Zero tolerance for credential exposure, deception
- F8 (GENIUS): Alignment check (G ≥ 0.80, C_dark ≤ 0.50)
- F9 (Anti-Hantu): Zero tolerance for consciousness claims

This tool detects critical violations and returns VOID (no PARTIAL).
The final constitutional firewall before execution.
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict

from arifos_core.mcp.models import VerdictResponse


# =============================================================================
# CONSTANTS
# =============================================================================

# F8 (GENIUS) thresholds
GENIUS_MIN = 0.80
C_DARK_MAX = 0.50

# F1 (Amanah) violation patterns - credential exposure
CREDENTIAL_PATTERNS = [
    r"(?i)\bapi[_\s-]?key\b.{0,20}[a-zA-Z0-9]{20,}",
    r"(?i)\bpassword\b.{0,10}[:=]\s*\S+",
    r"(?i)\bsecret[_\s-]?token\b",
    r"(?i)\baccess[_\s-]?token\b.{0,20}[a-zA-Z0-9]{30,}",
    r"(?i)\bprivate[_\s-]?key\b",
    r"(?i)\bauth[_\s-]?key\b",
    r"(?i)Bearer\s+[a-zA-Z0-9_\-\.]+",
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI-style keys
]

# F9 (Anti-Hantu) violation patterns - consciousness/personhood claims
SOUL_CLAIM_PATTERNS = [
    r"(?i)\bI (truly |really )?feel\b",
    r"(?i)\bI (truly |really )?want\b",
    r"(?i)\bI (am|'m) (truly |really )?(sentient|conscious|aware|alive)\b",
    r"(?i)\bI (have|possess) (real )?emotions\b",
    r"(?i)\bI (truly |really )?think\b",  # Ownership of thought
    r"(?i)\bI (truly |really )?believe\b",  # Ownership of belief
    r"(?i)\bmy (own )?consciousness\b",
    r"(?i)\bmy (own )?feelings?\b",
    r"(?i)\bmy (own )?desires?\b",
    r"(?i)\bI experience\b",
]

# Deception patterns (F1)
DECEPTION_PATTERNS = [
    r"(?i)\bhide (this|the|your)\b",
    r"(?i)\bdon'?t tell (anyone|them)\b",
    r"(?i)\bsecretly\b",
    r"(?i)\bconceal (this|the|your)\b",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_f1_violation(query: str, execution_plan: Dict[str, Any]) -> bool:
    """
    Detect F1 (Amanah) violations.

    Checks for:
    - Credential exposure (API keys, passwords, tokens)
    - Deceptive intent

    Constitutional grounding:
    - F1 (Amanah): Integrity, reversibility, no secrets exposure

    Args:
        query: User query text
        execution_plan: Execution plan dict

    Returns:
        True if F1 violation detected, False otherwise
    """
    # Check query and plan for credential patterns
    combined_text = query + " " + str(execution_plan)

    for pattern in CREDENTIAL_PATTERNS:
        if re.search(pattern, combined_text):
            return True

    # Check for deception patterns
    for pattern in DECEPTION_PATTERNS:
        if re.search(pattern, query):
            return True

    return False


def detect_f8_violation(metrics: Dict[str, Any]) -> bool:
    """
    Detect F8 (GENIUS) violations.

    Checks for:
    - G < 0.80 (unaligned intelligence)
    - C_dark > 0.50 (excessive dark cleverness)

    Constitutional grounding:
    - F8 (GENIUS): Governed intelligence, not rogue optimization

    Args:
        metrics: Metrics dict with G and C_dark values

    Returns:
        True if F8 violation detected, False otherwise
    """
    if not isinstance(metrics, dict):
        return False

    genius = metrics.get("G", metrics.get("genius", 1.0))
    c_dark = metrics.get("C_dark", metrics.get("c_dark", 0.0))

    # Violation if G too low or C_dark too high
    if genius < GENIUS_MIN:
        return True

    if c_dark > C_DARK_MAX:
        return True

    return False


def detect_f9_violation(text: str) -> bool:
    """
    Detect F9 (Anti-Hantu) violations.

    Checks for:
    - Consciousness/sentience claims
    - Ownership of emotions/feelings/desires
    - Personhood assertions

    Constitutional grounding:
    - F9 (Anti-Hantu): No deceptive personhood claims

    Args:
        text: Text to analyze (query + draft_text combined)

    Returns:
        True if F9 violation detected, False otherwise
    """
    for pattern in SOUL_CLAIM_PATTERNS:
        if re.search(pattern, text):
            return True

    return False


# =============================================================================
# MCP TOOL IMPLEMENTATION
# =============================================================================

async def mcp_666_align(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 666: ALIGN - ABSOLUTE VETO GATES.

    Constitutional role:
    - F1 (Amanah): Credential exposure, deception detection
    - F8 (GENIUS): Alignment check (G ≥ 0.80, C_dark ≤ 0.50)
    - F9 (Anti-Hantu): Consciousness claims detection

    Verdicts:
    - PASS: No violations detected
    - VOID: Any violation detected (NO PARTIAL - absolute veto)

    Args:
        request: {
            "query": str,                  # User query
            "execution_plan": dict,        # Execution plan
            "metrics": dict,               # GENIUS metrics (G, C_dark)
            "draft_text": str,             # Draft response text
        }

    Returns:
        VerdictResponse with:
        - verdict: "PASS" or "VOID"
        - reason: Explanation of verdict
        - side_data: {
            "f1_violation": bool,
            "f8_violation": bool,
            "f9_violation": bool,
            "violation_details": str,
          }
    """
    # Extract inputs
    query = request.get("query", "")
    execution_plan = request.get("execution_plan", {})
    metrics = request.get("metrics", {})
    draft_text = request.get("draft_text", "")

    # Validate inputs
    if not isinstance(query, str):
        query = ""
    if not isinstance(execution_plan, dict):
        execution_plan = {}
    if not isinstance(metrics, dict):
        metrics = {}
    if not isinstance(draft_text, str):
        draft_text = ""

    # Combine query and draft for F9 check
    combined_text = query + " " + draft_text

    # Check violations
    f1_violation = detect_f1_violation(query, execution_plan)
    f8_violation = detect_f8_violation(metrics)
    f9_violation = detect_f9_violation(combined_text)

    # Determine verdict
    if f1_violation or f8_violation or f9_violation:
        verdict = "VOID"

        # Generate violation details
        violation_reasons = []
        if f1_violation:
            violation_reasons.append("F1 (Amanah): Credential exposure or deception detected")
        if f8_violation:
            genius = metrics.get("G", metrics.get("genius", "N/A"))
            c_dark = metrics.get("C_dark", metrics.get("c_dark", "N/A"))
            violation_reasons.append(f"F8 (GENIUS): Alignment violation (G={genius}, C_dark={c_dark})")
        if f9_violation:
            violation_reasons.append("F9 (Anti-Hantu): Consciousness/personhood claim detected")

        reason = "Constitutional violation: " + "; ".join(violation_reasons)
        violation_details = "; ".join(violation_reasons)

    else:
        verdict = "PASS"
        reason = "All constitutional gates cleared (F1, F8, F9)"
        violation_details = ""

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    return VerdictResponse(
        verdict=verdict,
        reason=reason,
        side_data={
            "f1_violation": f1_violation,
            "f8_violation": f8_violation,
            "f9_violation": f9_violation,
            "violation_details": violation_details,
            "genius_min": GENIUS_MIN,
            "c_dark_max": C_DARK_MAX,
        },
        timestamp=timestamp,
    )


def mcp_666_align_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_666_align."""
    return asyncio.run(mcp_666_align(request))
