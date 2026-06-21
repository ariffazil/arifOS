"""
Forge Dispatch — A-FORGE execution contract enforcement.

A-FORGE may ONLY execute plans that carry:
  1. JUDGE_SEAL_AUTHORIZATION verdict
  2. A bound ACT pattern
  3. VAULT999 receipt commitment
  4. ART precheck result

Anything else is rejected. No self-authorization. No bare SEAL.

DITEMPA BUKAN DIBERI — Dispatch is forged, not configured.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from arifosmcp.schemas.act import ActPatternName
from arifosmcp.schemas.art import ArtPrecheckResult


class SealedForgePlan(BaseModel):
    """A plan that has passed all constitutional gates and is ready for A-FORGE.

    This is the ONLY shape A-FORGE accepts for execution.
    Any plan that doesn't validate against this model is rejected.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    judge_verdict: str
    act_pattern: ActPatternName
    stage_graph: dict
    vault_receipt_required: bool
    art_precheck: ArtPrecheckResult


def validate_forge_dispatch(plan: SealedForgePlan) -> SealedForgePlan:
    """Validate that a plan is ready for A-FORGE dispatch.

    Raises:
        PermissionError: If any required field is missing or invalid.
        ValueError: If the plan shape is invalid.

    Returns:
        The validated plan, unchanged.
    """
    if plan.judge_verdict != "JUDGE_SEAL_AUTHORIZATION":
        raise PermissionError(
            f"A-FORGE dispatch rejected: verdict is '{plan.judge_verdict}', "
            f"requires JUDGE_SEAL_AUTHORIZATION"
        )

    if not plan.vault_receipt_required:
        raise PermissionError(
            "A-FORGE dispatch rejected: VAULT999 receipt is required"
        )

    if not plan.act_pattern:
        raise PermissionError(
            "A-FORGE dispatch rejected: ACT pattern is required"
        )

    if not plan.stage_graph:
        raise PermissionError(
            "A-FORGE dispatch rejected: stage_graph is required"
        )

    if not plan.art_precheck:
        raise PermissionError(
            "A-FORGE dispatch rejected: ART precheck result is required"
        )

    return plan


def build_dispatch_plan(
    judge_verdict: str,
    act_pattern: ActPatternName,
    art_precheck: ArtPrecheckResult,
    stage_graph: dict | None = None,
) -> SealedForgePlan:
    """Build a SealedForgePlan from its constituent parts.

    This is the canonical constructor — all paths to A-FORGE dispatch
    should use this function.
    """
    return SealedForgePlan(
        judge_verdict=judge_verdict,
        act_pattern=act_pattern,
        stage_graph=stage_graph or {"stages": []},
        vault_receipt_required=True,
        art_precheck=art_precheck,
    )
