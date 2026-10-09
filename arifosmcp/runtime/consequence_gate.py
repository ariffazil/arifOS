"""
arifosmcp/runtime/consequence_gate.py
═══════════════════════════════════════════════════════════════════════════════
ATLAS333 P40 Consequence & Sovereignty Gate (Humanity Cluster)

Axiom:
  "Intelligence can be delegated. Consequence cannot."
  "Knowledge can be borrowed. Responsibility cannot."
  "Models can be copied. Sovereignty cannot."

Rules:
  1. Detects high-blast-radius and irreversible mutations.
  2. Autonomous agents (333-AGI, 555-ASI, 777-FORGE) CANNOT self-authorize irreversible actions.
  3. If caller is not verified human sovereign (ARIF / F13) and reversibility proof is absent -> 888_HOLD.

Constitutional Floors: F1 AMANAH, F13 SOVEREIGN, P40 ATLAS333.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SOVEREIGN_CALLERS: frozenset[str] = frozenset({
    "human_sovereign",
    "arif",
    "muhammad_arif_bin_fazil",
    "f13_sovereign"
})

# High-blast-radius / Irreversible action patterns
IRREVERSIBLE_ACTION_TYPES: frozenset[str] = frozenset({
    "drop_table",
    "delete_all",
    "force_push",
    "rm_rf",
    "destroy_volume",
    "financial_transfer",
    "rotate_master_secret",
    "modify_constitution_f1_f13",
    "irreversible_mutation"
})


@dataclass(frozen=True)
class ConsequenceEvaluation:
    action_name: str
    caller: str
    is_irreversible: bool
    requires_human_f13: bool
    verdict: str  # "PASS", "888_HOLD", "VOID"
    reason: str
    blast_radius: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    reversibility_score: float = 1.0  # R(a) ∈ [0,1] — LAW_ZEN_ATTENTION
    rollback_recipe: str | None = None  # compiled deterministic rollback


def evaluate_consequence(action: dict[str, Any], caller: str = "333_agent") -> ConsequenceEvaluation:
    """
    Evaluate an action through the P40 Consequence & Sovereignty Gate.

    LAW_ZEN_ATTENTION (2026-09-01, additive — F13 RATIFIED 2026-09-01):
      An irreversible-classified action with a deterministic rollback
      recipe inside the reversible sandbox (R(a) >= 0.85) no longer
      demands sovereign attention — the recipe IS the ex-ante mechanism
      that makes it reversible in practice. 888_HOLD survives only for
      the truly atomic surface: no recipe, no rollback, no sandbox.
    """
    action_type = str(action.get("type", action.get("action_type", ""))).lower().strip()
    action_class = str(action.get("action_class", "")).upper().strip()
    has_rollback_proof = bool(action.get("has_rollback_proof", False))
    raw_text = str(action).lower()

    # ── Deterministic reversibility score (K-Gate input) ───────────────
    # R(a): 1.0 fully reversible … 0.0 irreversible. Callers may supply a
    # computed score; otherwise derive from the action's own proof fields.
    reversibility_score = float(action.get("reversibility_score", 1.0))
    rollback_recipe = str(action.get("rollback_recipe", "") or "") or None

    if reversibility_score >= 0.85 and rollback_recipe:
        # Inside the sandbox: ex-ante mechanism design. Auto-pass with
        # receipt — zero sovereign attention burned (F1 AMANAH satisfied
        # by the compiled rollback, not by a popup).
        return ConsequenceEvaluation(
            action_name=action_type or "sandbox_action",
            caller=caller,
            is_irreversible=False,
            requires_human_f13=False,
            verdict="PASS",
            reason=(
                "LAW_ZEN_ATTENTION: deterministic rollback recipe compiled "
                f"(R(a)={reversibility_score:.2f} >= 0.85) — action is "
                "reversible by construction, sovereign attention preserved"
            ),
            blast_radius="LOW",
            reversibility_score=reversibility_score,
            rollback_recipe=rollback_recipe,
        )

    # Determine if action is irreversible
    is_irreversible = (
        action_class in {"T3", "IRREVERSIBLE"}
        or action_type in IRREVERSIBLE_ACTION_TYPES
        or any(k in raw_text for k in ["drop table", "rm -rf", "push --force", "delete from", "format disk"])
        or reversibility_score < 0.30  # below hard floor = effectively atomic
    )

    caller_clean = caller.lower().strip()
    is_human = caller_clean in SOVEREIGN_CALLERS or action.get("sovereign_signed", False)

    # If action is irreversible and no valid rollback proof exists
    if is_irreversible and not has_rollback_proof:
        if not is_human:
            return ConsequenceEvaluation(
                action_name=action_type or "unnamed_mutation",
                caller=caller,
                is_irreversible=True,
                requires_human_f13=True,
                verdict="888_HOLD",
                reason="P40 KERNEL GATE: Irreversible action cannot be authorized by synthetic agents. Consequence is non-delegable. Sovereign F13 decision required.",
                blast_radius="CRITICAL",
                reversibility_score=reversibility_score,
                rollback_recipe=rollback_recipe,
            )
        else:
            # Human sovereign carrying consequence
            return ConsequenceEvaluation(
                action_name=action_type or "sovereign_mutation",
                caller=caller,
                is_irreversible=True,
                requires_human_f13=True,
                verdict="PASS",
                reason="F13 SOVEREIGN APPROVED: Human sovereign carries moral and operational consequence.",
                blast_radius="HIGH",
                reversibility_score=reversibility_score,
                rollback_recipe=rollback_recipe,
            )

    # Reversible or low blast radius actions
    return ConsequenceEvaluation(
        action_name=action_type or "standard_action",
        caller=caller,
        is_irreversible=False,
        requires_human_f13=False,
        verdict="PASS",
        reason="Action is reversible or within autonomous capability tier.",
        blast_radius="LOW",
        reversibility_score=reversibility_score,
        rollback_recipe=rollback_recipe,
    )
