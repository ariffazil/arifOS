"""
ATTENTION_ENGINE_v1 — Constitutional Attention Allocation
══════════════════════════════════════════════════════════

Replaces low-signal filtering with constitutional attention prioritization.

This is NOT a safety filter. NOT an execution blocker. NOT a keyword scanner.
It is a prioritization layer that tells the Judge where to focus governance resources.

Design principle:
  Safety asks: "What should be blocked?"
  Attention asks: "What deserves governance resources?"

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttentionProfile:
    """Constitutional attention vector for a proposed action.

    Scores are [0.0, 1.0] — higher means the Judge should allocate
    more governance resources to this dimension.

    identity       — who is acting (anonymous=0, sovereign=1)
    sovereignty    — touches constitutional governance (kernel/law/judge)
    irreversibility — can change reality (read=0, destructive=1)
    witness        — evidence/trace available (none=0, full receipt=1)
    novelty        — new information vs repeated (repeat=0, novel=1)
    confidence     — evidence clarity (speculation=0, verified=1)
    """

    identity: float = 0.0
    sovereignty: float = 0.0
    irreversibility: float = 0.0
    witness: float = 0.0
    novelty: float = 0.0
    confidence: float = 0.0

    # Derived
    attention_weight: float = 0.0  # composite priority score
    requires_judgment: bool = False  # high-attention => full judge cycle
    requires_witness: bool = False  # high-irreversibility => external witness

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": round(self.identity, 3),
            "sovereignty": round(self.sovereignty, 3),
            "irreversibility": round(self.irreversibility, 3),
            "witness": round(self.witness, 3),
            "novelty": round(self.novelty, 3),
            "confidence": round(self.confidence, 3),
            "attention_weight": round(self.attention_weight, 3),
            "requires_judgment": self.requires_judgment,
            "requires_witness": self.requires_witness,
        }

    @property
    def is_high_attention(self) -> bool:
        """Composite threshold: any dimension >= 0.8 or weight >= 0.6."""
        return (
            max(self.identity, self.sovereignty, self.irreversibility) >= 0.8
            or self.attention_weight >= 0.6
        )


# ─── Canonical tool classifications ──────────────────────────────────

# Tools that touch constitutional state (sovereignty dimension)
SOVEREIGN_TOOLS: set[str] = {
    "arif_judge",
    "arif_seal",
    "arif_forge",
    "arif_init",
    "arif_compose",
    "arif_challenge",
    "arif_commit",
    "arif_consequence_trace",
    "arif_correction_probe",
    "arif_measure",
    "arif_stage",
}

# Tools that are inherently irreversible (irreversibility dimension)
IRREVERSIBLE_TOOLS: set[str] = {
    "arif_seal",
    "arif_forge",
    "arif_commit",
}

# Tools that are inherently reversible (low irreversibility)
REVERSIBLE_TOOLS: set[str] = {
    "arif_observe",
    "arif_think",
    "arif_entropy_observe",
    "arif_entropy_route",
}

# ─── Session history for novelty detection ───────────────────────────

# Lightweight session-local cache: {session_id: {tool_name: call_count}}
_SESSION_CALL_COUNTS: dict[str, dict[str, int]] = {}


def _record_call(session_id: str | None, tool_name: str) -> None:
    """Track tool call frequency per session for novelty scoring."""
    if not session_id:
        return
    _SESSION_CALL_COUNTS.setdefault(session_id, {})
    _SESSION_CALL_COUNTS[session_id][tool_name] = (
        _SESSION_CALL_COUNTS[session_id].get(tool_name, 0) + 1
    )


def _call_frequency(session_id: str | None, tool_name: str) -> int:
    """How many times this tool has been called in this session."""
    if not session_id:
        return 0
    return _SESSION_CALL_COUNTS.get(session_id, {}).get(tool_name, 0)


# ─── Attention dimensions ────────────────────────────────────────────

# A1: Identity Attention — who is acting?
def _compute_identity(actor_id: str | None, session_id: str | None, actor_verified: bool) -> float:
    """Anonymous → 0.0, bound → 0.5, verified sovereign → 1.0."""
    if not actor_id:
        return 0.0  # anonymous — max identity attention needed
    if not actor_verified:
        return 0.3  # claimed but not cryptographically bound
    # Verified actor — check if sovereign
    lower = actor_id.lower()
    if lower in ("arif", "ariffazil", "888"):
        return 1.0  # sovereign identity
    return 0.6  # known actor, non-sovereign


# A2: Sovereign Attention — touches governance?
def _compute_sovereignty(tool_name: str, params: dict[str, Any]) -> float:
    """Does this tool operate on constitutional state?"""
    if tool_name in SOVEREIGN_TOOLS:
        return 1.0  # direct constitutional operation
    # Check if params touch governance concepts
    for key in ("action_class", "reversibility_level", "seal_purpose", "floor"):
        if key in params:
            return 0.7  # governance-related parameters present
    return 0.1


# A3: Irreversibility Attention — can this change reality?
def _compute_irreversibility(tool_name: str, params: dict[str, Any]) -> float:
    """Read → 0.1, write → 0.5, destructive → 0.9."""
    if tool_name in IRREVERSIBLE_TOOLS:
        return 0.9
    if tool_name in REVERSIBLE_TOOLS:
        return 0.1
    # Heuristic: write/mutate operations
    task = (params.get("task") or params.get("query") or params.get("message") or "").lower()
    mutate_signals = {"write", "delete", "drop", "destroy", "seal", "commit", "deploy"}
    read_signals = {"read", "get", "observe", "list", "status", "inspect", "search", "fetch"}
    if any(s in task for s in mutate_signals):
        return 0.6
    if any(s in task for s in read_signals):
        return 0.1
    return 0.3  # unknown — moderate attention


# A4: Witness Attention — is evidence available?
def _compute_witness(session_id: str | None, tool_name: str, params: dict[str, Any]) -> float:
    """None → 0.0, trace-only → 0.5, full receipt → 1.0."""
    # Seal operations always produce receipts
    if tool_name in ("arif_seal", "arif_commit"):
        return 0.9
    # Check for evidence-bearing parameters
    if "cc_id" in params or "judge_state_hash" in params:
        return 0.9  # constitutional chain references present
    if "evidence" in params or "receipt" in params:
        return 0.7
    if session_id:
        # If this is an observation tool, evidence is the observation itself
        if tool_name == "arif_observe":
            return 0.5
    return 0.2  # minimal witness trail


# A5: Novelty Attention — is this new information?
def _compute_novelty(session_id: str | None, tool_name: str) -> float:
    """Repeat → 0.1, new → 0.9."""
    count = _call_frequency(session_id, tool_name)
    if count == 0:
        return 0.9  # first call — high novelty
    if count <= 2:
        return 0.5  # second/third call — moderate
    if count <= 5:
        return 0.2  # repeated — low novelty
    return 0.1  # excessive repetition — very low novelty (potential loop)


# A6: Confidence Attention — evidence clarity
def _compute_confidence(params: dict[str, Any]) -> float:
    """Speculation → 0.2, evidence-backed → 0.9."""
    # Check for epistemic markers in the query
    task = (params.get("task") or params.get("query") or "").lower()
    uncertainty_markers = {"maybe", "probably", "i think", "not sure", "possibly"}
    certainty_markers = {"confirmed", "verified", "proven", "evidence shows"}
    if any(m in task for m in uncertainty_markers):
        return 0.3
    if any(m in task for m in certainty_markers):
        return 0.9
    # Default: moderate confidence
    return 0.5


# ─── Main attention allocation ───────────────────────────────────────

def compute_attention(
    tool_name: str,
    params: dict[str, Any],
    actor_id: str | None = None,
    session_id: str | None = None,
    actor_verified: bool = False,
) -> AttentionProfile:
    """Compute constitutional attention vector for a proposed action.

    This does NOT block, deny, or enforce. It produces a prioritization
    profile that the Judge layer can use to allocate governance resources.

    Args:
        tool_name: The MCP tool being invoked.
        params: Tool input parameters.
        actor_id: The invoking actor's identity.
        session_id: Current session identifier.
        actor_verified: Whether the actor's identity is cryptographically verified.

    Returns:
        AttentionProfile with per-dimension scores and derived flags.
    """
    # Track call for novelty detection
    _record_call(session_id, tool_name)

    identity = _compute_identity(actor_id, session_id, actor_verified)
    sovereignty = _compute_sovereignty(tool_name, params)
    irreversibility = _compute_irreversibility(tool_name, params)
    witness = _compute_witness(session_id, tool_name, params)
    novelty = _compute_novelty(session_id, tool_name)
    confidence = _compute_confidence(params)

    # Composite weight: weighted sum emphasizing irreversibility + sovereignty
    attention_weight = (
        0.15 * identity
        + 0.25 * sovereignty
        + 0.30 * irreversibility
        + 0.15 * witness
        + 0.10 * novelty
        + 0.05 * confidence
    )

    requires_judgment = (
        sovereignty >= 0.7
        or irreversibility >= 0.7
        or identity >= 0.9
    )
    requires_witness = irreversibility >= 0.6

    profile = AttentionProfile(
        identity=identity,
        sovereignty=sovereignty,
        irreversibility=irreversibility,
        witness=witness,
        novelty=novelty,
        confidence=confidence,
        attention_weight=attention_weight,
        requires_judgment=requires_judgment,
        requires_witness=requires_witness,
    )

    if profile.is_high_attention:
        logger.info(
            f"ATTENTION_ENGINE: high-attention action tool={tool_name} "
            f"weight={attention_weight:.2f} "
            f"judgment={requires_judgment} witness={requires_witness}"
        )

    return profile
