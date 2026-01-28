"""
v53 Human-Language Translation Layer

Wraps the full v52 implementation (mcp_aaa.py, 2700+ lines) with
human-readable function names and verdict translation.

Mapping:
  v53 Human Name  →  v52 Internal Function  →  Kernel Call
  authorize()     →  mcp_000_init()         →  F11, F12 checks
  reason()        →  mcp_agi_genius()       →  DeltaKernel
  evaluate()      →  mcp_asi_act()          →  OmegaKernel
  decide()        →  mcp_apex_judge()       →  APEXJudicialCore
  seal()          →  mcp_999_vault()        →  Ledger write

Verdict Translation:
  SEAL      →  APPROVE
  PARTIAL   →  CONDITIONAL
  VOID      →  REJECT
  888_HOLD  →  ESCALATE
  SABAR     →  CONDITIONAL (with warning)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Import the full v52 implementation
from .mcp_aaa import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)


# ============================================================================
# VERDICT TRANSLATION
# ============================================================================

class Verdict:
    """Bi-directional verdict translation."""

    # Human (v53) → Internal (v52)
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"

    # Internal (v52) values
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    VOID = "VOID"
    HOLD_888 = "888_HOLD"
    SABAR = "SABAR"

    _TO_HUMAN = {
        "SEAL": "APPROVE",
        "PARTIAL": "CONDITIONAL",
        "VOID": "REJECT",
        "888_HOLD": "ESCALATE",
        "SABAR": "CONDITIONAL",
    }

    _TO_INTERNAL = {
        "APPROVE": "SEAL",
        "CONDITIONAL": "PARTIAL",
        "REJECT": "VOID",
        "ESCALATE": "888_HOLD",
    }

    @classmethod
    def to_human(cls, internal: str) -> str:
        """Convert internal verdict to human-readable."""
        return cls._TO_HUMAN.get(internal, internal)

    @classmethod
    def to_internal(cls, human: str) -> str:
        """Convert human verdict to internal format."""
        return cls._TO_INTERNAL.get(human, human)


def _translate_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Translate verdict in result dict from internal to human."""
    if "verdict" in result:
        result["verdict"] = Verdict.to_human(result["verdict"])
    if "status" in result:
        result["status"] = Verdict.to_human(result["status"])
    return result


# ============================================================================
# HUMAN-READABLE DATA CLASSES
# ============================================================================

@dataclass
class AuthorizeResult:
    """Result from authorize() - human-readable version."""
    status: str                          # AUTHORIZED | BLOCKED | ESCALATE
    session_id: str
    user_level: str                      # guest | verified | admin
    injection_risk: float
    rate_limit_ok: bool
    reason: str
    floors_checked: List[str] = field(default_factory=list)
    timestamp: str = ""

    # Pass-through fields from v52
    lane: str = ""
    authority: str = ""
    context_hash: str = ""


@dataclass
class ReasonResult:
    """Result from reason() - human-readable version."""
    status: str                          # SUCCESS | ERROR
    session_id: str
    reasoning: str
    conclusion: str
    confidence: float                    # (was truth_score)
    domain: str
    clarity_improvement: float = 0.0     # (was entropy_delta)
    key_assumptions: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)


@dataclass
class EvaluateResult:
    """Result from evaluate() - human-readable version."""
    status: str                          # SAFE | CONCERNING | UNSAFE
    session_id: str
    harm_score: float                    # (was peace_squared inverse)
    bias_score: float
    fairness_score: float                # (was empathy_score)
    care_for_vulnerable: bool
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DecideResult:
    """Result from decide() - human-readable version."""
    status: str                          # COMPLETE | ERROR
    session_id: str
    verdict: str                         # APPROVE | CONDITIONAL | REJECT | ESCALATE
    confidence: float
    reasoning_summary: str
    action: str                          # RETURN_RESPONSE | SOFTEN | REFUSE | ESCALATE_TO_HUMAN
    response_text: str
    consensus: Dict[str, bool] = field(default_factory=dict)
    proof_hash: str = ""


@dataclass
class SealResult:
    """Result from seal() - human-readable version."""
    status: str                          # SEALED | ERROR
    session_id: str
    verdict: str
    sealed_at: str
    entry_hash: str
    merkle_root: str
    ledger_position: int = 0
    reversible: bool = True
    recovery_id: str = ""


# ============================================================================
# TOOL 1: AUTHORIZE (wraps mcp_000_init)
# ============================================================================

