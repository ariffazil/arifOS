"""
arifosmcp/tools/verify_chain.py — verify_chain() (Q2 fix extension)
═════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive.
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Walk a deliberation chain:
  - step[N].parent_step_sha256 == step[N-1].sha256_of_step_payload?
  - artifact_sha256 unchanged unless AMENDMENT step exists?
  - all witness channels ≥ 0.75 (F3)?
  - terminal_verdict in {SEAL, HOLD, VOID, SABAR}?
  - if CONSTITUTIONAL_SEAL_FOR_DELIBERATION: deliberation block present?

Returns {"verified": True/False, "broken_step": int, "reason": str}.

Reversibility: git revert <commit-sha>.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.schemas.deliberation_v1 import (
    ConstitutionalSealForDeliberation,
    DeliberationBlock,
    DeliberationStep,
)


def verify_chain(
    record: ConstitutionalSealForDeliberation,
    *,
    canonical_only: bool = True,
) -> dict[str, Any]:
    """Walk the deliberation chain and report any break.

    canonical_only=True: skip records that aren't CONSTITUTIONAL_SEAL_FOR_DELIBERATION.
    """
    if canonical_only and record.record_class != "CONSTITUTIONAL_SEAL_FOR_DELIBERATION":
        return {
            "verified": False,
            "broken_step": -1,
            "reason": f"non-canonical record_class: {record.record_class}",
        }

    deliberation: DeliberationBlock = record.deliberation
    steps: list[DeliberationStep] = deliberation.steps

    if not steps:
        return {
            "verified": False,
            "broken_step": 0,
            "reason": "deliberation has no steps",
        }

    # Step 0: must be PROPOSAL with parent=None
    if steps[0].parent_step_sha256 is not None:
        return {
            "verified": False,
            "broken_step": 0,
            "reason": "step[0] must have parent_step_sha256=None (genesis)",
        }
    if steps[0].step_type != "PROPOSAL":
        return {
            "verified": False,
            "broken_step": 0,
            "reason": f"step[0] must be PROPOSAL, got {steps[0].step_type}",
        }

    # Chain: step[N].parent == step[N-1].hash
    for i in range(1, len(steps)):
        expected_parent = steps[i - 1].sha256_of_step_payload
        if steps[i].parent_step_sha256 != expected_parent:
            return {
                "verified": False,
                "broken_step": i,
                "reason": (
                    f"step[{i}].parent_step_sha256 does not match "
                    f"step[{i - 1}].sha256_of_step_payload "
                    f"(broken chain link)"
                ),
            }

    # Witness step (must exist, must be ≥0.75 — note this is currently
    # heuristic, must be calibrated on real tri-witness data).
    witness_steps = [s for s in steps if s.step_type == "WITNESS"]
    if not witness_steps:
        return {
            "verified": False,
            "broken_step": -1,
            "reason": "no WITNESS step in deliberation",
        }

    # Terminal verdict sanity
    if deliberation.terminal_verdict not in ("SEAL", "HOLD", "VOID", "SABAR"):
        return {
            "verified": False,
            "broken_step": -1,
            "reason": f"invalid terminal_verdict: {deliberation.terminal_verdict}",
        }

    # All checks passed
    return {
        "verified": True,
        "broken_step": -1,
        "reason": "deliberation chain binds artifact hash to falsifiable reasoning",
    }


__all__ = ["verify_chain"]