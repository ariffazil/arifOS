"""
ArifOSResponse — shared canonical response envelope for all organs and kernel.

This is the single source of truth for affordance fields (action_class, blast_radius,
reversibility, confidence, etc.) to eliminate duplication and drift (OBSERVE vs UNKNOWN bugs).

All organs (GEOX, WEALTH, WELL, A-FORGE) and arifOS core MUST import and use
this model (or equivalent validated dict) for responses that include governance metadata.

Usage:
    from arifosmcp.schemas.arifos_response import ArifOSResponse, ActionClass

    resp = ArifOSResponse(
        result=domain_result,
        action_class=ActionClass.OBSERVE,
        blast_radius="LOW",
        ...
    )
    return resp.model_dump()

Pick ONE canonical location for fields: top-level on the response (or inside a single
`affordance` subobject if preferred). Remove duplicated copies in full_affordance /
affordance_contract / top-level.

Contract tests should snapshot against this schema.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ActionClass(StrEnum):
    """Canonical action classification. Single source — no per-organ recompute."""

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    PROPOSE = "PROPOSE"
    PREPARE = "PREPARE"
    MUTATE = "MUTATE"
    EXECUTE_REVERSIBLE = "EXECUTE_REVERSIBLE"
    EXECUTE_HIGH_IMPACT = "EXECUTE_HIGH_IMPACT"
    IRREVERSIBLE = "IRREVERSIBLE"
    SEAL = "SEAL"
    UNKNOWN = "UNKNOWN"  # only for error paths; should be rare


class BlastRadius(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Reversibility(StrEnum):
    REVERSIBLE = "REVERSIBLE"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class ArifOSResponse(BaseModel):
    """Canonical response wrapper.

    Fields like action_class live HERE at top level (canonical).
    Nested copies (affordance_contract.action_class etc.) MUST be removed or
    become $ref / pointers to this.

    Every organ response that carries governance metadata should be (or contain)
    an instance of this before serialization.
    """

    result: Any = Field(..., description="Organ-specific domain payload")

    # Canonical governance / affordance fields — single computation site
    action_class: ActionClass = ActionClass.OBSERVE
    blast_radius: BlastRadius = BlastRadius.LOW
    reversibility: Reversibility = Reversibility.REVERSIBLE
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="0.0-1.0 evidence confidence"
    )
    mutation: bool = False
    requires_session: bool = True
    requires_lease: bool = False
    requires_human_ack: bool = False
    expected_blast_radius: str | None = None  # legacy compat string if needed
    output_is_evidence: bool = True
    safe_autonomous_use: bool = False

    # Identity / transport envelope (see identity propagation fix)
    envelope: dict[str, Any] | None = Field(
        default=None,
        description="Echoed input envelope: {session_id, constitutional_chain_id, actor_id, trace_id}. Must be echoed unchanged by organ.",
    )

    # Optional full affordance for humans (but action_class etc. authoritative at top)
    affordance: dict[str, Any] | None = None

    class Config:
        use_enum_values = True
        extra = "allow"  # allow organ-specific extra fields in result or top


def ensure_arifos_response(data: dict[str, Any] | ArifOSResponse) -> ArifOSResponse:
    """Validate/coerce any organ/kernel output to canonical ArifOSResponse.

    Use in post-processing and contract tests.
    """
    if isinstance(data, ArifOSResponse):
        return data
    if isinstance(data, dict):
        # Coerce action_class etc if present at top or nested (for migration)
        ac = data.get("action_class") or data.get("affordance", {}).get("action_class") or "OBSERVE"
        if isinstance(ac, str):
            try:
                ac = ActionClass(ac)
            except ValueError:
                ac = ActionClass.UNKNOWN
        data["action_class"] = ac
        if "_envelope" in data and "envelope" not in data:
            data["envelope"] = data.pop("_envelope")
        return ArifOSResponse(**data)
    raise ValueError("Cannot coerce to ArifOSResponse")


# ZEN helper: canonical tool -> action_class mapping (single source for organs)
TOOL_ACTION_CLASS: dict[str, ActionClass] = {
    # default OBSERVE for read/observe
}


def get_canonical_action_class(tool_name: str, organ: str = "") -> ActionClass:
    """Return the canonical action class for a tool. ZEN: no per-organ duplication."""
    name = tool_name.lower()
    if any(x in name for x in ["compute", "model", "interpret", "analyze"]):
        return ActionClass.ANALYZE
    if any(x in name for x in ["claim", "prospect", "mutate", "execute", "seal"]):
        return ActionClass.OBSERVE  # or higher, but organs decide
    if "govern" in name or "judge" in name:
        return ActionClass.OBSERVE
    return ActionClass.OBSERVE
