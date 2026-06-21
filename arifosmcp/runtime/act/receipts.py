"""
ACT receipts — VAULT999 receipt construction.

Every ACT execution produces a namespaced receipt for the
immutable ledger. No bare SEAL. Every receipt is hash-chained.

DITEMPA BUKAN DIBERI — Receipts are forged, not sealed.
"""

from __future__ import annotations
from datetime import datetime, timezone

from arifosmcp.schemas.act import ActPatternName, ActReceipt
from arifosmcp.schemas.art import ArtPrecheckResult


def build_execution_receipt(
    plan_id: str,
    actor_id: str,
    art_precheck: ArtPrecheckResult,
    act_pattern: ActPatternName,
    stages_completed: list[str],
    judge_verdict: str,
    task_id: str | None = None,
) -> ActReceipt:
    """Build a namespaced ART_ACT_EXECUTION_RECEIPT for VAULT999.

    Args:
        plan_id: The plan this execution belongs to.
        actor_id: Who initiated this execution.
        art_precheck: The ART reflex result that preceded execution.
        act_pattern: Which ACT pattern was used.
        stages_completed: Which stages finished successfully.
        judge_verdict: The constitutional verdict (must be JUDGE_SEAL_AUTHORIZATION).
        task_id: Optional task identifier.

    Returns:
        ActReceipt ready for VAULT999 sealing.
    """
    return ActReceipt(
        plan_id=plan_id,
        task_id=task_id,
        actor_id=actor_id,
        art_precheck=art_precheck,
        act_pattern=act_pattern,
        stages_completed=stages_completed,
        judge_verdict=judge_verdict,
        vault_receipt_required=True,
    )
