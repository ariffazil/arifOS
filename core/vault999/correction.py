"""
core/vault999/correction.py — P8 CORRECTION_SEAL

Implements PARADOX_DOCTRINE_V1 Section 9.

When new evidence proves a past SEAL was incorrect:
  1. Original SEAL hash is preserved (never deleted)
  2. CORRECTION_SEAL entry created with reference to original
  3. Rollback auto-suggested if action was reversible
  4. Trust scores adjusted:
     - Agents advocating wrong SEAL: -0.10
     - Agents that dissented: +0.05
     - Wrong evidence sources: flagged for reliability review
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CorrectionSeal:
    entry_type: str = "CORRECTION_SEAL"
    timestamp: str = ""
    references_seal: str = ""  # hash of original SEAL
    correction_reason: str = ""
    original_grounds: str = ""
    new_evidence: str = ""
    correction_type: str = ""  # EVIDENCE_OVERTURNED, FLOOR_MISCALCULATED, etc.
    original_verdict: str = "SEAL"
    corrected_verdict: str = "CORRECTED_VOID"
    reversibility_assessment: dict[str, Any] = field(default_factory=dict)
    trust_adjustments: dict[str, float] = field(default_factory=dict)
    human_notification: str = ""


_CORRECTION_TYPES = {
    "EVIDENCE_OVERTURNED": "Original evidence was wrong",
    "FLOOR_MISCALCULATED": "Floor score incorrectly computed",
    "AGENT_MISCONDUCT": "Agent fabricated or concealed evidence",
    "HUMAN_OVERRIDE_MISTAKE": "F13 applied on incorrect understanding",
    "TEMPORAL_INVALIDATION": "Safe then, unsafe now",
}


def issue_correction_seal(
    original_seal_hash: str,
    new_evidence: str,
    original_grounds: str,
    correction_type: str,
    was_reversible: bool,
    rollback_possible: bool,
    agent_verdicts: list[dict[str, Any]] | None = None,
) -> CorrectionSeal:
    """
    Issue a CORRECTION_SEAL for a proven-wrong past SEAL.

    Args:
        original_seal_hash: SHA-256 hash of the original SEAL entry
        new_evidence: Description of the new contradictory evidence
        original_grounds: What the original SEAL was based on
        correction_type: One of the _CORRECTION_TYPES keys
        was_reversible: Whether the original action was reversible
        rollback_possible: Whether rollback can still be performed
        agent_verdicts: List of {agent, verdict, was_correct} for trust adjustment
    """
    agent_verdicts = agent_verdicts or []
    trust_adjustments: dict[str, float] = {}

    for av in agent_verdicts:
        agent = av.get("agent", "unknown")
        verdict = av.get("verdict", "SEAL")
        was_correct = av.get("was_correct", True)

        if verdict == "SEAL" and not was_correct:
            trust_adjustments[agent] = -0.10
        elif verdict != "SEAL" and was_correct:
            trust_adjustments[agent] = +0.05

    reversibility = {
        "was_action_reversible": was_reversible,
        "rollback_possible": rollback_possible,
        "rollback_suggested": rollback_possible and was_reversible,
    }

    corrected_verdict = "CORRECTED_VOID"
    if correction_type == "TEMPORAL_INVALIDATION" and was_reversible:
        corrected_verdict = "CORRECTED_HOLD"

    notification = (
        f"Correction issued for SEAL {original_seal_hash[:16]}... "
        f"Type: {correction_type}. "
        f"Rollback suggested: {reversibility["rollback_suggested"]}."
    )

    return CorrectionSeal(
        timestamp=datetime.now(timezone.utc).isoformat(),
        references_seal=original_seal_hash,
        correction_reason="New evidence contradicts original grounds.",
        original_grounds=original_grounds,
        new_evidence=new_evidence,
        correction_type=correction_type,
        original_verdict="SEAL",
        corrected_verdict=corrected_verdict,
        reversibility_assessment=reversibility,
        trust_adjustments=trust_adjustments,
        human_notification=notification,
    )
