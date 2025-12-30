"""
arifos_meta_select - Tri-Witness consensus aggregator tool for MCP.

v45.1 Track A/B/C Enforcement Loop

Deterministic consensus algorithm for combining multiple witness verdicts.
Exposes meta_select() via MCP for IDE integration.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class MetaSelectRequest(BaseModel):
    """Request model for arifos_meta_select tool."""

    verdicts: List[Dict[str, Any]] = Field(
        ...,
        description="List of verdict dicts from witnesses (REQUIRED). Each dict must contain: 'source' (str), 'verdict' (str: SEAL/PARTIAL/VOID/SABAR/HOLD-888), 'confidence' (float: 0.0-1.0)"
    )
    consensus_threshold: float = Field(
        0.95,
        description="Minimum agreement rate for SEAL (default 0.95). If consensus < threshold, returns HOLD-888",
        ge=0.0,
        le=1.0
    )


class MetaSelectResponse(BaseModel):
    """Response model for arifos_meta_select tool."""

    winner: str = Field(
        ...,
        description="Winning verdict by plurality (SEAL/PARTIAL/VOID/SABAR/HOLD-888)"
    )
    consensus: float = Field(
        ...,
        description="Agreement rate (0.0-1.0): proportion of witnesses voting for winner"
    )
    verdict: str = Field(
        ...,
        description="Final meta-verdict: SEAL if (winner==SEAL AND consensus>=threshold), else HOLD-888"
    )
    tally: Dict[str, int] = Field(
        ...,
        description="Vote counts per verdict type: {verdict_name: count}"
    )
    evidence: str = Field(
        ...,
        description="Human-readable explanation of consensus result"
    )


def arifos_meta_select(request: MetaSelectRequest) -> MetaSelectResponse:
    """
    [GOVERNED] Aggregate multiple witness verdicts via deterministic consensus.

    Tri-Witness consensus aggregator for meta-selection across human, AI, and Earth witnesses.
    Uses verdict hierarchy for tie-breaking: VOID > HOLD-888 > SABAR > PARTIAL > SEAL.

    Args:
        request: MetaSelectRequest with verdicts list and optional consensus_threshold

    Returns:
        MetaSelectResponse with winner, consensus rate, final verdict, and tally

    Features:
        - Deterministic Consensus: Same inputs → same output (no randomness)
        - Verdict Hierarchy Tie-Breaking: VOID beats all, SEAL is weakest
        - Configurable Threshold: Default 0.95 (95% agreement)
        - HOLD-888 Escalation: Low consensus → human review required
        - Audit Trail: Evidence string explains reasoning

    Consensus Logic:
        - Count votes for each verdict type
        - Determine winner by plurality (or hierarchy if tie)
        - Calculate consensus = winner_votes / total_votes
        - If winner==SEAL AND consensus>=threshold → SEAL
        - Else → HOLD-888 (requires human review)

    Verdict Hierarchy (for tie-breaking):
        VOID > HOLD-888 > SABAR > PARTIAL > SEAL

    Examples:
        # Strong consensus (100% SEAL)
        result = arifos_meta_select(MetaSelectRequest(
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ]
        ))
        # → winner: SEAL, consensus: 1.0, verdict: SEAL

        # Low consensus (disagreement)
        result = arifos_meta_select(MetaSelectRequest(
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "VOID", "confidence": 0.99},
                {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
            ]
        ))
        # → winner: VOID (hierarchy), consensus: 0.33, verdict: HOLD-888

        # Custom threshold (80% required)
        result = arifos_meta_select(MetaSelectRequest(
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 0.95},
                {"source": "monitor", "verdict": "PARTIAL", "confidence": 0.80},
            ],
            consensus_threshold=0.80
        ))
        # → winner: SEAL, consensus: 0.75, verdict: HOLD-888 (0.75 < 0.80)
    """
    from arifos_core.enforcement.response_validator_extensions import meta_select

    # Call the core meta_select function
    result = meta_select(
        verdicts=request.verdicts,
        consensus_threshold=request.consensus_threshold,
    )

    # Convert to response model
    return MetaSelectResponse(**result)


# Tool metadata for MCP discovery
TOOL_METADATA = {
    "name": "arifos_meta_select",
    "description": (
        "Aggregate multiple witness verdicts via deterministic consensus (Track A/B/C v45.1). "
        "Combines human, AI, and Earth witness verdicts using verdict hierarchy. "
        "Returns winner, consensus rate, final verdict (SEAL/HOLD-888), and vote tally. "
        "Features: Deterministic algorithm, configurable threshold (default 0.95), "
        "HOLD-888 escalation for low consensus, audit trail evidence."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "verdicts": {
                "type": "array",
                "description": "List of verdict dicts from witnesses. Each dict must contain: 'source' (str), 'verdict' (str: SEAL/PARTIAL/VOID/SABAR/HOLD-888), 'confidence' (float: 0.0-1.0)",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Witness name (e.g., 'human', 'ai', 'earth')"
                        },
                        "verdict": {
                            "type": "string",
                            "description": "Witness verdict: SEAL/PARTIAL/VOID/SABAR/HOLD-888",
                            "enum": ["SEAL", "PARTIAL", "VOID", "SABAR", "HOLD-888"]
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (0.0-1.0)",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "required": ["source", "verdict", "confidence"]
                }
            },
            "consensus_threshold": {
                "type": "number",
                "description": "Minimum agreement rate for SEAL (default 0.95). If consensus < threshold, returns HOLD-888",
                "default": 0.95,
                "minimum": 0.0,
                "maximum": 1.0
            },
        },
        "required": ["verdicts"],
    },
}
