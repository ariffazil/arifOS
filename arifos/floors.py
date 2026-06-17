"""
floors.py — F1-F13 floor check functions.

Each floor is implemented as code, not as a principle. These
functions are called by `prethink` and the 4 guards. They are
the minimum local discipline — the kernel is the source of truth
and may issue stricter verdicts.

F1 AMANAH  — every action must be reversible or trigger 888 HOLD
F2 TRUTH   — every result must carry an epistemic stamp
F7 HUMILITY — confidence is capped at 0.90
F11 AUDIT  — every action must be traceable to an actor
F13 SOVEREIGN — high-impact actions require sovereign authority
"""

from __future__ import annotations

from arifos.decision import (
    ActionClass,
    FloorVerdict,
    HIGH_BLAST_TRIGGERS,
    HOLD_TRIGGERS,
)


def check_f1_reversibility(
    action_class: ActionClass,
    reversibility: str = "REVERSIBLE",
) -> FloorVerdict:
    """F1 AMANAH — irreversible actions trigger 888 HOLD."""
    is_irreversible = action_class in HOLD_TRIGGERS
    if is_irreversible:
        return FloorVerdict(
            floor_id="F1",
            verdict="HOLD",
            reason=f"F1 AMANAH: {action_class.value} is irreversible — requires 888 HOLD",
        )
    return FloorVerdict(
        floor_id="F1",
        verdict="PASS",
        reason=f"F1: action is {reversibility.lower()} within session scope",
    )


def check_f2_truth(taint: str, source: str | None) -> FloorVerdict:
    """F2 TRUTH — every result must carry an epistemic stamp."""
    if taint == "UNTRUSTED" and not source:
        return FloorVerdict(
            floor_id="F2",
            verdict="WARN",
            reason="F2: result is untrusted and has no source citation",
        )
    return FloorVerdict(
        floor_id="F2",
        verdict="PASS",
        reason=f"F2: result has taint={taint}, source={'present' if source else 'none'}",
    )


def check_f7_humility(confidence: float | None) -> FloorVerdict:
    """F7 HUMILITY — confidence is capped at 0.90."""
    if confidence is None:
        return FloorVerdict(
            floor_id="F7",
            verdict="WARN",
            reason="F7: no confidence declared — humility band required",
        )
    if confidence > 0.90:
        return FloorVerdict(
            floor_id="F7",
            verdict="FAIL",
            reason=f"F7 HUMILITY: confidence {confidence} exceeds 0.90 cap",
        )
    return FloorVerdict(
        floor_id="F7",
        verdict="PASS",
        reason=f"F7: confidence {confidence} within humility cap",
    )


def check_f11_audit(actor_id: str | None) -> FloorVerdict:
    """F11 AUDIT — every action must be traceable to an actor."""
    if not actor_id:
        return FloorVerdict(
            floor_id="F11",
            verdict="FAIL",
            reason="F11 AUDIT: no actor_id — cannot trace to sovereign",
        )
    return FloorVerdict(
        floor_id="F11",
        verdict="PASS",
        reason=f"F11: actor_id={actor_id} present and traceable",
    )


def check_f13_sovereign(
    action_class: ActionClass,
    blast_radius: str,
) -> FloorVerdict:
    """F13 SOVEREIGN — high-impact actions require sovereign authority."""
    if blast_radius in ("FEDERATION", "EXTERNAL") and action_class in HIGH_BLAST_TRIGGERS:
        return FloorVerdict(
            floor_id="F13",
            verdict="HOLD",
            reason=f"F13: {action_class.value} with blast_radius={blast_radius} requires sovereign authority",
        )
    return FloorVerdict(
        floor_id="F13",
        verdict="PASS",
        reason="F13: action within local/session scope",
    )