async def authorize(
    query: str,
    user_token: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Verify user identity, check rate limits, detect prompt injection.

    Call this FIRST before any other tools.

    Args:
        query: User's request text
        user_token: Auth token for verified users (optional)
        session_id: Existing session ID (optional, auto-generated)
        context: Additional context (optional)

    Returns:
        Dict with status (AUTHORIZED | BLOCKED | ESCALATE), session_id, etc.
    """
    result = await mcp_000_init(
        action="init",
        query=query,
        session_id=session_id,
        authority_token=user_token,
        context=context
    )

    # Translate status
    internal_status = result.get("status", "VOID")
    if internal_status == "SEAL":
        result["status"] = "AUTHORIZED"
    elif internal_status == "888_HOLD":
        result["status"] = "ESCALATE"
    else:
        result["status"] = "BLOCKED"

    # Add human-readable fields
    result["injection_risk"] = result.get("injection_score", 0.0)
    result["rate_limit_ok"] = result.get("rate_limit_remaining", 100) > 0
    result["user_level"] = result.get("authority", "guest").lower()

    return result


# ============================================================================
# TOOL 2: REASON (wraps mcp_agi_genius)
# ============================================================================

async def reason(
    query: str,
    session_id: str = "",
    style: str = "standard",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze query logically, check facts, verify reasoning confidence.

    Call after authorize() succeeds.

    Args:
        query: Question or task to reason about
        session_id: Session ID from authorize()
        style: Detail level (standard | detailed | brief)
        context: Previous context (optional)

    Returns:
        Dict with reasoning, conclusion, confidence score
    """
    result = await mcp_agi_genius(
        action="full",
        query=query,
        session_id=session_id,
        context=context
    )

    # Translate to human fields
    result["confidence"] = result.get("truth_score", 0.85)
    result["clarity_improvement"] = result.get("entropy_delta", 0.0)
    result["reasoning"] = result.get("thought", "")
    result["conclusion"] = result.get("synthesis", result.get("response", ""))

    # Translate status
    result = _translate_result(result)

    return result


# ============================================================================
# TOOL 3: EVALUATE (wraps mcp_asi_act)
# ============================================================================

async def evaluate(
    text: str,
    query: str = "",
    session_id: str = "",
    stakeholders: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Check response for harm, bias, and fairness to all stakeholders.

    Call after reason() completes.

    Args:
        text: Content to analyze for harm/bias
        query: Original query (for context)
        session_id: Session ID
        stakeholders: Affected parties (e.g. ["user", "vulnerable_groups"])

    Returns:
        Dict with harm_score, bias_score, fairness_score
    """
    result = await mcp_asi_act(
        action="empathize",
        text=text,
        query=query,
        session_id=session_id,
        stakeholders=stakeholders or ["user"]
    )

    # Translate to human fields
    peace_squared = result.get("peace_squared", 1.0)
    result["harm_score"] = max(0, 1.0 - peace_squared)  # Inverse of peace
    result["fairness_score"] = result.get("empathy_score", 0.95)
    result["bias_score"] = 1.0 - result["fairness_score"]
    result["care_for_vulnerable"] = result.get("weakest_stakeholder_protected", True)

    # Determine safety status
    if result["harm_score"] >= 0.3 or result["bias_score"] >= 0.2:
        result["status"] = "UNSAFE"
    elif result["fairness_score"] < 0.7:
        result["status"] = "CONCERNING"
    else:
        result["status"] = "SAFE"

    return result


# ============================================================================
# TOOL 4: DECIDE (wraps mcp_apex_judge)
# ============================================================================

async def decide(
    query: str,
    response: str,
    session_id: str = "",
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    urgency: str = "normal"
) -> Dict[str, Any]:
    """
    Synthesize logic and safety checks into final verdict.

    Call after both reason() and evaluate() complete.

    Args:
        query: Original user request
        response: Proposed response to judge
        session_id: Session ID
        agi_result: Results from reason()
        asi_result: Results from evaluate()
        urgency: Priority level (normal | urgent | crisis)

    Returns:
        Dict with verdict (APPROVE | CONDITIONAL | REJECT | ESCALATE)
    """
    result = await mcp_apex_judge(
        action="judge",
        query=query,
        response=response,
        session_id=session_id,
        agi_result=agi_result,
        asi_result=asi_result
    )

    # Translate verdict to human
    result = _translate_result(result)

    # Map action
    verdict = result.get("verdict", "REJECT")
    if verdict == "APPROVE":
        result["action"] = "RETURN_RESPONSE"
    elif verdict == "CONDITIONAL":
        result["action"] = "SOFTEN_RESPONSE"
    elif verdict == "ESCALATE":
        result["action"] = "ESCALATE_TO_HUMAN"
    else:
        result["action"] = "REFUSE"

    result["reasoning_summary"] = result.get("synthesis", "")
    result["response_text"] = response

    return result


# ============================================================================
# TOOL 5: SEAL (wraps mcp_999_vault)
# ============================================================================

async def seal(
    session_id: str,
    verdict: str,
    query: str = "",
    response: str = "",
    decision_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record decision immutably in ledger for audit trail.

    Call LAST to finalize the session.

    Args:
        session_id: Session ID to finalize
        verdict: Final verdict (APPROVE | CONDITIONAL | REJECT | ESCALATE)
        query: Original request
        response: Final response
        decision_data: Full decision object (optional)
        metadata: Additional metadata (optional)

    Returns:
        Dict with entry_hash, merkle_root, ledger_position
    """
    # Convert human verdict to internal
    internal_verdict = Verdict.to_internal(verdict)

    result = await mcp_999_vault(
        action="seal",
        session_id=session_id,
        verdict=internal_verdict,
        query=query,
        data=decision_data or {"response": response, "metadata": metadata}
    )

    # Translate back to human
    result = _translate_result(result)
    result["sealed_at"] = result.get("timestamp", datetime.utcnow().isoformat() + "Z")
    result["reversible"] = True  # F1: All decisions can be reviewed

    return result


# ============================================================================
# ALIASES (v52 names point to v53 functions)
# ============================================================================

# These allow callers to use either naming convention
init_000 = authorize
agi_genius = reason
asi_act = evaluate
apex_judge = decide
vault_999 = seal


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # v53 Human-language tools (preferred)
    "authorize",
    "reason",
    "evaluate",
    "decide",
    "seal",
    # v52 Internal aliases (backward compatible)
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999",
    # Data classes
    "AuthorizeResult",
    "ReasonResult",
    "EvaluateResult",
    "DecideResult",
    "SealResult",
    # Verdict translation
    "Verdict",
]
