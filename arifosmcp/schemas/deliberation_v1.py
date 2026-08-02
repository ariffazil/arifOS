"""
arifosmcp/schemas/deliberation_v1.py — DELIBERATION_RECEIPT envelope
═════════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive. D2=separate record_class.
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Extends the existing arifos.record.v1 envelope with a deliberation block
that binds the artifact hash to a falsifiable chain of reasoning. This is
the missing layer identified by audit — F2 TRUTH requires back-reference,
not pure SPEC/UNKNOWN.

Reversibility: git revert <commit-sha>.

Reference: arifosmcp/constitution/quranic_runtime_map.json (the artifact
under deliberation for the initial receipt mint).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ─── Deliberation step ────────────────────────────────────────────────────────


class DeliberationStep(BaseModel):
    """One ordered step in a deliberation chain."""

    order: int = Field(..., ge=0, description="0-indexed position in the chain")
    step_type: Literal[
        "PROPOSAL",  # INT: artifact_sha256 + falsifiable_prediction
        "WITNESS",  # witness_proposal from H/A/E channels
        "CHALLENGE",  # Popperian falsification attempt
        "AMENDMENT",  # artifact_sha256 changed — re-anchor
        "COOLING",  # deliberate drift observation
        "VERDICT",  # SEAL|HOLD|VOID|SABAR
    ]
    actor_id: str
    actor_signature: str = Field(..., description="Ed25519 or schema-stamped")
    sha256_of_step_payload: str = Field(..., description="self-binding hash")
    parent_step_sha256: str | None = Field(
        None, description="forms chain — points to previous step"
    )
    created_at_utc: str
    notes: str | None = None


# ─── Deliberation block ────────────────────────────────────────────────────────


class DeliberationBlock(BaseModel):
    """Ordered hash-chained steps that bind an artifact to a verdict."""

    artifact_sha256: str = Field(..., description="sha256 of artifact under deliberation")
    artifact_path: str
    artifact_class: Literal[
        "canon",
        "constitutional_map",
        "authority_gate",
        "schema",
        "code",
        "doctrine",
    ]
    steps: list[DeliberationStep] = Field(default_factory=list)
    terminal_verdict: Literal["SEAL", "HOLD", "VOID", "SABAR"]
    cooling_required: bool = False
    falsifiable_predictions: list[str] = Field(default_factory=list)
    epistemic_label: str = "INT (interpretive mapping) · PLAUSIBLE"


# ─── Envelope extension ────────────────────────────────────────────────────────


class ConstitutionalSealForDeliberation(BaseModel):
    """Top-level envelope that carries the deliberation block.

    This is a third lane under the existing arifos.record.v1 — distinct
    from SESSION_RECEIPT (Lane B) and CONSTITUTIONAL_SEAL (Lane A).
    """

    record_id: str
    record_class: Literal["CONSTITUTIONAL_SEAL_FOR_DELIBERATION"]
    actor_id: str
    session_id: str
    session_token: str | None = None
    lease_id: str | None = None
    artifact_sha256: str
    artifact_path: str
    deliberation: DeliberationBlock
    verify_chain_token: str = Field(
        ..., description="HMAC over the chained deliberation — verifiable"
    )
    sealed_at_utc: str
    ratified_by: str = "F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)"


__all__ = [
    "DeliberationStep",
    "DeliberationBlock",
    "ConstitutionalSealForDeliberation",
]