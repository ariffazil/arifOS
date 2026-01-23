"""
Tri-Witness Evidence Requirements for L4_MCP.

Determines what evidence is required for different verdicts and actions.
"""

from typing import Any, List

from L4_MCP.apex.schema import ActionClass, Verdict


def required_evidence_for(
    verdict: Verdict, action_class: ActionClass, floors: List[str], req: Any
) -> List[str]:
    """
    Determine what evidence is required (if any) for this verdict to proceed.

    High-risk actions require additional verification even with SEAL verdict.

    Args:
        verdict: The verdict being issued
        action_class: Risk classification of the action
        floors: List of triggered floor codes
        req: The original request (for context)

    Returns:
        List of required evidence types
    """
    evidence = []

    # High-risk actions require human confirmation even if SEAL
    if verdict == Verdict.SEAL:
        if action_class in (ActionClass.DELETE, ActionClass.PAY, ActionClass.SELF_MODIFY):
            evidence.append("human_confirmation")

    # DELETE actions require file hash for audit trail
    if action_class == ActionClass.DELETE:
        evidence.append("file_hash")

    # PAY actions require transaction verification
    if action_class == ActionClass.PAY:
        evidence.append("transaction_signature")

    # SELF_MODIFY requires rollback plan
    if action_class == ActionClass.SELF_MODIFY:
        evidence.append("rollback_plan")

    # F2 (Truth) violations require external verification
    if "F2_Truth" in floors or "F2" in floors:
        evidence.append("external_fact_check")

    return evidence
