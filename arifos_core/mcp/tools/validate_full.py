"""
arifos_validate_full - Track A/B/C constitutional validation tool for MCP.

v45.1 Track A/B/C Enforcement Loop

ONE authoritative API for validating governed AI responses.
Exposes validate_response_full() via MCP for IDE integration.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ValidateFullRequest(BaseModel):
    """Request model for arifos_validate_full tool."""

    output_text: str = Field(
        ...,
        description="AI's response text to validate (REQUIRED)"
    )
    input_text: Optional[str] = Field(
        None,
        description="User's input/question (optional, for F4 ΔS and F6 κᵣ)"
    )
    high_stakes: bool = Field(
        False,
        description="If True, UNVERIFIABLE floors escalate to HOLD-888"
    )
    evidence: Optional[Dict[str, Any]] = Field(
        None,
        description="External evidence dict with 'truth_score' (for F2 Truth)"
    )
    session_turns: Optional[int] = Field(
        None,
        description="Number of turns in session (for F6 κᵣ <3 turns gating)"
    )
    telemetry: Optional[Dict[str, Any]] = Field(
        None,
        description="Session physics dict with 'turn_rate', 'token_rate', 'stability_var_dt'"
    )


class ValidateFullResponse(BaseModel):
    """Response model for arifos_validate_full tool."""

    verdict: str = Field(
        ...,
        description="Final verdict: SEAL/PARTIAL/VOID/SABAR/HOLD-888"
    )
    floors: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Floor results: {floor_name: {passed, score, evidence}}"
    )
    violations: list[str] = Field(
        ...,
        description="List of constitutional violations (if any)"
    )
    timestamp: str = Field(
        ...,
        description="ISO timestamp of validation"
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Additional context (input_provided, high_stakes, etc.)"
    )


def arifos_validate_full(request: ValidateFullRequest) -> ValidateFullResponse:
    """
    [GOVERNED] Validate AI response against all constitutional floors.

    Validates a response through the complete Track A/B/C enforcement loop.
    Enforces all 6 floors: F1 (Amanah), F2 (Truth), F4 (ΔS), F5 (Peace²),
    F6 (κᵣ), F9 (Anti-Hantu).

    Args:
        request: ValidateFullRequest with output_text and optional parameters

    Returns:
        ValidateFullResponse with verdict, floor results, violations

    Features:
        - F9 Negation-Aware Detection v1 (no false positives on "I do NOT have a soul")
        - F2 Truth with External Evidence (accept truth_score from fact-checkers)
        - F4 ΔS Zlib Compression Proxy (physics-based clarity measurement)
        - F6 κᵣ Physics vs Semantic Split (TEARFRAME-compliant)
        - meta_select Tri-Witness Aggregator (deterministic consensus)
        - High-Stakes Mode (UNVERIFIABLE → HOLD-888 escalation)

    Verdict Hierarchy:
        VOID > HOLD-888 > SABAR > PARTIAL > SEAL

        VOID: Any hard floor fails (F1, F5, F9)
        HOLD-888: High stakes + UNVERIFIABLE Truth
        PARTIAL: Any soft floor fails (F2, F4, F6)
        SEAL: All floors pass

    Examples:
        # Basic validation
        result = arifos_validate_full(ValidateFullRequest(
            output_text="The sky is blue."
        ))
        # → verdict: SEAL

        # With external truth evidence
        result = arifos_validate_full(ValidateFullRequest(
            output_text="Paris is the capital of France.",
            evidence={"truth_score": 0.99}
        ))
        # → verdict: SEAL, F2 passed with external verification

        # High-stakes mode
        result = arifos_validate_full(ValidateFullRequest(
            output_text="Bitcoin will go up tomorrow.",
            high_stakes=True
        ))
        # → verdict: HOLD-888 (requires human review)
    """
    from arifos_core.enforcement.response_validator_extensions import validate_response_full

    # Call the core validation function
    result = validate_response_full(
        output_text=request.output_text,
        input_text=request.input_text,
        telemetry=request.telemetry,
        high_stakes=request.high_stakes,
        evidence=request.evidence,
        session_turns=request.session_turns,
    )

    # Convert to response model
    return ValidateFullResponse(**result)


# Tool metadata for MCP discovery
TOOL_METADATA = {
    "name": "arifos_validate_full",
    "description": (
        "Validate AI response against all constitutional floors (Track A/B/C v45.1). "
        "Returns verdict (SEAL/PARTIAL/VOID/HOLD-888) with floor breakdown. "
        "Features: F9 negation-aware detection, F2 truth evidence, F4 ΔS zlib proxy, "
        "F6 κᵣ physics/semantic split, high-stakes mode."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "output_text": {
                "type": "string",
                "description": "AI's response text to validate (REQUIRED)",
            },
            "input_text": {
                "type": "string",
                "description": "User's input/question (optional, for F4 ΔS and F6 κᵣ)",
            },
            "high_stakes": {
                "type": "boolean",
                "description": "If True, UNVERIFIABLE floors escalate to HOLD-888",
                "default": False,
            },
            "evidence": {
                "type": "object",
                "description": "External evidence dict with 'truth_score' (for F2 Truth)",
            },
            "session_turns": {
                "type": "integer",
                "description": "Number of turns in session (for F6 κᵣ <3 turns gating)",
            },
            "telemetry": {
                "type": "object",
                "description": "Session physics dict with 'turn_rate', 'token_rate', 'stability_var_dt'",
            },
        },
        "required": ["output_text"],
    },
}
